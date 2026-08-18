---
title: "LOOFIO Measurement Framework v1"
version: "1.0"
date: "2026-08-18"
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
  - "LOOFIO_EXPERIMENT_DESIGN_V1.md"
  - "LOOFIO_RECOMMENDATION_PACKAGE_V2.md"
  - "LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md"
---

# LOOFIO Measurement Framework v1

## 1. 문서 목적

이 문서는 LOOFIO Recommendation 또는 Action 실행 후 수집되는 결과를 **과장 없이 계산·해석·저장·학습**하기 위한 Measurement 계약을 정의한다.

LOOFIO가 답해야 하는 질문은 단순히 다음이 아니다.

```text
실행 후 매출이 올랐는가?
```

보다 구체적으로 다음을 구분해야 한다.

```text
실제로 얼마가 발생했는가
기준 기간보다 얼마나 달라졌는가
Action과 연결된 결과가 무엇인가
비교 설계상 어느 정도까지 증분 효과로 추정할 수 있는가
실행비·변동비를 뺀 경제적 가치가 남았는가
다른 시간대·Offering의 매출을 옮긴 것은 아닌가
데이터가 부족해 결론을 내릴 수 없는가
다음 실행에서 무엇을 바꿔야 하는가
```

핵심 원칙:

> Measurement는 Action의 성과를 좋게 보이게 만드는 계층이 아니다.
> 실제 결과, 비교 기준, 추정 범위, 비용, 데이터 품질과 한계를 분리해 다음 의사결정을 더 정확하게 만드는 계층이다.

---

# 2. 현재 구현 Snapshot

현재 `main`의 Result·Measurement는 다음 구조다.

```text
Manual Action 완료
→ Action Result 수동 기록
→ measurement_start_at / measurement_end_at
→ actual_spend(optional)
→ 측정 기간 Appointment 집계
→ 같은 길이의 직전 1~4주 창 집계
→ 평균 Baseline
→ Observed - Baseline signed delta
```

현재 버전:

```text
Action Result
→ manual-action-result-v1

Measurement
→ same-window-prior-four-weeks-v2
```

현재 Metric:

```text
appointment_count
completed_count
cancelled_count
no_show_count
actual_revenue
```

현재 `actual_revenue`:

```text
completed Appointment의 paid_amount 합계
```

현재 구현은 다음을 명시적으로 판단하지 않는다.

```text
Action이 변화를 일으켰는가
Incremental Revenue인가
ROI인가
통계적으로 유의한가
날씨·행사·인력·capacity를 보정했는가
```

Measurement Framework v1은 현재 경로를 제거하지 않는다.

```text
same-window-prior-four-weeks-v2
→ Grade C matched historical 또는 Grade D fallback로 보존
```

---

# 3. 파이프라인 위치

```text
Opportunity
→ Cause Analysis
→ Strategy
→ Playbook
→ Experiment Definition
→ Recommendation Package
→ User Decision
→ Action
→ Action / Experiment Result
→ Measurement Definition
→ Measurement Run
→ Measurement Result
→ Economic Evaluation
→ Learning Record
→ Next Decision Context
```

Measurement는 다음을 다시 선택하지 않는다.

```text
Cause
Strategy
Playbook
Treatment
Primary Metric
Success Threshold
Stop Condition
```

이 값들은 실행 전 Experiment Definition에서 고정한다.

---

# 4. Measurement 6계층 모델

```text
MeasurementDefinition
        ↓ execute
MeasurementRun
        ↓ collect
ObservedResult
        ↓ compare
ComparativeMeasurement
        ↓ interpret
EconomicEvaluation
        ↓ learn
DecisionOutcomeRecord
```

## 4.1 `MeasurementDefinition`

어떤 Metric을 어떤 Source와 Method로 계산할지 정의한다.

포함:

```text
method
metric definitions
observation window
comparison window / group
attribution
evidence grade plan
precision requirements
cost requirements
limitations
version
```

## 4.2 `MeasurementRun`

실제 계산 실행 단위.

포함:

```text
input source refs
status
started/completed
data quality
calculation version
```

## 4.3 `ObservedResult`

실제로 관찰된 사실.

예:

```text
완료 예약 7건
실제 완료 매출 560,000원
실제 지출 120,000원
수신거부 1건
```

## 4.4 `ComparativeMeasurement`

Observed와 Comparison/Baseline의 차이.

예:

```text
Treatment completion rate - Control completion rate
Observed completed count - matched historical baseline
```

## 4.5 `EconomicEvaluation`

