---
title: "LOOFIO Playbook Experiment Mapping v1"
version: "1.0"
date: "2026-08-17"
status: "Core Hospital Playbook별 Experiment Template 매핑"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
depends_on:
  - "LOOFIO_ACTION_PLAYBOOK_V1.md"
  - "LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md"
  - "LOOFIO_EXPERIMENT_DESIGN_V1.md"
---

# LOOFIO Playbook Experiment Mapping v1

## 1. 문서 목적

이 문서는 Hospital Appointment Core Playbook 12개와 Experiment Template의 정식 연결을 정의한다.

각 매핑은 다음을 고정한다.

```text
실험 목적
지원 Method
Assignment Unit
Evidence Grade ceiling
Sample guidance
Treatment / Comparison
Primary Metric
Secondary / Guardrail
Attribution
Success Threshold 형식
Stop Condition
Result Source
기존 Measurement fallback
```

Threshold 숫자와 실제 기간은 Playbook Instance별 Runtime Definition에서 승인 전에 확정한다.

---

# 2. Registry Summary

| Playbook | Experiment Template | Preferred Method | Grade ceiling |
|---|---|---|:---:|
| `PB_LOW_DEMAND_DATA_AUDIT_V1` | `EXP_DATA_QUALITY_DIAGNOSTIC_V1` | DIAGNOSTIC_VERIFICATION | D |
| `PB_LOW_DEMAND_TRACKING_SETUP_V1` | `EXP_TRACKING_VERIFICATION_V1` | DIAGNOSTIC_VERIFICATION | D |
| `PB_LOW_DEMAND_CAPACITY_REVIEW_V1` | `EXP_CAPACITY_DIAGNOSTIC_V1` | DIAGNOSTIC_VERIFICATION | D |
| `PB_OFFERING_SLOT_REALLOCATION_V1` | `EXP_SLOT_REALLOCATION_ALTERNATING_V1` | ALTERNATING_TIME_WINDOW | B |
| `PB_BOOKING_AVAILABILITY_AUDIT_V1` | `EXP_BOOKING_AVAILABILITY_BEFORE_AFTER_V1` | DIAGNOSTIC_VERIFICATION | D |
| `PB_LOW_DEMAND_REVISIT_COHORT_V1` | `EXP_REVISIT_HOLDOUT_V1` | RANDOMIZED_HOLDOUT | A |
| `PB_FRONT_DESK_REBOOKING_V1` | `EXP_FRONT_DESK_REBOOKING_ALTERNATING_V1` | CLUSTER_OR_SHIFT_SPLIT | B |
| `PB_BOOKING_PATH_VISIBILITY_V1` | `EXP_BOOKING_VISIBILITY_BEFORE_AFTER_V1` | CONTROLLED_ROUTE_SPLIT | B |
| `PB_BOOKING_FUNNEL_FRICTION_V1` | `EXP_FUNNEL_SINGLE_CHANGE_V1` | CONTROLLED_ROUTE_SPLIT | B |
| `PB_NON_DISCOUNT_VALUE_ADD_V1` | `EXP_NON_DISCOUNT_VALUE_ADD_V1` | RANDOMIZED_HOLDOUT / ALTERNATING_TIME_WINDOW | A/B |
| `PB_TRACKED_LOCAL_PARTNERSHIP_V1` | `EXP_PARTNER_CODE_SPLIT_V1` | PARTNER_CODE_SPLIT | B |
| `PB_NO_ACTION_MONITORING_V1` | `EXP_NO_ACTION_MONITORING_V1` | NO_ACTION_MONITORING | D |

Grade ceiling은 최대 설계 강도다.
실제 실행 품질에 따라 하향할 수 있다.

---

# 3. 공통 규칙

## 3.1 실제 예약 완료를 우선한다

가능하면 Primary Metric은 다음 순서를 따른다.

```text
completed appointment
> booking created
> inquiry
> click / view
```

예약 생성만 증가하고 취소·노쇼가 늘어날 수 있으므로 완료를 우선한다.

## 3.2 Exposure만 있는 Metric은 Diagnostic

