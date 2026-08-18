from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import timedelta

from app.decisioning.causes.models import CandidateStatus, CauseAnalysisResult, CauseRunStatus
from app.decisioning.context import ConsentCapability, EconomicsStatus, OfferingEligibilityStatus, PolicyReviewStatus
from app.decisioning.fields import DecisionField, DecisionFieldStatus
from app.decisioning.readiness import evaluate_readiness
from app.decisioning.strategies.mapping import CAUSE_STRATEGY_MAPPINGS
from app.decisioning.strategies.models import (
    AlternativeComparison, CollectionPlanItem, NoActionPlan, StrategyAnalysisResult, StrategyBlocker, StrategyCandidate,
    StrategyCandidateStatus, StrategyClass, StrategyFamily, StrategyInputIssue, StrategyPlaybookHandoff,
    StrategyRelation, StrategyRunStatus,
)
from app.decisioning.strategies.scoring import score_strategy
from app.decisioning.strategies.taxonomy import STRATEGY_BY_FAMILY, STRATEGY_TAXONOMY


_CORE = (StrategyFamily.CAPACITY_OPERATION, StrategyFamily.RETENTION_REACTIVATION, StrategyFamily.DISCOVERABILITY)
_EXECUTABLE = {StrategyClass.EXECUTION, StrategyClass.OPERATIONAL}
_PLAYBOOKS = {
    StrategyFamily.DATA_COLLECTION: ("PB_LOW_DEMAND_DATA_AUDIT_V1", "PB_LOW_DEMAND_TRACKING_SETUP_V1"),
    StrategyFamily.CAPACITY_OPERATION: ("PB_LOW_DEMAND_CAPACITY_REVIEW_V1", "PB_BOOKING_AVAILABILITY_AUDIT_V1"),
    StrategyFamily.RETENTION_REACTIVATION: ("PB_LOW_DEMAND_REVISIT_COHORT_V1", "PB_FRONT_DESK_REBOOKING_V1"),
    StrategyFamily.DISCOVERABILITY: ("PB_BOOKING_PATH_VISIBILITY_V1",),
    StrategyFamily.CONVERSION: ("PB_BOOKING_FUNNEL_FRICTION_V1",),
    StrategyFamily.OFFER_PACKAGING: ("PB_NON_DISCOUNT_VALUE_ADD_V1",),
    StrategyFamily.PARTNERSHIP_REFERRAL: ("PB_PARTNER_TRACKED_REFERRAL_V1",),
    StrategyFamily.ACQUISITION: ("PB_TRACKED_ACQUISITION_TEST_V1",),
    StrategyFamily.CANCELLATION_RECOVERY: ("PB_CANCELLATION_FLOW_REVIEW_V1",),
    StrategyFamily.NO_ACTION: ("PB_NO_ACTION_MONITORING_V1",),
}


def analyze_low_demand_strategy(snapshot, cause_analysis: CauseAnalysisResult) -> StrategyAnalysisResult:
    """Create deterministic Strategy candidates from a scoped Cause Analysis; never executes or persists."""
    snapshot.ensure_scope(tenant_id=cause_analysis.tenant_id, business_id=cause_analysis.business_id)
    if snapshot.opportunity_id != cause_analysis.opportunity_id or snapshot.opportunity.opportunity_type != "LOW_DEMAND_SLOT":
        raise ValueError("Strategy input does not match LOW_DEMAND_SLOT Cause Analysis")
    if cause_analysis.status is CauseRunStatus.INVALID_INPUT:
        raise ValueError("Cause Analysis is invalid")

    readiness = evaluate_readiness(snapshot)
    candidates = [_evaluate(family, snapshot, cause_analysis) for family in _seeded_families(cause_analysis)]
    selected, run_status = _select(candidates, cause_analysis)
    candidates = [candidate.model_copy(update={"selected": candidate.strategy_family is selected}) for candidate in candidates]
    candidates = sorted(candidates, key=_candidate_key)
    collection_plan = _collection_plan(candidates, snapshot) if selected is StrategyFamily.DATA_COLLECTION else ()
    no_action_plan = _no_action_plan(snapshot, candidates) if selected is StrategyFamily.NO_ACTION else None
    alternatives = _alternatives(candidates, selected)
    playbooks = tuple(sorted({item for candidate in candidates if candidate.strategy_family is selected or candidate.status in {StrategyCandidateStatus.ELIGIBLE, StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS} for item in candidate.playbook_candidates}))
    return StrategyAnalysisResult(
        id=_run_id(snapshot, cause_analysis), status=run_status, tenant_id=snapshot.tenant_id, business_id=snapshot.business_id,
        opportunity_id=snapshot.opportunity_id, cause_analysis_id=cause_analysis.id, decision_context_snapshot_id=snapshot.snapshot_id,
        decision_context_hash=snapshot.context_hash or snapshot.calculate_hash(), generated_at=cause_analysis.generated_at,
        candidates=tuple(candidates), selected_strategy=selected, alternative_comparisons=alternatives,
        data_collection_plan=collection_plan, no_action_plan=no_action_plan,
        next_stage=StrategyPlaybookHandoff(playbook_resolution_ready=selected not in {None, StrategyFamily.DATA_COLLECTION, StrategyFamily.NO_ACTION}, selected_strategy=selected, top_alternatives=tuple(candidate.strategy_family for candidate in candidates if candidate.status in {StrategyCandidateStatus.ELIGIBLE, StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS})[:2], blocked_reasons=tuple(sorted({blocker.code for candidate in candidates for blocker in candidate.blockers})), candidate_playbook_ids=playbooks),
        global_limitations=("Strategy Candidate는 성공 확률, ROI 또는 외부 실행 지시가 아닙니다.", *cause_analysis.global_limitations, *(f"Decision readiness: {readiness.level.value}",)),
    )