비용과 기여가치.

예:

```text
Actual Spend
Contribution per Completion
Incremental Contribution Estimate
Break-even Result
```

## 4.6 `DecisionOutcomeRecord`

다음 Recommendation에 재사용할 학습 단위.

```text
Opportunity Context
Cause
Strategy
Playbook
Experiment
Decision
Action
Result
Measurement
Evidence Grade
Precision
Economics
Limitations
```

---

# 5. 핵심 의미 계층

다음 값을 같은 필드나 같은 문장으로 합치지 않는다.

## 5.1 `Actual Result`

실제 Source에서 관찰된 값.

```text
actual_completed_appointments
actual_revenue
actual_spend
actual_cancellation_count
```

## 5.2 `Opportunity Estimate`

Opportunity 탐지 시점에 계산한 잠재 가치 범위.

```text
estimated_opportunity_value_low
estimated_opportunity_value_high
```

실행 결과가 아니다.

## 5.3 `Baseline`

Action이 없었을 경우를 비교하기 위한 기준.

종류:

```text
concurrent control
alternating comparison
matched historical
prior-window average
no-action monitoring
```

Baseline은 사실상의 counterfactual 근사이며 실제 미실행 세계를 직접 관찰한 값이 아니다.

## 5.4 `Observed Delta`

```text
Observed Value - Baseline Value
```

단순 차이다.

```text
observed_delta
!=
incremental_effect
```

## 5.5 `Attributed Result`

Tracking 또는 Source Code로 Action과 직접 연결된 결과.

예:

```text
action_id가 연결된 예약
partner_code로 연결된 완료 예약
booking_source_code로 연결된 예약
```

Attributed는 증분을 의미하지 않는다.

Action을 거치지 않았어도 발생했을 수 있다.

## 5.6 `Incremental Estimate`

Treatment와 Comparison의 사전 정의된 차이를 기반으로 Action 때문에 추가됐을 가능성이 있는 결과를 추정한 값.

사용 조건:

```text
유효한 비교 설계
result source 검증
assignment / contamination 검토
Evidence Grade와 Precision 표시
```

## 5.7 `Net Contribution Estimate`

```text
Incremental Outcome Estimate
× Contribution per Outcome
- Incremental Execution Cost
```

비용이 완전하지 않으면 계산하지 않는다.

---

# 6. Measurement 상태

```text
PENDING
COLLECTING
READY_TO_CALCULATE
COMPLETED
INCONCLUSIVE
INVALIDATED
FAILED
SUPERSEDED
```

## `PENDING`

Action 또는 Experiment가 아직 시작되지 않음.

## `COLLECTING`

Observation·follow-up window가 진행 중.

## `READY_TO_CALCULATE`

필수 Result Source와 기간이 닫힘.

## `COMPLETED`

계약에 따라 계산 완료.

성과가 긍정적이라는 의미가 아니다.

## `INCONCLUSIVE`

계산은 가능하지만 표본·Precision·결과 지연·비교 불균형 때문에 의사결정 근거가 부족.

## `INVALIDATED`

Tracking·assignment·데이터 품질·실행 중 계약 변경 때문에 해석 불가.

## `FAILED`

예상하지 못한 계산 오류.

## `SUPERSEDED`

새 Measurement version 또는 수정된 Experiment가 기존 결과를 대체.

---

# 7. Measurement Result 판단

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

필수:

- Success Threshold 통과
- Hard Guardrail 통과
- Result Source 유효
- Evidence Grade와 Precision 표시
- 경제성 결과를 과장하지 않음

다른 사업장·기간에서도 같은 효과가 난다는 뜻이 아니다.

## `NO_CLEAR_EFFECT`

유효한 Measurement지만 명확한 긍정·부정 차이가 없음.

## `NEGATIVE_OR_HARMFUL`

Primary Metric 악화, 경제성 악화 또는 Hard Guardrail 위반.

## `INCONCLUSIVE`

실험 계약은 유효하지만 표본·결과 수·정밀도 부족.

## `INVALIDATED`

결과 자체를 해석하기 어려움.

## `OPERATIONAL_LEARNING_ONLY`

Capacity·Tracking·Booking Path 같은 운영 검증.

## `DATA_QUALITY_RESOLVED`

데이터 품질 Playbook의 목표가 달성됨.

---

# 8. Evidence Grade와 Precision

## 8.1 Evidence Grade

```text
A
B
C
D
```

설계 강도를 나타낸다.

