---
title: "LOOFIO Planning Index"
version: "1.0"
date: "2026-08-18"
status: "문서 체계 단일 진입점"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
current_product_scope: "Hospital Appointment MVP"
target_scope: "LOW_DEMAND_SLOT Decision Intelligence vertical slice"
---

# LOOFIO Planning Index

## 1. 문서 목적

이 문서는 LOOFIO 프로젝트 문서의 **단일 진입점**이다.

LOOFIO 문서는 현재 구현, 제품 전략, 목표 설계, 개발 규칙, 구현 Backlog가 서로 다른 속도로 갱신된다. 따라서 파일이 존재한다는 이유만으로 다음을 가정해서는 안 된다.

```text
문서에 테이블이 있다
→ DB에 구현되어 있다

문서에 Endpoint가 있다
→ API가 구현되어 있다

문서에 Playbook이 있다
→ Pilot이나 고객 검증이 끝났다

문서에 AI 구조가 있다
→ LLM이 연결되어 있다
```

이 인덱스는 다음 질문에 답한다.

```text
현재 실제로 구현된 것은 무엇인가
어느 문서가 현재 Source of Truth인가
어느 문서가 다음 구현을 위한 확정 설계인가
어느 문서가 아직 작성되지 않았는가
개발자는 어떤 순서로 문서를 읽어야 하는가
문서가 충돌하면 무엇을 우선해야 하는가
코드 변경 후 어떤 문서를 갱신해야 하는가
```

---

# 2. 현재 기준

```text
Repository
→ JUNHOCHOI0309/LOOFIO

Branch
→ main

Document alignment content commit
→ 0adeaae5866f37afb679336d20c28c3cfb2e5e17

Current implemented code baseline recorded by status document
→ b7cc45d58b1fe1faa592888fd63f652ce0174f4a
```

현재 `CURRENT_IMPLEMENTATION_STATUS.md`는 `b7cc45d`를 기준 커밋으로 기록하고 있다. 그 이후 `371c5845`와 `0c75e524`은 주로 현재 구현에 문서를 맞춘 변경이다.

향후 상태 문서에는 다음처럼 두 값을 분리해 기록한다.

```text
code_baseline_commit
document_alignment_commit
```

## 현재 제품 범위

```text
Hospital Appointment MVP
```

현재 동작 루프:

```text
Google / Naver OAuth
→ Tenant / Business / Location
→ Hospital Appointment CSV inspect / preview / import
→ Mapping / Normalization
→ Appointment Metrics
→ 4개 Detector
→ Opportunity + Evidence + Score
→ Deterministic Manual Recommendation
→ User Decision
→ Manual Action
→ Action Result
→ same-window-prior-four-weeks-v2 Measurement
→ Dashboard
```

현재 구현되지 않은 핵심 범위:

```text
Decision Context
Cause Analysis
Strategy Engine
Versioned Action Playbook runtime
Experiment Definition / Evaluation
Recommendation Package v2
Recommendation Quality Validator
Structured Channel Execution
LLM Recommendation
External Context
Incremental Revenue
Staging / Production
다른 Archetype Adapter
```

---

# 3. 문서 상태 분류

| 상태 | 의미 | 구현 판단 |
|---|---|---|
| `CURRENT_IMPLEMENTED` | 현재 `main`의 code·migration·test와 일치 | 구현됨 |
| `CURRENT_PARTIAL` | 일부 구현됐지만 목표 기능 전체는 아님 | 부분 구현 |
| `CURRENT_DOC` | 현재 GitHub `docs/`에 존재하는 기준 문서 | 문서별로 다름 |
| `TARGET_SPEC_READY` | 로컬 구현용 상세 설계가 작성됐으나 GitHub·코드에는 미반영 | 미구현 |
| `CURRENT_NEEDS_ALIGNMENT` | 현재 GitHub 문서가 존재하나 새 Decision Intelligence 방향과 병합 필요 | 현재 규칙은 유효, 확장 규칙 미반영 |
| `PENDING_SPEC` | 작성 순서가 정해졌으나 아직 확정 문서가 없음 | 미구현 |
| `SUPERSEDED_DRAFT` | 더 세부적인 후속 문서가 대체 | 기준으로 사용하지 않음 |
| `FUTURE` | 첫 vertical slice 이후 | 미구현 |

