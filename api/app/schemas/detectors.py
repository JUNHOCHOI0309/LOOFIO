from pydantic import BaseModel, Field


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
