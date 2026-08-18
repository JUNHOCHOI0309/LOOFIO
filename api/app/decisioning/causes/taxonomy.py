from __future__ import annotations

from app.decisioning.causes.models import CauseCode, CauseDefinition, CauseInputRequirement, RequirementLevel


def _r(path: str, description: str) -> CauseInputRequirement:
    return CauseInputRequirement(field_path=path, level=RequirementLevel.REQUIRED, description=description)


def _o(path: str, description: str) -> CauseInputRequirement:
    return CauseInputRequirement(field_path=path, level=RequirementLevel.OPTIONAL, description=description)


def _b(path: str, description: str) -> CauseInputRequirement:
    return CauseInputRequirement(field_path=path, level=RequirementLevel.BLOCKING, description=description)


CAUSE_TAXONOMY: tuple[CauseDefinition, ...] = (
    CauseDefinition(
        code=CauseCode.DATA_QUALITY_ARTIFACT,
        stable_order=0,
        core_for_low_demand_slot=True,
        hypothesis="관측된 저수요 현상이 import, mapping, timezone 또는 source lineage 품질 문제의 영향일 가능성이 있습니다.",
        requirements=(
            _r("data_quality.import_status", "import 처리 상태"),
            _r("data_quality.validation_status", "validation 요약"),
            _r("data_quality.source_lineage_available", "Opportunity 근거 재현 가능 여부"),
            _r("data_quality.data_freshness_at", "데이터 최신성"),
            _o("data_quality.timezone_validation_status", "timezone 검증 상태"),
            _o("data_quality.offering_resolution_rate", "Offering 매핑 품질"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.CAPACITY_OR_OPERATION_CONSTRAINT,
        stable_order=1,
        core_for_low_demand_slot=True,
        hypothesis="목표 슬롯에 실제 판매 가능한 운영 capacity 또는 Offering 제공 가능성이 제한되었을 가능성이 있습니다.",
        requirements=(
            _r("business_constraints.business_hours", "목표 슬롯 영업 여부"),
            _r("operation.slot_capacity_confirmed", "슬롯 capacity 확인"),
            _r("operation.offering_available", "Offering 제공 가능 여부"),
            _o("operation.eligible_staff_count", "Offering 수행 가능 인원"),
            _o("operation.room_available", "공간 가용성"),
            _o("operation.equipment_available", "장비 가용성"),
            _b("operation.slot_capacity_confirmed", "수요 확대 전 capacity 확인"),
            _b("operation.offering_available", "Offering 실행 가능 여부"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.OFFER_SLOT_MISMATCH,
        stable_order=2,
        core_for_low_demand_slot=True,
        hypothesis="분석 대상 Offering의 특성과 목표 시간대가 맞지 않았을 가능성이 있습니다.",
        requirements=(
            _r("offering.offering_id", "분석 대상 Offering"),
            _r("offering.offering_name", "Offering 표시명"),
            _r("offering.target_slot_available", "목표 슬롯 Offering 제공 가능 여부"),
            _o("operation.eligible_staff_count", "Offering 수행 가능 인원"),
            _b("offering.target_slot_available", "목표 슬롯 실행 가능 여부"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.RETENTION_GAP,
        stable_order=3,
        core_for_low_demand_slot=True,
        hypothesis="재방문 가능 고객군이 목표 슬롯과 연결되지 않았을 가능성이 있습니다.",
        requirements=(
            _r("customer_activation.customer_token_available", "비식별 고객 연결 가능 여부"),
            _r("customer_activation.completed_visit_history_available", "완료 방문 이력"),
            _r("customer_activation.revisit_interval_available", "재방문 기준"),
            _r("customer_activation.eligible_cohort_count", "집계된 eligible cohort"),
            _b("customer_activation.marketing_consent_capability", "고객 접촉 동의 capability"),
            _b("channels.tracking_capability", "실행 추적 capability"),
            _b("measurement.result_source", "결과 source"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.DISCOVERABILITY_GAP,
        stable_order=4,
        core_for_low_demand_slot=True,
        hypothesis="Offering 또는 목표 슬롯이 발견·예약 경로에서 충분히 노출되지 않았을 가능성이 있습니다.",
        requirements=(
            _r("channels", "발견 경로"),
            _r("offering.target_slot_visible", "목표 슬롯 또는 Offering 노출 상태"),
            _r("measurement.result_source", "유입 결과 source"),
            _b("channels.tracking_capability", "실행 추적 capability"),
            _b("channels.owner", "실행 담당자"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.DEMAND_DEFICIT,
        stable_order=5,
        core_for_low_demand_slot=True,
        hypothesis="해당 요일·시간대의 수요 자체가 지속적으로 낮을 가능성이 있습니다.",
        requirements=(
            _r("observation.observed_weeks", "관측 주 수"),
            _r("observation.demand_index", "상대 수요 지수"),
            _r("observation.average_appointments_per_week", "평균 예약 수"),
            _r("observation.comparison_median_per_week", "비교 기준 예약 수"),
            _o("cause_signals.broader_demand_proxy_available", "더 넓은 수요 proxy"),
            _b("operation.slot_capacity_confirmed", "capacity가 열린 상태인지 확인"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.CONVERSION_FRICTION,
        stable_order=6,
        core_for_low_demand_slot=False,
        conditional_signal_path="cause_signals.booking_funnel_available",
        hypothesis="노출 또는 예약 시작 이후 예약 완료 단계에서 마찰이 있었을 가능성이 있습니다.",
        requirements=(
            _r("cause_signals.booking_funnel_available", "booking funnel 데이터"),
            _b("channels.tracking_capability", "funnel 추적 capability"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.CHANNEL_MISMATCH,
        stable_order=7,
        core_for_low_demand_slot=False,
        conditional_signal_path="cause_signals.channel_attribution_available",
        hypothesis="현재 채널의 도달 방식이 목표 Offering 또는 시간대와 맞지 않았을 가능성이 있습니다.",
        requirements=(
            _r("cause_signals.channel_attribution_available", "채널별 attribution 데이터"),
            _b("channels.tracking_capability", "attribution/tracking"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.VALUE_OR_PRICE_FRICTION,
        stable_order=8,
        core_for_low_demand_slot=False,
        conditional_signal_path="cause_signals.value_price_signal_available",
        hypothesis="가격 또는 가치 전달 관련 구조화 신호가 예약 전환을 낮췄을 가능성이 있습니다.",
        requirements=(
            _r("cause_signals.value_price_signal_available", "구조화된 가격/가치 신호"),
            _b("economics.variable_cost_per_completion", "혜택·가격 실행 전 비용 정보"),
        ),
    ),
    CauseDefinition(
        code=CauseCode.CANCELLATION_LEAKAGE,
        stable_order=9,
        core_for_low_demand_slot=False,
        conditional_signal_path="cause_signals.cancellation_evidence_available",
        hypothesis="예약 이후 취소 또는 노쇼로 목표 슬롯의 사용 가능 capacity가 소실되었을 가능성이 있습니다.",
        requirements=(
            _r("cause_signals.cancellation_evidence_available", "동일 segment의 이탈 근거"),
            _b("measurement.result_source", "결과 source"),
        ),
    ),
)


TAXONOMY_BY_CODE = {definition.code: definition for definition in CAUSE_TAXONOMY}
