from typing import Annotated

from fastapi import APIRouter, File, Header, HTTPException, Request, Response, UploadFile, status

from app.api.dependencies import require_active_tenant_user
from app.imports.appointments import AppointmentImportError, parse_appointments_csv, preview_appointments_csv
from app.imports.store import (
    BusinessNotFoundForTenant,
    ImportIdempotencyConflict,
    ImportStoreUnavailable,
    MultipleLocationsRequireMapping,
)
from app.schemas.imports import AppointmentImportPreview, AppointmentImportResult

router = APIRouter(tags=["imports"])


@router.post(
    "/businesses/{business_id}/imports/appointments/preview",
    response_model=AppointmentImportPreview,
    status_code=status.HTTP_200_OK,
)
async def preview_appointment_import(
    business_id: str,
    request: Request,
    file: UploadFile = File(...),
) -> AppointmentImportPreview:
    """Validate and normalize an appointments CSV without persisting source rows."""
    require_active_tenant_user(request)
    raw_csv = await _read_csv_file(file)
    try:
        return preview_appointments_csv(business_id=business_id, raw_csv=raw_csv)
    except AppointmentImportError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": "CSV 데이터를 검증할 수 없습니다.", "details": [str(error)]},
        ) from error


@router.post(
    "/businesses/{business_id}/imports/appointments",
    response_model=AppointmentImportResult,
    status_code=status.HTTP_201_CREATED,
)
async def persist_appointment_import(
    business_id: str,
    request: Request,
    response: Response,
    file: UploadFile = File(...),
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> AppointmentImportResult:
    """Persist a fully valid appointment CSV within the active tenant and business scope."""
    user = require_active_tenant_user(request)
    if not idempotency_key or len(idempotency_key) > 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": "VALIDATION_ERROR", "message": "Idempotency-Key 헤더가 필요합니다."},
        )
    raw_csv = await _read_csv_file(file)
    try:
        parsed = parse_appointments_csv(raw_csv)
    except AppointmentImportError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": "CSV 데이터를 검증할 수 없습니다.", "details": [str(error)]},
        ) from error
    if parsed.errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "VALIDATION_ERROR", "message": "오류 행을 수정한 뒤 다시 업로드해 주세요.", "details": parsed.errors},
        )
    try:
        result = request.app.state.import_store.persist_appointments(
            tenant_id=user.active_tenant_id,
            business_id=business_id,
            source_filename=file.filename or "appointments.csv",
            idempotency_key=idempotency_key,
            raw_csv=raw_csv,
            rows=parsed.rows,
        )
    except BusinessNotFoundForTenant as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except MultipleLocationsRequireMapping as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail={"code": "VALIDATION_ERROR", "message": str(error)}) from error
    except ImportIdempotencyConflict as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail={"code": "IDEMPOTENCY_CONFLICT", "message": str(error)}) from error
    except ImportStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "IMPORT_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    if result.replayed:
        response.status_code = status.HTTP_200_OK
        return result
    return result


@router.get("/businesses/{business_id}/imports/{import_id}", response_model=AppointmentImportResult)
async def get_appointment_import(business_id: str, import_id: str, request: Request) -> AppointmentImportResult:
    user = require_active_tenant_user(request)
    try:
        result = request.app.state.import_store.get_import(
            tenant_id=user.active_tenant_id, business_id=business_id, import_id=import_id
        )
    except BusinessNotFoundForTenant as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": str(error)}) from error
    except ImportStoreUnavailable as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail={"code": "IMPORT_STORAGE_UNAVAILABLE", "message": str(error)}) from error
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"code": "NOT_FOUND", "message": "Import를 찾을 수 없습니다."})
    return result


async def _read_csv_file(file: UploadFile) -> bytes:
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"code": "VALIDATION_ERROR", "message": "CSV 파일이 필요합니다."})
    return await file.read()
