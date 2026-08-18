from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import Field

from app.decisioning.fields import ContractModel


STRATEGY_ENGINE_VERSION = "strategy-engine-v1"
STRATEGY_PRIORITY_VERSION = "strategy-priority-v1"


class StrategyFamily(str, Enum):
    DATA_COLLECTION = "DATA_COLLECTION"
    CAPACITY_OPERATION = "CAPACITY_OPERATION"
    RETENTION_REACTIVATION = "RETENTION_REACTIVATION"
    DISCOVERABILITY = "DISCOVERABILITY"
    CONVERSION = "CONVERSION"
    OFFER_PACKAGING = "OFFER_PACKAGING"
    PARTNERSHIP_REFERRAL = "PARTNERSHIP_REFERRAL"
    ACQUISITION = "ACQUISITION"
    CANCELLATION_RECOVERY = "CANCELLATION_RECOVERY"
    NO_ACTION = "NO_ACTION"


class StrategyClass(str, Enum):
    EXECUTION = "EXECUTION"
    OPERATIONAL = "OPERATIONAL"
    DIAGNOSTIC = "DIAGNOSTIC"
    HOLD = "HOLD"


class StrategyRelation(str, Enum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    CONDITIONAL = "CONDITIONAL"
    INHIBITORY = "INHIBITORY"


class StrategyCandidateStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    ELIGIBLE_WITH_LIMITATIONS = "ELIGIBLE_WITH_LIMITATIONS"
    NEEDS_DATA = "NEEDS_DATA"
    NEEDS_POLICY_REVIEW = "NEEDS_POLICY_REVIEW"
    INFEASIBLE = "INFEASIBLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    DEPRIORITIZED = "DEPRIORITIZED"


class StrategyRunStatus(str, Enum):
    COMPLETED = "COMPLETED"
    MULTIPLE_VALID_OPTIONS = "MULTIPLE_VALID_OPTIONS"
    NEEDS_DATA = "NEEDS_DATA"
    NEEDS_POLICY_REVIEW = "NEEDS_POLICY_REVIEW"
    NO_EXECUTABLE_STRATEGY = "NO_EXECUTABLE_STRATEGY"
    INVALID_INPUT = "INVALID_INPUT"


class StrategyDefinition(ContractModel):
    family: StrategyFamily
    strategy_class: StrategyClass
    stable_order: int = Field(ge=0)
    minimum_readiness: str


class StrategyCauseMapping(ContractModel):
    cause_code: str
    strategy_family: StrategyFamily
    relation: StrategyRelation


class StrategyInputIssue(ContractModel):
    field_path: str
    reason_code: str


class StrategyBlocker(ContractModel):
    code: str
    field_path: str
    reason: str


class StrategyPriorityBreakdown(ContractModel):
    expected_net_value: float = Field(ge=0, le=25)
    evidence_fit: float = Field(ge=0, le=20)
    operational_feasibility: float = Field(ge=0, le=15)
    measurement_feasibility: float = Field(ge=0, le=15)
    policy_safety: float = Field(ge=0, le=10)
    time_to_learning: float = Field(ge=0, le=10)
    learning_value: float = Field(ge=0, le=5)
    total: float = Field(ge=0, le=100)


class CollectionPlanItem(ContractModel):
    field_path: str
    why_needed: str
    owner: str
    collection_method: str
    deadline: date
    verification_rule: str
    unblocks: tuple[StrategyFamily, ...]


class NoActionPlan(ContractModel):
    reason_codes: tuple[str, ...]
    monitoring_metric: str
    monitoring_segment: str
    review_at: date
    reopen_triggers: tuple[str, ...]
    current_limitations: tuple[str, ...]


class StrategyCandidate(ContractModel):
    strategy_family: StrategyFamily
    strategy_class: StrategyClass
    status: StrategyCandidateStatus
    selected: bool = False
    supporting_cause_refs: tuple[str, ...]
    inhibitory_cause_refs: tuple[str, ...]
    required_inputs: tuple[str, ...]
    missing_inputs: tuple[StrategyInputIssue, ...]
    blockers: tuple[StrategyBlocker, ...]
    economics_status: str
    measurement_status: str
    policy_status: str
    review_priority_score: float | None = Field(default=None, ge=0, le=100)
    score_version: str = STRATEGY_PRIORITY_VERSION
    score_breakdown: StrategyPriorityBreakdown | None = None
    selection_reason: str
    exclusion_reasons: tuple[str, ...]
    playbook_candidates: tuple[str, ...]
    limitations: tuple[str, ...]


class AlternativeComparison(ContractModel):
    strategy_a: StrategyFamily
    strategy_b: StrategyFamily
    preferred: StrategyFamily | None
    reason: str


class StrategyPlaybookHandoff(ContractModel):
    playbook_resolution_ready: bool
    selected_strategy: StrategyFamily | None
    top_alternatives: tuple[StrategyFamily, ...]
    blocked_reasons: tuple[str, ...]
    candidate_playbook_ids: tuple[str, ...]


class StrategyAnalysisResult(ContractModel):
    id: str
    version: str = STRATEGY_ENGINE_VERSION
    status: StrategyRunStatus
    tenant_id: str
    business_id: str
    opportunity_id: str
    cause_analysis_id: str
    decision_context_snapshot_id: str
    decision_context_hash: str
    generated_at: datetime
    candidates: tuple[StrategyCandidate, ...]
    selected_strategy: StrategyFamily | None
    alternative_comparisons: tuple[AlternativeComparison, ...]
    data_collection_plan: tuple[CollectionPlanItem, ...] = ()
    no_action_plan: NoActionPlan | None = None
    next_stage: StrategyPlaybookHandoff
    global_limitations: tuple[str, ...]
