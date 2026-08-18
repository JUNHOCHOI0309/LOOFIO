---
title: "LOOFIO Experiment Design v1"
version: "1.0"
date: "2026-08-17"
status: "로컬 구현용 확정 설계안"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
initial_domain: "Hospital Appointment MVP"
depends_on:
  - "LOOFIO_IMPLEMENTATION_ROADMAP_V2.md"
  - "LOOFIO_DECISION_INPUT_CONTRACT_V1.md"
  - "LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md"
  - "LOOFIO_STRATEGY_ENGINE_V1.md"
  - "LOOFIO_ACTION_PLAYBOOK_V1.md"
  - "LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md"
---

# LOOFIO Experiment Design v1

## 1. 문서 목적

이 문서는 Action Playbook을 실제 실행 전에 **검증 가능한 실험 계약**으로 변환하는 Experiment Design 계층을 정의한다.

현재 Hospital Appointment MVP의 Measurement는 다음 방식이다.

```text
완료 Action
→ 사람이 Action Result 기록
→ 측정 기간의 Appointment 집계
→ 같은 길이의 직전 1~4주 창 평균과 비교
→ signed delta 반환
```

현재 method:

```text
same-window-prior-four-weeks-v2
```

현재 계산 지표:

```text
appointment_count
completed_count
cancelled_count
no_show_count
actual_revenue
```

이 결과는 관찰 비교이며 다음을 주장하지 않는다.

```text
Action이 변화를 일으켰다
Incremental Revenue다
ROI다
통계적으로 유의하다
```

Experiment Design v1은 이 기존 Measurement를 제거하지 않는다.

```text
기존 baseline Measurement
→ Grade C 또는 D fallback

새 Experiment Contract
→ 실행 전에 대상·처리·비교·Metric·성공·중단조건을 고정
```

핵심 원칙:

> 실행 후 결과를 보고 기준을 만드는 것이 아니라, 실행 전에 무엇을 성공과 실패로 볼지 고정한다.

---

# 2. 파이프라인 위치

```text
Opportunity
→ Cause Analysis
→ Strategy Comparison
→ Playbook Instance
→ Experiment Designer
→ Experiment Draft
→ Recommendation Package
→ User Approval
→ Action
→ Result
→ Experiment Evaluation
→ Measurement / Learning
```

Experiment Designer는 Strategy나 Playbook을 다시 선택하지 않는다.

---

# 3. v1 범위

## 3.1 초기 범위

```text
Domain
→ Hospital Appointment MVP

Playbooks
→ Core 12 Playbooks

Execution
→ manual / staff-operated / copy-export

Evaluation
→ deterministic descriptive evaluation

AI
→ 사용하지 않음
```

## 3.2 비범위

v1은 다음을 구현 완료로 간주하지 않는다.

- 고급 인과 추론
- 자동 표본수 산출
- 자동 광고 플랫폼 실험 생성
- 실시간 multi-armed bandit
- 자동 예산 재배분
- 통계적 유의성 기반 자동 중단
- 개인 의료정보 기반 assignment
- Incremental Revenue 보장
- Playbook 자동 승격

---

# 4. 실험 5계층 모델

```text
ExperimentTemplate
        ↓ instantiate
ExperimentDefinition
        ↓ approve
ExperimentRun
        ↓ observe
ExperimentResult
        ↓ evaluate
ExperimentEvaluation
```

## 4.1 `ExperimentTemplate`

Playbook Definition에 연결되는 공통 템플릿.

포함:

```text
template_id
version
supported methods
assignment unit
default metrics
guardrail candidates
success template
stop template
attribution defaults
evidence grade ceiling
sample guidance
```

사업장·대상·기간·실제 threshold는 포함하지 않는다.

## 4.2 `ExperimentDefinition`

특정 Playbook Instance에 맞게 실행 전에 확정된 실험 계약.

포함:

```text
objective
hypothesis
estimand
population
assignment
treatment
comparison
period
metrics
success threshold
stop conditions
attribution window
tracking
economics
owner
approval
```

## 4.3 `ExperimentRun`

