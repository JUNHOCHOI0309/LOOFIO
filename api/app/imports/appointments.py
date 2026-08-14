import csv
import re
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import StringIO

from app.schemas.imports import AppointmentImportInspection, AppointmentImportPreview, AppointmentPreviewRow

REQUIRED_COLUMNS = {"appointment_id", "visit_start_at", "offering_name", "status"}
PERSISTED_SOURCE_COLUMNS = {
    "appointment_id",
    "location_key",
    "customer_token",
    "visit_start_at",
    "visit_end_at",
    "booked_at",
    "offering_name",
    "staff_key",
    "status",
    "listed_price",
    "paid_amount",
    "discount_amount",
    "source",
    "source_record_id",
}
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
CANONICAL_COLUMNS = PERSISTED_SOURCE_COLUMNS
HEADER_ALIASES = {
    "appointment_id": {"appointment_id", "appointmentid", "예약id", "예약번호", "예약번호id", "접수번호"},
    "visit_start_at": {"visit_start_at", "visitstartat", "방문일시", "예약일시", "진료일시", "시작일시"},
    "visit_end_at": {"visit_end_at", "visitendat", "종료일시", "진료종료일시"},
    "booked_at": {"booked_at", "bookedat", "예약생성일시", "예약등록일시", "접수일시"},
    "offering_name": {"offering_name", "service_name", "servicename", "서비스명", "진료명", "시술명", "상품명"},
    "status": {"status", "예약상태", "상태", "진료상태", "방문상태"},
    "customer_token": {"customer_token", "customertoken", "고객토큰", "가명고객키"},
    "location_key": {"location_key", "locationkey", "지점키", "지점코드"},
    "staff_key": {"staff_key", "staffkey", "담당자키", "의료진키"},
    "listed_price": {"listed_price", "listedprice", "정가", "판매가"},
    "paid_amount": {"paid_amount", "paidamount", "결제금액", "실결제금액", "수납금액"},
    "discount_amount": {"discount_amount", "discountamount", "할인금액"},
    "source": {"source", "출처", "예약경로"},
    "source_record_id": {"source_record_id", "sourcerecordid", "원본레코드id", "외부예약id"},
}
SENSITIVE_IDENTIFIER_HEADER_MARKERS = {"phone", "tel", "mobile", "email", "전화", "휴대폰", "연락처", "이메일", "주민"}


class AppointmentImportError(ValueError):
    """Raised when an import cannot meet the Hospital v1 data contract."""


@dataclass(frozen=True)
class AppointmentColumnMapping:
    column_mapping: dict[str, str]
    status_mapping: dict[str, str]


@dataclass(frozen=True)
class NormalizedAppointment:
    row_number: int
    appointment_id: str
    source_system: str
    source_record_id: str
    customer_token: str | None
    location_key: str | None
    visit_start_at: datetime
    visit_end_at: datetime | None
    booked_at: datetime | None
    offering_name: str
    staff_key: str | None
    status: str
    listed_price: Decimal | None
    paid_amount: Decimal | None
    discount_amount: Decimal | None
    raw_payload: dict[str, str]

    def normalized_payload(self) -> dict[str, str | None]:
        return {
            "appointment_id": self.appointment_id,
            "source_system": self.source_system,
            "source_record_id": self.source_record_id,
            "customer_token": self.customer_token,
            "location_key": self.location_key,
            "visit_start_at": self.visit_start_at.isoformat(),
            "visit_end_at": self.visit_end_at.isoformat() if self.visit_end_at else None,
            "booked_at": self.booked_at.isoformat() if self.booked_at else None,
            "offering_name": self.offering_name,
            "staff_key": self.staff_key,
            "status": self.status,
            "listed_price": str(self.listed_price) if self.listed_price is not None else None,
            "paid_amount": str(self.paid_amount) if self.paid_amount is not None else None,
            "discount_amount": str(self.discount_amount) if self.discount_amount is not None else None,
        }


@dataclass(frozen=True)
class ParsedAppointmentImport:
    total_rows: int
    rows: list[NormalizedAppointment]
    errors: list[str]


