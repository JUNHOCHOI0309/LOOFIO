from collections import defaultdict
from datetime import date
from statistics import median

from app.metrics.appointments import AppointmentMetricRow
from app.schemas.detectors import DormantCustomerCandidate, DormantCustomerDetection


DETECTOR_VERSION = "dormant-customer-v1"
MINIMUM_OVERDUE_RATIO = 1.3
MINIMUM_INDIVIDUAL_INTERVALS = 2
MINIMUM_OFFERING_REFERENCE_INTERVALS = 10
MINIMUM_BUSINESS_REFERENCE_INTERVALS = 30


def detect_dormant_customers(rows: list[AppointmentMetricRow], *, as_of_date: date) -> DormantCustomerDetection:
    """Return customers whose completed-visit gap exceeds a deterministic revisit baseline."""
    completed_by_customer: dict[str, list[AppointmentMetricRow]] = defaultdict(list)
    missing_customer_token_count = 0
    future_completed_appointment_count = 0
    for row in rows:
        if row.status != "completed":
            continue
        if row.visit_start_at.date() > as_of_date:
            future_completed_appointment_count += 1
            continue
        if not row.customer_token:
            missing_customer_token_count += 1
            continue
        completed_by_customer[row.customer_token].append(row)

    customer_visits = {token: _daily_visits(customer_rows) for token, customer_rows in completed_by_customer.items()}
    business_intervals = [
        interval
        for visits in customer_visits.values()
        for interval in _interval_days(visits)
    ]
    offering_intervals: dict[str, list[int]] = defaultdict(list)
    for customer_rows in completed_by_customer.values():
        rows_by_offering: dict[str, list[AppointmentMetricRow]] = defaultdict(list)
        for row in customer_rows:
            if row.offering_name:
                rows_by_offering[row.offering_name].append(row)
        for offering_name, offering_rows in rows_by_offering.items():
            offering_intervals[offering_name].extend(_interval_days(_daily_visits(offering_rows)))

    candidates: list[DormantCustomerCandidate] = []
    for customer_token, visits in customer_visits.items():
        if not visits:
            continue
        latest_visit = visits[-1]
        individual_intervals = _interval_days(visits)
        expected_revisit_days, baseline_source, reference_interval_count = _expected_revisit_days(
            individual_intervals=individual_intervals,
            offering_intervals=offering_intervals.get(latest_visit.offering_name or "", []),
            business_intervals=business_intervals,
        )
        if expected_revisit_days is None:
            continue
        days_since_last_completed_visit = (as_of_date - latest_visit.visit_start_at.date()).days
        overdue_ratio = days_since_last_completed_visit / expected_revisit_days
        if overdue_ratio < MINIMUM_OVERDUE_RATIO:
            continue
        candidates.append(
            DormantCustomerCandidate(
                customer_token=customer_token,
                latest_offering_name=latest_visit.offering_name,
                completed_visit_count=len(visits),
                last_completed_visit_date=latest_visit.visit_start_at.date(),
                days_since_last_completed_visit=days_since_last_completed_visit,
                expected_revisit_days=round(expected_revisit_days, 2),
                overdue_ratio=round(overdue_ratio, 4),
                baseline_source=baseline_source,
                reference_interval_count=reference_interval_count,
            )
        )
    candidates.sort(key=lambda item: (item.overdue_ratio, item.days_since_last_completed_visit, item.customer_token), reverse=True)

    limitations = [
        "완료 방문의 날짜 간격만 사용합니다. 예약·취소·노쇼는 재방문으로 계산하지 않습니다.",
        "기준 주기는 개인 방문 간격(최소 2개)을 우선하고, 부족하면 동일 Offering 고객군(최소 10개), 그다음 사업장 전체 고객군(최소 30개)의 중앙값을 사용합니다.",
        f"마지막 완료 방문 이후 경과일이 기준 주기의 {MINIMUM_OVERDUE_RATIO}배 이상일 때만 재방문 지연 후보로 표시합니다.",
        "후보는 이탈·고객 의도·매출 손실을 뜻하지 않으며, 고객 메시지나 외부 실행을 만들지 않습니다.",
    ]
    if missing_customer_token_count:
        limitations.append(f"가명 customer_token이 없는 완료 예약 {missing_customer_token_count}건은 고객별 분석에서 제외했습니다.")
    if future_completed_appointment_count:
        limitations.append(f"기준일 이후의 완료 예약 {future_completed_appointment_count}건은 분석에서 제외했습니다.")
    return DormantCustomerDetection(
        detector_version=DETECTOR_VERSION,
        as_of_date=as_of_date,
        minimum_overdue_ratio=MINIMUM_OVERDUE_RATIO,
        completed_customer_count=len(customer_visits),
        candidates=candidates,
        limitations=limitations,
    )


def _daily_visits(rows: list[AppointmentMetricRow]) -> list[AppointmentMetricRow]:
    """A same-day multi-service visit is one visit for revisit-cycle calculations."""
    latest_by_day: dict[date, AppointmentMetricRow] = {}
    for row in rows:
        visit_day = row.visit_start_at.date()
        current = latest_by_day.get(visit_day)
        if current is None or row.visit_start_at > current.visit_start_at:
            latest_by_day[visit_day] = row
    return [latest_by_day[visit_day] for visit_day in sorted(latest_by_day)]


def _interval_days(visits: list[AppointmentMetricRow]) -> list[int]:
    return [
        (next_visit.visit_start_at.date() - previous_visit.visit_start_at.date()).days
        for previous_visit, next_visit in zip(visits, visits[1:])
        if next_visit.visit_start_at.date() > previous_visit.visit_start_at.date()
    ]


def _expected_revisit_days(
    *, individual_intervals: list[int], offering_intervals: list[int], business_intervals: list[int]
) -> tuple[float | None, str | None, int]:
    if len(individual_intervals) >= MINIMUM_INDIVIDUAL_INTERVALS:
        return float(median(individual_intervals)), "individual", len(individual_intervals)
    if len(offering_intervals) >= MINIMUM_OFFERING_REFERENCE_INTERVALS:
        return float(median(offering_intervals)), "offering", len(offering_intervals)
    if len(business_intervals) >= MINIMUM_BUSINESS_REFERENCE_INTERVALS:
        return float(median(business_intervals)), "business", len(business_intervals)
    return None, None, 0
