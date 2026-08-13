from datetime import datetime

from pydantic import BaseModel, Field


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
