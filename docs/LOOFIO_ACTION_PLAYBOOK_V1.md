---
title: "LOOFIO Action Playbook v1"
version: "1.0"
date: "2026-08-17"
status: "로컬 구현용 확정 설계안"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
initial_domain: "Hospital Appointment MVP"
initial_opportunity: "LOW_DEMAND_SLOT"
depends_on:
  - "LOOFIO_IMPLEMENTATION_ROADMAP_V2.md"
  - "LOOFIO_DECISION_INPUT_CONTRACT_V1.md"
  - "LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md"
  - "LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md"
  - "LOOFIO_STRATEGY_ENGINE_V1.md"
  - "LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md"
---

# LOOFIO Action Playbook v1

## 1. 문서 목적

이 문서는 Strategy Engine이 선택한 개입 방향을 **구체적이고 반복 가능하며 측정 가능한 실행 템플릿**으로 변환하는 Action Playbook 계층의 구현 계약을 정의한다.

현재 제품 경계:

```text
Opportunity
→ Cause Analysis
→ Strategy Comparison
→ Action Playbook
→ Experiment Design
→ Recommendation Package
→ User Decision
→ Manual Action
→ Result
→ Measurement
```

Playbook의 핵심 목적은 다음 문제를 막는 것이다.

```text
"홍보를 강화하세요."
"SNS를 활용하세요."
"전단지를 배포하세요."
"휴면 고객에게 연락하세요."
```

이런 문장은 방향만 있고 다음이 없다.

- 정확한 적용 조건
- 적용하면 안 되는 조건
- 대상·제외 기준
- 실행 순서
- 담당자
- 비용 구조
- 추적 수단
- 성공조건
- 중단조건
- 결과 회수 방법

핵심 원칙:

> Playbook은 일반적인 아이디어 모음이 아니라, 특정 Opportunity·Cause·Strategy·사업 제약에 적용할 수 있는 versioned 실행 계약이다.

---

# 2. v1 범위

## 2.1 초기 범위

```text
Domain
→ Hospital Appointment MVP

Primary Opportunity
→ LOW_DEMAND_SLOT

Execution mode
→ manual / copy_export / staff_operated

Automatic execution
→ 금지

AI
→ 사용하지 않음
```

## 2.2 v1 이후 확장

```text
CANCELLATION_HOTSPOT
DORMANT_CUSTOMER
SERVICE_DEMAND_GAP
approved channel connectors
playbook outcome ranking
AI asset drafting
other archetypes
```

## 2.3 비범위

Playbook Definition은 다음을 포함하지 않는다.

- 특정 tenant ID
- 특정 병원명
- 개별 환자·고객 ID
- 전화번호·이메일 원문
- 진단명·의무기록
- runtime 대상 고객 목록
- 실제 실행 예산
- 사용자 승인
- 외부 계정 credential
- 실제 성과값

이 값들은 Runtime Playbook Instance 또는 별도 실행 시스템에서 관리한다.

---

# 3. 3계층 모델

Playbook을 하나의 JSON 객체로 처리하지 않는다.

```text
PlaybookDefinition
        ↓ resolve
PlaybookApplicabilityResult
        ↓ instantiate
PlaybookInstance
        ↓ approve
Action / Execution Package
```

## 3.1 `PlaybookDefinition`

사업장과 무관한 versioned 템플릿.

포함:

```text
identity
applicability
required inputs
preconditions
contraindications
step templates
economics template
experiment template
tracking requirements
policy tags
success/stop templates
lifecycle metadata
```

## 3.2 `PlaybookApplicabilityResult`

현재 Strategy·Decision Context에 해당 Playbook을 적용할 수 있는지 평가한 결과.

포함:

```text
status
supporting refs
missing inputs
blocking conditions
limitations
fit score
fit breakdown
```

## 3.3 `PlaybookInstance`

특정 tenant/business/opportunity에 맞게 대상·Offering·기간·예산·담당자를 채운 실행 초안.

포함:

```text
definition reference
strategy/cause refs
target definition
channel plan
runtime steps
economics
experiment draft
tracking
owner
schedule
limitations
```

## 3.4 `Action / Execution Package`

