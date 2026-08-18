# ADR 0021 — Versioned Action Playbook Registry

- 상태: Accepted
- 기준일: 2026-08-18
- 기준 문서 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`

## Context

`SNS를 강화하세요`, `전단지를 배포하세요`, `휴면 고객에게 연락하세요` 같은 자유형 조언은 적용 조건, 실행 금지 조건, 비용, 담당자, Tracking, 실험, 성공·중단조건을 재현할 수 없다. LLM이 매번 새로운 행동을 자유롭게 만들게 하면 같은 상황에 다른 결과가 나오고, 무엇이 실제로 효과가 있었는지 Playbook 단위로 학습하기 어렵다.

## Decision

실행 지식을 다음 세 계층으로 분리한다.

```text
PlaybookDefinition
→ PlaybookApplicabilityResult
→ PlaybookInstance
```

- `PlaybookDefinition`은 tenant와 무관한 versioned registry 항목이다.
- `PlaybookApplicabilityResult`는 현재 Strategy·Decision Context에 적용 가능한지를 평가한다.
- `PlaybookInstance`는 특정 Business의 대상·Offering·슬롯·담당자·기간·예산·Tracking을 주입한 실행 초안이다.

Canonical 식별자는 설명형 code와 version을 사용한다.

```text
playbook_code = PB_LOW_DEMAND_REVISIT_COHORT
version = 1.0
playbook_id = PB_LOW_DEMAND_REVISIT_COHORT_V1
```

`PB-01` 같은 숫자형 ID는 과거 문서 호환용 alias로만 유지하고 신규 API·DB key로 사용하지 않는다.

Lifecycle은 다음을 사용한다.

```text
DRAFT
→ VALIDATED_INTERNAL
→ PILOT
→ ACTIVE

DEPRECATED
BLOCKED
```

현재 Hospital Core Playbook 12개는 모두 `DRAFT`다. 문서가 작성됐다는 이유만으로 `ACTIVE`로 승격하지 않는다.

첫 구현은 Python static registry를 사용하고, Runtime row에는 사용한 `playbook_id`, definition version, definition hash를 저장한다. 운영 UI, rollout scope, 긴급 차단이 필요해질 때 Registry Persistence를 추가한다.

## Consequences

- Playbook별 적용성, 비용, 실험, 결과 연결률을 비교할 수 있다.
- Definition에는 특정 병원명, tenant ID, 고객 ID, 실제 예산, Provider credential을 넣을 수 없다.
- 의미 변경은 기존 version을 수정하지 않고 새 version을 만든다.
- 새로운 Strategy는 최소 하나의 적합한 Playbook 또는 `NO_APPLICABLE_PLAYBOOK` 결과가 필요하다.
- AI가 생성한 자유형 아이디어는 canonical Playbook을 대체하지 않는다.

## Risk self-review

- Registry가 경직될 수 있으므로 `DRAFT` Playbook 추가와 Pilot 관찰을 허용하되 final 실행에는 Lifecycle·Quality Gate를 적용한다.
- Contraindication과 정책 태그를 누락하면 실행 위험이 있으므로 Definition validation과 negative fixture를 필수로 한다.
- Playbook Fit Score는 성공 확률이 아니라 동일 Strategy 안의 적용 우선순위임을 UI에서 명시한다.
- 개별 고객 정보는 Instance 또는 Package에도 aggregate/tokenized scope로만 전달한다.

## Rollback

신규 Playbook Resolver를 비활성화하고 legacy deterministic Recommendation을 사용한다. 문제가 있는 Playbook은 `BLOCKED` 또는 `DEPRECATED`로 전환하며 과거 Instance와 결과 기록은 유지한다.
