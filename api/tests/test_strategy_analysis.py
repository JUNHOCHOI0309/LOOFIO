import copy
import json
from pathlib import Path

from app.decisioning.causes import analyze_low_demand_slot
from app.decisioning.causes.models import CauseCode
from app.decisioning.context import DecisionContextSnapshot
from app.decisioning.strategies import analyze_low_demand_strategy
from app.decisioning.strategies.mapping import CAUSE_STRATEGY_MAPPINGS
from app.decisioning.strategies.models import (
    StrategyCandidateStatus,
    StrategyFamily,
    StrategyRunStatus,
)
from app.decisioning.strategies.scoring import score_strategy
from app.decisioning.strategies.taxonomy import STRATEGY_TAXONOMY


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
    snapshot = DecisionContextSnapshot.model_validate(payload)
    return analyze_low_demand_strategy(snapshot, analyze_low_demand_slot(snapshot))


def _candidate(result, family: StrategyFamily):
    return next(item for item in result.candidates if item.strategy_family is family)


def test_strategy_taxonomy_and_mapping_are_complete_and_stable() -> None:
    assert len(STRATEGY_TAXONOMY) == 10
    assert len({item.family for item in STRATEGY_TAXONOMY}) == 10
    assert [item.family for item in STRATEGY_TAXONOMY][:2] == [
        StrategyFamily.DATA_COLLECTION,
        StrategyFamily.CAPACITY_OPERATION,
    ]
    mapped = {item.cause_code for item in CAUSE_STRATEGY_MAPPINGS}
    assert mapped == {item.value for item in CauseCode}
    assert StrategyFamily.DATA_COLLECTION in {item.family for item in STRATEGY_TAXONOMY}
    assert StrategyFamily.NO_ACTION in {item.family for item in STRATEGY_TAXONOMY}


def test_strategy_result_is_deterministic_and_separates_scores_from_cause_scores() -> None:
    first = _analyze(_payload())
    second = _analyze(copy.deepcopy(_payload()))

    assert first == second
    assert first.status in {StrategyRunStatus.COMPLETED, StrategyRunStatus.MULTIPLE_VALID_OPTIONS}
    assert any(item.review_priority_score is not None for item in first.candidates if item.strategy_family is not StrategyFamily.DATA_COLLECTION)
    assert _candidate(first, StrategyFamily.DATA_COLLECTION).review_priority_score is None
    assert _candidate(first, StrategyFamily.NO_ACTION).review_priority_score is None
    assert "customer_token" not in first.model_dump_json()
    assert all("성공 확률" in item.limitations[0] for item in first.candidates)


def test_critical_data_quality_and_missing_capacity_select_structured_data_collection() -> None:
    payload = _payload()
    payload["data_quality"]["validation_status"] = {
        "status": "conflicting",
        "conflicting_values": [
            {"value": "valid", "source": _field(True, "quality-a")["source"], "observed_at": OBSERVED_AT},
            {"value": "conflicting", "source": _field(True, "quality-b")["source"], "observed_at": OBSERVED_AT},
        ],
    }
    result = _analyze(payload)

    assert result.status is StrategyRunStatus.NEEDS_DATA
    assert result.selected_strategy is StrategyFamily.DATA_COLLECTION
    assert result.data_collection_plan
    assert _candidate(result, StrategyFamily.RETENTION_REACTIVATION).review_priority_score is None

    payload = _payload()
    payload["operation"]["slot_capacity_confirmed"] = {"status": "unknown"}
    result = _analyze(payload)
    assert result.selected_strategy is StrategyFamily.DATA_COLLECTION
    assert any(item.field_path == "operation.slot_capacity_confirmed" for item in result.data_collection_plan)


def test_unavailable_capacity_uses_no_action_hold_and_score_weights_are_clamped() -> None:
    payload = _payload()
    payload["operation"]["slot_capacity_confirmed"] = _field(False, "capacity-closed")
    result = _analyze(payload)

    assert result.selected_strategy is StrategyFamily.NO_ACTION
    assert result.no_action_plan is not None
    assert _candidate(result, StrategyFamily.RETENTION_REACTIVATION).status is StrategyCandidateStatus.INFEASIBLE

    score = score_strategy(
        expected_net_value=2,
        evidence_fit=-1,
        operational_feasibility=1,
        measurement_feasibility=1,
        policy_safety=1,
        time_to_learning=1,
        learning_value=1,
    )
    assert score.total == 80.0
    assert score.expected_net_value == 25.0
    assert score.evidence_fit == 0.0
