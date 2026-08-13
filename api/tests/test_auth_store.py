from app.auth.store import InMemoryAuthStore
from app.schemas.auth import AuthenticatedUser, TenantMembership


def test_in_memory_session_is_opaque_and_revocable() -> None:
    store = InMemoryAuthStore()
    user = store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="subject-1", email="user@example.com"))
    session_id = store.create_session(user.user_id)

    assert store.resolve_session(session_id).user_id == user.user_id
    store.revoke_session(session_id)
    assert store.resolve_session(session_id) is None


def test_active_tenant_must_be_a_user_membership() -> None:
    store = InMemoryAuthStore()
    user = store.find_or_create_user(AuthenticatedUser(provider="naver", provider_subject="subject-1"))
    session_id = store.create_session(user.user_id)
    store.memberships[user.user_id] = [TenantMembership(tenant_id="tenant-a", name="A 병원", role="owner")]

    assert store.switch_active_tenant(session_id, "tenant-b") is None
    assert store.switch_active_tenant(session_id, "tenant-a").active_tenant_id == "tenant-a"


def test_new_tenant_creates_owner_membership_and_can_be_activated() -> None:
    store = InMemoryAuthStore()
    user = store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="subject-2"))
    session_id = store.create_session(user.user_id)

    tenant = store.create_tenant(user.user_id, "  LOOFIO 피부과  ")

    assert tenant.name == "LOOFIO 피부과"
    assert tenant.role == "owner"
    assert store.switch_active_tenant(session_id, tenant.tenant_id).active_tenant_id == tenant.tenant_id


def test_businesses_are_scoped_to_their_tenant() -> None:
    store = InMemoryAuthStore()
    user = store.find_or_create_user(AuthenticatedUser(provider="google", provider_subject="subject-3"))
    tenant = store.create_tenant(user.user_id, "LOOFIO 피부과")

    business = store.create_business_with_location(
        tenant.tenant_id, "LOOFIO 피부과", "DERMATOLOGY", "강남점", "Asia/Seoul"
    )

    assert store.list_businesses(tenant.tenant_id) == [business]
    assert store.list_businesses("another-tenant") == []