| Grade | 대표 Method | 허용 해석 |
|---|---|---|
| A | Randomized Holdout | 비교군 대비 증분 Estimate 검토 가능 |
| B | Cluster/Shift, Alternating, Controlled Route | 제한적 증분 Estimate 검토 가능 |
| C | Matched Historical, prior-four-weeks | 관찰 비교 중심 |
| D | Before/After, Diagnostic, Manual Attribution | 신호·운영 학습 중심 |

## 8.2 Precision

```text
UNKNOWN
INSUFFICIENT
LOW
MODERATE
HIGH
```

Grade와 별개다.

```text
Grade A + Precision LOW
→ 무작위 설계지만 결과 표본이 작음
```

## 8.3 표현 규칙

### Grade A/B

다음과 같은 표현을 사용할 수 있다.

> Treatment와 Comparison의 차이를 기준으로 완료 예약 3건의 증분 효과 후보가 관찰됐습니다. Precision은 낮습니다.

### Grade C/D

다음과 같이 표현한다.

> 실행 기간의 완료 예약은 비교 기간보다 3건 많았습니다. Action의 인과효과로 단정할 수 없습니다.

금지:

> LOOFIO가 예약 3건을 만들었습니다.

---

# 9. Method Taxonomy v1

## 9.1 `RANDOMIZED_TREATMENT_CONTROL_V1`

입력:

```text
stable assignment
treatment outcomes
control outcomes
```

대표:

```text
재방문 cohort
비가격 가치 실험
```

Grade ceiling:

```text
A
```

## 9.2 `EXPLORATORY_RANDOMIZED_V1`

작은 표본의 무작위 비교.

Grade ceiling:

```text
B
```

## 9.3 `CLUSTER_OR_SHIFT_COMPARISON_V1`

직원 shift·일자·파트너 단위 비교.

Grade ceiling:

```text
B
```

## 9.4 `ALTERNATING_WINDOW_COMPARISON_V1`

Treatment와 Comparison 시간대를 교대.

Grade ceiling:

```text
B
```

## 9.5 `CONTROLLED_ROUTE_COMPARISON_V1`

예약 경로 A/B.

Grade ceiling:

```text
B
```

## 9.6 `PARTNER_CODE_COMPARISON_V1`

제휴처별 고유 code/QR.

Grade ceiling:

```text
B
```

동시 비교 없이 제휴처별 관찰만 하면 C.

## 9.7 `MATCHED_HISTORICAL_V1`

같은 요일·시간대·Offering의 과거 창과 비교.

Grade ceiling:

```text
C
```

## 9.8 `SAME_WINDOW_PRIOR_FOUR_WEEKS_V2`

현재 구현.

```text
observation window
vs
같은 길이의 직전 1~4주 창 평균
```

Grade:

```text
C
```

다음 조건이 약하면 D로 표시할 수 있다.

```text
comparison windows 부족
Offering/slot scope 불일치
capacity·운영 변화
result source 부분 누락
```

## 9.9 `BEFORE_AFTER_EXPLORATORY_V1`

단순 실행 전후.

Grade:

```text
D
```

## 9.10 `DIAGNOSTIC_VERIFICATION_V1`

참/거짓·Issue 해결·Tracking 연결 검증.

Grade:

```text
D
```

## 9.11 `NO_ACTION_MONITORING_V1`

실행하지 않고 재평가 Trigger 관찰.

Grade:

```text
D
```

---

# 10. Metric Catalog v1

## 10.1 Count

```text
appointment_count
completed_appointments
cancelled_appointments
no_show_appointments
target_slot_completed_appointments
completed_revisit_appointments_in_target_slot
completed_bookings_from_target_path
completed_bookings_by_partner
```

## 10.2 Rate

```text
booking_completion_rate
booking_to_completion_rate
on_site_rebooking_rate
contact_to_booking_rate
cancellation_rate
no_show_rate
refusal_or_unsubscribe_rate
```

Rate는 분자·분모를 사전 고정한다.

## 10.3 Revenue

```text
actual_revenue
revenue_per_completion
observed_revenue_delta
attributed_revenue
incremental_revenue_estimate
```

## 10.4 Economics

```text
actual_spend
media_cost
message_cost
benefit_cost
partner_cost
staff_time_cost
additional_service_cost
contribution_per_completion
cost_per_completed_booking
net_contribution_estimate
break_even_completions
```

## 10.5 Operational

```text
sellable_slot_status_verified
available_service_minutes
completed_appointments_per_sellable_slot_hour
eligible_staff_count
booking_availability_mismatch_count
steps_to_book
booking_path_error_count
staff_overtime_minutes
```

