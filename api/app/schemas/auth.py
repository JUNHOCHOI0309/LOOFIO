from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    user_id: str | None = None
    active_tenant_id: str | None = None
    provider: str
    provider_subject: str
    email: str | None = None
    display_name: str | None = None


class TenantMembership(BaseModel):
    tenant_id: str
    name: str
    role: str
