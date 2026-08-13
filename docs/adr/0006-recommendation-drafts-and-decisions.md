# ADR 0006 — Recommendation 초안과 사용자 결정 기록

## Status

Accepted

## Context

LowDemandSlot Opportunity는 결정론적으로 저장되어 있으나, Opportunity만으로는 사용자가 검토할 실행 가설과 그 결정을 남길 수 없었다. MVP에서는 고객 메시지, 광고, 쿠폰, 가격 변경 같은 외부 작업을 자동으로 수행하면 안 된다.

## Decision

- 저장된 `LOW_DEMAND_SLOT` Opportunity의 Observation, Estimate, confidence, limitations만 읽어 `low-demand-manual-test-v1` Recommendation 초안을 결정론적으로 만든다.
- 초안은 수동 시간대 혜택 실험 가설만 제시하며, 고객 대상·혜택·예산을 설정하지 않는다.
- `recommendations`에는 초안과 현재 결정 상태를, `recommendation_decisions`에는 승인·거절·수정·나중에 결정의 불변 이력을 저장한다.
- `owner`, `admin`, `marketer`만 초안을 만들고 결정을 기록할 수 있다. `viewer`는 조회만 가능하다.
- `approved`는 Action을 만들거나 외부 시스템을 호출하지 않는다. Action 및 Measurement는 별도 단계로 추가한다.
- Recommendation expected effect는 Opportunity Estimate를 명시적으로 참조하는 가정 기반 범위일 뿐이며 actual revenue나 결과가 아니다.

## Consequences

- Opportunity → Recommendation → Decision 연결이 tenant 범위에서 보존된다.
- 승인 후에도 외부 부작용이 없어 Human-in-the-loop 원칙을 유지한다.
- 향후 Action을 구현할 때 별도 승인, idempotency, 감사 로그, connector 안전 범위를 설계해야 한다.

## Rollback

이 변경은 additive migration이다. 기능을 중단해도 기존 Opportunity에는 영향이 없으며, Recommendation 조회·생성 endpoint만 비활성화하면 된다.