```text
impression
view
scan
click
```

만으로 Playbook 성공을 결정하지 않는다.

## 3.3 Actual Revenue

```text
completed appointment
+
paid_amount
```

를 사용한다.

Payment coverage가 부족하면 limitation을 표시한다.

## 3.4 Economics

비용-bearing Playbook은:

```text
actual_spend
benefit cost
partner cost
staff cost
```

를 가능한 범위에서 수집한다.

미수집 비용을 0으로 계산하지 않는다.

## 3.5 Current Measurement fallback

현재:

```text
same-window-prior-four-weeks-v2
```

는 Grade C 또는 D fallback으로만 사용한다.

---

# 4. EXP_DATA_QUALITY_DIAGNOSTIC_V1

## Mapping

```text
Playbook
→ PB_LOW_DEMAND_DATA_AUDIT_V1
```

## 목적

데이터 오류를 해결하고 Opportunity 근거가 재현되는지 확인한다.

## Method

```text
DIAGNOSTIC_VERIFICATION
```

## Assignment Unit

```text
NONE
```

## Treatment / Comparison

Treatment:

```text
mapping / timezone / status / lineage correction
```

Comparison:

```text
correction 전 validation snapshot
```

인과 실험이 아니라 검증 전후 기록이다.

## Primary Metric

```text
critical_data_quality_issues_resolved
```

정의:

```text
실행 전 critical issue count
-
실행 후 unresolved critical issue count
```

## Secondary

```text
rejected_row_rate
unknown_status_rate
offering_resolution_rate
customer_token_coverage_rate
payment_coverage_rate
opportunity_reproducibility
```

## Success Template

```text
COMPOSITE_ALL
├─ critical issue count <= approved threshold
├─ Opportunity evidence source reproducible = true
└─ follow-up Cause Analysis executable = true
```

## Stop

```text
PII_OR_SECURITY_INCIDENT
TENANT_SOURCE_CONFLICT
SOURCE_ACCESS_UNAVAILABLE
OPPORTUNITY_EVIDENCE_UNREPRODUCIBLE
```

## Grade / Decision

```text
Grade D
DATA_QUALITY_RESOLVED
또는
OPERATIONAL_LEARNING_ONLY
```

## Result Source

```text
import validation
mapping profile
Opportunity regeneration
```

---

# 5. EXP_TRACKING_VERIFICATION_V1

## Mapping

```text
Playbook
→ PB_LOW_DEMAND_TRACKING_SETUP_V1
```

## 목적

Action tracking 값이 정확한 tenant/business/action/result로 연결되는지 검증한다.

## Method

```text
DIAGNOSTIC_VERIFICATION
```

## Assignment Unit

```text
NONE
```

## Treatment

```text
tracking configuration
test event
```

## Primary Metric

```text
verified_action_result_linkage
```

Type:

```text
VERIFIED_TRUE
```

## Secondary

```text
test_event_count
misrouted_event_count
tracking_latency
missing_tracking_field_count
```

## Success

```text
test event >= 1
AND
correct tenant/business/action linkage
AND
no PII in tracking value
```

## Stop

```text
CROSS_TENANT_COLLISION
PII_OR_SECURITY_INCIDENT
RESULT_SOURCE_FAILURE
TRACKING_VALUE_NOT_UNIQUE
```

## Grade

```text
D
```

성공하더라도 마케팅 효과 근거가 아니다.

---

# 6. EXP_CAPACITY_DIAGNOSTIC_V1

## Mapping

```text
Playbook
→ PB_LOW_DEMAND_CAPACITY_REVIEW_V1
```

## 목적

목표 슬롯이 실제 판매 가능한지 검증한다.

## Method

```text
DIAGNOSTIC_VERIFICATION
```

## Assignment Unit

```text
TIME_SLOT_WINDOW
```

## Primary Metric

```text
sellable_slot_status_verified
```

Type:

```text
VERIFIED_TRUE
```

값:

```text
sellable
not_sellable
unknown
conflicting
```

Success:

```text
known sellable / not_sellable
+
source reference
+
follow-up Strategy 가능
```

## Secondary

