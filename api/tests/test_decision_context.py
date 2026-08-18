import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.decisioning.context import DecisionContextSnapshot, HOSPITAL_POLICY_VERSION


FIXTURE_DIR = Path(__file__).parent / "fixtures" / "decisioning" / "low_demand"


def _load(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


def test_low_demand_snapshot_has_stable_hash_and_safe_hospital_defaults() -> None:
    payload = _load("context_d4_v1.json")
    first = DecisionContextSnapshot.model_validate(payload)
    second = DecisionContextSnapshot.model_validate(payload)

    assert first.context_hash == second.context_hash == first.calculate_hash()
    assert first.policy is not None
    assert first.policy.manual_approval_required is True
    assert first.policy.clinical_targeting_prohibited is True
    assert first.policy.policy_review_status.source.reference == HOSPITAL_POLICY_VERSION
    assert first.model_dump(mode="json")["economics"]["budget_cap"]["value"]["amount"] == "0.00"


def test_snapshot_rejects_hash_tampering_timezone_and_cross_tenant_provenance() -> None:
    payload = _load("context_d4_v1.json")
    payload["context_hash"] = "0" * 64
    with pytest.raises(ValidationError, match="context_hash"):
        DecisionContextSnapshot.model_validate(payload)

    payload = _load("context_d4_v1.json")
    payload["business_timezone"] = "Not/A_Timezone"
    with pytest.raises(ValidationError, match="IANA timezone"):
        DecisionContextSnapshot.model_validate(payload)

    payload = _load("context_d4_v1.json")
    payload["goal"]["primary_goal"]["source"]["tenant_id"] = "OTHER_TENANT"
    with pytest.raises(ValidationError, match="provenance tenant_id"):
        DecisionContextSnapshot.model_validate(payload)


def test_snapshot_scope_guard_does_not_allow_cross_tenant_or_business_access() -> None:
    snapshot = DecisionContextSnapshot.model_validate(_load("context_d4_v1.json"))

    snapshot.ensure_scope(tenant_id="TENANT_FIXTURE_01", business_id="BUSINESS_FIXTURE_01")
    with pytest.raises(PermissionError, match="outside"):
        snapshot.ensure_scope(tenant_id="OTHER_TENANT", business_id="BUSINESS_FIXTURE_01")
    with pytest.raises(PermissionError, match="outside"):
        snapshot.ensure_scope(tenant_id="TENANT_FIXTURE_01", business_id="OTHER_BUSINESS")


def test_snapshot_requires_offset_timestamps_and_valid_period_order() -> None:
    payload = _load("context_d4_v1.json")
    payload["snapshot_at"] = "2026-08-17T12:00:00"
    with pytest.raises(ValidationError, match="UTC offset"):
        DecisionContextSnapshot.model_validate(payload)

    payload = _load("context_d4_v1.json")
    payload["measurement"]["period_end"]["value"] = "2026-08-20T00:00:00+09:00"
    with pytest.raises(ValidationError, match="period_end"):
        DecisionContextSnapshot.model_validate(payload)


def test_golden_fixture_checksums_and_source_ids_are_stable() -> None:
    expected = {
        "context_d4_v1.json": "035f08dbd33fa29e1105ad3c899ba5aebe82ac21e96d9923e04489389e57e870",
        "opportunity_v1.json": "e73f067a02dd56e2d61d7613fc7510835e1e934f4dc5eec59868d26f93ef996b",
        "package_reference_v1.json": "f032f6ed07422ea0b86e7ba96aab1bf04338454951f905d859431ae8c0cfd8e9",
    }
    documents = {name: _load(name) for name in expected}

    assert documents["context_d4_v1.json"]["opportunity_id"] == documents["opportunity_v1.json"]["opportunity_id"]
    assert documents["context_d4_v1.json"]["opportunity_id"] == documents["package_reference_v1.json"]["opportunity_id"]
    assert documents["context_d4_v1.json"]["snapshot_id"] == documents["package_reference_v1.json"]["source_snapshot_id"]
    for name, checksum in expected.items():
        canonical = json.dumps(
            documents[name], ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        actual = hashlib.sha256(canonical).hexdigest()
        assert actual == checksum
