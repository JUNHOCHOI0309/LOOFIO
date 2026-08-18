from __future__ import annotations

from app.decisioning.context import DataValidationStatus, DecisionContextSnapshot
from app.decisioning.fields import DecisionField, DecisionFieldStatus


class DataQualityAssessment:
    def __init__(self, critical_reasons: tuple[str, ...], limitations: tuple[str, ...]) -> None:
        self.critical_reasons = critical_reasons
        self.limitations = limitations

    @property
    def is_critical(self) -> bool:
        return bool(self.critical_reasons)


def resolve_data_quality(snapshot: DecisionContextSnapshot) -> DataQualityAssessment:
    context = snapshot.data_quality
    if context is None:
        return DataQualityAssessment((), ("DataQualityContext가 아직 제공되지 않았습니다.",))

    critical: list[str] = []
    if _is_conflict(context.validation_status):
        critical.append("CRITICAL_VALIDATION_CONFLICT")
    if _is_conflict(context.timezone_validation_status):
        critical.append("CRITICAL_TIMEZONE_CONFLICT")
    if context.validation_status and context.validation_status.value is DataValidationStatus.INVALID:
        critical.append("CRITICAL_VALIDATION_INVALID")
    if context.timezone_validation_status and context.timezone_validation_status.value is DataValidationStatus.INVALID:
        critical.append("CRITICAL_TIMEZONE_INVALID")
    if not snapshot.opportunity.evidence_refs:
        critical.append("OPPORTUNITY_EVIDENCE_UNREPRODUCIBLE")
    return DataQualityAssessment(tuple(critical), context.limitations)


def _is_conflict(field: DecisionField[DataValidationStatus] | None) -> bool:
    if field is None:
        return False
    return field.status is DecisionFieldStatus.CONFLICTING or field.value is DataValidationStatus.CONFLICTING