사용자가 승인한 실제 실행 단위.

현재 MVP에서는 기존 manual Action으로 연결한다.

---

# 4. 정식 ID와 과거 별칭 정책

이전 기획에는 숫자형 `PB-01~PB-10`과 설명형 `PB_*_V1`이 혼재한다.

v1의 정식 식별 규칙:

```text
playbook_code
→ PB_LOW_DEMAND_REVISIT_COHORT

version
→ 1.0

playbook_id
→ PB_LOW_DEMAND_REVISIT_COHORT_V1
```

## 4.1 필드

```text
playbook_code
version
playbook_id
legacy_aliases
```

## 4.2 규칙

- 설명형 `playbook_id`가 정식 참조다.
- 숫자형 `PB-01`은 과거 문서 호환용 별칭이다.
- 새 API·DB·코드는 숫자형 별칭을 FK나 key로 사용하지 않는다.
- 동일 `playbook_code`의 version은 불변으로 보존한다.
- 의미가 달라지면 기존 version을 수정하지 않고 새 major version을 만든다.

## 4.3 예

```json
{
  "playbook_code": "PB_LOW_DEMAND_REVISIT_COHORT",
  "version": "1.0",
  "playbook_id": "PB_LOW_DEMAND_REVISIT_COHORT_V1",
  "legacy_aliases": ["PB-01"]
}
```

---

# 5. Playbook Definition Contract

```json
{
  "playbook_code": "PB_LOW_DEMAND_REVISIT_COHORT",
  "version": "1.0",
  "playbook_id": "PB_LOW_DEMAND_REVISIT_COHORT_V1",
  "legacy_aliases": ["PB-01"],
  "name": "저수요 슬롯 재방문 cohort 실험",
  "description": "재방문 가능 비식별 고객군을 목표 슬롯과 연결하는 수동 실험",
  "lifecycle": {
    "status": "DRAFT",
    "owner_role": "playbook_experiment_owner",
    "created_at": "2026-08-17",
    "last_reviewed_at": null,
    "supersedes": null,
    "superseded_by": null
  },
  "classification": {
    "strategy_family": "RETENTION_REACTIVATION",
    "strategy_class": "EXECUTION",
    "applicable_archetypes": ["APPOINTMENT_SERVICE"],
    "applicable_domains": ["APPOINTMENT_HEALTH"],
    "opportunity_types": ["LOW_DEMAND_SLOT", "DORMANT_CUSTOMER"],
    "cause_codes": ["RETENTION_GAP"]
  },
  "readiness": {
    "minimum_for_evaluation": "D2",
    "minimum_for_instantiation": "D3",
    "minimum_for_economics_ranking": "D4"
  },
  "requirements": [],
  "preconditions": [],
  "contraindications": [],
  "target_template": {},
  "channel_options": [],
  "step_templates": [],
  "economics_template": {},
  "experiment_template": "EXP_REVISIT_HOLDOUT_V1",
  "tracking_requirements": [],
  "success_condition_templates": [],
  "stop_condition_templates": [],
  "policy_tags": [],
  "output_artifacts": [],
  "validation_metadata": {
    "spec_level": "DETAILED_V1",
    "internal_fixture_status": "not_started",
    "pilot_execution_count": 0,
    "result_connection_rate": null,
    "policy_incident_count": 0
  }
}
```

---

# 6. Definition 필드

## 6.1 Identity

```text
playbook_code
version
playbook_id
legacy_aliases
name
description
```

## 6.2 Classification

```text
strategy_family
strategy_class
applicable_archetypes
applicable_domains
opportunity_types
cause_codes
```

## 6.3 Readiness

```text
minimum_for_evaluation
minimum_for_instantiation
minimum_for_economics_ranking
```

## 6.4 Requirements

각 요구조건:

```text
field_path
requirement_level
allowed_status
why_needed
missing_behavior
```

`requirement_level`:

```text
REQUIRED
OPTIONAL
BLOCKING
CONDITIONAL
```

## 6.5 Preconditions

Playbook 적용 전 반드시 참이어야 하는 사업 조건.

예:

```text
목표 슬롯이 실제 영업시간 안에 있음
Offering이 해당 슬롯에서 제공 가능
수동 실행 담당자가 존재
```

