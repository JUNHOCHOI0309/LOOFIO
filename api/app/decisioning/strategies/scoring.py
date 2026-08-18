from app.decisioning.strategies.models import StrategyPriorityBreakdown


def score_strategy(*, expected_net_value: float, evidence_fit: float, operational_feasibility: float, measurement_feasibility: float, policy_safety: float, time_to_learning: float, learning_value: float) -> StrategyPriorityBreakdown:
    factors = [expected_net_value, evidence_fit, operational_feasibility, measurement_feasibility, policy_safety, time_to_learning, learning_value]
    values = [max(0.0, min(1.0, value)) for value in factors]
    parts = (25 * values[0], 20 * values[1], 15 * values[2], 15 * values[3], 10 * values[4], 10 * values[5], 5 * values[6])
    return StrategyPriorityBreakdown(
        expected_net_value=round(parts[0], 2), evidence_fit=round(parts[1], 2), operational_feasibility=round(parts[2], 2), measurement_feasibility=round(parts[3], 2), policy_safety=round(parts[4], 2), time_to_learning=round(parts[5], 2), learning_value=round(parts[6], 2), total=round(sum(parts), 2)
    )
