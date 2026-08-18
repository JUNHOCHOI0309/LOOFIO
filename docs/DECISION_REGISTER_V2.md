---
title: "LOOFIO Decision Register v2"
version: "2.0"
date: "2026-08-18"
status: "통합 의사결정 기준"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
code_baseline_commit: "b7cc45d58b1fe1faa592888fd63f652ce0174f4a"
current_scope: "Hospital LOW_DEMAND_SLOT Decision Intelligence vertical slice"
---

# LOOFIO Decision Register v2

## 1. 목적

이 문서는 LOOFIO의 제품·데이터·분석·추천·실험·실행·측정에 관한 결정을 **삭제하지 않고 상태와 변경 이력으로 관리**하는 단일 Registry다.

다음 문제를 막는다.

```text
이미 결정한 내용을 구현 중 다시 논의
현재 구현과 목표 설계를 혼동
새 문서가 과거 결정을 조용히 덮어씀
미결정 사항을 코드에서 임의로 선택
Pilot 전 임시 수치를 영구 정책으로 취급
```

Decision은 구현 완료를 의미하지 않는다.

```text
ACCEPTED decision
!=
code implemented
!=
pilot validated
!=
production active
```

## 2. 상태 체계

| 상태 | 의미 |
|---|---|
| `ACCEPTED` | 현재 목표 설계의 권위 있는 결정. 구현은 별도 상태로 판단한다. |
| `CURRENT_IMPLEMENTATION` | 현재 main의 사실을 기록. 장기 목표와 다를 수 있다. |
| `PROVISIONAL_V1` | 첫 vertical slice 구현 기준. Pilot 후 versioned 재검토. |
| `OPEN` | 아직 결정하지 않음. 구현이 임의 가정하면 안 된다. |
| `DEFERRED` | 방향은 유지하지만 명시적으로 뒤 단계로 미룸. |
| `SUPERSEDED` | 후속 결정이 대체. 이력 보존을 위해 삭제하지 않음. |
| `REJECTED` | 현재 설계에서 명시적으로 허용하지 않음. |

## 3. 변경 규칙

1. Decision ID는 재사용하거나 의미를 바꾸지 않는다.
2. 기존 결정을 바꾸면 과거 Record를 삭제하지 않고 새 Decision에서 `supersedes`를 기록한다.
3. 보안·API·DB·Metric·Score·Quality·Measurement·자동 실행 변경은 관련 ADR을 함께 만든다.
4. `OPEN` 항목은 구현 코드가 임의 기본값으로 확정하지 않는다.
5. `PROVISIONAL_V1`의 수치·가중치는 validator/method version을 가진다.
6. 코드·migration·test 완료 전 `CURRENT_IMPLEMENTATION_STATUS.md`에 구현 완료로 기록하지 않는다.
7. Decision 변경 시 최소 다음 영향을 기록한다.

```text
제품/UI
API
DB migration
Metric/Score/Measurement
Tenant/PII/보안
Legacy compatibility
Rollout/Rollback
관련 문서와 Backlog
```

## 4. 상태 요약

| 상태 | 개수 |
|---|---:|
| `ACCEPTED` | 54 |
| `CURRENT_IMPLEMENTATION` | 2 |
| `PROVISIONAL_V1` | 7 |
| `OPEN` | 10 |
| `DEFERRED` | 7 |
| `SUPERSEDED` | 4 |
| `REJECTED` | 4 |

총 Decision: **88개**

## 5. Category 요약

| Category | 개수 |
|---|---:|
| `AI` | 5 |
| `AI_PRIVACY` | 1 |
| `ANALYTICS` | 1 |
| `API` | 2 |
| `ARCHITECTURE` | 2 |
| `CAUSE` | 3 |
| `CHANNEL` | 1 |
| `COMPATIBILITY` | 2 |
| `CONNECTOR` | 1 |
| `DATA_MODEL` | 3 |
| `DATA_SEMANTICS` | 1 |
| `DECISION_INPUT` | 2 |
| `ECONOMICS` | 3 |
| `EXECUTION` | 9 |
| `EXPERIMENT` | 5 |
| `EXTERNAL_CONTEXT` | 3 |
| `GOVERNANCE` | 2 |
| `MEASUREMENT` | 5 |
| `PILOT` | 2 |
| `PLATFORM` | 2 |
| `PLAYBOOK` | 6 |
| `PRIVACY` | 3 |
| `PRODUCT` | 3 |
| `QUALITY` | 4 |
| `RECOMMENDATION` | 2 |
| `ROADMAP` | 4 |
| `SCOPE` | 4 |
| `SECURITY` | 1 |
| `STRATEGY` | 5 |
| `TAXONOMY` | 1 |

## 6. 핵심 결정 한눈에 보기

| ID | 상태 | 핵심 결정 |
|---|---|---|
| `DR-001` | `ACCEPTED` | LOOFIO의 핵심 가치는 사업 데이터에서 숨은 매출 기회를 발견하고, 실행·비용·측정이 포함된 다음 행동을 설계하는 것이다. 콘텐츠 생성은 목적이 아니라 실행 수단이다. |
| `DR-002` | `ACCEPTED` | Metric, Detector, Opportunity Score, Cause/Strategy/Playbook/Quality의 정량 규칙, 경제성 계산, Measurement는 deterministic backend가 담당한다. |
| `DR-019` | `ACCEPTED` | 단일 Recommendation Engine을 Decision Input, Cause Analysis, Strategy, Action Playbook, Experiment, Recommendation Package, Quality로 분리한다. |
| `DR-020` | `ACCEPTED` | 고객에게 제공하는 핵심 결과는 진단, 대안, 선택 이유, 실행 단계, 비용, 실험, 성공·중단조건이 포함된 Action Plan Package다. |
| `DR-021` | `ACCEPTED` | 최종 추천 전 최소 두 개 Strategy 후보를 비교하며, 단일 후보만 가능하면 구조화된 이유를 기록한다. |
| `DR-022` | `ACCEPTED` | LLM 자유 생성보다 versioned Action Playbook registry를 우선한다. |
| `DR-025` | `ACCEPTED` | 실행 가능한 Playbook은 실행 전에 대상, 처리, 비교, Primary Metric, 기간, 성공조건, 중단조건, Tracking, Result Source를 고정한다. |
| `DR-026` | `PROVISIONAL_V1` | v1 통과 기준은 Total Score 75 이상, Hard Fail 0, 모든 Section Floor 충족이다. |
| `DR-030` | `ACCEPTED` | Decision Input→Cause→Strategy→Playbook→Experiment→Package/Quality→UI/Manual Action→AI 순으로 구현한다. |
| `DR-033` | `ACCEPTED` | 비용, capacity, consent, Tracking, 결과가 unknown인 상태를 0·false·없음으로 해석하지 않는다. |
| `DR-034` | `ACCEPTED` | Cause Candidate는 검토 대상 가설이며 사실·인과관계·확률로 표현하지 않는다. |
| `DR-037` | `ACCEPTED` | Data Quality, capacity, Offering, policy/consent, Tracking/Measurement, economics Gate를 통과한 실행 전략만 Score를 받는다. |
| `DR-038` | `ACCEPTED` | 부족한 입력을 보완하는 DATA_COLLECTION과 실행을 보류하는 NO_ACTION을 정상 결과로 허용한다. |
| `DR-041` | `ACCEPTED` | PlaybookDefinition, PlaybookApplicabilityResult, PlaybookInstance를 분리한다. |
| `DR-045` | `ACCEPTED` | ExperimentTemplate, Definition, Run, Result, Evaluation을 분리한다. |
| `DR-047` | `ACCEPTED` | Evidence Grade는 설계 강도, Precision은 표본과 결과 정밀도를 나타내며 별도로 관리한다. |
| `DR-049` | `ACCEPTED` | Package는 EXECUTION, OPERATIONAL, DIAGNOSTIC, HOLD로 구분한다. |
| `DR-051` | `ACCEPTED` | 일반 사용자와 관리자는 Hard Fail을 강제로 PASSED로 바꿀 수 없다. |
| `DR-053` | `ACCEPTED` | Actual Result, Opportunity Estimate, Baseline, Observed Delta, Attributed Result, Incremental Estimate, Net Contribution Estimate를 분리한다. |
| `DR-056` | `ACCEPTED` | MANUAL, COPY_EXPORT, STAFF_OPERATED, APPROVED_CONNECTOR, BOUNDED_AUTOMATION을 구분한다. |
| `DR-059` | `ACCEPTED` | 모든 실행형 Package는 ACTION_ID, URL, source code, partner code, QR, provider ID 등 최소 하나의 검증된 Tracking을 가진다. |
| `DR-063` | `ACCEPTED` | 환자 이름, 연락처 원문, 주민번호, 진단, 질병·증상, 처방, 검사, 의무기록, 상담 원문을 Package·AI·Tracking 값에 넣지 않는다. |
| `DR-067` | `ACCEPTED` | Decision Intelligence Persistence는 전용 Data Schema와 API Contract 문서가 확정된 뒤 구현한다. |
| `DR-071` | `ACCEPTED` | 첫 구현은 Hospital LOW_DEMAND_SLOT의 Decision Context→Cause→Strategy→Playbook→Experiment→Package/Quality→기존 Manual Action→Current Measurement Adapter다. |

