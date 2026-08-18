---
title: "LOOFIO Implementation Roadmap v2"
version: "2.0"
date: "2026-08-17"
status: "로컬 구현용 상세 기획안"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
implementation_scope: "Hospital Appointment MVP → Decision Intelligence"
---

# LOOFIO Implementation Roadmap v2

## 1. 문서 목적

이 문서는 현재 LOOFIO Hospital Appointment MVP에서 다음 제품 단계인 **Decision Intelligence**를 구현하기 위한 전체 순서, 선행조건, 산출물, 테스트, 완료조건을 정의한다.

현재 제품은 다음 루프까지 구현되어 있다.

```text
Google / Naver OAuth
→ Tenant / Business / Location
→ Hospital Appointment CSV
→ Mapping / Normalization
→ Appointment Metrics
→ 4개 Detector
→ Opportunity + Evidence + Score
→ Deterministic Manual Recommendation
→ User Decision
→ Manual Action
→ Result
→ Baseline Measurement
→ Dashboard
```

현재 Recommendation은 안전한 수동 검토 초안이지만, 다음 질문에 충분히 답하지 못한다.

```text
왜 이 문제가 생겼을 가능성이 높은가
어떤 대안들을 비교했는가
왜 이 대안을 1순위로 선택했는가
실행 비용과 기여가치는 무엇인가
온라인·오프라인에서 정확히 무엇을 하는가
어떤 조건이면 성공·중단하는가
```

따라서 다음 목표는 LLM 연결 자체가 아니라 아래 파이프라인을 먼저 만드는 것이다.

```text
Opportunity
→ Decision Input
→ Cause Analysis
→ Strategy Comparison
→ Action Playbook
→ Economics / Feasibility
→ Experiment Design
→ Recommendation Package
→ Recommendation Quality Gate
→ Decision
→ Manual Action
→ Result
→ Measurement
```

---

# 2. 현재 Source of Truth

## 2.1 구현 여부

현재 구현 여부는 다음 순서를 따른다.

```text
1. api/migrations/*.sql
2. api/app/*
3. api/tests/*
4. docs/CURRENT_IMPLEMENTATION_STATUS.md
5. docs/API_CONTRACT.md
```

기획 문서에 entity 또는 endpoint가 정의되어 있어도 migration·code·test가 없으면 구현된 것으로 취급하지 않는다.

## 2.2 현재 기술 기준

```text
Frontend
→ Next.js / React / TypeScript

Backend
→ FastAPI / Pydantic / psycopg

Database
→ PostgreSQL

Authentication
→ Google / Naver direct OAuth
→ PostgreSQL server-side session

Current execution
→ Manual Action only

Current measurement
→ Previous equal-length 1–4 week baseline comparison
```

## 2.3 현재 Detector

```text
LOW_DEMAND_SLOT
CANCELLATION_HOTSPOT
DORMANT_CUSTOMER
SERVICE_DEMAND_GAP
```

`RevenueGap`은 결제 표본이 충분한 `LOW_DEMAND_SLOT` Opportunity의 Estimate 계층으로 사용한다.

---

# 3. 로드맵 설계 원칙

## 3.1 AI보다 의사결정 계약을 먼저 구현한다

다음 순서를 지킨다.

```text
Deterministic contract
→ Deterministic candidate generation
→ Validation
→ Persistence
→ API
→ UI
→ AI wording / explanation
```

AI가 없어도 다음이 가능해야 한다.

- 원인 후보 생성
- 전략 후보 비교
- 적용 가능한 Playbook 선택
- 경제성 입력 부족 판정
- 실험 초안 생성
- Recommendation 품질 판정

## 3.2 기존 흐름을 제거하지 않는다

다음은 유지한다.

```text
POST /opportunities/{id}/recommendations/draft
Recommendation Decision
Manual Action
Action Result
Current Measurement
```

새 구조는 additive하게 추가한다.

```text
Legacy Recommendation
+
Decision Intelligence Recommendation Package
```

새 흐름이 안정될 때까지 기존 Recommendation을 fallback과 회귀 기준으로 사용한다.

## 3.3 일반 조언은 완료된 Recommendation이 아니다

