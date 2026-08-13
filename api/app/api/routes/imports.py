from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.imports.appointments import AppointmentImportError, preview_appointments_csv
from app.schemas.imports import AppointmentImportPreview

router = APIRouter(tags=["imports"])


@router.post(
    "/businesses/{business_id}/imports/appointments/preview",
    response_model=AppointmentImportPreview,
    status_code=status.HTTP_200_OK,
)
async def preview_appointment_import(
    business_id: str,
    file: UploadFile = File(...),
) -> AppointmentImportPreview:
    """Validate and normalize an appointments CSV without persisting source rows."""
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="A CSV file is required.")

    raw_csv = await file.read()
    try:
        return preview_appointments_csv(business_id=business_id, raw_csv=raw_csv)
    except AppointmentImportError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