## 7. Detailed Decision Records

### DR-001 — 제품 핵심 가치

- **상태:** `ACCEPTED`
- **Category:** `PRODUCT`
- **결정:** LOOFIO의 핵심 가치는 사업 데이터에서 숨은 매출 기회를 발견하고, 실행·비용·측정이 포함된 다음 행동을 설계하는 것이다. 콘텐츠 생성은 목적이 아니라 실행 수단이다.
- **근거:** 일반적인 AI 콘텐츠 도구와 차별화하려면 발견에서 실행·결과까지 연결돼야 한다.
- **구현 영향:** 제품 KPI·화면·Backlog는 콘텐츠 수보다 Opportunity→Action→Result 연결을 우선한다.
- **재검토 Trigger:** 제품의 핵심 가치 제안 자체를 변경할 때만 재검토한다.
- **근거 문서:** `AI_마케팅_매니저_데이터_수집_및_기획_전략_v1.1.md`, `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-002 — Deterministic 분석 경계

- **상태:** `ACCEPTED`
- **Category:** `ANALYTICS`
- **결정:** Metric, Detector, Opportunity Score, Cause/Strategy/Playbook/Quality의 정량 규칙, 경제성 계산, Measurement는 deterministic backend가 담당한다.
- **근거:** 수치와 판정의 재현성·감사·회귀 검증을 보장하기 위해서다.
- **구현 영향:** LLM SDK는 Metric·Detector·Score·경제성·실험 평가 모듈에 들어가지 않는다.
- **재검토 Trigger:** 정량 판정의 책임을 다른 계층으로 이동하려는 제안이 있을 때 재검토한다.
- **근거 문서:** `LOOFIO_OPPORTUNITY_ENGINE_V1.md`, `AGENTS.md`, `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

### DR-003 — 초기 제품 루프

- **상태:** `SUPERSEDED`
- **Category:** `PRODUCT`
- **결정:** 초기 루프는 Opportunity→Recommendation→Decision→Action→Result→Measurement로 정의됐다.
- **근거:** 현재 구현의 설명에는 유효하지만, 원인·대안·Playbook·실험을 분리하지 못한다.
- **구현 영향:** 현재 legacy 흐름의 설명에만 사용하고 목표 아키텍처의 기준으로 사용하지 않는다.
- **재검토 Trigger:** 없음. DR-019가 목표 구조를 대체한다.
- **근거 문서:** `DECISION_REGISTER_V1.md`

### DR-004 — Multi-tenant 격리

- **상태:** `ACCEPTED`
- **Category:** `SECURITY`
- **결정:** Tenant와 Business는 보안·데이터 격리의 불변 경계다.
- **근거:** 고객사 데이터 혼합은 제품 신뢰와 보안의 치명적 실패다.
- **구현 영향:** Query, cache, file, AI context, export, Playbook, Action, Measurement는 tenant/business scope를 가진다.
- **재검토 Trigger:** Tenant 모델 자체를 폐기하거나 계층을 재정의할 때만 재검토한다.
- **근거 문서:** `AGENTS.md`, `ARCHITECTURE.md`, `DEPENDENCY_RULES.md`

### DR-005 — Hospital Appointment를 첫 Domain Adapter로 사용

- **상태:** `ACCEPTED`
- **Category:** `SCOPE`
- **결정:** Hospital Appointment는 첫 검증 Domain이며, 장기 제품 전체를 병원으로 제한하지 않는다.
- **근거:** 예약·고객·결제·시간대가 현재 Opportunity Engine을 검증하기에 적합하다.
- **구현 영향:** 첫 vertical slice와 Pilot은 Hospital Appointment에 집중한다.
- **재검토 Trigger:** Hospital에서 핵심 루프가 검증되거나 Domain이 부적합하다는 근거가 생길 때 재검토한다.
- **근거 문서:** `CURRENT_IMPLEMENTATION_STATUS.md`, `LOOFIO_HOSPITAL_MVP_DECISIONS_v1.md`

### DR-006 — 직업분류와 Business Archetype 분리

- **상태:** `ACCEPTED`
- **Category:** `TAXONOMY`
- **결정:** KECO/KSCO는 온보딩의 출발점이며 실제 데이터·Detector routing은 Business Archetype과 수익 구조를 사용한다.
- **근거:** 직업명과 실제 사업 운영·매출 구조는 일치하지 않을 수 있다.
- **구현 영향:** 공식 taxonomy 원본과 LOOFIO mapping/version을 분리 저장한다.
- **재검토 Trigger:** 새 공식 분류체계 또는 Archetype 구조 변경 시 재검토한다.
- **근거 문서:** `LOOFIO_BUSINESS_TAXONOMY_V1.md`

### DR-007 — Appointment는 전사 Core Root가 아님

- **상태:** `ACCEPTED`
- **Category:** `DATA_MODEL`
- **결정:** Appointment는 APPOINTMENT_SERVICE의 Domain Object이며 전체 LOOFIO의 공통 Root가 아니다.
- **근거:** 소매·프로젝트·회원·현장 서비스는 다른 Domain Object가 필요하다.
- **구현 영향:** 공통 분석 계층은 Business, Offering, Customer, Event/Metric, Opportunity, Action, Measurement를 중심으로 둔다.
- **재검토 Trigger:** 모든 지원 Archetype이 Appointment로 자연스럽게 표현된다는 근거가 생길 때만 재검토한다.
- **근거 문서:** `LOOFIO_BUSINESS_TAXONOMY_V1.md`, `LOOFIO_DATA_SCHEMA_V1.md`

### DR-008 — 공통 판매 대상 용어는 Offering

- **상태:** `ACCEPTED`
- **Category:** `DATA_MODEL`
- **결정:** 상품·서비스·패키지·회원권 등 판매 대상을 공통으로 표현할 때 Offering을 사용한다.
- **근거:** Service라는 용어는 상품·패키지·회원권을 포괄하지 못한다.
- **구현 영향:** 새 Domain Adapter와 API는 공통 계층에서 Offering을 사용한다.
- **재검토 Trigger:** 공통 도메인 용어를 전면 재설계할 때 재검토한다.
- **근거 문서:** `LOOFIO_DATA_SCHEMA_V1.md`, `LOOFIO_BUSINESS_TAXONOMY_V1.md`

### DR-009 — 현재 deterministic Recommendation 유지

- **상태:** `CURRENT_IMPLEMENTATION`
- **Category:** `COMPATIBILITY`
- **결정:** 현재 유형별 deterministic manual Recommendation Draft는 구현 상태이며, 새 Package가 안정될 때까지 fallback과 회귀 기준으로 유지한다.
- **근거:** 기존 Decision·Action·Result 흐름을 끊지 않고 점진적으로 확장해야 한다.
- **구현 영향:** 신규 Package는 legacy adapter를 통해 기존 Action과 연결한다.
- **재검토 Trigger:** Package 기반 정식 Action 경로가 Pilot에서 안정화된 뒤 제거 여부를 검토한다.
- **근거 문서:** `CURRENT_IMPLEMENTATION_STATUS.md`, `LOOFIO_RECOMMENDATION_PACKAGE_V2.md`

### DR-010 — 현재 Measurement는 관찰 비교

- **상태:** `CURRENT_IMPLEMENTATION`
- **Category:** `MEASUREMENT`
- **결정:** 현재 same-window-prior-four-weeks-v2는 직전 동일 길이 창 평균과의 관찰 비교이며 Incremental Revenue가 아니다.
- **근거:** 현재 데이터만으로 인과효과를 주장할 수 없다.
- **구현 영향:** 현재 API·숫자는 유지하고 새 Framework에서 Grade C 또는 조건에 따라 D로 해석한다.
- **재검토 Trigger:** 더 강한 비교 Method가 구현돼도 기존 historical 결과의 의미는 변경하지 않는다.
- **근거 문서:** `CURRENT_IMPLEMENTATION_STATUS.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-011 — 첫 AI Provider

- **상태:** `OPEN`
- **Category:** `AI`
- **결정:** AI Provider와 모델은 아직 결정하지 않는다.
- **근거:** Provider보다 AI Gateway·입력 경계·구조화 출력·평가 체계를 먼저 확정해야 한다.
- **구현 영향:** 비즈니스 코드는 Provider/model에 직접 의존하지 않는다.
- **재검토 Trigger:** M5 Package Preview가 안정되고 AI wording Epic을 시작할 때 결정한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`, `FUTURE: LOOFIO_AI_ARCHITECTURE_V2.md`

### DR-012 — Production 배포 Provider

- **상태:** `OPEN`
- **Category:** `PLATFORM`
- **결정:** Cloud, managed PostgreSQL, Secret Manager, Monitoring, production migration runner는 아직 결정하지 않는다.
- **근거:** 현재는 Local과 CI가 기준이며 요구조건 없이 Provider를 고정할 이유가 없다.
- **구현 영향:** Provider 특정 구현을 Core 문서에 하드코딩하지 않는다.
- **재검토 Trigger:** Staging 설계를 시작하기 전에 ADR로 결정한다.
- **근거 문서:** `DEPLOYMENT_FLOW.md`, `CURRENT_IMPLEMENTATION_STATUS.md`

