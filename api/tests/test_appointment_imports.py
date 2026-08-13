from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_preview_normalizes_valid_appointments_csv() -> None:
    response = client.post(
        "/api/v1/businesses/biz_demo/imports/appointments/preview",
        files={
            "file": (
                "appointments.csv",
                "appointment_id,visit_start_at,visit_end_at,offering_name,status,customer_token\n"
                "apt-1,2026-08-13T10:00:00+09:00,2026-08-13T10:30:00+09:00,피코토닝,완료,tokenized-customer-001\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["valid_rows"] == 1
    assert body["invalid_rows"] == 0
    assert body["preview"][0]["status"] == "completed"
    assert body["preview"][0]["customer_token_present"] is True


def test_preview_rejects_csv_without_required_columns() -> None:
    response = client.post(
        "/api/v1/businesses/biz_demo/imports/appointments/preview",
        files={"file": ("appointments.csv", "appointment_id,status\napt-1,완료\n", "text/csv")},
    )

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert "Missing required columns" in error["details"][0]
    assert error["request_id"]


def test_preview_reports_invalid_rows_without_storing_raw_identifier() -> None:
    response = client.post(
        "/api/v1/businesses/biz_demo/imports/appointments/preview",
        files={
            "file": (
                "appointments.csv",
                "appointment_id,visit_start_at,offering_name,status,customer_token\n"
                "apt-1,2026-08-13T10:00:00,피코토닝,완료,01012345678\n",
                "text/csv",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["invalid_rows"] == 1
    assert "UTC offset" in body["errors"][0]


def test_preview_rejects_non_csv_with_standard_error_contract() -> None:
    response = client.post(
        "/api/v1/businesses/biz_demo/imports/appointments/preview",
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
    response = client.post("/api/v1/businesses/biz_demo/imports/appointments/preview")

    assert response.status_code == 422
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["message"] == "요청을 처리할 수 없습니다."
    assert error["details"]


def test_csv_preview_allows_local_web_origin() -> None:
    response = client.options(
        "/api/v1/businesses/biz_demo/imports/appointments/preview",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
