from collections import Counter

from app.metrics.appointments import AppointmentMetricRow, WEEKDAY_NAMES
from app.schemas.detectors import ServiceDemandGapCandidate, ServiceDemandGapDetection


DETECTOR_VERSION = "service-demand-gap-v1"
MINIMUM_OBSERVED_WEEKS = 8
MINIMUM_OFFERING_APPOINTMENTS = 20
MINIMUM_SLOT_APPOINTMENTS = 15
MINIMUM_EXPECTED_SLOT_OFFERING_APPOINTMENTS = 5.0
MAXIMUM_SHARE_INDEX = 0.5


def detect_service_demand_gaps(rows: list[AppointmentMetricRow]) -> ServiceDemandGapDetection:
    """Find observed slots where an Offering's reservation share is relatively low."""
    observed_weeks = {(row.visit_start_at.isocalendar().year, row.visit_start_at.isocalendar().week) for row in rows}
    if len(observed_weeks) < MINIMUM_OBSERVED_WEEKS:
        return ServiceDemandGapDetection(
            detector_version=DETECTOR_VERSION,
            minimum_observed_weeks=MINIMUM_OBSERVED_WEEKS,
            observed_weeks=len(observed_weeks),
            minimum_offering_appointments=MINIMUM_OFFERING_APPOINTMENTS,
            minimum_slot_appointments=MINIMUM_SLOT_APPOINTMENTS,
            maximum_share_index=MAXIMUM_SHARE_INDEX,
            candidates=[],
            limitations=["ServiceDemandGap 탐지에는 최소 8주 관측치가 필요합니다."],
        )

    rows_with_offering = [row for row in rows if row.offering_name]
    total_appointments = len(rows_with_offering)
    offering_counts = Counter(row.offering_name for row in rows_with_offering)
    slot_counts = Counter((row.visit_start_at.weekday(), row.visit_start_at.hour // 2 * 2) for row in rows_with_offering)
    offering_slot_counts = Counter(
        (row.offering_name, row.visit_start_at.weekday(), row.visit_start_at.hour // 2 * 2)
        for row in rows_with_offering
    )
    candidates: list[ServiceDemandGapCandidate] = []
    for (offering_name, weekday, hour), slot_offering_appointment_count in offering_slot_counts.items():
        offering_appointment_count = offering_counts[offering_name]
        slot_appointment_count = slot_counts[(weekday, hour)]
        if offering_appointment_count < MINIMUM_OFFERING_APPOINTMENTS or slot_appointment_count < MINIMUM_SLOT_APPOINTMENTS:
            continue
        business_offering_share = offering_appointment_count / total_appointments if total_appointments else 0.0
        expected_slot_offering_appointment_count = slot_appointment_count * business_offering_share
        if expected_slot_offering_appointment_count < MINIMUM_EXPECTED_SLOT_OFFERING_APPOINTMENTS:
            continue
        slot_offering_share = slot_offering_appointment_count / slot_appointment_count
        share_index = slot_offering_share / business_offering_share if business_offering_share else 0.0
        if share_index > MAXIMUM_SHARE_INDEX:
            continue
        candidates.append(
            ServiceDemandGapCandidate(
                offering_name=offering_name,
                weekday=WEEKDAY_NAMES[weekday],
                slot_start_hour=hour,
                observed_weeks=len(observed_weeks),
                offering_appointment_count=offering_appointment_count,
                slot_appointment_count=slot_appointment_count,
                slot_offering_appointment_count=slot_offering_appointment_count,
                business_offering_share=round(business_offering_share, 4),
                slot_offering_share=round(slot_offering_share, 4),
                expected_slot_offering_appointment_count=round(expected_slot_offering_appointment_count, 4),
                share_index=round(share_index, 4),
            )
        )
    candidates.sort(key=lambda item: (item.share_index, item.expected_slot_offering_appointment_count - item.slot_offering_appointment_count, item.offering_name, item.weekday, item.slot_start_hour))

    limitations = [
        "각 Offering의 전체 예약 비중과 관측된 요일·2시간 슬롯의 예약 비중을 비교합니다.",
        f"최소 {MINIMUM_OBSERVED_WEEKS}주 관측, Offering 예약 {MINIMUM_OFFERING_APPOINTMENTS}건, 슬롯 예약 {MINIMUM_SLOT_APPOINTMENTS}건, 비교 기준 예약 {MINIMUM_EXPECTED_SLOT_OFFERING_APPOINTMENTS:g}건이 필요합니다.",
        f"슬롯 내 Offering 비중이 전체 비중의 {MAXIMUM_SHARE_INDEX:.0%} 이하일 때만 상대 수요 저하 후보로 표시합니다.",
        "관측된 예약이 있는 시간대만 비교하므로 영업시간 전체의 빈 슬롯, capacity, 실제 매출, 원인·인과관계를 뜻하지 않습니다.",
        "이 결과는 Observation이며 Recommendation, 할인, 가격 변경, 외부 실행을 만들지 않습니다.",
    ]
    missing_offering_count = len(rows) - total_appointments
    if missing_offering_count:
        limitations.append(f"Offering이 없는 예약 {missing_offering_count}건은 Offering별 비교에서 제외했습니다.")
    return ServiceDemandGapDetection(
        detector_version=DETECTOR_VERSION,
        minimum_observed_weeks=MINIMUM_OBSERVED_WEEKS,
        observed_weeks=len(observed_weeks),
        minimum_offering_appointments=MINIMUM_OFFERING_APPOINTMENTS,
        minimum_slot_appointments=MINIMUM_SLOT_APPOINTMENTS,
        maximum_share_index=MAXIMUM_SHARE_INDEX,
        candidates=candidates,
        limitations=limitations,
    )
