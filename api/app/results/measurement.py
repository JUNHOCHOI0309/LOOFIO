from datetime import timedelta
from decimal import Decimal

from app.metrics.appointments import AppointmentMetricRow, calculate_appointment_metrics
from app.schemas.metrics import Money
from app.schemas.results import ActionMeasurement, MeasurementDelta, MeasurementMetrics


def calculate_action_measurement(*, action_id: str, result_id: str, observation_rows: list[AppointmentMetricRow], baseline_rows: list[list[AppointmentMetricRow]], start_at, end_at) -> ActionMeasurement:
    observed = _measurement_metrics(observation_rows)
    baselines = [_measurement_metrics(rows) for rows in baseline_rows]
    baseline = _average(baselines) if baselines else None
    change = _difference(observed, baseline) if baseline else None
    return ActionMeasurement(
        action_id=action_id, result_id=result_id,
        observation_window={"start_at": start_at, "end_at": end_at}, baseline_window_count=len(baselines),
        observed=observed, baseline_average=baseline, change_from_baseline=change,
        limitations=[
            "측정 기간의 저장된 예약 데이터를 집계한 관찰값입니다. Action이 변화를 일으켰다는 인과관계는 판단하지 않습니다.",
            "Baseline은 같은 길이의 직전 1~4주 창 평균입니다. 계절성, 날씨, 행사, 인력·수용량 변화는 보정하지 않습니다.",
            "actual_revenue는 completed 예약의 paid_amount 합계이며, 추정 매출이나 Incremental Revenue가 아닙니다.",
        ],
    )


def baseline_windows(start_at, end_at) -> list[tuple]:
    return [(start_at - timedelta(days=7 * week), end_at - timedelta(days=7 * week)) for week in range(1, 5)]


def _measurement_metrics(rows: list[AppointmentMetricRow]) -> MeasurementMetrics:
    metrics = calculate_appointment_metrics(rows)
    return MeasurementMetrics(appointment_count=metrics.appointment_count, completed_count=metrics.completed_count,
                              cancelled_count=metrics.cancelled_count, no_show_count=metrics.no_show_count,
                              actual_revenue=metrics.actual_revenue)


def _average(values: list[MeasurementMetrics]) -> MeasurementMetrics:
    count = Decimal(len(values))
    return MeasurementMetrics(
        appointment_count=round(sum(item.appointment_count for item in values) / len(values), 2),
        completed_count=round(sum(item.completed_count for item in values) / len(values), 2),
        cancelled_count=round(sum(item.cancelled_count for item in values) / len(values), 2),
        no_show_count=round(sum(item.no_show_count for item in values) / len(values), 2),
        actual_revenue=Money(amount=f"{(sum((Decimal(item.actual_revenue.amount) for item in values), Decimal('0')) / count).quantize(Decimal('0.01'))}"),
    )


def _difference(observed: MeasurementMetrics, baseline: MeasurementMetrics) -> MeasurementDelta:
    return MeasurementDelta(
        appointment_count=round(observed.appointment_count - baseline.appointment_count, 2),
        completed_count=round(observed.completed_count - baseline.completed_count, 2),
        cancelled_count=round(observed.cancelled_count - baseline.cancelled_count, 2),
        no_show_count=round(observed.no_show_count - baseline.no_show_count, 2),
        actual_revenue=Money(amount=f"{(Decimal(observed.actual_revenue.amount) - Decimal(baseline.actual_revenue.amount)).quantize(Decimal('0.01'))}"),
    )
