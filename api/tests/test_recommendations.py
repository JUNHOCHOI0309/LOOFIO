import base64
import json
from datetime import datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow
from app.metrics.store import InMemoryAppointmentMetricStore
from app.opportunities.low_demand import build_low_demand_opportunity_drafts
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


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
