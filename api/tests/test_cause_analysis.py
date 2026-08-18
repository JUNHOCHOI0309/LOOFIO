import copy
import json
from pathlib import Path

from app.decisioning.causes import analyze_low_demand_slot
from app.decisioning.causes.models import (
    CAUSE_PRIORITY_VERSION,
    CandidateStatus,
    CauseCode,
    CauseRunStatus,
)
from app.decisioning.causes.scoring import score_cause
from app.decisioning.causes.taxonomy import CAUSE_TAXONOMY
from app.decisioning.context import DecisionContextSnapshot


FIXTURE = Path(__file__).parent / "fixtures" / "decisioning" / "low_demand" / "context_d4_v1.json"
OBSERVED_AT = "2026-08-17T10:00:00+09:00"


def _payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _field(value: object, reference: str) -> dict:
    return {
        "status": "known",
        "value": value,
        "source": {
            "type": "manual_verified",
            "reference": reference,
            "tenant_id": "TENANT_FIXTURE_01",
            "business_id": "BUSINESS_FIXTURE_01",
        },
        "observed_at": OBSERVED_AT,
    }


def _analyze(payload: dict):
    return analyze_low_demand_slot(DecisionContextSnapshot.model_validate(payload))


def _candidate(result, code: CauseCode):
    return next(candidate for candidate in result.candidates if candidate.cause_code is code)


def test_taxonomy_has_six_stable_low_demand_core_causes_and_unique_codes() -> None:
    core = [definition.code for definition in CAUSE_TAXONOMY if definition.core_for_low_demand_slot]

    assert len(CAUSE_TAXONOMY) == 10
    assert len({definition.code for definition in CAUSE_TAXONOMY}) == 10
    assert core == [
        CauseCode.DATA_QUALITY_ARTIFACT,
        CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT,
        CauseCode.OFFER_SLOT_MISMATCH,
        CauseCode.RETENTION_GAP,
        CauseCode.DISCOVERABILITY_GAP,
        CauseCode.DEMAND_DEFICIT,
    ]
    assert all(definition.hypothesis.endswith("가능성이 있습니다.") for definition in CAUSE_TAXONOMY)


def test_complete_context_returns_reviewable_hypotheses_with_source_links() -> None:
    result = _analyze(_payload())
    demand = _candidate(result, CauseCode.DEMAND_DEFICIT)
    retention = _candidate(result, CauseCode.RETENTION_GAP)

    assert result.status is CauseRunStatus.COMPLETED
    assert demand.status is CandidateStatus.REVIEWABLE
    assert demand.review_priority_score is not None
    assert demand.score_version == CAUSE_PRIORITY_VERSION
    assert demand.opportunity_evidence_refs == ("EVIDENCE_LOW_DEMAND_TUE_14_01",)
    assert "observation.demand_index" in demand.supporting_evidence_refs
    assert retention.status is CandidateStatus.REVIEWABLE
    assert all("원인은" not in candidate.hypothesis for candidate in result.candidates)
    assert all("아닙니다" in candidate.limitations[0] for candidate in result.candidates)


def test_required_unknown_produces_needs_data_but_optional_unknown_keeps_score() -> None:
    payload = _payload()
    payload["operation"]["slot_capacity_confirmed"] = {"status": "unknown"}
    result = _analyze(payload)
    capacity = _candidate(result, CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT)

    assert capacity.status is CandidateStatus.NEEDS_DATA
    assert capacity.review_priority_score is None
    assert capacity.missing_required_inputs[0].field_path == "operation.slot_capacity_confirmed"
    assert any(question.field_path == "operation.slot_capacity_confirmed" for question in result.recommended_diagnostics)

    payload = _payload()
    payload["operation"]["eligible_staff_count"] = {"status": "unknown"}
    result = _analyze(payload)
    capacity = _candidate(result, CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT)
    assert capacity.status is CandidateStatus.DEPRIORITIZED
    assert capacity.review_priority_score is not None
    assert any(issue.field_path == "operation.eligible_staff_count" for issue in capacity.missing_optional_inputs)


