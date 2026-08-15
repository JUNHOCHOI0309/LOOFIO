from collections import defaultdict
from decimal import Decimal

from app.analytics.detectors.low_demand_slots import DETECTOR_VERSION as LOW_DEMAND_DETECTOR_VERSION, detect_low_demand_slots
from app.metrics.appointments import AppointmentMetricRow
from app.schemas.detectors import RevenueGapCandidate, RevenueGapDetection
from app.schemas.metrics import Money


DETECTOR_VERSION = "revenue-gap-benchmark-v1"
MINIMUM_COMPLETED_PAYMENT_SAMPLES = 5
WEEKS_PER_MONTH = Decimal("4.345")


def detect_revenue_gaps(rows: list[AppointmentMetricRow]) -> RevenueGapDetection:
    low_demand = detect_low_demand_slots(rows)
    weekly_slot_counts = _weekly_slot_counts(rows, low_demand.observed_weeks)
    candidates: list[RevenueGapCandidate] = []
    missing_payment_samples = 0

    for candidate in low_demand.candidates:
        weekday_index = _weekday_index(candidate.weekday)
        reference_hours = {
            hour for (weekday, hour), weekly_count in weekly_slot_counts.items()
            if weekday == weekday_index and hour != candidate.slot_start_hour and weekly_count >= candidate.comparison_median_per_week
        }
        paid_amounts = [
            row.paid_amount for row in rows
            if row.visit_start_at.weekday() == weekday_index
            and row.visit_start_at.hour // 2 * 2 in reference_hours
            and row.status == "completed" and row.paid_amount is not None
        ]
        if len(paid_amounts) < MINIMUM_COMPLETED_PAYMENT_SAMPLES:
            missing_payment_samples += 1
            continue
        weekly_booking_gap = round(candidate.comparison_median_per_week - candidate.average_appointments_per_week, 4)
        if weekly_booking_gap <= 0:
            continue
        average_paid_amount = sum(paid_amounts, Decimal("0")) / Decimal(len(paid_amounts))
        monthly_base = Decimal(str(weekly_booking_gap)) * average_paid_amount * WEEKS_PER_MONTH
        candidates.append(
            RevenueGapCandidate(
                weekday=candidate.weekday,
                slot_start_hour=candidate.slot_start_hour,
                observed_weeks=candidate.observed_weeks,
                average_appointments_per_week=candidate.average_appointments_per_week,
                comparison_median_per_week=candidate.comparison_median_per_week,
                weekly_booking_gap=weekly_booking_gap,
                completed_payment_sample_count=len(paid_amounts),
                average_reference_paid_amount=_money(average_paid_amount),
                monthly_value_low=_money(monthly_base * Decimal("0.50")),
                monthly_value_high=_money(monthly_base),
            )
        )

    limitations = [
        *low_demand.limitations,
        "금액은 같은 요일의 비교 시간대에서 완료되고 paid_amount가 있는 예약 표본만 사용합니다.",
        "주간 예약 격차의 50~100%가 회복되고 평균 결제금액이 유지된다는 시나리오입니다. 실제 손실·보장 매출·인과효과가 아닙니다.",
        "수용 가능 인력·슬롯 데이터가 없어 Capacity Gap은 계산하지 않습니다.",
    ]
    if missing_payment_samples:
        limitations.append(f"저수요 후보 {missing_payment_samples}건은 비교 시간대의 완료 결제 표본이 {MINIMUM_COMPLETED_PAYMENT_SAMPLES}건 미만이라 금액 추정을 제외했습니다.")
    candidates.sort(key=lambda item: (Decimal(item.monthly_value_high.amount), item.weekday, item.slot_start_hour), reverse=True)
    return RevenueGapDetection(
        detector_version=DETECTOR_VERSION,
        source_detector_version=LOW_DEMAND_DETECTOR_VERSION,
        minimum_completed_payment_samples=MINIMUM_COMPLETED_PAYMENT_SAMPLES,
        observed_weeks=low_demand.observed_weeks,
        candidates=candidates,
        limitations=limitations,
    )


def _weekly_slot_counts(rows: list[AppointmentMetricRow], observed_weeks: int) -> dict[tuple[int, int], float]:
    counts: dict[tuple[int, int], int] = defaultdict(int)
    for row in rows:
        counts[(row.visit_start_at.weekday(), row.visit_start_at.hour // 2 * 2)] += 1
    return {key: count / observed_weeks for key, count in counts.items()} if observed_weeks else {}


def _weekday_index(name: str) -> int:
    return ("MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY").index(name)


def _money(value: Decimal) -> Money:
    return Money(amount=f"{value.quantize(Decimal('0.01'))}")
