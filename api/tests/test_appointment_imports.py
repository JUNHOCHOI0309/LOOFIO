import base64
import json

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.auth.store import InMemoryAuthStore
from app.imports.appointments import parse_appointments_csv
from app.imports.store import InMemoryAppointmentImportStore
from app.main import app
from app.schemas.auth import AuthenticatedUser


VALID_CSV = (
    "appointment_id,location_key,customer_token,visit_start_at,visit_end_at,booked_at,offering_name,status,listed_price,paid_amount,discount_amount,source,source_record_id\n"
    "apt-1,loc-a,tokenized-customer-001,2026-08-13T10:00:00+09:00,2026-08-13T10:30:00+09:00,2026-08-10T10:00:00+09:00,피코토닝,완료,100000,90000,10000,sample_csv,record-1\n"
)


def test_preview_normalizes_valid_appointments_csv(monkeypatch) -> None:
    client, _, _ = _authenticated_client(monkeypatch)

    response = client.post("/api/v1/businesses/biz-a/imports/appointments/preview", files=_csv_file(VALID_CSV))

    assert response.status_code == 200
    body = response.json()
    assert body["valid_rows"] == 1
    assert body["invalid_rows"] == 0
    assert body["preview"][0]["status"] == "completed"
    assert body["preview"][0]["customer_token_present"] is True


def test_preview_requires_an_authenticated_active_tenant() -> None:
    client = TestClient(app)

    response = client.post("/api/v1/businesses/biz-a/imports/appointments/preview", files=_csv_file(VALID_CSV))

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_preview_rejects_csv_without_required_columns(monkeypatch) -> None:
    client, _, _ = _authenticated_client(monkeypatch)

    response = client.post(
        "/api/v1/businesses/biz-a/imports/appointments/preview",
        files=_csv_file("appointment_id,status\napt-1,완료\n"),
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "Missing required columns" in error["details"][0]


def test_normalizer_drops_unallowlisted_source_columns() -> None:
    parsed = parse_appointments_csv((VALID_CSV.rstrip() + ",phone\n").encode("utf-8"))

    assert parsed.errors == []
    assert "phone" not in parsed.rows[0].raw_payload


def test_import_persists_once_replays_same_key_and_reports_source_duplicates(monkeypatch) -> None:
    client, _, import_store = _authenticated_client(monkeypatch)
    url = "/api/v1/businesses/biz-a/imports/appointments"

    first = client.post(url, headers={"Idempotency-Key": "import-1"}, files=_csv_file(VALID_CSV))
    replay = client.post(url, headers={"Idempotency-Key": "import-1"}, files=_csv_file(VALID_CSV))
    duplicate = client.post(url, headers={"Idempotency-Key": "import-2"}, files=_csv_file(VALID_CSV))

    assert first.status_code == 201
    assert first.json()["imported_rows"] == 1
    assert replay.status_code == 200
    assert replay.json()["replayed"] is True
    assert duplicate.status_code == 201
    assert duplicate.json()["imported_rows"] == 0
    assert duplicate.json()["duplicate_rows"] == 1
    assert len(import_store.source_records) == 1


def test_import_rejects_invalid_rows_without_creating_import(monkeypatch) -> None:
    client, _, import_store = _authenticated_client(monkeypatch)
    invalid_csv = VALID_CSV.replace("tokenized-customer-001", "raw-identifier")

    response = client.post(
        "/api/v1/businesses/biz-a/imports/appointments",
        headers={"Idempotency-Key": "invalid-import"},
        files=_csv_file(invalid_csv),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert import_store.imports == {}


def test_import_cannot_access_another_tenants_business(monkeypatch) -> None:
    client, _, import_store = _authenticated_client(monkeypatch)
    import_store.register_business(tenant_id="other-tenant", business_id="biz-other")

    response = client.post(
        "/api/v1/businesses/biz-other/imports/appointments",
        headers={"Idempotency-Key": "forbidden-import"},
        files=_csv_file(VALID_CSV),
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_import_requires_idempotency_key(monkeypatch) -> None:
    client, _, _ = _authenticated_client(monkeypatch)

    response = client.post("/api/v1/businesses/biz-a/imports/appointments", files=_csv_file(VALID_CSV))

    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_preview_rejects_non_csv_with_standard_error_contract(monkeypatch) -> None:
    client, _, _ = _authenticated_client(monkeypatch)

    response = client.post(
        "/api/v1/businesses/biz-a/imports/appointments/preview",
        headers={"X-Request-ID": "request-123"},
        files={"file": ("appointments.xlsx", b"not-a-csv", "application/octet-stream")},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "CSV 파일이 필요합니다.",
            "details": [],
            "request_id": "request-123",
        }
    }


def test_request_validation_uses_standard_error_contract() -> None:
    response = TestClient(app).post("/api/v1/businesses/biz-a/imports/appointments/preview")

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"] == "요청을 처리할 수 없습니다."
    assert error["details"]


def test_csv_preview_allows_local_web_origin() -> None:
    response = TestClient(app).options(
        "/api/v1/businesses/biz-a/imports/appointments/preview",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "idempotency-key" in response.headers["access-control-allow-headers"].lower()


def _authenticated_client(monkeypatch):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="import-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Import Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    import_store = InMemoryAppointmentImportStore()
    import_store.register_business(tenant_id=tenant.tenant_id, business_id="biz-a")
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "import_store", import_store)
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))
    return client, tenant, import_store


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")


def _csv_file(content: str):
    return {"file": ("appointments.csv", content, "text/csv")}