다음은 최종 결과로 허용하지 않는다.

```text
SNS를 강화하세요.
전단지를 배포하세요.
프로모션을 진행하세요.
휴면 고객에게 연락하세요.
```

최종 Recommendation Package는 최소 다음을 포함한다.

1. Opportunity
2. Cause candidates
3. Missing data
4. Compared strategies
5. Selected strategy
6. Playbook
7. Target
8. Offering
9. Online/offline channel plan
10. Owner
11. Start/end
12. Budget/cost status
13. Experiment method
14. Primary metric
15. Guardrails
16. Success condition
17. Stop condition
18. Result source
19. Limitations
20. Quality result

## 3.4 `unknown`은 0이 아니다

비용·마진·capacity·동의·추적 정보가 없으면 0이나 가능으로 추정하지 않는다.

```text
known
unknown
not_applicable
conflicting
stale
```

상태를 명시적으로 유지한다.

## 3.5 `NO_ACTION`과 `DATA_COLLECTION`은 유효한 전략이다

경제성이 없거나 데이터가 부족하면 광고·할인을 억지로 권하지 않는다.

```text
NO_ACTION
DATA_COLLECTION
CAPACITY_OPERATION
```

도 정상적인 Strategy 결과로 허용한다.

---

# 4. 목표 모듈 구조

현재 저장소에 additive하게 다음 모듈을 추가하는 방향을 권장한다.

```text
api/app/
├─ decisioning/
│  ├─ __init__.py
│  ├─ inputs/
│  │  ├─ contracts.py
│  │  ├─ readiness.py
│  │  └─ validation.py
│  ├─ causes/
│  │  ├─ taxonomy.py
│  │  ├─ low_demand.py
│  │  └─ scoring.py
│  ├─ strategies/
│  │  ├─ taxonomy.py
│  │  ├─ low_demand.py
│  │  └─ scoring.py
│  ├─ playbooks/
│  │  ├─ registry.py
│  │  ├─ applicability.py
│  │  └─ hospital_appointment.py
│  ├─ economics/
│  │  ├─ contracts.py
│  │  └─ calculator.py
│  ├─ experiments/
│  │  ├─ contracts.py
│  │  ├─ designer.py
│  │  └─ validation.py
│  ├─ packages/
│  │  ├─ assembler.py
│  │  ├─ quality.py
│  │  └─ adapter.py
│  └─ store.py
│
├─ schemas/
│  └─ decisioning.py
│
└─ api/routes/
   └─ decisioning.py
```

실제 package 이름은 로컬 구현 시작 시 현재 코드와 충돌 여부를 확인한 뒤 확정한다.

---

# 5. 단계와 의존관계

```text
Phase 0  문서·계약 정렬
   ↓
Phase 1  Decision Input Contract
   ↓
Phase 2  Cause Analysis
   ↓
Phase 3  Strategy Engine
   ↓
Phase 4  Action Playbook Registry
   ↓
Phase 5  Economics / Feasibility
   ↓
Phase 6  Experiment Design
   ↓
Phase 7  Recommendation Package / Quality Gate
   ↓
Phase 8  UI / Existing Manual Action 연결
   ↓
Phase 9  AI Explanation / Content Draft
   ↓
Phase 10 External Context
   ↓
Phase 11 Controlled Channel Execution
   ↓
Phase 12 Measurement / Learning 고도화
   ↓
Phase 13 다른 Archetype 확장
```

`Phase 9`의 AI를 앞 단계보다 먼저 구현하지 않는다.

---

# 6. Phase 0 — 문서와 상태 정렬

## 목표

현재 구현과 목표 설계를 혼동하지 않는 문서 체계를 만든다.

## 산출물

```text
docs/00_PLANNING_INDEX.md
docs/DECISION_REGISTER_V2.md
docs/LOOFIO_IMPLEMENTATION_ROADMAP_V2.md
docs/LOOFIO_DECISION_INPUT_CONTRACT_V1.md
```

기존 문서 수정 후보:

```text
CURRENT_IMPLEMENTATION_STATUS.md
docs/README.md
AGENTS.md
ARCHITECTURE.md
DEPENDENCY_RULES.md
API_CONTRACT.md
PROHIBITED_CHANGES.md
```

