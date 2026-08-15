from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


ActionStatus = Literal["planned", "in_progress", "completed", "cancelled"]


class PlannedBudget(BaseModel):
    amount: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    currency: Literal["KRW"] = "KRW"


class CreateManualActionRequest(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    execution_notes: str | None = Field(default=None, max_length=1000)
    planned_start_at: datetime
    planned_end_at: datetime | None = None
    planned_budget: PlannedBudget | None = None

    @model_validator(mode="after")
    def validate_schedule(self) -> "CreateManualActionRequest":
        if self.planned_start_at.tzinfo is None:
            raise ValueError("planned_start_at은 UTC offset을 포함해야 합니다.")
        if self.planned_end_at and self.planned_end_at.tzinfo is None:
            raise ValueError("planned_end_at은 UTC offset을 포함해야 합니다.")
        if self.planned_end_at and self.planned_end_at < self.planned_start_at:
            raise ValueError("planned_end_at은 planned_start_at 이후여야 합니다.")
        return self


class UpdateActionStatusRequest(BaseModel):
    status: ActionStatus
    note: str | None = Field(default=None, max_length=1000)


class ActionStatusEvent(BaseModel):
    id: str
    status: ActionStatus
    note: str | None = None
    changed_by_user_id: str
    created_at: datetime


class Action(BaseModel):
    id: str
    business_id: str
    recommendation_id: str
    version: str
    status: ActionStatus
    action_type: str
    channel: str
    title: str
    execution_notes: str | None = None
    planned_start_at: datetime
    planned_end_at: datetime | None = None
    planned_budget: PlannedBudget | None = None
    created_by_user_id: str
    started_at: datetime | None = None
    completed_at: datetime | None = None
    cancelled_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    status_events: list[ActionStatusEvent] = Field(default_factory=list)


class ActionCreateResult(BaseModel):
    action: Action
    replayed: bool = False