## 10.6 Guardrail

```text
complaint_count
policy_incident_count
tracking_failure_count
capacity_breach_count
other_slot_displacement
other_offering_displacement
assignment_contamination_count
```

---

# 11. Metric Definition Contract

```json
{
  "metric_code": "booking_completion_rate",
  "metric_version": "booking-completion-rate-v1",
  "role": "PRIMARY",
  "unit": "rate",
  "numerator": {
    "event": "completed_booking"
  },
  "denominator": {
    "event": "booking_start"
  },
  "filters": {
    "business_id": "BIZ_01",
    "weekday": "TUE",
    "start_hour": 14,
    "end_hour": 16
  },
  "source": "normalized_booking_funnel",
  "missing_behavior": "INVALIDATE_IF_MATERIAL",
  "direction": "increase"
}
```

## 규칙

- Metric Version 필수.
- 실행 후 numerator/denominator 변경 금지.
- 필터·시간대·Offering scope 고정.
- 금액은 Decimal + currency.
- Result Source와 lineage 기록.
- AI가 Metric 정의를 만들거나 변경하지 않음.

---

# 12. Observed Result Contract

```json
{
  "result_id": "MRESULT_xxx",
  "source_type": "EXPERIMENT_RESULT",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "action_id": "ACT_01",
  "experiment_id": "EXP_01",
  "observation_window": {
    "start_at": "2026-08-20T00:00:00+09:00",
    "end_at": "2026-09-03T00:00:00+09:00"
  },
  "metrics": [
    {
      "metric_code": "completed_revisit_appointments_in_target_slot",
      "value": "4",
      "unit": "completed_appointments",
      "source_status": "VERIFIED"
    },
    {
      "metric_code": "actual_revenue",
      "value": {
        "amount": "320000.00",
        "currency": "KRW"
      },
      "source_status": "VERIFIED"
    }
  ],
  "actual_costs": [],
  "data_quality": {},
  "limitations": []
}
```

---

# 13. Comparison Contract

```text
comparison_type
treatment definition
comparison definition
metric definition
observed treatment
observed comparison
raw difference
normalized difference
precision
limitations
```

## Count Delta

```text
Count Delta
=
Treatment Count
-
Comparison Count
```

직접 비교 가능한 동일 크기·기간일 때만 사용한다.

## Rate Delta

```text
Treatment Rate
-
Comparison Rate
```

각 Rate의 denominator를 표시한다.

## Historical Delta

```text
Observed Value
-
Historical Baseline Average
```

## Relative Delta

```text
(Observed - Baseline) / Baseline
```

Baseline = 0이면 계산하지 않고 `not_applicable` 또는 별도 absolute delta를 사용한다.

---

# 14. Incremental Outcome Estimate

## 14.1 Individual Treatment-Control

```text
Treatment Rate
=
Treatment Outcomes / Treatment Assigned

Control Rate
=
Control Outcomes / Control Assigned

Rate Difference
=
Treatment Rate - Control Rate
```

```text
Incremental Outcomes Estimate
=
Rate Difference × Treatment Assigned
```

표시:

- Point estimate
- Treatment/control sample
- Precision
- Evidence Grade
- Contamination
- Limitations

## 14.2 Cluster / Window

단위가 동일하고 exposure가 비교 가능할 때:

```text
Average Treatment Outcome per Unit
-
Average Comparison Outcome per Unit
```

필요하면 Treatment Unit 수에 적용한다.

작은 cluster 수에서는 `INCONCLUSIVE`를 우선한다.

## 14.3 Historical

Grade C/D에서는 기본적으로:

```text
Observed Delta
```

만 제공한다.

`incremental_estimate`는 null을 유지한다.

예외적으로 향후 별도 method version이 정의되기 전에는 Grade C/D에서 증분 수치를 계산하지 않는다.

---

# 15. Actual Revenue

```text
Actual Revenue
=
completed Appointment의 paid_amount 합계
```

## 필수 표시

```text
payment coverage
currency
observation window
Offering/slot scope
source status
```

## 제한

- `booked` 가격은 actual revenue가 아님.
- list price는 actual revenue가 아님.
- 결제 누락은 0원이 아님.
- 환불·취소 결제 모델이 추가되면 별도 version이 필요.
- Grade와 무관하게 Actual Revenue는 실제 관측값이다.

---

# 16. Cost Capture Contract

## Cost Type

