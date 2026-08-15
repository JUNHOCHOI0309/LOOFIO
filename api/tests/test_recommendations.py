import base64
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow
from app.metrics.store import InMemoryAppointmentMetricStore
from app.imports.appointments import parse_appointments_csv
from app.opportunities.low_demand import build_low_demand_opportunity_drafts
from app.opportunities.other_detectors import build_other_detector_opportunity_drafts
from app.opportunities.store import InMemoryOpportunityStore
from app.recommendations.store import InMemoryRecommendationStore
from app.schemas.auth import AuthenticatedUser
from app.schemas.auth import TenantMembership


def test_recommendation_draft_and_decision_keep_observation_and_estimate_separate(monkeypatch) -> None:
    client, tenant_id, opportunity_id = _authenticated_client_with_opportunity(monkeypatch)

    draft = client.post(f"/api/v1/opportunities/{opportunity_id}/recommendations/draft")
    listed = client.get(f"/api/v1/opportunities/{opportunity_id}/recommendations")

    assert draft.status_code == 200
    assert draft.json()["action_type"] == "manual_time_slot_offer_test"
    assert draft.json()["channel"] == "manual"
    assert draft.json()["expected_effect"]["basis"] == "opportunity_estimate"
    assert "외부 실행은 일어나지 않습니다" in draft.json()["limitations"][-1]
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    decision = client.post(
        f"/api/v1/recommendations/{draft.json()['id']}/decisions",
        json={"decision": "modified", "reason_code": "LOCAL_TEST", "modified_payload": {"test_duration_weeks": 4}},
    )

    assert tenant_id
    assert decision.status_code == 200
    assert decision.json()["status"] == "modified"
    assert decision.json()["latest_decision"]["decision"] == "modified"
    assert decision.json()["latest_decision"]["modified_payload"] == {"test_duration_weeks": 4, "manual_notes": None}


def test_recommendation_decision_requires_modified_payload(monkeypatch) -> None:
    client, _, opportunity_id = _authenticated_client_with_opportunity(monkeypatch)
    draft = client.post(f"/api/v1/opportunities/{opportunity_id}/recommendations/draft")

    response = client.post(f"/api/v1/recommendations/{draft.json()['id']}/decisions", json={"decision": "modified"})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_recommendation_draft_cannot_access_another_tenant_opportunity(monkeypatch) -> None:
    client, _, _ = _authenticated_client_with_opportunity(monkeypatch)

    response = client.post("/api/v1/opportunities/not-this-tenants-opportunity/recommendations/draft")

    assert response.status_code == 404


def test_viewer_cannot_create_recommendation_draft(monkeypatch) -> None:
    client, tenant_id, opportunity_id = _authenticated_client_with_opportunity(monkeypatch)
    auth_store = app.state.auth_store
    user_id = next(iter(auth_store.memberships))
    auth_store.memberships[user_id] = [TenantMembership(tenant_id=tenant_id, name="Recommendation Tenant", role="viewer")]

    response = client.post(f"/api/v1/opportunities/{opportunity_id}/recommendations/draft")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_other_detector_recommendations_are_versioned_manual_and_customer_safe(monkeypatch) -> None:
    client, tenant_id, _ = _authenticated_client_with_opportunity(monkeypatch)
    rows = _fixture_metric_rows("hospital_operational_mix_v1.csv")
    opportunities = app.state.opportunity_store.refresh(
        tenant_id=tenant_id,
        business_id="business-for-recommendation",
        drafts=build_other_detector_opportunity_drafts(rows, as_of_date=datetime.fromisoformat("2026-08-15T00:00:00+09:00").date()),
    )
    expected = {
        "CANCELLATION_HOTSPOT": ("cancellation-hotspot-manual-review-v1", "manual_cancellation_flow_review"),
        "DORMANT_CUSTOMER": ("dormant-customer-manual-review-v1", "manual_revisit_cohort_review"),
        "SERVICE_DEMAND_GAP": ("service-demand-gap-manual-review-v1", "manual_offering_slot_review"),
    }

    for opportunity_type, (version, action_type) in expected.items():
        opportunity = next(item for item in opportunities if item.type == opportunity_type)
        response = client.post(f"/api/v1/opportunities/{opportunity.id}/recommendations/draft")

        assert response.status_code == 200
        assert response.json()["version"] == version
        assert response.json()["action_type"] == action_type
        assert response.json()["channel"] == "manual"
        assert response.json()["expected_effect"] is None
        assert any("외부 실행은 일어나지 않습니다" in limitation for limitation in response.json()["limitations"])

    dormant = next(item for item in opportunities if item.type == "DORMANT_CUSTOMER")
    dormant_draft = client.post(f"/api/v1/opportunities/{dormant.id}/recommendations/draft").json()
    assert rows[0].customer_token not in json.dumps(dormant_draft, ensure_ascii=False)
    assert dormant_draft["target_segment"]["customer_reference"] == "not_included"


def _authenticated_client_with_opportunity(monkeypatch):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="recommendation-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Recommendation Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    metric_store = InMemoryAppointmentMetricStore()
    opportunity_store = InMemoryOpportunityStore()
    business_id = "business-for-recommendation"
    metric_store.register_rows(tenant_id=tenant.tenant_id, business_id=business_id, rows=_twelve_week_demand_rows())
    opportunities = opportunity_store.refresh_low_demand(
        tenant_id=tenant.tenant_id,
        business_id=business_id,
        drafts=build_low_demand_opportunity_drafts(_twelve_week_demand_rows()),
    )
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "metric_store", metric_store)
    monkeypatch.setattr(app.state, "opportunity_store", opportunity_store)
    monkeypatch.setattr(app.state, "recommendation_store", InMemoryRecommendationStore())
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))
    return client, tenant.tenant_id, opportunities[0].id


def _twelve_week_demand_rows() -> list[AppointmentMetricRow]:
    rows: list[AppointmentMetricRow] = []
    first_monday = datetime.fromisoformat("2026-05-04T00:00:00+09:00")
    for week in range(12):
        day = first_monday + timedelta(weeks=week)
        rows.append(AppointmentMetricRow(visit_start_at=day.replace(hour=10), status="completed", paid_amount=Decimal("30000")))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=14), status="completed", paid_amount=Decimal("30000")) for _ in range(4))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=16), status="completed", paid_amount=Decimal("30000")) for _ in range(3))
    return rows


def _fixture_metric_rows(filename: str) -> list[AppointmentMetricRow]:
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


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
