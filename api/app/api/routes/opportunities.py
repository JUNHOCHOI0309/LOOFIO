from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.analytics.detectors.low_demand_slots import DETECTOR_VERSION
from app.api.dependencies import require_active_tenant_user
from app.metrics.store import MetricBusinessNotFound, MetricStoreUnavailable
from app.opportunities.low_demand import build_low_demand_opportunity_drafts
from app.opportunities.store import OpportunityBusinessNotFound, OpportunityStoreUnavailable
from app.schemas.opportunities import Opportunity, OpportunityRefreshResult

router = APIRouter(tags=["opportunities"])


@router.post("/businesses/{business_id}/opportunities/refresh", response_model=OpportunityRefreshResult)
async def refresh_low_demand_opportunities(
    business_id: str,
    request: Request,
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
) -> OpportunityRefreshResult:
    user = require_active_tenant_user(request)
    _validate_range(start_at, end_at)
    try:
        rows = request.app.state.metric_store.read_appointments(
            tenant_id=user.active_tenant_id, business_id=business_id, start_at=start_at, end_at=end_at
        )
        opportunities = request.app.state.opportunity_store.refresh_low_demand(
            tenant_id=user.active_tenant_id,
            business_id=business_id,
            drafts=build_low_demand_opportunity_drafts(rows),
        )
    except (MetricBusinessNotFound, OpportunityBusinessNotFound) as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except (MetricStoreUnavailable, OpportunityStoreUnavailable) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "OPPORTUNITY_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    return OpportunityRefreshResult(detector_version=DETECTOR_VERSION, refreshed_count=len(opportunities), opportunities=opportunities)


@router.get("/businesses/{business_id}/opportunities", response_model=list[Opportunity])
async def list_opportunities(business_id: str, request: Request) -> list[Opportunity]:
    user = require_active_tenant_user(request)
    try:
        return request.app.state.opportunity_store.list_opportunities(tenant_id=user.active_tenant_id, business_id=business_id)
    except OpportunityBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except OpportunityStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "OPPORTUNITY_STORAGE_UNAVAILABLE", "message": str(error)}) from error


def _validate_range(start_at: datetime | None, end_at: datetime | None) -> None:
    if (start_at and start_at.tzinfo is None) or (end_at and end_at.tzinfo is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "기간은 UTC offset을 포함해야 합니다."})
    if start_at and end_at and end_at < start_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "종료 시점은 시작 시점 이후여야 합니다."})
