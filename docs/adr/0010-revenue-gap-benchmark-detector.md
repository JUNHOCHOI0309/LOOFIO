# ADR 0010 — RevenueGap Benchmark Detector v1

## Status

Accepted

## Decision

- `RevenueGap`은 `LowDemandSlot` 후보의 주간 예약 격차를 금액 범위로 환산하는 별도 결정론적 detector다.
- 기준 결제금액은 전체 사업장 평균이 아니라, 해당 후보와 같은 요일에서 비교 기준을 충족한 다른 2시간 슬롯의 `completed` / `paid_amount` 표본 평균을 사용한다.
- 완료 결제 표본이 5건 미만이면 금액 후보를 만들지 않는다.
- 월간 범위는 `주간 예약 격차 × 기준 평균 결제금액 × 4.345주 × 50~100% 회복 가정`으로 계산한다.
- `revenue-gap-benchmark-v1` 결과는 Observation(예약 격차)과 Estimate(회복 가정)를 분리하며, Opportunity·Recommendation·Action을 자동 생성하지 않는다.

## Limitations

- 예약 가능 capacity, 인력, 날씨, 행사, 가격 변동, 서비스 구성은 보정하지 않는다.
- 결과는 실제 매출 손실, 보장 매출, Incremental Revenue, Action 효과나 ROI를 뜻하지 않는다.

## Rollback

새 read-only detector endpoint를 비활성화해도 저장된 Opportunity, Action, Result에는 영향이 없다.
