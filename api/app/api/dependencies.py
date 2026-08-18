from fastapi import HTTPException, Request, status

from app.auth.store import AuthStoreUnavailable
from app.schemas.auth import AuthenticatedUser


def require_authenticated_user(request: Request) -> AuthenticatedUser:
    session_id = request.session.get("session_id")
    if not session_id:
        _raise_authentication_required()

    try:
        user = request.app.state.auth_store.resolve_session(session_id)
    except AuthStoreUnavailable as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AUTH_STORAGE_UNAVAILABLE", "message": str(error)},
        ) from error

    if not user:
        _raise_authentication_required()
    return user


def require_active_tenant_user(request: Request) -> AuthenticatedUser:
    user = require_authenticated_user(request)
    if not user.active_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "ACTIVE_TENANT_REQUIRED", "message": "활성 Tenant를 먼저 선택해야 합니다."},
        )
    return user


def require_decision_preview_editor(request: Request, *, user_id: str, tenant_id: str) -> None:
    """Limit mutable-input previews to the same editor roles as Recommendation drafts."""
    role = next(
        (item.role for item in request.app.state.auth_store.list_tenants(user_id) if item.tenant_id == tenant_id),
        None,
    )
    if role not in {"owner", "admin", "marketer"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Cause Preview는 owner, admin 또는 marketer 역할만 수행할 수 있습니다.",
            },
        )


def _raise_authentication_required() -> None:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "AUTHENTICATION_REQUIRED", "message": "로그인이 필요합니다."},
    )