```text
eligible_staff_count
available_service_minutes
booking_availability_mismatch_count
room_or_equipment_constraint_count
```

## Stop

```text
OPERATION_SOURCE_CONFLICT
OFFERING_POLICY_UNKNOWN
STAFF_PII_REQUIRED
```

## Grade

```text
D
```

---

# 7. EXP_SLOT_REALLOCATION_ALTERNATING_V1

## Mapping

```text
Playbook
→ PB_OFFERING_SLOT_REALLOCATION_V1
```

## 목적

Offering 노출·운영 우선순위 변경이 목표 슬롯 완료 예약을 개선하는지 탐색한다.

## Preferred Method

```text
ALTERNATING_TIME_WINDOW
```

Fallback:

```text
MATCHED_HISTORICAL_WINDOW
BEFORE_AFTER_EXPLORATORY
```

## Assignment Unit

```text
TIME_SLOT_WINDOW
```

## Sample Guidance

권장:

```text
treatment window >= 4
comparison window >= 4
same weekday / same slot
```

미달:

```text
Grade C/D
Precision LOW
```

## Treatment

```text
선택 Offering의 예약 화면·운영 우선순위 변경
```

## Comparison

```text
기존 Offering 배치 또는 교대 comparison window
```

## Primary Metric

우선:

```text
completed_appointments_per_sellable_slot_hour
```

capacity denominator가 없으면:

```text
target_slot_completed_appointments
```

## Secondary

```text
actual_revenue
offering_share
booking_count
```

## Guardrails

```text
other_offering_displacement
cancellation_rate
staff_overtime_minutes
capacity_breach
```

## Success Template

```text
ABSOLUTE_DELTA_AT_LEAST
또는
RATE_DELTA_AT_LEAST
+
all hard guardrails pass
```

## Stop

```text
CAPACITY_BREACH
STAFF_OVERLOAD
OTHER_OFFERING_DISPLACEMENT_THRESHOLD
TRACKING_FAILURE
SCHEDULE_OR_OFFERING_CHANGE
```

## Grade

```text
B ceiling with prospective alternating design
C with matched historical
D with simple before/after
```

## Current Measurement fallback

```text
same-window-prior-four-weeks-v2
→ Grade C maximum
```

---

# 8. EXP_BOOKING_AVAILABILITY_BEFORE_AFTER_V1

## Mapping

```text
Playbook
→ PB_BOOKING_AVAILABILITY_AUDIT_V1
```

## 목적

운영상 제공 가능한 슬롯이 실제 예약 경로에서도 선택 가능한지 검증한다.

## Method

```text
DIAGNOSTIC_VERIFICATION
```

보조:

```text
BEFORE_AFTER_EXPLORATORY
```

## Assignment Unit

```text
BOOKING_PATH
```

## Primary Metric

```text
verified_bookable_target_slot
```

Type:

```text
VERIFIED_TRUE
```

## Secondary

```text
booking_path_error_count
steps_to_book
test_completion_time
availability_mismatch_count
```

## Success

```text
target slot selectable
AND
test booking path completes
AND
tracking result linkage verified
```

## Stop

```text
DOUBLE_BOOKING_RISK
TEST_EVENT_CLEANUP_FAILURE
TRACKING_FAILURE
PATIENT_DATA_USED_IN_TEST
```

## Grade

```text
D
```

예약 가능 상태 개선 후 실제 예약 효과는 별도 실험이 필요하다.

---

# 9. EXP_REVISIT_HOLDOUT_V1

## Mapping

```text
Playbook
→ PB_LOW_DEMAND_REVISIT_COHORT_V1
```

## 목적

적법한 재방문 cohort 수동 실행이 비교군보다 목표 슬롯 완료 재방문을 늘리는지 검증한다.

## Preferred Method

```text
RANDOMIZED_HOLDOUT
```

Fallback:

```text
EXPLORATORY_RANDOMIZED_HOLDOUT
MATCHED_HISTORICAL_WINDOW
```

## Assignment Unit

```text
CUSTOMER_TOKEN
```

## Eligibility

