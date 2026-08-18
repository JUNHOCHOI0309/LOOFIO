---
title: "LOOFIO Recommendation Package v2"
version: "2.0"
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
  - "LOOFIO_ACTION_PLAYBOOK_V1.md"
  - "LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md"
  - "LOOFIO_EXPERIMENT_DESIGN_V1.md"
  - "LOOFIO_PLAYBOOK_EXPERIMENT_MAPPING_V1.md"
---

# LOOFIO Recommendation Package v2

## 1. 문서 목적

이 문서는 Opportunity부터 Experiment까지의 구조화된 결과를 사용자가 실제로 검토·수정·승인할 수 있는 **최종 Action Plan Package**로 조립하는 계약을 정의한다.

LOOFIO가 고객에게 판매해야 하는 것은 다음과 같은 일반 조언이 아니다.

```text
홍보를 강화하세요.
SNS를 활용하세요.
전단지를 배포하세요.
휴면 고객에게 연락하세요.
```

최종 결과는 최소한 다음에 답해야 한다.

```text
무엇이 관측됐는가
어떤 원인 가설을 검토했는가
어떤 대안을 비교했는가
왜 이 전략과 Playbook을 선택했는가
누구에게·무엇을·언제·어떻게 실행하는가
온라인과 오프라인 채널은 각각 어떤 역할을 하는가
비용과 경제성은 어느 수준까지 확인됐는가
어떤 방식으로 비교하고 측정하는가
무엇을 성공·중단 조건으로 보는가
현재 모르는 것과 한계는 무엇인가
```

핵심 원칙:

> Recommendation Package는 AI가 자유롭게 쓴 보고서가 아니다.
> Opportunity·Cause·Strategy·Playbook·Economics·Experiment의 versioned 결과를 보존하면서 사용자가 바로 실행 판단을 내릴 수 있도록 조립한 구조화 의사결정 문서다.

---

# 2. 현재 구현과의 관계

현재 GitHub `main`에는 다음 흐름이 구현되어 있다.

```text
Opportunity
→ Deterministic Recommendation Draft
→ Recommendation Decision
→ Manual Action
→ Action Result
→ same-window-prior-four-weeks-v2 Measurement
```

현재 Recommendation 필드:

```text
hypothesis
action_type
channel
target_segment
expected_effect(optional)
confidence
explanation
limitations
```

Recommendation Package v2는 이를 즉시 제거하지 않는다.

```text
Recommendation Package v2
→ Quality Gate
→ Legacy-compatible Recommendation Adapter
→ 기존 Decision
→ 기존 Manual Action
```

기존 `/recommendations/draft`는 fallback과 회귀 기준으로 유지한다.

---

# 3. 파이프라인 위치

```text
Opportunity
+ Decision Context Snapshot
+ Cause Analysis
+ Strategy Run
+ Playbook Instance
+ Economics / Feasibility
+ Experiment Definition
        ↓
Recommendation Package Assembler
        ↓
Package Draft
        ↓
Recommendation Quality Validator
        ↓
READY_FOR_REVIEW 또는 NEEDS_*/QUALITY_REJECTED
        ↓
User Decision
        ↓
Manual Action / future Execution Package
```

Assembler는 Metric·Cause Score·Strategy Score·Playbook Fit·Experiment Result를 다시 계산하지 않는다.

---

# 4. Source of Truth

Package는 다음 source reference를 필수로 가진다.

```text
opportunity_id
opportunity_detector_version
opportunity_score_version
decision_context_snapshot_id / contract_version
cause_analysis_id / version
strategy_run_id / version
playbook_instance_id
playbook_id / definition_version
experiment_definition_id / template_version
quality_result_id / validator_version
```

Source가 persistence되지 않은 Preview 단계에서는 다음을 대신 저장한다.

```text
source type
input hash
version
generated_at
```

Package 본문에 복사한 숫자보다 원본 source reference가 우선한다.

---

# 5. Package Type

Strategy Class를 기반으로 네 종류를 사용한다.

```text
EXECUTION
OPERATIONAL
DIAGNOSTIC
HOLD
```

## `EXECUTION`

고객·예약 경로·Offering·제휴 등에 실제 개입하는 패키지.

예:

```text
RETENTION_REACTIVATION
DISCOVERABILITY
CONVERSION
OFFER_PACKAGING
PARTNERSHIP_REFERRAL
ACQUISITION
CANCELLATION_RECOVERY
```

## `OPERATIONAL`

직원·capacity·Offering·예약 가능 상태를 조정·검증하는 패키지.

예:

```text
CAPACITY_OPERATION
```

## `DIAGNOSTIC`