def preview_appointments_csv(
    *, business_id: str, raw_csv: bytes, mapping: AppointmentColumnMapping | None = None
) -> AppointmentImportPreview:
    """Parse a CSV preview without persisting source rows."""
    parsed = parse_appointments_csv(raw_csv, mapping=mapping)
    return AppointmentImportPreview(
        business_id=business_id,
        total_rows=parsed.total_rows,
        valid_rows=len(parsed.rows),
        invalid_rows=len(parsed.errors),
        errors=parsed.errors,
        preview=[
            AppointmentPreviewRow(
                source_record_id=row.appointment_id,
                visit_start_at=row.visit_start_at,
                visit_end_at=row.visit_end_at,
                offering_name=row.offering_name,
                status=row.status,
                customer_token_present=row.customer_token is not None,
            )
            for row in parsed.rows[:20]
        ],
    )


def inspect_appointments_csv(raw_csv: bytes) -> AppointmentImportInspection:
    fieldnames = _read_fieldnames(raw_csv)
    suggestions = suggest_column_mapping(fieldnames)
    return AppointmentImportInspection(
        source_columns=fieldnames,
        suggested_column_mapping=suggestions,
        required_columns=sorted(REQUIRED_COLUMNS),
    )


def suggest_column_mapping(fieldnames: list[str]) -> dict[str, str]:
    suggestions: dict[str, str] = {}
    normalized_headers: dict[str, list[str]] = {}
    for fieldname in fieldnames:
        normalized_headers.setdefault(_normalize_header(fieldname), []).append(fieldname)
    for canonical_column, aliases in HEADER_ALIASES.items():
        matches = [header for alias in aliases for header in normalized_headers.get(_normalize_header(alias), [])]
        if len(set(matches)) == 1:
            suggestions[canonical_column] = matches[0]
    return suggestions


def parse_appointments_csv(
    raw_csv: bytes, *, mapping: AppointmentColumnMapping | None = None
) -> ParsedAppointmentImport:
    content = _decode_csv(raw_csv)
    reader = csv.DictReader(StringIO(content))
    fieldnames = list(reader.fieldnames or [])
    if len(fieldnames) != len(set(fieldnames)):
        raise AppointmentImportError("The CSV has duplicate column headers.")
    effective_mapping = mapping or AppointmentColumnMapping(
        column_mapping={column: column for column in fieldnames if column in CANONICAL_COLUMNS}, status_mapping={}
    )
    _validate_mapping(effective_mapping, fieldnames)
    missing_columns = sorted(REQUIRED_COLUMNS - set(effective_mapping.column_mapping))
    if missing_columns:
        raise AppointmentImportError(f"Missing required columns: {', '.join(missing_columns)}")

    valid_rows: list[NormalizedAppointment] = []
    errors: list[str] = []
    total_rows = 0
    status_map = {**STATUS_MAP, **{key.strip().lower(): value for key, value in effective_mapping.status_mapping.items()}}
    for row_number, source_row in enumerate(reader, start=2):
        total_rows += 1
        row = {
            canonical_column: source_row.get(source_column)
            for canonical_column, source_column in effective_mapping.column_mapping.items()
        }
        try:
            valid_rows.append(_normalize_row(row, row_number, status_map=status_map))
        except AppointmentImportError as error:
            errors.append(str(error))

    return ParsedAppointmentImport(total_rows=total_rows, rows=valid_rows, errors=errors)


def _read_fieldnames(raw_csv: bytes) -> list[str]:
    content = _decode_csv(raw_csv)
    reader = csv.DictReader(StringIO(content))
    fieldnames = list(reader.fieldnames or [])
    if not fieldnames:
        raise AppointmentImportError("The CSV must include a header row.")
    if len(fieldnames) != len(set(fieldnames)):
        raise AppointmentImportError("The CSV has duplicate column headers.")
    return fieldnames


def _decode_csv(raw_csv: bytes) -> str:
    if not raw_csv:
        raise AppointmentImportError("The CSV file is empty.")

    try:
        return raw_csv.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise AppointmentImportError("The CSV must use UTF-8 encoding.") from error