## 완료조건

- code baseline commit과 document alignment commit을 구분
- 구현·부분 구현·기획·미구현 상태를 명시
- 다음 우선순위가 AI Gateway가 아니라 Decision Input부터 시작
- 새 문서 간 명칭·버전·책임이 일치
- 기존 ADR 0001~0019는 수정하지 않음

## 권장 신규 ADR

```text
0020-decision-intelligence-layering.md
0021-versioned-action-playbooks.md
0022-recommendation-quality-gate.md
0023-experiment-before-execution.md
```

---

# 7. Phase 1 — Decision Input Contract

## 목표

Opportunity를 양질의 해결책으로 변환하는 데 필요한 사업 입력을 표준화한다.

## 핵심 객체

```text
DecisionContextSnapshot
BusinessGoalContext
EconomicsContext
OperationalCapacityContext
OfferingEligibilityContext
CustomerActivationContext
ChannelCapabilityContext
HistoricalActionContext
ExternalContextSummary
PolicyConstraintContext
MeasurementCapabilityContext
DecisionReadiness
```

## 구현 작업

### Contract

- Pydantic schema
- field status wrapper
- provenance
- freshness
- conflict 상태
- missing data behavior
- Hospital PII 제한

### Readiness

```text
D0 Opportunity-only
D1 Diagnostic-ready
D2 Strategy-ready
D3 Experiment-ready
D4 Economics-ready
```

### API 후보

```text
GET  /api/v1/businesses/{businessId}/decision-context
PUT  /api/v1/businesses/{businessId}/decision-context
POST /api/v1/opportunities/{opportunityId}/decision-context/preview
```

첫 구현에서는 persistence 없이 request payload 또는 in-memory preview로 시작할 수 있다.

### DB 후보

다음 migration 번호는 로컬 `main`의 마지막 번호를 다시 확인한 뒤 지정한다.

```text
business_decision_profiles
offering_economics
business_channel_capabilities
business_operational_constraints
decision_context_snapshots
```

초기 vertical slice에서는 DB 없이 Opportunity preview 요청으로 먼저 검증해도 된다.

## 테스트

- unknown과 0 구분
- tenant/business scope
- timezone
- Money decimal
- conflicting input
- stale input
- PII field reject
- missing consent
- missing capacity
- missing result source
- deterministic readiness

## 완료 Gate

```text
같은 입력 → 같은 Readiness
필수 데이터 부족 → 정확한 missing requirements
경제성 미상 → contribution 계산 금지
capacity 미상 → demand generation strategy 제한
동의 미확인 → direct customer contact 비활성화
추적 수단 없음 → executable recommendation 불가
```

---

# 8. Phase 2 — Cause Analysis

## 목표

Opportunity의 현상과 원인 가설을 분리한다.

## Cause Taxonomy v1

```text
DEMAND_DEFICIT
DISCOVERABILITY_GAP
CONVERSION_FRICTION
RETENTION_GAP
OFFER_SLOT_MISMATCH
CAPACITY_OR_OPERATION_CONSTRAINT
CANCELLATION_LEAKAGE
VALUE_OR_PRICE_FRICTION
CHANNEL_MISMATCH
DATA_QUALITY_ARTIFACT
```

## 입력

```text
Opportunity
Evidence
Limitations
Decision Context
Metric Summary
External Context(optional)
```

## 출력

```text
cause_code
hypothesis
supporting_evidence_refs
contradicting_evidence_refs
missing_data
diagnostic_questions
testability
review_priority_score
limitations
```

## 첫 적용

```text
LOW_DEMAND_SLOT
```

기본 후보:

```text
DATA_QUALITY_ARTIFACT
RETENTION_GAP
DISCOVERABILITY_GAP
OFFER_SLOT_MISMATCH
CAPACITY_OR_OPERATION_CONSTRAINT
DEMAND_DEFICIT
```

## 테스트

- evidence ref가 없는 candidate 금지
- cause를 사실형으로 단정하지 않음
- `DATA_QUALITY_ARTIFACT` 검토
- raw CSV 직접 접근 없음
- patient clinical data 사용 없음
- score를 probability로 표시하지 않음
- 동일 입력의 동일 순서

