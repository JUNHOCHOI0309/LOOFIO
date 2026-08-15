import base64
import json
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.analytics.detectors.service_demand_gaps import detect_service_demand_gaps
from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow
from app.metrics.store import InMemoryAppointmentMetricStore
from app.schemas.auth import AuthenticatedUser


def test_service_demand_gap_finds_underrepresented_offering_in_observed_slot() -> None:
    result = detect_service_demand_gaps(_service_demand_rows())

    candidate = next(item for item in result.candidates if item.offering_name == "클리닉" and item.slot_start_hour == 10)
    assert result.detector_version == "service-demand-gap-v1"
    assert result.observed_weeks == 12
    assert candidate.offering_appointment_count == 60
    assert candidate.slot_appointment_count == 108
    assert candidate.slot_offering_appointment_count == 12
    assert candidate.business_offering_share == 0.2941
    assert candidate.slot_offering_share == 0.1111
    assert candidate.expected_slot_offering_appointment_count == 31.7647
    assert candidate.share_index == 0.3778


def test_service_demand_gap_requires_eight_weeks() -> None:
    result = detect_service_demand_gaps(_service_demand_rows()[:119])

    assert result.candidates == []
    assert "최소 8주" in result.limitations[0]


def test_service_demand_gap_api_scopes_to_active_tenant(monkeypatch) -> None:
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="service-demand-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Service Demand Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    metric_store = InMemoryAppointmentMetricStore()
    metric_store.register_rows(tenant_id=tenant.tenant_id, business_id="biz-a", rows=_service_demand_rows())
    metric_store.register_rows(tenant_id="other-tenant", business_id="biz-other", rows=_service_demand_rows())
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "metric_store", metric_store)
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))

    own = client.get("/api/v1/businesses/biz-a/detectors/service-demand-gaps")
    other = client.get("/api/v1/businesses/biz-other/detectors/service-demand-gaps")

    assert own.status_code == 200
    assert own.json()["candidates"]
    assert other.status_code == 404


def _service_demand_rows() -> list[AppointmentMetricRow]:
    rows: list[AppointmentMetricRow] = []
    first_monday = datetime.fromisoformat("2026-05-04T00:00:00+09:00")
    for week in range(12):
        day = first_monday + timedelta(weeks=week)
        rows.append(AppointmentMetricRow(visit_start_at=day.replace(hour=10), status="completed", paid_amount=None, offering_name="클리닉"))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=10), status="completed", paid_amount=None, offering_name="일반 진료") for _ in range(8))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=14), status="completed", paid_amount=None, offering_name="클리닉") for _ in range(4))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=14), status="completed", paid_amount=None, offering_name="일반 진료") for _ in range(4))
    return rows


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
