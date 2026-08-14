from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class AppointmentPreviewRow(BaseModel):
    source_record_id: str
    visit_start_at: datetime
    visit_end_at: datetime | None = None
    offering_name: str
    status: str
    customer_token_present: bool


class AppointmentImportPreview(BaseModel):
    business_id: str
    total_rows: int = Field(ge=0)
    valid_rows: int = Field(ge=0)
    invalid_rows: int = Field(ge=0)
    errors: list[str]
    preview: list[AppointmentPreviewRow]


class AppointmentImportResult(BaseModel):
    import_id: str
    business_id: str
    total_rows: int = Field(ge=0)
    imported_rows: int = Field(ge=0)
    duplicate_rows: int = Field(ge=0)
    invalid_rows: int = Field(ge=0)
    status: str
    replayed: bool = False


class AppointmentImportInspection(BaseModel):
    source_columns: list[str]
    suggested_column_mapping: dict[str, str]
    required_columns: list[str]


class AppointmentImportMappingRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    column_mapping: dict[str, str] = Field(min_length=4)
    status_mapping: dict[str, str] = Field(default_factory=dict)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 2:
            raise ValueError("매핑 이름은 공백을 제외하고 두 글자 이상이어야 합니다.")
        return normalized


class AppointmentImportMapping(BaseModel):
    id: str
    business_id: str
    name: str
    column_mapping: dict[str, str]
    status_mapping: dict[str, str]
    created_at: datetime
    updated_at: datetime
