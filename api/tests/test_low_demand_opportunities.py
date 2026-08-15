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
from app.opportunities.store import InMemoryOpportunityStore
from app.schemas.auth import AuthenticatedUser


def test_low_demand_opportunity_separates_observation_from_estimate() -> None:
    drafts = build_low_demand_opportunity_drafts(_twelve_week_demand_rows(with_payments=True))
    monday_morning = next(draft for draft in drafts if draft.segment["weekday"] == "MONDAY" and draft.segment["start_hour"] == 10)

    assert monday_morning.observation.demand_index == 0.2857
    assert monday_morning.estimate is not None
    assert monday_morning.estimate.value_low.amount == "162937.50"
    assert monday_morning.estimate.value_high.amount == "325875.00"
    assert "50~100%" in monday_morning.estimate.assumptions[1]
    assert monday_morning.score <= 100
    assert monday_morning.confidence < 1
    assert monday_morning.detector_version == "low-demand-revenue-gap-v2"
    assert "비교 시간대의 완료 결제금액 표본" in monday_morning.estimate.assumptions[2]


def test_low_demand_opportunity_omits_estimate_without_paid_amounts() -> None:
    drafts = build_low_demand_opportunity_drafts(_twelve_week_demand_rows(with_payments=False))

    assert drafts
    assert all(draft.estimate is None for draft in drafts)
    assert "결제금액 표본" in drafts[0].limitations[-1]


def test_project_sample_pack_exercises_revenue_gap_scenarios() -> None:
    positive = build_low_demand_opportunity_drafts(_fixture_metric_rows("hospital_revenue_gap_positive_v1.csv"))
    sparse = build_low_demand_opportunity_drafts(_fixture_metric_rows("hospital_revenue_gap_sparse_payment_v1.csv"))
    operational = build_low_demand_opportunity_drafts(_fixture_metric_rows("hospital_operational_mix_v1.csv"))

    assert len(positive) == 1
    assert positive[0].estimate is not None
    assert positive[0].estimate.value_high.amount == "805442.82"
    assert len(sparse) == 1
    assert sparse[0].estimate is None
    assert len(operational) == 7
    assert all(draft.estimate is not None for draft in operational)


def test_refresh_persists_opportunities_idempotently_within_tenant(monkeypatch) -> None:
    client, tenant_id, metric_store = _authenticated_client(monkeypatch)
    metric_store.register_rows(tenant_id=tenant_id, business_id="biz-a", rows=_twelve_week_demand_rows(with_payments=True))
    url = "/api/v1/businesses/biz-a/opportunities/refresh"

    first = client.post(url)
    second = client.post(url)
    listed = client.get("/api/v1/businesses/biz-a/opportunities")

    assert first.status_code == 200
    assert first.json()["refreshed_count"] == 1
    assert first.json()["opportunities"][0]["estimate"]["value_high"]["amount"] == "325875.00"
    assert second.status_code == 200
    assert second.json()["opportunities"][0]["id"] == first.json()["opportunities"][0]["id"]
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_refresh_cannot_read_another_tenants_business(monkeypatch) -> None:
    client, _, metric_store = _authenticated_client(monkeypatch)
    metric_store.register_rows(tenant_id="other-tenant", business_id="biz-other", rows=_twelve_week_demand_rows(with_payments=True))

    response = client.post("/api/v1/businesses/biz-other/opportunities/refresh")

    assert response.status_code == 404


def _twelve_week_demand_rows(*, with_payments: bool) -> list[AppointmentMetricRow]:
    rows: list[AppointmentMetricRow] = []
    first_monday = datetime.fromisoformat("2026-05-04T00:00:00+09:00")
    paid_amount = Decimal("30000") if with_payments else None
    for week in range(12):
        day = first_monday + timedelta(weeks=week)
        rows.append(AppointmentMetricRow(visit_start_at=day.replace(hour=10), status="completed", paid_amount=paid_amount))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=14), status="completed", paid_amount=paid_amount) for _ in range(4))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=16), status="completed", paid_amount=paid_amount) for _ in range(3))
    return rows


def _fixture_metric_rows(filename: str) -> list[AppointmentMetricRow]:
    root = Path(__file__).resolve().parents[2]
    parsed = parse_appointments_csv((root / "sample-data" / "appointments" / filename).read_bytes())
    assert not parsed.errors
    return [AppointmentMetricRow(visit_start_at=row.visit_start_at, status=row.status, paid_amount=row.paid_amount) for row in parsed.rows]


def _authenticated_client(monkeypatch):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="opportunity-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Opportunity Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    metric_store = InMemoryAppointmentMetricStore()
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "metric_store", metric_store)
    monkeypatch.setattr(app.state, "opportunity_store", InMemoryOpportunityStore())
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))
    return client, tenant.tenant_id, metric_store


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
