from collections import defaultdict

from app.metrics.appointments import AppointmentMetricRow, WEEKDAY_NAMES
from app.schemas.detectors import CancellationHotspotCandidate, CancellationHotspotDetection


DETECTOR_VERSION = "cancellation-hotspot-v1"
MINIMUM_APPOINTMENT_SAMPLES = 15
MINIMUM_BASELINE_MULTIPLE = 1.5
DISRUPTION_STATUSES = frozenset({"cancelled", "no_show"})


def detect_cancellation_hotspots(rows: list[AppointmentMetricRow]) -> CancellationHotspotDetection:
    """Find observed weekday/time/offering groups with unusually frequent cancellations or no-shows."""
    observed_weeks = {(row.visit_start_at.isocalendar().year, row.visit_start_at.isocalendar().week) for row in rows}
    baseline_appointment_count = len(rows)
    baseline_disruption_count = sum(row.status in DISRUPTION_STATUSES for row in rows)
    baseline_disruption_rate = _rate(baseline_disruption_count, baseline_appointment_count)
    grouped_rows: dict[tuple[int, int, str], list[AppointmentMetricRow]] = defaultdict(list)
    missing_offering_count = 0
    for row in rows:
        if not row.offering_name:
            missing_offering_count += 1
            continue
        grouped_rows[(row.visit_start_at.weekday(), row.visit_start_at.hour // 2 * 2, row.offering_name)].append(row)

    candidates: list[CancellationHotspotCandidate] = []
    if baseline_disruption_rate > 0:
        for (weekday, hour, offering_name), group in grouped_rows.items():
            appointment_count = len(group)
            cancelled_count = sum(row.status == "cancelled" for row in group)
            no_show_count = sum(row.status == "no_show" for row in group)
            disruption_count = cancelled_count + no_show_count
            disruption_rate = _rate(disruption_count, appointment_count)
            rate_multiple = disruption_rate / baseline_disruption_rate
            if appointment_count < MINIMUM_APPOINTMENT_SAMPLES or rate_multiple < MINIMUM_BASELINE_MULTIPLE:
                continue
            candidates.append(
                CancellationHotspotCandidate(
                    weekday=WEEKDAY_NAMES[weekday],
                    slot_start_hour=hour,
                    offering_name=offering_name,
                    observed_weeks=len(observed_weeks),
                    appointment_count=appointment_count,
                    cancelled_count=cancelled_count,
                    no_show_count=no_show_count,
                    disruption_count=disruption_count,
                    disruption_rate=round(disruption_rate, 4),
                    baseline_disruption_rate=round(baseline_disruption_rate, 4),
                    rate_multiple=round(rate_multiple, 4),
                )
            )
    candidates.sort(key=lambda item: (item.rate_multiple, item.disruption_rate, item.appointment_count, item.weekday, item.slot_start_hour, item.offering_name), reverse=True)

    limitations = [
        "취소와 노쇼를 함께 예약 이탈로 계산합니다. 취소 사유나 고객 의도는 알 수 없습니다.",
        f"요일·2시간 슬롯·Offering 조합의 예약 표본이 {MINIMUM_APPOINTMENT_SAMPLES}건 이상이고, 사업장 전체 예약 이탈률의 {MINIMUM_BASELINE_MULTIPLE}배 이상일 때만 후보로 표시합니다.",
        "관측된 패턴은 원인·인과관계·매출 손실·Recommendation을 의미하지 않습니다.",
        "영업시간·예약 가능 인력·외부 요인을 보정하지 않습니다.",
    ]
    if missing_offering_count:
        limitations.append(f"Offering이 없는 예약 {missing_offering_count}건은 시간대·Offering 후보 비교에서 제외했습니다.")
    return CancellationHotspotDetection(
        detector_version=DETECTOR_VERSION,
        minimum_appointment_samples=MINIMUM_APPOINTMENT_SAMPLES,
        minimum_baseline_multiple=MINIMUM_BASELINE_MULTIPLE,
        observed_weeks=len(observed_weeks),
        baseline_appointment_count=baseline_appointment_count,
        baseline_disruption_count=baseline_disruption_count,
        baseline_disruption_rate=round(baseline_disruption_rate, 4),
        candidates=candidates,
        limitations=limitations,
    )


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0