def _seeded_families(cause_analysis: CauseAnalysisResult) -> tuple[StrategyFamily, ...]:
    families = {StrategyFamily.DATA_COLLECTION, StrategyFamily.NO_ACTION, *_CORE}
    active = {candidate.cause_code.value for candidate in cause_analysis.candidates if candidate.status is not CandidateStatus.NOT_APPLICABLE}
    for mapping in CAUSE_STRATEGY_MAPPINGS:
        if mapping.cause_code in active and mapping.relation is not StrategyRelation.INHIBITORY:
            families.add(mapping.strategy_family)
    return tuple(sorted(families, key=lambda family: STRATEGY_BY_FAMILY[family].stable_order))


def _evaluate(family: StrategyFamily, snapshot, cause_analysis: CauseAnalysisResult) -> StrategyCandidate:
    definition = STRATEGY_BY_FAMILY[family]
    support, inhibitors = _cause_links(family, cause_analysis)
    missing, blockers = _gates(family, snapshot, cause_analysis, inhibitors)
    policy_status = _policy_status(snapshot)
    measurement_status = _measurement_status(snapshot)
    economics_status = snapshot.economics.economics_status.value if snapshot.economics else "unknown"
    if definition.strategy_class is StrategyClass.DIAGNOSTIC:
        status = StrategyCandidateStatus.ELIGIBLE
    elif definition.strategy_class is StrategyClass.HOLD:
        status = StrategyCandidateStatus.ELIGIBLE
    elif blockers:
        status = (
            StrategyCandidateStatus.NEEDS_POLICY_REVIEW
            if any(blocker.code == "POLICY_REVIEW_REQUIRED" for blocker in blockers)
            else StrategyCandidateStatus.INFEASIBLE
            if any(blocker.code.endswith("UNAVAILABLE") or blocker.code == "ECONOMICS_INFEASIBLE" for blocker in blockers)
            else StrategyCandidateStatus.DEPRIORITIZED
            if all(blocker.code == "INHIBITORY_CAUSE" for blocker in blockers)
            else StrategyCandidateStatus.NEEDS_DATA
        )
    elif missing:
        status = StrategyCandidateStatus.NEEDS_DATA
    elif not support:
        status = StrategyCandidateStatus.DEPRIORITIZED
    else:
        status = StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS if snapshot.economics and snapshot.economics.economics_status is EconomicsStatus.PARTIAL else StrategyCandidateStatus.ELIGIBLE
    score = None
    if definition.strategy_class in _EXECUTABLE and status in {StrategyCandidateStatus.ELIGIBLE, StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS}:
        score = score_strategy(expected_net_value=_economic_factor(snapshot, family), evidence_fit=_evidence_factor(support, cause_analysis), operational_feasibility=_operational_factor(snapshot), measurement_feasibility=_measurement_factor(snapshot), policy_safety=_policy_factor(snapshot), time_to_learning=1.0 if definition.strategy_class is StrategyClass.OPERATIONAL else 0.75, learning_value=0.75 if family in {StrategyFamily.CAPACITY_OPERATION, StrategyFamily.DISCOVERABILITY} else 0.5)
    return StrategyCandidate(strategy_family=family, strategy_class=definition.strategy_class, status=status, supporting_cause_refs=support, inhibitory_cause_refs=inhibitors, required_inputs=tuple(_requirements(family)), missing_inputs=tuple(missing), blockers=tuple(blockers), economics_status=economics_status, measurement_status=measurement_status, policy_status=policy_status, review_priority_score=score.total if score else None, score_breakdown=score, selection_reason=_selection_reason(family, status), exclusion_reasons=tuple(blocker.code for blocker in blockers), playbook_candidates=_PLAYBOOKS.get(family, ()), limitations=("Strategy Priority Score는 성공 확률이나 ROI가 아닙니다.",))


