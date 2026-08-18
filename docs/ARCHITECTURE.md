# LOOFIO Architecture v2

- 기준일: 2026-08-18
- 기준 브랜치: `main`
- 문서 정렬 기준 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`
- 상태: 현재 구현 + Decision Intelligence 목표 아키텍처

## 1. 목적

이 문서는 LOOFIO의 시스템 경계와 데이터 흐름을 정의한다.

현재 구현 루프:

```text
Hospital Appointment CSV
→ Normalization
→ Metrics
→ 4 Detectors
→ Opportunity + Evidence + Score
→ Deterministic Recommendation Draft
→ Decision
→ Manual Action
→ Result
→ Measurement
→ Dashboard
```

목표 의사결정 루프:

```text
Business Data
+
External Context
        ↓
Deterministic Analytics
        ↓
Opportunity Detection
        ↓
Cause Analysis
        ↓
Strategy Comparison
        ↓
Action Playbook Resolution
        ↓
Economics / Feasibility
        ↓
Experiment Design
        ↓
Recommendation Package
        ↓
User Decision
        ↓
Channel Execution
        ↓
Result
        ↓
Measurement
        ↓
Next Analysis
```

핵심 원칙:

> AI가 원본 데이터에서 기회·원인·경제성·효과를 임의로 생성하지 않는다. 각 계층이 구조화된 계약을 만들고 AI는 설명과 표현을 보조한다.

---

# 2. 현재와 목표를 구분한다

## 현재 Source of Truth

```text
api/migrations/*.sql
api/app/*
api/tests/*
docs/CURRENT_IMPLEMENTATION_STATUS.md
docs/API_CONTRACT.md
```

## 목표 설계

```text
LOOFIO_DECISION_INPUT_CONTRACT_V1.md
LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md
LOOFIO_STRATEGY_ENGINE_V1.md
LOOFIO_ACTION_PLAYBOOK_V1.md
LOOFIO_EXPERIMENT_DESIGN_V1.md
LOOFIO_RECOMMENDATION_PACKAGE_V2.md
LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md
LOOFIO_CHANNEL_EXECUTION_V1.md
LOOFIO_MEASUREMENT_FRAMEWORK_V1.md
LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md
LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md
```

목표 문서의 entity·endpoint·module은 migration·code·test가 생기기 전에는 구현된 것으로 취급하지 않는다.

---

# 3. Logical Architecture

```text
┌────────────────────────────────────────────────────────┐
│ Apps / UI                                              │
│ Dashboard · Opportunity · Diagnosis · Plan · Results   │
└──────────────────────────┬─────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│ API Layer                                              │
│ Auth · Validation · DTO · Idempotency · Version        │
└──────────────────────────┬─────────────────────────────┘
                           ↓
┌────────────────────────────────────────────────────────┐
│ Application Layer                                      │
│ Use Cases · Transaction · Policy · Orchestration       │
└───────┬────────────┬──────────────┬────────────────────┘
        ↓            ↓              ↓
  Ingestion      Analytics     Decision Intelligence
                                   │
                ┌──────────────────┼─────────────────────┐
                ↓                  ↓                     ↓
              Cause            Strategy            Playbook/Experiment
                └──────────────────┬─────────────────────┘
                                   ↓
                        Recommendation Package
                                   ↓
                         Decision / Action / Result
                                   ↓
                              Measurement
```

Port/Adapter 방향:

```text
Domain / Analytics / Decision Intelligence
        ↓ depends on
Ports / Contracts

Infrastructure / AI Providers / External Connectors
        → implement Ports
```

---

# 4. Runtime Data Flow

## 4.1 Import

```text
CSV / API
→ Raw Inspection
→ Validation
→ Column / Status Mapping
→ Domain Normalization
→ Appointment / Offering / Customer
```

현재 Hospital MVP의 raw·normalized lineage와 import idempotency를 유지한다.

## 4.2 Analytics

```text
Normalized Domain
→ Metric Engine
→ Detector
→ Opportunity
→ Evidence
→ Opportunity Score
```

현재 Detector:

```text
LOW_DEMAND_SLOT
CANCELLATION_HOTSPOT
DORMANT_CUSTOMER
SERVICE_DEMAND_GAP
```

RevenueGap은 LowDemandSlot Opportunity의 Estimate 계층에 포함된다.

Metric·Detector·Score는 LLM 없이 재현 가능해야 한다.

## 4.3 Cause Analysis

```text
Opportunity
+ Evidence
+ Limitations
+ Metric Summary
+ Business / Offering / Operation Context
+ External Context(optional)
→ Cause Candidates
→ Diagnostic Questions
```

출력은 가설이다.

```text
cause_code
hypothesis
supporting_evidence_refs
contradicting_evidence_refs
missing_data
testability
score
limitations
```

Cause Analysis가 Raw Import 전체를 직접 읽지 않는다.

## 4.4 Strategy Selection

```text
Opportunity
+ Cause Candidates
+ Business Goal
+ Economics
+ Capacity / Staff
+ Available Channels
+ Policy
→ Strategy Candidates
→ Ranked Alternatives
```

최소 2개 후보를 비교하거나 단일 후보 사유를 남긴다.

유효 Strategy Family:

```text
ACQUISITION
CONVERSION
RETENTION_REACTIVATION
CANCELLATION_RECOVERY
OFFER_PACKAGING
CAPACITY_OPERATION
DISCOVERABILITY
PARTNERSHIP_REFERRAL
DATA_COLLECTION
NO_ACTION
```

## 4.5 Playbook Resolution

```text
Selected Strategy
+ Opportunity / Cause
+ Archetype
+ Data Readiness
+ Policy
→ Applicable Versioned Playbooks
```

Playbook은 tenant별 자유 문장이 아니라 versioned definition이다.
사업장별 값은 별도 plan instance에 주입한다.

## 4.6 Economics / Feasibility

```text
Offering price
Variable cost
Benefit cost
Media / Partner cost
Staff time
Capacity
Policy
→ Economics / Feasibility Result
```

비용 미상은 `unknown`으로 유지한다.

## 4.7 Experiment Design

```text
Playbook
+ Population
+ Treatment
+ Comparison
+ Time
+ Primary Metric
+ Guardrail
+ Success / Stop
+ Attribution Window
→ Experiment Contract
```

핵심 metric은 AI 문장에서 가져오지 않는다.

## 4.8 Recommendation Package Assembly

```text
Opportunity
+ Cause Analysis
+ Strategy Comparison
+ Selected Playbook
+ Economics
+ Experiment
+ Channel Plan
→ Final Action Plan Package
→ Quality Validation
```

Recommendation Package Assembler는 수치를 재계산하지 않는다.

## 4.9 User Decision / Action

```text
Recommendation Package
→ approved / rejected / modified / later
→ Action Draft
→ Approval
→ Manual / Assisted / Connector Execution
```

현재 Hospital MVP는 manual execution만 구현되어 있다.

## 4.10 Measurement

```text
Action
→ Actual Result
→ Baseline
→ External Context Review
→ Observed Delta
→ Incremental Estimate(optional)
→ Economics
→ Evidence Grade
```

현재 구현은 직전 동일 길이 baseline과의 관찰 비교다.

---

# 5. Physical Module Mapping

## 현재 구현 위치

| 책임 | 현재 위치 |
|---|---|
| Web | `apps/web/app` |
| API routes | `api/app/api/routes` |
| Auth/session | `api/app/auth` |
| Import/normalization | `api/app/imports` |
| Metrics | `api/app/metrics` |
| Detectors | `api/app/analytics/detectors` |
| Scoring | `api/app/analytics/scoring` |
| Opportunity | `api/app/opportunities` |
| Recommendation | `api/app/recommendations` |
| Action | `api/app/actions` |
| Result/Measurement | `api/app/results` |
| Schema | `api/app/schemas` |
| Migration | `api/migrations` |
| Tests | `api/tests` |

## 목표 additive module 후보

구현 시 실제 package 명은 코드 구조 검토 후 확정한다.

```text
api/app/decisioning/causes
api/app/decisioning/strategies
api/app/decisioning/playbooks
api/app/experiments
api/app/recommendation_packages
api/app/recommendation_quality
api/app/channel_execution
api/app/ai/gateway
```

기존 `recommendations`, `actions`, `results`를 즉시 이동·삭제하지 않는다.

---

# 6. Core Domain

## Tenant

보안·데이터 격리 경계.

## Business / Location

분석·실행의 사업장 범위.

## Offering

진료·시술·검사·상품·서비스 등 분석과 실행의 대상.

## Customer

사업장 범위의 가명 고객.

## Appointment

Hospital `APPOINTMENT_SERVICE` Domain Object.

## Opportunity

Detector가 생성한 현상·Evidence·Estimate·Score.

## CauseCandidate

원인 가설과 근거·반증·부족 데이터.

## StrategyCandidate

개입 방향, 점수, 비용·위험·선택/제외 이유.

## PlaybookDefinition

적용·금지조건, 실행 절차, 비용·실험 template를 가진 versioned definition.

## Experiment

대상·처리·비교·기간·metric·성공·중단조건.

## RecommendationPackage

최종 Action Plan Package.

## Action / Result / Measurement

승인된 실행, 실제 결과, baseline 기반 해석.

---

# 7. Stage Ownership and Boundary

| Stage | Source of Truth | 하지 않는 일 |
|---|---|---|
| Opportunity | Metric/Detector | 원인·해결책 선택 |
| Cause | Evidence references | 원인 확정 |
| Strategy | constraints/economics | 콘텐츠 생성 |
| Playbook | registry definition | tenant 값 하드코딩 |
| Experiment | deterministic contract | 효과 보장 |
| Recommendation Package Assembler | prior stage outputs | raw 분석·수치 계산 |
| Channel | approved plan | Opportunity 판단 |
| Measurement | actual result + baseline | AI 설명을 사실로 사용 |

---

# 8. AI Boundary

```text
Structured Domain / Decision Data
→ Context Builder
→ PII / Policy Filter
→ AI Gateway
→ Provider Adapter
→ Structured Output
→ Validators
```

Validator:

```text
Schema
Evidence Fidelity
Playbook Compliance
Economics Integrity
Execution Completeness
Policy Safety
Recommendation Quality
```

AI 실패:

```text
Opportunity remains
Cause/Strategy deterministic outputs remain
Playbook/Experiment template remains
Deterministic Recommendation fallback
```

AI 실패가 Opportunity transaction을 rollback하지 않는다.

---

# 9. Database Boundary

현재 실행 가능한 스키마 Source of Truth:

```text
api/migrations/0001 ... current
```

향후 additive entity 후보:

```text
cause_analysis_runs
cause_candidates
strategy_runs
strategy_candidates
playbook_definitions
playbook_instances
experiments
recommendation_packages
recommendation_quality_results
channel_execution_records
```

추가 원칙:

- tenant/business scope
- version
- source references
- immutable or append-only history가 필요한지 정의
- status transition
- idempotency
- audit
- retention
- forward-fix

---

# 10. Channel Boundary

온라인:

```text
CRM / approved messaging
Search Ads
Social Ads
Organic Social
Map / Business Profile
Website / Landing
Booking Page
Email
```

오프라인:

```text
Front-desk rebooking
Waitlist operation
Staff callback
Local partnership
Referral card/code
In-store signage
Tracked printed material
```

모든 실행은 최소 하나의 tracking 수단을 가진다.

```text
UTM
unique URL
booking source code
coupon code
partner code
QR
action_id
manual source tagging
```

자동 실행은 현재 범위가 아니다.

---

# 11. External Context Boundary

외부 데이터는 원인 확정이 아니라 가설 보조다.

```text
Weather
Holiday
Local Event
Living Population
Trade Area
```

허용:

> 비 예보가 수요 감소 가설을 보조한다.

금지:

> 비 때문에 매출이 감소했다.

---

# 12. Security Boundary

필수:

- tenant/business scoped repository
- tenant/business scoped cache/file/AI context
- OAuth secret 평문 저장 금지
- patient PII/clinical data AI 전송 금지
- Action target 최소화
- offline target/export 보존기간
- audit log

---

# 13. Failure Isolation

각 단계는 독립적으로 실패 상태를 가질 수 있다.

```text
Opportunity persisted
Cause failed
Strategy not run
Playbook not applicable
Experiment incomplete
Quality rejected
AI failed
Channel failed
Measurement inconclusive
```

실패한 후속 단계가 앞선 deterministic 결과를 삭제하지 않는다.

---

# 14. Versioned Intelligence

버전 필수:

```text
taxonomy mapping
normalizer
metric
detector
opportunity score
cause analysis
cause score
strategy rules
strategy score
playbook
experiment template
recommendation package schema
recommendation quality score
prompt/model route
channel execution contract
measurement method
```

과거 결과를 현재 버전으로 조용히 덮어쓰지 않는다.

---

# 15. MVP Architecture Scope

## 현재 완료

```text
CSV Import
→ Appointment Normalization
→ Metrics
→ 4 Detectors
→ Opportunity / Score
→ Deterministic Recommendation
→ Decision
→ Manual Action
→ Result
→ Baseline Measurement
```

## 다음 vertical slice

```text
LOW_DEMAND_SLOT
→ deterministic Cause Candidates
→ Strategy 2~3개 비교
→ PB-01 선택
→ Experiment Template
→ Recommendation Package
→ Quality Validator
→ 기존 manual Action
```

첫 vertical slice는 AI 없이 완성 가능하다.

AI는 이후 설명·콘텐츠 초안에 연결한다.

---

# 16. 현재 기술

확정:

```text
Next.js / React / TypeScript
FastAPI / Pydantic / psycopg
PostgreSQL
Google / Naver direct OAuth
Server-side session
GitHub Actions regression CI
```

미확정:

```text
AI provider/model
Queue/cache
Staging/Production provider
Monitoring
Secret Manager
Production migration runner
External channel connector
```