결정에 필요한 데이터·Tracking·정책·경제성 입력을 보완하는 패키지.

예:

```text
DATA_COLLECTION
```

## `HOLD`

현재 실행하지 않고 Metric과 재평가 Trigger를 관리하는 패키지.

예:

```text
NO_ACTION
```

Package Type에 따라 일부 필드의 의미가 달라지지만, 일반 조언을 허용하는 것은 아니다.

---

# 6. Package Lifecycle

```text
DRAFT
NEEDS_DATA
NEEDS_POLICY_REVIEW
QUALITY_REJECTED
READY_FOR_REVIEW
APPROVED
REJECTED
DEFERRED
SUPERSEDED
CANCELLED
```

## `DRAFT`

Assembler가 생성했지만 Quality 평가 전이거나 아직 수정 중.

## `NEEDS_DATA`

실행 또는 실험을 완성하는 필수 입력이 부족.

반드시 다음을 포함한다.

```text
missing field path
why needed
owner
collection method
completion rule
unblocked stage
```

## `NEEDS_POLICY_REVIEW`

Hospital 정책·동의·Offering 마케팅 적합성 검토가 필요.

## `QUALITY_REJECTED`

Hard Fail이 있거나 Score·section floor를 통과하지 못함.

고객의 최종 실행 추천으로 표시하지 않는다.

## `READY_FOR_REVIEW`

다음 조건을 모두 만족한다.

```text
Quality PASSED
Hard Fail = 0
Required upstream source ready
사용자에게 숨겨진 blocking input 없음
```

이는 승인이나 효과 보장을 뜻하지 않는다.

## `APPROVED`

권한 있는 사용자가 승인.

## `REJECTED`

사용자가 실행하지 않기로 결정.

## `DEFERRED`

`later` 결정.
재검토 시 freshness와 capacity·policy·economics를 다시 검증한다.

## `SUPERSEDED`

수정으로 새 Package version이 생성됐거나 새 Opportunity/Context 결과가 우선함.

## `CANCELLED`

실행 전 운영상 취소.

---

# 7. Package Object Model

```text
RecommendationPackageDraft
        ↓ evaluate
RecommendationQualityResult
        ↓ if passed
RecommendationPackageVersion
        ↓ decide
RecommendationPackageDecision
        ↓ approve
Action / Experiment Run
```

## 7.1 `RecommendationPackageDraft`

Assembler 출력.
Quality 통과 전이다.

## 7.2 `RecommendationQualityResult`

Deterministic validator 결과.

## 7.3 `RecommendationPackageVersion`

Source reference와 내용이 고정된 검토 단위.

## 7.4 `RecommendationPackageDecision`

기존 Decision 의미를 유지한다.

```text
approved
rejected
modified
later
```

`modified`는 원본 Package를 직접 수정하지 않고 새 Version을 생성한다.

---

# 8. 전체 Output Contract

```json
{
  "id": "RPKG_xxx",
  "public_id": "RPKG-20260817-0001",
  "package_version": "recommendation-package-v2",
  "revision": 1,
  "status": "READY_FOR_REVIEW",
  "package_type": "EXECUTION",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "location_id": "LOC_01",
  "created_at": "2026-08-17T17:00:00+09:00",
  "valid_until": "2026-08-24T17:00:00+09:00",
  "sources": {},
  "executive_summary": {},
  "diagnosis": {},
  "missing_information": [],
  "alternatives": [],
  "selected_plan": {},
  "economics": {},
  "experiment": {},
  "success_and_stop": {},
  "tracking": {},
  "assumptions": [],
  "limitations": [],
  "quality": {},
  "decision": null
}
```

---

# 9. Sources Contract

```json
{
  "opportunity": {
    "id": "OPP_01",
    "type": "LOW_DEMAND_SLOT",
    "detector_version": "low-demand-revenue-gap-v2",
    "score_version": "opportunity-score-v1",
    "evidence_refs": ["EVID_01", "EVID_02"]
  },
  "decision_context": {
    "snapshot_id": "DCTX_01",
    "contract_version": "decision-input-v1",
    "input_hash": "..."
  },
  "cause_analysis": {
    "id": "CAUSE_01",
    "version": "cause-analysis-v1"
  },
  "strategy_run": {
    "id": "STRATEGY_01",
    "version": "strategy-engine-v1",
    "score_version": "strategy-priority-v1"
  },
  "playbook": {
    "instance_id": "PBI_01",
    "playbook_id": "PB_LOW_DEMAND_REVISIT_COHORT_V1",
    "definition_version": "1.0",
    "fit_version": "playbook-fit-v1"
  },
  "experiment": {
    "id": "EXP_01",
    "definition_version": "experiment-definition-v1",
    "template_id": "EXP_REVISIT_HOLDOUT_V1"
  }
}
```

