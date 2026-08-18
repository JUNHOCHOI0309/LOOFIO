from __future__ import annotations

import re
from collections.abc import Mapping, Sequence


class HospitalPIIError(ValueError):
    def __init__(self, field_paths: Sequence[str]) -> None:
        self.field_paths = tuple(sorted(set(field_paths)))
        super().__init__(
            "Hospital decision context contains prohibited PII or clinical fields: "
            + ", ".join(self.field_paths)
        )


_FORBIDDEN_KEYS = {
    "patientname",
    "patientfullname",
    "rawphone",
    "phone",
    "phonenumber",
    "mobile",
    "mobilephone",
    "rawemail",
    "email",
    "emailaddress",
    "residentregistrationnumber",
    "residentnumber",
    "rrn",
    "ssn",
    "diagnosis",
    "diagnosisname",
    "disease",
    "symptom",
    "symptoms",
    "prescription",
    "testresult",
    "medicalrecord",
    "medicalrecordnumber",
    "consultationtext",
    "clinicalnote",
}


def _normalize_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_hospital_pii_fields(payload: object, path: tuple[str, ...] = ()) -> tuple[str, ...]:
    found: list[str] = []
    if isinstance(payload, Mapping):
        for raw_key, value in payload.items():
            key = str(raw_key)
            normalized = _normalize_key(key)
            current = (*path, key)
            parent_is_patient = any(_normalize_key(part) in {"patient", "patients"} for part in path)
            if normalized in _FORBIDDEN_KEYS or (parent_is_patient and normalized in {"name", "id"}):
                found.append(".".join(current))
                continue
            found.extend(find_hospital_pii_fields(value, current))
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            found.extend(find_hospital_pii_fields(value, (*path, str(index))))
    return tuple(sorted(set(found)))


def assert_no_hospital_pii(payload: object) -> None:
    fields = find_hospital_pii_fields(payload)
    if fields:
        raise HospitalPIIError(fields)
