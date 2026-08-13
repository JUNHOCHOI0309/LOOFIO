import csv
from datetime import datetime
from io import StringIO

from app.schemas.imports import AppointmentImportPreview, AppointmentPreviewRow

REQUIRED_COLUMNS = {"appointment_id", "visit_start_at", "offering_name", "status"}
STATUS_MAP = {
    "booked": "booked",
    "예약": "booked",
    "completed": "completed",
    "완료": "completed",
    "방문완료": "completed",
    "cancelled": "cancelled",
    "canceled": "cancelled",
    "취소": "cancelled",
    "no_show": "no_show",
    "noshow": "no_show",
    "노쇼": "no_show",
    "unknown": "unknown",
}


class AppointmentImportError(ValueError):
    """Raised when an import cannot meet the Hospital v1 data contract."""


def preview_appointments_csv(*, business_id: str, raw_csv: bytes) -> AppointmentImportPreview:
    """Parse a small CSV preview into a deterministic, non-persistent normalized result."""
    if not raw_csv:
        raise AppointmentImportError("The CSV file is empty.")

    try:
        content = raw_csv.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise AppointmentImportError("The CSV must use UTF-8 encoding.") from error

    reader = csv.DictReader(StringIO(content))
    fieldnames = set(reader.fieldnames or [])
    missing_columns = sorted(REQUIRED_COLUMNS - fieldnames)
    if missing_columns:
        raise AppointmentImportError(f"Missing required columns: {', '.join(missing_columns)}")

    valid_rows: list[AppointmentPreviewRow] = []
    errors: list[str] = []
    for row_number, row in enumerate(reader, start=2):
        try:
            valid_rows.append(_normalize_row(row, row_number))
        except AppointmentImportError as error:
            errors.append(str(error))

    return AppointmentImportPreview(
        business_id=business_id,
        total_rows=len(valid_rows) + len(errors),
        valid_rows=len(valid_rows),
        invalid_rows=len(errors),
        errors=errors,
        preview=valid_rows[:20],
    )


def _normalize_row(row: dict[str, str | None], row_number: int) -> AppointmentPreviewRow:
    appointment_id = (row.get("appointment_id") or "").strip()
    offering_name = (row.get("offering_name") or "").strip()
    if not appointment_id:
        raise AppointmentImportError(f"Row {row_number}: appointment_id is required.")
    if not offering_name:
        raise AppointmentImportError(f"Row {row_number}: offering_name is required.")

    visit_start_at = _parse_datetime(row.get("visit_start_at"), row_number, "visit_start_at")
    visit_end_at = _parse_datetime(row.get("visit_end_at"), row_number, "visit_end_at", required=False)
    if visit_end_at and visit_end_at < visit_start_at:
        raise AppointmentImportError(f"Row {row_number}: visit_end_at cannot be before visit_start_at.")

    normalized_status = STATUS_MAP.get((row.get("status") or "").strip().lower())
    if normalized_status is None:
        raise AppointmentImportError(f"Row {row_number}: unsupported status.")

    customer_token = (row.get("customer_token") or "").strip() or None
    if customer_token and len(customer_token) < 16:
        raise AppointmentImportError(f"Row {row_number}: customer_token must be a pseudonymous token, not a raw identifier.")

    return AppointmentPreviewRow(
        source_record_id=appointment_id,
        visit_start_at=visit_start_at,
        visit_end_at=visit_end_at,
        offering_name=offering_name,
        status=normalized_status,
        customer_token_present=customer_token is not None,
    )


def _parse_datetime(
    value: str | None, row_number: int, field_name: str, *, required: bool = True
) -> datetime | None:
    text = (value or "").strip()
    if not text:
        if required:
            raise AppointmentImportError(f"Row {row_number}: {field_name} is required.")
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as error:
        raise AppointmentImportError(f"Row {row_number}: {field_name} must be ISO-8601.") from error
    if parsed.tzinfo is None:
        raise AppointmentImportError(f"Row {row_number}: {field_name} must include a UTC offset.")
    return parsed
