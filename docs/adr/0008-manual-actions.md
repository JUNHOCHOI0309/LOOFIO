# ADR 0008 — 승인된 Recommendation의 수동 Action

## Status

Accepted

## Context

Recommendation에 대한 승인 기록만으로는 사업자가 실제로 무엇을 언제 실행했는지, 이후 측정할 단위를 남길 수 없다. 그러나 MVP에서 승인만으로 외부 고객 접촉·광고 집행·쿠폰 활성화가 발생해서는 안 된다.

## Decision

- `approved` Recommendation에서만 `manual-action-v1` Action 초안을 생성한다.
- Action은 제목, 내부 실행 메모, 예정 시작/종료 시각, 선택적 예정 예산과 생성자를 저장한다.
- 상태는 `planned`, `in_progress`, `completed`, `cancelled`이며 허용된 단방향 전이만 적용한다.
- 생성과 모든 상태 변경은 `action_status_events`에 actor와 메모를 남긴다.
- Action은 외부 실행 payload나 connector를 갖지 않는다. 고객 메시지, 광고, 쿠폰, 가격 변경은 생성·승인·상태 변경 어느 단계에서도 실행하지 않는다.
- `owner`, `admin`, `marketer`만 Action을 생성하거나 상태를 변경할 수 있고 `viewer`는 조회만 할 수 있다.

## Consequences

- Recommendation → Decision → Action의 tenant-scoped 추적성이 생긴다.
- 완료된 Action은 향후 Result 입력과 Measurement의 명시적 기준점이 된다.
- 실제 외부 실행을 추가할 때는 별도 Action type, idempotency, connector 안전 범위, 감사 로그, rollback 설계를 추가해야 한다.

## Rollback

Migration은 additive다. Action API를 비활성화해도 기존 Recommendation과 Decision에는 영향이 없고, Action 이력은 보존한다.
