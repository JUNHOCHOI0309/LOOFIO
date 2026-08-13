from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.auth.oauth import OAuthConfigurationError, get_oauth_client, get_settings, profile_from_token
from app.schemas.auth import AuthenticatedUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/{provider}/login")
async def begin_login(provider: str, request: Request) -> RedirectResponse:
    """Start a provider-hosted Authorization Code flow with signed state storage."""
    try:
        settings = get_settings()
        client = get_oauth_client(provider, settings)
    except OAuthConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AUTH_CONFIGURATION_REQUIRED", "message": str(error)},
        ) from error

    redirect_uri = f"{settings.api_origin}/api/v1/auth/{provider}/callback"
    return await client.authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def complete_login(provider: str, request: Request) -> RedirectResponse:
    """Exchange an authorization code, retain a minimum profile, and redirect without code parameters."""
    try:
        settings = get_settings()
        client = get_oauth_client(provider, settings)
        token = await client.authorize_access_token(request)
        profile = await profile_from_token(provider, client, token)
    except OAuthConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AUTH_CONFIGURATION_REQUIRED", "message": str(error)},
        ) from error

    request.session["identity"] = profile.model_dump()
    return RedirectResponse(f"{settings.app_origin}/?login=success", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/me", response_model=AuthenticatedUser)
async def current_user(request: Request) -> AuthenticatedUser:
    identity = request.session.get("identity")
    if not identity:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTHENTICATION_REQUIRED", "message": "로그인이 필요합니다."},
        )
    return AuthenticatedUser.model_validate(identity)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response) -> None:
    request.session.clear()
    response.delete_cookie("session")