승인 후 실제 실행 상태와 배정·노출·운영 사건을 기록한다.

## 4.4 `ExperimentResult`

실제로 수집된 treatment/comparison 결과와 비용·운영 incident.

## 4.5 `ExperimentEvaluation`

미리 고정된 계약에 따라 결과를 해석한다.

다음이 포함된다.

```text
observed delta
guardrail result
success condition result
stop condition result
evidence grade
precision status
limitations
decision
```

---

# 5. Experiment Definition Contract

```json
{
  "experiment_id": "EXP_RUN_xxx",
  "definition_version": "experiment-definition-v1",
  "template_id": "EXP_REVISIT_HOLDOUT_V1",
  "template_version": "1.0",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "opportunity_id": "OPP_01",
  "strategy_run_id": "STRATEGY_01",
  "playbook_instance_id": "PBI_01",
  "status": "DRAFT",
  "objective": "목표 슬롯의 완료 재방문 예약 증가 가능성을 검증",
  "hypothesis": {
    "statement": "적법한 재방문 cohort 수동 실행은 비교군보다 목표 슬롯 완료 예약을 늘릴 수 있다.",
    "type": "directional",
    "expected_direction": "increase"
  },
  "estimand": {
    "metric_code": "completed_revisit_appointments_in_target_slot",
    "comparison": "treatment_minus_control",
    "unit": "completed_appointments"
  },
  "population": {},
  "assignment": {},
  "treatment": {},
  "comparison": {},
  "schedule": {},
  "metrics": {},
  "success_threshold": {},
  "stop_conditions": [],
  "attribution": {},
  "tracking": {},
  "economics": {},
  "evidence_plan": {
    "method": "RANDOMIZED_HOLDOUT",
    "grade_ceiling": "A",
    "precision_status": "UNKNOWN"
  },
  "owner": "marketer",
  "approval": {
    "required": true,
    "status": "pending"
  },
  "limitations": []
}
```

---

# 6. Experiment 상태

```text
DRAFT
NEEDS_DATA
NEEDS_POLICY_REVIEW
READY_FOR_APPROVAL
APPROVED
SCHEDULED
RUNNING
PAUSED
STOPPED
COMPLETED
INVALIDATED
CANCELLED
SUPERSEDED
```

## 주요 전이

```text
DRAFT
→ NEEDS_DATA
→ DRAFT

DRAFT
→ NEEDS_POLICY_REVIEW
→ DRAFT

DRAFT
→ READY_FOR_APPROVAL
→ APPROVED
→ SCHEDULED
→ RUNNING
→ COMPLETED

RUNNING
→ PAUSED
→ RUNNING

RUNNING / PAUSED
→ STOPPED

DRAFT / APPROVED / SCHEDULED
→ CANCELLED

DRAFT
→ SUPERSEDED

RUNNING / COMPLETED
→ INVALIDATED
```

## 규칙

- `RUNNING` 이후 핵심 계약을 수정하지 않는다.
- 수정이 필요하면 현재 실험을 `STOPPED` 또는 `INVALIDATED`하고 새 Definition version을 만든다.
- `COMPLETED`는 성공을 뜻하지 않는다.
- `STOPPED`는 실패만을 뜻하지 않는다. 사전에 정의한 안전 중단일 수 있다.

---

# 7. 실행 시작 후 불변 필드

다음은 `RUNNING` 이후 수정 금지다.

```text
template_id / version
playbook_id / version
objective
hypothesis
estimand
assignment unit
assignment rule
treatment
comparison
primary metric
success threshold
stop condition
attribution window
evidence grade plan
tracking key contract
budget cap
```

변경 가능한 운영 메타데이터:

```text
pause/resume event
실제 노출 시각
운영 incident
실제 지출
결과 수집 지연
outcome notes
```

핵심 계약 변경 시 새 experiment version이 필요하다.

---

# 8. Method Taxonomy v1

## 8.1 `RANDOMIZED_HOLDOUT`

개별 비식별 단위를 treatment/control로 안정적으로 배정.

대표:

```text
재방문 cohort
비가격 Offering 노출
```

장점:

- 비교 설계가 명확
- 알려지지 않은 차이를 평균적으로 줄임

제약:

- 충분한 대상
- stable assignment
- consent·정책
- contamination 관리
- 결과 연결

Evidence Grade ceiling:

```text
A
```

## 8.2 `EXPLORATORY_RANDOMIZED_HOLDOUT`

대상이 작아 무작위 배정은 가능하지만 정밀도가 낮은 탐색 설계.

Grade ceiling:

```text
B
```

## 8.3 `CLUSTER_OR_SHIFT_SPLIT`

직원 shift·요일·경로·파트너처럼 묶음 단위로 treatment/comparison을 배정.

대표:

```text
front-desk rebooking
booking path
partner split
```

Grade ceiling:

```text
B
```

Cluster 수가 부족하거나 비동등하면 C로 하향.

## 8.4 `ALTERNATING_TIME_WINDOW`

같은 요일·시간대의 treatment/comparison window를 교대로 배치.

대표:

```text
Offering-slot 재배치
front-desk protocol
```

Grade ceiling:

```text
B
```

최소 paired cycle과 context 안정성이 부족하면 C/D.

## 8.5 `CONTROLLED_ROUTE_SPLIT`

동시에 존재하는 예약 경로 A/B 또는 URL·화면 버전을 분리.

대표:

```text
booking path visibility
funnel friction
```

Grade ceiling:

```text
B
```

v1은 자동 웹 실험 플랫폼을 전제하지 않는다.

## 8.6 `PARTNER_CODE_SPLIT`

제휴처별 고유 code/QR로 결과를 분리하고, 가능한 경우 후보를 treatment/comparison 또는 단계 도입으로 나눈다.

Grade ceiling:

```text
B
```

단순 제휴처별 관찰만 있으면 C.

## 8.7 `MATCHED_HISTORICAL_WINDOW`

같은 요일·시간대·Offering 등 가능한 조건을 맞춘 과거 창과 비교.

현재 `same-window-prior-four-weeks-v2`를 포함할 수 있다.

Grade ceiling:

```text
C
```

## 8.8 `BEFORE_AFTER_EXPLORATORY`

단순 실행 전후 비교.

Grade ceiling:

```text
D
```

## 8.9 `DIAGNOSTIC_VERIFICATION`

데이터·capacity·tracking·예약 가능 상태를 참/거짓 또는 issue count로 확인.

인과효과 목적이 아니다.

Grade:

```text
D
```

## 8.10 `NO_ACTION_MONITORING`

실행하지 않고 Metric·재평가 trigger를 관찰.

Grade:

```text
D
```

---

# 9. Evidence Grade

Evidence Grade는 설계 강도를 나타낸다.

```text
A
B
C
D
```

성공·정밀도·효과 크기를 뜻하지 않는다.

## Grade A

필수:

- 사전 정의된 randomized assignment
- treatment/control 동시 운영
- 안정적인 결과 연결
- 주요 contamination 관리
- primary metric 사전 고정
- 정책·추적 검증

## Grade B

다음 중 하나:

- exploratory randomized
- prospective cluster/shift split
- alternating window
- controlled route split
- partner split

필수:

- 사전 정의
- 비교군
- 같은 관측 기간
- 주요 차이 기록
- tracking

## Grade C

- matched historical
- 현재 동일 요일·시간대 baseline
- prospective specification은 있으나 동시 비교군 없음

필수:

- 비교 창 규칙 고정
- context difference 기록
- 현재 Measurement limitations 유지

## Grade D

- simple before/after
- diagnostic verification
- manual attribution
- no-action monitoring

인과효과를 주장하지 않는다.

## Grade 하향 규칙

실행 후 다음이 발견되면 Grade를 하향할 수 있다.

```text
assignment contamination
tracking failure
comparison imbalance
schedule/capacity change
policy-driven treatment change
missing outcomes
external event shock
```

실행 후 Grade를 상향하지 않는다.
더 강한 설계는 새 Experiment로 수행한다.