## 상태 표시 원칙

```text
TARGET_SPEC_READY
!=
구현 완료

DRAFT Playbook
!=
검증 완료

PILOT
!=
ACTIVE

READY_FOR_REVIEW
!=
APPROVED

COMPLETED Experiment
!=
SUCCESS
```

---

# 4. Source of Truth

문서 충돌은 **무엇을 판단하는가**에 따라 우선순위가 다르다.

## 4.1 보안·정책·변경 금지

```text
1. 법적·보안 요구사항
2. docs/AGENTS.md
3. docs/PROHIBITED_CHANGES.md
4. 관련 ADR
5. Domain 상세 설계
```

## 4.2 현재 구현 여부

```text
1. api/migrations/*.sql
2. api/app/*
3. api/tests/*
4. apps/web/*
5. docs/CURRENT_IMPLEMENTATION_STATUS.md
6. docs/API_CONTRACT.md
7. 목표 설계 문서
```

## 4.3 현재 API 의미

```text
1. FastAPI / Pydantic 구현
2. API contract tests
3. docs/API_CONTRACT.md
4. Decision Intelligence API proposal
```

## 4.4 현재 DB 의미

```text
1. api/migrations/*.sql 순서
2. Repository / Store implementation
3. docs/LOOFIO_DATA_SCHEMA_V1.md
4. Decision Intelligence Data Schema proposal
```

## 4.5 다음 구현 설계

```text
1. 이 Planning Index
2. DECISION_REGISTER_V2.md
3. LOOFIO_IMPLEMENTATION_ROADMAP_V2.md
4. LOOFIO_IMPLEMENTATION_BACKLOG_V1.md
5. 해당 Domain 상세 설계
6. Governance 문서
```

## 핵심 규칙

목표 설계와 현재 코드가 충돌한다고 해서 목표 문서에 맞춰 현재 구현 사실을 다시 서술하지 않는다.

```text
먼저:
migration / code / test

그 다음:
CURRENT_IMPLEMENTATION_STATUS

그 다음:
목표 설계
```

---

# 5. 문서 읽는 순서

## 5.1 처음 프로젝트를 보는 사람

```text
00_PLANNING_INDEX.md
→ CURRENT_IMPLEMENTATION_STATUS.md
→ LOOFIO_IMPLEMENTATION_ROADMAP_V2.md
→ LOOFIO_IMPLEMENTATION_BACKLOG_V1.md
→ ARCHITECTURE.md
→ AGENTS.md
```

## 5.2 현재 기능을 수정하는 개발자

```text
CURRENT_IMPLEMENTATION_STATUS.md
→ API_CONTRACT.md
→ LOOFIO_DATA_SCHEMA_V1.md
→ 관련 code / migration / tests
→ 관련 ADR
```

## 5.3 첫 Decision Intelligence vertical slice 구현자

```text
LOOFIO_IMPLEMENTATION_ROADMAP_V2.md
→ LOOFIO_IMPLEMENTATION_BACKLOG_V1.md
→ LOOFIO_DECISION_INPUT_CONTRACT_V1.md
→ LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md
→ LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md
→ LOOFIO_STRATEGY_ENGINE_V1.md
→ LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md
→ LOOFIO_ACTION_PLAYBOOK_V1.md
→ LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md
→ LOOFIO_EXPERIMENT_DESIGN_V1.md
→ LOOFIO_PLAYBOOK_EXPERIMENT_MAPPING_V1.md
→ LOOFIO_RECOMMENDATION_PACKAGE_V2.md
→ LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md
→ LOOFIO_MEASUREMENT_FRAMEWORK_V1.md
→ LOOFIO_CHANNEL_EXECUTION_V1.md
```

