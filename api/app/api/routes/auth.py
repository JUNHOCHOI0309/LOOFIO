from fastapi import APIRouter, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse

from app.api.dependencies import require_authenticated_user
from app.auth.oauth import OAuthConfigurationError, get_oauth_client, get_settings, profile_from_token
from app.auth.store import AuthStoreUnavailable
from app.schemas.auth import AuthenticatedUser, CreateTenantRequest, TenantMembership

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
        user = request.app.state.auth_store.find_or_create_user(profile)
        session_id = request.app.state.auth_store.create_session(user.user_id)
        destination = "/onboarding" if not request.app.state.auth_store.list_tenants(user.user_id) else "/"
    except OAuthConfigurationError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AUTH_CONFIGURATION_REQUIRED", "message": str(error)},
        ) from error
    except AuthStoreUnavailable as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AUTH_STORAGE_UNAVAILABLE", "message": str(error)},
        ) from error

    request.session["session_id"] = session_id
    return RedirectResponse(f"{settings.app_origin}{destination}?login=success", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/me", response_model=AuthenticatedUser)
async def current_user(request: Request) -> AuthenticatedUser:
    return require_authenticated_user(request)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response) -> None:
    session_id = request.session.get("session_id")
    if session_id:
        request.app.state.auth_store.revoke_session(session_id)
    request.session.clear()
    response.delete_cookie("session")


@router.get("/tenants", response_model=list[TenantMembership])
async def my_tenants(request: Request) -> list[TenantMembership]:
    user = require_authenticated_user(request)
    return request.app.state.auth_store.list_tenants(user.user_id)


@router.post("/active-tenant/{tenant_id}", response_model=AuthenticatedUser)
async def switch_active_tenant(tenant_id: str, request: Request) -> AuthenticatedUser:
    require_authenticated_user(request)
    session_id = request.session.get("session_id")
    user = request.app.state.auth_store.switch_active_tenant(session_id, tenant_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "FORBIDDEN", "message": "해당 Tenant에 접근할 수 없습니다."})
    return user


@router.post("/tenants", response_model=AuthenticatedUser, status_code=status.HTTP_201_CREATED)
async def create_tenant(payload: CreateTenantRequest, request: Request) -> AuthenticatedUser:
    user = require_authenticated_user(request)
    session_id = request.session.get("session_id")
    membership = request.app.state.auth_store.create_tenant(user.user_id, payload.name)
    active_user = request.app.state.auth_store.switch_active_tenant(session_id, membership.tenant_id)
    if not active_user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail={"code": "INTERNAL_ERROR", "message": "Tenant를 활성화하지 못했습니다."})
    return active_user
