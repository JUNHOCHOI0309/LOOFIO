from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from app.decisioning.fields import (
    DecisionField,
    DecisionFieldStatus,
    Money,
    Provenance,
    SourceType,
    SourcedValue,
)


OBSERVED_AT = datetime.fromisoformat("2026-08-17T12:00:00+09:00")
SOURCE = Provenance(type=SourceType.USER_ENTERED, reference="decision-context-form-v1")


def test_unknown_and_known_zero_are_distinct() -> None:
    unknown = DecisionField[int](status=DecisionFieldStatus.UNKNOWN)
    zero = DecisionField[int](
        status=DecisionFieldStatus.KNOWN,
        value=0,
        source=SOURCE,
        observed_at=OBSERVED_AT,
    )

    assert unknown.value is None
    assert not unknown.is_usable
    assert zero.value == 0
    assert zero.is_usable
    assert unknown.model_dump() != zero.model_dump()


def test_known_field_requires_provenance_and_offset_timestamp() -> None:
    with pytest.raises(ValidationError, match="require provenance"):
        DecisionField[int](status="known", value=1, observed_at=OBSERVED_AT)
    with pytest.raises(ValidationError, match="UTC offset"):
        DecisionField[int](
            status="known",
            value=1,
            source=SOURCE,
            observed_at=datetime(2026, 8, 17, 12),
        )


def test_field_transition_revalidates_new_immutable_state() -> None:
    unknown = DecisionField[int](status="unknown")
    known = unknown.transition(
        status=DecisionFieldStatus.KNOWN,
        value=4,
        source=SOURCE,
        observed_at=OBSERVED_AT,
    )
    stale = known.transition(status=DecisionFieldStatus.STALE)

    assert unknown.status is DecisionFieldStatus.UNKNOWN
    assert known.status is DecisionFieldStatus.KNOWN
    assert stale.status is DecisionFieldStatus.STALE
    assert stale.value == 4


def test_conflicting_field_requires_distinct_sourced_values() -> None:
    values = (
        SourcedValue(value=True, source=SOURCE, observed_at=OBSERVED_AT),
        SourcedValue(
            value=False,
            source=Provenance(type="manual_verified", reference="owner-confirmation-v1"),
            observed_at=OBSERVED_AT,
        ),
    )
    conflict = DecisionField[bool](status="conflicting", conflicting_values=values)

    assert conflict.value is None
    assert len(conflict.conflicting_values) == 2
    with pytest.raises(ValidationError, match="distinct values"):
        DecisionField[bool](status="conflicting", conflicting_values=(values[0], values[0]))


def test_money_uses_decimal_and_rejects_negative_or_excess_precision() -> None:
    money = Money(amount="0.00")

    assert money.amount == Decimal("0.00")
    assert money.model_dump_json() == '{"amount":"0.00","currency":"KRW"}'
    with pytest.raises(ValidationError):
        Money(amount="-0.01")
    with pytest.raises(ValidationError):
        Money(amount="1.234")
