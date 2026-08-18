from app.decisioning.strategies.models import StrategyClass, StrategyDefinition, StrategyFamily


STRATEGY_TAXONOMY: tuple[StrategyDefinition, ...] = (
    StrategyDefinition(family=StrategyFamily.DATA_COLLECTION, strategy_class=StrategyClass.DIAGNOSTIC, stable_order=0, minimum_readiness="D0"),
    StrategyDefinition(family=StrategyFamily.CAPACITY_OPERATION, strategy_class=StrategyClass.OPERATIONAL, stable_order=1, minimum_readiness="D1"),
    StrategyDefinition(family=StrategyFamily.RETENTION_REACTIVATION, strategy_class=StrategyClass.EXECUTION, stable_order=2, minimum_readiness="D2"),
    StrategyDefinition(family=StrategyFamily.DISCOVERABILITY, strategy_class=StrategyClass.EXECUTION, stable_order=3, minimum_readiness="D2"),
    StrategyDefinition(family=StrategyFamily.CONVERSION, strategy_class=StrategyClass.EXECUTION, stable_order=4, minimum_readiness="D2"),
    StrategyDefinition(family=StrategyFamily.OFFER_PACKAGING, strategy_class=StrategyClass.EXECUTION, stable_order=5, minimum_readiness="D2"),
    StrategyDefinition(family=StrategyFamily.PARTNERSHIP_REFERRAL, strategy_class=StrategyClass.EXECUTION, stable_order=6, minimum_readiness="D3"),
    StrategyDefinition(family=StrategyFamily.ACQUISITION, strategy_class=StrategyClass.EXECUTION, stable_order=7, minimum_readiness="D3"),
    StrategyDefinition(family=StrategyFamily.CANCELLATION_RECOVERY, strategy_class=StrategyClass.EXECUTION, stable_order=8, minimum_readiness="D2"),
    StrategyDefinition(family=StrategyFamily.NO_ACTION, strategy_class=StrategyClass.HOLD, stable_order=9, minimum_readiness="D0"),
)

STRATEGY_BY_FAMILY = {definition.family: definition for definition in STRATEGY_TAXONOMY}