---

# 10. Evidence Grade와 Precision 분리

Grade A라고 결과가 정확하다는 뜻은 아니다.

별도 `precision_status`:

```text
UNKNOWN
INSUFFICIENT
LOW
MODERATE
HIGH
```

v1에서 자동 통계 power를 계산하지 않아도 된다.

최소한 다음을 표시한다.

```text
assignment unit count
treatment count
comparison count
outcome count
missing outcome count
```

표본이 작으면:

```text
Grade A method
+
Precision LOW
+
Evaluation INCONCLUSIVE 가능
```

---

# 11. Assignment Unit

```text
CUSTOMER_TOKEN
APPOINTMENT
ELIGIBLE_VISIT
TIME_SLOT_WINDOW
DAY
WEEK
STAFF_SHIFT
BOOKING_PATH
PARTNER
LOCATION
NONE
```

Hospital 제한:

- raw patient identifier 사용 금지
- `CUSTOMER_TOKEN`은 내부 가명 key
- Recommendation·UI에 개별 token 노출 금지
- assignment export는 실행 시스템의 적법한 범위에서만 처리

---

# 12. Assignment Contract

```json
{
  "unit": "CUSTOMER_TOKEN",
  "method": "RANDOMIZED_HOLDOUT",
  "rule_version": "stable-hmac-assignment-v1",
  "treatment_ratio": 0.8,
  "control_ratio": 0.2,
  "stratification": [
    "offering_id",
    "overdue_band"
  ],
  "salt_reference": "secure-experiment-salt",
  "freeze_at": "2026-08-20T00:00:00+09:00",
  "reassignment_allowed": false
}
```

## Stable Assignment 제안

```text
HMAC(
  secure experiment salt,
  internal token + experiment_id
)
→ bucket
```

규칙:

- raw phone/email 사용 금지
- salt를 client/문서에 노출하지 않음
- 동일 Experiment에서 재배정 금지
- 제외 기준 적용 후 배정
- assignment log 또는 재현 가능한 rule version 보존

---

# 13. Population Contract

```text
eligibility criteria
exclusion criteria
unit
estimated eligible count
frozen eligible count
treatment count
comparison count
privacy mode
source refs
```

## 필수 제외 검토

```text
이미 목표 슬롯 예약
동의 거부
최근 동일 Action
정책상 제외
capacity와 무관한 대상
missing outcome linkage
```

Population을 결과 확인 후 변경하지 않는다.

---

# 14. Treatment / Comparison Contract

## Treatment

```text
무엇이 달라지는가
누가 노출되는가
언제 노출되는가
어떤 채널인가
어떤 비용이 발생하는가
```

## Comparison

```text
NO_TREATMENT
CURRENT_PROCESS
ALTERNATIVE_PROCESS
HISTORICAL_MATCH
NO_ACTION
```

한 번에 핵심 변경 하나를 우선한다.

```text
가격
문구
채널
Offering
운영 프로토콜
```

을 동시에 바꾸면 해석 가능성이 낮아진다.

---

# 15. Metric 역할

```text
PRIMARY
SECONDARY
GUARDRAIL
DIAGNOSTIC
ECONOMIC
```

## Primary Metric

실험의 주요 판단 기준.
v1에서 하나만 허용한다.

## Secondary

설명력과 운영 이해를 보조.

## Guardrail

주요 지표 개선과 함께 악화하면 안 되는 안전·운영 지표.

## Diagnostic

퍼널·추적·실행 품질.

## Economic

실제 지출·기여가치.
D4가 아니면 제한적으로 사용.

---

# 16. Metric Contract

```json
{
  "metric_code": "booking_completion_rate",
  "role": "PRIMARY",
  "metric_version": "booking-completion-rate-v1",
  "numerator": "completed_bookings",
  "denominator": "booking_starts",
  "segment": {
    "weekday": "TUE",
    "start_hour": 14,
    "end_hour": 16
  },
  "direction": "increase",
  "source": "normalized_booking_funnel",
  "missing_behavior": "INVALIDATE_IF_ABOVE_THRESHOLD"
}
```