## 5.4 API·DB를 구현하는 개발자

아직 작성 예정인 다음 두 문서까지 확인한 뒤 Persistence 작업을 시작한다.

```text
LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md
LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md
```

그 전에는 Preview·Pure Domain·In-memory 구현까지만 의미를 고정한다.

## 5.5 배포·보안·운영 담당자

```text
AGENTS.md
→ PROHIBITED_CHANGES.md
→ ARCHITECTURE.md
→ DEPENDENCY_RULES.md
→ CODE_OWNERSHIP.md
→ DEPLOYMENT_FLOW.md
→ CHANNEL_EXECUTION_V1.md
→ MEASUREMENT_FRAMEWORK_V1.md
```

---

# 6. 전체 문서 흐름

```text
제품 목적
│
├─ AI 마케팅 매니저 전략 v1.1
├─ TECH ROADMAP
├─ Business Taxonomy
└─ Hospital MVP Decisions

현재 구현
│
├─ CURRENT_IMPLEMENTATION_STATUS
├─ DATA_SCHEMA_V1
├─ API_CONTRACT
├─ OPPORTUNITY_ENGINE_V1
└─ ADR 0001~0019

Decision Intelligence 목표 설계
│
├─ IMPLEMENTATION_ROADMAP_V2
├─ DECISION_INPUT_CONTRACT
├─ CAUSE_ANALYSIS
├─ STRATEGY_ENGINE
├─ ACTION_PLAYBOOK
├─ EXPERIMENT_DESIGN
├─ RECOMMENDATION_PACKAGE
├─ RECOMMENDATION_QUALITY_BAR
├─ MEASUREMENT_FRAMEWORK
└─ CHANNEL_EXECUTION

실행 계획
│
├─ IMPLEMENTATION_BACKLOG_V1
├─ DECISION_REGISTER_V2
├─ DATA_SCHEMA_DECISION_INTELLIGENCE_V1
└─ API_CONTRACT_DECISION_INTELLIGENCE_V1

Governance
│
├─ AGENTS
├─ ARCHITECTURE
├─ DEPENDENCY_RULES
├─ PROHIBITED_CHANGES
├─ CODE_OWNERSHIP
└─ DEPLOYMENT_FLOW
```

---

# 7. 현재 GitHub 기준 문서 Registry

아래 문서는 현재 `main`의 `docs/`에서 확인되는 기준 문서다.

