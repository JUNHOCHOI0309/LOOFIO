from dataclasses import dataclass
from decimal import Decimal

from app.analytics.detectors.low_demand_slots import DETECTOR_VERSION as LOW_DEMAND_DETECTOR_VERSION, detect_low_demand_slots
from app.analytics.detectors.revenue_gap import detect_revenue_gaps
from app.analytics.scoring.opportunity_score import OpportunityScore, score_opportunity
from app.metrics.appointments import AppointmentMetricRow
from app.schemas.detectors import RevenueGapCandidate
from app.schemas.opportunities import OpportunityEstimate, OpportunityObservation


OPPORTUNITY_DETECTOR_CODE = "LOW_DEMAND_REVENUE_GAP"
OPPORTUNITY_DETECTOR_VERSION = "low-demand-revenue-gap-v2"


@dataclass(frozen=True)
class OpportunityDraft:
    opportunity_type: str
    detector_code: str
    detector_version: str
    natural_key: str
    segment: dict[str, str | int]
    observation: OpportunityObservation
    estimate: OpportunityEstimate | None
    scoring: OpportunityScore
    confidence: float
    limitations: list[str]
    evidence: list[tuple[str, dict[str, object]]]

    @property
    def score(self) -> float:
        return self.scoring.total


def build_low_demand_opportunity_drafts(rows: list[AppointmentMetricRow]) -> list[OpportunityDraft]:
    detection = detect_low_demand_slots(rows)
    revenue_gaps = {
        (candidate.weekday, candidate.slot_start_hour): candidate
        for candidate in detect_revenue_gaps(rows).candidates
    }
    drafts: list[OpportunityDraft] = []
    for candidate in detection.candidates:
        observation = OpportunityObservation(
            average_appointments_per_week=candidate.average_appointments_per_week,
            comparison_median_per_week=candidate.comparison_median_per_week,
            demand_index=candidate.demand_index,
            observed_weeks=candidate.observed_weeks,
        )
        revenue_gap = revenue_gaps.get((candidate.weekday, candidate.slot_start_hour))
        estimate = _estimate(revenue_gap)
        confidence = _confidence(candidate.observed_weeks, revenue_gap is not None)
        scoring = _score(
            estimate=estimate,
            demand_index=candidate.demand_index,
            observed_weeks=candidate.observed_weeks,
            confidence=confidence,
        )
        segment = {"weekday": candidate.weekday, "start_hour": candidate.slot_start_hour, "end_hour": candidate.slot_start_hour + 2}
        limitations = [*detection.limitations]
        if not estimate:
            limitations.append("같은 요일 비교 시간대의 완료 결제금액 표본이 5건 미만이라 금액 추정은 제공하지 않습니다.")
        evidence = [
            (
                "LOW_DEMAND_OBSERVATION",
                {"segment": segment, "observation": observation.model_dump(), "detector_version": LOW_DEMAND_DETECTOR_VERSION},
            ),
        ]
        if estimate:
            evidence.append(("REVENUE_GAP_BENCHMARK", revenue_gap.model_dump(mode="json")))
        drafts.append(
            OpportunityDraft(
                opportunity_type="LOW_DEMAND_SLOT",
                detector_code=OPPORTUNITY_DETECTOR_CODE,
                detector_version=OPPORTUNITY_DETECTOR_VERSION,
                natural_key=f"{candidate.weekday}:{candidate.slot_start_hour}",
                segment=segment,
                observation=observation,
                estimate=estimate,
                scoring=scoring,
                confidence=confidence,
                limitations=limitations,
                evidence=evidence,
            )
        )
    return drafts


def _estimate(revenue_gap: RevenueGapCandidate | None) -> OpportunityEstimate | None:
    if not revenue_gap:
        return None
    return OpportunityEstimate(
        value_low=revenue_gap.monthly_value_low,
        value_high=revenue_gap.monthly_value_high,
        assumptions=[
            "같은 요일의 비교 시간대 중앙값까지 예약 수요가 회복된다고 가정합니다.",
            "주간 예약 격차의 50~100%가 회복되는 시나리오를 사용합니다.",
            f"같은 요일 비교 시간대의 완료 결제금액 표본 {revenue_gap.completed_payment_sample_count}건과 월 4.345주를 사용합니다.",
        ],
    )


def _confidence(observed_weeks: int, has_payment_data: bool) -> float:
    weeks_component = min(0.25, max(0, observed_weeks - 8) * 0.03125)
    payment_component = 0.15 if has_payment_data else 0.0
    return round(min(0.85, 0.45 + weeks_component + payment_component), 3)


def _score(
    *, estimate: OpportunityEstimate | None, demand_index: float, observed_weeks: int, confidence: float
) -> OpportunityScore:
    if estimate:
        impact_ratio = float(Decimal(estimate.value_high.amount) / Decimal("1000000"))
    else:
        impact_ratio = 1 - min(1.0, demand_index)
    return score_opportunity(
        impact_ratio=impact_ratio,
        confidence_ratio=confidence,
        persistence_ratio=observed_weeks / 12,
        actionability_ratio=1.0,
    )