### DR-013 — External Context 최소 시작 범위

- **상태:** `DEFERRED`
- **Category:** `EXTERNAL_CONTEXT`
- **결정:** External Context는 Holiday, Weather, Local Event부터 시작하는 방향을 유지하되 첫 deterministic vertical slice 이후로 미룬다.
- **근거:** 내부 사업 데이터와 의사결정 루프를 먼저 안정화해야 한다.
- **구현 영향:** Cause 보조 Evidence와 Measurement limitation으로만 연결한다.
- **재검토 Trigger:** M7 이후 External Context Epic 시작 시 Provider와 필드를 확정한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-014 — MVP 자동 외부 실행

- **상태:** `REJECTED`
- **Category:** `EXECUTION`
- **결정:** 사용자 승인 없는 메시지, 광고, 게시, 쿠폰, 제휴비용, 외부 설정 변경은 MVP에서 허용하지 않는다.
- **근거:** 비용·정책·브랜드·개인정보 위험이 직접 발생한다.
- **구현 영향:** 현재 허용 범위는 manual, copy_export, staff_operated다.
- **재검토 Trigger:** Bounded Automation 별도 정책·Kill Switch·Pilot이 준비되기 전까지 유지한다.
- **근거 문서:** `PROHIBITED_CHANGES.md`, `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-015 — Fine-tuning 우선순위

- **상태:** `DEFERRED`
- **Category:** `AI`
- **결정:** Decision→Outcome 데이터셋, 안정된 schema, eval suite, 동의·법적 정책이 확보되기 전에는 Fine-tuning을 우선하지 않는다.
- **근거:** 현재 병목은 모델 파라미터가 아니라 데이터 계약과 실행 지식 구조다.
- **구현 영향:** Prompt/RAG/규칙 기반 baseline을 먼저 구축한다.
- **재검토 Trigger:** 반복적 실패 패턴과 충분한 학습 쌍이 확인되면 재검토한다.
- **근거 문서:** `FUTURE: LOOFIO_AI_ARCHITECTURE_V2.md`, `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-016 — AI Recommendation을 다음 1순위로 둔 계획

- **상태:** `SUPERSEDED`
- **Category:** `ROADMAP`
- **결정:** Recommendation Engine과 AI Architecture를 즉시 다음 우선순위로 두던 계획은 폐기한다.
- **근거:** 좋은 해결책의 Cause·Strategy·Playbook·Experiment 계약 없이 AI를 연결하면 일반 조언만 늘어난다.
- **구현 영향:** DR-030의 deterministic Decision Intelligence 우선순위로 대체한다.
- **재검토 Trigger:** 없음.
- **근거 문서:** `DECISION_REGISTER_V1.md`

### DR-017 — Staging·CSV를 AI 다음 순위로 둔 계획

- **상태:** `SUPERSEDED`
- **Category:** `ROADMAP`
- **결정:** Staging과 CSV robustness는 중요하지만 Decision Intelligence 문서·첫 Package Preview 이후 순서로 재배치한다.
- **근거:** 현재 제품 차별화의 가장 큰 공백은 해결책 품질이다.
- **구현 영향:** CSV variation은 M6 Pilot 준비 항목, Staging은 운영 Phase에서 다룬다.
- **재검토 Trigger:** 새 Roadmap이 변경될 때 재검토한다.
- **근거 문서:** `DECISION_REGISTER_V1.md`, `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-018 — External Context를 세 번째 우선순위로 둔 계획

- **상태:** `SUPERSEDED`
- **Category:** `ROADMAP`
- **결정:** External Context와 Pilot을 즉시 세 번째로 두던 순서는 새 Milestone 구조로 대체한다.
- **근거:** 원인 확정이 아닌 보조 정보이므로 내부 Decision Loop 이후가 적절하다.
- **구현 영향:** DR-013, DR-073의 순서를 따른다.
- **재검토 Trigger:** 없음.
- **근거 문서:** `DECISION_REGISTER_V1.md`, `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-019 — Recommendation 책임 분해

- **상태:** `ACCEPTED`
- **Category:** `ARCHITECTURE`
- **결정:** 단일 Recommendation Engine을 Decision Input, Cause Analysis, Strategy, Action Playbook, Experiment, Recommendation Package, Quality로 분리한다.
- **근거:** 현상·원인·대안·실행·측정 책임을 분리해야 일반 조언과 근거 왜곡을 막을 수 있다.
- **구현 영향:** 각 단계는 versioned contract와 별도 테스트 경계를 가진다.
- **재검토 Trigger:** 첫 vertical slice에서 경계가 과도하거나 누락됐다는 근거가 생기면 ADR로 변경한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`, `ARCHITECTURE_V2 candidate`

### DR-020 — 유료 가치의 기준은 Action Plan Package

- **상태:** `ACCEPTED`
- **Category:** `PRODUCT`
- **결정:** 고객에게 제공하는 핵심 결과는 진단, 대안, 선택 이유, 실행 단계, 비용, 실험, 성공·중단조건이 포함된 Action Plan Package다.
- **근거:** 아이디어나 문구만으로는 고객이 돈을 낼 실효성이 부족하다.
- **구현 영향:** 최종 UI와 품질 평가는 Package 완성도를 기준으로 한다.
- **재검토 Trigger:** Pilot 사용자 연구에서 다른 핵심 결과물이 더 중요하다는 근거가 생길 때 재검토한다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_PACKAGE_V2.md`

### DR-021 — 최소 대안 비교

- **상태:** `ACCEPTED`
- **Category:** `STRATEGY`
- **결정:** 최종 추천 전 최소 두 개 Strategy 후보를 비교하며, 단일 후보만 가능하면 구조화된 이유를 기록한다.
- **근거:** 하나의 아이디어를 바로 추천하면 경제성·운영·측정 측면의 더 나은 대안을 놓친다.
- **구현 영향:** 선택 전략은 2위, NO_ACTION, 비용-bearing이면 저비용 대안과 비교한다.
- **재검토 Trigger:** 특정 Package Type에서 대안 비교가 불필요하다는 명확한 근거가 있을 때만 예외를 versioning한다.
- **근거 문서:** `LOOFIO_STRATEGY_ENGINE_V1.md`, `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

### DR-022 — Versioned Playbook 우선

- **상태:** `ACCEPTED`
- **Category:** `PLAYBOOK`
- **결정:** LLM 자유 생성보다 versioned Action Playbook registry를 우선한다.
- **근거:** 적용 조건·금지 조건·비용·실험·정책을 재현하고 학습하려면 구조화된 실행 지식이 필요하다.
- **구현 영향:** AI는 Playbook을 표현·구체화할 수 있으나 canonical 실행 근거를 대신하지 않는다.
- **재검토 Trigger:** Playbook으로 표현하기 어려운 반복 사례가 누적되면 확장 메커니즘을 재검토한다.
- **근거 문서:** `LOOFIO_ACTION_PLAYBOOK_V1.md`

### DR-023 — 온라인·오프라인 통합 평가

- **상태:** `ACCEPTED`
- **Category:** `CHANNEL`
- **결정:** 온라인과 오프라인을 별도 제품으로 나누지 않고 병목, 비용, 실행 가능성, 추적 가능성 기준으로 함께 비교한다.
- **근거:** 현장 재예약·제휴·예약 경로·CRM은 같은 사업 문제를 해결하는 대안이다.
- **구현 영향:** Strategy는 채널보다 먼저 선택하고 Playbook이 채널 역할을 조합한다.
- **재검토 Trigger:** 새 Product packaging 결정이 생길 때 재검토한다.
- **근거 문서:** `LOOFIO_STRATEGY_ENGINE_V1.md`, `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-024 — 경제성 평가 범위

- **상태:** `ACCEPTED`
- **Category:** `ECONOMICS`
- **결정:** 가능한 경우 매출뿐 아니라 변동원가, 혜택원가, 매체비, 메시지비, 제휴비, 직원시간, 추가 서비스비를 포함한다.
- **근거:** 매출이 늘어도 비용을 빼면 손실일 수 있다.
- **구현 영향:** 경제성은 complete/partial/unknown/not_applicable/infeasible로 표시한다.
- **재검토 Trigger:** 업종별 비용 모델이 추가되면 versioned calculator로 확장한다.
- **근거 문서:** `LOOFIO_DECISION_INPUT_CONTRACT_V1.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-025 — 실행 전 Experiment 계약

- **상태:** `ACCEPTED`
- **Category:** `EXPERIMENT`
- **결정:** 실행 가능한 Playbook은 실행 전에 대상, 처리, 비교, Primary Metric, 기간, 성공조건, 중단조건, Tracking, Result Source를 고정한다.
- **근거:** 결과를 본 뒤 기준을 정하면 성과를 임의 해석하게 된다.
- **구현 영향:** RUNNING 이후 핵심 계약 변경은 새 Experiment version을 요구한다.
- **재검토 Trigger:** Diagnostic/Hold Type의 대체 계약을 제외하고 유지한다.
- **근거 문서:** `LOOFIO_EXPERIMENT_DESIGN_V1.md`

### DR-026 — Recommendation Quality Gate v1

- **상태:** `PROVISIONAL_V1`
- **Category:** `QUALITY`
- **결정:** v1 통과 기준은 Total Score 75 이상, Hard Fail 0, 모든 Section Floor 충족이다.
- **근거:** 구체성 하나가 근거·경제성·측정 부실을 가리지 못하게 해야 한다.
- **구현 영향:** Validator version을 저장하고 일반 조언·PII·unknown=0·Grade 과장을 차단한다.
- **재검토 Trigger:** 첫 Pilot 결과와 revision/acceptance 분포를 검토한 뒤 threshold·weight를 재조정한다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

### DR-027 — Legacy Recommendation을 fallback으로 유지

- **상태:** `ACCEPTED`
- **Category:** `COMPATIBILITY`
- **결정:** 현재 deterministic Recommendation Draft는 새 Package의 fallback과 baseline으로 유지한다.
- **근거:** 새 시스템 실패가 현재 제품 루프 전체를 중단하면 안 된다.
- **구현 영향:** Package→Legacy Adapter를 두고 기존 Decision·Action API를 유지한다.
- **재검토 Trigger:** Package 기반 Action이 운영에서 안정화되고 migration plan이 생기면 재검토한다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_PACKAGE_V2.md`

