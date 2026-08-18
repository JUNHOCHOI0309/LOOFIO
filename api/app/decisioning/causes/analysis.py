from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from app.decisioning.causes.data_quality import DataQualityAssessment, resolve_data_quality
from app.decisioning.causes.models import (
    CAUSE_ANALYSIS_VERSION,
    CandidateStatus,
    CauseAnalysisResult,
    CauseCandidate,
    CauseCode,
    CauseDefinition,
    CauseInputIssue,
    CauseRunStatus,
    CauseStrategyHandoff,
    DiagnosticPriority,
    DiagnosticQuestion,
    DownstreamBlocker,
    EvidenceStrength,
    RequirementLevel,
)
from app.decisioning.causes.scoring import evidence_strength, score_cause
from app.decisioning.causes.taxonomy import CAUSE_TAXONOMY
from app.decisioning.context import (
    ConsentCapability,
    DecisionContextSnapshot,
    TrackingCapability,
)
from app.decisioning.fields import DecisionField, DecisionFieldStatus


_STATUS_ORDER = {
    CandidateStatus.REVIEWABLE: 0,
    CandidateStatus.NEEDS_DATA: 1,
    CandidateStatus.DEPRIORITIZED: 2,
    CandidateStatus.NOT_APPLICABLE: 3,
    CandidateStatus.BLOCKED: 4,
}


@dataclass(frozen=True)
class _CandidateEvaluation:
    definition: CauseDefinition
    status: CandidateStatus
    required_missing: tuple[CauseInputIssue, ...]
    optional_missing: tuple[CauseInputIssue, ...]
    blockers: tuple[DownstreamBlocker, ...]
    supporting_refs: tuple[str, ...]
    contradicting_refs: tuple[str, ...]
    score: Any | None
    strength: EvidenceStrength


def analyze_low_demand_slot(snapshot: DecisionContextSnapshot) -> CauseAnalysisResult:
    """Produce a pure, deterministic Cause Analysis without raw-data access or persistence."""
    if snapshot.opportunity.opportunity_type != "LOW_DEMAND_SLOT":
        raise ValueError("Cause Analysis v1 supports LOW_DEMAND_SLOT only")

    quality = resolve_data_quality(snapshot)
    definitions = tuple(definition for definition in CAUSE_TAXONOMY if _is_seeded(definition, snapshot))
    evaluations = tuple(_evaluate(definition, snapshot, quality) for definition in definitions)
    diagnostics = _diagnostics(evaluations)
    by_code = {
        evaluation.definition.code: tuple(
            question.id for question in diagnostics if question.cause_code is evaluation.definition.code
        )
        for evaluation in evaluations
    }
    candidates = tuple(
        _candidate_from(evaluation, snapshot, by_code[evaluation.definition.code])
        for evaluation in evaluations
    )
    candidates = tuple(
        sorted(
            candidates,
            key=lambda candidate: (
                _STATUS_ORDER[candidate.status],
                -(candidate.review_priority_score if candidate.review_priority_score is not None else -1),
                _definition_order(candidate.cause_code),
            ),
        )
    )
    run_status = _run_status(candidates, quality)
    global_limitations = (
        "Cause Candidate는 원인 확정, 인과관계 또는 성공 확률이 아닙니다.",
        *quality.limitations,
        *(f"Critical data quality condition: {reason}" for reason in quality.critical_reasons),
    )
    return CauseAnalysisResult(
        id=_analysis_id(snapshot),
        status=run_status,
        tenant_id=snapshot.tenant_id,
        business_id=snapshot.business_id,
        opportunity_id=snapshot.opportunity_id,
        decision_context_snapshot_id=snapshot.snapshot_id,
        decision_context_hash=snapshot.context_hash or snapshot.calculate_hash(),
        generated_at=snapshot.snapshot_at,
        candidates=candidates,
        recommended_diagnostics=diagnostics,
        global_limitations=global_limitations,
        next_stage=CauseStrategyHandoff(
            strategy_ready=run_status is CauseRunStatus.COMPLETED,
            blocked_reasons=quality.critical_reasons,
            candidate_codes=tuple(candidate.cause_code for candidate in candidates),
        ),
    )


