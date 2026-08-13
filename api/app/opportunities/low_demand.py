from dataclasses import dataclass
from decimal import Decimal

from app.analytics.detectors.low_demand_slots import DETECTOR_VERSION, detect_low_demand_slots
from app.metrics.appointments import AppointmentMetricRow, calculate_appointment_metrics
from app.schemas.metrics import Money
from app.schemas.opportunities import OpportunityEstimate, OpportunityObservation


@dataclass(frozen=True)
class OpportunityDraft:
    natural_key: str
    segment: dict[str, str | int]
    observation: OpportunityObservation
    estimate: OpportunityEstimate | None
    score: float
    confidence: float
    limitations: list[str]
    evidence: list[tuple[str, dict[str, object]]]


def build_low_demand_opportunity_drafts(rows: list[AppointmentMetricRow]) -> list[OpportunityDraft]:
    detection = detect_low_demand_slots(rows)
    metrics = calculate_appointment_metrics(rows)
    average_revenue = metrics.average_completed_revenue
    drafts: list[OpportunityDraft] = []
    for candidate in detection.candidates:
        observation = OpportunityObservation(
            average_appointments_per_week=candidate.average_appointments_per_week,
            comparison_median_per_week=candidate.comparison_median_per_week,
            demand_index=candidate.demand_index,
            observed_weeks=candidate.observed_weeks,
        )
        estimate = _estimate(candidate.comparison_median_per_week - candidate.average_appointments_per_week, average_revenue)
        confidence = _confidence(candidate.observed_weeks, average_revenue is not None)
        score = _score(estimate, candidate.observed_weeks, confidence)
        segment = {"weekday": candidate.weekday, "start_hour": candidate.slot_start_hour, "end_hour": candidate.slot_start_hour + 2}
        limitations = [*detection.limitations]
        if not estimate:
            limitations.append("완료 예약의 결제금액 표본이 없어 금액 추정은 제공하지 않습니다.")
        evidence = [
            (
                "LOW_DEMAND_OBSERVATION",
                {"segment": segment, "observation": observation.model_dump(), "detector_version": DETECTOR_VERSION},
            ),
        ]
        if estimate:
            evidence.append(("REVENUE_GAP_ASSUMPTIONS", estimate.model_dump()))
        drafts.append(
            OpportunityDraft(
                natural_key=f"{candidate.weekday}:{candidate.slot_start_hour}",
                segment=segment,
                observation=observation,
                estimate=estimate,
                score=score,
                confidence=confidence,
                limitations=limitations,
                evidence=evidence,
            )
        )
    return drafts


def _estimate(weekly_booking_gap: float, average_revenue: Money | None) -> OpportunityEstimate | None:
    if weekly_booking_gap <= 0 or not average_revenue:
        return None
    base_monthly_value = Decimal(str(weekly_booking_gap)) * Decimal(average_revenue.amount) * Decimal("4.345")
    return OpportunityEstimate(
        value_low=Money(amount=f"{(base_monthly_value * Decimal('0.50')).quantize(Decimal('0.01'))}"),
        value_high=Money(amount=f"{base_monthly_value.quantize(Decimal('0.01'))}"),
        assumptions=[
            "같은 요일의 비교 시간대 중앙값까지 예약 수요가 회복된다고 가정합니다.",
            "주간 예약 격차의 50~100%가 회복되는 시나리오를 사용합니다.",
            "완료 예약의 평균 paid_amount와 월 4.345주를 사용합니다.",
        ],
    )


def _confidence(observed_weeks: int, has_payment_data: bool) -> float:
    weeks_component = min(0.25, max(0, observed_weeks - 8) * 0.03125)
    payment_component = 0.15 if has_payment_data else 0.0
    return round(min(0.85, 0.45 + weeks_component + payment_component), 3)


def _score(estimate: OpportunityEstimate | None, observed_weeks: int, confidence: float) -> float:
    impact = min(35.0, float(Decimal(estimate.value_high.amount) / Decimal("1000000") * Decimal("35"))) if estimate else 0.0
    confidence_points = confidence * 30
    persistence = min(20.0, observed_weeks / 12 * 20)
    return round(impact + confidence_points + persistence + 15, 2)
