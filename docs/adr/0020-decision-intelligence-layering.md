# ADR 0020 — Decision Intelligence 계층 분리

- 상태: Accepted
- 기준일: 2026-08-18
- 기준 문서 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`

## Context

현재 Hospital MVP는 Opportunity에서 deterministic Recommendation Draft를 생성한 뒤 Decision, Manual Action, Result, baseline Measurement로 연결한다. 이 흐름은 현재 제품 루프를 검증하는 데 유효하지만, Opportunity에서 곧바로 행동 초안으로 이동하므로 다음 책임이 분리되어 있지 않다.

```text
사업 입력의 준비도
가능한 원인 가설
대안 전략 비교
재사용 가능한 실행 지식
실행 전 실험 계약
최종 실행 패키지
품질 검증
```

이 책임을 하나의 AI Recommendation Engine이나 하나의 거대한 서비스에 넣으면 원인과 행동, 계산과 설명, 실행과 측정의 경계가 흐려지고 일반적인 조언으로 퇴행할 위험이 있다.

## Decision

Opportunity 이후 목표 구조를 다음 additive 계층으로 분리한다.

```text
Opportunity
→ Decision Context / Readiness
→ Cause Analysis
→ Strategy Comparison
→ Versioned Action Playbook
→ Economics / Feasibility
→ Experiment Definition
→ Recommendation Package
→ Recommendation Quality
→ User Decision
→ Existing Action / Future Execution
→ Result / Measurement
```

각 계층은 다음 원칙을 따른다.

- Metric, Detector, Score, 경제성, 품질, Measurement의 정량 판정은 deterministic하다.
- Cause Candidate는 사실이 아니라 검증 가능한 가설이다.
- Strategy는 최소 대안을 비교하고 `DATA_COLLECTION`, `CAPACITY_OPERATION`, `NO_ACTION`을 정상 결과로 허용한다.
- Recommendation Package Assembler는 앞 단계의 결과를 조립하며 숫자를 재계산하거나 만들어내지 않는다.
- 각 단계는 ID, version, source reference 또는 input hash를 보존한다.
- 첫 구현은 저장·외부 실행이 없는 Preview-first 방식으로 진행한다.
- 현재 deterministic Recommendation과 Manual Action은 fallback과 회귀 기준으로 유지한다.

이 ADR은 목표 아키텍처의 결정이며, 관련 migration·code·test가 없는 계층을 구현 완료로 만들지 않는다.

## Consequences

- 모듈과 API가 늘어나지만 각 책임을 독립적으로 테스트하고 버전 관리할 수 있다.
- UI는 Observation, Cause, Strategy, Playbook, Experiment, Package, Quality를 구분해 표시해야 한다.
- Persistence는 전용 Data Schema와 API Contract에 따라 additive하게 추가한다.
- 기존 Recommendation·Action·Result·Measurement 계약은 즉시 제거하지 않는다.
- AI는 deterministic 구조를 설명·표현하는 계층으로 뒤로 이동한다.

## Risk self-review

- 계층이 과도하게 세분화되어 개발 속도를 낮출 수 있으므로 첫 범위는 `LOW_DEMAND_SLOT` 하나로 제한한다.
- Client가 앞 단계 결과를 임의 조작하지 못하도록 서버가 Opportunity를 읽고 단계별 결과를 재계산한다.
- 문서 존재를 구현 완료로 오인하지 않도록 `CURRENT_IMPLEMENTATION_STATUS.md`에 미구현 상태를 유지한다.
- Tenant·Business scope는 모든 Snapshot·Run·Package에 포함한다.

## Rollback

Decision Intelligence Preview 또는 신규 Package 생성 기능을 비활성화하고 현재 deterministic Recommendation Draft 흐름으로 되돌린다. 신규 테이블이 이미 추가됐다면 데이터를 삭제하지 않고 읽기·쓰기만 중단한 뒤 forward-fix를 우선한다.