## 6.6 Contraindications

Playbook을 적용하면 안 되는 조건.

예:

```text
capacity 없음
정책 BLOCKED
최근 동일 cohort 과도한 접촉
추적 수단 없음
기여금액 음수
```

Contraindication은 일반 limitation보다 강하다.

```text
contraindication hit
→ applicability = CONTRAINDICATED
→ instance 생성 금지
```

## 6.7 Target Template

대상 정의의 구조만 제공한다.

```text
inclusion criteria
exclusion criteria
minimum sample
maximum sample
cohort unit
privacy mode
```

실제 고객 목록은 포함하지 않는다.

## 6.8 Channel Options

가능한 온라인·오프라인 실행 경로와 역할.

```text
channel_type
role
execution_mode
required_tracking
required_policy
```

## 6.9 Step Templates

각 단계의 역할·입력·산출물·완료조건.

## 6.10 Economics Template

필요 비용과 계산 가능 수준.

## 6.11 Experiment Template

Experiment Designer가 사용할 template ID.

## 6.12 Tracking Requirements

Action과 Result 연결에 필요한 최소 추적 수단.

## 6.13 Policy Tags

Hospital·개인정보·자동화 제한.

---

# 7. Step Template Contract

```json
{
  "step_id": "S01",
  "order": 1,
  "name": "목표 cohort eligibility 확인",
  "step_type": "VALIDATE",
  "owner_role": "marketer",
  "required_inputs": [
    "customer_activation.eligible_cohort_count"
  ],
  "instructions": [
    "재방문 기준을 지난 비식별 cohort 수를 확인합니다.",
    "개별 customer token은 Recommendation Package에 포함하지 않습니다."
  ],
  "output_artifacts": [
    "eligible_cohort_summary"
  ],
  "tracking_events": [],
  "completion_rule": {
    "type": "field_known",
    "field_path": "runtime.eligible_cohort_count"
  },
  "failure_behavior": "RETURN_NEEDS_DATA"
}
```

## 7.1 Step Type

```text
VALIDATE
CONFIGURE
SELECT
PREPARE
APPROVE
EXECUTE_MANUAL
VERIFY
MEASURE_SETUP
DOCUMENT
MONITOR
STOP
```

## 7.2 실패 동작

```text
RETURN_NEEDS_DATA
RETURN_NEEDS_POLICY_REVIEW
MARK_CONTRAINDICATED
SKIP_OPTIONAL
STOP_INSTANCE
```

## 7.3 원칙

- 단계는 담당자가 이해할 수 있는 동사로 시작한다.
- “홍보한다”처럼 완료 여부를 판정할 수 없는 단계 금지.
- 각 단계는 최소 하나의 completion rule 또는 output artifact를 가진다.
- 자동 실행과 수동 실행 단계를 구분한다.
- 현재 Hospital MVP의 실행 단계는 `EXECUTE_MANUAL`까지만 허용한다.

---

# 8. Playbook Lifecycle

```text
DRAFT
→ VALIDATED_INTERNAL
→ PILOT
→ ACTIVE

DRAFT / VALIDATED_INTERNAL / PILOT / ACTIVE
→ BLOCKED

VALIDATED_INTERNAL / PILOT / ACTIVE
→ DEPRECATED
```

## 8.1 `DRAFT`

문서·계약만 존재.

사용:

```text
내부 preview
fixture 설계
```

사용자 final Recommendation 후보로 표시하지 않는다.

## 8.2 `VALIDATED_INTERNAL`

필수:

- Definition 필수 section 완료
- generic advice check 통과
- applicability fixture 통과
- contraindication fixture 통과
- Experiment template 존재
- Tracking 존재
- success/stop 존재
- Hospital policy tags 존재
- PII fixture 통과

사용:

```text
내부 테스트
선택된 테스트 사업장 preview
```

## 8.3 `PILOT`

필수:

- 내부 검증 완료
- pilot owner
- 실행·결과 수집 계획
- 정책 검토
- rollback/stop 절차
- 최소 1개 실제 pilot result connection 경로

사용 범위는 지정 사업장으로 제한한다.