```text
MEDIA
MESSAGE
BENEFIT
PARTNER
STAFF_TIME
ADDITIONAL_SERVICE
PRODUCTION
PLATFORM
OTHER
```

## Cost Record

```json
{
  "cost_type": "STAFF_TIME",
  "status": "unknown",
  "planned_amount": null,
  "actual_amount": null,
  "currency": "KRW",
  "quantity": null,
  "unit_cost": null,
  "source": null,
  "notes": "운영자 검토 시간이 기록되지 않았습니다."
}
```

## 상태

```text
VERIFIED
ESTIMATED
UNKNOWN
NOT_APPLICABLE
CONFLICTING
```

## 규칙

- `UNKNOWN`을 0으로 처리하지 않는다.
- Planned와 Actual 분리.
- Estimated 비용으로 Net Contribution을 계산하면 `estimate` 표시.
- Actual Spend가 없으면 `actual_spend = unknown`.
- Budget Cap과 Actual Spend 비교 가능.

---

# 17. Contribution 계산

## 17.1 Contribution per Completion

```text
Contribution per Completion
=
Net Revenue per Completion
- Variable Cost per Completion
- Benefit Cost per Completion
- Incremental Service Cost per Completion
```

필수:

```text
모든 주요 구성요소 complete
또는
누락 구성요소가 명시적으로 not_applicable
```

## 17.2 Incremental Revenue Estimate

```text
Incremental Revenue Estimate
=
Incremental Completed Outcomes Estimate
× Net Revenue per Completion
```

Grade A/B와 적절한 Result Source에서만 검토한다.

## 17.3 Net Contribution Estimate

```text
Net Contribution Estimate
=
Incremental Completed Outcomes Estimate
× Contribution per Completion
- Incremental Fixed Execution Cost
```

## 17.4 Break-even

```text
Break-even Completed Outcomes
=
Incremental Fixed Execution Cost
/
Contribution per Completion
```

Contribution <= 0이면 `infeasible`.

## 17.5 Revenue-only

비용이 incomplete하면:

```text
Incremental Revenue Estimate
→ 가능할 수 있음

Net Contribution Estimate
→ null

Economics Status
→ partial
```

---

# 18. Opportunity Estimate와 Result 비교

Opportunity 단계의 잠재 가치와 실행 결과를 비교할 수 있지만 의미를 섞지 않는다.

```text
Opportunity Estimate
→ 비교 시간대 수준을 가정한 잠재 범위

Experiment Result
→ 실제 실행 후 관찰/비교 결과
```

허용:

> 초기 Opportunity Estimate 상한은 460,000원이었고, 실행 기간의 Actual Revenue는 320,000원이었습니다. 두 값은 계산 목적이 다릅니다.

금지:

> 예상했던 460,000원 중 320,000원을 회수했습니다.

별도 attribution/estimand가 없으면 회수율을 계산하지 않는다.

---

# 19. Attribution Window

Action·Playbook별로 정의한다.

## 필드

```text
exposure_start/end
booking_attribution_window
completion_followup_window
late_result_behavior
source precedence
```

## 예

### Revisit

```text
exposure → booking: 7일
experiment end → completion follow-up: 14일
```

### Partner

```text
partner code 유효기간
+
예약 완료 follow-up
```

### Front Desk

```text
on-site rebooking: 방문 당일
completed revisit: 예약 완료일까지
```

## 규칙

- 모든 Action에 같은 기간 적용 금지.
- 실행 전에 고정.
- Late Result는 별도 표시.
- Attribution Window 밖 Result를 임의 포함하지 않음.
- Booking과 Completion을 별도 관찰.

---

# 20. Result Source 우선순위

```text
1. normalized completed Appointment
2. verified payment transaction
3. booking source code / action_id
4. verified connector event
5. manual verified result
6. self-reported unverified result
```

Source Status:

```text
VERIFIED
PARTIAL
MISSING
CONFLICTING
STALE
UNVERIFIED
```

Primary Metric Source가 `MISSING` 또는 `CONFLICTING`이면:

```text
INCONCLUSIVE
또는
INVALIDATED
```

---

# 21. Baseline 선택 규칙

## 21.1 Concurrent Control

가장 우선.

```text
same period
same eligibility
treatment/control assignment
```

## 21.2 Alternating / Cluster Comparison

```text
same weekday/slot/Offering
prospective assignment
```

## 21.3 Matched Historical

필수:

```text
same weekday
same slot
same duration
same Offering scope
same location
same metric version
```

가능하면 확인:

