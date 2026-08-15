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


class CancellationHotspotCandidate(BaseModel):
    weekday: str
    slot_start_hour: int = Field(ge=0, le=22)
    offering_name: str = Field(min_length=1)
    observed_weeks: int = Field(ge=0)
    appointment_count: int = Field(ge=1)
    cancelled_count: int = Field(ge=0)
    no_show_count: int = Field(ge=0)
    disruption_count: int = Field(ge=0)
    disruption_rate: float = Field(ge=0, le=1)
    baseline_disruption_rate: float = Field(ge=0, le=1)
    rate_multiple: float = Field(ge=0)


class CancellationHotspotDetection(BaseModel):
    detector_version: str
    minimum_appointment_samples: int = Field(ge=1)
    minimum_baseline_multiple: float = Field(gt=0)
    observed_weeks: int = Field(ge=0)
    baseline_appointment_count: int = Field(ge=0)
    baseline_disruption_count: int = Field(ge=0)
    baseline_disruption_rate: float = Field(ge=0, le=1)
    candidates: list[CancellationHotspotCandidate]
    limitations: list[str]
