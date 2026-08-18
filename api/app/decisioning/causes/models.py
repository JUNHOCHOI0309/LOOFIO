from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import Field

from app.decisioning.fields import ContractModel


CAUSE_ANALYSIS_VERSION = "cause-analysis-v1"
CAUSE_PRIORITY_VERSION = "cause-priority-v1"


class CauseCode(str, Enum):
    DATA_QUALITY_ARTIFACT = "DATA_QUALITY_ARTIFACT"
    CAPACITY_OR_OPERATION_CONSTRAINT = "CAPACITY_OR_OPERATION_CONSTRAINT"
    OFFER_SLOT_MISMATCH = "OFFER_SLOT_MISMATCH"
    RETENTION_GAP = "RETENTION_GAP"
    DISCOVERABILITY_GAP = "DISCOVERABILITY_GAP"
    DEMAND_DEFICIT = "DEMAND_DEFICIT"
    CONVERSION_FRICTION = "CONVERSION_FRICTION"
    CHANNEL_MISMATCH = "CHANNEL_MISMATCH"
    VALUE_OR_PRICE_FRICTION = "VALUE_OR_PRICE_FRICTION"
    CANCELLATION_LEAKAGE = "CANCELLATION_LEAKAGE"


class RequirementLevel(str, Enum):
    REQUIRED = "R"
    OPTIONAL = "O"
    BLOCKING = "B"
    CONDITIONAL = "C"


class CandidateStatus(str, Enum):
    REVIEWABLE = "REVIEWABLE"
    NEEDS_DATA = "NEEDS_DATA"
    DEPRIORITIZED = "DEPRIORITIZED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    BLOCKED = "BLOCKED"


class CauseRunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    NEEDS_DATA = "NEEDS_DATA"
    BLOCKED_BY_DATA_QUALITY = "BLOCKED_BY_DATA_QUALITY"
    INVALID_INPUT = "INVALID_INPUT"


class EvidenceStrength(str, Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    INSUFFICIENT = "insufficient"


class DiagnosticPriority(str, Enum):
    REQUIRED = "required"
    BLOCKING = "blocking"
    OPTIONAL = "optional"


class CauseInputRequirement(ContractModel):
    field_path: str = Field(min_length=1)
    level: RequirementLevel
    description: str = Field(min_length=1)


class CauseDefinition(ContractModel):
    code: CauseCode
    stable_order: int = Field(ge=0)
    hypothesis: str = Field(min_length=1)
    core_for_low_demand_slot: bool
    requirements: tuple[CauseInputRequirement, ...]
    conditional_signal_path: str | None = None


class CauseInputIssue(ContractModel):
    field_path: str
    level: RequirementLevel
    reason_code: str


class DownstreamBlocker(ContractModel):
    field_path: str
    reason_code: str
    blocked_capability: str


class CausePriorityBreakdown(ContractModel):
    evidence_support: float = Field(ge=0, le=35)
    pattern_consistency: float = Field(ge=0, le=20)
    data_completeness: float = Field(ge=0, le=20)
    contradiction_absence: float = Field(ge=0, le=15)
    testability: float = Field(ge=0, le=10)
    total: float = Field(ge=0, le=100)


class DiagnosticQuestion(ContractModel):
    id: str
    cause_code: CauseCode
    field_path: str
    question: str
    answer_type: str
    priority: DiagnosticPriority
    why_needed: str
    allowed_answers: tuple[str | bool | int, ...]
    pii_class: str = "none"
    readiness_effect: dict[str, str]


class CauseCandidate(ContractModel):
    cause_code: CauseCode
    status: CandidateStatus
    hypothesis: str
    review_priority_score: float | None = Field(default=None, ge=0, le=100)
    score_version: str = CAUSE_PRIORITY_VERSION
    score_breakdown: CausePriorityBreakdown | None = None
    evidence_strength: EvidenceStrength
    opportunity_evidence_refs: tuple[str, ...]
    supporting_evidence_refs: tuple[str, ...]
    contradicting_evidence_refs: tuple[str, ...]
    required_inputs: tuple[str, ...]
    missing_required_inputs: tuple[CauseInputIssue, ...]
    missing_optional_inputs: tuple[CauseInputIssue, ...]
    downstream_blockers: tuple[DownstreamBlocker, ...]
    diagnostic_question_ids: tuple[str, ...]
    limitations: tuple[str, ...]


class CauseStrategyHandoff(ContractModel):
    strategy_ready: bool
    blocked_reasons: tuple[str, ...]
    candidate_codes: tuple[CauseCode, ...]


class CauseAnalysisResult(ContractModel):
    id: str
    version: str = CAUSE_ANALYSIS_VERSION
    status: CauseRunStatus
    tenant_id: str
    business_id: str
    opportunity_id: str
    opportunity_type: str = "LOW_DEMAND_SLOT"
    decision_context_snapshot_id: str
    decision_context_hash: str
    generated_at: datetime
    candidates: tuple[CauseCandidate, ...]
    recommended_diagnostics: tuple[DiagnosticQuestion, ...]
    global_limitations: tuple[str, ...]
    next_stage: CauseStrategyHandoff