def test_capacity_false_is_a_reviewable_operational_hypothesis_and_not_a_demand_conclusion() -> None:
    payload = _payload()
    payload["operation"]["slot_capacity_confirmed"] = _field(False, "owner-capacity-closed-v1")
    result = _analyze(payload)
    capacity = _candidate(result, CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT)
    demand = _candidate(result, CauseCode.DEMAND_DEFICIT)

    assert capacity.status is CandidateStatus.REVIEWABLE
    assert "operation.slot_capacity_confirmed" in capacity.supporting_evidence_refs
    assert capacity.review_priority_score is not None
    assert any(blocker.reason_code == "NOT_CONFIRMED" for blocker in demand.downstream_blockers)


def test_critical_data_conflict_prioritizes_data_quality_and_blocks_business_causes() -> None:
    payload = _payload()
    payload["data_quality"]["validation_status"] = {
        "status": "conflicting",
        "conflicting_values": [
            {"value": "valid", "source": _field(True, "validation-source-a")["source"], "observed_at": OBSERVED_AT},
            {"value": "conflicting", "source": _field(True, "validation-source-b")["source"], "observed_at": OBSERVED_AT},
        ],
    }
    result = _analyze(payload)
    quality = _candidate(result, CauseCode.DATA_QUALITY_ARTIFACT)
    demand = _candidate(result, CauseCode.DEMAND_DEFICIT)

    assert result.status is CauseRunStatus.BLOCKED_BY_DATA_QUALITY
    assert quality.status is CandidateStatus.REVIEWABLE
    assert "data_quality.validation_status" in quality.supporting_evidence_refs
    assert demand.status is CandidateStatus.BLOCKED
    assert demand.review_priority_score is None


def test_stale_data_quality_context_requires_refresh_without_claiming_a_business_cause() -> None:
    payload = _payload()
    payload["data_quality"]["data_freshness_at"] = {
        "status": "stale",
        "value": OBSERVED_AT,
        "source": _field(True, "stale-import-freshness-v1")["source"],
        "observed_at": OBSERVED_AT,
    }
    result = _analyze(payload)
    quality = _candidate(result, CauseCode.DATA_QUALITY_ARTIFACT)

    assert result.status is CauseRunStatus.COMPLETED
    assert quality.status is CandidateStatus.NEEDS_DATA
    assert quality.review_priority_score is None
    assert quality.missing_required_inputs[0].reason_code == "STALE"


def test_conditional_candidates_only_activate_from_structured_signals() -> None:
    baseline = _analyze(_payload())
    assert len(baseline.candidates) == 6

    payload = _payload()
    payload["cause_signals"].update(
        {
            "booking_funnel_available": _field(True, "funnel-v1"),
            "channel_attribution_available": _field(True, "attribution-v1"),
            "value_price_signal_available": _field(True, "value-signal-v1"),
            "cancellation_evidence_available": _field(True, "cancellation-signal-v1"),
        }
    )
    result = _analyze(payload)

    assert {candidate.cause_code for candidate in result.candidates} == set(CauseCode)


def test_score_clamps_factors_and_result_is_deterministic_and_token_free() -> None:
    score = score_cause(
        evidence_support_ratio=2,
        pattern_consistency_ratio=-1,
        data_completeness_ratio=0.5,
        contradiction_absence_ratio=1,
        testability_ratio=1,
    )
    assert score.total == 70.0
    assert score.evidence_support == 35.0
    assert score.pattern_consistency == 0.0

    payload = _payload()
    first = _analyze(payload)
    second = _analyze(copy.deepcopy(payload))
    assert first == second
    serialized = first.model_dump_json()
    assert '"customer_token":' not in serialized
    assert "patient_name" not in serialized