## 규칙

- Rate는 numerator/denominator 고정.
- denominator를 결과 확인 후 변경하지 않음.
- `actual_revenue`는 completed Appointment의 paid amount.
- payment coverage 부족 시 actual revenue 제한 표시.
- Estimate를 Actual Metric으로 사용 금지.
- Net Contribution은 비용이 complete일 때만 계산.

---

# 17. Core Metric Catalog v1

## 예약·완료

```text
appointment_count
completed_appointments
target_slot_completed_appointments
completed_revisit_appointments_in_target_slot
completed_bookings_from_target_path
completed_bookings_by_partner
```

## Rate

```text
booking_completion_rate
on_site_rebooking_rate
contact_to_booking_rate
booking_to_completion_rate
cancellation_rate
no_show_rate
```

## Diagnostic

```text
critical_data_quality_issues_resolved
verified_action_result_linkage
sellable_slot_status_verified
verified_bookable_target_slot
booking_path_error_count
steps_to_book
```

## Operation

```text
completed_appointments_per_sellable_slot_hour
eligible_staff_count
available_service_minutes
staff_overtime_minutes
other_offering_displacement
```

## Money

```text
actual_revenue
actual_spend
cost_per_completed_booking
contribution_per_completion
net_contribution_estimate
```

`net_contribution_estimate`는 D4 + 비용 complete에서만 사용한다.

## Safety / Policy

```text
complaint_count
refusal_or_unsubscribe_rate
policy_incident_count
tracking_failure_count
cross_tenant_collision_count
```

---

# 18. Success Threshold Contract

```json
{
  "threshold_type": "ABSOLUTE_DELTA_AT_LEAST",
  "metric_code": "completed_revisit_appointments_in_target_slot",
  "value": 3,
  "comparison": "treatment_minus_control",
  "evaluation_window": "defined_observation_window",
  "requires_all_guardrails_pass": true
}
```

## Threshold Type

```text
VERIFIED_TRUE
ISSUE_COUNT_AT_MOST
ABSOLUTE_VALUE_AT_LEAST
ABSOLUTE_DELTA_AT_LEAST
RELATIVE_DELTA_AT_LEAST
RATE_DELTA_AT_LEAST
NON_INFERIOR_WITH_GUARDRAILS
ECONOMICS_POSITIVE
MONITORING_TRIGGER_REACHED
COMPOSITE_ALL
```

## 규칙

- AI가 threshold 숫자를 생성하지 않는다.
- 사용자 설정 또는 versioned deterministic template를 사용한다.
- Playbook Template은 형식과 default 후보를 제공한다.
- Runtime 값은 승인 전에 확인한다.
- Guardrail breach가 있으면 primary success만으로 성공 처리하지 않는다.
- 표본 부족이면 threshold 달성 여부와 별개로 `INCONCLUSIVE` 가능.

---

# 19. Stop Condition Contract

```json
{
  "condition_code": "BUDGET_CAP_REACHED",
  "severity": "HARD",
  "metric_code": "actual_spend",
  "operator": ">=",
  "value": {
    "amount": "120000.00",
    "currency": "KRW"
  },
  "action": "STOP_NEW_EXPOSURE",
  "owner": "marketer"
}
```

## Severity

```text
HARD
SOFT
REVIEW
```

## 주요 Stop Code

```text
PII_OR_SECURITY_INCIDENT
POLICY_INCIDENT
BUDGET_CAP_REACHED
CAPACITY_BREACH
STAFF_OVERLOAD
COMPLAINT_THRESHOLD
REFUSAL_THRESHOLD
TRACKING_FAILURE
RESULT_SOURCE_FAILURE
DATA_QUALITY_FAILURE
ASSIGNMENT_CONTAMINATION
COMPARISON_IMBALANCE
SCHEDULE_OR_OFFERING_CHANGE
MINIMUM_SAMPLE_UNREACHABLE
ECONOMICS_INFEASIBLE
```

## 동작