| 문서 | 상태 | 역할 | 다음 조치 |
|---|---|---|---|
| `docs/README.md` | `CURRENT_DOC` | Planning Index 안내와 문서 분류 | 본 묶음의 축약 안내본으로 교체 |
| `docs/CURRENT_IMPLEMENTATION_STATUS.md` | `CURRENT_DOC` | 실제 구현 상태 기준 | 본 묶음에서 code/document 기준과 다음 Backlog를 정렬 |
| `docs/AI_마케팅_매니저_데이터_수집_및_기획_전략_v1.1.md` | `CURRENT_DOC` | 제품 전략·숨은 매출 방향 | Decision Intelligence 가치 제안과 연결 |
| `docs/LOOFIO_TECH_ROADMAP_v1.md` | `CURRENT_DOC` | 장기 기술·제품 방향 | v2 구현 로드맵을 실행 기준으로 연결 |
| `docs/LOOFIO_HOSPITAL_MVP_DECISIONS_v1.md` | `CURRENT_DOC` | Hospital MVP 결정 | 새 Decision/Playbook 정책의 ADR 연결 |
| `docs/LOOFIO_BUSINESS_TAXONOMY_V1.md` | `CURRENT_DOC` | 다업종 Archetype 장기 설계 | Hospital 검증 전 추가 확장 보류 |
| `docs/LOOFIO_BUSINESS_TAXONOMY_MAPPING_V1.csv` | `CURRENT_DOC` | 공식 분류→LOOFIO mapping 자료 | 원본 mapping 자산으로 유지 |
| `docs/LOOFIO_DATA_SCHEMA_V1.md` | `CURRENT_DOC` | 현재 migration 기반 DB 요약 | Decision Intelligence 제안 스키마와 분리 |
| `docs/LOOFIO_OPPORTUNITY_ENGINE_V1.md` | `CURRENT_DOC` | Metric·Detector·Opportunity 경계 | Cause Analysis input handoff만 연결 |
| `docs/API_CONTRACT.md` | `CURRENT_DOC` | 현재 `/api/v1` 계약 | 신규 API 문서 완성 후 additive alignment |
| `docs/AGENTS.md` | `CURRENT_DOC` | 저장소 최상위 개발 규칙 | 본 묶음의 병합본 적용 |
| `docs/ARCHITECTURE.md` | `CURRENT_DOC` | 현재·목표 시스템 경계 | 본 묶음의 병합본 적용 |
| `docs/DEPENDENCY_RULES.md` | `CURRENT_DOC` | 현재·목표 의존 규칙 | 본 묶음의 병합본 적용 |
| `docs/PROHIBITED_CHANGES.md` | `CURRENT_DOC` | Decision Intelligence 금지 변경 | 본 묶음의 병합본 적용 |
| `docs/CODE_OWNERSHIP.md` | `CURRENT_DOC` | 현재·목표 Logical ownership | 본 묶음의 병합본 적용 |
| `docs/DEPLOYMENT_FLOW.md` | `CURRENT_DOC` | 현재 CI·목표 Release Gate | 본 묶음의 병합본 적용 |
| `docs/adr/*` | `CURRENT_DOC` | 시점별 결정 기록 | 과거 ADR 수정 금지, 0020 이후 추가 |

---

# 8. Decision Intelligence 상세 설계 Registry

다음 문서는 본 기획 작업에서 작성 완료된 목표 설계다. GitHub에 반영하더라도 migration·code·test가 생기기 전에는 구현 완료로 취급하지 않는다.

| 순서 | 문서 | 상태 | 책임 |
|---:|---|---|---|
| 1 | `docs/LOOFIO_IMPLEMENTATION_ROADMAP_V2.md` | `TARGET_SPEC_READY` | 전체 Phase·Gate·첫 vertical slice |
| 2 | `docs/LOOFIO_IMPLEMENTATION_BACKLOG_V1.md` | `TARGET_SPEC_READY` | Canonical Task 169개·Milestone·Dependency |
| 3 | `docs/LOOFIO_DECISION_INPUT_CONTRACT_V1.md` | `TARGET_SPEC_READY` | 해결책 생성에 필요한 사업 입력·D0~D4 |
| 4 | `docs/LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md` | `TARGET_SPEC_READY` | Observation과 Cause Hypothesis 분리 |
| 5 | `docs/LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md` | `TARGET_SPEC_READY` | Cause별 Required/Optional/Blocking |
| 6 | `docs/LOOFIO_STRATEGY_ENGINE_V1.md` | `TARGET_SPEC_READY` | Hard Gate·대안 비교·전략 선택 |
| 7 | `docs/LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md` | `TARGET_SPEC_READY` | Cause→Strategy deterministic mapping |
| 8 | `docs/LOOFIO_ACTION_PLAYBOOK_V1.md` | `TARGET_SPEC_READY` | Definition·Applicability·Instance |
| 9 | `docs/LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md` | `TARGET_SPEC_READY` | Hospital Core Playbook 12개 |
| 10 | `docs/LOOFIO_EXPERIMENT_DESIGN_V1.md` | `TARGET_SPEC_READY` | Template·Definition·Run·Result·Evaluation |
| 11 | `docs/LOOFIO_PLAYBOOK_EXPERIMENT_MAPPING_V1.md` | `TARGET_SPEC_READY` | Core Playbook 12개 실험 연결 |
| 12 | `docs/LOOFIO_RECOMMENDATION_PACKAGE_V2.md` | `TARGET_SPEC_READY` | 최종 Action Plan Package |
| 13 | `docs/LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md` | `TARGET_SPEC_READY` | 75점·Section Floor·Hard Fail |
| 14 | `docs/LOOFIO_MEASUREMENT_FRAMEWORK_V1.md` | `TARGET_SPEC_READY` | Actual·Delta·Incremental·Economics 의미 |
| 15 | `docs/LOOFIO_CHANNEL_EXECUTION_V1.md` | `TARGET_SPEC_READY` | Manual→Connector 실행 계약 |
| 16 | `docs/LOOFIO_CHANNEL_CAPABILITY_AND_EVENT_MATRIX_V1.md` | `TARGET_SPEC_READY` | 채널별 승인·Tracking·Event·비용 |
| 17 | `docs/LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md` | `TARGET_SPEC_READY` | `0012~0020` additive schema proposal |
| 18 | `docs/LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md` | `TARGET_SPEC_READY` | Preview-first·additive API proposal |
| 19 | `docs/DECISION_REGISTER_V2.md` | `TARGET_SPEC_READY` | 확정·임시·미결정·폐기 Decision Registry |
| 20 | `docs/00_PLANNING_INDEX.md` | `TARGET_SPEC_READY` | 문서 단일 진입점 |

