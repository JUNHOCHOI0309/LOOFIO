from __future__ import annotations

from app.decisioning.causes.models import CausePriorityBreakdown, EvidenceStrength


def score_cause(
    *,
    evidence_support_ratio: float,
    pattern_consistency_ratio: float,
    data_completeness_ratio: float,
    contradiction_absence_ratio: float,
    testability_ratio: float,
) -> CausePriorityBreakdown:
    evidence_support = round(_clamp(evidence_support_ratio) * 35, 2)
    pattern_consistency = round(_clamp(pattern_consistency_ratio) * 20, 2)
    data_completeness = round(_clamp(data_completeness_ratio) * 20, 2)
    contradiction_absence = round(_clamp(contradiction_absence_ratio) * 15, 2)
    testability = round(_clamp(testability_ratio) * 10, 2)
    total = round(
        evidence_support + pattern_consistency + data_completeness + contradiction_absence + testability,
        2,
    )
    return CausePriorityBreakdown(
        evidence_support=evidence_support,
        pattern_consistency=pattern_consistency,
        data_completeness=data_completeness,
        contradiction_absence=contradiction_absence,
        testability=testability,
        total=total,
    )


def evidence_strength(
    *, evidence_support_ratio: float, data_completeness_ratio: float, required_complete: bool
) -> EvidenceStrength:
    if not required_complete:
        return EvidenceStrength.INSUFFICIENT
    if evidence_support_ratio >= 0.75 and data_completeness_ratio >= 0.75:
        return EvidenceStrength.STRONG
    if evidence_support_ratio >= 0.5:
        return EvidenceStrength.MODERATE
    return EvidenceStrength.WEAK


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))
