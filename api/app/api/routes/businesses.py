from fastapi import APIRouter, Request, status

from app.api.dependencies import require_active_tenant_user
from app.schemas.businesses import BusinessLocation, CreateBusinessRequest

router = APIRouter(prefix="/businesses", tags=["businesses"])


@router.post("", response_model=BusinessLocation, status_code=status.HTTP_201_CREATED)
async def create_business(payload: CreateBusinessRequest, request: Request) -> BusinessLocation:
    user = require_active_tenant_user(request)
    return request.app.state.auth_store.create_business_with_location(
        tenant_id=user.active_tenant_id,
        name=payload.name,
        medical_domain=payload.medical_domain,
        location_name=payload.location_name,
        timezone=payload.timezone,
    )


@router.get("", response_model=list[BusinessLocation])
async def list_businesses(request: Request) -> list[BusinessLocation]:
    user = require_active_tenant_user(request)
    return request.app.state.auth_store.list_businesses(user.active_tenant_id)