def _is_seeded(definition: CauseDefinition, snapshot: DecisionContextSnapshot) -> bool:
    if definition.core_for_low_demand_slot:
        return True
    if definition.conditional_signal_path is None:
        return False
    return _available(snapshot, definition.conditional_signal_path)[0] and bool(
        _value(snapshot, definition.conditional_signal_path)
    )


def _evaluate(
    definition: CauseDefinition, snapshot: DecisionContextSnapshot, quality: DataQualityAssessment
) -> _CandidateEvaluation:
    required_missing: list[CauseInputIssue] = []
    optional_missing: list[CauseInputIssue] = []
    for requirement in definition.requirements:
        if requirement.level is RequirementLevel.BLOCKING:
            continue
        available, reason = _available(snapshot, requirement.field_path)
        if (
            definition.code is CauseCode.DATA_QUALITY_ARTIFACT
            and quality.is_critical
            and requirement.field_path
            in {"data_quality.validation_status", "data_quality.timezone_validation_status"}
            and reason == "CONFLICTING"
        ):
            available = True
        if available:
            continue
        issue = CauseInputIssue(
            field_path=requirement.field_path,
            level=requirement.level,
            reason_code=reason,
        )
        if requirement.level is RequirementLevel.REQUIRED:
            required_missing.append(issue)
        elif requirement.level is RequirementLevel.OPTIONAL:
            optional_missing.append(issue)

    supporting, contradicting = _map_evidence(definition.code, snapshot, quality)
    blockers = _downstream_blockers(definition, snapshot)
    required_complete = not required_missing
    if quality.is_critical and definition.code is not CauseCode.DATA_QUALITY_ARTIFACT:
        return _CandidateEvaluation(
            definition,
            CandidateStatus.BLOCKED,
            tuple(required_missing),
            tuple(optional_missing),
            blockers,
            supporting,
            contradicting,
            None,
            EvidenceStrength.INSUFFICIENT,
        )
    if not required_complete:
        return _CandidateEvaluation(
            definition,
            CandidateStatus.NEEDS_DATA,
            tuple(required_missing),
            tuple(optional_missing),
            blockers,
            supporting,
            contradicting,
            None,
            EvidenceStrength.INSUFFICIENT,
        )

    evidence_ratio = min(1.0, 0.25 + 0.25 * len(supporting)) if supporting else 0.1
    pattern_ratio = _pattern_consistency(definition.code, snapshot, supporting)
    completeness_ratio = (len(definition.requirements) - len(optional_missing) - sum(
        1 for item in definition.requirements if item.level is RequirementLevel.BLOCKING
    )) / max(1, len(definition.requirements) - sum(
        1 for item in definition.requirements if item.level is RequirementLevel.BLOCKING
    ))
    contradiction_absence_ratio = max(0.0, 1.0 - 0.5 * len(contradicting))
    testability_ratio = 0.8 if definition.code is not CauseCode.DATA_QUALITY_ARTIFACT else 0.9
    score = score_cause(
        evidence_support_ratio=evidence_ratio,
        pattern_consistency_ratio=pattern_ratio,
        data_completeness_ratio=completeness_ratio,
        contradiction_absence_ratio=contradiction_absence_ratio,
        testability_ratio=testability_ratio,
    )
    status = (
        CandidateStatus.DEPRIORITIZED
        if not supporting and contradicting
        else CandidateStatus.REVIEWABLE
    )
    return _CandidateEvaluation(
        definition,
        status,
        tuple(required_missing),
        tuple(optional_missing),
        blockers,
        supporting,
        contradicting,
        score,
        evidence_strength(
            evidence_support_ratio=evidence_ratio,
            data_completeness_ratio=completeness_ratio,
            required_complete=True,
        ),
    )


def _candidate_from(
    evaluation: _CandidateEvaluation, snapshot: DecisionContextSnapshot, question_ids: tuple[str, ...]
) -> CauseCandidate:
    return CauseCandidate(
        cause_code=evaluation.definition.code,
        status=evaluation.status,
        hypothesis=evaluation.definition.hypothesis,
        review_priority_score=evaluation.score.total if evaluation.score else None,
        score_breakdown=evaluation.score,
        evidence_strength=evaluation.strength,
        opportunity_evidence_refs=snapshot.opportunity.evidence_refs,
        supporting_evidence_refs=evaluation.supporting_refs,
        contradicting_evidence_refs=evaluation.contradicting_refs,
        required_inputs=tuple(
            requirement.field_path
            for requirement in evaluation.definition.requirements
            if requirement.level is RequirementLevel.REQUIRED
        ),
        missing_required_inputs=evaluation.required_missing,
        missing_optional_inputs=evaluation.optional_missing,
        downstream_blockers=evaluation.blockers,
        diagnostic_question_ids=question_ids,
        limitations=("Cause Candidate는 원인 확정 또는 성공 확률이 아닙니다.",),
    )


