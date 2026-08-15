from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.opportunities.low_demand import OPPORTUNITY_DETECTOR_VERSION
from app.api.dependencies import require_active_tenant_user
from app.metrics.store import MetricBusinessNotFound, MetricStoreUnavailable
from app.opportunities.low_demand import build_low_demand_opportunity_drafts
from app.opportunities.other_detectors import build_other_detector_opportunity_drafts
from app.opportunities.store import OpportunityBusinessNotFound, OpportunityStoreUnavailable
from app.recommendations.low_demand import build_low_demand_recommendation_draft
from app.recommendations.store import RecommendationNotFound, RecommendationStoreUnavailable
from app.schemas.opportunities import Opportunity, OpportunityRefreshResult
from app.schemas.recommendations import Recommendation, RecommendationDecisionRequest

router = APIRouter(tags=["opportunities"])


@router.post("/businesses/{business_id}/opportunities/refresh", response_model=OpportunityRefreshResult)
async def refresh_low_demand_opportunities(
    business_id: str,
    request: Request,
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
    as_of_date: date | None = Query(default=None),
) -> OpportunityRefreshResult:
    user = require_active_tenant_user(request)
    _validate_range(start_at, end_at)
    try:
        rows = request.app.state.metric_store.read_appointments(
            tenant_id=user.active_tenant_id, business_id=business_id, start_at=start_at, end_at=end_at
        )
        drafts = [*build_low_demand_opportunity_drafts(rows), *build_other_detector_opportunity_drafts(rows, as_of_date=as_of_date)]
        opportunities = request.app.state.opportunity_store.refresh(
            tenant_id=user.active_tenant_id,
            business_id=business_id,
            drafts=drafts,
        )
    except (MetricBusinessNotFound, OpportunityBusinessNotFound) as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except (MetricStoreUnavailable, OpportunityStoreUnavailable) as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "OPPORTUNITY_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    return OpportunityRefreshResult(
        detector_version=OPPORTUNITY_DETECTOR_VERSION,
        refreshed_count=len(opportunities),
        opportunities=opportunities,
        refreshed_detector_versions=sorted({opportunity.detector.version for opportunity in opportunities}),
    )


@router.get("/businesses/{business_id}/opportunities", response_model=list[Opportunity])
async def list_opportunities(business_id: str, request: Request) -> list[Opportunity]:
    user = require_active_tenant_user(request)
    try:
        return request.app.state.opportunity_store.list_opportunities(tenant_id=user.active_tenant_id, business_id=business_id)
    except OpportunityBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except OpportunityStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "OPPORTUNITY_STORAGE_UNAVAILABLE", "message": str(error)}) from error


@router.post("/opportunities/{opportunity_id}/recommendations/draft", response_model=Recommendation)
async def create_recommendation_draft(opportunity_id: str, request: Request) -> Recommendation:
    user = require_active_tenant_user(request)
    _require_recommendation_editor(request, user.user_id, user.active_tenant_id)
    try:
        opportunity = request.app.state.opportunity_store.get_opportunity(
            tenant_id=user.active_tenant_id, opportunity_id=opportunity_id
        )
        return request.app.state.recommendation_store.create_or_get_draft(
            tenant_id=user.active_tenant_id,
            opportunity_id=opportunity.id,
            draft=build_low_demand_recommendation_draft(opportunity),
        )
    except OpportunityBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": str(error)}) from error
    except RecommendationStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "RECOMMENDATION_STORAGE_UNAVAILABLE", "message": str(error)}) from error


@router.get("/opportunities/{opportunity_id}/recommendations", response_model=list[Recommendation])
async def list_recommendations(opportunity_id: str, request: Request) -> list[Recommendation]:
    user = require_active_tenant_user(request)
    try:
        request.app.state.opportunity_store.get_opportunity(tenant_id=user.active_tenant_id, opportunity_id=opportunity_id)
        return request.app.state.recommendation_store.list_for_opportunity(
            tenant_id=user.active_tenant_id, opportunity_id=opportunity_id
        )
    except OpportunityBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except RecommendationStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "RECOMMENDATION_STORAGE_UNAVAILABLE", "message": str(error)}) from error


@router.post("/recommendations/{recommendation_id}/decisions", response_model=Recommendation)
async def decide_recommendation(
    recommendation_id: str, payload: RecommendationDecisionRequest, request: Request
) -> Recommendation:
    user = require_active_tenant_user(request)
    _require_recommendation_editor(request, user.user_id, user.active_tenant_id)
    try:
        return request.app.state.recommendation_store.record_decision(
            tenant_id=user.active_tenant_id,
            recommendation_id=recommendation_id,
            user_id=user.user_id,
            payload=payload,
        )
    except RecommendationNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except RecommendationStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "RECOMMENDATION_STORAGE_UNAVAILABLE", "message": str(error)}) from error


def _validate_range(start_at: datetime | None, end_at: datetime | None) -> None:
    if (start_at and start_at.tzinfo is None) or (end_at and end_at.tzinfo is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "기간은 UTC offset을 포함해야 합니다."})
    if start_at and end_at and end_at < start_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "종료 시점은 시작 시점 이후여야 합니다."})


def _require_recommendation_editor(request: Request, user_id: str, tenant_id: str) -> None:
    role = next((item.role for item in request.app.state.auth_store.list_tenants(user_id) if item.tenant_id == tenant_id), None)
    if role not in {"owner", "admin", "marketer"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={"code": "FORBIDDEN", "message": "추천 초안과 결정은 owner, admin 또는 marketer 역할만 수행할 수 있습니다."})