## 규칙

- ID·version·hash 없이 자연어만 복사하지 않는다.
- Package에서 Observation 숫자를 변경하지 않는다.
- AI가 source reference를 새로 만들지 않는다.
- source가 stale 또는 superseded면 Package 재검증이 필요하다.

---

# 10. Executive Summary Contract

사용자에게 처음 보여주는 요약.

```text
headline
why_now
selected_strategy
selected_playbook
expected_decision
execution_mode
confidence_and_limits
```

예:

```json
{
  "headline": "화요일 14~16시 저수요 슬롯에 대해 재방문 cohort 수동 실험을 우선 검토합니다.",
  "why_now": "최근 12주 중 반복적으로 수요가 낮았고, 해당 시간대 capacity와 Offering 제공 가능 상태가 확인됐습니다.",
  "selected_strategy": "RETENTION_REACTIVATION",
  "selected_playbook": "PB_LOW_DEMAND_REVISIT_COHORT_V1",
  "expected_decision": "2주 수동 비교 실험 승인 여부",
  "execution_mode": "manual",
  "confidence_and_limits": "재방문 cohort와 운영 가능성은 확인됐으나 변동원가가 없어 순기여이익은 계산하지 않습니다."
}
```

금지:

```text
매출을 늘릴 최적의 전략입니다.
성공 가능성이 74%입니다.
예상 매출이 반드시 발생합니다.
```

---

# 11. Diagnosis Contract

```text
observations
estimates
cause_candidates
selected_cause_context
contradictions
missing_information
limitations
```

## 11.1 Observation

Opportunity의 실제 관측값을 그대로 참조한다.

```json
{
  "reference": "OPP_01:EVID_01",
  "statement": "화요일 14~16시의 주당 평균 예약은 1.7건입니다.",
  "value": 1.7,
  "unit": "appointments_per_week",
  "source_type": "observation"
}
```

## 11.2 Estimate

```json
{
  "reference": "OPP_01:ESTIMATE",
  "statement": "비교 시간대 수준을 가정한 잠재 가치 범위입니다.",
  "value_low": {
    "amount": "380000.00",
    "currency": "KRW"
  },
  "value_high": {
    "amount": "460000.00",
    "currency": "KRW"
  },
  "assumptions": [],
  "source_type": "estimate"
}
```

Estimate를 실제 손실이나 예상 Action 결과로 변환하지 않는다.

## 11.3 Cause Candidate

최소 상위 후보와 반대 근거를 함께 표시한다.

```text
cause code
hypothesis
review priority
supporting evidence
contradicting evidence
missing data
```

Cause를 확정 원인으로 표시하지 않는다.

---

# 12. Missing Information Contract

```json
{
  "field_path": "economics.variable_cost_per_completion",
  "status": "unknown",
  "why_needed": "순기여이익과 유료 대안의 경제성을 비교하기 위해 필요합니다.",
  "blocking_scope": [
    "net_contribution",
    "ACQUISITION"
  ],
  "owner": "business_owner",
  "collection_method": "manual_input",
  "completion_rule": "known money with source",
  "priority": "blocking"
}
```

## 규칙

- “정보가 부족합니다”만 표시하지 않는다.
- 필드·목적·담당자·수집 방법·해제되는 기능을 명시한다.
- Package가 `NEEDS_DATA`이면 최소 하나의 blocking item이 있어야 한다.
- `READY_FOR_REVIEW` Package에는 숨겨진 blocking item이 없어야 한다.

---

# 13. Alternative Strategy Contract

최소 두 개 Strategy를 비교하거나 단일 후보 이유를 기록한다.

```json
{
  "rank": 1,
  "strategy_family": "RETENTION_REACTIVATION",
  "status": "ELIGIBLE_WITH_LIMITATIONS",
  "score": 74.25,
  "score_version": "strategy-priority-v1",
  "selected": true,
  "supporting_cause_refs": ["CAUSE_01:RETENTION_GAP"],
  "why_considered": "재방문 가능한 cohort와 목표 슬롯 capacity가 확인됐습니다.",
  "why_selected_or_rejected": "저비용 수동 비교가 가능해 1순위로 검토합니다.",
  "economics_status": "partial",
  "measurement_status": "grade_b_possible",
  "policy_status": "approved_manual_only",
  "playbook_candidates": ["PB_LOW_DEMAND_REVISIT_COHORT_V1"],
  "limitations": []
}
```

## 필수 비교

```text
선택 전략 vs 2위 전략
선택 전략 vs NO_ACTION
유료 전략이면 저비용·운영 전략
```

## 비교 차원

