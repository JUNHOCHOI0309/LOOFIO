from fastapi import APIRouter, HTTPException, Request, Response, status

from app.actions.store import (
    ActionInvalidTransition,
    ActionNotFound,
    ActionRecommendationNotApproved,
    ActionStoreUnavailable,
)
from app.api.dependencies import require_active_tenant_user
from app.schemas.actions import Action, ActionCreateResult, CreateManualActionRequest, UpdateActionStatusRequest


router = APIRouter(tags=["actions"])


@router.post("/recommendations/{recommendation_id}/actions", response_model=ActionCreateResult, status_code=status.HTTP_201_CREATED)
async def create_manual_action(
    recommendation_id: str, payload: CreateManualActionRequest, request: Request, response: Response
) -> ActionCreateResult:
    user = require_active_tenant_user(request)
    _require_action_editor(request, user.user_id, user.active_tenant_id)
    try:
        result = request.app.state.action_store.create_or_get_manual_action(
            tenant_id=user.active_tenant_id, recommendation_id=recommendation_id, user_id=user.user_id, payload=payload
        )
    except ActionRecommendationNotApproved as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "CONFLICT", "message": str(error)}) from error
    except ActionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ActionStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "ACTION_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    return result


@router.get("/recommendations/{recommendation_id}/actions", response_model=list[Action])
async def list_recommendation_actions(recommendation_id: str, request: Request) -> list[Action]:
    user = require_active_tenant_user(request)
    try:
        return request.app.state.action_store.list_for_recommendation(
            tenant_id=user.active_tenant_id, recommendation_id=recommendation_id
        )
    except ActionStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "ACTION_STORAGE_UNAVAILABLE", "message": str(error)}) from error


@router.get("/businesses/{business_id}/actions", response_model=list[Action])
async def list_business_actions(business_id: str, request: Request) -> list[Action]:
    user = require_active_tenant_user(request)
    try:
        return request.app.state.action_store.list_for_business(tenant_id=user.active_tenant_id, business_id=business_id)
    except ActionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ActionStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "ACTION_STORAGE_UNAVAILABLE", "message": str(error)}) from error


@router.get("/actions/{action_id}", response_model=Action)
async def get_action(action_id: str, request: Request) -> Action:
    user = require_active_tenant_user(request)
    try:
        return request.app.state.action_store.get_action(tenant_id=user.active_tenant_id, action_id=action_id)
    except ActionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ActionStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "ACTION_STORAGE_UNAVAILABLE", "message": str(error)}) from error


@router.patch("/actions/{action_id}", response_model=Action)
async def update_action_status(action_id: str, payload: UpdateActionStatusRequest, request: Request) -> Action:
    user = require_active_tenant_user(request)
    _require_action_editor(request, user.user_id, user.active_tenant_id)
    try:
        return request.app.state.action_store.update_status(
            tenant_id=user.active_tenant_id, action_id=action_id, user_id=user.user_id, payload=payload
        )
    except ActionInvalidTransition as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "CONFLICT", "message": str(error)}) from error
    except ActionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ActionStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "ACTION_STORAGE_UNAVAILABLE", "message": str(error)}) from error


def _require_action_editor(request: Request, user_id: str, tenant_id: str) -> None:
    role = next((item.role for item in request.app.state.auth_store.list_tenants(user_id) if item.tenant_id == tenant_id), None)
    if role not in {"owner", "admin", "marketer"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "FORBIDDEN", "message": "Action 초안과 상태 변경은 owner, admin 또는 marketer 역할만 수행할 수 있습니다."})
