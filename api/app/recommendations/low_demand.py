from dataclasses import dataclass

from app.schemas.opportunities import Opportunity
from app.schemas.recommendations import RecommendationExpectedEffect


RECOMMENDATION_VERSION = "low-demand-manual-test-v1"


@dataclass(frozen=True)
class RecommendationDraft:
    version: str
    hypothesis: str
    action_type: str
    channel: str
    target_segment: dict[str, str | int]
    expected_effect: RecommendationExpectedEffect | None
    confidence: float
    explanation: str
    limitations: list[str]


def build_low_demand_recommendation_draft(opportunity: Opportunity) -> RecommendationDraft:
    """Create a deterministic, non-executing test proposal from an Opportunity only."""
    if opportunity.type != "LOW_DEMAND_SLOT":
        raise ValueError("LOW_DEMAND_SLOT Opportunity만 지원합니다.")

    weekday = str(opportunity.segment["weekday"])
    start_hour = int(opportunity.segment["start_hour"])
    end_hour = int(opportunity.segment["end_hour"])
    expected_effect = (
        RecommendationExpectedEffect(
            value_low=opportunity.estimate.value_low,
            value_high=opportunity.estimate.value_high,
            assumptions=opportunity.estimate.assumptions,
            basis="opportunity_estimate",
        )
        if opportunity.estimate
        else None
    )
    limitations = [
        *opportunity.limitations,
        "이 초안은 수요를 높인다는 인과관계를 증명하지 않으며, 수동으로 검토할 실험 가설입니다.",
        "승인만으로 고객 메시지, 광고, 쿠폰, 가격 변경 등 외부 실행은 일어나지 않습니다.",
    ]
    return RecommendationDraft(
        version=RECOMMENDATION_VERSION,
        hypothesis=(
            f"{weekday} {start_hour:02d}:00–{end_hour:02d}:00 슬롯에 한정된 수동 프로모션을 작게 검토하면 "
            "해당 슬롯의 예약 수요 변화를 측정할 수 있습니다."
        ),
        action_type="manual_time_slot_offer_test",
        channel="manual",
        target_segment={
            "weekday": weekday,
            "start_hour": start_hour,
            "end_hour": end_hour,
            "customer_targeting": "not_configured",
        },
        expected_effect=expected_effect,
        confidence=opportunity.confidence,
        explanation=(
            "저수요 Observation을 검증하기 위한 수동 실험 초안입니다. 대상 고객 선정, 혜택 내용, "
            "예산 및 실제 실행은 별도 Action 단계에서 사용자가 승인해야 합니다."
        ),
        limitations=limitations,
    )
