from datetime import date

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


class DormantCustomerCandidate(BaseModel):
    customer_token: str = Field(min_length=16)
    latest_offering_name: str | None = None
    completed_visit_count: int = Field(ge=1)
    last_completed_visit_date: date
    days_since_last_completed_visit: int = Field(ge=0)
    expected_revisit_days: float = Field(gt=0)
    overdue_ratio: float = Field(ge=0)
    baseline_source: str
    reference_interval_count: int = Field(ge=1)


class DormantCustomerDetection(BaseModel):
    detector_version: str
    as_of_date: date
    minimum_overdue_ratio: float = Field(gt=0)
    completed_customer_count: int = Field(ge=0)
    candidates: list[DormantCustomerCandidate]
    limitations: list[str]


class ServiceDemandGapCandidate(BaseModel):
    offering_name: str = Field(min_length=1)
    weekday: str
    slot_start_hour: int = Field(ge=0, le=22)
    observed_weeks: int = Field(ge=0)
    offering_appointment_count: int = Field(ge=1)
    slot_appointment_count: int = Field(ge=1)
    slot_offering_appointment_count: int = Field(ge=1)
    business_offering_share: float = Field(ge=0, le=1)
    slot_offering_share: float = Field(ge=0, le=1)
    expected_slot_offering_appointment_count: float = Field(ge=0)
    share_index: float = Field(ge=0)


class ServiceDemandGapDetection(BaseModel):
    detector_version: str
    minimum_observed_weeks: int = Field(ge=1)
    observed_weeks: int = Field(ge=0)
    minimum_offering_appointments: int = Field(ge=1)
    minimum_slot_appointments: int = Field(ge=1)
    maximum_share_index: float = Field(gt=0)
    candidates: list[ServiceDemandGapCandidate]
    limitations: list[str]