def _normalize_row(
    row: dict[str, str | None], row_number: int, *, status_map: dict[str, str]
) -> NormalizedAppointment:
    appointment_id = _required_text(row, "appointment_id", row_number)
    offering_name = _required_text(row, "offering_name", row_number)
    visit_start_at = _parse_datetime(row.get("visit_start_at"), row_number, "visit_start_at")
    visit_end_at = _parse_datetime(row.get("visit_end_at"), row_number, "visit_end_at", required=False)
    booked_at = _parse_datetime(row.get("booked_at"), row_number, "booked_at", required=False)
    if visit_end_at and visit_end_at < visit_start_at:
        raise AppointmentImportError(f"Row {row_number}: visit_end_at cannot be before visit_start_at.")

    normalized_status = status_map.get((row.get("status") or "").strip().lower())
    if normalized_status is None:
        raise AppointmentImportError(f"Row {row_number}: unsupported status.")

    customer_token = _optional_text(row.get("customer_token"))
    if customer_token and len(customer_token) < 16:
        raise AppointmentImportError(f"Row {row_number}: customer_token must be a pseudonymous token, not a raw identifier.")

    raw_payload = {
        key: (value or "")
        for key, value in row.items()
        if key is not None and key in PERSISTED_SOURCE_COLUMNS
    }
    return NormalizedAppointment(
        row_number=row_number,
        appointment_id=appointment_id,
        source_system=_optional_text(row.get("source")) or "csv",
        source_record_id=_optional_text(row.get("source_record_id")) or appointment_id,
        customer_token=customer_token,
        location_key=_optional_text(row.get("location_key")),
        visit_start_at=visit_start_at,
        visit_end_at=visit_end_at,
        booked_at=booked_at,
        offering_name=offering_name,
        staff_key=_optional_text(row.get("staff_key")),
        status=normalized_status,
        listed_price=_parse_money(row.get("listed_price"), row_number, "listed_price"),
        paid_amount=_parse_money(row.get("paid_amount"), row_number, "paid_amount"),
        discount_amount=_parse_money(row.get("discount_amount"), row_number, "discount_amount"),
        raw_payload=raw_payload,
    )


def _required_text(row: dict[str, str | None], field_name: str, row_number: int) -> str:
    value = _optional_text(row.get(field_name))
    if not value:
        raise AppointmentImportError(f"Row {row_number}: {field_name} is required.")
    return value


def _optional_text(value: str | None) -> str | None:
    text = (value or "").strip()
    return text or None


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


def _parse_money(value: str | None, row_number: int, field_name: str) -> Decimal | None:
    text = (value or "").strip()
    if not text:
        return None
    try:
        amount = Decimal(text)
    except InvalidOperation as error:
        raise AppointmentImportError(f"Row {row_number}: {field_name} must be a decimal amount.") from error
    if amount < 0:
        raise AppointmentImportError(f"Row {row_number}: {field_name} cannot be negative.")
    return amount


def _validate_mapping(mapping: AppointmentColumnMapping, fieldnames: list[str]) -> None:
    unknown_canonical_columns = sorted(set(mapping.column_mapping) - CANONICAL_COLUMNS)
    if unknown_canonical_columns:
        raise AppointmentImportError(f"Unsupported canonical columns: {', '.join(unknown_canonical_columns)}")
    missing_source_columns = sorted(set(mapping.column_mapping.values()) - set(fieldnames))
    if missing_source_columns:
        raise AppointmentImportError(f"Mapped source columns are missing: {', '.join(missing_source_columns)}")
    if len(mapping.column_mapping.values()) != len(set(mapping.column_mapping.values())):
        raise AppointmentImportError("One source column cannot map to multiple Appointment fields.")
    invalid_statuses = sorted(set(mapping.status_mapping.values()) - set(STATUS_MAP.values()))
    if invalid_statuses:
        raise AppointmentImportError(f"Unsupported mapped statuses: {', '.join(invalid_statuses)}")
    customer_token_source = mapping.column_mapping.get("customer_token")
    if customer_token_source and any(marker in _normalize_header(customer_token_source) for marker in SENSITIVE_IDENTIFIER_HEADER_MARKERS):
        raise AppointmentImportError("customer_token cannot map from a raw phone, email, or government identifier column.")


def validate_column_mapping_definition(mapping: AppointmentColumnMapping) -> None:
    """Validate a reusable mapping without requiring a particular uploaded file yet."""
    _validate_mapping(mapping, list(mapping.column_mapping.values()))
    missing_columns = sorted(REQUIRED_COLUMNS - set(mapping.column_mapping))
    if missing_columns:
        raise AppointmentImportError(f"Missing required columns: {', '.join(missing_columns)}")


def _normalize_header(value: str) -> str:
    return re.sub(r"[^0-9a-z가-힣]", "", value.strip().lower())
