# ADR 0011 — RevenueGap Benchmark를 사용하는 LowDemand Opportunity v2

## Status

Accepted

## Context

기존 `low-demand-slot-v1` Opportunity의 금액 Estimate는 사업장 전체 완료 결제금액 평균을 사용했다. RevenueGap Benchmark Detector v1은 같은 요일 비교 시간대의 결제 표본을 사용할 수 있게 했다. 이는 Estimate 의미의 변경이므로 기존 Opportunity를 같은 version으로 갱신하면 안 된다.

## Decision

- 새 Opportunity는 `LOW_DEMAND_REVENUE_GAP` / `low-demand-revenue-gap-v2` detector metadata로 저장한다.
- Observation은 기존 LowDemandSlot의 예약 수요 비교를 유지한다.
- Estimate는 같은 요일 비교 시간대의 `completed` / `paid_amount` 표본이 5건 이상일 때만 RevenueGap Benchmark를 사용한다.
- 과거 `LOW_DEMAND_SLOT` / `low-demand-slot-v1` 레코드와 연결된 Recommendation·Action·Result는 변경하지 않는다.
- 결제 표본이 부족한 v2 Opportunity는 Observation만 저장하고, Recommendation과 외부 실행을 자동으로 만들지 않는다.

## Consequences

- `refresh`는 기존 v1과 별개의 versioned Opportunity를 생성할 수 있다. 목록 소비자는 새 v2를 우선 표시할 수 있지만, 과거 데이터는 감사·재현 목적으로 남는다.
- 계산식 변경을 위한 DB migration은 필요 없다. 기존 natural key가 detector code/version을 포함하기 때문이다.

## Rollback

v2 refresh를 비활성화하면 기존 v1 Opportunity와 모든 관련 이력은 그대로 보존된다.