---

# 9. 현재 범위의 문서 작성 상태

```text
제품·의사결정 상세 설계     완료
Measurement·Execution 설계 완료
Implementation Backlog      완료
Planning Index              완료
Decision Register           완료
Data Schema Proposal        완료
API Contract Proposal       완료
Governance 병합본           완료
ADR 0020~0025               완료
```

현재 남은 것은 새 기획 문서가 아니라 code·migration·test 구현이다.

Persistence는 기술 계약이 완료됐지만 다음 Gate를 우회하지 않는다.

```text
M1~M7 Preview·Manual Pilot
Legacy 회귀
Migration preflight
M8 단계 배포
```

---

# 10. Superseded·보류 문서

다음 초기 초안은 더 세부적인 문서가 책임을 대체했다.

| 문서/개념 | 상태 | 대체 문서 |
|---|---|---|
| 단일 `Recommendation Engine v1` | `SUPERSEDED_DRAFT` | Cause + Strategy + Playbook + Package + Quality |
| 초기 `AI Architecture v1`의 AI 우선순위 | `FUTURE` | Deterministic Package 완료 후 AI Architecture v2 |
| 초기 `LOOFIO_POSTGRES_SCHEMA_V1.sql` 설계 초안 | `SUPERSEDED_DRAFT` | 현재 migration + 향후 DI Data Schema |
| 구현용 Patch/Code Package | 프로젝트 문서 아님 | 로컬 구현은 Backlog와 상세 MD 기준 |
| 각 Artifact package의 `README`, `manifest`, `VALIDATION_REPORT` | 저장소 문서 아님 | 다운로드 검증용 보조 파일 |

## 원칙

GitHub `docs/`에는 최종 상세 설계 MD만 넣고, 대화용 ZIP·Manifest·Validation 파일은 기본적으로 넣지 않는다.

---

# 11. 첫 vertical slice 문서 경계

## 대상

```text
Opportunity Type
→ LOW_DEMAND_SLOT

Domain
→ Hospital Appointment

Execution
→ Manual / Staff-operated

Measurement
→ Current Grade C adapter 우선
```

## 포함

```text
Decision Context Preview
Cause Preview
Strategy Preview
Static Playbook Registry
Experiment Draft Preview
Recommendation Package + Quality Preview
기존 Recommendation / Manual Action Handoff
Current Measurement Adapter
Manual / Staff Execution Package
```

## 제외

```text
LLM
External Context
실제 SMS/Kakao/Ads Connector
Bounded Automation
Grade A/B production persistence
Incremental Revenue 보장
다른 Opportunity
다른 Archetype
```

---

# 12. 구현 Milestone와 문서

