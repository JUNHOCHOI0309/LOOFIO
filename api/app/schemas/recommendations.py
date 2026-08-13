from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.metrics import Money


DecisionType = Literal["approved", "rejected", "modified", "later"]


class RecommendationExpectedEffect(BaseModel):
    value_low: Money
    value_high: Money
    assumptions: list[str]
    basis: Literal["opportunity_estimate"]


class RecommendationModification(BaseModel):
    test_duration_weeks: int | None = Field(default=None, ge=1, le=12)
    manual_notes: str | None = Field(default=None, max_length=500)


class RecommendationDecisionRequest(BaseModel):
    decision: DecisionType
    reason_code: str | None = Field(default=None, max_length=64, pattern=r"^[A-Z0-9_]+$")
    reason_text: str | None = Field(default=None, max_length=1000)
    modified_payload: RecommendationModification | None = None

    @model_validator(mode="after")
    def validate_modification(self) -> "RecommendationDecisionRequest":
        if self.decision == "modified" and not self.modified_payload:
            raise ValueError("modified 결정에는 수정 내용이 필요합니다.")
        if self.decision != "modified" and self.modified_payload:
            raise ValueError("수정 내용은 modified 결정에서만 사용할 수 있습니다.")
        return self


class RecommendationDecision(BaseModel):
    id: str
    decision: DecisionType
    reason_code: str | None = None
    reason_text: str | None = None
    modified_payload: RecommendationModification | None = None
    decided_by_user_id: str
    decided_at: datetime


class Recommendation(BaseModel):
    id: str
    opportunity_id: str
    version: str
    status: Literal["draft", "approved", "rejected", "modified", "later"]
    hypothesis: str
    action_type: str
    channel: str
    target_segment: dict[str, str | int]
    expected_effect: RecommendationExpectedEffect | None = None
    confidence: float = Field(ge=0, le=1)
    explanation: str
    limitations: list[str]
    created_at: datetime
    latest_decision: RecommendationDecision | None = None
