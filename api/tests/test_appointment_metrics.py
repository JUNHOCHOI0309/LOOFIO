import base64
import json
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow, calculate_appointment_metrics
from app.metrics.store import InMemoryAppointmentMetricStore
from app.schemas.auth import AuthenticatedUser


def test_calculate_appointment_metrics_uses_completed_revenue_only() -> None:
    rows = [
        _row("2026-05-18T10:00:00+09:00", "completed", "30000"),
        _row("2026-05-18T11:00:00+09:00", "cancelled", "30000"),
        _row("2026-05-19T16:00:00+09:00", "no_show", None),
        _row("2026-05-19T18:00:00+09:00", "booked", "50000"),
    ]

    metrics = calculate_appointment_metrics(rows)

    assert metrics.metric_version == "appointment-observation-v1"
    assert metrics.appointment_count == 4
    assert metrics.completed_count == 1
    assert metrics.cancelled_count == 1
    assert metrics.no_show_count == 1
    assert metrics.cancellation_rate == 0.25
    assert metrics.actual_revenue.amount == "30000.00"
    assert metrics.average_completed_revenue.amount == "30000.00"
    monday_slot = next(slot for slot in metrics.time_slots if slot.weekday == "MONDAY" and slot.slot_start_hour == 10)
    assert monday_slot.appointment_count == 2
    assert monday_slot.cancellation_rate == 0.5


def test_empty_metrics_do_not_invent_rates_or_revenue() -> None:
    metrics = calculate_appointment_metrics([])

    assert metrics.appointment_count == 0
    assert metrics.cancellation_rate == 0.0
    assert metrics.actual_revenue.amount == "0.00"
    assert metrics.average_completed_revenue is None
    assert metrics.period_start is None


def test_metrics_api_scopes_reads_to_active_tenant(monkeypatch) -> None:
    client, tenant_id, metric_store = _authenticated_client(monkeypatch)
    metric_store.register_rows(tenant_id=tenant_id, business_id="biz-a", rows=[_row("2026-05-18T10:00:00+09:00", "completed", "30000")])
    metric_store.register_rows(tenant_id="other-tenant", business_id="biz-other", rows=[_row("2026-05-18T10:00:00+09:00", "completed", "99999")])

    own = client.get("/api/v1/businesses/biz-a/metrics/appointments")
    other = client.get("/api/v1/businesses/biz-other/metrics/appointments")

    assert own.status_code == 200
    assert own.json()["actual_revenue"] == {"amount": "30000.00", "currency": "KRW"}
    assert other.status_code == 404


def test_metrics_api_rejects_naive_time_range(monkeypatch) -> None:
    client, tenant_id, metric_store = _authenticated_client(monkeypatch)
    metric_store.register_rows(tenant_id=tenant_id, business_id="biz-a", rows=[])

    response = client.get("/api/v1/businesses/biz-a/metrics/appointments?start_at=2026-05-01T00:00:00")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def _row(visit_start_at: str, status: str, paid_amount: str | None) -> AppointmentMetricRow:
    return AppointmentMetricRow(
        visit_start_at=datetime.fromisoformat(visit_start_at),
        status=status,
        paid_amount=Decimal(paid_amount) if paid_amount else None,
    )


def _authenticated_client(monkeypatch):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="metric-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Metric Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    metric_store = InMemoryAppointmentMetricStore()
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "metric_store", metric_store)
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))
    return client, tenant.tenant_id, metric_store


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
