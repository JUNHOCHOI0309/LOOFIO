import json
from pathlib import Path

import pytest
from app.decisioning.context import DecisionContextSnapshot
from app.decisioning.privacy import HospitalPIIError, assert_no_hospital_pii, find_hospital_pii_fields


FIXTURE = Path(__file__).parent / "fixtures" / "decisioning" / "low_demand" / "context_d4_v1.json"


@pytest.mark.parametrize(
    "field_name,sensitive_value",
    [
        ("patient_name", "홍길동"),
        ("phone_number", "010-1234-5678"),
        ("email", "patient@example.com"),
        ("resident_registration_number", "900101-1234567"),
        ("diagnosis", "민감 진단"),
        ("medical_record", "민감 의무기록"),
        ("consultation_text", "민감 상담 원문"),
    ],
)
def test_hospital_pii_negative_corpus_is_rejected(field_name: str, sensitive_value: str) -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["customer_activation"][field_name] = sensitive_value

    with pytest.raises(HospitalPIIError) as exc_info:
        DecisionContextSnapshot.model_validate(payload)

    message = str(exc_info.value)
    assert field_name in message
    assert sensitive_value not in message


def test_nested_patient_name_is_rejected_but_business_and_offering_names_are_allowed() -> None:
    assert find_hospital_pii_fields({"business_name": "견본 병원", "offering_name": "견본 진료"}) == ()
    with pytest.raises(HospitalPIIError, match="patient.name"):
        assert_no_hospital_pii({"patient": {"name": "민감 이름"}})
