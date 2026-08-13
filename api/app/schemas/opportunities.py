from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.metrics import Money


class OpportunityObservation(BaseModel):
    average_appointments_per_week: float = Field(ge=0)
    comparison_median_per_week: float = Field(gt=0)
    demand_index: float = Field(ge=0)
    observed_weeks: int = Field(ge=0)


class OpportunityEstimate(BaseModel):
    value_low: Money
    value_high: Money
    assumptions: list[str]


class OpportunityDetector(BaseModel):
    code: str
    version: str


class Opportunity(BaseModel):
    id: str
    type: str
    status: str
    segment: dict[str, str | int]
    observation: OpportunityObservation
    estimate: OpportunityEstimate | None = None
    score: float = Field(ge=0, le=100)
    confidence: float = Field(ge=0, le=1)
    limitations: list[str]
    detector: OpportunityDetector
    first_detected_at: datetime
    last_detected_at: datetime


class OpportunityRefreshResult(BaseModel):
    detector_version: str
    refreshed_count: int = Field(ge=0)
    opportunities: list[Opportunity]
