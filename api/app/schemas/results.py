from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.metrics import Money


RESULT_VERSION = "manual-action-result-v1"
MEASUREMENT_METHOD_VERSION = "same-window-prior-four-weeks-v2"


class ActualSpend(BaseModel):
    amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    currency: Literal["KRW"] = "KRW"


class CreateActionResultRequest(BaseModel):
    execution_summary: str = Field(min_length=2, max_length=1000)
    measurement_start_at: datetime
    measurement_end_at: datetime
    actual_spend: ActualSpend | None = None
    outcome_notes: str | None = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_window(self) -> "CreateActionResultRequest":
        if self.measurement_start_at.tzinfo is None or self.measurement_end_at.tzinfo is None:
            raise ValueError("측정 기간은 UTC offset을 포함해야 합니다.")
        if self.measurement_end_at <= self.measurement_start_at:
            raise ValueError("측정 종료 시점은 시작 시점 이후여야 합니다.")
        return self


class ActionResult(BaseModel):
    id: str
    action_id: str
    version: str
    execution_summary: str
    measurement_start_at: datetime
    measurement_end_at: datetime
    actual_spend: ActualSpend | None = None
    outcome_notes: str | None = None
    recorded_by_user_id: str
    recorded_at: datetime


class ActionResultCreateResult(BaseModel):
    result: ActionResult
    replayed: bool = False


class MeasurementMetrics(BaseModel):
    appointment_count: float = Field(ge=0)
    completed_count: float = Field(ge=0)
    cancelled_count: float = Field(ge=0)
    no_show_count: float = Field(ge=0)
    actual_revenue: Money


class MeasurementDelta(BaseModel):
    """Signed difference between observed and baseline metrics."""

    appointment_count: float
    completed_count: float
    cancelled_count: float
    no_show_count: float
    actual_revenue: Money


class ActionMeasurement(BaseModel):
    action_id: str
    result_id: str
    method_version: str = MEASUREMENT_METHOD_VERSION
    observation_window: dict[str, datetime]
    baseline_window_count: int = Field(ge=0)
    observed: MeasurementMetrics
    baseline_average: MeasurementMetrics | None = None
    change_from_baseline: MeasurementDelta | None = None
    limitations: list[str]