def _map_evidence(
    code: CauseCode, snapshot: DecisionContextSnapshot, quality: DataQualityAssessment
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    supporting: list[str] = []
    contradicting: list[str] = []

    def bool_evidence(path: str, *, true_supports: bool) -> None:
        available, _ = _available(snapshot, path)
        value = _value(snapshot, path)
        if not available or not isinstance(value, bool):
            return
        if value is true_supports:
            supporting.append(path)
        else:
            contradicting.append(path)

    if code is CauseCode.DATA_QUALITY_ARTIFACT:
        if quality.is_critical:
            supporting.extend(_quality_ref_for_reason(reason) for reason in quality.critical_reasons)
        else:
            bool_evidence("data_quality.source_lineage_available", true_supports=False)
            for path in ("data_quality.validation_status", "data_quality.timezone_validation_status"):
                if _available(snapshot, path)[0]:
                    contradicting.append(path)
    elif code is CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT:
        bool_evidence("business_constraints.business_hours", true_supports=False)
        bool_evidence("operation.slot_capacity_confirmed", true_supports=False)
        bool_evidence("operation.offering_available", true_supports=False)
        bool_evidence("operation.room_available", true_supports=False)
        bool_evidence("operation.equipment_available", true_supports=False)
        eligible = _value(snapshot, "operation.eligible_staff_count")
        if isinstance(eligible, int):
            (supporting if eligible == 0 else contradicting).append("operation.eligible_staff_count")
    elif code is CauseCode.OFFER_SLOT_MISMATCH:
        bool_evidence("offering.target_slot_available", true_supports=False)
    elif code is CauseCode.RETENTION_GAP:
        cohort = _value(snapshot, "customer_activation.eligible_cohort_count")
        if isinstance(cohort, int):
            (supporting if cohort > 0 else contradicting).append("customer_activation.eligible_cohort_count")
        bool_evidence("customer_activation.customer_token_available", true_supports=True)
    elif code is CauseCode.DISCOVERABILITY_GAP:
        bool_evidence("offering.target_slot_visible", true_supports=False)
    elif code is CauseCode.DEMAND_DEFICIT:
        observation = snapshot.observation
        if observation is not None:
            if observation.observed_weeks >= 8 and observation.demand_index <= 0.65:
                supporting.append("observation.demand_index")
            else:
                contradicting.append("observation.demand_index")
            signal = _value(snapshot, "cause_signals.broader_demand_proxy_available")
            if signal is True:
                supporting.append("cause_signals.broader_demand_proxy_available")
    return tuple(sorted(set(supporting))), tuple(sorted(set(contradicting)))


def _quality_ref_for_reason(reason: str) -> str:
    return {
        "CRITICAL_VALIDATION_CONFLICT": "data_quality.validation_status",
        "CRITICAL_VALIDATION_INVALID": "data_quality.validation_status",
        "CRITICAL_TIMEZONE_CONFLICT": "data_quality.timezone_validation_status",
        "CRITICAL_TIMEZONE_INVALID": "data_quality.timezone_validation_status",
        "OPPORTUNITY_EVIDENCE_UNREPRODUCIBLE": "opportunity.evidence_refs",
    }[reason]


def _downstream_blockers(
    definition: CauseDefinition, snapshot: DecisionContextSnapshot
) -> tuple[DownstreamBlocker, ...]:
    blockers: list[DownstreamBlocker] = []
    for requirement in definition.requirements:
        if requirement.level is not RequirementLevel.BLOCKING:
            continue
        available, reason = _available(snapshot, requirement.field_path)
        value = _value(snapshot, requirement.field_path)
        blocked = not available
        reason_code = reason
        if requirement.field_path in {
            "operation.slot_capacity_confirmed",
            "operation.offering_available",
            "offering.target_slot_available",
        }:
            blocked = value is not True
            reason_code = "NOT_CONFIRMED" if available else reason
        elif requirement.field_path == "customer_activation.marketing_consent_capability":
            blocked = value not in {
                ConsentCapability.VERIFIED_ALLOWED,
                ConsentCapability.NOT_REQUIRED_FOR_MANUAL_REVIEW,
            }
            reason_code = "CONSENT_NOT_AVAILABLE" if blocked else ""
        elif requirement.field_path == "channels.tracking_capability":
            blocked = not _tracked_channel(snapshot)
            reason_code = "TRACKING_UNAVAILABLE" if blocked else ""
        elif requirement.field_path == "channels.owner":
            blocked = not _channel_owner(snapshot)
            reason_code = "OWNER_UNAVAILABLE" if blocked else ""
        if blocked:
            blockers.append(
                DownstreamBlocker(
                    field_path=requirement.field_path,
                    reason_code=reason_code,
                    blocked_capability=_blocked_capability(definition.code),
                )
            )
    return tuple(blockers)


def _blocked_capability(code: CauseCode) -> str:
    return {
        CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT: "demand_expansion",
        CauseCode.OFFER_SLOT_MISMATCH: "target_slot_playbook",
        CauseCode.RETENTION_GAP: "customer_contact_execution",
        CauseCode.DISCOVERABILITY_GAP: "discoverability_execution",
        CauseCode.DEMAND_DEFICIT: "paid_acquisition_justification",
        CauseCode.VALUE_OR_PRICE_FRICTION: "benefit_or_discount_execution",
    }.get(code, "recommendation_package")


def _pattern_consistency(code: CauseCode, snapshot: DecisionContextSnapshot, supporting: tuple[str, ...]) -> float:
    if code is CauseCode.DEMAND_DEFICIT and snapshot.observation is not None:
        return min(1.0, snapshot.observation.observed_weeks / 12)
    return 0.7 if supporting else 0.4


def _diagnostics(evaluations: tuple[_CandidateEvaluation, ...]) -> tuple[DiagnosticQuestion, ...]:
    questions: list[DiagnosticQuestion] = []
    for evaluation in evaluations:
        for issue in (*evaluation.required_missing, *evaluation.optional_missing):
            questions.append(_question(evaluation.definition.code, issue.field_path, issue.level))
        for blocker in evaluation.blockers:
            questions.append(_question(evaluation.definition.code, blocker.field_path, RequirementLevel.BLOCKING))
    unique = {question.id: question for question in questions}
    return tuple(sorted(unique.values(), key=_question_sort_key))


def _question(code: CauseCode, field_path: str, level: RequirementLevel) -> DiagnosticQuestion:
    template = _QUESTION_TEMPLATES.get(field_path)
    if template is None:
        template = (
            f"{field_path} 정보를 확인할 수 있습니까?",
            "enum",
            ("known", "unknown"),
            "Cause Candidate를 안전하게 검토하기 위해 필요합니다.",
        )
    question, answer_type, allowed_answers, why_needed = template
    priority = (
        DiagnosticPriority.REQUIRED
        if level is RequirementLevel.REQUIRED
        else DiagnosticPriority.BLOCKING
        if level is RequirementLevel.BLOCKING
        else DiagnosticPriority.OPTIONAL
    )
    return DiagnosticQuestion(
        id=f"CQ_{code.value}_{field_path.replace('.', '_').upper()}",
        cause_code=code,
        field_path=field_path,
        question=question,
        answer_type=answer_type,
        priority=priority,
        why_needed=why_needed,
        allowed_answers=allowed_answers,
        readiness_effect={"known": "cause_evaluable", "unknown": "needs_data"},
    )


_QUESTION_TEMPLATES: dict[str, tuple[str, str, tuple[str | bool | int, ...], str]] = {
    "data_quality.validation_status": (
        "외부 상태값이 내부 예약 상태로 모두 확인됐습니까?",
        "boolean_with_unknown",
        (True, False, "unknown"),
        "데이터 품질 문제와 실제 수요 현상을 구분하기 위해 필요합니다.",
    ),
    "data_quality.timezone_validation_status": (
        "예약 시각의 timezone이 사업장 시간대와 일치합니까?",
        "boolean_with_unknown",
        (True, False, "unknown"),
        "시간대 오류로 슬롯 관측이 왜곡되지 않았는지 확인해야 합니다.",
    ),
    "business_constraints.business_hours": (
        "목표 시간대가 실제 영업시간 안에 있었습니까?",
        "boolean_with_unknown",
        (True, False, "unknown"),
        "수요 부족과 판매 불가 슬롯을 구분하기 위해 필요합니다.",
    ),
    "operation.slot_capacity_confirmed": (
        "목표 시간대에 실제 예약 가능한 여유가 있었습니까?",
        "boolean_with_unknown",
        (True, False, "unknown"),
        "수요 확대 전에 capacity를 확인해야 합니다.",
    ),
    "operation.offering_available": (
        "목표 시간대에 해당 Offering을 제공할 수 있었습니까?",
        "boolean_with_unknown",
        (True, False, "unknown"),
        "Offering 실행 가능 여부를 확인해야 합니다.",
    ),
    "customer_activation.marketing_consent_capability": (
        "비식별 고객군에 대한 연락 동의 capability를 확인할 수 있습니까?",
        "enum",
        ("verified_allowed", "verified_denied", "unknown", "restricted"),
        "고객 직접 접촉 실행을 안전하게 제한하기 위해 필요합니다.",
    ),
    "channels.tracking_capability": (
        "실행 결과를 Action ID나 예약 source로 연결할 수 있습니까?",
        "enum",
        ("action_id", "manual_source_tag", "none"),
        "실행 결과를 측정하기 위해 필요합니다.",
    ),
}


def _question_sort_key(question: DiagnosticQuestion) -> tuple[int, int, str]:
    group = {
        CauseCode.DATA_QUALITY_ARTIFACT: 0,
        CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT: 1,
        CauseCode.OFFER_SLOT_MISMATCH: 1,
        CauseCode.RETENTION_GAP: 2,
        CauseCode.DISCOVERABILITY_GAP: 3,
        CauseCode.DEMAND_DEFICIT: 4,
    }.get(question.cause_code, 5)
    return (group, _definition_order(question.cause_code), question.field_path)


def _run_status(candidates: tuple[CauseCandidate, ...], quality: DataQualityAssessment) -> CauseRunStatus:
    if quality.is_critical:
        return CauseRunStatus.BLOCKED_BY_DATA_QUALITY
    if any(candidate.status is CandidateStatus.REVIEWABLE for candidate in candidates):
        return CauseRunStatus.COMPLETED
    return CauseRunStatus.NEEDS_DATA


def _analysis_id(snapshot: DecisionContextSnapshot) -> str:
    value = "|".join(
        (
            snapshot.tenant_id,
            snapshot.business_id,
            snapshot.opportunity_id,
            snapshot.context_hash or snapshot.calculate_hash(),
            CAUSE_ANALYSIS_VERSION,
        )
    )
    return f"CAUSE_RUN_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:24]}"


def _definition_order(code: CauseCode) -> int:
    return next(definition.stable_order for definition in CAUSE_TAXONOMY if definition.code is code)


def _available(snapshot: DecisionContextSnapshot, path: str) -> tuple[bool, str]:
    value = _raw(snapshot, path)
    if value is None:
        return False, "MISSING"
    if isinstance(value, DecisionField):
        if value.status is DecisionFieldStatus.KNOWN:
            return True, ""
        return False, value.status.value.upper()
    if isinstance(value, tuple):
        return (bool(value), "MISSING")
    return True, ""


def _value(snapshot: DecisionContextSnapshot, path: str) -> object:
    value = _raw(snapshot, path)
    return value.value if isinstance(value, DecisionField) else value


def _raw(snapshot: DecisionContextSnapshot, path: str) -> object:
    if path == "channels":
        return snapshot.channels
    if path == "channels.tracking_capability":
        return tuple(channel.tracking_capability for channel in snapshot.channels)
    if path == "channels.owner":
        return tuple(channel.owner for channel in snapshot.channels)
    value: object = snapshot
    for part in path.split("."):
        value = getattr(value, part, None)
        if value is None:
            return None
    return value


def _tracked_channel(snapshot: DecisionContextSnapshot) -> bool:
    return any(channel.tracking_capability is not TrackingCapability.NONE for channel in snapshot.channels)


def _channel_owner(snapshot: DecisionContextSnapshot) -> bool:
    return any(owner.is_usable and bool(owner.value and owner.value.strip()) for owner in (channel.owner for channel in snapshot.channels))
