from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.metrics import Money


class OpportunityObservation(BaseModel):
    kind: str = "low_demand"
    observed_weeks: int | None = Field(default=None, ge=0)
    average_appointments_per_week: float | None = Field(default=None, ge=0)
    comparison_median_per_week: float | None = Field(default=None, gt=0)
    demand_index: float | None = Field(default=None, ge=0)
    appointment_count: int | None = Field(default=None, ge=0)
    cancelled_count: int | None = Field(default=None, ge=0)
    no_show_count: int | None = Field(default=None, ge=0)
    disruption_rate: float | None = Field(default=None, ge=0, le=1)
    baseline_disruption_rate: float | None = Field(default=None, ge=0, le=1)
    rate_multiple: float | None = Field(default=None, ge=0)
    customer_reference: str | None = None
    last_completed_visit_date: str | None = None
    days_since_last_completed_visit: int | None = Field(default=None, ge=0)
    expected_revisit_days: float | None = Field(default=None, gt=0)
    overdue_ratio: float | None = Field(default=None, ge=0)
    baseline_source: str | None = None
    offering_appointment_count: int | None = Field(default=None, ge=0)
    slot_appointment_count: int | None = Field(default=None, ge=0)
    slot_offering_appointment_count: int | None = Field(default=None, ge=0)
    business_offering_share: float | None = Field(default=None, ge=0, le=1)
    slot_offering_share: float | None = Field(default=None, ge=0, le=1)
    share_index: float | None = Field(default=None, ge=0)


class OpportunityEstimate(BaseModel):
    value_low: Money
    value_high: Money
    assumptions: list[str]


class OpportunityDetector(BaseModel):
    code: str
    version: str


class OpportunityScoreBreakdown(BaseModel):
    impact: float = Field(ge=0, le=35)
    confidence: float = Field(ge=0, le=30)
    persistence: float = Field(ge=0, le=20)
    actionability: float = Field(ge=0, le=15)
    total: float = Field(ge=0, le=100)


class OpportunityScoring(BaseModel):
    version: str
    breakdown: OpportunityScoreBreakdown | None = None


class Opportunity(BaseModel):
    id: str
    type: str
    status: str
    segment: dict[str, str | int]
    observation: OpportunityObservation
    estimate: OpportunityEstimate | None = None
    score: float = Field(ge=0, le=100)
    scoring: OpportunityScoring
    confidence: float = Field(ge=0, le=1)
    limitations: list[str]
    detector: OpportunityDetector
    first_detected_at: datetime
    last_detected_at: datetime


class OpportunityRefreshResult(BaseModel):
    detector_version: str
    refreshed_count: int = Field(ge=0)
    opportunities: list[Opportunity]
    refreshed_detector_versions: list[str] = Field(default_factory=list)