```text
evidence fit
expected net value
fixed / variable cost
capacity fit
policy risk
measurement strength
time to learning
operational burden
audience scope
reusability
```

현재 Context에 연결하지 않은 일반 장단점은 충분하지 않다.

---

# 14. Selected Plan Contract

```text
strategy
playbook
objective
target
offering_scope
slot_scope
channel_plan
execution_steps
output_artifacts
owner
schedule
budget
approval requirements
```

## 14.1 Objective

한 문장으로 무엇을 검증하는지 표현한다.

예:

> 재방문 가능 cohort에 대한 1회 수동 실행이 화요일 14~16시 완료 예약에 영향을 주는지 검증한다.

## 14.2 Target

```text
target_type
inclusion
exclusion
estimated_size
privacy_mode
source refs
```

개별 PII를 포함하지 않는다.

## 14.3 Offering / Slot

```text
offering IDs and names
weekday
start/end hour
capacity confirmation
policy status
```

## 14.4 Owner

```text
role
optional user reference
responsibilities
handoff condition
```

Owner가 없으면 실행형 Package는 Hard Fail이다.

---

# 15. Channel Plan

온라인과 오프라인을 단순 나열하지 않고 각 역할을 정의한다.

```json
[
  {
    "channel_type": "MANUAL_CRM_REVIEW",
    "role": "RETAIN",
    "execution_mode": "manual",
    "owner": "marketer",
    "tracking_type": "action_id",
    "budget_cap": null,
    "policy_status": "approved_manual_only",
    "asset_requirements": [
      "approved_message_draft",
      "target_slot_booking_path"
    ]
  },
  {
    "channel_type": "BOOKING_PAGE",
    "role": "CONVERT",
    "execution_mode": "staff_operated",
    "owner": "operations",
    "tracking_type": "booking_source_code",
    "budget_cap": null,
    "policy_status": "approved",
    "asset_requirements": [
      "target_slot_link"
    ]
  }
]
```

## 규칙

- Primary channel과 support channel의 역할을 구분한다.
- 유료 채널은 budget cap과 economics가 필요하다.
- Tracking이 없는 채널은 final execution plan에 포함하지 않는다.
- 현재 MVP는 `manual`, `copy_export`, `staff_operated`만 허용한다.
- `approved_connector`, `automatic`은 미구현이다.

---

# 16. Execution Step Contract

```json
{
  "step_id": "S03",
  "order": 3,
  "name": "Treatment와 Holdout을 고정한다",
  "step_type": "CONFIGURE",
  "owner": "marketer",
  "instructions": [
    "승인된 assignment rule을 사용합니다.",
    "실험 시작 후 대상을 재배정하지 않습니다."
  ],
  "required_inputs": [
    "experiment.assignment"
  ],
  "output_artifacts": [
    "assignment_summary"
  ],
  "completion_rule": {
    "type": "artifact_verified",
    "artifact": "assignment_summary"
  },
  "failure_behavior": "STOP_INSTANCE"
}
```

## 최소 실행형 Package 기준

- 완료 판정 가능한 Step 3개 이상
- 실행 전 검증 Step
- Tracking/Measurement setup Step
- 실제 수동 실행 Step
- Result 회수 Step
- 중단 시 처리 Step

“홍보한다” 한 줄은 실행 단계가 아니다.

---

# 17. Output Artifact Contract

실행자가 준비·검증해야 하는 산출물.

```text
capacity_confirmation
eligible_cohort_summary
approved_asset
booking_path
tracking_test_result
assignment_summary
partner_code_map
experiment_definition
stop_rule_sheet
result_collection_checklist
```

각 Artifact:

```text
artifact_type
owner
status
source reference
verified_at
limitations
```

실행형 Package가 `READY_FOR_REVIEW`가 되려면 blocking Artifact의 생성 경로가 정의돼 있어야 한다.

---

# 18. Economics Contract

```json
{
  "status": "partial",
  "currency": "KRW",
  "estimated_opportunity_value": {
    "source": "opportunity_estimate",
    "value_low": "380000.00",
    "value_high": "460000.00"
  },
  "planned_costs": [
    {
      "cost_type": "staff_time",
      "status": "unknown",
      "amount": null,
      "source": null
    }
  ],
  "budget_cap": {
    "status": "known",
    "amount": "120000.00",
    "currency": "KRW"
  },
  "contribution_per_completion": {
    "status": "unknown",
    "amount": null
  },
  "break_even_completions": null,
  "net_contribution_estimate": null,
  "limitations": [
    "변동원가가 없어 순기여이익을 계산하지 않습니다."
  ]
}
```

## 상태

```text
complete
partial
unknown
not_applicable
infeasible
```