```text
holiday
weather
event
staff/capacity
price/Offering change
other Action
```

## 21.4 Prior Four Weeks

현재 구현을 사용.

```text
same-window-prior-four-weeks-v2
```

필수 limitation을 유지한다.

---

# 22. External Context

사용 목적:

```text
comparison window 적합성 검토
limitation
결과 해석 보조
후속 Cause 재평가
```

External Context만으로 인과 조정을 완료했다고 표시하지 않는다.

예:

> Treatment 기간에 지역 행사가 있어 비교 가능성이 낮아 Evidence Grade를 C로 하향했습니다.

금지:

> 지역 행사 효과를 완전히 제거한 순수 Action 효과입니다.

---

# 23. Contamination / Crossover

## Contamination

Comparison 단위가 Treatment를 받음.

## Crossover

배정된 단위가 다른 조건으로 이동.

## 기록

```text
assigned_treatment_count
assigned_comparison_count
treatment_exposed_count
comparison_exposed_count
contamination_count
crossover_count
missing_assignment_count
```

## 처리

Template별 사전 Threshold를 사용한다.

결과:

```text
Continue with limitation
Grade downgrade
INCONCLUSIVE
INVALIDATED
```

실행 후 임의 기준을 만들지 않는다.

---

# 24. Displacement / Cannibalization

저수요 슬롯 결과가 좋아도 다른 매출을 이동시킨 것일 수 있다.

필수 검토:

```text
target slot change
other slot change
target Offering change
other Offering change
total completed appointments
total actual revenue
existing customer reschedule
staff capacity movement
```

## Net Outcome View

```text
Target Segment Delta
Other Segment Delta
Business Total Delta
```

## 규칙

- 다른 슬롯 감소를 숨기지 않는다.
- 같은 고객의 예약 시간 이동을 신규 예약으로 중복 계산하지 않는다.
- target slot만으로 Incremental Revenue 계산 금지.
- total business outcome과 segment outcome을 함께 표시한다.

---

# 25. Guardrail Evaluation

Guardrail 상태:

```text
PASSED
BREACHED
NOT_OBSERVED
UNKNOWN
NOT_APPLICABLE
```

Hard Guardrail이 `BREACHED`이면:

```text
SUCCESS_CANDIDATE 불가
NEGATIVE_OR_HARMFUL 또는 STOPPED 검토
```

예:

```text
complaint threshold
policy incident
capacity breach
staff overload
tracking failure
```

---

# 26. Data Quality and Precision

## Data Completeness

```text
expected records
observed records
missing records
coverage rate
```

## Precision Input

```text
assignment count
treatment count
comparison count
outcome count
missing outcome count
cluster/window count
```

## Precision Rule v1

v1에서 자동 신뢰구간을 필수로 하지 않는다.

대신 deterministic rule로:

```text
INSUFFICIENT
LOW
MODERATE
HIGH
```

를 부여한다.

향후 통계 모듈이 추가되면 별도 `precision-method-v2`로 확장한다.

---

# 27. Measurement Output Contract

```json
{
  "measurement_id": "MEAS_xxx",
  "measurement_version": "measurement-framework-v1",
  "method": {
    "code": "RANDOMIZED_TREATMENT_CONTROL_V1",
    "version": "1.0"
  },
  "status": "COMPLETED",
  "decision": "INCONCLUSIVE",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "opportunity_id": "OPP_01",
  "recommendation_package_id": "RPKG_01",
  "action_id": "ACT_01",
  "experiment_id": "EXP_01",
  "windows": {},
  "evidence_grade": "A",
  "precision_status": "LOW",
  "result_sources": [],
  "primary_metric": {
    "metric_code": "completed_revisit_appointments_in_target_slot",
    "treatment": {
      "numerator": 4,
      "denominator": 58,
      "rate": 0.06897
    },
    "comparison": {
      "numerator": 1,
      "denominator": 14,
      "rate": 0.07143
    },
    "observed_delta": -0.00246,
    "incremental_estimate": null
  },
  "secondary_metrics": [],
  "guardrails": [],
  "actual_revenue": {
    "amount": "320000.00",
    "currency": "KRW",
    "coverage_status": "VERIFIED"
  },
  "costs": [],
  "economics": {
    "status": "partial",
    "net_contribution_estimate": null
  },
  "contamination": {},
  "displacement": {},
  "external_context": [],
  "success_threshold_result": "NOT_PASSED",
  "limitations": [
    "표본이 작아 정밀도가 낮습니다.",
    "변동원가가 없어 순기여이익을 계산하지 않습니다."
  ],
  "calculated_at": "2026-09-18T12:00:00+09:00"
}
```

