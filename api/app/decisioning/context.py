from __future__ import annotations

import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any, Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import Field, model_validator

from app.decisioning.fields import (
    ContractModel,
    DecisionField,
    DecisionFieldStatus,
    Money,
    Provenance,
    SourceType,
    require_aware,
)
from app.decisioning.privacy import assert_no_hospital_pii


CONTRACT_VERSION = "decision-input-v1"
HASH_VERSION = "decision-context-sha256-v1"
HOSPITAL_POLICY_VERSION = "hospital-policy-v1"


class PrimaryGoal(str, Enum):
    FILL_LOW_DEMAND_SLOTS = "FILL_LOW_DEMAND_SLOTS"
    REDUCE_CANCELLATION = "REDUCE_CANCELLATION"
    IMPROVE_REVISIT = "IMPROVE_REVISIT"
    INCREASE_COMPLETED_APPOINTMENTS = "INCREASE_COMPLETED_APPOINTMENTS"
    INCREASE_CONTRIBUTION = "INCREASE_CONTRIBUTION"
    IMPROVE_BOOKING_CONVERSION = "IMPROVE_BOOKING_CONVERSION"
    COLLECT_MISSING_DATA = "COLLECT_MISSING_DATA"


class OfferingEligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    NEEDS_POLICY_REVIEW = "needs_policy_review"
    NOT_AVAILABLE = "not_available"
    NOT_MARKETING_ENABLED = "not_marketing_enabled"
    INSUFFICIENT_DATA = "insufficient_data"


class ConsentCapability(str, Enum):
    VERIFIED_ALLOWED = "verified_allowed"
    VERIFIED_DENIED = "verified_denied"
    UNKNOWN = "unknown"
    NOT_REQUIRED_FOR_MANUAL_REVIEW = "not_required_for_manual_review"
    RESTRICTED = "restricted"


class ChannelType(str, Enum):
    MANUAL = "MANUAL"
    FRONT_DESK = "FRONT_DESK"
    STAFF_CALLBACK = "STAFF_CALLBACK"
    WAITLIST = "WAITLIST"
    BOOKING_PAGE = "BOOKING_PAGE"
    WEBSITE = "WEBSITE"
    TRACKED_PRINT = "TRACKED_PRINT"


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    AVAILABLE_MANUAL = "available_manual"
    NOT_CONNECTED = "not_connected"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


class ExecutionMode(str, Enum):
    MANUAL = "manual"
    COPY_EXPORT = "copy_export"
    APPROVED_CONNECTOR = "approved_connector"


class TrackingCapability(str, Enum):
    UTM = "UTM"
    UNIQUE_URL = "unique_url"
    BOOKING_SOURCE_CODE = "booking_source_code"
    COUPON_CODE = "coupon_code"
    PARTNER_CODE = "partner_code"
    QR = "QR"
    ACTION_ID = "action_id"
    MANUAL_SOURCE_TAG = "manual_source_tag"
    NONE = "none"


