from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_current_user_requires_authentication() -> None:
    response = client.get("/api/v1/auth/me", headers={"X-Request-ID": "request-1"})

    assert response.status_code == 401
    assert response.json()["error"] == {
        "code": "AUTHENTICATION_REQUIRED",
        "message": "로그인이 필요합니다.",
        "details": [],
        "request_id": "request-1",
    }


def test_login_requires_oauth_environment_configuration() -> None:
    response = client.get("/api/v1/auth/google/login")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "AUTH_CONFIGURATION_REQUIRED"
    assert "SESSION_SECRET" in response.json()["error"]["message"]