def _cause_links(family, cause_analysis):
    support, inhibitors = [], []
    for candidate in cause_analysis.candidates:
        if candidate.status not in {CandidateStatus.REVIEWABLE, CandidateStatus.DEPRIORITIZED, CandidateStatus.BLOCKED}:
            continue
        for mapping in CAUSE_STRATEGY_MAPPINGS:
            if mapping.cause_code != candidate.cause_code.value or mapping.strategy_family is not family:
                continue
            ref = f"{cause_analysis.id}:{candidate.cause_code.value}"
            if mapping.relation is StrategyRelation.INHIBITORY:
                if candidate.status in {CandidateStatus.REVIEWABLE, CandidateStatus.BLOCKED}:
                    inhibitors.append(ref)
            elif candidate.status is CandidateStatus.REVIEWABLE:
                support.append((ref, mapping.relation, candidate.review_priority_score or 0.0))
    return tuple(item[0] for item in support), tuple(inhibitors)


def _gates(family, snapshot, cause_analysis, inhibitors):
    if family in {StrategyFamily.DATA_COLLECTION, StrategyFamily.NO_ACTION}:
        return [], []
    missing, blockers = [], []
    if cause_analysis.status is CauseRunStatus.BLOCKED_BY_DATA_QUALITY:
        blockers.append(StrategyBlocker(code="CRITICAL_DATA_QUALITY", field_path="data_quality", reason="Critical data quality conflict blocks execution strategies."))
    if inhibitors:
        blockers.append(StrategyBlocker(code="INHIBITORY_CAUSE", field_path="cause_analysis", reason="A reviewable Cause inhibits this strategy."))
    for path in _requirements(family):
        value = _field(snapshot, path)
        if value is None or (isinstance(value, DecisionField) and value.status is not DecisionFieldStatus.KNOWN):
            missing.append(StrategyInputIssue(field_path=path, reason_code="MISSING" if value is None else value.status.value.upper()))
            continue
        raw = value.value if isinstance(value, DecisionField) else value
        if path in {"operation.slot_capacity_confirmed", "operation.offering_available", "offering.target_slot_available", "measurement.action_level_tracking", "measurement.baseline_available"} and raw is not True:
            blockers.append(StrategyBlocker(code="CAPACITY_UNAVAILABLE" if path.startswith(("operation", "offering")) else "MEASUREMENT_UNAVAILABLE", field_path=path, reason="Required capability is not confirmed."))
        if path == "customer_activation.eligible_cohort_count" and (not isinstance(raw, int) or raw <= 0):
            blockers.append(StrategyBlocker(code="COHORT_UNAVAILABLE", field_path=path, reason="No aggregate eligible cohort is available."))
    if family in {StrategyFamily.RETENTION_REACTIVATION, StrategyFamily.CANCELLATION_RECOVERY} and snapshot.customer_activation and snapshot.customer_activation.marketing_consent_capability.value not in {ConsentCapability.VERIFIED_ALLOWED, ConsentCapability.NOT_REQUIRED_FOR_MANUAL_REVIEW}:
        blockers.append(StrategyBlocker(code="CONSENT_UNAVAILABLE", field_path="customer_activation.marketing_consent_capability", reason="Consent capability is not available."))
    if family in {StrategyFamily.RETENTION_REACTIVATION, StrategyFamily.DISCOVERABILITY, StrategyFamily.CONVERSION, StrategyFamily.OFFER_PACKAGING, StrategyFamily.PARTNERSHIP_REFERRAL, StrategyFamily.ACQUISITION, StrategyFamily.CANCELLATION_RECOVERY} and _policy_factor(snapshot) is None:
        blockers.append(StrategyBlocker(code="POLICY_REVIEW_REQUIRED", field_path="policy.policy_review_status", reason="Policy review is required before execution."))
    if family in {StrategyFamily.PARTNERSHIP_REFERRAL, StrategyFamily.ACQUISITION} and _economic_factor(snapshot, family) is None:
        blockers.append(StrategyBlocker(code="ECONOMICS_INFEASIBLE", field_path="economics", reason="Cost-bearing strategy requires complete economics and budget."))
    return missing, blockers


