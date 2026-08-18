from __future__ import annotations

from enum import Enum
from typing import Callable

from pydantic import Field

from app.decisioning.context import (
    ConnectionStatus,
    DecisionContextSnapshot,
    EconomicsStatus,
    TrackingCapability,
)
from app.decisioning.fields import ContractModel, DecisionField, DecisionFieldStatus


READINESS_VERSION = "decision-readiness-v1"


class ReadinessLevel(str, Enum):
    D0 = "D0"
    D1 = "D1"
    D2 = "D2"
    D3 = "D3"
    D4 = "D4"


class RequirementOwner(str, Enum):
    BUSINESS_OWNER = "business_owner"
    OPERATIONS = "operations"
    MARKETING = "marketing"
    FINANCE = "finance"
    DATA = "data"
    POLICY = "policy"


class MissingRequirement(ContractModel):
    field_path: str
    reason_code: str
    owner: RequirementOwner
    collection_method: str
    completion_rule: str
    unlocks: tuple[str, ...] = Field(min_length=1)


class DecisionReadiness(ContractModel):
    level: ReadinessLevel
    version: str = READINESS_VERSION
    available_capabilities: tuple[str, ...]
    blocked_capabilities: tuple[str, ...]
    missing_requirements: tuple[MissingRequirement, ...]


_CAPABILITIES = {
    ReadinessLevel.D0: (
        "cause_candidate_draft",
        "missing_data_resolution",
        "diagnostic_questions",
    ),
    ReadinessLevel.D1: (
        "cause_prioritization",
        "capacity_review",
        "operational_diagnosis",
    ),
    ReadinessLevel.D2: (
        "strategy_comparison",
        "non_contact_playbook",
        "feasibility_assessment",
    ),
    ReadinessLevel.D3: (
        "experiment_draft",
        "recommendation_package",
        "quality_validation",
    ),
    ReadinessLevel.D4: (
        "contribution_estimate",
        "break_even_analysis",
        "economics_ranking",
        "net_contribution_measurement",
    ),
}


class _Requirement:
    def __init__(
        self,
        level: ReadinessLevel,
        field_path: str,
        owner: RequirementOwner,
        collection_method: str,
        completion_rule: str,
        unlocks: tuple[str, ...],
        check: Callable[[DecisionContextSnapshot], tuple[bool, str]],
    ) -> None:
        self.level = level
        self.field_path = field_path
        self.owner = owner
        self.collection_method = collection_method
        self.completion_rule = completion_rule
        self.unlocks = unlocks
        self.check = check


def _field_state(field: DecisionField[object] | None, *, allow_not_applicable: bool = False) -> tuple[bool, str]:
    if field is None:
        return False, "MISSING"
    if field.status is DecisionFieldStatus.KNOWN:
        return True, ""
    if allow_not_applicable and field.status is DecisionFieldStatus.NOT_APPLICABLE:
        return True, ""
    return False, field.status.value.upper()


