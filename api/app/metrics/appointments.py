from collections import defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal

from app.schemas.metrics import AppointmentMetrics, DailyAppointmentMetric, Money, TimeSlotAppointmentMetric

METRIC_VERSION = "appointment-observation-v1"
WEEKDAY_NAMES = ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY")


@dataclass(frozen=True)
class AppointmentMetricRow:
    visit_start_at: datetime
    status: str
    paid_amount: Decimal | None
    offering_name: str | None = None


def calculate_appointment_metrics(rows: list[AppointmentMetricRow]) -> AppointmentMetrics:
    daily: dict[date, _Counts] = defaultdict(_Counts)
    time_slots: dict[tuple[int, int], _Counts] = defaultdict(_Counts)
    totals = _Counts()
    observed_weeks: set[tuple[int, int]] = set()

    for row in rows:
        totals.add(row)
        daily[row.visit_start_at.date()].add(row)
        time_slots[(row.visit_start_at.weekday(), row.visit_start_at.hour // 2 * 2)].add(row)
        iso_year, iso_week, _ = row.visit_start_at.isocalendar()
        observed_weeks.add((iso_year, iso_week))

    sorted_days = [
        DailyAppointmentMetric(
            date=day,
            appointment_count=counts.appointment_count,
            completed_count=counts.completed_count,
            cancelled_count=counts.cancelled_count,
            no_show_count=counts.no_show_count,
            actual_revenue=_money(counts.actual_revenue),
        )
        for day, counts in sorted(daily.items())
    ]
    sorted_slots = [
        TimeSlotAppointmentMetric(
            weekday=WEEKDAY_NAMES[weekday],
            slot_start_hour=hour,
            appointment_count=counts.appointment_count,
            completed_count=counts.completed_count,
            cancelled_count=counts.cancelled_count,
            cancellation_rate=_rate(counts.cancelled_count, counts.appointment_count),
            actual_revenue=_money(counts.actual_revenue),
        )
        for (weekday, hour), counts in sorted(time_slots.items())
    ]
    dates = sorted(daily)
    average_completed_revenue = (
        _money(totals.actual_revenue / totals.completed_with_revenue_count)
        if totals.completed_with_revenue_count
        else None
    )
    return AppointmentMetrics(
        metric_version=METRIC_VERSION,
        period_start=dates[0] if dates else None,
        period_end=dates[-1] if dates else None,
        observed_weeks=len(observed_weeks),
        appointment_count=totals.appointment_count,
        completed_count=totals.completed_count,
        cancelled_count=totals.cancelled_count,
        no_show_count=totals.no_show_count,
        cancellation_rate=_rate(totals.cancelled_count, totals.appointment_count),
        actual_revenue=_money(totals.actual_revenue),
        average_completed_revenue=average_completed_revenue,
        daily=sorted_days,
        time_slots=sorted_slots,
        limitations=[
            "수용 가능 인력·슬롯 데이터가 없어 가동률과 예약률은 계산하지 않습니다.",
            "actual_revenue는 completed 상태의 paid_amount 합계이며, 추정 매출이 아닙니다.",
        ],
    )


@dataclass
class _Counts:
    appointment_count: int = 0
    completed_count: int = 0
    cancelled_count: int = 0
    no_show_count: int = 0
    completed_with_revenue_count: int = 0
    actual_revenue: Decimal = Decimal("0")

    def add(self, row: AppointmentMetricRow) -> None:
        self.appointment_count += 1
        if row.status == "completed":
            self.completed_count += 1
            if row.paid_amount is not None:
                self.completed_with_revenue_count += 1
                self.actual_revenue += row.paid_amount
        elif row.status == "cancelled":
            self.cancelled_count += 1
        elif row.status == "no_show":
            self.no_show_count += 1


def _rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def _money(amount: Decimal) -> Money:
    return Money(amount=f"{amount.quantize(Decimal('0.01'))}")
