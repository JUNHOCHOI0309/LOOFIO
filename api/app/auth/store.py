from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol
from uuid import uuid4

import psycopg
from psycopg.rows import dict_row

from app.schemas.auth import AuthenticatedUser, TenantMembership


class AuthStoreUnavailable(RuntimeError):
    """Raised when an auth operation needs a database that is not configured or reachable."""


class AuthStore(Protocol):
    def find_or_create_user(self, identity: AuthenticatedUser) -> AuthenticatedUser: ...
    def create_session(self, user_id: str) -> str: ...
    def resolve_session(self, session_id: str) -> AuthenticatedUser | None: ...
    def revoke_session(self, session_id: str) -> None: ...
    def list_tenants(self, user_id: str) -> list[TenantMembership]: ...
    def create_tenant(self, user_id: str, name: str) -> TenantMembership: ...
    def switch_active_tenant(self, session_id: str, tenant_id: str) -> AuthenticatedUser | None: ...


class PostgresAuthStore:
    def __init__(self, database_url: str | None) -> None:
        self.database_url = database_url

    def find_or_create_user(self, identity: AuthenticatedUser) -> AuthenticatedUser:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT u.id, u.email, u.display_name FROM user_identities i "
                "JOIN users u ON u.id = i.user_id WHERE i.provider = %s AND i.provider_subject = %s",
                (identity.provider, identity.provider_subject),
            )
            existing = cursor.fetchone()
            if existing:
                return AuthenticatedUser(
                    user_id=str(existing["id"]), provider=identity.provider, provider_subject=identity.provider_subject,
                    email=existing["email"], display_name=existing["display_name"],
                )
            cursor.execute(
                "INSERT INTO users (email, display_name) VALUES (%s, %s) RETURNING id",
                (identity.email, identity.display_name),
            )
            user_id = str(cursor.fetchone()["id"])
            cursor.execute(
                "INSERT INTO user_identities (user_id, provider, provider_subject, email_at_link_time) VALUES (%s, %s, %s, %s)",
                (user_id, identity.provider, identity.provider_subject, identity.email),
            )
            return identity.model_copy(update={"user_id": user_id})

    def create_session(self, user_id: str) -> str:
        session_id = str(uuid4())
        expiry = datetime.now(timezone.utc) + timedelta(days=14)
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sessions (id, user_id, expires_at) VALUES (%s, %s, %s)",
                (session_id, user_id, expiry),
            )
        return session_id

    def resolve_session(self, session_id: str) -> AuthenticatedUser | None:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT s.user_id, s.active_tenant_id, u.email, u.display_name, i.provider, i.provider_subject "
                "FROM sessions s JOIN users u ON u.id = s.user_id "
                "JOIN user_identities i ON i.user_id = u.id "
                "WHERE s.id = %s AND s.revoked_at IS NULL AND s.expires_at > now() "
                "ORDER BY i.created_at ASC LIMIT 1",
                (session_id,),
            )
            row = cursor.fetchone()
            if not row:
                return None
            return AuthenticatedUser(
                user_id=str(row["user_id"]), active_tenant_id=_optional_id(row["active_tenant_id"]),
                provider=row["provider"], provider_subject=row["provider_subject"],
                email=row["email"], display_name=row["display_name"],
            )

    def revoke_session(self, session_id: str) -> None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute("UPDATE sessions SET revoked_at = now() WHERE id = %s", (session_id,))

    def list_tenants(self, user_id: str) -> list[TenantMembership]:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute(
                "SELECT t.id, t.name, tm.role FROM tenant_members tm JOIN tenants t ON t.id = tm.tenant_id "
                "WHERE tm.user_id = %s ORDER BY t.created_at ASC",
                (user_id,),
            )
            return [TenantMembership(tenant_id=str(row["id"]), name=row["name"], role=row["role"]) for row in cursor.fetchall()]

    def create_tenant(self, user_id: str, name: str) -> TenantMembership:
        with self._connection() as connection, connection.cursor(row_factory=dict_row) as cursor:
            cursor.execute("INSERT INTO tenants (name) VALUES (%s) RETURNING id, name", (name.strip(),))
            tenant = cursor.fetchone()
            cursor.execute(
                "INSERT INTO tenant_members (tenant_id, user_id, role) VALUES (%s, %s, 'owner')",
                (tenant["id"], user_id),
            )
            return TenantMembership(tenant_id=str(tenant["id"]), name=tenant["name"], role="owner")

    def switch_active_tenant(self, session_id: str, tenant_id: str) -> AuthenticatedUser | None:
        with self._connection() as connection, connection.cursor() as cursor:
            cursor.execute(
                "UPDATE sessions s SET active_tenant_id = %s "
                "WHERE s.id = %s AND s.revoked_at IS NULL AND s.expires_at > now() "
                "AND EXISTS (SELECT 1 FROM tenant_members tm WHERE tm.tenant_id = %s AND tm.user_id = s.user_id)",
                (tenant_id, session_id, tenant_id),
            )
            if cursor.rowcount != 1:
                return None
        return self.resolve_session(session_id)

    def _connection(self):
        if not self.database_url:
            raise AuthStoreUnavailable("DATABASE_URL 환경 변수가 필요합니다.")
        try:
            return psycopg.connect(self.database_url.replace("postgresql+psycopg://", "postgresql://", 1))
        except psycopg.Error as error:
            raise AuthStoreUnavailable("인증 데이터베이스에 연결할 수 없습니다.") from error


@dataclass
class InMemoryAuthStore:
    """Test-only AuthStore implementation; never configure this in an application environment."""

    users: dict[tuple[str, str], AuthenticatedUser]
    sessions: dict[str, AuthenticatedUser]
    memberships: dict[str, list[TenantMembership]]

    def __init__(self) -> None:
        self.users = {}
        self.sessions = {}
        self.memberships = {}

    def find_or_create_user(self, identity: AuthenticatedUser) -> AuthenticatedUser:
        key = (identity.provider, identity.provider_subject)
        existing = self.users.get(key)
        if existing:
            return existing
        user = identity.model_copy(update={"user_id": str(uuid4())})
        self.users[key] = user
        self.memberships[user.user_id] = []
        return user

    def create_session(self, user_id: str) -> str:
        user = next(user for user in self.users.values() if user.user_id == user_id)
        session_id = str(uuid4())
        self.sessions[session_id] = user
        return session_id

    def resolve_session(self, session_id: str) -> AuthenticatedUser | None:
        return self.sessions.get(session_id)

    def revoke_session(self, session_id: str) -> None:
        self.sessions.pop(session_id, None)

    def list_tenants(self, user_id: str) -> list[TenantMembership]:
        return self.memberships.get(user_id, [])

    def create_tenant(self, user_id: str, name: str) -> TenantMembership:
        membership = TenantMembership(tenant_id=str(uuid4()), name=name.strip(), role="owner")
        self.memberships.setdefault(user_id, []).append(membership)
        return membership

    def switch_active_tenant(self, session_id: str, tenant_id: str) -> AuthenticatedUser | None:
        user = self.sessions.get(session_id)
        if not user or tenant_id not in {membership.tenant_id for membership in self.list_tenants(user.user_id)}:
            return None
        updated = user.model_copy(update={"active_tenant_id": tenant_id})
        self.sessions[session_id] = updated
        self.users[(updated.provider, updated.provider_subject)] = updated
        return updated


def _optional_id(value: object) -> str | None:
    return str(value) if value is not None else None