## 8.4 `ACTIVE`

필수:

- 완료된 pilot 결과 존재
- result source 연결 검증
- 중대한 정책 incident 없음
- 운영자가 30분 이내 실행 준비 가능
- 기대·실제 비용 필드 회수 가능
- owner 승인

v1은 고정 실행 횟수 임계값을 정하지 않는다.
향후 운영 데이터가 쌓이면 승격 정책을 versioned rule로 분리한다.

## 8.5 `DEPRECATED`

새 Instance 생성 금지.
과거 Instance·Result는 유지.

## 8.6 `BLOCKED`

정책·안전·데이터 문제로 즉시 사용 중단.
기존 실행도 운영 검토 대상.

---

# 9. Resolver 입력

```text
Strategy Run
Cause Analysis
Decision Context Snapshot
Opportunity
Playbook Registry
Policy Configuration
as_of
```

필수 Strategy handoff:

```text
selected strategy 또는 top alternatives
supporting causes
inhibitory causes
blockers
decision readiness
economics status
measurement status
policy status
slot/offering scope
candidate playbook IDs
```

---

# 10. Resolver 처리 순서

```text
1. Registry version 검증
2. Strategy family 일치
3. Opportunity / Cause 적용성
4. Archetype / Domain 적용성
5. Lifecycle status
6. Minimum readiness
7. Required / Conditional 입력
8. Preconditions
9. Contraindications
10. Policy tags
11. Tracking / Result source
12. Economics requirement
13. Experiment template availability
14. Fit Score
15. Candidate 비교
16. Provisional Playbook 선택
```

Hard Gate를 Fit Score보다 먼저 적용한다.

---

# 11. Applicability 상태

```text
ELIGIBLE
ELIGIBLE_WITH_LIMITATIONS
NEEDS_DATA
NEEDS_POLICY_REVIEW
CONTRAINDICATED
BLOCKED
NOT_APPLICABLE
DEPRECATED
```

## `ELIGIBLE`

모든 blocking 조건 충족.

## `ELIGIBLE_WITH_LIMITATIONS`

실행은 가능하지만 economics·measurement가 제한적.

예:

```text
Revenue-only
Evidence Grade C
수동 실행만 가능
```

## `NEEDS_DATA`

Required/Blocking 입력 부족.

## `NEEDS_POLICY_REVIEW`

정책 status가 approved가 아님.

## `CONTRAINDICATED`

명시적 적용 금지 조건 발생.

## `BLOCKED`

Registry status 또는 critical safety issue.

## `NOT_APPLICABLE`

Strategy·Opportunity·Cause·Domain 불일치.

## `DEPRECATED`

과거 reference만 허용.

---

# 12. Playbook Fit Score v1

Fit Score는 Hard Gate를 통과한 다음 상태에서만 계산한다.

```text
ELIGIBLE
ELIGIBLE_WITH_LIMITATIONS
```

## 12.1 구성

```text
Strategy / Cause Fit      25
Input Completeness        20
Operational Fit           15
Measurement Fit           15
Economics Fit             10
Policy Safety             10
Time to Launch             5
Total                    100
```

## 12.2 의미

> 동일 Strategy 안에서 어떤 Playbook을 먼저 구체화할지 정하는 우선순위.

다음 의미가 아니다.

```text
성공 확률
ROI
인과효과
매출 증가율
```

## 12.3 선택 기준

```text
minimum_fit_score = 70
```

단일 선택:

```text
top >= 70
AND
top - second >= 5
```

복수 옵션:

```text
top >= 70
AND
top - second < 5
```

기준 미달:

```text
Playbook resolver가 억지로 선택하지 않음
→ Strategy Engine에 NEEDS_DATA / NO_APPLICABLE_PLAYBOOK 반환
```

---

# 13. Fit Factor 규칙

## 13.1 Strategy / Cause Fit — 25

- Strategy family 정확히 일치
- PRIMARY supporting Cause
- inhibitory Cause 없음
- Opportunity segment 일치

## 13.2 Input Completeness — 20

- Required 충족
- Optional coverage
- stale/conflicting 없음
- blocking input 충족

## 13.3 Operational Fit — 15

