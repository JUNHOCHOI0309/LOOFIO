from pydantic import BaseModel, Field

from app.schemas.metrics import Money


class LowDemandSlotCandidate(BaseModel):
    weekday: str
    slot_start_hour: int = Field(ge=0, le=22)
    observed_weeks: int = Field(ge=0)
    average_appointments_per_week: float = Field(ge=0)
    comparison_median_per_week: float = Field(gt=0)
    demand_index: float = Field(ge=0)


class LowDemandSlotDetection(BaseModel):
    detector_version: str
    minimum_observed_weeks: int
    observed_weeks: int = Field(ge=0)
    candidates: list[LowDemandSlotCandidate]
    limitations: list[str]


class RevenueGapCandidate(BaseModel):
    weekday: str
    slot_start_hour: int = Field(ge=0, le=22)
    observed_weeks: int = Field(ge=0)
    average_appointments_per_week: float = Field(ge=0)
    comparison_median_per_week: float = Field(gt=0)
    weekly_booking_gap: float = Field(gt=0)
    completed_payment_sample_count: int = Field(ge=1)
    average_reference_paid_amount: Money
    monthly_value_low: Money
    monthly_value_high: Money


class RevenueGapDetection(BaseModel):
    detector_version: str
    source_detector_version: str
    minimum_completed_payment_samples: int = Field(ge=1)
    observed_weeks: int = Field(ge=0)
    candidates: list[RevenueGapCandidate]
    limitations: list[str]
