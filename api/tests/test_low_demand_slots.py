import base64
import json
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.analytics.detectors.low_demand_slots import detect_low_demand_slots
from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow
from app.metrics.store import InMemoryAppointmentMetricStore
from app.schemas.auth import AuthenticatedUser


def test_low_demand_slot_detector_finds_relative_weekday_slot_gap() -> None:
    rows = _twelve_week_demand_rows()

    result = detect_low_demand_slots(rows)

    candidate = next(item for item in result.candidates if item.weekday == "MONDAY" and item.slot_start_hour == 10)
    assert result.detector_version == "low-demand-slot-v1"
    assert result.observed_weeks == 12
    assert candidate.average_appointments_per_week == 1.0
    assert candidate.comparison_median_per_week == 3.5
    assert candidate.demand_index == 0.2857


def test_low_demand_slot_detector_requires_eight_weeks() -> None:
    result = detect_low_demand_slots(_twelve_week_demand_rows()[:21])

    assert result.observed_weeks == 3
    assert result.candidates == []
    assert "최소 8주" in result.limitations[0]


def test_low_demand_slot_api_scopes_to_active_tenant(monkeypatch) -> None:
    client, tenant_id, metric_store = _authenticated_client(monkeypatch)
    metric_store.register_rows(tenant_id=tenant_id, business_id="biz-a", rows=_twelve_week_demand_rows())
    metric_store.register_rows(tenant_id="other-tenant", business_id="biz-other", rows=_twelve_week_demand_rows())

    own = client.get("/api/v1/businesses/biz-a/detectors/low-demand-slots")
    other = client.get("/api/v1/businesses/biz-other/detectors/low-demand-slots")

    assert own.status_code == 200
    assert own.json()["candidates"]
    assert other.status_code == 404


def _twelve_week_demand_rows() -> list[AppointmentMetricRow]:
    rows: list[AppointmentMetricRow] = []
    first_monday = datetime.fromisoformat("2026-05-04T00:00:00+09:00")
    for week in range(12):
        day = first_monday + timedelta(weeks=week)
        rows.append(AppointmentMetricRow(visit_start_at=day.replace(hour=10), status="completed", paid_amount=None))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=14), status="completed", paid_amount=None) for _ in range(4))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=16), status="completed", paid_amount=None) for _ in range(3))
    return rows


def _authenticated_client(monkeypatch):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="detector-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Detector Tenant")
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