## 완료 Gate

- 최소 3개 후보 또는 후보 부족 이유
- 모든 후보에 supporting/missing data
- contradiction 보존
- diagnostic question 구조화
- Cause 결과만으로 외부 Action 실행 불가

---

# 9. Phase 3 — Strategy Engine

## 목표

원인 후보와 사업 제약을 기반으로 개입 전략을 비교한다.

## Strategy Family

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

## Strategy Score 후보

```text
Expected Net Value       25
Evidence Fit             20
Operational Feasibility  15
Measurement Feasibility  15
Policy / Brand Safety    10
Time to Impact           10
Learning Value            5
```

점수는 성공 확률이 아니다.

## 핵심 규칙

- 최소 2개 후보 비교
- 단일 후보 시 이유 기록
- `NO_ACTION`, `DATA_COLLECTION` 허용
- economics unknown 보존
- capacity/policy/consent 반영
- 채널 이름이 아니라 전략군을 먼저 선택

## LOW_DEMAND_SLOT 후보 예

```text
RETENTION_REACTIVATION
DISCOVERABILITY
CAPACITY_OPERATION
DATA_COLLECTION
NO_ACTION
```

## 테스트

- 데이터가 충분하면 최소 2개 후보
- capacity 미상 시 `CAPACITY_OPERATION` 또는 `DATA_COLLECTION` 우선 가능
- 고객 식별 없음 시 reactivation 제한
- 경제성 불가 시 paid acquisition 제외
- policy 미검토 시 direct execution 제외
- deterministic rank

## 완료 Gate

- 선택 이유와 제외 이유
- required input
- cost status
- risk
- playbook candidate
- selection version

---

# 10. Phase 4 — Action Playbook Registry

## 목표

자유형 AI 아이디어 대신 versioned 행동 라이브러리를 사용한다.

## Playbook Contract

```text
playbook_id
version
status
name
applicable_archetypes
opportunity_types
cause_codes
strategy_families
required_data
preconditions
contraindications
online_steps
offline_steps
economics_model
experiment_template
success_conditions
stop_conditions
policy_tags
owner
last_reviewed_at
```

## 상태

```text
DRAFT
VALIDATED_INTERNAL
PILOT
ACTIVE
DEPRECATED
BLOCKED
```

## Hospital Appointment 초기 Playbook

```text
PB-01 저수요 슬롯 재방문 cohort 실험
PB-02 잔여 슬롯 대기 명단 회수
PB-03 예약 확인·취소 흐름 개선
PB-04 검색 의도 기반 잔여 슬롯 포착
PB-05 예약 퍼널 마찰 제거
PB-06 현장 재예약 프로토콜
PB-07 추적 가능한 지역 제휴
PB-08 할인 없는 부가가치 실험
PB-09 Offering-시간대 재배치
PB-10 데이터 수집 실험
PB-11 Capacity 검토
PB-12 No-action monitoring
```

## 구현 순서

1. Python registry
2. applicability validator
3. fixture-based tests
4. DB persistence는 pilot 이후 검토

## 테스트

- version/status 필수
- required/precondition/contraindication
- tenant/customer/runtime value 하드코딩 금지
- online/offline step 최소 기준
- economics template
- experiment template
- policy tag
- deprecated/blocked 미선택

## 완료 Gate

최소 5개 Playbook이 `VALIDATED_INTERNAL` 상태이며 LOW_DEMAND_SLOT 후보 비교에 사용된다.

---

# 11. Phase 5 — Economics / Feasibility

## 목표

매출이 아니라 가능한 경우 순기여가치와 실행 가능성을 비교한다.

## 입력

```text
Net revenue per completion
Variable cost per completion
Benefit/discount cost
Incremental service cost
Media cost
Message cost
Partner cost
Staff time cost
Budget cap
Capacity
```

## 계산

```text
Contribution per Completion
=
Net Revenue
- Variable Cost
- Benefit Cost
- Incremental Service Cost
```

```text
Break-even Completions
=
Fixed Execution Cost
÷ Contribution per Completion
```