def _requirements(family):
    common = ("operation.slot_capacity_confirmed", "operation.offering_available", "offering.target_slot_available", "measurement.result_source", "measurement.action_level_tracking", "channels.owner")
    return {
        StrategyFamily.CAPACITY_OPERATION: ("business_constraints.business_hours", "operation.slot_capacity_confirmed", "operation.offering_available"),
        StrategyFamily.RETENTION_REACTIVATION: common + ("customer_activation.eligible_cohort_count", "customer_activation.completed_visit_history_available", "customer_activation.revisit_interval_available", "customer_activation.marketing_consent_capability"),
        StrategyFamily.DISCOVERABILITY: common + ("offering.target_slot_visible", "policy.policy_review_status"),
        StrategyFamily.CONVERSION: common + ("cause_signals.booking_funnel_available",),
        StrategyFamily.OFFER_PACKAGING: common + ("offering.eligibility", "policy.policy_review_status"),
        StrategyFamily.PARTNERSHIP_REFERRAL: common + ("cause_signals.channel_attribution_available", "policy.policy_review_status", "economics.budget_cap"),
        StrategyFamily.ACQUISITION: common + ("cause_signals.broader_demand_proxy_available", "policy.policy_review_status", "economics.budget_cap"),
        StrategyFamily.CANCELLATION_RECOVERY: common + ("cause_signals.cancellation_evidence_available", "customer_activation.marketing_consent_capability"),
    }.get(family, ())


def _field(snapshot, path):
    if path == "channels.owner":
        return next((item.owner for item in snapshot.channels if item.owner.is_usable), None)
    value = snapshot
    for part in path.split("."):
        value = getattr(value, part, None)
        if value is None:
            return None
    return value


def _economic_factor(snapshot, family):
    economics = snapshot.economics
    if economics is None or economics.economics_status is EconomicsStatus.UNKNOWN:
        return None if family in {StrategyFamily.PARTNERSHIP_REFERRAL, StrategyFamily.ACQUISITION} else 0.5
    if family in {StrategyFamily.PARTNERSHIP_REFERRAL, StrategyFamily.ACQUISITION} and (
        not economics.budget_cap.value or economics.budget_cap.value.amount <= 0
    ):
        return None
    if economics.economics_status is EconomicsStatus.INFEASIBLE:
        return 0.0
    if economics.economics_status is EconomicsStatus.PARTIAL:
        return 0.5
    if not economics.expected_net_revenue_per_completion.value:
        return 0.5
    costs = (economics.variable_cost_per_completion, economics.benefit_cost_per_completion, economics.incremental_service_cost_per_completion, economics.staff_time_cost)
    known_cost = sum((field.value.amount for field in costs if field.value), start=0)
    return 1.0 if economics.expected_net_revenue_per_completion.value.amount > known_cost else 0.0


def _evidence_factor(support, cause_analysis):
    scores = []
    for ref in support:
        code = ref.rsplit(":", 1)[-1]
        candidate = next(item for item in cause_analysis.candidates if item.cause_code.value == code)
        scores.append((candidate.review_priority_score or 0) / 100)
    return min(1.0, (max(scores) if scores else 0.0) + min(0.1, max(0, len(scores) - 1) * 0.05))


def _operational_factor(snapshot):
    values = [_field(snapshot, path) for path in ("operation.slot_capacity_confirmed", "operation.offering_available")]
    if all(isinstance(value, DecisionField) and value.value is True for value in values):
        return 1.0
    return 0.5


def _measurement_factor(snapshot):
    measurement = snapshot.measurement
    if not measurement or not measurement.result_source.is_usable:
        return None
    return 0.75 if measurement.action_level_tracking.value is True else 0.5


def _policy_factor(snapshot):
    policy = snapshot.policy
    if not policy or not policy.policy_review_status.is_usable:
        return None
    value = policy.policy_review_status.value
    if value is PolicyReviewStatus.APPROVED:
        return 0.8 if snapshot.goal and snapshot.goal.manual_only else 1.0
    if value is PolicyReviewStatus.NEEDS_REVIEW:
        return None
    return 0.0


def _policy_status(snapshot):
    factor = _policy_factor(snapshot)
    return "needs_review" if factor is None else "approved" if factor > 0 else "blocked"


def _measurement_status(snapshot):
    factor = _measurement_factor(snapshot)
    return "unavailable" if factor is None else "grade_c_possible" if factor >= 0.75 else "grade_d_possible"