### DR-028 — AI 역할 경계

- **상태:** `ACCEPTED`
- **Category:** `AI`
- **결정:** AI는 설명, 가설 표현, 대안 비교 문장, 직원 스크립트와 콘텐츠 초안을 담당한다.
- **근거:** 수치·Score·경제성·실험 계약·Quality 판정은 deterministic이어야 한다.
- **구현 영향:** AI 출력은 source fidelity와 policy validator를 통과해야 한다.
- **재검토 Trigger:** AI 사용 범위를 확대하려면 별도 ADR과 eval evidence가 필요하다.
- **근거 문서:** `FUTURE: LOOFIO_AI_ARCHITECTURE_V2.md`, `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

### DR-029 — 현재 Measurement의 Evidence 해석

- **상태:** `ACCEPTED`
- **Category:** `MEASUREMENT`
- **결정:** 현재 prior-four-weeks 비교는 기본 Grade C이며, 조건이 약하면 D로 하향한다.
- **근거:** 동시 비교군과 운영·외부 조건 보정이 없기 때문이다.
- **구현 영향:** UI는 관찰 차이와 causal effect를 분리한다.
- **재검토 Trigger:** Method가 변경되면 새 version과 새 Measurement Run을 사용한다.
- **근거 문서:** `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-030 — 다음 구현 우선순위

- **상태:** `ACCEPTED`
- **Category:** `ROADMAP`
- **결정:** Decision Input→Cause→Strategy→Playbook→Experiment→Package/Quality→UI/Manual Action→AI 순으로 구현한다.
- **근거:** 모델 연결보다 좋은 해결책의 구조와 검증 기준을 먼저 고정해야 한다.
- **구현 영향:** Implementation Backlog M1~M7을 따른다.
- **재검토 Trigger:** Backlog의 의존성이나 Pilot 결과가 바뀔 때 재검토한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`, `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`

### DR-031 — DecisionField 상태·출처·신선도

- **상태:** `ACCEPTED`
- **Category:** `DECISION_INPUT`
- **결정:** 중요 입력은 값뿐 아니라 known/unknown/not_applicable/conflicting/stale/restricted와 source·observed_at을 가진다.
- **근거:** 값이 없는 이유와 신뢰도를 구분해야 안전한 전략 선택이 가능하다.
- **구현 영향:** Decision Context와 Missing Requirement는 이 공통 계약을 사용한다.
- **재검토 Trigger:** 운영에서 추가 상태가 반복적으로 필요할 때 minor version을 검토한다.
- **근거 문서:** `LOOFIO_DECISION_INPUT_CONTRACT_V1.md`

### DR-032 — Decision Readiness D0~D4

- **상태:** `PROVISIONAL_V1`
- **Category:** `DECISION_INPUT`
- **결정:** v1은 Opportunity-only D0부터 Economics-ready D4까지 5단계 Readiness를 사용한다.
- **근거:** 입력 수준에 따라 가능한 Cause·Strategy·Experiment·경제성 기능을 명확히 제한하기 위해서다.
- **구현 영향:** 같은 입력은 같은 Readiness와 blocked capability를 반환한다.
- **재검토 Trigger:** Pilot에서 단계가 과도하거나 부족한지 검토한다.
- **근거 문서:** `LOOFIO_DECISION_INPUT_CONTRACT_V1.md`

### DR-033 — Unknown은 0이 아님

- **상태:** `ACCEPTED`
- **Category:** `DATA_SEMANTICS`
- **결정:** 비용, capacity, consent, Tracking, 결과가 unknown인 상태를 0·false·없음으로 해석하지 않는다.
- **근거:** 잘못된 기본값은 유료 전략·순기여가치·실행 가능성을 왜곡한다.
- **구현 영향:** 계산기는 unknown을 전파하고 필요한 경우 NEEDS_DATA를 반환한다.
- **재검토 Trigger:** 예외를 허용하지 않는다. Not applicable은 별도 상태다.
- **근거 문서:** `LOOFIO_DECISION_INPUT_CONTRACT_V1.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-034 — Cause는 가설

- **상태:** `ACCEPTED`
- **Category:** `CAUSE`
- **결정:** Cause Candidate는 검토 대상 가설이며 사실·인과관계·확률로 표현하지 않는다.
- **근거:** 현재 내부 데이터만으로 근본 원인을 확정할 수 없는 경우가 많다.
- **구현 영향:** Supporting, Contradicting, Missing Data, Diagnostic Question을 함께 반환한다.
- **재검토 Trigger:** 강한 causal model이 추가돼도 별도 의미와 version으로 구분한다.
- **근거 문서:** `LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md`

### DR-035 — Data Quality를 선행 Cause로 검토

- **상태:** `ACCEPTED`
- **Category:** `CAUSE`
- **결정:** DATA_QUALITY_ARTIFACT는 모든 Opportunity에서 먼저 검토하며 critical conflict는 사업 Cause rank를 차단한다.
- **근거:** 시간대·상태·매핑·중복 오류를 사업 문제로 오판하면 잘못된 실행을 낳는다.
- **구현 영향:** Critical conflict 시 BLOCKED_BY_DATA_QUALITY와 구체적 correction plan을 반환한다.
- **재검토 Trigger:** Import/lineage 구조가 바뀌면 DataQualityContext를 갱신한다.
- **근거 문서:** `LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md`, `LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md`

### DR-036 — Cause Priority Score v1

- **상태:** `PROVISIONAL_V1`
- **Category:** `CAUSE`
- **결정:** Cause 검토 우선순위는 Evidence 35, Pattern 20, Completeness 20, Contradiction Absence 15, Testability 10으로 계산한다.
- **근거:** Actionability를 Cause 단계에서 제거해 해결하기 쉬운 가설이 근거보다 높아지는 것을 막는다.
- **구현 영향:** Required 입력이 없으면 score는 null이며 확률로 표시하지 않는다.
- **재검토 Trigger:** 첫 Cause fixture와 Pilot 진단 일치율을 본 뒤 weight를 재검토한다.
- **근거 문서:** `LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md`

### DR-037 — Strategy Hard Gate가 Score보다 우선

- **상태:** `ACCEPTED`
- **Category:** `STRATEGY`
- **결정:** Data Quality, capacity, Offering, policy/consent, Tracking/Measurement, economics Gate를 통과한 실행 전략만 Score를 받는다.
- **근거:** 높은 Opportunity Estimate가 실행 불가능하거나 위험한 전략을 우선시키면 안 된다.
- **구현 영향:** Blocked/Needs Data/Policy/Infeasible 상태를 score null로 유지한다.
- **재검토 Trigger:** Gate 순서를 바꾸려면 안전·경제성 영향 검토가 필요하다.
- **근거 문서:** `LOOFIO_STRATEGY_ENGINE_V1.md`

### DR-038 — DATA_COLLECTION과 NO_ACTION은 정상 전략

- **상태:** `ACCEPTED`
- **Category:** `STRATEGY`
- **결정:** 부족한 입력을 보완하는 DATA_COLLECTION과 실행을 보류하는 NO_ACTION을 정상 결과로 허용한다.
- **근거:** 항상 광고·할인·연락을 권하는 것은 경제적이지도 안전하지도 않다.
- **구현 영향:** 두 전략은 실행 Strategy Score와 같은 방식으로 단순 비교하지 않는다.
- **재검토 Trigger:** 제품이 모든 경우 Action을 강제해야 한다는 전략 변경 시 재검토한다.
- **근거 문서:** `LOOFIO_STRATEGY_ENGINE_V1.md`

### DR-039 — Strategy Priority Score v1

- **상태:** `PROVISIONAL_V1`
- **Category:** `STRATEGY`
- **결정:** v1은 Net Value 25, Evidence Fit 20, Operational 15, Measurement 15, Policy 10, Time to Learning 10, Learning Value 5를 사용하고 최소 65점·1/2위 5점 gap을 적용한다.
- **근거:** 경제성·근거·운영·측정을 균형 있게 비교하기 위한 초기 규칙이다.
- **구현 영향:** 점수는 성공확률이 아니며 eligible 실행·운영 전략에만 적용한다.
- **재검토 Trigger:** Pilot의 선택·수정·결과 데이터를 기반으로 재조정한다.
- **근거 문서:** `LOOFIO_STRATEGY_ENGINE_V1.md`