---

# 28. Current Measurement Adapter

현재 `ActionMeasurement`를 새 Framework에 연결한다.

## 현재 입력

```text
action_id
result_id
observation rows
baseline row windows
start_at
end_at
```

## Adapter 결과

```text
method.code
→ SAME_WINDOW_PRIOR_FOUR_WEEKS_V2

evidence_grade
→ C 기본

precision_status
→ baseline window count와 outcome count 기반

observed
→ current observed metrics

baseline
→ current baseline_average

observed_delta
→ current change_from_baseline

incremental_estimate
→ null

economics
→ actual_spend가 있더라도 current method에서는 net contribution null

limitations
→ 현재 3개 limitation 보존
```

## Grade D 하향 후보

```text
baseline window count < 2
comparison scope mismatch
capacity change
major other Action
result source partial
```

기존 API 의미를 변경하지 않고 additive response 또는 새 endpoint로 확장한다.

---

# 29. User-facing 표현 규칙

## 실제값

> 측정 기간에 완료 예약 7건과 실제 완료 매출 560,000원이 기록됐습니다.

## Grade C 관찰 차이

> 같은 길이의 직전 4주 창 평균보다 완료 예약이 2.8건 많았습니다. Action의 인과효과로 단정할 수 없습니다.

## Grade A/B 증분 후보

> Treatment와 Comparison의 차이를 기준으로 완료 예약의 증분 효과 후보가 관찰됐습니다. Evidence Grade는 B이고 Precision은 낮습니다.

## 경제성 Partial

> 실행비 120,000원은 확인됐지만 변동원가가 없어 순기여이익은 계산하지 않습니다.

## 결과 없음

> 명확한 효과가 관찰되지 않았습니다.

## 데이터 부족

> 결과 연결이 불완전해 결론을 내릴 수 없습니다.

금지:

```text
LOOFIO가 만든 매출
보장된 추가 매출
실패한 캠페인
효과가 없는 전략
```

데이터 실패·표본 부족·유효한 무효 결과를 구분한다.

---

# 30. Persistence 제안

현재 Measurement는 요청 시 계산한다.

Decision Intelligence 확장 시 다음을 검토한다.

```text
measurement_definitions
measurement_runs
measurement_metric_results
measurement_comparisons
measurement_cost_records
measurement_guardrail_results
measurement_context_observations
measurement_evaluations
decision_outcome_records
```

## 저장 원칙

```text
Definition / Method / Version
Source refs
Calculation inputs hash
Calculated result
Limitations
Evidence Grade
Precision
```

원본 Appointment를 복제 저장하지 않는다.

과거 Measurement를 새 Method로 덮어쓰지 않고 새 Run을 생성한다.

---

# 31. API 후보

## 현재 호환

```text
GET /api/v1/actions/{actionId}/measurements
```

기존 response 유지.

## 확장 Preview

```text
POST /api/v1/experiments/{experimentId}/measurements/preview
```

## Persistence

```text
POST /api/v1/experiments/{experimentId}/measurements
GET  /api/v1/measurements/{measurementId}
GET  /api/v1/actions/{actionId}/measurement-history
POST /api/v1/measurements/{measurementId}/recalculate
```

`recalculate`는 기존 결과를 수정하지 않고 새 Run을 만든다.

---

# 32. Versioning

버전 필수:

```text
metric definition
measurement method
baseline selection
precision rule
economic calculation
context adjustment
evaluation decision
```

예:

```text
measurement-framework-v1
same-window-prior-four-weeks-v2
precision-rule-v1
economics-evaluation-v1
```

버전 변경 조건:

- 공식 변경
- 분모·필터 변경
- Baseline 규칙 변경
- 비용 포함 범위 변경
- Evidence Grade 규칙 변경
- Decision 상태 규칙 변경

---

# 33. Determinism

동일 입력:

```text
Measurement Definition
Experiment Definition
Action/Result source refs
Metric versions
Method version
Cost records
External Context snapshot
Calculation as_of
```

동일 결과:

- Metric values
- Baseline
- Delta
- Incremental Estimate
- Evidence Grade
- Precision
- Economics
- Decision
- Limitations

AI는 계산에 관여하지 않는다.

---

# 34. 오류 계약

