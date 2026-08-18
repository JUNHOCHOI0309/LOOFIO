from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Generic, Literal, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator


T = TypeVar("T")


class DecisionFieldStatus(str, Enum):
    KNOWN = "known"
    UNKNOWN = "unknown"
    NOT_APPLICABLE = "not_applicable"
    CONFLICTING = "conflicting"
    STALE = "stale"
    RESTRICTED = "restricted"


class SourceType(str, Enum):
    USER_ENTERED = "user_entered"
    MANUAL_VERIFIED = "manual_verified"
    IMPORTED_CSV = "imported_csv"
    DERIVED_METRIC = "derived_metric"
    SYSTEM_OBSERVED = "system_observed"
    EXTERNAL_API = "external_api"
    CONNECTOR = "connector"
    HISTORICAL_ACTION = "historical_action"
    POLICY_CONFIGURATION = "policy_configuration"


def require_aware(value: datetime | None, field_name: str) -> datetime | None:
    if value is not None and (value.tzinfo is None or value.utcoffset() is None):
        raise ValueError(f"{field_name} must include a UTC offset")
    return value


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Money(ContractModel):
    amount: Decimal = Field(ge=0, max_digits=20, decimal_places=2)
    currency: Literal["KRW"] = "KRW"

    @field_serializer("amount", when_used="json")
    def serialize_amount(self, value: Decimal) -> str:
        return format(value, ".2f")


class Provenance(ContractModel):
    type: SourceType
    reference: str = Field(min_length=1, max_length=255)
    tenant_id: str | None = Field(default=None, min_length=1)
    business_id: str | None = Field(default=None, min_length=1)

    @model_validator(mode="after")
    def validate_scope_shape(self) -> Provenance:
        if self.business_id is not None and self.tenant_id is None:
            raise ValueError("business-scoped provenance also requires tenant_id")
        return self


class SourcedValue(ContractModel, Generic[T]):
    value: T
    source: Provenance
    observed_at: datetime

    @model_validator(mode="after")
    def validate_timestamp(self) -> SourcedValue[T]:
        require_aware(self.observed_at, "observed_at")
        return self


class DecisionField(ContractModel, Generic[T]):
    status: DecisionFieldStatus
    value: T | None = None
    source: Provenance | None = None
    observed_at: datetime | None = None
    verified_at: datetime | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)
    notes: str | None = Field(default=None, max_length=1000)
    conflicting_values: tuple[SourcedValue[T], ...] = ()

    @model_validator(mode="after")
    def validate_state_contract(self) -> DecisionField[T]:
        require_aware(self.observed_at, "observed_at")
        require_aware(self.verified_at, "verified_at")
        if self.verified_at and self.observed_at and self.verified_at < self.observed_at:
            raise ValueError("verified_at cannot precede observed_at")

        if self.status in {DecisionFieldStatus.KNOWN, DecisionFieldStatus.STALE}:
            if self.value is None:
                raise ValueError(f"{self.status.value} fields require a value")
            if self.source is None:
                raise ValueError(f"{self.status.value} fields require provenance")
            if self.observed_at is None:
                raise ValueError(f"{self.status.value} fields require observed_at")
            if self.conflicting_values:
                raise ValueError(f"{self.status.value} fields cannot contain conflicting_values")
        elif self.status is DecisionFieldStatus.CONFLICTING:
            if self.value is not None:
                raise ValueError("conflicting fields cannot expose a selected value")
            if len(self.conflicting_values) < 2:
                raise ValueError("conflicting fields require at least two sourced values")
            values = {
                json.dumps(item.value, default=str, ensure_ascii=False, sort_keys=True)
                for item in self.conflicting_values
            }
            if len(values) < 2:
                raise ValueError("conflicting fields require at least two distinct values")
        else:
            if self.value is not None:
                raise ValueError(f"{self.status.value} fields cannot contain a value")
            if self.conflicting_values:
                raise ValueError(f"{self.status.value} fields cannot contain conflicting_values")
        return self

    @property
    def is_usable(self) -> bool:
        return self.status is DecisionFieldStatus.KNOWN

    def transition(self, **changes: object) -> DecisionField[T]:
        """Return a newly validated field state; DecisionField values remain immutable."""
        return self.model_copy(update=changes, deep=True).model_validate(
            {**self.model_dump(), **changes}
        )