- capacity
- Offering availability
- owner
- 실행 준비시간
- staff/room/equipment

## 13.4 Measurement Fit — 15

- primary metric
- tracking
- result source
- comparison method
- 예상 Evidence Grade

## 13.5 Economics Fit — 10

- 비용 구조가 현재 context와 맞음
- unknown을 0으로 처리하지 않음
- 유료/혜택 Playbook은 budget cap과 cost 필요
- 비유료 diagnostic Playbook은 `not_applicable`로 정상 처리

## 13.6 Policy Safety — 10

- Hospital policy approved
- consent
- no clinical targeting
- no prohibited claims
- manual approval

## 13.7 Time to Launch — 5

```text
<= 3 business days → 1.00
<= 7 business days → 0.75
<= 14 days         → 0.50
> 14 days          → 0.25
unknown            → 0.25 + limitation
```

---

# 14. Playbook Instance Contract

```json
{
  "instance_id": "PBI_xxx",
  "instance_version": "playbook-instance-v1",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "opportunity_id": "OPP_01",
  "cause_analysis_id": "CAUSE_01",
  "strategy_run_id": "STRATEGY_01",
  "playbook_id": "PB_LOW_DEMAND_REVISIT_COHORT_V1",
  "definition_version": "1.0",
  "status": "DRAFT",
  "target": {
    "inclusion": [],
    "exclusion": [],
    "estimated_size": 72,
    "privacy_mode": "aggregate"
  },
  "offering_scope": [],
  "slot_scope": {
    "weekday": "TUE",
    "start_hour": 14,
    "end_hour": 16
  },
  "channel_plan": [],
  "runtime_steps": [],
  "economics": {},
  "experiment_draft": {},
  "tracking": {},
  "owner": "marketer",
  "planned_start_at": null,
  "planned_end_at": null,
  "limitations": [],
  "fit": {
    "version": "playbook-fit-v1",
    "score": 82,
    "breakdown": {}
  }
}
```

## Instance 상태

```text
DRAFT
NEEDS_DATA
NEEDS_POLICY_REVIEW
READY_FOR_EXPERIMENT
READY_FOR_RECOMMENDATION
SUPERSEDED
CANCELLED
```

Instance 자체는 Action이 아니다.
사용자 승인 후 기존 Action 또는 미래 Execution Package로 변환한다.

---

# 15. Target Contract

## 필수

```text
target_type
inclusion
exclusion
estimated_size
minimum_size
maximum_size(optional)
privacy_mode
source_refs
```

## Privacy Mode

```text
aggregate
tokenized_internal
external_system_managed
```

Hospital Recommendation Package의 기본값:

```text
aggregate
```

개별 contact 정보는 기존 적법한 CRM 또는 실행 환경에서만 처리한다.

## 제외 기준 예

```text
최근 동일 Action 접촉
동의 거부
target Offering 부적합
이미 목표 슬롯 예약
최근 과도한 메시지
정책상 제외
```

---

# 16. Channel Plan Contract

```text
channel_type
role
execution_mode
owner
start/end
tracking
budget cap
asset requirements
approval status
limitations
```

Channel Role:

```text
DISCOVER
CONVERT
RETAIN
RECOVER
VERIFY
MEASURE
```

현재 실행 모드:

```text
manual
copy_export
staff_operated
```

미구현:

```text
approved_connector
automatic
```

---

# 17. Tracking Contract

모든 실행형 Playbook은 최소 하나를 요구한다.

```text
UTM
unique_url
booking_source_code
coupon_code
partner_code
QR
action_id
manual_source_tag
```

Tracking 필드:

```text
tracking_type
tracking_value
source_system
verification_status
test_event_at
result_linkage
```

## 규칙

- `tracking = none`이면 실행형 Instance는 `NEEDS_DATA`.
- Tracking setup 자체는 `PB_LOW_DEMAND_TRACKING_SETUP_V1`로 전환 가능.
- 대량 전단·제휴·현장 안내도 배포처·제휴처별 추적이 없으면 final Recommendation 불가.
- test event를 검증하기 전 `READY_FOR_RECOMMENDATION` 금지.

---

# 18. Economics Template