```text
STOP_NEW_EXPOSURE
PAUSE_AND_REVIEW
INVALIDATE_EXPERIMENT
CONTINUE_WITH_LIMITATION
```

---

# 20. Sample Readiness

v1은 통계적 power를 자동 보장하지 않는다.

```text
SUFFICIENT_FOR_METHOD
EXPLORATORY_ONLY
INSUFFICIENT
UNKNOWN
```

## 운영 가이드

### Individual randomized holdout

```text
eligible >= 40
→ standard randomized holdout 검토
→ treatment/control 각각 최소 1건 이상 outcome 필요
→ precision은 별도 표시

eligible 20~39
→ exploratory randomized
→ Grade ceiling B

eligible < 20
→ matched historical 또는 diagnostic
→ Grade C/D
```

이 기준은 제품 운영용 최소 가이드이며 통계적 power 보장이 아니다.

### Alternating window

권장:

```text
최소 4 treatment window
+
최소 4 comparison window
+
동일 요일·시간대
```

미달이면 Grade C/D.

### Partner / cluster

권장:

```text
최소 3개 이상의 추적 가능한 unit
가능하면 treatment/comparison 또는 단계 도입
```

unit 수가 적으면 exploratory로 표시한다.

---

# 21. Time Contract

```text
eligibility_freeze_at
assignment_at
exposure_start_at
exposure_end_at
observation_start_at
observation_end_at
completion_followup_end_at
evaluation_at
```

모든 timestamp는 UTC offset 포함.

## Attribution Window

```text
exposure_to_booking
booking_to_completion
action_to_result
```

예:

```json
{
  "booking_attribution_days": 7,
  "completion_followup_days": 14,
  "late_result_behavior": "REPORT_SEPARATELY"
}
```

이는 Template default 후보이며 Playbook·Offering 특성에 따라 승인 전에 확정한다.

---

# 22. Baseline Contract

Matched Historical 또는 current Measurement 사용 시:

```text
same weekday
same slot
same duration
same Offering scope
same location
same metric definition
```

가능하면 추가 확인:

```text
holiday
weather
event
staff/capacity
price/Offering change
other campaign
```

현재 `same-window-prior-four-weeks-v2`는 다음 제한을 유지한다.

```text
계절성 미보정
날씨·행사 미보정
인력·capacity 변화 미보정
인과효과 아님
```

---

# 23. Contamination / Crossover / Displacement

## Contamination

Comparison unit가 treatment를 받음.

## Crossover

Treatment unit가 다른 조건으로 이동.

## Displacement

목표 슬롯 증가가 다른 시간·Offering 감소를 동반.

## 필수 기록

```text
contamination_count
crossover_count
other_slot_change
other_offering_change
assignment_violation
```

## 규칙

- 일정 수준 이상이면 Grade 하향 또는 invalidation.
- exact threshold는 Template 또는 Runtime Definition에 고정.
- target slot만 보고 전체 completed appointments 감소를 숨기지 않는다.

---

# 24. Economics Contract

```text
planned_budget
actual_spend
fixed_cost
variable_cost
benefit_cost
partner_cost
staff_time_cost
additional_service_cost
```

## Evaluation

```text
Actual Spend
Actual Revenue
Observed Delta
Contribution Estimate
```

분리한다.

## 규칙

- 비용-bearing 실험에서 actual spend 미수집 시 economic result는 `UNKNOWN`.
- 비용 unknown을 0으로 처리하지 않는다.
- Net Contribution은 cost complete에서만 계산.
- RevenueGap Estimate를 실제 Experiment Result로 사용하지 않는다.
- budget cap breach는 Hard Stop 후보.

---

# 25. Result Collection Contract

```text
exposure events
assignment records
booking events
completed appointment events
cancellation/no-show
tracking source
actual spend
policy/complaint incident
operational incident
```

## Result Source 상태

```text
VERIFIED
PARTIAL
MISSING
CONFLICTING
STALE
```

Primary Metric source가 `MISSING/CONFLICTING`이면 Evaluation을 `INVALIDATED` 또는 `INCONCLUSIVE`로 처리한다.

