# ADR 0016 — Versioned Manual Recommendations for Detector Opportunities v1

## Status

Accepted

## Context

CancellationHotspot, DormantCustomer, ServiceDemandGap Opportunity는 저장·조회할 수 있었지만 LowDemand·RevenueGap만 Recommendation → Decision → Action → Measurement 경로를 사용할 수 있었다. 관측 결과를 자동 실행이나 인과 주장으로 바꾸지 않으면서, 사용자가 기록 가능한 수동 검토 경로가 필요하다.

## Decision

- `LOW_DEMAND_SLOT`은 기존 `low-demand-manual-test-v1`을 유지한다.
- `CANCELLATION_HOTSPOT`, `DORMANT_CUSTOMER`, `SERVICE_DEMAND_GAP`에는 유형별 version을 가진 결정론적 수동 Recommendation을 만든다.
- 세 유형의 Recommendation은 `manual` channel만 사용하고, `expected_effect`는 만들지 않는다.
- CancellationHotspot은 예약 이탈 운영 절차 점검, ServiceDemandGap은 Offering·시간대 운영 상태 점검, DormantCustomer는 가명 코호트 수준의 재방문 운영 기록 점검만 제안한다.
- DormantCustomer Recommendation의 segment·설명·limitations에는 customer token·연락처·개별 메시지 대상을 포함하지 않는다.
- 승인 후에도 기존 Manual Action 계획만 만들 수 있으며, 고객 메시지·광고·쿠폰·가격 변경 등 외부 실행은 생성하지 않는다.

## Self-review

- Opportunity Intelligence 관점: detector Observation·score·confidence·Estimate를 Recommendation이 수정하거나 새 수치로 만들지 않는 것을 확인했다.
- Action/Measurement 관점: 모든 새 action type은 `manual` channel로만 저장되고, 승인·Action 생성만으로 외부 부작용이 없음을 확인했다.
- Data/Privacy 관점: DormantCustomer 견본 데이터의 customer token이 Recommendation API 응답에 포함되지 않는 회귀 테스트를 추가했다.

## Consequences

- 모든 현재 Opportunity 유형이 동일한 Decision·Action·Measurement 기록 흐름에 들어갈 수 있다.
- Observation 전용 후보에 대해 실제 매출 효과나 원인·이탈을 주장하지 않는다.
- 유형별 Recommendation 문구 또는 자동 채널 실행을 확장할 때는 새 recommendation version과 별도 안전 검토가 필요하다.

## Rollback

새 Recommendation version의 draft 생성을 비활성화해도 기존 Opportunity, Decision, Action, Result, Measurement는 삭제되거나 재해석되지 않는다.
