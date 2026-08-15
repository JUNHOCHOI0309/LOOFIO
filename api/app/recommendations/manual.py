from app.recommendations.low_demand import RecommendationDraft, build_low_demand_recommendation_draft
from app.schemas.opportunities import Opportunity


RECOMMENDATION_VERSIONS = {
    "CANCELLATION_HOTSPOT": "cancellation-hotspot-manual-review-v1",
    "DORMANT_CUSTOMER": "dormant-customer-manual-review-v1",
    "SERVICE_DEMAND_GAP": "service-demand-gap-manual-review-v1",
}


def build_manual_recommendation_draft(opportunity: Opportunity) -> RecommendationDraft:
    """Build a deterministic, non-executing review proposal from a stored Opportunity."""
    if opportunity.type == "LOW_DEMAND_SLOT":
        return build_low_demand_recommendation_draft(opportunity)
    if opportunity.type == "CANCELLATION_HOTSPOT":
        return _cancellation_hotspot_review(opportunity)
    if opportunity.type == "DORMANT_CUSTOMER":
        return _dormant_customer_review(opportunity)
    if opportunity.type == "SERVICE_DEMAND_GAP":
        return _service_demand_gap_review(opportunity)
    raise ValueError(f"지원하지 않는 Opportunity 유형입니다: {opportunity.type}")


def _cancellation_hotspot_review(opportunity: Opportunity) -> RecommendationDraft:
    weekday, start_hour, end_hour, offering_name = _slot_segment(opportunity)
    observation = opportunity.observation
    return RecommendationDraft(
        version=RECOMMENDATION_VERSIONS[opportunity.type],
        hypothesis=(
            f"{weekday} {start_hour:02d}:00–{end_hour:02d}:00의 {offering_name} 예약 이탈 패턴을 "
            "수동으로 점검하면, 해당 구간의 예약 안내·운영 절차를 검토할 근거를 만들 수 있습니다."
        ),
        action_type="manual_cancellation_flow_review",
        channel="manual",
        target_segment={"weekday": weekday, "start_hour": start_hour, "end_hour": end_hour, "offering_name": offering_name},
        expected_effect=None,
        confidence=opportunity.confidence,
        explanation=(
            f"이 구간의 예약 이탈률은 {(observation.disruption_rate or 0) * 100:.1f}%이며, "
            f"사업장 기준의 {(observation.rate_multiple or 0):.1f}배입니다. "
            "원인이나 고객 의도를 단정하지 않고 내부 운영 기록을 수동으로 검토하는 초안입니다."
        ),
        limitations=_review_limitations(opportunity),
    )


def _dormant_customer_review(opportunity: Opportunity) -> RecommendationDraft:
    offering_name = str(opportunity.segment.get("offering_name", "unknown"))
    observation = opportunity.observation
    return RecommendationDraft(
        version=RECOMMENDATION_VERSIONS[opportunity.type],
        hypothesis=(
            "재방문 지연이 관찰된 가명 고객 코호트의 운영 기록을 수동으로 검토하면, "
            "다음 예약 유입 여부를 점검할 근거를 만들 수 있습니다."
        ),
        action_type="manual_revisit_cohort_review",
        channel="manual",
        target_segment={"offering_name": offering_name, "customer_targeting": "not_configured", "customer_reference": "not_included"},
        expected_effect=None,
        confidence=opportunity.confidence,
        explanation=(
            f"마지막 완료 방문 후 {observation.days_since_last_completed_visit}일이 경과했고, "
            f"기준 재방문 간격은 {observation.expected_revisit_days}일입니다. "
            "개별 고객 식별자·연락처·메시지 내용은 Recommendation에 포함하지 않습니다."
        ),
        limitations=_review_limitations(opportunity, customer_safe=True),
    )


def _service_demand_gap_review(opportunity: Opportunity) -> RecommendationDraft:
    weekday, start_hour, end_hour, offering_name = _slot_segment(opportunity)
    observation = opportunity.observation
    return RecommendationDraft(
        version=RECOMMENDATION_VERSIONS[opportunity.type],
        hypothesis=(
            f"{weekday} {start_hour:02d}:00–{end_hour:02d}:00의 {offering_name} 예약 패턴을 수동으로 점검하면, "
            "해당 시간대의 서비스 안내·예약 가능 상태를 검토할 근거를 만들 수 있습니다."
        ),
        action_type="manual_offering_slot_review",
        channel="manual",
        target_segment={"weekday": weekday, "start_hour": start_hour, "end_hour": end_hour, "offering_name": offering_name},
        expected_effect=None,
        confidence=opportunity.confidence,
        explanation=(
            f"해당 슬롯의 {offering_name} 예약 비중은 {(observation.slot_offering_share or 0) * 100:.1f}%로, "
            f"전체 비중 대비 {(observation.share_index or 0):.2f}배입니다. "
            "영업시간·capacity·가격·할인 효과나 원인을 가정하지 않는 수동 검토 초안입니다."
        ),
        limitations=_review_limitations(opportunity),
    )


def _slot_segment(opportunity: Opportunity) -> tuple[str, int, int, str]:
    return (
        str(opportunity.segment["weekday"]),
        int(opportunity.segment["start_hour"]),
        int(opportunity.segment["end_hour"]),
        str(opportunity.segment.get("offering_name", "Offering")),
    )


def _review_limitations(opportunity: Opportunity, *, customer_safe: bool = False) -> list[str]:
    limitations = [
        *opportunity.limitations,
        "이 초안은 결정론적으로 저장된 Observation을 검토하기 위한 것이며, 원인·인과관계·실제 손실을 단정하지 않습니다.",
        "승인만으로 고객 메시지, 광고, 쿠폰, 가격 변경 등 외부 실행은 일어나지 않습니다.",
    ]
    if customer_safe:
        limitations.append("개별 고객 연락처·원문 식별자·메시지 대상은 포함하지 않으며, 외부 연락을 제안하지 않습니다.")
    return limitations