```text
재방문 기준 초과
목표 Offering 이력
동의 가능
최근 동일 Action 없음
이미 목표 슬롯 예약 아님
결과 연결 가능
```

## Sample Guidance

```text
eligible >= 40
→ randomized holdout / Grade A ceiling

20~39
→ exploratory randomized / Grade B ceiling

< 20
→ matched historical / Grade C ceiling
```

이는 power 보장이 아니라 운영 최소 가이드다.

## Treatment

```text
승인된 수동 재방문 실행 1회
+
목표 슬롯·Offering 예약 경로
```

## Comparison

```text
holdout: 동일 eligibility지만 실행하지 않음
```

Holdout은 실험 기간 동안 동일 Action을 받지 않는다.

## Primary Metric

```text
completed_revisit_appointments_in_target_slot
```

Comparison:

```text
treatment rate - control rate
```

rate denominator:

```text
assigned eligible customers
```

## Secondary

```text
bookings_created
booking_to_completion_rate
actual_revenue
contact_to_booking_rate
```

## Guardrails

```text
refusal_or_unsubscribe_rate
complaint_count
cancellation_rate
capacity_breach
recent_contact_overlap
```

## Attribution default candidate

```text
booking attribution: exposure 후 7일
completion follow-up: experiment end 후 14일
late result: 별도 보고
```

Runtime 승인 전에 확정한다.

## Success Template

```text
RATE_DELTA_AT_LEAST
또는
ABSOLUTE_DELTA_AT_LEAST
+
guardrails pass
+
minimum outcome count
```

## Stop

```text
REFUSAL_THRESHOLD
COMPLAINT_THRESHOLD
CONSENT_FAILURE
WRONG_COHORT
CAPACITY_BREACH
TRACKING_FAILURE
BUDGET_CAP_REACHED
```

## Grade

```text
A / B / C
```

Grade A라도 표본이 작으면 `Precision LOW`와 `INCONCLUSIVE` 가능.

---

# 10. EXP_FRONT_DESK_REBOOKING_ALTERNATING_V1

## Mapping

```text
Playbook
→ PB_FRONT_DESK_REBOOKING_V1
```

## 목적

중립적 현장 다음 예약 안내가 비교 조건보다 재예약률과 완료 재방문을 개선하는지 검증한다.

## Preferred Method

```text
CLUSTER_OR_SHIFT_SPLIT
ALTERNATING_TIME_WINDOW
```

## Assignment Unit

```text
STAFF_SHIFT
또는
TIME_SLOT_WINDOW
```

개별 환자를 직원 재량으로 선택하지 않는다.

## Treatment

```text
승인된 중립 안내 프로토콜
+
제안 여부 기록
```

## Comparison

```text
current process
또는
comparison shift/window
```

## Primary Metric

```text
on_site_rebooking_rate
```

정의:

```text
현장 재예약 완료 수
/
eligible visit 중 실제 안내 기회를 가진 수
```

## Secondary

```text
staff_offer_rate
completed_revisit_rate
cancellation_rate
```

## Guardrails

```text
complaint_count
staff_burden
policy_incident
capacity_breach
```

## Success

```text
RATE_DELTA_AT_LEAST
+
staff_offer_rate minimum
+
guardrails pass
```

## Stop

```text
COMPLAINT_THRESHOLD
STAFF_OVERLOAD
POLICY_INCIDENT
DENOMINATOR_RECORDING_FAILURE
```

## Grade

```text
B with prospective shift/window split
C with matched historical
D with simple before/after
```

---

# 11. EXP_BOOKING_VISIBILITY_BEFORE_AFTER_V1

## Mapping

```text
Playbook
→ PB_BOOKING_PATH_VISIBILITY_V1
```

## 목적

목표 Offering·슬롯 가시성 변경이 해당 경로의 완료 예약을 개선하는지 검증한다.

## Preferred Method

```text
CONTROLLED_ROUTE_SPLIT
```

Fallback:

```text
MATCHED_HISTORICAL_WINDOW
BEFORE_AFTER_EXPLORATORY
```

## Assignment Unit

```text
BOOKING_PATH
또는
TIME_SLOT_WINDOW
```