```text
cost_components
revenue_inputs
contribution_inputs
budget_requirement
break_even_rule
unknown_behavior
infeasible_rule
```

Cost Component:

```text
media
message
benefit
partner
staff_time
additional_service
production
other
```

## 규칙

- 비용 `unknown`을 0으로 처리하지 않는다.
- 비용이 발생하지 않는 diagnostic Playbook은 economics=`not_applicable`.
- 혜택·광고·제휴 Playbook은 budget cap 필수.
- 기여금액 <= 0이면 해당 조건 `CONTRAINDICATED` 또는 `INFEASIBLE`.
- price만 있으면 revenue-only.
- Hospital price mode가 insured/variable이면 단순 list price 기반 과장 금지.

---

# 19. Experiment Template 연결

Playbook은 실험 전체를 확정하지 않고 다음 default를 제공한다.

```text
template_id
supported_methods
default_primary_metric
secondary_metric candidates
guardrail candidates
success template
stop template
evidence grade ceiling
minimum sample guidance
```

Experiment Designer가 runtime context를 반영해 최종 Draft를 만든다.

## 원칙

- 성공·중단조건 없는 Playbook Instance 금지.
- result source 없는 실행형 Playbook 금지.
- Grade C/D 결과를 Incremental Revenue로 표현하지 않는다.
- 실행 시작 후 성공조건을 조용히 바꾸지 않는다.

---

# 20. Policy Tags v1

```text
HOSPITAL_MANUAL_APPROVAL_REQUIRED
NO_AUTOMATIC_EXTERNAL_EXECUTION
NO_CLINICAL_TARGETING
NO_PATIENT_PII_IN_PACKAGE
NO_MEDICAL_OUTCOME_GUARANTEE
NO_UNVERIFIED_BEFORE_AFTER_CLAIM
CONSENT_REQUIRED_FOR_DIRECT_CONTACT
TRACKING_REQUIRED
RESULT_SOURCE_REQUIRED
BUDGET_CAP_REQUIRED_FOR_PAID_ACTION
ECONOMICS_REQUIRED_FOR_DISCOUNT_OR_BENEFIT
```

Policy Tag는 실제 법적 적합성을 자동 보장하지 않는다.
정책 검토가 필요한 항목을 코드와 UI에서 차단하기 위한 내부 안전 태그다.

---

# 21. Output Artifact

Playbook별로 실행자가 생성해야 할 결과물.

예:

```text
data_quality_review
capacity_confirmation
eligible_cohort_summary
booking_path_checklist
staff_script
partner_code_map
tracking_test_result
experiment_draft
stop_rule_sheet
```

모든 Step은 필요한 경우 Artifact와 연결한다.

---

# 22. Registry Contract

Registry는 현재 Python static registry로 시작한다.

```text
get(playbook_id)
list_by_strategy(strategy_family)
list_by_opportunity(opportunity_type)
resolve_candidates(strategy_run)
validate_definition(playbook)
```

## DB 전환 조건

다음이 필요해질 때 persistence를 검토한다.

- 운영 UI에서 Playbook 관리
- tenant별 허용/차단 정책
- lifecycle 승격 승인
- rollout scope
- historical execution 통계
- 긴급 BLOCKED 처리

DB 후보:

```text
playbook_definitions
playbook_versions
playbook_rollout_scopes
playbook_policy_tags
```

Definition 내용은 JSONB만으로 숨기지 않고 검색·필터 핵심 필드는 일반 컬럼을 둔다.

---

# 23. API 후보

## Registry 조회

```text
GET /api/v1/playbooks
GET /api/v1/playbooks/{playbookId}
```

현재는 내부/관리 API로 제한 가능.

## Resolver Preview

```text
POST /api/v1/strategy-runs/{strategyRunId}/playbooks/preview
```

Request:

```json
{
  "decision_context": {},
  "as_of": "2026-08-17T16:00:00+09:00"
}
```

Response:

```text
applicability results
fit scores
selected/top alternatives
missing inputs
blockers
```

## Instance Preview

```text
POST /api/v1/playbooks/{playbookId}/instances/preview
```

Persistence는 다음 단계에서 추가한다.

기존 `/recommendations/draft`는 유지한다.

---

