from datetime import date, datetime

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.analytics.detectors.cancellation_hotspots import detect_cancellation_hotspots
from app.analytics.detectors.dormant_customers import detect_dormant_customers
from app.analytics.detectors.low_demand_slots import detect_low_demand_slots
from app.analytics.detectors.revenue_gap import detect_revenue_gaps
from app.api.dependencies import require_active_tenant_user
from app.metrics.store import MetricBusinessNotFound, MetricStoreUnavailable
from app.schemas.detectors import CancellationHotspotDetection, DormantCustomerDetection, LowDemandSlotDetection, RevenueGapDetection

router = APIRouter(tags=["detectors"])


@router.get("/businesses/{business_id}/detectors/low-demand-slots", response_model=LowDemandSlotDetection)
async def get_low_demand_slot_candidates(
    business_id: str,
    request: Request,
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
) -> LowDemandSlotDetection:
    user = require_active_tenant_user(request)
    if (start_at and start_at.tzinfo is None) or (end_at and end_at.tzinfo is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "기간은 UTC offset을 포함해야 합니다."})
    if start_at and end_at and end_at < start_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "종료 시점은 시작 시점 이후여야 합니다."})
    try:
        rows = request.app.state.metric_store.read_appointments(
            tenant_id=user.active_tenant_id, business_id=business_id, start_at=start_at, end_at=end_at
        )
    except MetricBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except MetricStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "METRIC_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    return detect_low_demand_slots(rows)


@router.get("/businesses/{business_id}/detectors/revenue-gaps", response_model=RevenueGapDetection)
async def get_revenue_gap_candidates(
    business_id: str,
    request: Request,
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
) -> RevenueGapDetection:
    user = require_active_tenant_user(request)
    if (start_at and start_at.tzinfo is None) or (end_at and end_at.tzinfo is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "기간은 UTC offset을 포함해야 합니다."})
    if start_at and end_at and end_at < start_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "종료 시점은 시작 시점 이후여야 합니다."})
    try:
        rows = request.app.state.metric_store.read_appointments(
            tenant_id=user.active_tenant_id, business_id=business_id, start_at=start_at, end_at=end_at
        )
    except MetricBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except MetricStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "METRIC_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    return detect_revenue_gaps(rows)


@router.get("/businesses/{business_id}/detectors/cancellation-hotspots", response_model=CancellationHotspotDetection)
async def get_cancellation_hotspot_candidates(
    business_id: str,
    request: Request,
    start_at: datetime | None = Query(default=None),
    end_at: datetime | None = Query(default=None),
) -> CancellationHotspotDetection:
    user = require_active_tenant_user(request)
    if (start_at and start_at.tzinfo is None) or (end_at and end_at.tzinfo is None):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "기간은 UTC offset을 포함해야 합니다."})
    if start_at and end_at and end_at < start_at:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": "종료 시점은 시작 시점 이후여야 합니다."})
    try:
        rows = request.app.state.metric_store.read_appointments(
            tenant_id=user.active_tenant_id, business_id=business_id, start_at=start_at, end_at=end_at
        )
    except MetricBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except MetricStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "METRIC_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    return detect_cancellation_hotspots(rows)


@router.get("/businesses/{business_id}/detectors/dormant-customers", response_model=DormantCustomerDetection)
async def get_dormant_customer_candidates(
    business_id: str,
    request: Request,
    as_of_date: date = Query(...),
) -> DormantCustomerDetection:
    user = require_active_tenant_user(request)
    try:
        rows = request.app.state.metric_store.read_appointments(
            tenant_id=user.active_tenant_id, business_id=business_id, start_at=None, end_at=None
        )
    except MetricBusinessNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except MetricStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "METRIC_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    return detect_dormant_customers(rows, as_of_date=as_of_date)
