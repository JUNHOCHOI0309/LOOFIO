from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import ValidationError

from app.api.dependencies import require_active_tenant_user, require_decision_preview_editor
from app.decisioning.cause_preview import CausePreviewApplication, CausePreviewInputError
from app.decisioning.privacy import HospitalPIIError, assert_no_hospital_pii
from app.opportunities.store import OpportunityBusinessNotFound, OpportunityStoreUnavailable
from app.schemas.cause_analyses import CauseAnalysisPreviewRequest, CauseAnalysisPreviewResponse


router = APIRouter(tags=["cause-analyses"])


@router.post(
    "/opportunities/{opportunity_id}/cause-analyses/preview",
    response_model=CauseAnalysisPreviewResponse,
    operation_id="preview_cause_analysis",
)
async def preview_cause_analysis(
    opportunity_id: str, payload: dict[str, Any], request: Request
) -> CauseAnalysisPreviewResponse:
    """Recompute a scoped Cause Analysis without creating a database resource."""
    user = require_active_tenant_user(request)
    require_decision_preview_editor(request, user_id=user.user_id, tenant_id=user.active_tenant_id)
    try:
        assert_no_hospital_pii(payload)
    except HospitalPIIError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "PII_FIELD_REJECTED",
                "message": "병원 Cause Preview에는 환자 개인정보나 임상정보를 포함할 수 없습니다.",
                "details": list(error.field_paths),
            },
        ) from error

    try:
        preview_request = CauseAnalysisPreviewRequest.model_validate(payload)
        return CausePreviewApplication(request.app.state.opportunity_store).preview(
            tenant_id=user.active_tenant_id,
            opportunity_id=opportunity_id,
            payload=preview_request,
        )
    except OpportunityBusinessNotFound as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "NOT_FOUND", "message": str(error)},
        ) from error
    except OpportunityStoreUnavailable as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "OPPORTUNITY_STORAGE_UNAVAILABLE", "message": str(error)},
        ) from error
    except (ValidationError, CausePreviewInputError) as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "DECISION_CONTEXT_INVALID", "message": "Decision Context를 확인할 수 없습니다."},
        ) from error