def _select(candidates, cause_analysis):
    if cause_analysis.status is CauseRunStatus.BLOCKED_BY_DATA_QUALITY:
        return StrategyFamily.DATA_COLLECTION, StrategyRunStatus.NEEDS_DATA
    eligible = [candidate for candidate in candidates if candidate.strategy_class in _EXECUTABLE and candidate.status in {StrategyCandidateStatus.ELIGIBLE, StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS}]
    eligible.sort(key=lambda item: (-(item.review_priority_score or 0), STRATEGY_BY_FAMILY[item.strategy_family].stable_order))
    if eligible and (eligible[0].review_priority_score or 0) >= 65:
        if len(eligible) > 1 and (eligible[0].review_priority_score or 0) - (eligible[1].review_priority_score or 0) < 5:
            return None, StrategyRunStatus.MULTIPLE_VALID_OPTIONS
        return eligible[0].strategy_family, StrategyRunStatus.COMPLETED
    if any(candidate.status is StrategyCandidateStatus.NEEDS_DATA for candidate in candidates):
        return StrategyFamily.DATA_COLLECTION, StrategyRunStatus.NEEDS_DATA
    if any(candidate.status is StrategyCandidateStatus.NEEDS_POLICY_REVIEW for candidate in candidates):
        return None, StrategyRunStatus.NEEDS_POLICY_REVIEW
    if not eligible:
        return StrategyFamily.NO_ACTION, StrategyRunStatus.NO_EXECUTABLE_STRATEGY
    return StrategyFamily.NO_ACTION, StrategyRunStatus.COMPLETED


def _collection_plan(candidates, snapshot):
    paths = sorted({item.field_path for candidate in candidates for item in candidate.missing_inputs} | {blocker.field_path for candidate in candidates for blocker in candidate.blockers if blocker.field_path not in {"cause_analysis", "data_quality"}})
    deadline = (snapshot.snapshot_at + timedelta(days=7)).date()
    return tuple(CollectionPlanItem(field_path=path, why_needed="Strategy 후보의 Hard Gate를 확인하기 위해 필요합니다.", owner="policy" if "policy" in path or "consent" in path else "operations" if path.startswith(("operation", "offering", "business_constraints")) else "data", collection_method="manual_confirmation", deadline=deadline, verification_rule="known value with provenance", unblocks=tuple(candidate.strategy_family for candidate in candidates if path in candidate.required_inputs)) for path in paths)


def _no_action_plan(snapshot, candidates):
    return NoActionPlan(reason_codes=("INSUFFICIENT_EVIDENCE",), monitoring_metric="demand_index", monitoring_segment="target weekday and slot", review_at=(snapshot.snapshot_at + timedelta(days=28)).date(), reopen_triggers=("Demand Index가 연속 4주 기준 이하", "capacity가 다시 확보됨", "추적 수단 설정 완료"), current_limitations=tuple(item.limitations[0] for item in candidates))


def _alternatives(candidates, selected):
    eligible = [item for item in candidates if item.strategy_class in _EXECUTABLE and item.status in {StrategyCandidateStatus.ELIGIBLE, StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS}]
    eligible.sort(key=_candidate_key)
    if len(eligible) < 2:
        return ()
    first, second = eligible[:2]
    preferred = first.strategy_family if selected is first.strategy_family else None
    return (AlternativeComparison(strategy_a=first.strategy_family, strategy_b=second.strategy_family, preferred=preferred, reason="Cause evidence, feasibility, measurement and policy inputs을 분리해 비교했습니다."),)


def _candidate_key(candidate):
    rank = {StrategyCandidateStatus.ELIGIBLE: 0, StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS: 1, StrategyCandidateStatus.NEEDS_DATA: 2, StrategyCandidateStatus.NEEDS_POLICY_REVIEW: 3, StrategyCandidateStatus.DEPRIORITIZED: 4, StrategyCandidateStatus.INFEASIBLE: 5}
    return (rank[candidate.status], -(candidate.review_priority_score or -1), STRATEGY_BY_FAMILY[candidate.strategy_family].stable_order)


def _selection_reason(family, status):
    if status in {StrategyCandidateStatus.ELIGIBLE, StrategyCandidateStatus.ELIGIBLE_WITH_LIMITATIONS}:
        return f"{family.value} 전략을 현재 Cause와 Decision Context에 연결해 검토합니다."
    return "필수 Gate 또는 입력이 충족되기 전에는 실행 전략으로 선택하지 않습니다."


def _run_id(snapshot, cause_analysis):
    value = "|".join((snapshot.tenant_id, snapshot.business_id, snapshot.opportunity_id, cause_analysis.id, snapshot.context_hash or snapshot.calculate_hash(), "strategy-engine-v1"))
    return "STRATEGY_RUN_" + hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]
