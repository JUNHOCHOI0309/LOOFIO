from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import Field, field_validator

from app.decisioning.causes.models import CauseAnalysisResult
from app.decisioning.context import DecisionContextSnapshot
from app.decisioning.fields import ContractModel, require_aware


CAUSE_PREVIEW_CONTRACT_VERSION = "cause-preview-v1"


class CauseAnalysisPreviewRequest(ContractModel):
    """Unpersisted input for a LOW_DEMAND_SLOT Cause Analysis preview."""

    contract_version: Literal["cause-preview-v1"] = CAUSE_PREVIEW_CONTRACT_VERSION
    as_of: datetime
    decision_context: dict[str, Any] = Field(default_factory=dict)

    @field_validator("as_of")
    @classmethod
    def validate_as_of(cls, value: datetime) -> datetime:
        return require_aware(value, "as_of")


class PreviewMetadata(ContractModel):
    preview_id: str
    persisted: Literal[False] = False
    input_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    generated_at: datetime
    as_of: datetime
    engine_versions: dict[str, str]


class CauseAnalysisPreviewResponse(ContractModel):
    preview: PreviewMetadata
    decision_context: DecisionContextSnapshot
    cause_analysis: CauseAnalysisResult
