import copy
import json
from pathlib import Path

from app.decisioning.context import DecisionContextSnapshot
from app.decisioning.readiness import ReadinessLevel, evaluate_readiness


FIXTURE = Path(__file__).parent / "fixtures" / "decisioning" / "low_demand" / "context_d4_v1.json"


def _payload() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _readiness(payload: dict):
    return evaluate_readiness(DecisionContextSnapshot.model_validate(payload))


def test_d0_through_d4_boundaries_are_deterministic() -> None:
    d4_payload = _payload()
    assert _readiness(d4_payload).level is ReadinessLevel.D4

    d3_payload = copy.deepcopy(d4_payload)
    d3_payload["economics"]["economics_status"] = "partial"
    d3_payload["economics"]["variable_cost_per_completion"] = {"status": "unknown"}
    assert _readiness(d3_payload).level is ReadinessLevel.D3

    d2_payload = copy.deepcopy(d4_payload)
    d2_payload["customer_activation"]["marketing_consent_capability"] = {"status": "unknown"}
    d2_payload["channels"][0]["tracking_capability"] = "none"
    assert _readiness(d2_payload).level is ReadinessLevel.D2

    d1_payload = copy.deepcopy(d4_payload)
    d1_payload["operation"]["slot_capacity_confirmed"] = {"status": "unknown"}
    assert _readiness(d1_payload).level is ReadinessLevel.D1

    d0_payload = copy.deepcopy(d4_payload)
    d0_payload["goal"] = None
    assert _readiness(d0_payload).level is ReadinessLevel.D0

    assert _readiness(d4_payload) == _readiness(d4_payload)


def test_missing_requirement_plan_is_structured_and_stably_ordered() -> None:
    payload = _payload()
    payload["operation"]["slot_capacity_confirmed"] = {"status": "unknown"}
    payload["customer_activation"]["marketing_consent_capability"] = {"status": "restricted"}
    payload["channels"][0]["tracking_capability"] = "none"
    payload["economics"]["economics_status"] = "partial"
    payload["economics"]["variable_cost_per_completion"] = {"status": "unknown"}
    readiness = _readiness(payload)
    missing = {item.field_path: item for item in readiness.missing_requirements}

    assert readiness.level is ReadinessLevel.D1
    assert missing["operation.slot_capacity_confirmed"].reason_code == "UNKNOWN"
    assert missing["customer_activation.marketing_consent_capability"].reason_code == "RESTRICTED"
    assert missing["channels.tracking_capability"].reason_code == "TRACKING_NONE"
    assert missing["economics.variable_cost_per_completion"].owner.value == "finance"
    assert missing["economics.variable_cost_per_completion"].collection_method == "provide_variable_cost"
    assert missing["economics.variable_cost_per_completion"].unlocks == ("contribution_estimate",)


def test_zero_budget_is_known_while_unknown_budget_blocks_experiment_readiness() -> None:
    known_zero = _readiness(_payload())
    payload = _payload()
    payload["economics"]["economics_status"] = "partial"
    payload["economics"]["budget_cap"] = {"status": "unknown"}
    unknown = _readiness(payload)

    assert known_zero.level is ReadinessLevel.D4
    assert unknown.level is ReadinessLevel.D2
    assert "economics.budget_cap" in {item.field_path for item in unknown.missing_requirements}
