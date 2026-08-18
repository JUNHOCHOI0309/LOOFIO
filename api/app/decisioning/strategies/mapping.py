from app.decisioning.causes.models import CauseCode
from app.decisioning.strategies.models import StrategyCauseMapping, StrategyFamily, StrategyRelation


def _map(cause: CauseCode, family: StrategyFamily, relation: StrategyRelation) -> StrategyCauseMapping:
    return StrategyCauseMapping(cause_code=cause.value, strategy_family=family, relation=relation)


CAUSE_STRATEGY_MAPPINGS: tuple[StrategyCauseMapping, ...] = (
    _map(CauseCode.DATA_QUALITY_ARTIFACT, StrategyFamily.DATA_COLLECTION, StrategyRelation.PRIMARY),
    _map(CauseCode.DATA_QUALITY_ARTIFACT, StrategyFamily.NO_ACTION, StrategyRelation.SECONDARY),
    *(_map(CauseCode.DATA_QUALITY_ARTIFACT, family, StrategyRelation.INHIBITORY) for family in (
        StrategyFamily.CAPACITY_OPERATION, StrategyFamily.RETENTION_REACTIVATION, StrategyFamily.DISCOVERABILITY, StrategyFamily.CONVERSION, StrategyFamily.OFFER_PACKAGING, StrategyFamily.PARTNERSHIP_REFERRAL, StrategyFamily.ACQUISITION, StrategyFamily.CANCELLATION_RECOVERY)),
    _map(CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT, StrategyFamily.CAPACITY_OPERATION, StrategyRelation.PRIMARY),
    _map(CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT, StrategyFamily.DATA_COLLECTION, StrategyRelation.SECONDARY),
    _map(CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT, StrategyFamily.OFFER_PACKAGING, StrategyRelation.CONDITIONAL),
    *(_map(CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT, family, StrategyRelation.INHIBITORY) for family in (StrategyFamily.RETENTION_REACTIVATION, StrategyFamily.DISCOVERABILITY, StrategyFamily.ACQUISITION)),
    _map(CauseCode.OFFER_SLOT_MISMATCH, StrategyFamily.CAPACITY_OPERATION, StrategyRelation.PRIMARY),
    _map(CauseCode.OFFER_SLOT_MISMATCH, StrategyFamily.OFFER_PACKAGING, StrategyRelation.PRIMARY),
    _map(CauseCode.OFFER_SLOT_MISMATCH, StrategyFamily.DISCOVERABILITY, StrategyRelation.SECONDARY),
    _map(CauseCode.OFFER_SLOT_MISMATCH, StrategyFamily.RETENTION_REACTIVATION, StrategyRelation.CONDITIONAL),
    _map(CauseCode.OFFER_SLOT_MISMATCH, StrategyFamily.CONVERSION, StrategyRelation.CONDITIONAL),
    _map(CauseCode.RETENTION_GAP, StrategyFamily.RETENTION_REACTIVATION, StrategyRelation.PRIMARY),
    _map(CauseCode.RETENTION_GAP, StrategyFamily.OFFER_PACKAGING, StrategyRelation.SECONDARY),
    _map(CauseCode.RETENTION_GAP, StrategyFamily.PARTNERSHIP_REFERRAL, StrategyRelation.CONDITIONAL),
    _map(CauseCode.DISCOVERABILITY_GAP, StrategyFamily.DISCOVERABILITY, StrategyRelation.PRIMARY),
    _map(CauseCode.DISCOVERABILITY_GAP, StrategyFamily.CONVERSION, StrategyRelation.SECONDARY),
    _map(CauseCode.DISCOVERABILITY_GAP, StrategyFamily.ACQUISITION, StrategyRelation.CONDITIONAL),
    _map(CauseCode.DISCOVERABILITY_GAP, StrategyFamily.PARTNERSHIP_REFERRAL, StrategyRelation.CONDITIONAL),
    _map(CauseCode.DEMAND_DEFICIT, StrategyFamily.NO_ACTION, StrategyRelation.PRIMARY),
    _map(CauseCode.DEMAND_DEFICIT, StrategyFamily.CAPACITY_OPERATION, StrategyRelation.PRIMARY),
    _map(CauseCode.DEMAND_DEFICIT, StrategyFamily.OFFER_PACKAGING, StrategyRelation.SECONDARY),
    _map(CauseCode.DEMAND_DEFICIT, StrategyFamily.PARTNERSHIP_REFERRAL, StrategyRelation.CONDITIONAL),
    _map(CauseCode.DEMAND_DEFICIT, StrategyFamily.ACQUISITION, StrategyRelation.INHIBITORY),
    _map(CauseCode.CONVERSION_FRICTION, StrategyFamily.CONVERSION, StrategyRelation.PRIMARY),
    _map(CauseCode.CONVERSION_FRICTION, StrategyFamily.DISCOVERABILITY, StrategyRelation.SECONDARY),
    _map(CauseCode.CONVERSION_FRICTION, StrategyFamily.OFFER_PACKAGING, StrategyRelation.CONDITIONAL),
    _map(CauseCode.CONVERSION_FRICTION, StrategyFamily.ACQUISITION, StrategyRelation.INHIBITORY),
    _map(CauseCode.CHANNEL_MISMATCH, StrategyFamily.DISCOVERABILITY, StrategyRelation.PRIMARY),
    _map(CauseCode.CHANNEL_MISMATCH, StrategyFamily.ACQUISITION, StrategyRelation.SECONDARY),
    _map(CauseCode.CHANNEL_MISMATCH, StrategyFamily.PARTNERSHIP_REFERRAL, StrategyRelation.CONDITIONAL),
    _map(CauseCode.VALUE_OR_PRICE_FRICTION, StrategyFamily.OFFER_PACKAGING, StrategyRelation.PRIMARY),
    _map(CauseCode.VALUE_OR_PRICE_FRICTION, StrategyFamily.CONVERSION, StrategyRelation.SECONDARY),
    _map(CauseCode.VALUE_OR_PRICE_FRICTION, StrategyFamily.RETENTION_REACTIVATION, StrategyRelation.CONDITIONAL),
    _map(CauseCode.CANCELLATION_LEAKAGE, StrategyFamily.CANCELLATION_RECOVERY, StrategyRelation.PRIMARY),
    _map(CauseCode.CANCELLATION_LEAKAGE, StrategyFamily.CAPACITY_OPERATION, StrategyRelation.SECONDARY),
    _map(CauseCode.CANCELLATION_LEAKAGE, StrategyFamily.RETENTION_REACTIVATION, StrategyRelation.CONDITIONAL),
    _map(CauseCode.CANCELLATION_LEAKAGE, StrategyFamily.ACQUISITION, StrategyRelation.INHIBITORY),
)
