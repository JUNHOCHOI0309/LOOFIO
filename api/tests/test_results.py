import base64
import json
from datetime import datetime, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.actions.store import InMemoryActionStore
from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow
from app.metrics.store import InMemoryAppointmentMetricStore
from app.results.store import InMemoryResultStore
from app.schemas.actions import CreateManualActionRequest, UpdateActionStatusRequest
from app.schemas.auth import AuthenticatedUser, TenantMembership


RESULT_PAYLOAD = {
    "execution_summary": "안내 문구를 수동으로 제공하고 현장 반응을 기록했습니다.",
    "measurement_start_at": "2026-08-18T14:00:00+09:00",
    "measurement_end_at": "2026-08-18T16:00:00+09:00",
    "actual_spend": {"amount": "10000", "currency": "KRW"},
}


def test_completed_action_records_result_once_and_returns_deterministic_measurement(monkeypatch) -> None:
    client, tenant_id, action, result_store, metric_store = _completed_action_client(monkeypatch)
    metric_store.register_rows(tenant_id=tenant_id, business_id=action.business_id, rows=[
        _row("2026-08-18T14:30:00+09:00", "completed", "30000"),
        _row("2026-08-18T15:15:00+09:00", "cancelled", None),
        _row("2026-08-11T14:30:00+09:00", "completed", "10000"),
        _row("2026-08-04T14:30:00+09:00", "completed", "20000"),
        _row("2026-07-28T14:30:00+09:00", "completed", "20000"),
        _row("2026-07-21T14:30:00+09:00", "completed", "30000"),
    ])

    created = client.post(f"/api/v1/actions/{action.id}/results", json=RESULT_PAYLOAD)
    replayed = client.post(f"/api/v1/actions/{action.id}/results", json=RESULT_PAYLOAD)
    measurement = client.get(f"/api/v1/actions/{action.id}/measurements")

    assert created.status_code == 201
    assert replayed.status_code == 200
    assert replayed.json()["replayed"] is True
    assert measurement.status_code == 200
    assert measurement.json()["observed"]["actual_revenue"]["amount"] == "30000.00"
    assert measurement.json()["baseline_average"]["actual_revenue"]["amount"] == "20000.00"
    assert measurement.json()["change_from_baseline"]["actual_revenue"]["amount"] == "10000.00"
    assert "인과관계는 판단하지 않습니다" in measurement.json()["limitations"][0]
    assert result_store.get(tenant_id=tenant_id, action_id=action.id).actual_spend.amount == Decimal("10000")


def test_result_requires_completed_action_and_editor_role(monkeypatch) -> None:
    client, tenant_id, action, result_store, _ = _completed_action_client(monkeypatch, completed=False)
    blocked = client.post(f"/api/v1/actions/{action.id}/results", json=RESULT_PAYLOAD)
    assert blocked.status_code == 409

    result_store.register_action(tenant_id=tenant_id, action_id=action.id, completed=True)
    auth_store = app.state.auth_store
    user_id = next(iter(auth_store.memberships))
    auth_store.memberships[user_id] = [TenantMembership(tenant_id=tenant_id, name="Result Tenant", role="viewer")]
    forbidden = client.post(f"/api/v1/actions/{action.id}/results", json=RESULT_PAYLOAD)
    assert forbidden.status_code == 403


def _completed_action_client(monkeypatch, completed: bool = True):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="result-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Result Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    action_store = InMemoryActionStore()
    action_store.register_recommendation(tenant_id=tenant.tenant_id, recommendation_id="rec-result", status="approved", action_type="manual_time_slot_offer_test", channel="manual")
    payload = CreateManualActionRequest(title="수동 실험", planned_start_at=datetime(2026, 8, 18, 14, tzinfo=timezone.utc))
    action = action_store.create_or_get_manual_action(tenant_id=tenant.tenant_id, recommendation_id="rec-result", user_id=user.user_id, payload=payload).action
    if completed:
        action_store.update_status(tenant_id=tenant.tenant_id, action_id=action.id, user_id=user.user_id, payload=UpdateActionStatusRequest(status="in_progress"))
        action = action_store.update_status(tenant_id=tenant.tenant_id, action_id=action.id, user_id=user.user_id, payload=UpdateActionStatusRequest(status="completed"))
    result_store = InMemoryResultStore()
    result_store.register_action(tenant_id=tenant.tenant_id, action_id=action.id, completed=completed)
    metric_store = InMemoryAppointmentMetricStore()
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "action_store", action_store)
    monkeypatch.setattr(app.state, "result_store", result_store)
    monkeypatch.setattr(app.state, "metric_store", metric_store)
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))
    return client, tenant.tenant_id, action, result_store, metric_store


def _row(value: str, status: str, amount: str | None) -> AppointmentMetricRow:
    return AppointmentMetricRow(visit_start_at=datetime.fromisoformat(value), status=status, paid_amount=Decimal(amount) if amount else None)


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