```text
MEASUREMENT_DEFINITION_INVALID
MEASUREMENT_RESULT_SOURCE_REQUIRED
MEASUREMENT_RESULT_SOURCE_CONFLICT
MEASUREMENT_WINDOW_INVALID
MEASUREMENT_METRIC_INVALID
MEASUREMENT_BASELINE_UNAVAILABLE
MEASUREMENT_ASSIGNMENT_INVALID
MEASUREMENT_COMPARISON_INVALID
MEASUREMENT_TRACKING_FAILURE
MEASUREMENT_COST_INPUT_REQUIRED
MEASUREMENT_ECONOMICS_INCOMPLETE
MEASUREMENT_CONTAMINATION_EXCEEDED
MEASUREMENT_DISPLACEMENT_UNRESOLVED
MEASUREMENT_INVALIDATED
MEASUREMENT_IMMUTABLE
TENANT_SCOPE_MISMATCH
PII_FIELD_REJECTED
UNSUPPORTED_MEASUREMENT_VERSION
MEASUREMENT_INTERNAL_ERROR
```

---

# 35. 테스트 전략

## Current Adapter

- 현재 observed/baseline/delta 동일
- 1~4주 Baseline
- signed negative/positive delta
- actual revenue
- limitation 3개 보존
- Grade C/D adapter

## Metric

- numerator/denominator
- baseline = 0
- Decimal Money
- missing payment
- timezone
- segment filter
- metric version

## Experiment Comparison

- treatment/control rate
- assignment count
- cluster/window comparison
- historical comparison
- contamination
- precision

## Economics

- unknown != 0
- planned vs actual
- contribution complete/partial
- break-even
- negative contribution
- budget cap

## Evaluation

- success threshold
- guardrail breach
- Grade/Precision
- inconclusive
- invalidated
- negative/harmful
- operational-only

## Security

- tenant/business
- customer token not exposed
- patient PII reject
- clinical data not used

## Regression

- existing Action Result API
- existing Measurement API
- Recommendation Package / Experiment links
- deterministic recalculation

---

# 36. Local Implementation Backlog

```text
MF-001 Measurement terminology/value objects
MF-002 Method taxonomy
MF-003 Metric catalog v1
MF-004 Measurement Definition schema
MF-005 Current Measurement adapter
MF-006 Treatment/Control calculator
MF-007 Historical baseline calculator
MF-008 Evidence Grade / Precision
MF-009 Result Source quality
MF-010 Cost capture
MF-011 Economics calculator
MF-012 Contamination / Displacement
MF-013 Guardrail evaluation
MF-014 Measurement decision engine
MF-015 Output contract
MF-016 Preview API
MF-017 Persistence proposal
MF-018 User-facing wording
MF-019 Fixtures / Regression
MF-020 ADR / Current Status update
```

---

# 37. 첫 구현 순서

## Step 1 — Adapter 우선

현재 `same-window-prior-four-weeks-v2` 결과를 새 Output Contract로 감싼다.

목표:

- 기존 숫자 불변
- Evidence Grade C
- Precision
- 의미 계층 분리

## Step 2 — Experiment Result Contract

Treatment/Comparison 결과를 받을 구조를 만든다.

## Step 3 — Grade A/B 계산

- randomized
- cluster/window

## Step 4 — Cost/Economics

Actual Spend와 cost completeness를 추가한다.

## Step 5 — Decision Outcome Record

Playbook별 결과 학습 구조를 만든다.

---

# 38. 완료조건

Measurement Framework v1 완료조건:

1. Actual/Estimate/Baseline/Delta/Incremental 분리
2. Measurement 6계층 모델
3. Method Taxonomy
4. Evidence Grade와 Precision 분리
5. Metric Catalog/version
6. Treatment/Comparison 계산
7. Grade C/D causal 표현 금지
8. Actual Revenue 정의
9. Cost unknown과 0 분리
10. Contribution/Break-even 규칙
11. Attribution Window
12. Result Source 상태
13. Contamination/Crossover
14. Displacement
15. Guardrail
16. Current Measurement adapter
17. Deterministic calculation
18. tenant/PII 안전
19. 회귀 테스트
20. 코드 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 39. 구현 연결

Channel Execution·Data Schema·API Contract 설계가 완료됐다.

첫 구현은 기존 `same-window-prior-four-weeks-v2`를 새 의미 계층으로 감싸는 Adapter부터 시작한다.

```text
MF-001~MF-005
→ MF-008~MF-009
→ MF-015
→ MF-018~MF-020
```

Grade A/B 계산과 Persistence는 첫 Package Preview·Manual Pilot 이후로 유지한다.