## 의미 분리

```text
Actual Revenue
Opportunity Estimate
Expected Effect
Observed Delta
Incremental Estimate
Net Contribution Estimate
```

를 같은 필드로 합치지 않는다.

## Package Type별 경제성

### EXECUTION

비용 상태와 budget cap 필수.
비용-bearing이면 complete 또는 허용된 partial 정책 필요.

### OPERATIONAL

직원 시간·운영비가 있으면 표시.
매출 효과가 목적이 아니면 `not_applicable` 가능.

### DIAGNOSTIC

수집·검토 비용과 보완될 의사결정 범위를 표시.
매출 효과를 요구하지 않는다.

### HOLD

실행하지 않는 이유와 불필요한 지출 회피를 정성적으로 표시.
가상의 “절감 매출”을 만들지 않는다.

---

# 19. Experiment Contract

Package는 Experiment Definition을 요약하되 핵심 계약을 보존한다.

```text
experiment_id
template_id/version
method
evidence grade ceiling
precision status
population
assignment
treatment
comparison
schedule
primary metric
secondary metrics
guardrails
success threshold
stop conditions
attribution window
result source
approval status
```

## 규칙

- Primary Metric은 하나.
- Success/Stop은 실행 전에 고정.
- Grade C/D를 Incremental Revenue로 표현하지 않는다.
- Precision과 Grade를 분리.
- Experiment가 `NEEDS_DATA`이면 실행형 Package도 `NEEDS_DATA`.
- `NO_ACTION` Package도 monitoring experiment를 가진다.

---

# 20. Success and Stop Contract

사용자가 Package만 읽고도 유지·중단 조건을 알 수 있어야 한다.

```json
{
  "success_conditions": [
    {
      "source": "experiment.success_threshold",
      "description": "Treatment와 비교군의 목표 슬롯 완료 재방문율 차이가 승인한 최소 기준 이상",
      "metric_code": "completed_revisit_appointments_in_target_slot"
    }
  ],
  "stop_conditions": [
    {
      "condition_code": "COMPLAINT_THRESHOLD",
      "severity": "HARD",
      "action": "STOP_NEW_EXPOSURE"
    },
    {
      "condition_code": "CAPACITY_BREACH",
      "severity": "HARD",
      "action": "PAUSE_AND_REVIEW"
    }
  ],
  "review_at": "2026-09-04T10:00:00+09:00"
}
```

Threshold 숫자가 정해지지 않았다면 `READY_FOR_REVIEW`가 될 수 없다.

---

# 21. Tracking Contract

```text
tracking type
tracking value/reference
verification status
test event
result linkage
source system
```

## 규칙

- 실행형 Package에서 Tracking `none`은 Hard Fail.
- Test event 미검증은 `NEEDS_DATA`.
- Partner·Print·Offline 실행도 partner code·QR·manual source tag가 필요하다.
- Tracking 값에 PII를 넣지 않는다.
- 다른 tenant와 공유되는 code를 사용하지 않는다.

---

# 22. Assumption Contract

```json
{
  "assumption_id": "A-001",
  "statement": "목표 슬롯에 Offering을 제공할 수 있다.",
  "status": "user_confirmed",
  "source": "DCTX.operation.slot_capacity_confirmed",
  "impact_area": [
    "RETENTION_REACTIVATION",
    "experiment population"
  ],
  "validation_method": "manual operational confirmation",
  "owner": "operations",
  "expires_at": "2026-08-24T00:00:00+09:00"
}
```

## 상태

```text
proposed
user_confirmed
data_supported
rejected
expired
```

Blocking 가정이 `proposed/expired`이면 `READY_FOR_REVIEW` 금지.

---

# 23. Limitations Contract

Limitations는 upstream에서 누락 없이 전파한다.

범주:

```text
DATA
CAUSAL
ECONOMICS
MEASUREMENT
POLICY
OPERATIONAL
EXTERNAL_CONTEXT
PRECISION
```

예:

```json
{
  "code": "ECONOMICS_VARIABLE_COST_UNKNOWN",
  "category": "ECONOMICS",
  "statement": "변동원가가 없어 순기여이익은 계산하지 않습니다.",
  "source_ref": "DCTX.economics.variable_cost_per_completion",
  "severity": "material"
}
```

Quality를 통과하기 위해 limitation을 숨기는 행위를 금지한다.

---

# 24. Package Type별 필수 계약

## 24.1 EXECUTION

필수:

```text
target
Offering/slot scope
channel plan
owner
schedule
budget/cost status
tracking
result source
experiment
success/stop
policy/consent
```

## 24.2 OPERATIONAL

필수:

```text
operation scope
owner
verification step
before/after or diagnostic metric
success/stop
result source
```

고객 대상과 마케팅 budget은 `not_applicable`일 수 있다.

## 24.3 DIAGNOSTIC

필수:

```text
missing field paths
why needed
owner
collection method
deadline
verification rule
unblocked strategy/stage
```

Primary Metric은 데이터 보완 완료 또는 검증 상태다.

## 24.4 HOLD

필수:

```text
reason code
current blockers
monitoring metric
review date
reopen trigger
limitations
```

Target과 채널은 `not_applicable`.
실행하지 않는다는 이유만으로 구조가 비어 있어서는 안 된다.

---

# 25. Package Assembly Pipeline

```text
1. Source Contract Validation
2. Source Freshness Validation
3. Diagnosis Snapshot
4. Missing Information Resolution
5. Alternative Strategy Assembly
6. Selected Playbook Instance Validation
7. Channel / Step / Artifact Assembly
8. Economics Assembly
9. Experiment Assembly
10. Limitation / Assumption Propagation
11. Draft Status Derivation
12. Quality Validation
13. Final Status Derivation
```

## 25.1 Source Validation

- tenant/business 일치
- version 지원
- superseded source 아님
- Opportunity status/expiry
- PII 없음

## 25.2 Draft Status

```text
critical missing input
→ NEEDS_DATA

policy unresolved
→ NEEDS_POLICY_REVIEW

구조 완성
→ DRAFT → Quality 평가
```

## 25.3 Final Status

```text
Hard Fail > 0
→ QUALITY_REJECTED

Score < 75 또는 section floor 미달
→ QUALITY_REJECTED

Quality PASSED
→ READY_FOR_REVIEW
```

---

# 26. Modification과 Versioning

## 26.1 사용자가 수정할 수 있는 항목

정책 범위 안에서:

```text
실행 기간
담당자
budget cap
manual notes
허용된 Target inclusion/exclusion
Playbook의 optional 실행 step
success threshold의 승인 가능한 runtime 값
```

## 26.2 사용자가 직접 바꿀 수 없는 항목

```text
Opportunity Observation
Evidence source
Cause 결과의 source facts
Strategy/Playbook/Experiment version
Policy hard constraint
Evidence Grade 규칙
Quality Score 계산
Actual/Estimate 의미
```

## 26.3 수정 시 처리

```text
decision = modified
→ current package SUPERSEDED
→ revision + 1 Package 생성
→ 영향받는 downstream 재조립
→ Quality 재평가
```

실행 중인 Experiment의 immutable 필드를 수정할 수 없다.

---

# 27. Decision Contract

기존 의미를 유지한다.

```text
approved
rejected
modified
later
```

추가 저장:

```text
reason_code
reason_text
modified_fields
decided_by
decided_at
source_package_revision
```

Reason Code 후보:

```text
NOT_RELEVANT
DATA_INACCURATE
STAFF_CAPACITY
NO_DISCOUNT
BRAND_MISMATCH
POLICY_CONCERN
ECONOMICS_UNCLEAR
MEASUREMENT_TOO_WEAK
ALREADY_DOING
TOO_COMPLEX
DEFER_UNTIL_DATE
OTHER
```

---

# 28. Legacy Recommendation Adapter

기존 Recommendation·Action 흐름과 연결한다.

## 28.1 적용 조건

```text
Package status = READY_FOR_REVIEW 또는 APPROVED
Quality PASSED
Package Type != HOLD unless monitoring Action
```

## 28.2 필드 매핑

```text
hypothesis
→ selected Cause hypothesis + limitation

action_type
→ selected Playbook canonical action type

channel
→ manual

target_segment
→ aggregate Target summary

expected_effect
→ deterministic source가 있을 때만
→ basis를 명시
→ 없으면 null

confidence
→ Opportunity confidence를 그대로 복사하지 않음
→ Adapter v1에서는 Package confidence를 만들지 않고 0~1 field가 필요하면 제한적 rule 또는 legacy compatibility 값
→ UI에서 성공 확률로 표시 금지

explanation
→ executive summary + selected reason

limitations
→ Package limitations
```

## 28.3 권장 Version

```text
recommendation-package-legacy-adapter-v1
```

## 28.4 주의

현재 Recommendation schema의 `confidence`가 필수이므로 로컬 구현 시 다음 중 하나를 ADR로 결정해야 한다.

1. legacy adapter에서 Opportunity confidence를 **현상 신뢰도**라는 limitation과 함께 임시 사용
2. Recommendation schema를 additive하게 의미 분리
3. Package 기반 Action endpoint를 추가해 legacy Recommendation 변환을 줄임