# 24. Determinism과 Versioning

동일 입력:

```text
Strategy Run
Cause Analysis
Decision Context
Playbook Registry version
Playbook Definition version
Resolver version
Fit Score version
as_of
```

동일 결과:

- candidate set
- applicability
- blockers
- fit score
- order
- selected/top alternatives
- runtime step skeleton

과거 Instance를 새 Definition으로 재해석하지 않는다.

---

# 25. 오류 계약

```text
PLAYBOOK_NOT_FOUND
PLAYBOOK_DEPRECATED
PLAYBOOK_BLOCKED
PLAYBOOK_NOT_APPLICABLE
PLAYBOOK_INPUT_REQUIRED
PLAYBOOK_POLICY_REVIEW_REQUIRED
PLAYBOOK_CONTRAINDICATED
PLAYBOOK_TRACKING_REQUIRED
PLAYBOOK_RESULT_SOURCE_REQUIRED
PLAYBOOK_ECONOMICS_REQUIRED
PLAYBOOK_EXPERIMENT_TEMPLATE_MISSING
NO_APPLICABLE_PLAYBOOK
TENANT_SCOPE_MISMATCH
PII_FIELD_REJECTED
UNSUPPORTED_PLAYBOOK_VERSION
PLAYBOOK_RESOLVER_INTERNAL_ERROR
```

기존 Error Envelope를 따른다.

---

# 26. 테스트 전략

## Definition Validation

- ID/code/version unique
- required sections
- stable alias
- lifecycle
- strategy/opportunity/cause
- readiness
- experiment template
- success/stop
- policy tags
- output artifact

## Applicability

- strategy mismatch
- cause mismatch
- readiness 부족
- precondition
- contraindication
- policy
- tracking
- result source
- economics

## Fit Score

- factor clamp
- hard gate before score
- fixed weights
- null handling
- tie-break
- minimum score
- multiple option

## Instance

- tenant/business scope
- no PII
- aggregate target
- deterministic steps
- owner/schedule
- result source
- tracking test

## Regression

- Opportunity/Strategy result 불변
- 기존 Recommendation/Action/Result/Measurement 불변
- no automatic execution

---

# 27. 로컬 구현 Backlog

## PB-001 — Contract

- Definition schema
- Instance schema
- Applicability schema
- Step schema

## PB-002 — ID / Alias

- canonical code
- version
- legacy alias map
- uniqueness

## PB-003 — Registry

- static registry
- query
- validation
- registry version

## PB-004 — Lifecycle

- status
- promotion rules
- blocked/deprecated

## PB-005 — Requirement / Gate

- readiness
- precondition
- contraindication
- policy
- tracking
- economics

## PB-006 — Fit Score

- factors
- threshold
- tie-break
- alternative result

## PB-007 — Instance Builder

- runtime target
- channel plan
- steps
- economics
- experiment skeleton

## PB-008 — Preview API

- resolver
- instance preview
- auth/tenant
- PII reject

## PB-009 — Catalog

- detailed core playbooks
- expansion index
- legacy alias
- fixtures

## PB-010 — Regression

- Strategy handoff
- existing manual Action adapter
- sample pack

---

# 28. 완료조건

Action Playbook Framework v1 완료조건:

1. Definition / Applicability / Instance 분리
2. canonical ID와 legacy alias 정책
3. lifecycle과 승격 Gate
4. Required/Optional/Blocking/Conditional
5. precondition/contraindication
6. step completion rule
7. tracking/result source
8. economics unknown 처리
9. experiment template
10. policy tags
11. fit score version
12. deterministic resolver
13. Hospital PII 미포함
14. 자동 실행 없음
15. 기존 Manual Action 호환
16. code 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 29. 구현 연결

Playbook별 Experiment Template과 Recommendation Package 계약은 완료됐다.

로컬 구현 순서:

```text
PB-001~PB-010
→ PBC-001~PBC-009
→ EX-001~EX-015
→ EXM-001~EXM-010
```

Core 12개 Playbook은 모두 `DRAFT`에서 시작하며, 문서 존재만으로 `VALIDATED_INTERNAL`, `PILOT`, `ACTIVE`로 승격하지 않는다.
