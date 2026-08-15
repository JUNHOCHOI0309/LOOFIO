# ADR 0012 — CancellationHotspot Detector v1

## Status

Accepted

## Context

Hospital MVP v0.2는 어떤 요일·시간대·Offering에서 취소 또는 노쇼가 반복적으로 높은지를 관찰해야 한다. 예약 상태와 Offering은 정규화된 Appointment 데이터에 이미 있으며, 새 DB 구조나 외부 호출 없이 결정론적으로 계산할 수 있다.

## Decision

- `cancellation-hotspot-v1`은 요일 × 2시간 슬롯 × Offering 조합을 비교 단위로 사용한다.
- 예약 이탈률은 `(cancelled + no_show) / 전체 예약`으로 계산한다. `booked`와 `unknown`을 포함한 모든 저장 예약은 분모에 남긴다.
- 해당 조합의 예약 표본이 15건 이상이고, 이탈률이 같은 business·기간 전체 이탈률의 1.5배 이상일 때만 후보를 반환한다.
- 이 detector는 read-only Observation endpoint만 제공하며 Opportunity, Recommendation, Action, 외부 채널 실행을 자동 생성하지 않는다.
- 기존 Metric/Detector와 다른 의미의 계산이므로 별도 detector version을 사용한다.

## Limitations

- 취소·노쇼 사유, 고객 의도, 운영 인력, 영업시간, 날씨·행사·가격 변화는 보정하지 않는다.
- 후보는 패턴 관찰일 뿐 원인·인과관계·실제 매출 손실·ROI를 뜻하지 않는다.
- Offering이 없는 예약은 조합 후보에서 제외하고 limitation으로 공개한다.

## Self-review

- Opportunity Intelligence 관점: pure Metric DTO 입력만 사용하며, 동일 입력에는 같은 결과를 반환한다. 표본·baseline·version·limitations를 응답에 기록한다.
- Product/UI 관점: 취소·노쇼 관찰을 Recommendation 또는 자동 고객 접촉으로 표현하지 않고 Dashboard에서 Observation으로만 표시한다.

## Rollback

새 endpoint와 Dashboard 카드만 비활성화하면 된다. 저장된 Opportunity, Recommendation, Action, Result에는 영향이 없다.