성공 확률로 오해할 수 있으므로 2 또는 3이 장기적으로 적합하다.

---

# 29. User-facing UI Contract

## 29.1 Summary View

```text
오늘 발견된 문제
추천하는 1순위 행동
왜 이 행동인가
실행 준비도
비용 상태
측정 강도
결정 버튼
```

## 29.2 Detail View

권장 순서:

```text
1. 관측 사실과 Estimate
2. 원인 가설과 반대 근거
3. 부족한 정보
4. 비교한 대안
5. 선택한 Playbook
6. 대상·Offering·시간대
7. 온라인·오프라인 채널 역할
8. 실행 단계
9. 비용·경제성
10. Experiment
11. 성공·중단조건
12. Tracking
13. 한계
14. Quality 결과
```

## 29.3 표시 규칙

- Observation, Estimate, Hypothesis, Recommendation, Actual Result 색상/라벨 분리
- Score의 의미를 성공확률로 표시하지 않음
- `unknown`, `not_applicable`, `infeasible` 구분
- Grade와 Precision 분리
- Quality Score는 “문서·실행 설계 완성도”로 표시
- Quality가 실패한 초안은 최종 추천처럼 강조하지 않음

---

# 30. Preview API 후보

```text
POST /api/v1/opportunities/{opportunityId}/recommendation-packages/preview
```

Request:

```json
{
  "decision_context": {},
  "cause_analysis": {},
  "strategy_run": {},
  "playbook_instance": {},
  "experiment_definition": {},
  "as_of": "2026-08-17T17:00:00+09:00"
}
```

특성:

- 저장 없음
- 외부 실행 없음
- 동일 입력 → 동일 Package
- Quality 결과 포함
- owner/admin/marketer
- tenant mismatch 404
- PII field 422

---

# 31. Persistence API 후보

```text
POST /api/v1/opportunities/{opportunityId}/recommendation-packages
GET  /api/v1/opportunities/{opportunityId}/recommendation-packages
GET  /api/v1/recommendation-packages/{packageId}
POST /api/v1/recommendation-packages/{packageId}/revalidate
POST /api/v1/recommendation-packages/{packageId}/decisions
POST /api/v1/recommendation-packages/{packageId}/actions
```

기존 Recommendation API는 유지한다.

---

# 32. DB 후보

```text
recommendation_packages
recommendation_package_versions
recommendation_package_source_refs
recommendation_package_alternatives
recommendation_package_steps
recommendation_package_artifacts
recommendation_package_assumptions
recommendation_package_limitations
recommendation_package_quality_results
recommendation_package_decisions
```

## 핵심 일반 컬럼

```text
id
tenant_id
business_id
opportunity_id
package_type
package_version
revision
status
source_hash
quality_status
quality_score
created_at
valid_until
approved_at
superseded_at
```

세부 구조 일부는 JSONB를 사용할 수 있지만 검색·권한·상태·version·score는 일반 컬럼으로 둔다.

---

# 33. Determinism과 Idempotency

동일 입력:

```text
Opportunity source/version
Decision Context snapshot/hash
Cause Analysis version
Strategy Run version
Playbook Instance/version
Experiment Definition/version
Assembler version
Quality Validator version
as_of
```

동일 결과:

- Package source refs
- status
- alternatives
- selected plan
- steps
- economics
- experiment
- limitations
- quality result

Preview ID 후보:

```text
sha256(
  tenant_id
  + business_id
  + opportunity_id
  + all source hashes
  + assembler version
  + quality version
  + as_of
)
```

---

# 34. 오류 계약

```text
RECOMMENDATION_PACKAGE_SOURCE_INVALID
RECOMMENDATION_PACKAGE_SOURCE_STALE
RECOMMENDATION_PACKAGE_INPUT_REQUIRED
RECOMMENDATION_PACKAGE_POLICY_REVIEW_REQUIRED
RECOMMENDATION_PACKAGE_PLAYBOOK_INVALID
RECOMMENDATION_PACKAGE_EXPERIMENT_INVALID
RECOMMENDATION_PACKAGE_TRACKING_REQUIRED
RECOMMENDATION_PACKAGE_ECONOMICS_REQUIRED
RECOMMENDATION_PACKAGE_QUALITY_FAILED
RECOMMENDATION_PACKAGE_IMMUTABLE
RECOMMENDATION_PACKAGE_SUPERSEDED
RECOMMENDATION_PACKAGE_DECISION_INVALID
TENANT_SCOPE_MISMATCH
PII_FIELD_REJECTED
UNSUPPORTED_RECOMMENDATION_PACKAGE_VERSION
RECOMMENDATION_PACKAGE_INTERNAL_ERROR
```

---

