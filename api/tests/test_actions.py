import base64
import json

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.actions.store import InMemoryActionStore
from app.auth.store import InMemoryAuthStore
from app.main import app
from app.schemas.auth import AuthenticatedUser, TenantMembership


ACTION_PAYLOAD = {
    "title": "화요일 오후 수동 혜택 실험",
    "execution_notes": "내부 검토를 마친 뒤 수동으로 실행합니다.",
    "planned_start_at": "2026-08-18T14:00:00+09:00",
    "planned_end_at": "2026-08-18T16:00:00+09:00",
    "planned_budget": {"amount": "0", "currency": "KRW"},
}


def test_approved_recommendation_creates_one_manual_action_and_records_transitions(monkeypatch) -> None:
    client, tenant_id, action_store = _authenticated_client(monkeypatch)
    action_store.register_recommendation(
        tenant_id=tenant_id, recommendation_id="rec-approved", status="approved",
        action_type="manual_time_slot_offer_test", channel="manual",
    )

    created = client.post("/api/v1/recommendations/rec-approved/actions", json=ACTION_PAYLOAD)
    replayed = client.post("/api/v1/recommendations/rec-approved/actions", json=ACTION_PAYLOAD)

    assert created.status_code == 201
    assert created.json()["action"]["status"] == "planned"
    assert created.json()["action"]["status_events"][0]["status"] == "planned"
    assert replayed.status_code == 200
    assert replayed.json()["replayed"] is True

    action_id = created.json()["action"]["id"]
    started = client.patch(f"/api/v1/actions/{action_id}", json={"status": "in_progress", "note": "수동 실행 시작"})
    completed = client.patch(f"/api/v1/actions/{action_id}", json={"status": "completed"})
    invalid = client.patch(f"/api/v1/actions/{action_id}", json={"status": "in_progress"})

    assert started.status_code == 200
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    assert [event["status"] for event in completed.json()["status_events"]] == ["planned", "in_progress", "completed"]
    assert invalid.status_code == 409


def test_action_cannot_be_created_until_recommendation_is_approved(monkeypatch) -> None:
    client, tenant_id, action_store = _authenticated_client(monkeypatch)
    action_store.register_recommendation(
        tenant_id=tenant_id, recommendation_id="rec-draft", status="draft",
        action_type="manual_time_slot_offer_test", channel="manual",
    )

    response = client.post("/api/v1/recommendations/rec-draft/actions", json=ACTION_PAYLOAD)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "CONFLICT"


def test_action_cannot_access_another_tenants_recommendation(monkeypatch) -> None:
    client, _, action_store = _authenticated_client(monkeypatch)
    action_store.register_recommendation(
        tenant_id="other-tenant", recommendation_id="rec-other", status="approved",
        action_type="manual_time_slot_offer_test", channel="manual",
    )

    response = client.post("/api/v1/recommendations/rec-other/actions", json=ACTION_PAYLOAD)

    assert response.status_code == 404


def test_viewer_cannot_create_or_change_actions(monkeypatch) -> None:
    client, tenant_id, action_store = _authenticated_client(monkeypatch)
    action_store.register_recommendation(
        tenant_id=tenant_id, recommendation_id="rec-viewer", status="approved",
        action_type="manual_time_slot_offer_test", channel="manual",
    )
    auth_store = app.state.auth_store
    user_id = next(iter(auth_store.memberships))
    auth_store.memberships[user_id] = [TenantMembership(tenant_id=tenant_id, name="Action Tenant", role="viewer")]

    response = client.post("/api/v1/recommendations/rec-viewer/actions", json=ACTION_PAYLOAD)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"


def test_business_action_history_is_tenant_scoped_and_newest_first(monkeypatch) -> None:
    client, tenant_id, action_store = _authenticated_client(monkeypatch)
    action_store.register_recommendation(tenant_id=tenant_id, recommendation_id="rec-history-old", status="approved", action_type="manual_time_slot_offer_test", channel="manual", business_id="business-history")
    action_store.register_recommendation(tenant_id=tenant_id, recommendation_id="rec-history-new", status="approved", action_type="manual_time_slot_offer_test", channel="manual", business_id="business-history")
    old = client.post("/api/v1/recommendations/rec-history-old/actions", json=ACTION_PAYLOAD).json()["action"]
    new = client.post("/api/v1/recommendations/rec-history-new/actions", json={**ACTION_PAYLOAD, "title": "새 실행"}).json()["action"]

    history = client.get("/api/v1/businesses/business-history/actions")
    other_business = client.get("/api/v1/businesses/business-other/actions")

    assert history.status_code == 200
    assert [item["id"] for item in history.json()] == [new["id"], old["id"]]
    assert other_business.status_code == 404


def _authenticated_client(monkeypatch):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="action-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Action Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    action_store = InMemoryActionStore()
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "action_store", action_store)
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))
    return client, tenant.tenant_id, action_store


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
