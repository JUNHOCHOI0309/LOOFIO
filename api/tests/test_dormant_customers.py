import base64
import json
from datetime import date, datetime

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.analytics.detectors.dormant_customers import detect_dormant_customers
from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow
from app.metrics.store import InMemoryAppointmentMetricStore
from app.schemas.auth import AuthenticatedUser


def test_dormant_customer_prefers_individual_revisit_cycle_and_deduplicates_same_day_visits() -> None:
    result = detect_dormant_customers(_individual_cycle_rows(), as_of_date=date(2026, 8, 6))

    candidate = next(item for item in result.candidates if item.customer_token == _token("individual"))
    assert result.detector_version == "dormant-customer-v1"
    assert candidate.completed_visit_count == 3
    assert candidate.last_completed_visit_date == date(2026, 6, 26)
    assert candidate.expected_revisit_days == 28.0
    assert candidate.overdue_ratio == 1.4643
    assert candidate.baseline_source == "individual"
    assert candidate.reference_interval_count == 2


def test_dormant_customer_uses_offering_cycle_when_individual_history_is_insufficient() -> None:
    sleeping_token = _token("offering-sleeper")
    rows = [AppointmentMetricRow(datetime.fromisoformat("2026-06-01T10:00:00+09:00"), "completed", None, "검사", sleeping_token)]
    for index in range(10):
        token = _token(f"cohort-{index}")
        rows.extend([
            AppointmentMetricRow(datetime.fromisoformat("2026-05-01T10:00:00+09:00"), "completed", None, "검사", token),
            AppointmentMetricRow(datetime.fromisoformat("2026-05-29T10:00:00+09:00"), "completed", None, "검사", token),
        ])

    result = detect_dormant_customers(rows, as_of_date=date(2026, 8, 1))

    candidate = next(item for item in result.candidates if item.customer_token == sleeping_token)
    assert candidate.expected_revisit_days == 28.0
    assert candidate.baseline_source == "offering"
    assert candidate.reference_interval_count == 10


def test_dormant_customer_does_not_cross_overdue_ratio_boundary() -> None:
    result = detect_dormant_customers(_individual_cycle_rows(), as_of_date=date(2026, 8, 1))

    assert result.candidates == []


def test_dormant_customer_api_requires_as_of_date_and_scopes_to_active_tenant(monkeypatch) -> None:
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="dormant-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Dormant Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    metric_store = InMemoryAppointmentMetricStore()
    metric_store.register_rows(tenant_id=tenant.tenant_id, business_id="biz-a", rows=_individual_cycle_rows())
    metric_store.register_rows(tenant_id="other-tenant", business_id="biz-other", rows=_individual_cycle_rows())
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "metric_store", metric_store)
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))

    missing_date = client.get("/api/v1/businesses/biz-a/detectors/dormant-customers")
    own = client.get("/api/v1/businesses/biz-a/detectors/dormant-customers?as_of_date=2026-08-06")
    other = client.get("/api/v1/businesses/biz-other/detectors/dormant-customers?as_of_date=2026-08-06")

    assert missing_date.status_code == 422
    assert own.status_code == 200
    assert own.json()["candidates"]
    assert other.status_code == 404


def _individual_cycle_rows() -> list[AppointmentMetricRow]:
    token = _token("individual")
    return [
        AppointmentMetricRow(datetime.fromisoformat("2026-05-01T10:00:00+09:00"), "completed", None, "일반 진료", token),
        AppointmentMetricRow(datetime.fromisoformat("2026-05-01T16:00:00+09:00"), "completed", None, "검사", token),
        AppointmentMetricRow(datetime.fromisoformat("2026-05-29T10:00:00+09:00"), "completed", None, "일반 진료", token),
        AppointmentMetricRow(datetime.fromisoformat("2026-06-26T10:00:00+09:00"), "completed", None, "일반 진료", token),
    ]


def _token(label: str) -> str:
    return f"customer-token-{label:0<24}"


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