| Milestone | 구현 결과 | 필수 문서 |
|---|---|---|
| `M1` | Decision Input Foundation | Decision Input Contract, Backlog |
| `M2` | Cause Preview | Cause Engine, Cause Requirements |
| `M3` | Strategy Preview | Strategy Engine, Cause→Strategy |
| `M4` | Playbook·Experiment Draft | Playbook, Catalog, Experiment, Mapping |
| `M5` | Package·Quality Preview | Recommendation Package, Quality Bar |
| `M6` | Manual Pilot UI | Backlog, Governance alignment, API current contract |
| `M7` | Measurement·Manual Execution | Measurement Framework, Channel Execution |
| `M8` | Persistence·정식 API | DI Data Schema, DI API Contract |
| `M9` | Connector Pilot | Channel Execution, 별도 Provider ADR |

---

# 13. 문서 갱신 Trigger

## 코드·기능 구현

갱신:

```text
CURRENT_IMPLEMENTATION_STATUS.md
관련 API_CONTRACT
관련 DATA_SCHEMA
관련 ADR
필요 시 README / Planning Index 상태
```

## DB Migration 추가

갱신:

```text
api/migrations
LOOFIO_DATA_SCHEMA_V1.md 또는 DI Data Schema
CURRENT_IMPLEMENTATION_STATUS
API Contract if externally visible
```

## Endpoint 추가·변경

갱신:

```text
Pydantic / FastAPI
Contract tests
API_CONTRACT 또는 DI API Contract
CURRENT_IMPLEMENTATION_STATUS
```

## Metric·Score·Validator 공식 변경

필수:

```text
새 Version
Tests
관련 상세 설계
ADR
CURRENT_IMPLEMENTATION_STATUS
```

과거 결과를 새 의미로 조용히 덮어쓰지 않는다.

## Playbook 변경

```text
새 Definition version
Lifecycle status
Experiment mapping
Policy tags
Fixture
```

## 제품 결정 변경

```text
DECISION_REGISTER_V2
ADR
영향받는 상세 설계
Backlog
```

---

# 14. 문서 작성 규칙

## Frontmatter 권장

```yaml
title:
version:
date:
status:
base_repository:
base_branch:
base_commit:
depends_on:
```

## 파일명

```text
고정 Governance
→ AGENTS.md
→ ARCHITECTURE.md
→ API_CONTRACT.md

Versioned Domain Spec
→ LOOFIO_<DOMAIN>_V1.md
→ LOOFIO_<DOMAIN>_V2.md

현재 상태
→ CURRENT_IMPLEMENTATION_STATUS.md

결정 기록
→ adr/NNNN-*.md
```

## Version 규칙

Major:

- 필드 의미 변경
- 상태 의미 변경
- score/metric 공식 호환 불가
- lifecycle 구조 변경

Minor:

- optional field
- 설명·예시
- backward-compatible validation 추가

## 상태 표현

문서가 `확정 설계안`이어도 구현 상태는 별도다.

```text
설계 확정
!=
코드 구현
!=
Pilot 검증
!=
Active 운영
```

---

# 15. 알려진 문서 부채

## 15.1 CURRENT_IMPLEMENTATION_STATUS 기준 커밋 — 본 묶음에서 정렬

본 병합본은 다음 값을 분리한다.

```text
code_baseline_commit: b7cc45d...
source_document_alignment_commit: 0c75e524...
document_alignment_commit: 0adeaae5866f37afb679336d20c28c3cfb2e5e17
```

## 15.2 다음 구현 우선순위 — 본 묶음에서 정렬

`CURRENT_IMPLEMENTATION_STATUS.md`의 다음 우선순위를 아래 실행 기준으로 교체했다.


```text
Decision Input
→ Cause
→ Strategy
→ Playbook
→ Experiment
→ Package / Quality
→ UI / Manual Action
→ AI Explanation
```

현재 구현 사실은 유지하고 “다음 우선순위”만 갱신했다.

## 15.3 docs/README 역할 — 본 묶음에서 정렬

