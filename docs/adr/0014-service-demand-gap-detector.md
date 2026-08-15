# ADR 0014 — ServiceDemandGap Detector v1

## Status

Accepted

## Context

Hospital MVP v0.4는 Offering별 수요가 특정 요일·시간대에 어떻게 분포하는지 관찰해야 한다. 현재 Appointment에는 Offering과 예약 시각이 있으나 영업시간·capacity·Offering별 가용 인력은 없다. 따라서 빈 시간이나 매출 기회를 단정하지 않는 상대 예약 비중 비교로 범위를 제한한다.

## Decision

- `service-demand-gap-v1`은 모든 저장 예약의 Offering별 전체 비중과 요일 × 2시간 슬롯 안의 Offering 비중을 비교한다. 취소·노쇼도 예약 수요 기록으로 분모에 포함한다.
- 최소 8주 관측, Offering 예약 20건, 슬롯 예약 15건, 전체 비중으로 계산한 슬롯 기대 예약 5건을 충족해야 비교한다.
- 슬롯 내 Offering 비중이 business 전체 Offering 비중의 50% 이하일 때만 후보를 반환한다.
- 후보에는 관찰된 슬롯 예약 수, 해당 Offering 예약 수, 두 비중, 비교 기준 기대 예약 수, share index를 포함한다.
- 결과는 read-only Observation이다. Opportunity, Estimate, Recommendation, 할인·가격 변경, 고객 메시지, 외부 실행을 자동 생성하지 않는다.

## Limitations

- 관측된 예약이 있는 시간대만 비교하며, 예약 0건을 영업시간의 빈 슬롯이나 capacity 부족으로 해석하지 않는다.
- Offering별 제공 가능 여부, 인력, 가격, 계절성, 외부 요인, 고객군을 보정하지 않는다.
- 상대 비중의 차이는 원인·매출 손실·인과관계·실행 효과를 뜻하지 않는다.

## Self-review

- Opportunity Intelligence 관점: pure Metric DTO만 사용하고, 표본 기준·share index·detector version·limitations를 응답에 기록한다.
- Product/UI 관점: “상대 수요 저하”를 사실로만 표시하고, 판매 기회·할인 효과·자동 실행으로 표현하지 않는다.

## Rollback

새 read-only endpoint와 Dashboard 카드만 비활성화하면 된다. 기존 Opportunity, Recommendation, Action, Result에는 영향을 주지 않는다.
