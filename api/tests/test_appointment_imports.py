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
    assert "Missing required columns" in response.json()["detail"]


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