### DR-040 — Paid Acquisition의 높은 준비도 요구

- **상태:** `ACCEPTED`
- **Category:** `STRATEGY`
- **결정:** 유료 신규 획득은 외부 수요 근거, capacity, Offering, D4 경제성, 예산 상한, Tracking, Result Source, 정책 승인을 요구한다.
- **근거:** 수요 자체가 없거나 funnel이 고장난 상태에서 광고비를 쓰는 것을 막아야 한다.
- **구현 영향:** 조건 미충족 시 NEEDS_DATA, INFEASIBLE 또는 저비용 대안을 선택한다.
- **재검토 Trigger:** 첫 paid channel Pilot 전에 Provider-specific 조건을 추가한다.
- **근거 문서:** `LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md`, `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-041 — Playbook 3계층 모델

- **상태:** `ACCEPTED`
- **Category:** `PLAYBOOK`
- **결정:** PlaybookDefinition, PlaybookApplicabilityResult, PlaybookInstance를 분리한다.
- **근거:** 공통 실행 지식과 사업장 runtime 값을 섞으면 재사용·감사·versioning이 어렵다.
- **구현 영향:** Definition에는 tenant/customer/runtime budget을 저장하지 않는다.
- **재검토 Trigger:** Registry 관리 방식이 DB로 바뀌어도 세 계층 의미는 유지한다.
- **근거 문서:** `LOOFIO_ACTION_PLAYBOOK_V1.md`

### DR-042 — Canonical Playbook ID

- **상태:** `ACCEPTED`
- **Category:** `PLAYBOOK`
- **결정:** 설명형 canonical ID와 version을 정식 key로 사용하고 PB-01~PB-10은 legacy alias로만 유지한다.
- **근거:** 숫자 alias는 의미와 확장성을 설명하지 못한다.
- **구현 영향:** 신규 API·DB·코드는 canonical ID만 사용한다.
- **재검토 Trigger:** ID scheme 변경은 migration과 alias 보존을 요구한다.
- **근거 문서:** `LOOFIO_ACTION_PLAYBOOK_V1.md`, `LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md`

### DR-043 — Playbook Lifecycle

- **상태:** `PROVISIONAL_V1`
- **Category:** `PLAYBOOK`
- **결정:** Playbook은 DRAFT→VALIDATED_INTERNAL→PILOT→ACTIVE 흐름과 BLOCKED/DEPRECATED 상태를 사용한다.
- **근거:** 문서 작성, 내부 검증, 실제 Pilot, 운영 활성은 서로 다른 성숙도다.
- **구현 영향:** 현재 Core 12개는 모두 DRAFT다.
- **재검토 Trigger:** 정량 승격 기준은 DR-078이 해결될 때 versioned 정책으로 보완한다.
- **근거 문서:** `LOOFIO_ACTION_PLAYBOOK_V1.md`

### DR-044 — Hospital Core Playbook 12개

- **상태:** `ACCEPTED`
- **Category:** `PLAYBOOK`
- **결정:** LOW_DEMAND_SLOT 첫 범위에서 데이터 품질, Tracking, capacity, Offering 재배치, 예약 가용성, 재방문 cohort, Front Desk, 예약 가시성, funnel, 비가격 가치, 지역 제휴, NO_ACTION의 12개 Core Playbook을 상세화한다.
- **근거:** 마케팅·운영·진단·보류를 함께 검증하기 위한 최소 카탈로그다.
- **구현 영향:** Core는 DRAFT로 구현하고 Expansion Playbook은 자동 선택하지 않는다.
- **재검토 Trigger:** Pilot 결과와 Opportunity 확장에 따라 Catalog version을 추가한다.
- **근거 문서:** `LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md`

### DR-045 — Experiment 5계층 모델

- **상태:** `ACCEPTED`
- **Category:** `EXPERIMENT`
- **결정:** ExperimentTemplate, Definition, Run, Result, Evaluation을 분리한다.
- **근거:** 템플릿, 승인된 계약, 실제 운영, 수집 결과, 해석은 서로 다른 책임이다.
- **구현 영향:** 각 계층은 version과 source reference를 가진다.
- **재검토 Trigger:** 통계 엔진을 추가해도 계층 분리는 유지한다.
- **근거 문서:** `LOOFIO_EXPERIMENT_DESIGN_V1.md`

### DR-046 — 실행 후 Experiment 핵심 계약 불변

- **상태:** `ACCEPTED`
- **Category:** `EXPERIMENT`
- **결정:** RUNNING 이후 가설, assignment, treatment, comparison, Primary Metric, success/stop, attribution, budget cap을 수정하지 않는다.
- **근거:** 결과를 본 뒤 기준을 바꾸는 것을 방지한다.
- **구현 영향:** 변경이 필요하면 기존 Experiment를 중단·무효화하고 새 version을 만든다.
- **재검토 Trigger:** 예외 없음. 운영 metadata만 추가 가능하다.
- **근거 문서:** `LOOFIO_EXPERIMENT_DESIGN_V1.md`

### DR-047 — Evidence Grade와 Precision 분리

- **상태:** `ACCEPTED`
- **Category:** `EXPERIMENT`
- **결정:** Evidence Grade는 설계 강도, Precision은 표본과 결과 정밀도를 나타내며 별도로 관리한다.
- **근거:** 무작위 설계라도 표본이 작으면 결론이 불충분할 수 있다.
- **구현 영향:** Grade A + Precision LOW + INCONCLUSIVE를 허용한다.
- **재검토 Trigger:** 통계 method v2가 추가돼도 의미 분리는 유지한다.
- **근거 문서:** `LOOFIO_EXPERIMENT_DESIGN_V1.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-048 — 현재 Measurement의 Experiment fallback 위치

- **상태:** `ACCEPTED`
- **Category:** `EXPERIMENT`
- **결정:** same-window-prior-four-weeks-v2는 Matched Historical Grade C 또는 Before/After Grade D fallback으로만 사용한다.
- **근거:** 현재 구현을 보존하면서 더 강한 Method와 의미를 구분하기 위해서다.
- **구현 영향:** Grade A/B Treatment-Control 계산을 대체하지 않는다.
- **재검토 Trigger:** 현재 Measurement 공식이 변경되면 새 version으로 재검토한다.
- **근거 문서:** `LOOFIO_PLAYBOOK_EXPERIMENT_MAPPING_V1.md`

### DR-049 — Recommendation Package Type 4개

- **상태:** `ACCEPTED`
- **Category:** `RECOMMENDATION`
- **결정:** Package는 EXECUTION, OPERATIONAL, DIAGNOSTIC, HOLD로 구분한다.
- **근거:** 모든 유효 결과가 마케팅 실행은 아니며 Type별 필수 계약이 다르다.
- **구현 영향:** 각 Type은 빈 Section 대신 맞는 대체 계약을 가져야 한다.
- **재검토 Trigger:** 새 Strategy Class가 생기면 Type 확장을 검토한다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_PACKAGE_V2.md`

### DR-050 — Package Revision은 불변 기록

- **상태:** `ACCEPTED`
- **Category:** `RECOMMENDATION`
- **결정:** 사용자 수정은 기존 Package를 덮어쓰지 않고 새 revision을 만들며 기존 revision은 SUPERSEDED된다.
- **근거:** 어떤 근거와 계획을 승인했는지 감사 가능해야 한다.
- **구현 영향:** 영향받는 downstream을 재조립하고 Quality를 다시 평가한다.
- **재검토 Trigger:** 불변 versioning 정책을 바꾸려면 Data Schema/API migration이 필요하다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_PACKAGE_V2.md`

### DR-051 — Quality Hard Fail 수동 Override 금지

- **상태:** `ACCEPTED`
- **Category:** `QUALITY`
- **결정:** 일반 사용자와 관리자는 Hard Fail을 강제로 PASSED로 바꿀 수 없다.
- **근거:** PII·정책·Tracking·경제성·실험 무결성을 점수나 권한으로 우회하면 안 된다.
- **구현 영향:** 입력·Strategy·Playbook·Experiment를 수정하고 새 revision을 평가한다.
- **재검토 Trigger:** 법적 예외가 필요하면 Governance/ADR/새 정책 version을 거친다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

### DR-052 — Legacy API를 additive하게 유지

- **상태:** `ACCEPTED`
- **Category:** `API`
- **결정:** 현재 /recommendations/draft, Decision, Manual Action, Result, Measurement 계약을 즉시 제거하지 않는다.
- **근거:** 현재 제품 루프와 회귀 테스트를 유지하며 점진적으로 전환해야 한다.
- **구현 영향:** 신규 Preview와 Package API는 additive하게 추가한다.
- **재검토 Trigger:** legacy 제거는 실제 사용·migration·deprecation plan이 준비될 때 별도 결정한다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_PACKAGE_V2.md`, `LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md 예정`

### DR-053 — Measurement 의미 계층 분리

- **상태:** `ACCEPTED`
- **Category:** `MEASUREMENT`
- **결정:** Actual Result, Opportunity Estimate, Baseline, Observed Delta, Attributed Result, Incremental Estimate, Net Contribution Estimate를 분리한다.
- **근거:** 서로 다른 값을 같은 '성과'로 표시하면 효과를 과장하게 된다.
- **구현 영향:** API·DB·UI는 별도 field와 label을 사용한다.
- **재검토 Trigger:** 새 causal method가 추가돼도 기존 의미를 덮어쓰지 않는다.
- **근거 문서:** `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-054 — Net Contribution 계산 조건

