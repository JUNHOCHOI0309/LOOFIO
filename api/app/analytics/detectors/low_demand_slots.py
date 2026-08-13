from collections import Counter, defaultdict
from statistics import median

from app.metrics.appointments import AppointmentMetricRow, WEEKDAY_NAMES
from app.schemas.detectors import LowDemandSlotCandidate, LowDemandSlotDetection

DETECTOR_VERSION = "low-demand-slot-v1"
MINIMUM_OBSERVED_WEEKS = 8
MAXIMUM_DEMAND_INDEX = 0.65


def detect_low_demand_slots(rows: list[AppointmentMetricRow]) -> LowDemandSlotDetection:
    observed_weeks = {(row.visit_start_at.isocalendar().year, row.visit_start_at.isocalendar().week) for row in rows}
    if len(observed_weeks) < MINIMUM_OBSERVED_WEEKS:
        return LowDemandSlotDetection(
            detector_version=DETECTOR_VERSION,
            minimum_observed_weeks=MINIMUM_OBSERVED_WEEKS,
            observed_weeks=len(observed_weeks),
            candidates=[],
            limitations=["LowDemandSlot 탐지에는 최소 8주 관측치가 필요합니다."],
        )

    slot_counts = Counter((row.visit_start_at.weekday(), row.visit_start_at.hour // 2 * 2) for row in rows)
    slots_by_weekday: dict[int, list[tuple[int, float]]] = defaultdict(list)
    for (weekday, hour), count in slot_counts.items():
        slots_by_weekday[weekday].append((hour, count / len(observed_weeks)))

    candidates: list[LowDemandSlotCandidate] = []
    for weekday, slots in slots_by_weekday.items():
        if len(slots) < 2:
            continue
        for hour, average_demand in slots:
            comparison_values = [value for comparison_hour, value in slots if comparison_hour != hour]
            comparison_median = median(comparison_values)
            if comparison_median <= 0:
                continue
            demand_index = average_demand / comparison_median
            if demand_index <= MAXIMUM_DEMAND_INDEX:
                candidates.append(
                    LowDemandSlotCandidate(
                        weekday=WEEKDAY_NAMES[weekday],
                        slot_start_hour=hour,
                        observed_weeks=len(observed_weeks),
                        average_appointments_per_week=round(average_demand, 4),
                        comparison_median_per_week=round(comparison_median, 4),
                        demand_index=round(demand_index, 4),
                    )
                )
    candidates.sort(key=lambda candidate: (candidate.demand_index, candidate.weekday, candidate.slot_start_hour))
    return LowDemandSlotDetection(
        detector_version=DETECTOR_VERSION,
        minimum_observed_weeks=MINIMUM_OBSERVED_WEEKS,
        observed_weeks=len(observed_weeks),
        candidates=candidates,
        limitations=[
            "수용 가능 인력·슬롯 데이터가 없어 예약 수요의 상대 비교를 사용합니다.",
            "관측된 예약이 있는 시간대만 비교하므로 영업시간 전체의 빈 슬롯을 의미하지 않습니다.",
            "이 결과는 Opportunity 후보 Observation이며, 예상 매출이나 Recommendation이 아닙니다.",
        ],
    )