class PolicyReviewStatus(str, Enum):
    APPROVED = "approved"
    NEEDS_REVIEW = "needs_review"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class EconomicsStatus(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    INFEASIBLE = "infeasible"


class ResultSource(str, Enum):
    NORMALIZED_COMPLETED_APPOINTMENTS = "normalized_completed_appointments"
    PAYMENT_TRANSACTIONS = "payment_transactions"
    BOOKING_SOURCE_CODE = "booking_source_code"
    COUPON_REDEMPTION = "coupon_redemption"
    PARTNER_CODE = "partner_code"
    MANUAL_VERIFIED_RESULT = "manual_verified_result"
    CONNECTOR_DELIVERY_EVENT = "connector_delivery_event"


class ImportStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class DataValidationStatus(str, Enum):
    VALID = "valid"
    INVALID = "invalid"
    CONFLICTING = "conflicting"


class OpportunityContext(ContractModel):
    opportunity_type: Literal["LOW_DEMAND_SLOT"]
    detector_code: str = Field(min_length=1)
    detector_version: str = Field(min_length=1)
    evidence_refs: tuple[str, ...] = Field(min_length=1)
    limitations: tuple[str, ...] = ()


class LowDemandObservation(ContractModel):
    observed_weeks: int = Field(ge=0)
    average_appointments_per_week: float = Field(ge=0)
    comparison_median_per_week: float = Field(gt=0)
    demand_index: float = Field(ge=0)


class BusinessConstraintContext(ContractModel):
    # In the first slice this is the verified answer to whether the target slot is open.
    business_hours: DecisionField[bool] | None = None


class DataQualityContext(ContractModel):
    import_status: DecisionField[ImportStatus] | None = None
    validation_status: DecisionField[DataValidationStatus] | None = None
    source_lineage_available: DecisionField[bool] | None = None
    data_freshness_at: DecisionField[datetime] | None = None
    timezone_validation_status: DecisionField[DataValidationStatus] | None = None
    mapping_profile_version: DecisionField[str] | None = None
    valid_row_count: DecisionField[int] | None = None
    rejected_row_count: DecisionField[int] | None = None
    duplicate_row_count: DecisionField[int] | None = None
    unknown_status_count: DecisionField[int] | None = None
    missing_required_field_count: DecisionField[int] | None = None
    offering_resolution_rate: DecisionField[float] | None = None
    customer_token_coverage_rate: DecisionField[float] | None = None
    payment_coverage_rate: DecisionField[float] | None = None
    limitations: tuple[str, ...] = ()

    @model_validator(mode="after")
    def validate_ranges(self) -> DataQualityContext:
        nonnegative = (
            self.valid_row_count,
            self.rejected_row_count,
            self.duplicate_row_count,
            self.unknown_status_count,
            self.missing_required_field_count,
        )
        for field in nonnegative:
            if field is not None and field.value is not None and field.value < 0:
                raise ValueError("data quality count cannot be negative")
        rates = (
            self.offering_resolution_rate,
            self.customer_token_coverage_rate,
            self.payment_coverage_rate,
        )
        for field in rates:
            if field is not None and field.value is not None and not 0 <= field.value <= 1:
                raise ValueError("data quality rate must be between 0 and 1")
        if self.data_freshness_at and self.data_freshness_at.value:
            require_aware(self.data_freshness_at.value, "data_freshness_at")
        return self


class CauseSignalContext(ContractModel):
    booking_funnel_available: DecisionField[bool] | None = None
    channel_attribution_available: DecisionField[bool] | None = None
    value_price_signal_available: DecisionField[bool] | None = None
    cancellation_evidence_available: DecisionField[bool] | None = None
    broader_demand_proxy_available: DecisionField[bool] | None = None


class GoalContext(ContractModel):
    primary_goal: DecisionField[PrimaryGoal]
    no_discount_policy: bool = False
    manual_only: bool = True


class OperationalCapacityContext(ContractModel):
    target_weekday: Literal["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
    target_start_hour: int = Field(ge=0, le=23)
    target_end_hour: int = Field(ge=1, le=24)
    slot_capacity_confirmed: DecisionField[bool]
    offering_available: DecisionField[bool]
    target_population_count: DecisionField[int]
    available_staff_count: DecisionField[int] | None = None
    eligible_staff_count: DecisionField[int] | None = None
    room_available: DecisionField[bool] | None = None
    equipment_available: DecisionField[bool] | None = None

    @model_validator(mode="after")
    def validate_slot(self) -> OperationalCapacityContext:
        if self.target_end_hour <= self.target_start_hour:
            raise ValueError("target_end_hour must be after target_start_hour")
        if self.target_population_count.value is not None and self.target_population_count.value < 0:
            raise ValueError("target_population_count cannot be negative")
        return self


class OfferingEligibilityContext(ContractModel):
    offering_id: str = Field(min_length=1)
    offering_name: str = Field(min_length=1)
    eligibility: DecisionField[OfferingEligibilityStatus]
    target_slot_available: DecisionField[bool] | None = None
    target_slot_visible: DecisionField[bool] | None = None


class CustomerActivationContext(ContractModel):
    customer_token_available: DecisionField[bool]
    eligible_cohort_count: DecisionField[int]
    marketing_consent_capability: DecisionField[ConsentCapability]
    completed_visit_history_available: DecisionField[bool] | None = None
    revisit_interval_available: DecisionField[bool] | None = None

    @model_validator(mode="after")
    def validate_counts(self) -> CustomerActivationContext:
        if self.eligible_cohort_count.value is not None and self.eligible_cohort_count.value < 0:
            raise ValueError("eligible_cohort_count cannot be negative")
        return self


class ChannelCapabilityContext(ContractModel):
    channel_type: ChannelType
    connection_status: ConnectionStatus
    execution_mode: ExecutionMode
    tracking_capability: TrackingCapability
    owner: DecisionField[str]


class EconomicsContext(ContractModel):
    economics_status: EconomicsStatus = EconomicsStatus.UNKNOWN
    budget_cap: DecisionField[Money]
    expected_net_revenue_per_completion: DecisionField[Money]
    variable_cost_per_completion: DecisionField[Money]
    benefit_cost_per_completion: DecisionField[Money]
    incremental_service_cost_per_completion: DecisionField[Money]
    media_cost: DecisionField[Money]
    message_cost: DecisionField[Money]
    partner_cost: DecisionField[Money]
    staff_time_cost: DecisionField[Money]

    @model_validator(mode="after")
    def validate_complete_status(self) -> EconomicsContext:
        if self.economics_status is EconomicsStatus.COMPLETE:
            required = (self.expected_net_revenue_per_completion,)
            resolvable_costs = (
                self.variable_cost_per_completion,
                self.benefit_cost_per_completion,
                self.incremental_service_cost_per_completion,
                self.media_cost,
                self.message_cost,
                self.partner_cost,
                self.staff_time_cost,
            )
            if not all(field.status is DecisionFieldStatus.KNOWN for field in required):
                raise ValueError("complete economics requires known net revenue")
            if not all(
                field.status in {DecisionFieldStatus.KNOWN, DecisionFieldStatus.NOT_APPLICABLE}
                for field in resolvable_costs
            ):
                raise ValueError("complete economics requires every cost to be known or not_applicable")
        return self


class HospitalPolicyContext(ContractModel):
    domain: Literal["HOSPITAL"] = "HOSPITAL"
    policy_review_status: DecisionField[PolicyReviewStatus]
    manual_approval_required: Literal[True] = True
    clinical_targeting_prohibited: Literal[True] = True
    automatic_external_execution_prohibited: Literal[True] = True
    patient_pii_in_ai_context_prohibited: Literal[True] = True
    medical_outcome_guarantee_prohibited: Literal[True] = True
    unverified_before_after_claim_prohibited: Literal[True] = True

    @classmethod
    def safe_default(
        cls, *, snapshot_at: datetime, tenant_id: str, business_id: str
    ) -> HospitalPolicyContext:
        return cls(
            policy_review_status=DecisionField[PolicyReviewStatus](
                status=DecisionFieldStatus.KNOWN,
                value=PolicyReviewStatus.APPROVED,
                source=Provenance(
                    type=SourceType.POLICY_CONFIGURATION,
                    reference=HOSPITAL_POLICY_VERSION,
                    tenant_id=tenant_id,
                    business_id=business_id,
                ),
                observed_at=snapshot_at,
            )
        )


class MeasurementCapabilityContext(ContractModel):
    period_start: DecisionField[datetime]
    period_end: DecisionField[datetime]
    result_source: DecisionField[ResultSource]
    baseline_available: DecisionField[bool]
    action_level_tracking: DecisionField[bool]
    actual_spend_available: DecisionField[bool]

    @model_validator(mode="after")
    def validate_period(self) -> MeasurementCapabilityContext:
        for name in ("period_start", "period_end"):
            field = getattr(self, name)
            if field.value is not None:
                require_aware(field.value, name)
        if self.period_start.value and self.period_end.value:
            if self.period_end.value <= self.period_start.value:
                raise ValueError("period_end must be after period_start")
        return self


class DecisionContextSnapshot(ContractModel):
    contract_version: Literal["decision-input-v1"] = CONTRACT_VERSION
    hash_version: Literal["decision-context-sha256-v1"] = HASH_VERSION
    context_hash: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    tenant_id: str = Field(min_length=1)
    business_id: str = Field(min_length=1)
    location_id: str | None = Field(default=None, min_length=1)
    opportunity_id: str = Field(min_length=1)
    snapshot_id: str = Field(min_length=1)
    snapshot_at: datetime
    business_timezone: str = Field(min_length=1)
    data_window_start: datetime
    data_window_end: datetime
    opportunity: OpportunityContext
    observation: LowDemandObservation | None = None
    goal: GoalContext | None = None
    business_constraints: BusinessConstraintContext | None = None
    operation: OperationalCapacityContext | None = None
    offering: OfferingEligibilityContext | None = None
    customer_activation: CustomerActivationContext | None = None
    channels: tuple[ChannelCapabilityContext, ...] = ()
    economics: EconomicsContext | None = None
    policy: HospitalPolicyContext | None = None
    measurement: MeasurementCapabilityContext | None = None
    data_quality: DataQualityContext | None = None
    cause_signals: CauseSignalContext | None = None
    limitations: tuple[str, ...] = ()

    def __init__(self, **data: Any) -> None:
        assert_no_hospital_pii(data)
        super().__init__(**data)

    @classmethod
    def model_validate(cls, obj: Any, **kwargs: Any) -> DecisionContextSnapshot:
        # Reject before Pydantic creates an error containing the sensitive input value.
        assert_no_hospital_pii(obj)
        return super().model_validate(obj, **kwargs)

    @model_validator(mode="after")
    def validate_snapshot(self) -> DecisionContextSnapshot:
        for name in ("snapshot_at", "data_window_start", "data_window_end"):
            require_aware(getattr(self, name), name)
        if self.data_window_end < self.data_window_start:
            raise ValueError("data_window_end cannot precede data_window_start")
        try:
            ZoneInfo(self.business_timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError("business_timezone must be a valid IANA timezone") from exc

        if self.policy is None:
            object.__setattr__(
                self,
                "policy",
                HospitalPolicyContext.safe_default(
                    snapshot_at=self.snapshot_at,
                    tenant_id=self.tenant_id,
                    business_id=self.business_id,
                ),
            )
        self._validate_provenance_scope()

        expected_hash = self.calculate_hash()
        if self.context_hash is not None and self.context_hash != expected_hash:
            raise ValueError("context_hash does not match the canonical snapshot payload")
        object.__setattr__(self, "context_hash", expected_hash)
        return self

    def calculate_hash(self) -> str:
        payload = self.model_dump(mode="json", exclude={"context_hash"})
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def ensure_scope(self, *, tenant_id: str, business_id: str) -> None:
        if self.tenant_id != tenant_id or self.business_id != business_id:
            raise PermissionError("decision context is outside the active tenant/business scope")

    def _validate_provenance_scope(self) -> None:
        for field in _walk_decision_fields(self):
            sources = [field.source] if field.source else []
            sources.extend(item.source for item in field.conflicting_values)
            for source in sources:
                if source.tenant_id is not None and source.tenant_id != self.tenant_id:
                    raise ValueError("provenance tenant_id does not match snapshot tenant_id")
                if source.business_id is not None and source.business_id != self.business_id:
                    raise ValueError("provenance business_id does not match snapshot business_id")


def _walk_decision_fields(value: object) -> tuple[DecisionField[Any], ...]:
    found: list[DecisionField[Any]] = []
    if isinstance(value, DecisionField):
        return (value,)
    if isinstance(value, ContractModel):
        for field_name in type(value).model_fields:
            found.extend(_walk_decision_fields(getattr(value, field_name)))
    elif isinstance(value, (list, tuple)):
        for item in value:
            found.extend(_walk_decision_fields(item))
    return tuple(found)
