from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    provider: str
    provider_subject: str
    email: str | None = None
    display_name: str | None = None