def _path_field(path: str, *, allow_not_applicable: bool = False) -> Callable[[DecisionContextSnapshot], tuple[bool, str]]:
    parts = path.split(".")

    def check(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
        value: object = snapshot
        for part in parts:
            value = getattr(value, part, None)
            if value is None:
                return False, "MISSING"
        return _field_state(value if isinstance(value, DecisionField) else None, allow_not_applicable=allow_not_applicable)

    return check


def _context_present(path: str) -> Callable[[DecisionContextSnapshot], tuple[bool, str]]:
    def check(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
        return (getattr(snapshot, path) is not None, "MISSING")

    return check


def _channel_available(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
    available = {
        ConnectionStatus.CONNECTED,
        ConnectionStatus.AVAILABLE_MANUAL,
    }
    return (any(channel.connection_status in available for channel in snapshot.channels), "MISSING")


def _tracked_channel(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
    return (
        any(channel.tracking_capability is not TrackingCapability.NONE for channel in snapshot.channels),
        "TRACKING_NONE",
    )


def _channel_owner(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
    fields = [channel.owner for channel in snapshot.channels]
    if not fields:
        return False, "MISSING"
    if any(field.is_usable and bool(field.value and field.value.strip()) for field in fields):
        return True, ""
    return False, next((field.status.value.upper() for field in fields if not field.is_usable), "MISSING")


def _target_population(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
    candidates = [
        snapshot.operation.target_population_count if snapshot.operation else None,
        snapshot.customer_activation.eligible_cohort_count if snapshot.customer_activation else None,
    ]
    for field in candidates:
        ready, _ = _field_state(field)
        if ready:
            return True, ""
    reasons = [field.status.value.upper() for field in candidates if field is not None]
    return False, reasons[0] if reasons else "MISSING"


def _actual_spend_collection(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
    field = snapshot.measurement.actual_spend_available if snapshot.measurement else None
    ready, reason = _field_state(field)
    if not ready:
        return False, reason
    return (field.value is True, "NOT_AVAILABLE")


def _complete_economics(snapshot: DecisionContextSnapshot) -> tuple[bool, str]:
    if snapshot.economics is None:
        return False, "MISSING"
    return (snapshot.economics.economics_status is EconomicsStatus.COMPLETE, "INCOMPLETE")


def _requirement(
    level: ReadinessLevel,
    field_path: str,
    owner: RequirementOwner,
    collection_method: str,
    completion_rule: str,
    unlocks: tuple[str, ...],
    check: Callable[[DecisionContextSnapshot], tuple[bool, str]] | None = None,
    *,
    allow_not_applicable: bool = False,
) -> _Requirement:
    return _Requirement(
        level,
        field_path,
        owner,
        collection_method,
        completion_rule,
        unlocks,
        check or _path_field(field_path, allow_not_applicable=allow_not_applicable),
    )


_REQUIREMENTS = (
    _requirement(ReadinessLevel.D1, "goal", RequirementOwner.BUSINESS_OWNER, "confirm_primary_goal", "goal context exists", ("cause_prioritization",), _context_present("goal")),
    _requirement(ReadinessLevel.D1, "goal.primary_goal", RequirementOwner.BUSINESS_OWNER, "confirm_primary_goal", "status is known with provenance", ("cause_prioritization",)),
    _requirement(ReadinessLevel.D1, "operation", RequirementOwner.OPERATIONS, "confirm_target_slot", "target slot operation context exists", ("operational_diagnosis",), _context_present("operation")),
    _requirement(ReadinessLevel.D1, "offering", RequirementOwner.OPERATIONS, "select_offering", "offering context exists", ("operational_diagnosis",), _context_present("offering")),
    _requirement(ReadinessLevel.D2, "operation.slot_capacity_confirmed", RequirementOwner.OPERATIONS, "verify_slot_capacity", "capacity status is known", ("strategy_comparison",)),
    _requirement(ReadinessLevel.D2, "operation.offering_available", RequirementOwner.OPERATIONS, "verify_offering_availability", "availability status is known", ("strategy_comparison",)),
    _requirement(ReadinessLevel.D2, "offering.eligibility", RequirementOwner.POLICY, "review_offering_eligibility", "eligibility status is known", ("strategy_comparison",)),
    _requirement(ReadinessLevel.D2, "channels", RequirementOwner.MARKETING, "register_available_channel", "at least one connected or manual channel exists", ("non_contact_playbook",), _channel_available),
    _requirement(ReadinessLevel.D2, "policy.policy_review_status", RequirementOwner.POLICY, "review_hospital_policy", "policy status is known", ("feasibility_assessment",)),
    _requirement(ReadinessLevel.D3, "target_population", RequirementOwner.DATA, "calculate_aggregate_target_population", "target population or eligible cohort count is known", ("experiment_draft",), _target_population),
    _requirement(ReadinessLevel.D3, "customer_activation.marketing_consent_capability", RequirementOwner.POLICY, "verify_consent_capability", "consent capability is known", ("recommendation_package",)),
    _requirement(ReadinessLevel.D3, "channels.tracking_capability", RequirementOwner.MARKETING, "configure_action_tracking", "at least one channel tracking method is not none", ("experiment_draft",), _tracked_channel),
    _requirement(ReadinessLevel.D3, "channels.owner", RequirementOwner.BUSINESS_OWNER, "assign_execution_owner", "at least one available channel owner is known", ("recommendation_package",), _channel_owner),
    _requirement(ReadinessLevel.D3, "measurement.period_start", RequirementOwner.OPERATIONS, "set_experiment_period", "period start is known and timezone-aware", ("experiment_draft",)),
    _requirement(ReadinessLevel.D3, "measurement.period_end", RequirementOwner.OPERATIONS, "set_experiment_period", "period end is known and timezone-aware", ("experiment_draft",)),
    _requirement(ReadinessLevel.D3, "measurement.result_source", RequirementOwner.DATA, "configure_result_source", "result source is known", ("quality_validation",)),
    _requirement(ReadinessLevel.D3, "economics.budget_cap", RequirementOwner.FINANCE, "set_budget_status", "budget cap is known or not applicable", ("recommendation_package",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "economics.economics_status", RequirementOwner.FINANCE, "complete_economics_inputs", "economics status is complete", ("contribution_estimate", "economics_ranking"), _complete_economics),
    _requirement(ReadinessLevel.D4, "economics.expected_net_revenue_per_completion", RequirementOwner.FINANCE, "provide_net_revenue", "net revenue is known", ("contribution_estimate",)),
    _requirement(ReadinessLevel.D4, "economics.variable_cost_per_completion", RequirementOwner.FINANCE, "provide_variable_cost", "variable cost is known or not applicable", ("contribution_estimate",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "economics.benefit_cost_per_completion", RequirementOwner.FINANCE, "provide_benefit_cost", "benefit cost is known or not applicable", ("contribution_estimate",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "economics.incremental_service_cost_per_completion", RequirementOwner.FINANCE, "provide_incremental_service_cost", "incremental service cost is known or not applicable", ("contribution_estimate",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "economics.media_cost", RequirementOwner.FINANCE, "provide_media_cost", "media cost is known or not applicable", ("economics_ranking",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "economics.message_cost", RequirementOwner.FINANCE, "provide_message_cost", "message cost is known or not applicable", ("economics_ranking",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "economics.partner_cost", RequirementOwner.FINANCE, "provide_partner_cost", "partner cost is known or not applicable", ("economics_ranking",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "economics.staff_time_cost", RequirementOwner.FINANCE, "provide_staff_time_cost", "staff time cost is known or not applicable", ("economics_ranking",), allow_not_applicable=True),
    _requirement(ReadinessLevel.D4, "measurement.actual_spend_available", RequirementOwner.DATA, "configure_actual_spend_collection", "actual spend collection is available", ("net_contribution_measurement",), _actual_spend_collection),
)


def evaluate_readiness(snapshot: DecisionContextSnapshot) -> DecisionReadiness:
    failures: list[tuple[_Requirement, str]] = []
    passing_levels = {ReadinessLevel.D0}
    for level in (ReadinessLevel.D1, ReadinessLevel.D2, ReadinessLevel.D3, ReadinessLevel.D4):
        level_failures = []
        for requirement in _REQUIREMENTS:
            if requirement.level is not level:
                continue
            passed, reason = requirement.check(snapshot)
            if not passed:
                level_failures.append((requirement, reason))
        failures.extend(level_failures)
        if not level_failures and all(previous in passing_levels for previous in _levels_before(level)):
            passing_levels.add(level)

    level = max(passing_levels, key=lambda item: int(item.value[1]))
    available = tuple(
        capability
        for candidate in ReadinessLevel
        if int(candidate.value[1]) <= int(level.value[1])
        for capability in _CAPABILITIES[candidate]
    )
    blocked = tuple(
        capability
        for candidate in ReadinessLevel
        if int(candidate.value[1]) > int(level.value[1])
        for capability in _CAPABILITIES[candidate]
    )
    missing = tuple(
        MissingRequirement(
            field_path=requirement.field_path,
            reason_code=reason,
            owner=requirement.owner,
            collection_method=requirement.collection_method,
            completion_rule=requirement.completion_rule,
            unlocks=requirement.unlocks,
        )
        for requirement, reason in failures
    )
    return DecisionReadiness(
        level=level,
        available_capabilities=available,
        blocked_capabilities=blocked,
        missing_requirements=missing,
    )


def _levels_before(level: ReadinessLevel) -> tuple[ReadinessLevel, ...]:
    target = int(level.value[1])
    return tuple(candidate for candidate in ReadinessLevel if 0 < int(candidate.value[1]) < target)
