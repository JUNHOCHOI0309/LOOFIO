import base64
import copy
import json
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner

from app.auth.store import InMemoryAuthStore
from app.main import app
from app.metrics.appointments import AppointmentMetricRow
from app.opportunities.low_demand import build_low_demand_opportunity_drafts
from app.opportunities.store import InMemoryOpportunityStore
from app.schemas.auth import AuthenticatedUser, TenantMembership


FIXTURE = Path(__file__).parent / "fixtures" / "decisioning" / "low_demand" / "context_d4_v1.json"
AS_OF = "2026-08-18T12:00:00+09:00"


def test_cause_preview_is_scoped_unpersisted_and_deterministic(monkeypatch) -> None:
    client, tenant_id, business_id, opportunity_id, opportunity_store = _authenticated_client(monkeypatch)
    payload = _preview_payload(tenant_id=tenant_id, business_id=business_id)
    url = f"/api/v1/opportunities/{opportunity_id}/cause-analyses/preview"

    first = client.post(url, json=payload)
    second = client.post(url, json=copy.deepcopy(payload))

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    body = first.json()
    assert body["preview"]["persisted"] is False
    assert body["preview"]["preview_id"].startswith("CAUSE_PREVIEW_")
    assert body["preview"]["input_hash"] == body["preview"]["input_hash"]
    assert body["cause_analysis"]["generated_at"] == AS_OF
    assert body["decision_context"]["tenant_id"] == tenant_id
    assert body["decision_context"]["business_id"] == business_id
    assert body["cause_analysis"]["opportunity_id"] == opportunity_id
    assert body["cause_analysis"]["candidates"][0]["hypothesis"].endswith("가능성이 있습니다.")
    assert body["cause_analysis"]["candidates"][0]["opportunity_evidence_refs"] == [
        f"OPPORTUNITY:{opportunity_id}:OBSERVATION"
    ]
    assert len(opportunity_store.opportunities) == 1


def test_cause_preview_requires_authenticated_editor_role(monkeypatch) -> None:
    client, tenant_id, business_id, opportunity_id, _ = _authenticated_client(monkeypatch)
    payload = _preview_payload(tenant_id=tenant_id, business_id=business_id)
    url = f"/api/v1/opportunities/{opportunity_id}/cause-analyses/preview"

    anonymous = TestClient(app).post(url, json=payload)
    assert anonymous.status_code == 401
    assert anonymous.json()["error"]["code"] == "AUTHENTICATION_REQUIRED"

    auth_store = app.state.auth_store
    user_id = next(iter(auth_store.memberships))
    auth_store.memberships[user_id] = [
        TenantMembership(tenant_id=tenant_id, name="Cause Preview Tenant", role="viewer")
    ]
    viewer = client.post(url, json=payload)
    assert viewer.status_code == 403
    assert viewer.json()["error"]["code"] == "FORBIDDEN"


def test_cause_preview_hides_other_tenant_opportunity_and_rejects_pii(monkeypatch) -> None:
    client, tenant_id, business_id, opportunity_id, opportunity_store = _authenticated_client(monkeypatch)
    payload = _preview_payload(tenant_id=tenant_id, business_id=business_id)
    other = _other_tenant_opportunity(opportunity_store)

    cross_tenant = client.post(
        f"/api/v1/opportunities/{other}/cause-analyses/preview", json=payload
    )
    assert cross_tenant.status_code == 404
    assert cross_tenant.json()["error"]["code"] == "NOT_FOUND"

    payload["decision_context"]["patient_name"] = "not-allowed"
    pii = client.post(
        f"/api/v1/opportunities/{opportunity_id}/cause-analyses/preview", json=payload
    )
    assert pii.status_code == 422
    assert pii.json()["error"]["code"] == "PII_FIELD_REJECTED"
    assert "not-allowed" not in json.dumps(pii.json(), ensure_ascii=False)