- **상태:** `ACCEPTED`
- **Category:** `ECONOMICS`
- **결정:** 주요 비용이 complete 또는 not_applicable일 때만 Net Contribution을 계산한다.
- **근거:** 비용 누락을 0으로 처리하면 경제성을 과장한다.
- **구현 영향:** 비용이 partial이면 revenue-only 또는 제한적 incremental revenue까지만 표시한다.
- **재검토 Trigger:** 업종별 비용 구성요소가 추가되면 calculator version을 갱신한다.
- **근거 문서:** `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-055 — Displacement와 Cannibalization 검토

- **상태:** `ACCEPTED`
- **Category:** `MEASUREMENT`
- **결정:** 목표 슬롯·Offering 성과와 함께 다른 슬롯·Offering·전체 사업 결과를 검토한다.
- **근거:** 예약 시간을 옮긴 것을 신규 매출로 중복 계산할 수 있다.
- **구현 영향:** Target Segment Delta와 Business Total Delta를 함께 표시한다.
- **재검토 Trigger:** 새 Attribution model이 추가돼도 displacement 검토는 유지한다.
- **근거 문서:** `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-056 — Channel Execution 수준 5개

- **상태:** `ACCEPTED`
- **Category:** `EXECUTION`
- **결정:** MANUAL, COPY_EXPORT, STAFF_OPERATED, APPROVED_CONNECTOR, BOUNDED_AUTOMATION을 구분한다.
- **근거:** 사람이 실행하는 것과 외부 API·자동화를 같은 기능으로 취급하면 승인·Retry·비용·보안 경계가 흐려진다.
- **구현 영향:** 각 수준은 capability와 정책 상태를 별도로 가진다.
- **재검토 Trigger:** 실행 수준을 추가할 때 별도 version을 사용한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-057 — 첫 vertical slice 실행 수준

- **상태:** `ACCEPTED`
- **Category:** `EXECUTION`
- **결정:** 첫 slice는 MANUAL, COPY_EXPORT, STAFF_OPERATED까지만 구현한다.
- **근거:** 현재 Action 구조와 호환되고 자동 외부 부작용을 만들지 않기 때문이다.
- **구현 영향:** APPROVED_CONNECTOR는 Provider Pilot 이후로 미룬다.
- **재검토 Trigger:** M7 Manual Pilot 완료 후 재검토한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`, `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`

### DR-058 — Action과 Execution 분리

- **상태:** `ACCEPTED`
- **Category:** `EXECUTION`
- **결정:** Action은 승인된 사업 실행 계획이고 Execution Package/Attempt/Event는 실제 채널 전달 상태다.
- **근거:** 계획 완료와 메시지 전달·직원 작업·부분 실패는 같은 상태가 아니다.
- **구현 영향:** 현재 Action 상태는 유지하고 Execution 상태를 additive하게 추가한다.
- **재검토 Trigger:** legacy Action 모델을 제거할 때 migration과 함께 재검토한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-059 — 실행형 Package Tracking 필수

- **상태:** `ACCEPTED`
- **Category:** `EXECUTION`
- **결정:** 모든 실행형 Package는 ACTION_ID, URL, source code, partner code, QR, provider ID 등 최소 하나의 검증된 Tracking을 가진다.
- **근거:** 추적 없는 행동은 결과·비용·학습과 연결할 수 없다.
- **구현 영향:** Tracking test event가 검증되기 전 실행 준비 완료가 아니다.
- **재검토 Trigger:** Diagnostic/Hold의 대체 Metric 계약만 예외다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-060 — Approval Scope Hash

- **상태:** `PROVISIONAL_V1`
- **Category:** `EXECUTION`
- **결정:** 승인은 대상, Asset, 채널, 기간, 예산, Tracking, Experiment, Provider 계정의 Hash에 귀속한다.
- **근거:** 승인 후 범위가 바뀌면 기존 승인이 유효하지 않다.
- **구현 영향:** Hash 변경 시 재승인을 요구한다.
- **재검토 Trigger:** 구현 복잡도와 운영 UX를 첫 Staff/Copy Export Pilot에서 검토한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-061 — Idempotency·Retry·Cancel 명시

- **상태:** `ACCEPTED`
- **Category:** `EXECUTION`
- **결정:** 중복 실행을 막는 Idempotency, bounded Retry, verify-before-retry, 취소·회수 가능 범위를 계약에 포함한다.
- **근거:** Timeout과 재시도는 중복 메시지·광고·Task를 만들 수 있다.
- **구현 영향:** Manual Task와 Connector 모두 logical key와 Attempt/Event를 가진다.
- **재검토 Trigger:** Provider-specific 정책은 Connector Adapter에서 확장한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-062 — Provider-neutral Connector Port

- **상태:** `ACCEPTED`
- **Category:** `ARCHITECTURE`
- **결정:** 외부 Provider는 validate, preview, execute, status, cancel, cost, events Port 뒤에 둔다.
- **근거:** Core Strategy·Playbook·Measurement를 특정 SDK에 묶지 않기 위해서다.
- **구현 영향:** Connector는 전략·Target 이유·Budget Policy·Measurement 해석을 결정하지 않는다.
- **재검토 Trigger:** 첫 Provider를 선택해도 Port 경계는 유지한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`, `DEPENDENCY_RULES.md`

### DR-063 — Hospital PII·임상 Targeting 금지

- **상태:** `ACCEPTED`
- **Category:** `PRIVACY`
- **결정:** 환자 이름, 연락처 원문, 주민번호, 진단, 질병·증상, 처방, 검사, 의무기록, 상담 원문을 Package·AI·Tracking 값에 넣지 않는다.
- **근거:** 의료정보는 높은 민감도와 오남용 위험을 가진다.
- **구현 영향:** 분석은 aggregate 또는 tokenized internal cohort를 사용하고 임상 Targeting을 금지한다.
- **재검토 Trigger:** 법·동의·보안 구조가 바뀌어도 별도 Privacy/Legal 결정 없이는 유지한다.
- **근거 문서:** `LOOFIO_DECISION_INPUT_CONTRACT_V1.md`, `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-064 — 외부 실행 전 명시적 사용자 승인

- **상태:** `ACCEPTED`
- **Category:** `EXECUTION`
- **결정:** 외부 메시지·광고·게시·혜택·제휴·설정 변경은 Package version과 범위에 대한 명시적 승인 후에만 가능하다.
- **근거:** 비용과 고객 접점이 발생하는 부작용을 사용자 통제 아래 둬야 한다.
- **구현 영향:** 현재 Manual Action도 승인된 Recommendation에서만 생성하는 규칙을 유지한다.
- **재검토 Trigger:** Bounded Automation 도입 시 별도 opt-in 정책을 추가한다.
- **근거 문서:** `CURRENT_IMPLEMENTATION_STATUS.md`, `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-065 — Bounded Automation 도입 조건

- **상태:** `DEFERRED`
- **Category:** `EXECUTION`
- **결정:** 자동 실행은 per-business opt-in, hard budget/volume/risk limits, kill switch, alert, audit, cancel, incident runbook을 갖춘 별도 Phase로 미룬다.
- **근거:** 현재는 자동화의 안전·운영 기반이 없다.
- **구현 영향:** MVP UI에서 자동 실행 기능처럼 표시하지 않는다.
- **재검토 Trigger:** Approved Connector Pilot과 운영 사고 대응이 검증된 후 재검토한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-066 — External Context는 보조 Evidence

- **상태:** `ACCEPTED`
- **Category:** `EXTERNAL_CONTEXT`
- **결정:** 날씨·공휴일·행사·유동정보는 Cause 확정이 아니라 가설 보조와 비교 가능성 limitation으로 사용한다.
- **근거:** 외부 상관관계를 인과관계로 오해하면 잘못된 설명이 된다.
- **구현 영향:** Internal Business Data가 우선이며 Provider 실패가 Detector를 실패시키지 않는다.
- **재검토 Trigger:** 향후 causal context model이 생기면 별도 Method로 확장한다.
- **근거 문서:** `LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-067 — Persistence 구현 시점

- **상태:** `ACCEPTED`
- **Category:** `DATA_MODEL`
- **결정:** Decision Intelligence Persistence는 전용 Data Schema와 API Contract 문서가 확정된 뒤 구현한다.
- **근거:** 현재 상세 문서에 흩어진 후보 테이블을 바로 migration으로 옮기면 중복·호환 문제를 만들 수 있다.
- **구현 영향:** 그 전에는 Pure Domain, Pydantic, Static Registry, In-memory Resolver, Preview API를 구현한다.
- **재검토 Trigger:** 두 기술 계약이 완료되면 Backlog AFTER_SCHEMA_API를 해제한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`, `00_PLANNING_INDEX.md`

