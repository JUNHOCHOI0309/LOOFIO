from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from app.decisioning.causes.models import CauseAnalysisResult
from app.decisioning.context import DecisionContextSnapshot
from app.decisioning.fields import ContractModel, require_aware
from app.decisioning.strategies.models import StrategyAnalysisResult
from app.schemas.cause_analyses import PreviewMetadata


STRATEGY_PREVIEW_CONTRACT_VERSION = "strategy-preview-v1"


class StrategyPreviewRequest(ContractModel):
    """Unpersisted input that recalculates Cause and Strategy for one opportunity."""

    contract_version: Literal["strategy-preview-v1"] = STRATEGY_PREVIEW_CONTRACT_VERSION
    as_of: datetime
    decision_context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("as_of")
    @classmethod
    def validate_as_of(cls, value: datetime) -> datetime:
        return require_aware(value, "as_of")


class StrategyPreviewResponse(ContractModel):
    preview: PreviewMetadata
    decision_context: DecisionContextSnapshot
    cause_analysis: CauseAnalysisResult
    strategy_run: StrategyAnalysisResult