def test_cause_preview_rejects_client_controlled_opportunity_and_naive_as_of(monkeypatch) -> None:
    client, tenant_id, business_id, opportunity_id, _ = _authenticated_client(monkeypatch)
    payload = _preview_payload(tenant_id=tenant_id, business_id=business_id)
    url = f"/api/v1/opportunities/{opportunity_id}/cause-analyses/preview"

    payload["decision_context"]["observation"] = {"demand_index": 0}
    injected = client.post(url, json=payload)
    assert injected.status_code == 422
    assert injected.json()["error"]["code"] == "DECISION_CONTEXT_INVALID"

    payload = _preview_payload(tenant_id=tenant_id, business_id=business_id)
    payload["as_of"] = "2026-08-18T12:00:00"
    naive = client.post(url, json=payload)
    assert naive.status_code == 422
    assert naive.json()["error"]["code"] == "DECISION_CONTEXT_INVALID"


def _preview_payload(*, tenant_id: str, business_id: str) -> dict:
    context = json.loads(FIXTURE.read_text(encoding="utf-8"))
    for field in {
        "tenant_id",
        "business_id",
        "opportunity_id",
        "snapshot_id",
        "snapshot_at",
        "context_hash",
        "opportunity",
        "observation",
    }:
        context.pop(field, None)
    _replace_scope(context, tenant_id=tenant_id, business_id=business_id)
    return {"contract_version": "cause-preview-v1", "as_of": AS_OF, "decision_context": context}


def _replace_scope(value: object, *, tenant_id: str, business_id: str) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "tenant_id":
                value[key] = tenant_id
            elif key == "business_id":
                value[key] = business_id
            else:
                _replace_scope(item, tenant_id=tenant_id, business_id=business_id)
    elif isinstance(value, list):
        for item in value:
            _replace_scope(item, tenant_id=tenant_id, business_id=business_id)


def _authenticated_client(monkeypatch):
    auth_store = InMemoryAuthStore()
    user = auth_store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="cause-preview-user"))
    session_id = auth_store.create_session(user.user_id)
    tenant = auth_store.create_tenant(user.user_id, "Cause Preview Tenant")
    auth_store.switch_active_tenant(session_id, tenant.tenant_id)
    opportunity_store = InMemoryOpportunityStore()
    business_id = "cause-preview-business"
    opportunity = opportunity_store.refresh_low_demand(
        tenant_id=tenant.tenant_id,
        business_id=business_id,
        drafts=build_low_demand_opportunity_drafts(_low_demand_rows()),
    )[0]
    monkeypatch.setattr(app.state, "auth_store", auth_store)
    monkeypatch.setattr(app.state, "opportunity_store", opportunity_store)
    client = TestClient(app)
    client.cookies.set("session", _signed_session_cookie(session_id))
    return client, tenant.tenant_id, business_id, opportunity.id, opportunity_store


def _other_tenant_opportunity(store: InMemoryOpportunityStore) -> str:
    return store.refresh_low_demand(
        tenant_id="other-tenant",
        business_id="other-business",
        drafts=build_low_demand_opportunity_drafts(_low_demand_rows()),
    )[0].id


def _low_demand_rows() -> list[AppointmentMetricRow]:
    rows: list[AppointmentMetricRow] = []
    first_monday = datetime.fromisoformat("2026-05-04T00:00:00+09:00")
    for week in range(12):
        day = first_monday + timedelta(weeks=week)
        rows.append(AppointmentMetricRow(visit_start_at=day.replace(hour=10), status="completed", paid_amount=Decimal("30000")))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=14), status="completed", paid_amount=Decimal("30000")) for _ in range(4))
        rows.extend(AppointmentMetricRow(visit_start_at=day.replace(hour=16), status="completed", paid_amount=Decimal("30000")) for _ in range(3))
    return rows


def _signed_session_cookie(session_id: str) -> str:
    middleware = next(middleware for middleware in app.user_middleware if middleware.cls.__name__ == "SessionMiddleware")
    payload = base64.b64encode(json.dumps({"session_id": session_id}).encode("utf-8"))
    return TimestampSigner(str(middleware.kwargs["secret_key"])).sign(payload).decode("utf-8")