### DR-068 — Preview-first API

- **상태:** `ACCEPTED`
- **Category:** `API`
- **결정:** 각 새 계층은 저장·외부 실행 없는 deterministic Preview API로 먼저 검증한다.
- **근거:** 계약과 품질을 검증한 뒤 Persistence·부작용을 추가하는 것이 안전하다.
- **구현 영향:** Cause, Strategy, Playbook, Experiment, Package, Execution, Measurement에 Preview 경로를 둔다.
- **재검토 Trigger:** Preview가 성능·운영 요구를 충족하지 못할 때 API 문서에서 조정한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`

### DR-069 — 구현 Source of Truth 순서

- **상태:** `ACCEPTED`
- **Category:** `GOVERNANCE`
- **결정:** 구현 여부는 migration→code→tests→CURRENT_IMPLEMENTATION_STATUS→API Contract→목표 설계 순으로 판단한다.
- **근거:** 기획 문서가 코드보다 앞서기 때문에 문서만으로 구현을 주장하면 안 된다.
- **구현 영향:** 상태 문서는 code_baseline_commit과 document_alignment_commit을 분리한다.
- **재검토 Trigger:** Repository 구조가 바뀌면 Planning Index에서 갱신한다.
- **근거 문서:** `00_PLANNING_INDEX.md`

### DR-070 — Planning Index를 문서 단일 진입점으로 사용

- **상태:** `ACCEPTED`
- **Category:** `GOVERNANCE`
- **결정:** docs/00_PLANNING_INDEX.md를 문서 읽기 순서·상태·Source of Truth의 단일 진입점으로 사용한다.
- **근거:** 문서 수가 많아져 현재·목표·미구현을 구분하기 어렵다.
- **구현 영향:** docs/README는 인덱스를 가리키는 짧은 안내로 축소한다.
- **재검토 Trigger:** 문서 구조가 폴더 기반으로 재편되면 인덱스를 갱신한다.
- **근거 문서:** `00_PLANNING_INDEX.md`

### DR-071 — 첫 vertical slice 범위

- **상태:** `ACCEPTED`
- **Category:** `SCOPE`
- **결정:** 첫 구현은 Hospital LOW_DEMAND_SLOT의 Decision Context→Cause→Strategy→Playbook→Experiment→Package/Quality→기존 Manual Action→Current Measurement Adapter다.
- **근거:** 하나의 end-to-end 경로로 계약과 품질을 검증해야 한다.
- **구현 영향:** LLM, External Context, 실제 Connector, 다른 Opportunity, 다른 Archetype은 제외한다.
- **재검토 Trigger:** M6/M7 Gate 통과 후 다음 범위를 결정한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`

### DR-072 — AI Architecture 구현 시점

- **상태:** `DEFERRED`
- **Category:** `AI`
- **결정:** AI Gateway·Provider·LLM 설명은 deterministic Recommendation Package가 안정된 이후로 미룬다.
- **근거:** AI가 구조를 대신 만들면 일반 조언과 근거 왜곡이 재발한다.
- **구현 영향:** M5 이후 wording/content task로 연결한다.
- **재검토 Trigger:** M5 Gate 통과 시 DR-011과 함께 재검토한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-073 — External Context 구현 시점

- **상태:** `DEFERRED`
- **Category:** `EXTERNAL_CONTEXT`
- **결정:** External Context는 M7 이후 Cause 보조와 Measurement limitation부터 연결한다.
- **근거:** 내부 데이터 계약과 실행·측정 경로가 먼저다.
- **구현 영향:** Detector의 필수 runtime dependency로 만들지 않는다.
- **재검토 Trigger:** M7 완료 후 첫 Provider를 결정한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-074 — 다른 Opportunity 확장

- **상태:** `DEFERRED`
- **Category:** `SCOPE`
- **결정:** CANCELLATION_HOTSPOT, DORMANT_CUSTOMER, SERVICE_DEMAND_GAP의 Decision Intelligence 상세화는 LOW_DEMAND_SLOT 이후로 미룬다.
- **근거:** 공통 계층을 한 유형에서 검증한 뒤 확장하는 것이 효율적이다.
- **구현 영향:** 현재 Detector와 legacy Recommendation은 유지한다.
- **재검토 Trigger:** 첫 vertical slice Gate 통과 후 우선순위를 정한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-075 — 다른 Archetype 확장

- **상태:** `DEFERRED`
- **Category:** `SCOPE`
- **결정:** Appointment Personal, Membership Fitness, Field Maintenance, Walk-in Commerce 확장은 Hospital 검증 이후로 미룬다.
- **근거:** Decision Input·Cause·Playbook·Policy가 업종별로 달라진다.
- **구현 영향:** Business Taxonomy와 Adapter 구조만 유지한다.
- **재검토 Trigger:** Hospital Pilot에서 공통 계약 재사용성이 확인되면 재검토한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`, `LOOFIO_BUSINESS_TAXONOMY_V1.md`

### DR-076 — 첫 실제 Playbook Pilot

- **상태:** `OPEN`
- **Category:** `PILOT`
- **결정:** 첫 실제 Pilot Playbook은 아직 확정하지 않는다. PB_LOW_DEMAND_REVISIT_COHORT_V1이 주요 후보지만 consent·cohort·Tracking 조건을 먼저 확인한다.
- **근거:** 데이터 준비도에 따라 Capacity Review나 Data Audit가 첫 Pilot이 될 수 있다.
- **구현 영향:** Pilot 대상 사업장의 D0~D4 결과를 보고 선택한다.
- **재검토 Trigger:** 첫 3~5개 후보 사업장의 Decision Context 진단 후 결정한다.
- **근거 문서:** `LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md`

### DR-077 — Quality Score 재보정

- **상태:** `OPEN`
- **Category:** `QUALITY`
- **결정:** 75점·weights·Section Floor는 v1 구현 기준이나 Pilot 후 유지 여부는 미결정이다.
- **근거:** 현재는 전문가 설계 기준이며 실제 승인·수정·실행·결과 분포가 없다.
- **구현 영향:** Validator version을 유지한 채 Pilot 데이터로 새 version을 검토한다.
- **재검토 Trigger:** 최소 Pilot Package·revision·decision 데이터가 쌓인 뒤 결정한다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

### DR-078 — Playbook ACTIVE 정량 승격 기준

- **상태:** `OPEN`
- **Category:** `PLAYBOOK`
- **결정:** ACTIVE 승격에 필요한 최소 실행 횟수·결과 연결률·정책 incident 상한은 아직 결정하지 않는다.
- **근거:** 현재 근거 없이 임계값을 고정하면 형식적인 운영 기준이 된다.
- **구현 영향:** v1에서는 qualitative Gate와 owner 승인만 정의한다.
- **재검토 Trigger:** VALIDATED_INTERNAL/PILOT 실제 운영 데이터가 생긴 뒤 결정한다.
- **근거 문서:** `LOOFIO_ACTION_PLAYBOOK_V1.md`

### DR-079 — Grade A/B 통계·Power 방법

- **상태:** `OPEN`
- **Category:** `MEASUREMENT`
- **결정:** 자동 표본수, 신뢰구간, 통계 검정, cluster correction의 정식 Method는 아직 결정하지 않는다.
- **근거:** 현재는 운영 가이드와 Precision 상태만 정의돼 있다.
- **구현 영향:** v1에서 Grade와 Precision을 분리하고 과장 표현을 금지한다.
- **재검토 Trigger:** 실제 Experiment Result 분포와 필요 정확도를 확인한 뒤 통계 ADR을 작성한다.
- **근거 문서:** `LOOFIO_EXPERIMENT_DESIGN_V1.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-080 — 데이터 보존·삭제·법적 기간

- **상태:** `OPEN`
- **Category:** `PRIVACY`
- **결정:** Execution Event, tokenized assignment, direct-contact export, raw webhook, AI log의 정확한 보존 기간은 아직 결정하지 않는다.
- **근거:** 법적·보안·Provider·사업 운영 요구를 함께 검토해야 한다.
- **구현 영향:** 현재는 최소화·목적 제한·Export 단기 만료·Secret 분리를 원칙으로 한다.
- **재검토 Trigger:** 직접 고객 접촉·Connector·AI 저장 기능 전에 확정한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-081 — 첫 Approved Connector·채널

- **상태:** `OPEN`
- **Category:** `CONNECTOR`
- **결정:** 첫 실제 Connector와 Provider는 아직 결정하지 않는다.
- **근거:** Kakao/SMS/Email/Booking/Ads는 동의·비용·API·취소·결과 Event 특성이 다르다.
- **구현 영향:** MVP는 manual/copy/staff로 유지한다.
- **재검토 Trigger:** M7 완료 후 Pilot 가치·정책·API 안정성 기준으로 선택한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-082 — Production 플랫폼 구성