```text
Net Contribution Estimate
=
Incremental Completion Estimate
× Contribution per Completion
- Media Cost
- Message Cost
- Partner Cost
- Additional Staff Cost
```

## 상태

```text
complete
partial
unknown
infeasible
```

## 규칙

- unknown을 0으로 계산하지 않음
- price만 있으면 revenue-only
- 기여금액 <= 0이면 현재 조건 `infeasible`
- budget cap 없는 paid action 금지
- capacity가 없으면 추가 예약 최대치를 계산하지 않음

## 테스트

- Decimal
- KRW
- negative reject
- unknown propagation
- benefit cost 반영
- break-even rounding
- infeasible
- capacity upper bound

## 완료 Gate

모든 Strategy 후보가 최소 `economics.status`를 가진다.

---

# 12. Phase 6 — Experiment Design

## 목표

추천 행동을 실행 전 검증 가능한 계약으로 만든다.

## Experiment Contract

```text
objective
population
treatment
comparison
start_at
end_at
primary_metric
secondary_metrics
guardrails
success_threshold
stop_conditions
attribution_window
result_source
economics
evidence_grade_target
```

## 비교 방식

```text
Randomized Holdout
Alternating Time Window
Matched Historical Window
Before/After Exploratory
Partner/Channel Split
Diagnostic Review
```

## Evidence Grade

```text
A
→ 무작위 또는 강한 비교군

B
→ 합리적 비교군 / 교대 설계

C
→ 동일 요일·시간대 baseline

D
→ 단순 전후 / 수동 귀속
```

## 규칙

- primary metric 하나
- success/stop 실행 전에 고정
- result source 필수
- Grade C/D를 Incremental Revenue로 표현하지 않음
- 작은 표본이면 Grade 하향
- displacement guardrail

## 테스트

- period validation
- timezone
- treatment/comparison overlap
- primary metric
- guardrail
- success/stop
- result source
- evidence grade
- immutable after execution start

## 완료 Gate

선택된 Playbook이 실행 가능한 Experiment Draft를 생성하거나, 정확한 missing input을 반환한다.

---

# 13. Phase 7 — Recommendation Package / Quality Gate

## 목표

앞 단계의 결과를 실행 가능한 최종 패키지로 조립한다.

## Package 상태

```text
DRAFT
NEEDS_DATA
NEEDS_POLICY_REVIEW
QUALITY_REJECTED
READY_FOR_REVIEW
APPROVED
REJECTED
SUPERSEDED
```

## Package 구성

```text
diagnosis
cause_candidates
missing_information
alternative_strategies
selected_strategy
playbook
target
offering
channel_plan
execution_steps
owner
schedule
budget
economics
experiment
success_and_stop
tracking
limitations
quality
```

## Quality Score

```text
Evidence Linkage        20
Specificity             20
Economics               20
Feasibility             15
Measurement Design      15
Alternative Comparison  10
```

최종 기준:

```text
Score >= 75
AND
Hard Fail = 0
```

## Hard Fail

- general advice
- no target
- no period
- no budget or unknown status
- no owner
- no primary metric
- no success/stop
- no result source
- evidence mismatch
- invented numeric value
- capacity/policy not reviewed
- no alternatives
- tracking absent

## 기존 Recommendation adapter

품질을 통과한 Package를 기존 수동 Recommendation/Action 흐름에 연결한다.

```text
Recommendation Package
→ Legacy-compatible Recommendation Draft
→ Existing Decision
→ Existing Manual Action
```

## 테스트

- Quality score
- hard fail
- unknown economics
- evidence fidelity
- no invented values
- generic advice rejection
- legacy compatibility
- tenant isolation

## 완료 Gate

LOW_DEMAND_SLOT fixture에서 최소 하나의 `READY_FOR_REVIEW` 또는 정확한 `NEEDS_*` 결과를 재현한다.

---

# 14. Phase 8 — UI / Manual Action 연결

## 목표

운영자가 결과를 검토하고 부족한 입력을 보완한 뒤 기존 Manual Action으로 연결한다.

## Opportunity Detail UI

권장 순서:

```text
1. Observation / Estimate
2. Cause Candidates
3. Missing Information
4. Strategy Comparison
5. Selected Playbook
6. Economics / Feasibility
7. Experiment
8. Quality Result
9. Approve / Modify / Reject / Later
```

## 입력 UX

거대한 초기 폼 대신 필요 시 질문한다.

예:

```text
화요일 14~16시에 해당 Offering을 실제로 제공할 수 있습니까?
마케팅 가능한 재방문 고객군을 구분할 수 있습니까?
예약 완료를 Action과 연결할 source code가 있습니까?
할인 없이 제공할 수 있는 부가가치가 있습니까?
```

## 기존 Action 연결

- 현재 Action status 유지
- Recommendation Package reference를 optional하게 추가
- 현재 `manual` channel 유지
- 자동 실행 없음

## 완료 Gate

사용자가 30분 이내에 추가 컨설팅 없이 실행 준비를 시작할 수 있는 수준의 정보가 UI에 표시된다.

---

# 15. Phase 9 — AI Explanation / Content Draft

## 목표

이미 결정된 구조를 읽기 쉬운 설명과 실행 자산으로 변환한다.

## AI 역할

허용:

- Cause hypothesis wording
- 대안 비교 설명
- 실행 절차 설명
- 직원 스크립트 초안
- 온라인 문구 초안
- 오프라인 제휴 안내문 초안

금지:

- Metric 계산
- Cause score 계산
- Strategy rank 계산
- 비용 계산
- Experiment 결과 계산
- Quality score 계산
- patient clinical data 사용

## AI Gateway

```text
task_type
model_route
provider adapter
structured schema
PII filter
evidence fidelity validator
retry budget
fallback
audit
```

## 완료 Gate

- deterministic 숫자 mismatch = 0
- schema success
- provider 실패 시 deterministic fallback
- patient PII 없음
- cost/token audit

---

# 16. Phase 10 — External Context

## 목표

원인 확정이 아니라 가설과 Measurement limitation을 보조한다.

## 우선순위

```text
1. Holiday
2. Weather
3. Local Event
4. Trade Area / Footfall
```

## 규칙

허용:

> 비 예보가 Demand Deficit 가설을 보조합니다.

금지:

> 비 때문에 예약이 감소했습니다.

## 완료 Gate

- provider/version/valid window/geo scope
- data quality
- internal data보다 우선하지 않음
- provider 실패 시 Detector 영향 없음

---

# 17. Phase 11 — Controlled Channel Execution

## 목표

수동 실행에서 승인 기반 보조 실행으로 확장한다.

## 순서

```text
Manual
→ Copy / Export
→ Approved Connector Execution
→ Bounded Automation
```

## 필수

- explicit approval
- hard budget cap
- target scope
- start/end
- tracking identifier
- external reference
- retry/idempotency
- delivery/result event
- cancel/disable path

## 온라인

```text
CRM / approved messaging
Search Ads
Social Ads
Business Profile
Website / Landing
Booking Page
```

## 오프라인

```text
Front-desk rebooking
Waitlist
Staff callback
Partner referral
QR / source code
Tracked print
```

## 완료 Gate

추적 없는 Action은 실행할 수 없다.

---

# 18. Phase 12 — Measurement / Learning

## 목표

관찰 비교에서 점진적으로 더 신뢰할 수 있는 학습 데이터로 발전한다.

## 의미 분리

```text
Actual Revenue
Opportunity Estimate
Observed Delta
Attributed Result
Incremental Estimate
Net Contribution Estimate
Evidence Grade
```

## 초기 유지

현재 Measurement를 Grade C/D baseline으로 유지한다.

## 확장

- experiment-aware result
- treatment/comparison
- cost
- displacement
- external context
- playbook performance
- recommendation acceptance/modification
- result connection rate

## Fine-tuning 전제

다음 이전에는 fine-tuning을 우선하지 않는다.

- stable schema
- sufficient Decision→Outcome pairs
- evaluation suite
- consent/legal policy
- repeated failure pattern
- prompt baseline

---

# 19. Phase 13 — 다른 Archetype 확장

Hospital에서 공통 Core를 검증한 뒤 확장한다.