본 병합본의 `docs/README.md`는 Planning Index를 가리키는 짧은 안내와 문서 Registry로 갱신했다.


```text
docs/README.md
→ 짧은 안내
→ 00_PLANNING_INDEX.md 링크

00_PLANNING_INDEX.md
→ 실제 단일 진입점
```

## 15.4 CODEOWNERS 참조 — 본 묶음에서 정렬

현재 `main`에는 `.github/CODEOWNERS`와 `.github/CODEOWNERS.template`이 없다. 본 병합본은 존재하지 않는 template 참조를 제거하고 `CODE_OWNERSHIP.md`에 논리적 후보만 남겼다.

## 15.5 Governance v2 — 본 묶음에서 정렬

본 병합본은 다음 항목을 Governance에 반영했다.

```text
Cause / Strategy / Playbook / Experiment dependency
일반 조언 금지
Recommendation Quality Hard Fail
경제성 unknown 처리
Grade C/D 인과 표현 금지
Execution approval / tracking / idempotency
현재 구현과 목표 설계 분리
```

---

# 16. ADR 계획

기존 `0001~0019`는 수정하지 않는다.

본 묶음에 다음 ADR을 포함한다.

```text
0020-decision-intelligence-layering.md
0021-versioned-action-playbooks.md
0022-recommendation-quality-gate.md
0023-experiment-before-execution.md
0024-measurement-meaning-separation.md
0025-channel-execution-levels.md
0026-cause-analysis-preview-api.md
```

ADR은 “현재 구현 여부”가 아니라 해당 시점의 결정과 근거를 보존한다.

---

# 17. GitHub 반영 권장 순서

모든 문서를 한 번에 무질서하게 추가하지 않는다.

## Step 1 — 문서 진입점·결정

```text
00_PLANNING_INDEX.md
DECISION_REGISTER_V2.md
LOOFIO_IMPLEMENTATION_ROADMAP_V2.md
LOOFIO_IMPLEMENTATION_BACKLOG_V1.md
```

## Step 2 — Domain 상세 설계

```text
Decision Input
Cause + Requirements
Strategy + Mapping
Playbook + Catalog
Experiment + Mapping
Recommendation Package + Quality
Measurement
Channel Execution + Matrix
```

## Step 3 — 기술 계약

```text
LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md
LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md
```

## Step 4 — 현재 문서 정렬

```text
CURRENT_IMPLEMENTATION_STATUS.md
docs/README.md
AGENTS.md
ARCHITECTURE.md
DEPENDENCY_RULES.md
PROHIBITED_CHANGES.md
CODE_OWNERSHIP.md
DEPLOYMENT_FLOW.md
```

## Step 5 — ADR

```text
0020+
```

---

# 18. 로컬 구현 시작 기준

첫 Pure Domain 구현에 필요한 핵심 문서가 모두 완료됐다.

```text
[완료] Planning Index / Decision Register
[완료] Implementation Roadmap / Backlog
[완료] Decision Input
[완료] Cause / Strategy
[완료] Playbook / Experiment
[완료] Recommendation Package / Quality
[완료] Measurement / Channel Execution
[완료] DI Data Schema / API Contract
[완료] Governance 병합본
[완료] ADR 0020~0025
```

현재 구현 상태는 여전히 기존 Hospital MVP다. 다음 실제 작업은 코드 구현이다.

```text
B01 — Decision Contract
→ DI-001~DI-005
→ QA-001 / QA-003 / QA-004
```

Persistence는 M1~M7 Gate 이후 M8에서 시작한다.

---

# 19. 다음 단계

신규 기획 문서 작성은 현재 범위에서 종료한다.

```text
1. 본 문서 묶음을 GitHub docs에 반영 — 완료
2. 실제 반영 commit SHA를 CURRENT_IMPLEMENTATION_STATUS에 기록 — 완료
3. 로컬에서 B01 — Decision Contract 구현
```

코드 구현 전후 상태는 `CURRENT_IMPLEMENTATION_STATUS.md`, 작업 순서는 `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`를 따른다.
