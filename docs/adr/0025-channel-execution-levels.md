# ADR 0025 — Channel Execution 수준과 부작용 경계

- 상태: Accepted
- 기준일: 2026-08-18
- 기준 문서 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`

## Context

현재 Action은 승인된 Recommendation에서 생성되는 사람이 수행할 계획이며 외부 메시지·광고·게시·쿠폰·Provider API를 호출하지 않는다. 향후 온라인·오프라인 실행을 연결할 때 사람이 복사해 실행하는 단계, 직원 업무, 승인된 Connector, 자동화는 승인·비용·재시도·취소·보안 위험이 서로 다르다.

Action의 사업 상태와 실제 채널 전달 상태를 하나의 `planned/in_progress/completed`만으로 표현하면 부분 실패, Provider timeout, 중복 실행, 이미 회수할 수 없는 발송을 정확히 기록하기 어렵다.

## Decision

Channel Execution 수준을 다음으로 구분한다.

```text
MANUAL
COPY_EXPORT
STAFF_OPERATED
APPROVED_CONNECTOR
BOUNDED_AUTOMATION
```

첫 Hospital Decision Intelligence vertical slice는 다음까지만 구현한다.

```text
MANUAL
COPY_EXPORT
STAFF_OPERATED
```

`APPROVED_CONNECTOR`는 별도 Provider Pilot 이후, `BOUNDED_AUTOMATION`은 per-business opt-in, hard budget/volume/risk limit, kill switch, audit, cancel, incident runbook이 준비된 별도 Phase에서만 허용한다.

객체를 다음처럼 분리한다.

```text
Action
→ ExecutionPackage
→ ExecutionAttempt
→ ExecutionEvent
→ OutcomeLinkageEvent
```

- Action은 승인된 사업 실행 계획이다.
- ExecutionPackage는 대상·Asset·채널·기간·예산·Tracking·승인 범위를 고정한다.
- Attempt는 실제 실행 시도이며 Idempotency·Retry·Provider reference를 가진다.
- Event는 append-only 실행·전달·직원 작업·취소·결과 기록이다.

모든 실행형 Package는 검증된 Tracking과 Result Source를 요구한다. 외부 부작용은 명시적 사용자 승인 후에만 실행하며 승인 범위는 Target, Asset, Channel, Schedule, Budget, Tracking, Experiment, Provider account의 hash로 고정한다.

같은 Idempotency Key와 같은 Payload는 기존 결과를 반환하고, 같은 Key와 다른 Payload는 conflict다. Timeout 후 Provider 상태를 확인하지 않고 즉시 재시도하지 않는다. 취소는 미래 실행을 중단할 수 있으나 이미 전달된 메시지·완료된 통화·배포된 인쇄물을 회수한 것으로 표시하지 않는다.

## Consequences

- 현재 `manual-action-v1`을 유지하면서 구조화된 Manual/Staff Execution을 additive하게 추가할 수 있다.
- 승인·추적·비용·부분 실패·취소·결과 Event를 채널과 무관한 공통 계약으로 관리한다.
- Provider SDK는 `validate`, `preview`, `execute`, `status`, `cancel`, `cost`, `events` Port 뒤에 둔다.
- Connector는 Opportunity·Strategy·Target 이유·Budget Policy·Measurement 해석을 결정하지 않는다.
- 직접 연락처 Export는 기본 기능으로 제공하지 않고 aggregate/tokenized/external-system-managed Target을 우선한다.

## Risk self-review

- Connector 기능이 미구현인데 UI에서 실행 가능한 것처럼 표시하지 않는다.
- 비용-bearing 실행은 budget cap과 권한 정책을 요구한다.
- Tracking 값·Event payload·로그에 환자 PII나 Secret을 저장하지 않는다.
- Cross-tenant idempotency key, tracking code, Provider event collision을 negative test로 검증한다.
- 이미 발생한 외부 부작용은 코드 rollback과 별도 운영 취소 절차를 구분한다.

## Rollback

Execution Package·Connector 기능을 비활성화하고 기존 Manual Action·Result 흐름으로 되돌린다. 이미 발생한 Attempt와 Event는 감사 기록으로 유지하고, 가능한 미래 실행만 취소한다.