## Treatment

```text
Offering·슬롯 정보와 예약 경로를 명확하게 한 버전
```

## Comparison

```text
기존 경로
또는
동시 comparison route
```

## Primary Metric

노출 denominator가 있으면:

```text
booking_completion_rate_from_target_path
```

없으면:

```text
completed_bookings_from_target_path
```

## Secondary

```text
path_visits
booking_starts
steps_to_book
booking_path_error_count
```

## Guardrails

```text
booking_error
capacity_breach
other_path_displacement
policy_incident
```

## Success

```text
RATE_DELTA_AT_LEAST
또는
ABSOLUTE_DELTA_AT_LEAST
+
guardrails pass
```

## Stop

```text
BOOKING_ERROR_THRESHOLD
CAPACITY_BREACH
TRACKING_FAILURE
SCHEDULE_OR_OFFERING_CHANGE
POLICY_INCIDENT
```

## Grade

```text
B controlled split
C matched historical
D simple before/after
```

---

# 12. EXP_FUNNEL_SINGLE_CHANGE_V1

## Mapping

```text
Playbook
→ PB_BOOKING_FUNNEL_FRICTION_V1
```

## 목적

예약 Funnel의 한 가지 마찰 변경이 완료 전환율을 개선하는지 검증한다.

## Preferred Method

```text
CONTROLLED_ROUTE_SPLIT
```

Fallback:

```text
ALTERNATING_TIME_WINDOW
MATCHED_HISTORICAL_WINDOW
```

## Assignment Unit

```text
BOOKING_PATH
또는
TIME_SLOT_WINDOW
```

## Treatment

```text
사전 정의한 단일 변경 1개
```

예:

```text
단계 축소
목표 슬롯 딥링크
오류 수정
가용성 표시 개선
```

## Comparison

```text
current path
```

## Primary Metric

```text
booking_completion_rate
=
completed bookings / booking starts
```

## Secondary

```text
booking_start_rate
steps_to_complete
time_to_book
inquiry_to_booking
```

## Guardrails

```text
booking_error
support_inquiry
cancellation_rate
capacity_breach
```

## Success

```text
RATE_DELTA_AT_LEAST
+
no hard guardrail breach
```

## Stop

```text
BOOKING_ERROR_THRESHOLD
TRACKING_FAILURE
MULTIPLE_SIMULTANEOUS_CHANGES
CAPACITY_BREACH
```

## Grade

```text
B controlled route
B/C alternating
C historical
```

---

# 13. EXP_NON_DISCOUNT_VALUE_ADD_V1

## Mapping

```text
Playbook
→ PB_NON_DISCOUNT_VALUE_ADD_V1
```

## 목적

정책상 허용되고 비용이 확인된 비가격 부가가치가 무혜택 또는 기존 조건보다 목표 슬롯 완료 예약과 기여가치를 개선하는지 검증한다.

## Preferred Method

```text
RANDOMIZED_HOLDOUT
또는
ALTERNATING_TIME_WINDOW
```

## Assignment Unit

```text
CUSTOMER_TOKEN
TIME_SLOT_WINDOW
```

## Preconditions

```text
benefit cost known
policy approved
capacity confirmed
result source
budget cap
```

## Treatment

```text
비가격 부가가치 조건
```

## Comparison

```text
무혜택 current process
또는
비교 가능한 다른 비가격 조건
```

## Primary Metric

```text
completed_appointments_in_target_slot
```

customer assignment이면 rate 사용:

```text
completed appointment rate per assigned eligible unit
```

## Secondary

```text
actual_revenue
actual_spend
benefit_cost
net_contribution_estimate
booking_to_completion_rate
```

## Guardrails

```text
complaint_count
policy_incident
staff_burden
capacity_breach
other_slot_displacement
```

## Success

D4:

```text
primary threshold pass
AND
ECONOMICS_POSITIVE
AND
guardrails pass
```

D3 revenue-only:

```text
primary threshold pass
+
economic result limited
```

## Stop

