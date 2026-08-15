# ADR 0015 — Versioned Detector Opportunities v1

## Status

Accepted

## Decision

- `opportunities`는 기존 `LOW_DEMAND_SLOT` 외에 `CANCELLATION_HOTSPOT`, `DORMANT_CUSTOMER`, `SERVICE_DEMAND_GAP` 유형을 저장할 수 있도록 additive migration으로 확장한다.
- 새 유형은 각각 detector code/version과 자연 키를 분리한다. LowDemand의 과거 v1/v2 Opportunity와 연결된 Recommendation·Action·Result는 변경하지 않는다.
- CancellationHotspot과 ServiceDemandGap은 일반 refresh에 포함한다. DormantCustomer는 명시적인 `as_of_date`가 있을 때만 refresh해 기준일이 재현 가능하도록 한다.
- 세 유형은 Observation과 limitations만 저장하며 Estimate·Recommendation·Action을 자동 생성하지 않는다.
- DormantCustomer의 natural key와 evidence에는 원문 customer token 대신 SHA-256 hash를 사용하고, 화면용 Observation에는 마스킹된 참조값만 저장한다.

## Scoring

Score와 confidence는 실행 효과나 매출 실현 확률이 아닌, Dashboard 정렬을 위한 결정론적 우선순위 보조값이다. 표본 수·관측 주수·상대 편차만 사용하며 0.7 confidence를 상한으로 둔다.

## Rollback

새 Opportunity 유형 refresh를 비활성화해도 기존 LowDemand Opportunity와 모든 Action 이력은 남는다. Migration은 기존 행을 변경하거나 삭제하지 않는다.
