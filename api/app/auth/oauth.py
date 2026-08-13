import os
from dataclasses import dataclass
from urllib.parse import urlparse

from authlib.integrations.starlette_client import OAuth, StarletteOAuth2App
from dotenv import load_dotenv

from app.schemas.auth import AuthenticatedUser

GOOGLE_METADATA_URL = "https://accounts.google.com/.well-known/openid-configuration"
NAVER_AUTHORIZE_URL = "https://nid.naver.com/oauth2.0/authorize"
NAVER_TOKEN_URL = "https://nid.naver.com/oauth2.0/token"
NAVER_PROFILE_URL = "https://openapi.naver.com/v1/nid/me"

load_dotenv()


class OAuthConfigurationError(ValueError):
    """Raised when an OAuth flow is requested without safe environment configuration."""


@dataclass(frozen=True)
class OAuthSettings:
    app_origin: str
    api_origin: str
    google_client_id: str
    google_client_secret: str
    naver_client_id: str
    naver_client_secret: str


def get_settings() -> OAuthSettings:
    session_secret = os.getenv("SESSION_SECRET")
    app_origin = os.getenv("APP_ORIGIN", "http://localhost:3000").rstrip("/")
    api_origin = os.getenv("API_ORIGIN", "http://localhost:8000").rstrip("/")
    _require_https_outside_localhost(app_origin, "APP_ORIGIN")
    _require_https_outside_localhost(api_origin, "API_ORIGIN")
    if not session_secret:
        raise OAuthConfigurationError("SESSION_SECRET 환경 변수가 필요합니다.")
    return OAuthSettings(
        app_origin=app_origin,
        api_origin=api_origin,
        google_client_id=os.getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
        google_client_secret=os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", ""),
        naver_client_id=os.getenv("NAVER_OAUTH_CLIENT_ID", ""),
        naver_client_secret=os.getenv("NAVER_OAUTH_CLIENT_SECRET", ""),
    )


def get_oauth_client(provider: str, settings: OAuthSettings) -> StarletteOAuth2App:
    oauth = OAuth()
    if provider == "google":
        _require_provider_values(settings.google_client_id, settings.google_client_secret, "Google")
        return oauth.register(
            name="google",
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            server_metadata_url=GOOGLE_METADATA_URL,
            client_kwargs={"scope": "openid email profile"},
        )
    if provider == "naver":
        _require_provider_values(settings.naver_client_id, settings.naver_client_secret, "Naver")
        return oauth.register(
            name="naver",
            client_id=settings.naver_client_id,
            client_secret=settings.naver_client_secret,
            authorize_url=NAVER_AUTHORIZE_URL,
            access_token_url=NAVER_TOKEN_URL,
            api_base_url="https://openapi.naver.com/v1/",
        )
    raise OAuthConfigurationError("지원하지 않는 로그인 제공자입니다.")


async def profile_from_token(
    provider: str, client: StarletteOAuth2App, token: dict[object, object]
) -> AuthenticatedUser:
    if provider == "google":
        userinfo = token.get("userinfo")
        if not isinstance(userinfo, dict):
            userinfo = await client.userinfo(token=token)
        subject = userinfo.get("sub")
        if not isinstance(subject, str):
            raise OAuthConfigurationError("Google 사용자 식별자를 확인하지 못했습니다.")
        return AuthenticatedUser(
            provider="google",
            provider_subject=subject,
            email=_string_or_none(userinfo.get("email")),
            display_name=_string_or_none(userinfo.get("name")),
        )

    response = await client.get("nid/me", token=token)
    payload = response.json()
    profile = payload.get("response", {})
    subject = profile.get("id")
    if not isinstance(subject, str):
        raise OAuthConfigurationError("Naver 사용자 식별자를 확인하지 못했습니다.")
    return AuthenticatedUser(
        provider="naver",
        provider_subject=subject,
        email=_string_or_none(profile.get("email")),
        display_name=_string_or_none(profile.get("name") or profile.get("nickname")),
    )


def _require_provider_values(client_id: str, client_secret: str, provider_name: str) -> None:
    if not client_id or not client_secret:
        raise OAuthConfigurationError(f"{provider_name} OAuth Client ID와 Client Secret 환경 변수가 필요합니다.")


def _require_https_outside_localhost(origin: str, variable_name: str) -> None:
    parsed = urlparse(origin)
    if not parsed.scheme or not parsed.netloc:
        raise OAuthConfigurationError(f"{variable_name}은(는) 완전한 origin URL이어야 합니다.")
    if parsed.hostname not in {"localhost", "127.0.0.1"} and parsed.scheme != "https":
        raise OAuthConfigurationError(f"{variable_name}은(는) localhost 외 환경에서 HTTPS를 사용해야 합니다.")


def _string_or_none(value: object) -> str | None:
    return value if isinstance(value, str) else None