```text
BUDGET_CAP_REACHED
ECONOMICS_INFEASIBLE
POLICY_INCIDENT
CAPACITY_BREACH
TRACKING_FAILURE
```

## Grade

```text
A randomized individual
B alternating window
C matched historical
```

---

# 14. EXP_PARTNER_CODE_SPLIT_V1

## Mapping

```text
Playbook
→ PB_TRACKED_LOCAL_PARTNERSHIP_V1
```

## 목적

제휴처별 고유 code/QR 기반 추천 흐름의 완료 예약과 비용을 비교한다.

## Preferred Method

```text
PARTNER_CODE_SPLIT
```

가능하면:

```text
후보 파트너를 단계 도입
또는
동일 기간 treatment/comparison 그룹
```

## Assignment Unit

```text
PARTNER
```

## Sample Guidance

```text
추적 가능한 partner >= 3
```

적은 unit에서는 Precision LOW.

## Treatment

```text
partner-specific tracked referral
```

## Comparison

```text
no-install / later-start partner
또는
other comparable partner
```

## Primary Metric

```text
completed_bookings_by_partner
```

## Secondary

```text
code_scan_to_booking_rate
cost_per_completed_booking
net_contribution_by_partner
actual_revenue
```

## Guardrails

```text
policy_incident
partner_complaint
untracked_referral
capacity_breach
source_code_collision
```

## Success

```text
partner별 minimum completed booking
+
cost cap
+
guardrails pass
```

## Stop

```text
BUDGET_CAP_REACHED
SOURCE_CODE_COLLISION
POLICY_INCIDENT
PARTNER_COMPLAINT
CAPACITY_BREACH
NO_TRACKED_RESULT_BY_REVIEW_DATE
```

## Grade

```text
B prospective split/step introduction
C observational partner comparison
D no comparison
```

---

# 15. EXP_NO_ACTION_MONITORING_V1

## Mapping

```text
Playbook
→ PB_NO_ACTION_MONITORING_V1
```

## 목적

현재 실행을 보류하고 사전 정의한 Metric과 재평가 trigger를 관찰한다.

## Method

```text
NO_ACTION_MONITORING
```

## Assignment Unit

```text
NONE
```

## Treatment

```text
no new action
```

## Comparison

```text
not applicable
```

## Primary Metric

```text
configured_monitoring_metric
```

예:

```text
demand_index
target_slot_completed_appointments
capacity_status
tracking_readiness
economics_status
```

## Success

이 Playbook에서 “성공”은 매출 증가가 아니다.

```text
review completed on schedule
AND
reopen trigger evaluated
AND
unnecessary spend avoided
```

## Decision

```text
MONITORING_CONTINUE
REOPEN_DECISIONING
NO_ACTION_RECONFIRMED
```

## Stop / Reopen

```text
new critical data
capacity restored
policy approved
tracking configured
economics completed
demand threshold repeated
```

## Grade

```text
D
```

---

# 16. Template 공통 Validation

모든 Template은 다음을 가져야 한다.

```text
template_id
version
playbook mapping
supported method
grade ceiling
assignment unit
primary metric
guardrails
success threshold form
stop conditions
result source
current measurement fallback
```

실행형 Template:

```text
tracking required
owner required
period required
approval required
```

비용-bearing Template:

```text
budget cap
actual spend
cost fields
```

---

# 17. Mapping 구현 Backlog

```text
EXM-001 Template registry
EXM-002 Playbook foreign reference validation
EXM-003 Metric catalog reference validation
EXM-004 Method/Grade validation
EXM-005 sample guidance
EXM-006 threshold/stop template
EXM-007 current Measurement fallback
EXM-008 core 12 fixtures
EXM-009 mapping completeness test
EXM-010 documentation update
```

---

# 18. 완료조건

1. Core Playbook 12개 전부 Template 연결
2. Template ID unique
3. Method와 Grade ceiling
4. Assignment Unit
5. Primary Metric 하나
6. Secondary/Guardrail
7. Success form
8. Stop conditions
9. Result source
10. Current Measurement fallback
11. 비용-bearing economic rule
12. Hospital PII 미사용
13. causal wording 제한
14. mapping completeness fixture