# 35. LOW_DEMAND_SLOT 실행형 예시

## Situation

```text
화요일 14~16시 저수요가 반복
목표 슬롯 capacity 확인
Offering 제공 가능
재방문 가능 cohort 72명
동의 상태 확인
수동 채널과 tracking 존재
변동원가는 unknown
```

## Alternatives

```text
1. RETENTION_REACTIVATION
2. DISCOVERABILITY
3. NO_ACTION
```

## Selected

```text
PB_LOW_DEMAND_REVISIT_COHORT_V1
```

## Package Result

```text
Package Type
→ EXECUTION

Economics
→ partial / revenue-only

Experiment
→ EXP_REVISIT_HOLDOUT_V1
→ exploratory or randomized based on frozen cohort

Execution
→ manual

Quality
→ 경제성 한계가 명시되고 나머지 계약이 완성되면 통과 가능
```

## 고객에게 보여줄 핵심

> 신규 광고보다 기존 재방문 cohort의 목표 슬롯 연결을 먼저 검토합니다. 매체비 없이 비교 실험이 가능하고 완료 예약까지 추적할 수 있기 때문입니다. 다만 변동원가가 없어 순기여이익은 계산하지 않습니다.

---

# 36. 진단형 예시

## Situation

```text
timezone/status mapping conflict
Opportunity evidence 재현 불가
```

## Selected

```text
DATA_COLLECTION
PB_LOW_DEMAND_DATA_AUDIT_V1
```

## Package Type

```text
DIAGNOSTIC
```

## Required Plan

```text
확인할 field
담당자
수정 방식
검증 규칙
재계산 대상
완료 일정
```

“데이터를 더 모으세요”만 반환하면 Quality Hard Fail이다.

---

# 37. HOLD 예시

## Situation

```text
capacity 없음
경제성 infeasible
추적 수단도 없음
```

## Selected

```text
NO_ACTION
PB_NO_ACTION_MONITORING_V1
```

## Package Type

```text
HOLD
```

## 필수

```text
보류 이유
모니터링 metric
재검토 날짜
재개 trigger
추가 비용을 쓰지 않는 이유
```

NO_ACTION은 결과 없음이 아니라 명시적인 의사결정이다.

---

# 38. 테스트 전략

## Contract

- source refs/version/hash
- package type
- status
- section completeness
- unknown/N/A
- no PII

## Assembly

- upstream value mutation 없음
- limitations propagation
- alternatives
- selected plan
- package type-specific fields

## Versioning

- modification creates new revision
- old becomes superseded
- stale source revalidation
- immutable after approved/action started

## Legacy Compatibility

- current Recommendation schema adapter
- existing Decision
- existing Manual Action
- current Result/Measurement

## Security

- tenant/business
- patient PII
- clinical targeting
- tracking value
- output aggregate

## Quality

- hard fail
- section floors
- total threshold
- generic advice rejection
- diagnostic/hold type-specific validation

---

# 39. 로컬 구현 Backlog

```text
RP-001 Package Type / Status enum
RP-002 Source Reference contract
RP-003 Package Draft schema
RP-004 Diagnosis assembler
RP-005 Alternative assembler
RP-006 Selected Plan assembler
RP-007 Economics / Experiment adapter
RP-008 Assumption / Limitation propagation
RP-009 Status derivation
RP-010 Quality integration
RP-011 Modification / Revision
RP-012 Legacy Recommendation adapter
RP-013 Preview API
RP-014 Persistence proposal
RP-015 UI contract
RP-016 Fixtures / Regression
RP-017 ADR / Current Status update
```

---

# 40. 완료조건

Recommendation Package v2 완료조건:

1. Package Type 4개
2. Source reference/version/hash
3. Lifecycle와 revision
4. Diagnosis·Cause·Missing Data
5. 최소 대안 비교
6. 선택 이유·제외 이유
7. Target·Offering·Slot
8. Channel 역할·Owner·Schedule
9. 완료 가능한 실행 Step
10. Artifact·Tracking
11. Economics 의미 분리
12. Experiment·Success·Stop
13. Assumption·Limitation
14. Package Type별 계약
15. Quality Gate 연결
16. 기존 Recommendation/Action 호환
17. tenant/PII 안전
18. 동일 입력 동일 결과
19. 코드 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 41. 구현 연결

Quality Bar·Measurement·Channel Execution·API·Data Schema 설계가 완료됐다.

로컬 구현 순서:

```text
RP-001~RP-017
→ RQ-001~RQ-017
→ UI-001~UI-009
→ 기존 Manual Action handoff
```

Quality-passed Package가 안정되기 전에는 LLM 설명이나 외부 Connector를 우선하지 않는다.