권장 순서:

```text
APPOINTMENT_PERSONAL
MEMBERSHIP_FITNESS
FIELD_MAINTENANCE
WALKIN_COMMERCE
```

새 Archetype Gate:

- Domain Contract
- Decision Input Adapter
- Metric Adapter
- Detector compatibility
- Cause mapping
- Strategy mapping
- Playbook set
- policy
- sample fixtures
- regression

---

# 20. 첫 Vertical Slice

전체를 한 번에 구현하지 않는다.

## 범위

```text
Opportunity
→ LOW_DEMAND_SLOT

Decision Input
→ capacity
→ offering eligibility
→ customer activation capability
→ channel/tracking
→ basic economics

Cause
→ 4~6 candidates

Strategy
→ RETENTION_REACTIVATION
→ DISCOVERABILITY
→ CAPACITY_OPERATION
→ DATA_COLLECTION
→ NO_ACTION

Playbook
→ PB-01
→ PB-04
→ PB-10
→ PB-11
→ PB-12

Experiment
→ holdout / historical / diagnostic

Package
→ quality validation

Execution
→ existing manual Action
```

## 제외

```text
LLM
External Context
Actual message/ad connector
Incrementality
Other Opportunity types
Other Archetypes
```

## 완료조건

1. 동일 입력에 동일 Package
2. 입력 부족 시 정확한 `NEEDS_DATA`
3. 경제성 불가 시 `NO_ACTION`
4. 일반 조언 Quality Fail
5. existing Manual Action 호환
6. cross-tenant access 불가
7. patient PII 없음

---

# 21. 로컬 구현 Backlog 순서

## Epic DI-01 — Contract

```text
DI-001 Decision field status/provenance
DI-002 Decision Context schema
DI-003 Readiness evaluator
DI-004 Missing requirement resolver
DI-005 Hospital PII validator
```

## Epic DI-02 — Cause

```text
DI-101 Cause taxonomy
DI-102 LOW_DEMAND_SLOT candidate seed
DI-103 Evidence linkage
DI-104 Diagnostic questions
DI-105 Cause score/version
```

## Epic DI-03 — Strategy

```text
DI-201 Strategy taxonomy
DI-202 Cause→Strategy mapping
DI-203 Feasibility filter
DI-204 Strategy score
DI-205 Alternative comparison
```

## Epic DI-04 — Playbook

```text
DI-301 Registry
DI-302 Applicability
DI-303 Initial 5 playbooks
DI-304 Policy tags
DI-305 Version/status
```

## Epic DI-05 — Economics / Experiment

```text
DI-401 Money/cost contract
DI-402 Contribution calculator
DI-403 Experiment contract
DI-404 Evidence Grade
DI-405 Success/stop validator
```

## Epic DI-06 — Package / Quality

```text
DI-501 Package assembler
DI-502 Quality score
DI-503 Hard Fail validator
DI-504 Legacy adapter
DI-505 Preview API
```

## Epic DI-07 — UI

```text
DI-601 Decision input questions
DI-602 Cause/strategy comparison
DI-603 Experiment summary
DI-604 Quality status
DI-605 Existing Action handoff
```

---

# 22. Definition of Done

각 Epic은 다음을 만족해야 한다.

```text
contract
deterministic implementation
version
tests
tenant scope
PII validation
API contract if exposed
migration if persisted
sample fixture
failure status
fallback
documentation
CURRENT_IMPLEMENTATION_STATUS update
```

문서 작성 또는 UI 표시만으로 완료가 아니다.

---

# 23. 당분간 하지 않는 것

```text
자동 광고 집행
자동 고객 메시지
환자 임상데이터 활용
Fine-tuning
MMM
GEO
Synthetic Consumer
Agentic Commerce
다업종 동시 구현
인과효과 보장
```

---

# 24. 최종 우선순위

```text
1. Decision Input Contract
2. LOW_DEMAND_SLOT Cause Analysis
3. Strategy Comparison
4. Playbook Registry
5. Economics / Experiment
6. Recommendation Package / Quality Gate
7. UI / Manual Action
8. AI Explanation
9. External Context
10. Controlled Execution
```