- **상태:** `OPEN`
- **Category:** `PLATFORM`
- **결정:** Cloud hosting, managed DB, queue/cache, monitoring, error tracking, Secret Manager, backup/restore 제품은 미결정이다.
- **근거:** 현재는 공급자 독립 운영 계약만 있다.
- **구현 영향:** Core 문서에서 특정 Vendor를 가정하지 않는다.
- **재검토 Trigger:** Staging/Production ADR에서 결정한다.
- **근거 문서:** `DEPLOYMENT_FLOW.md`

### DR-083 — AI 입력·출력·Prompt Log 보존 정책

- **상태:** `OPEN`
- **Category:** `AI_PRIVACY`
- **결정:** AI request의 전체 입력·출력·Prompt를 어느 범위와 기간으로 저장할지 아직 결정하지 않는다.
- **근거:** 감사·평가와 민감정보 최소화가 충돌할 수 있다.
- **구현 영향:** v1은 input hash, version, tokens, cost, status 중심을 우선한다.
- **재검토 Trigger:** 첫 AI Provider 연결 전에 Privacy/Security 결정이 필요하다.
- **근거 문서:** `FUTURE: LOOFIO_AI_ARCHITECTURE_V2.md`

### DR-084 — 초기 Pilot 사업장 규모

- **상태:** `PROVISIONAL_V1`
- **Category:** `PILOT`
- **결정:** 초기 Pilot 후보는 3~5개 사업장을 목표로 한다.
- **근거:** 운영 관찰이 가능하면서도 서로 다른 데이터 품질·업무 제약을 비교하기 위한 임시 범위다.
- **구현 영향:** 동일 Domain과 충분한 데이터 준비도를 우선한다.
- **재검토 Trigger:** 모집 가능성·지원 부담·분석 기간을 보고 변경한다.
- **근거 문서:** `LOOFIO_IMPLEMENTATION_ROADMAP_V2.md`

### DR-085 — 직원 시간 비용의 기본값

- **상태:** `ACCEPTED`
- **Category:** `ECONOMICS`
- **결정:** v1은 직원 시간 비용의 임의 기본값을 두지 않고 unknown 또는 사용자 제공 값으로 처리한다.
- **근거:** 일률적 기본 시급은 사업장·역할·업무 부담을 왜곡한다.
- **구현 영향:** 비용이 없으면 경제성 partial과 limitation을 유지한다.
- **재검토 Trigger:** 업종별 검증된 비용 모델이 생기면 별도 version으로 검토한다.
- **근거 문서:** `LOOFIO_DECISION_INPUT_CONTRACT_V1.md`, `LOOFIO_MEASUREMENT_FRAMEWORK_V1.md`

### DR-086 — 직접 연락처 Export 기본 금지

- **상태:** `REJECTED`
- **Category:** `PRIVACY`
- **결정:** 환자·고객 연락처 원문을 기본 Export 기능으로 제공하지 않는다.
- **근거:** 유출·오남용·장기 보존 위험이 크다.
- **구현 영향:** 외부 적법한 CRM이 Target 조건을 처리하거나 최소 reference·단기 만료 계약을 사용한다.
- **재검토 Trigger:** 법·동의·보안 검토가 완료된 특수 Connector 외에는 유지한다.
- **근거 문서:** `LOOFIO_CHANNEL_EXECUTION_V1.md`

### DR-087 — Quality Hard Fail 관리자 우회

- **상태:** `REJECTED`
- **Category:** `QUALITY`
- **결정:** 관리자 권한으로 Hard Fail을 직접 PASSED로 바꾸는 기능을 만들지 않는다.
- **근거:** 정책·보안·실험 무결성이 권한에 의해 무력화될 수 있다.
- **구현 영향:** 새 Package revision과 재검증만 허용한다.
- **재검토 Trigger:** Governance/Legal 예외 절차가 별도 설계되기 전까지 유지한다.
- **근거 문서:** `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

### DR-088 — 자유형 AI 전략을 Source of Truth로 사용

- **상태:** `REJECTED`
- **Category:** `AI`
- **결정:** LLM이 Raw Data를 읽고 Cause·Strategy·Playbook·경제성·성공조건을 자유롭게 생성한 결과를 Source of Truth로 사용하지 않는다.
- **근거:** 재현·근거·정책·비용·측정 계약이 보장되지 않는다.
- **구현 영향:** AI는 versioned deterministic 입력을 설명·표현하는 계층으로 제한한다.
- **재검토 Trigger:** 충분한 eval과 새 아키텍처 결정 없이는 유지한다.
- **근거 문서:** `AGENTS.md`, `LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md`

## 8. Open Decision Gate

다음 결정은 아직 열려 있으며, 표시된 단계 전에는 반드시 확정해야 한다.

| ID | 결정 | 늦어도 결정할 시점 | 현재 구현에서의 처리 |
|---|---|---|---|
| `DR-011` | 첫 AI Provider | M5 이후 AI Epic 시작 전 | Provider-neutral interface만 구현 |
| `DR-012` | Production 배포 Provider | Staging 설계 전 | Local/CI와 공급자 독립 계약 유지 |
| `DR-076` | 첫 실제 Playbook Pilot | 첫 실제 Pilot 사업장 진단 후 | Playbook은 모두 DRAFT |
| `DR-077` | Quality Score 재보정 | 첫 Pilot Package 결과 후 | quality-v1 고정 |
| `DR-078` | Playbook ACTIVE 정량 승격 기준 | Playbook ACTIVE 승격 전 | DRAFT/VALIDATED/PILOT까지만 |
| `DR-079` | Grade A/B 통계·Power 방법 | Grade A/B production Measurement 전 | Precision rule v1 사용 |
| `DR-080` | 데이터 보존·삭제·법적 기간 | 직접 접촉·Export·Connector 전 | 최소화·단기 만료 원칙 |
| `DR-081` | 첫 Approved Connector·채널 | M9 Connector Pilot 전 | Manual/Copy/Staff만 |
| `DR-082` | Production 플랫폼 구성 | Staging/Production 전 | Provider 미고정 |
| `DR-083` | AI 입력·출력·Prompt Log 보존 정책 | 첫 AI Provider 연결 전 | Hash/metadata 중심 로그 |

## 9. Superseded / Rejected Decisions

### Superseded

- `DR-003` 초기 제품 루프 — 초기 루프는 Opportunity→Recommendation→Decision→Action→Result→Measurement로 정의됐다.
- `DR-016` AI Recommendation을 다음 1순위로 둔 계획 — Recommendation Engine과 AI Architecture를 즉시 다음 우선순위로 두던 계획은 폐기한다.
- `DR-017` Staging·CSV를 AI 다음 순위로 둔 계획 — Staging과 CSV robustness는 중요하지만 Decision Intelligence 문서·첫 Package Preview 이후 순서로 재배치한다.
- `DR-018` External Context를 세 번째 우선순위로 둔 계획 — External Context와 Pilot을 즉시 세 번째로 두던 순서는 새 Milestone 구조로 대체한다.

### Rejected

- `DR-014` MVP 자동 외부 실행 — 사용자 승인 없는 메시지, 광고, 게시, 쿠폰, 제휴비용, 외부 설정 변경은 MVP에서 허용하지 않는다.
- `DR-086` 직접 연락처 Export 기본 금지 — 환자·고객 연락처 원문을 기본 Export 기능으로 제공하지 않는다.
- `DR-087` Quality Hard Fail 관리자 우회 — 관리자 권한으로 Hard Fail을 직접 PASSED로 바꾸는 기능을 만들지 않는다.
- `DR-088` 자유형 AI 전략을 Source of Truth로 사용 — LLM이 Raw Data를 읽고 Cause·Strategy·Playbook·경제성·성공조건을 자유롭게 생성한 결과를 Source of Truth로 사용하지 않는다.

## 10. Pilot 후 의무 재검토

다음 Decision은 첫 Pilot 후 자동으로 재검토한다.

```text
DR-026 Quality threshold / Section Floor
DR-032 D0~D4 Readiness
DR-036 Cause Score weights
DR-039 Strategy Score / 65점 / 5점 gap
DR-043 Playbook lifecycle
DR-060 Approval Scope Hash UX
DR-076 첫 Pilot Playbook
DR-077 Quality 재보정
DR-078 ACTIVE 승격 기준
DR-079 Precision / 통계 Method
DR-084 Pilot 사업장 규모
```

재검토 입력:

```text
Package Quality pass/fail
사용자 approve/reject/modified/later
Package revision 횟수
Action 실행률
Result 연결률
Playbook별 운영 부담·비용
Measurement Evidence Grade / Precision
정책·PII incident
4주 반복 사용
```

## 11. ADR 연결

기존 ADR 0001~0019는 수정하지 않는다.

본 문서 묶음에 다음 ADR을 추가한다.

```text
0020-decision-intelligence-layering.md
0021-versioned-action-playbooks.md
0022-recommendation-quality-gate.md
0023-experiment-before-execution.md
0024-measurement-meaning-separation.md
0025-channel-execution-levels.md
```

## 12. 구현 연결

다음 기술 계약이 완료됐다.

```text
LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md
LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md
```

이 Register의 `ACCEPTED`·`PROVISIONAL_V1` 결정은 Data Schema·API Contract·Backlog에 반영돼 있다.

신규 기획 문서 작성은 현재 범위에서 종료하고, 로컬 구현은 `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`의 `B01 — Decision Contract`부터 시작한다.
