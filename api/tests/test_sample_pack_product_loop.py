import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from app.actions.store import InMemoryActionStore
from app.imports.appointments import parse_appointments_csv
from app.metrics.appointments import AppointmentMetricRow
from app.opportunities.low_demand import build_low_demand_opportunity_drafts
from app.opportunities.other_detectors import build_other_detector_opportunity_drafts
from app.opportunities.store import InMemoryOpportunityStore
from app.recommendations.manual import build_manual_recommendation_draft
from app.recommendations.store import InMemoryRecommendationStore
from app.results.measurement import baseline_windows, calculate_action_measurement
from app.results.store import InMemoryResultStore
from app.schemas.actions import CreateManualActionRequest, UpdateActionStatusRequest
from app.schemas.results import CreateActionResultRequest


AS_OF_DATE = datetime.fromisoformat("2026-08-15T00:00:00+09:00").date()


def test_sample_pack_keeps_detector_profiles_stable() -> None:
    positive = _rows("hospital_revenue_gap_positive_v1.csv")
    sparse = _rows("hospital_revenue_gap_sparse_payment_v1.csv")
    operational = _rows("hospital_operational_mix_v1.csv")

    positive_drafts = build_low_demand_opportunity_drafts(positive)
    sparse_drafts = build_low_demand_opportunity_drafts(sparse)
    operational_drafts = build_low_demand_opportunity_drafts(operational)
    operational_other_drafts = build_other_detector_opportunity_drafts(operational, as_of_date=AS_OF_DATE)

    assert len(positive_drafts) == 1
    assert positive_drafts[0].estimate is not None
    assert positive_drafts[0].estimate.value_high.amount == "805442.82"
    assert len(sparse_drafts) == 1
    assert sparse_drafts[0].estimate is None
    assert len(operational_drafts) == 7
    assert {draft.opportunity_type for draft in operational_other_drafts} >= {
        "CANCELLATION_HOTSPOT",
        "DORMANT_CUSTOMER",
        "SERVICE_DEMAND_GAP",
    }


def test_operational_sample_simulates_opportunity_to_measurement_loop_without_external_execution() -> None:
    rows = _rows("hospital_operational_mix_v1.csv")
    drafts = [
        *build_low_demand_opportunity_drafts(rows),
        *build_other_detector_opportunity_drafts(rows, as_of_date=AS_OF_DATE),
    ]
    opportunity_store = InMemoryOpportunityStore()
    first_opportunities = opportunity_store.refresh(tenant_id="sample-tenant", business_id="operational-sample", drafts=drafts)
    second_opportunities = opportunity_store.refresh(tenant_id="sample-tenant", business_id="operational-sample", drafts=drafts)

    assert {(item.type, item.detector.version, item.id) for item in first_opportunities} == {
        (item.type, item.detector.version, item.id) for item in second_opportunities
    }

    recommendation_store = InMemoryRecommendationStore()
    recommendations = [
        recommendation_store.create_or_get_draft(
            tenant_id="sample-tenant",
            opportunity_id=opportunity.id,
            draft=build_manual_recommendation_draft(opportunity),
        )
        for opportunity in first_opportunities
    ]
    action_types = {item.action_type for item in recommendations}

    assert {"manual_time_slot_offer_test", "manual_cancellation_flow_review", "manual_revisit_cohort_review", "manual_offering_slot_review"} <= action_types
    assert all(item.channel == "manual" for item in recommendations)
    assert all(item.expected_effect is None for item in recommendations if item.action_type != "manual_time_slot_offer_test")
    dormant_recommendation = next(item for item in recommendations if item.action_type == "manual_revisit_cohort_review")
    customer_token = next(row.customer_token for row in rows if row.customer_token)
    assert customer_token not in json.dumps(dormant_recommendation.model_dump(mode="json"), ensure_ascii=False)

    recommendation = next(item for item in recommendations if item.action_type == "manual_time_slot_offer_test")
    action_store = InMemoryActionStore()
    action_store.register_recommendation(
        tenant_id="sample-tenant",
        recommendation_id=recommendation.id,
        status="approved",
        action_type=recommendation.action_type,
        channel=recommendation.channel,
        business_id="operational-sample",
    )
    measurement_start = _measurement_window(rows)
    action = action_store.create_or_get_manual_action(
        tenant_id="sample-tenant",
        recommendation_id=recommendation.id,
        user_id="sample-user",
        payload=CreateManualActionRequest(title="견본 데이터 수동 점검", planned_start_at=measurement_start),
    ).action
    action = action_store.update_status(
        tenant_id="sample-tenant", action_id=action.id, user_id="sample-user", payload=UpdateActionStatusRequest(status="in_progress")
    )
    action = action_store.update_status(
        tenant_id="sample-tenant", action_id=action.id, user_id="sample-user", payload=UpdateActionStatusRequest(status="completed")
    )

    result_store = InMemoryResultStore()
    result_store.register_action(tenant_id="sample-tenant", action_id=action.id, completed=True)
    measurement_end = measurement_start + timedelta(hours=2)
    result = result_store.create_or_get(
        tenant_id="sample-tenant",
        action_id=action.id,
        user_id="sample-user",
        payload=CreateActionResultRequest(
            execution_summary="견본 데이터 기반 수동 검토를 기록했습니다.",
            measurement_start_at=measurement_start,
            measurement_end_at=measurement_end,
            actual_spend={"amount": Decimal("0"), "currency": "KRW"},
        ),
    ).result
    measurement = calculate_action_measurement(
        action_id=action.id,
        result_id=result.id,
        observation_rows=_rows_in_window(rows, measurement_start, measurement_end),
        baseline_rows=[_rows_in_window(rows, start, end) for start, end in baseline_windows(measurement_start, measurement_end)],
        start_at=measurement_start,
        end_at=measurement_end,
    )

    assert [event.status for event in action.status_events] == ["planned", "in_progress", "completed"]
    assert result.actual_spend is not None and result.actual_spend.amount == Decimal("0")
    assert measurement.baseline_window_count == 4
    assert measurement.method_version == "same-window-prior-four-weeks-v2"
    assert measurement.change_from_baseline is not None
    assert measurement.change_from_baseline.appointment_count < 0
    assert "인과관계는 판단하지 않습니다" in measurement.limitations[0]


def _rows(filename: str) -> list[AppointmentMetricRow]:
    root = Path(__file__).resolve().parents[2]
    parsed = parse_appointments_csv((root / "sample-data" / "appointments" / filename).read_bytes())
    assert not parsed.errors
    return [
        AppointmentMetricRow(
            visit_start_at=row.visit_start_at,
            status=row.status,
            paid_amount=row.paid_amount,
            offering_name=row.offering_name,
            customer_token=row.customer_token,
        )
        for row in parsed.rows
    ]


def _measurement_window(rows: list[AppointmentMetricRow]) -> datetime:
    anchor = rows[len(rows) // 2].visit_start_at
    return anchor.replace(minute=0, second=0, microsecond=0, hour=(anchor.hour // 2) * 2)


def _rows_in_window(rows: list[AppointmentMetricRow], start_at: datetime, end_at: datetime) -> list[AppointmentMetricRow]:
    return [row for row in rows if start_at <= row.visit_start_at < end_at]