---

# 26. Evaluation Decision

```text
SUCCESS_CANDIDATE
NO_CLEAR_EFFECT
NEGATIVE_OR_HARMFUL
INCONCLUSIVE
INVALIDATED
OPERATIONAL_LEARNING_ONLY
DATA_QUALITY_RESOLVED
MONITORING_CONTINUE
REOPEN_DECISIONING
```

## `SUCCESS_CANDIDATE`

- success threshold 통과
- hard guardrail 통과
- result source valid
- sample precision이 최소 허용 수준
- 아직 일반화된 성공 보장이 아님

## `NO_CLEAR_EFFECT`

효과가 명확하지 않으나 실험은 유효.

## `NEGATIVE_OR_HARMFUL`

주요 Metric 악화 또는 guardrail breach.

## `INCONCLUSIVE`

표본·정밀도·기간이 부족하지만 계약 자체는 유효.

## `INVALIDATED`

tracking·assignment·data quality·계약 변경 등으로 해석 불가.

## `OPERATIONAL_LEARNING_ONLY`

capacity·funnel·운영 확인 등 인과 목적이 아닌 결과.

---

# 27. Evaluation Output Contract

```json
{
  "experiment_id": "EXP_RUN_01",
  "evaluation_version": "experiment-evaluation-v1",
  "status": "COMPLETED",
  "method": "RANDOMIZED_HOLDOUT",
  "evidence_grade": "A",
  "precision_status": "LOW",
  "primary_metric": {
    "treatment": 4,
    "comparison": 1,
    "delta": 3
  },
  "secondary_metrics": [],
  "guardrails": [],
  "economics": {
    "status": "partial"
  },
  "success_threshold_result": "PASSED",
  "stop_condition_events": [],
  "decision": "INCONCLUSIVE",
  "limitations": [
    "무작위 배정은 수행했으나 완료 예약 표본이 작아 정밀도가 낮습니다."
  ]
}
```

Threshold가 통과해도 Precision이 낮으면 `INCONCLUSIVE`일 수 있다.

---

# 28. Current Action / Result / Measurement 연결

## 기존 유지

```text
Recommendation Decision
→ Manual Action
→ Action Result
→ calculate_action_measurement
```

## additive 연결

```text
Experiment Definition
→ Recommendation Package
→ Existing Manual Action
→ Action Result
→ Experiment Result Adapter
→ Experiment Evaluation
```

## 현재 Action Result 재사용

현재 필드:

```text
execution_summary
measurement_start_at
measurement_end_at
actual_spend(optional)
outcome_notes
```

추가로 필요한 Experiment 결과는 별도 persistence 또는 structured result payload로 확장한다.

## 현재 Measurement 재사용

```text
same-window-prior-four-weeks-v2
```

사용:

- Grade C matched historical
- Grade D before/after fallback
- secondary context

사용하지 않음:

- Grade A/B treatment-control 계산 대체
- Incremental Revenue 확정
- Playbook 성공 보장

---

# 29. API 후보

## Template

```text
GET /api/v1/experiment-templates
GET /api/v1/experiment-templates/{templateId}
```

## Preview

```text
POST /api/v1/playbook-instances/{instanceId}/experiments/preview
```

## Persistence

```text
POST /api/v1/playbook-instances/{instanceId}/experiments
GET  /api/v1/experiments/{experimentId}
POST /api/v1/experiments/{experimentId}/approve
POST /api/v1/experiments/{experimentId}/events
POST /api/v1/experiments/{experimentId}/results
GET  /api/v1/experiments/{experimentId}/evaluation
```

현재 구현 전까지 proposal이다.

---

# 30. DB 후보

```text
experiment_templates
experiment_definitions
experiment_versions
experiment_assignments
experiment_events
experiment_metric_definitions
experiment_guardrails
experiment_stop_conditions
experiment_results
experiment_evaluations
```

## 공통

```text
tenant_id
business_id
version
status
source references
input hash
created_at
approved_at
started_at
completed_at
invalidated_at
```

## Assignment

개별 token assignment를 저장해야 한다면:

- tenant/business scope
- internal token only
- 짧은 목적 제한
- export audit
- retention
- raw contact 정보 없음

---

# 31. Determinism

동일 입력:

```text
Playbook Instance
Experiment Template version
Decision Context
Metric Catalog version
Experiment Designer version
as_of
```

동일 Draft:

- method candidates
- metric set
- guardrails
- default threshold form
- stop condition set
- grade ceiling
- missing inputs

Assignment은 승인 후 stable rule로 재현돼야 한다.

---

# 32. 오류 계약

```text
EXPERIMENT_TEMPLATE_NOT_FOUND
EXPERIMENT_TEMPLATE_NOT_APPLICABLE
EXPERIMENT_INPUT_REQUIRED
EXPERIMENT_POLICY_REVIEW_REQUIRED
EXPERIMENT_TRACKING_REQUIRED
EXPERIMENT_RESULT_SOURCE_REQUIRED
EXPERIMENT_ECONOMICS_REQUIRED
EXPERIMENT_ASSIGNMENT_INVALID
EXPERIMENT_COMPARISON_INVALID
EXPERIMENT_METRIC_INVALID
EXPERIMENT_THRESHOLD_REQUIRED
EXPERIMENT_STOP_CONDITION_REQUIRED
EXPERIMENT_IMMUTABLE_AFTER_START
EXPERIMENT_RESULT_INVALID
EXPERIMENT_INVALIDATED
TENANT_SCOPE_MISMATCH
PII_FIELD_REJECTED
UNSUPPORTED_EXPERIMENT_VERSION
EXPERIMENT_ENGINE_INTERNAL_ERROR
```

---

# 33. 테스트 전략

## Template

- ID/version unique
- Playbook mapping
- method
- grade ceiling
- metric roles
- threshold/stop template

## Definition

- primary metric exactly one
- treatment/comparison
- period
- timezone
- assignment
- tracking
- result source
- owner/approval
- budget cap

## Assignment

- stable
- no raw PII
- ratio
- exclusions
- no reassignment
- tenant isolation

## State

- valid transitions
- immutable after RUNNING
- pause/stop/invalidate
- completed != success

## Evaluation

- threshold
- guardrails
- grade downgrade
- precision
- missing result
- actual/estimate separation
- Grade C/D causal wording prohibition

## Regression

- current Action/Result/Measurement remains valid
- `same-window-prior-four-weeks-v2` unchanged
- existing API unchanged

---

# 34. 로컬 구현 Backlog

```text
EX-001 ExperimentTemplate schema
EX-002 Method / Evidence Grade enums
EX-003 Metric Catalog v1
EX-004 Definition schema
EX-005 State machine
EX-006 Success Threshold / Stop Condition
EX-007 Assignment contract
EX-008 Sample readiness
EX-009 Result contract
EX-010 Evaluation engine
EX-011 Current Measurement adapter
EX-012 Preview API
EX-013 Persistence proposal
EX-014 Fixtures
EX-015 Documentation / ADR
```

---

# 35. 완료조건

Experiment Design v1 완료조건:

1. Template / Definition / Run / Result / Evaluation 분리
2. Method Taxonomy
3. Evidence Grade A~D
4. Precision 별도 표시
5. Primary Metric 하나
6. numerator/denominator 고정
7. success/stop 사전 고정
8. assignment 안정성
9. tracking/result source 필수
10. cost unknown과 0 분리
11. contamination/displacement
12. 실행 후 immutable
13. Grade C/D 인과 표현 금지
14. current Measurement fallback 연결
15. tenant/PII 안전
16. 동일 입력 동일 Draft
17. 코드 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 36. 구현 연결

Recommendation Package·Quality·Measurement 설계는 완료됐다.

로컬 구현 순서:

```text
EX-001~EX-015
→ EXM-001~EXM-010
→ RP-001~RP-017
→ RQ-001~RQ-017
```

첫 vertical slice에서는 Definition·Preview를 우선하고 실제 Assignment·Connector 실행은 뒤 단계로 유지한다.
