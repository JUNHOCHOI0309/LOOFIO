from fastapi import APIRouter, HTTPException, Request, Response, status

from app.api.dependencies import require_active_tenant_user
from app.metrics.store import MetricBusinessNotFound, MetricStoreUnavailable
from app.results.measurement import baseline_windows, calculate_action_measurement
from app.results.store import ResultActionNotCompleted, ResultNotFound, ResultStoreUnavailable
from app.schemas.results import ActionMeasurement, ActionResult, ActionResultCreateResult, CreateActionResultRequest


router = APIRouter(tags=["results", "measurements"])


@router.post("/actions/{action_id}/results", response_model=ActionResultCreateResult, status_code=status.HTTP_201_CREATED)
async def create_action_result(action_id: str, payload: CreateActionResultRequest, request: Request, response: Response) -> ActionResultCreateResult:
    user = require_active_tenant_user(request)
    _require_result_editor(request, user.user_id, user.active_tenant_id)
    try:
        result = request.app.state.result_store.create_or_get(tenant_id=user.active_tenant_id, action_id=action_id, user_id=user.user_id, payload=payload)
    except ResultActionNotCompleted as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "CONFLICT", "message": str(error)}) from error
    except ResultNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ResultStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "RESULT_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    if result.replayed:
        response.status_code = status.HTTP_200_OK
    return result


@router.get("/actions/{action_id}/results", response_model=ActionResult)
async def get_action_result(action_id: str, request: Request) -> ActionResult:
    user = require_active_tenant_user(request)
    try:
        return request.app.state.result_store.get(tenant_id=user.active_tenant_id, action_id=action_id)
    except ResultNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ResultStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "RESULT_STORAGE_UNAVAILABLE", "message": str(error)}) from error


@router.get("/actions/{action_id}/measurements", response_model=ActionMeasurement)
async def get_action_measurement(action_id: str, request: Request) -> ActionMeasurement:
    user = require_active_tenant_user(request)
    try:
        action = request.app.state.action_store.get_action(tenant_id=user.active_tenant_id, action_id=action_id)
        result = request.app.state.result_store.get(tenant_id=user.active_tenant_id, action_id=action_id)
        observed_rows = request.app.state.metric_store.read_appointments(tenant_id=user.active_tenant_id, business_id=action.business_id,
                                                                          start_at=result.measurement_start_at, end_at=result.measurement_end_at)
        baselines = [request.app.state.metric_store.read_appointments(tenant_id=user.active_tenant_id, business_id=action.business_id, start_at=start_at, end_at=end_at)
                     for start_at, end_at in baseline_windows(result.measurement_start_at, result.measurement_end_at)]
    except ResultNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except MetricBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except (ResultStoreUnavailable, MetricStoreUnavailable) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "MEASUREMENT_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    return calculate_action_measurement(action_id=action_id, result_id=result.id, observation_rows=observed_rows, baseline_rows=baselines,
                                        start_at=result.measurement_start_at, end_at=result.measurement_end_at)


def _require_result_editor(request: Request, user_id: str, tenant_id: str) -> None:
    role = next((item.role for item in request.app.state.auth_store.list_tenants(user_id) if item.tenant_id == tenant_id), None)
    if role not in {"owner", "admin", "marketer"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "FORBIDDEN", "message": "Action 결과 기록은 owner, admin 또는 marketer 역할만 수행할 수 있습니다."})
