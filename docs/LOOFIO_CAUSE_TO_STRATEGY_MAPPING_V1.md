---
title: "LOOFIO Cause to Strategy Mapping v1"
version: "1.0"
date: "2026-08-17"
status: "Cause→Strategy 결정 매핑표"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
depends_on:
  - "LOOFIO_DECISION_INPUT_CONTRACT_V1.md"
  - "LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md"
  - "LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md"
  - "LOOFIO_STRATEGY_ENGINE_V1.md"
---

# LOOFIO Cause to Strategy Mapping v1

## 1. 문서 목적

이 문서는 Cause Analysis 결과를 Strategy Candidate로 변환하는 deterministic mapping, 전략별 필요 입력, 차단 조건, Playbook 후보를 정의한다.

이 매핑은 다음을 의미하지 않는다.

```text
Cause가 사실이다
Strategy가 반드시 성공한다
Playbook이 자동 실행된다
```

역할:

```text
Cause Candidate
→ 어떤 Strategy Family를 비교할지 결정
→ 실행 가능성·경제성·정책·측정 Gate
→ Playbook 후보 전달
```

---

# 2. Relation Type

```text
PRIMARY
SECONDARY
CONDITIONAL
INHIBITORY
```

## PRIMARY

해당 Cause를 다루는 기본 전략.

Weight:

```text
1.00
```

## SECONDARY

보조 또는 대체 전략.

Weight:

```text
0.70
```

## CONDITIONAL

추가 데이터·정책·경제성 조건을 충족할 때만 활성화.

Weight:

```text
0.50
```

## INHIBITORY

해당 Cause가 강할수록 전략을 억제.

예:

```text
DEMAND_DEFICIT
→ ACQUISITION 억제
```

Weight:

```text
-1.00
```

---

# 3. 전체 Cause→Strategy Matrix

| Cause | Primary | Secondary | Conditional | Inhibitory |
|---|---|---|---|---|
| `DATA_QUALITY_ARTIFACT` | DATA_COLLECTION | NO_ACTION | - | 모든 실행 전략 |
| `CAPACITY_OR_OPERATION_CONSTRAINT` | CAPACITY_OPERATION | DATA_COLLECTION, NO_ACTION | OFFER_PACKAGING | ACQUISITION, DISCOVERABILITY, RETENTION |
| `OFFER_SLOT_MISMATCH` | CAPACITY_OPERATION, OFFER_PACKAGING | DISCOVERABILITY | RETENTION_REACTIVATION, CONVERSION | ACQUISITION if slot unavailable |
| `RETENTION_GAP` | RETENTION_REACTIVATION | OFFER_PACKAGING | FRONT-DESK 계열 Playbook, PARTNERSHIP_REFERRAL | ACQUISITION when existing cohort sufficient |
| `DISCOVERABILITY_GAP` | DISCOVERABILITY | CONVERSION | ACQUISITION, PARTNERSHIP_REFERRAL | NO_ACTION when measurable low-cost fix exists |
| `DEMAND_DEFICIT` | NO_ACTION, CAPACITY_OPERATION | OFFER_PACKAGING | PARTNERSHIP_REFERRAL, ACQUISITION | paid ACQUISITION without external demand proof |
| `CONVERSION_FRICTION` | CONVERSION | DISCOVERABILITY | OFFER_PACKAGING | ACQUISITION before funnel repair |
| `CHANNEL_MISMATCH` | DISCOVERABILITY | ACQUISITION | PARTNERSHIP_REFERRAL | current ineffective channel continuation |
| `VALUE_OR_PRICE_FRICTION` | OFFER_PACKAGING | CONVERSION | RETENTION_REACTIVATION | discount without economics |
| `CANCELLATION_LEAKAGE` | CANCELLATION_RECOVERY | CAPACITY_OPERATION | RETENTION_REACTIVATION | acquisition before leakage repair |

주: `FRONT-DESK`는 Strategy Family가 아니라 `RETENTION_REACTIVATION` 또는 `CAPACITY_OPERATION` 하위 Playbook 실행 방식이다.

---

# 4. LOW_DEMAND_SLOT Mapping

## 4.1 Core Candidate Set

```text
CAPACITY_OPERATION
RETENTION_REACTIVATION
DISCOVERABILITY
DATA_COLLECTION
NO_ACTION
```

## 4.2 Conditional Candidate Set

```text
CONVERSION
OFFER_PACKAGING
PARTNERSHIP_REFERRAL
ACQUISITION
CANCELLATION_RECOVERY
```

## 4.3 Candidate 생성 순서

```text
1. DATA_QUALITY_ARTIFACT
2. CAPACITY_OR_OPERATION_CONSTRAINT
3. OFFER_SLOT_MISMATCH
4. RETENTION_GAP
5. DISCOVERABILITY_GAP
6. DEMAND_DEFICIT
7. 조건부 Cause
8. DATA_COLLECTION fallback
9. NO_ACTION comparator
```

---

# 5. DATA_QUALITY_ARTIFACT Mapping

## PRIMARY — DATA_COLLECTION

생성 조건:

```text
Cause status = REVIEWABLE / NEEDS_DATA / BLOCKED
critical 또는 blocking data issue 존재
```

필수 출력:

```text
field path
issue
owner
collection/fix method
verification rule
deadline
unblocked strategies
```

Playbook 후보:

```text
PB_LOW_DEMAND_DATA_AUDIT_V1
PB_LOW_DEMAND_TRACKING_SETUP_V1
```

## SECONDARY — NO_ACTION

조건:

- 데이터 교정이 현재 불가능
- Opportunity Evidence를 재현할 수 없음
- 실행 시 오판 위험이 큼

모니터링:

```text
data refresh
mapping correction
new Opportunity regeneration
```

## INHIBITORY

Critical data quality issue는 모든 실행 전략을 차단한다.

---

# 6. CAPACITY_OR_OPERATION_CONSTRAINT Mapping

## PRIMARY — CAPACITY_OPERATION

필수:

```text
business hours
target slot
capacity state
Offering availability
operational owner
```

Playbook:

```text
PB_LOW_DEMAND_CAPACITY_REVIEW_V1
PB_OFFERING_SLOT_REALLOCATION_V1
PB_BOOKING_AVAILABILITY_AUDIT_V1
```

## SECONDARY — DATA_COLLECTION

capacity가 `unknown/conflicting/stale`일 때.

## SECONDARY — NO_ACTION

capacity를 늘릴 수 없고 운영상 의도된 공석일 때.

## CONDITIONAL — OFFER_PACKAGING

Offering 제공은 가능하지만 duration·구성·직원 배치가 슬롯과 맞지 않을 때.

## INHIBITORY

다음 전략을 억제:

```text
RETENTION_REACTIVATION
DISCOVERABILITY
PARTNERSHIP_REFERRAL
ACQUISITION
```

capacity가 `known true`로 확인되기 전에는 final execution 불가.

---

# 7. OFFER_SLOT_MISMATCH Mapping

## PRIMARY — CAPACITY_OPERATION

조건:

- duration/staff/room 배치 문제
- target slot Offering unavailable
- 운영 배치 변경이 핵심

Playbook:

```text
PB_OFFERING_SLOT_REALLOCATION_V1
PB_LOW_DEMAND_CAPACITY_REVIEW_V1
```

## PRIMARY — OFFER_PACKAGING

조건:

- Offering은 제공 가능
- 시간대와 가치·구성의 적합성이 문제
- 정책·경제성 확인

Playbook:

```text
PB_NON_DISCOUNT_VALUE_ADD_V1
PB_TIME_SLOT_OFFER_BUNDLE_V1
```

## SECONDARY — DISCOVERABILITY

Offering은 적합하지만 목표 시간대 노출이 약한 경우.

## CONDITIONAL — RETENTION_REACTIVATION

기존 해당 Offering 고객 cohort가 있고 재방문 주기가 맞는 경우.

## CONDITIONAL — CONVERSION

Offering 노출은 있으나 예약 완료 마찰이 있는 경우.

---

# 8. RETENTION_GAP Mapping

## PRIMARY — RETENTION_REACTIVATION

필수 평가:

```text
eligible cohort
revisit history
capacity
Offering eligibility
consent capability
contact channel
tracking
result source
```

Playbook:

```text
PB_LOW_DEMAND_REVISIT_COHORT_V1
PB_FRONT_DESK_REBOOKING_V1
PB_STAFF_CALLBACK_REVISIT_V1
```

## SECONDARY — OFFER_PACKAGING

기존 고객이 돌아올 이유가 약하고, 정책상 허용되는 비가격 가치 보강이 가능한 경우.

## CONDITIONAL — PARTNERSHIP_REFERRAL

기존 고객이 아니라 연관 고객군을 보완적으로 확보할 때만.

## INHIBITORY — ACQUISITION

다음이면 신규 획득보다 기존 cohort를 먼저 평가한다.

```text
eligible cohort 충분
수동/저비용 실행 가능
측정 가능
```

---

# 9. DISCOVERABILITY_GAP Mapping

## PRIMARY — DISCOVERABILITY

필수:

```text
target slot available
Offering eligible
visibility path
tracking
owner
result source
```

Playbook:

```text
PB_BOOKING_PATH_VISIBILITY_V1
PB_SEARCH_INTENT_SLOT_CAPTURE_V1
PB_MAP_PROFILE_OFFERING_AUDIT_V1
```

## SECONDARY — CONVERSION

노출은 있으나 예약 완료가 낮을 때.

## CONDITIONAL — ACQUISITION

필수 추가:

```text
external demand proxy
paid channel capability
budget cap
economics D4
policy approved
```

## CONDITIONAL — PARTNERSHIP_REFERRAL

지역 보완 채널이 있고 고유 추적 코드를 적용할 수 있을 때.

---

# 10. DEMAND_DEFICIT Mapping

## PRIMARY — NO_ACTION

조건:

```text
반복 저수요
외부 수요 proxy도 낮음
경제성 낮음
capacity를 다른 곳에 사용하는 편이 합리적
```

Playbook:

```text
PB_NO_ACTION_MONITORING_V1
```

## PRIMARY — CAPACITY_OPERATION

시간대 운영 축소·Offering 재배치·staff schedule 조정이 더 합리적일 때.

## SECONDARY — OFFER_PACKAGING

기존 수요가 작지만 특정 Offering 구성 실험의 비용이 낮을 때.

## CONDITIONAL — PARTNERSHIP_REFERRAL

지역 내 complementary audience 근거가 있을 때.

## CONDITIONAL — ACQUISITION

다음 조건을 모두 충족해야 한다.

```text
외부 수요 근거 존재
현재 발견 경로 부족
capacity 확인
D4 economics
tracking
policy
```

## INHIBITORY

외부 수요 근거가 없으면 paid ACQUISITION을 억제한다.

---

# 11. CONVERSION_FRICTION Mapping

## PRIMARY — CONVERSION

필수:

```text
funnel exposure/start/completion
booking path owner
target slot availability
tracking
result source
```

Playbook:

```text
PB_BOOKING_FUNNEL_FRICTION_V1
PB_DEEP_LINK_SLOT_TEST_V1
```

## SECONDARY — DISCOVERABILITY

노출 구조와 예약 경로를 동시에 수정해야 할 때.

## CONDITIONAL — OFFER_PACKAGING

Offering 정보·가치 설명이 funnel 마찰의 일부일 때.

## INHIBITORY — ACQUISITION

현재 funnel이 고장난 상태에서 추가 유입 확대를 억제한다.

---

# 12. CHANNEL_MISMATCH Mapping

## PRIMARY — DISCOVERABILITY

채널별 노출·예약 source mix를 조정한다.

Playbook:

```text
PB_CHANNEL_SOURCE_REALLOCATION_V1
PB_BOOKING_PATH_VISIBILITY_V1
```

## SECONDARY — ACQUISITION

성과가 확인된 유료/신규 채널로 제한적 재배분.

## CONDITIONAL — PARTNERSHIP_REFERRAL

오프라인 referral이 기존 채널보다 추적·경제성 측면에서 적합할 때.

## INHIBITORY

현재 비효율 채널을 그대로 유지하는 Playbook을 차단한다.

---

# 13. VALUE_OR_PRICE_FRICTION Mapping

## PRIMARY — OFFER_PACKAGING

필수:

```text
Offering eligibility
price mode
정책
경제성
result source
```

Playbook:

```text
PB_NON_DISCOUNT_VALUE_ADD_V1
PB_VALUE_EXPLANATION_TEST_V1
```

## SECONDARY — CONVERSION

가격·가치 정보의 제시 방식이 예약 마찰을 만드는 경우.

## CONDITIONAL — RETENTION_REACTIVATION

기존 고객에게 정책상 허용되는 비가격 부가가치를 제안할 때.

## INHIBITORY

경제성 없이 할인하는 전략을 차단한다.

---

# 14. CANCELLATION_LEAKAGE Mapping

## PRIMARY — CANCELLATION_RECOVERY

필수:

```text
cancellation/no-show evidence
reminder/reschedule/waitlist capability
consent/policy
tracking
result source
```

Playbook:

```text
PB_CANCELLATION_FLOW_REVIEW_V1
PB_WAITLIST_RECOVERY_V1
PB_RESCHEDULE_PATH_V1
```

## SECONDARY — CAPACITY_OPERATION

취소 발생 후 슬롯 회수 운영이 핵심일 때.

## CONDITIONAL — RETENTION_REACTIVATION

취소 고객군을 적법한 재예약 흐름으로 연결할 때.

## INHIBITORY — ACQUISITION

기존 예약 이탈이 큰데 신규 유입부터 확대하는 것을 억제한다.

---

# 15. Strategy Input Requirement Matrix

## 15.1 DATA_COLLECTION

| 항목 | 등급 |
|---|:---:|
| missing field paths | R |
| why needed | R |
| owner | R |
| collection method | R |
| verification rule | R |
| deadline/review date | R |
| unblocked strategies | R |
| economics | not applicable |
| result source | O |

최소 Readiness:

```text
D0
```

---

## 15.2 CAPACITY_OPERATION

| 항목 | 등급 |
|---|:---:|
| target slot | R |
| business hours | R |
| capacity state | R |
| Offering availability | R |
| operational owner | B |
| staff/room/equipment detail | O |
| tracking | O/B |
| result source | B for experiment |
| economics | O |

최소 Readiness:

```text
D1 평가
D2 실행
```

---

## 15.3 RETENTION_REACTIVATION

| 항목 | 등급 |
|---|:---:|
| eligible cohort | R |
| revisit history | R |
| capacity | R |
| Offering eligibility | R |
| consent capability | B |
| contact channel | B |
| recent contact history | O/B |
| tracking | B |
| owner | B |
| result source | B |
| economics | O/B if benefit/paid |

최소 Readiness:

```text
D2 평가
D3 실행
D4 경제성 순위
```

---

## 15.4 DISCOVERABILITY

| 항목 | 등급 |
|---|:---:|
| target slot availability | R |
| Offering eligibility | R |
| visibility status/path | R |
| tracking | B |
| owner | B |
| result source | B |
| policy | B |
| channel exposure metrics | O |
| budget | B for paid |
| economics | B for paid |

최소 Readiness:

```text
D2 평가
D3 실행
D4 paid
```

---

## 15.5 CONVERSION

| 항목 | 등급 |
|---|:---:|
| funnel start/end metrics | R |
| booking path owner | R/B |
| target slot availability | R |
| tracking | B |
| result source | B |
| error/step detail | O |
| economics | O |

최소 Readiness:

```text
D2 평가
D3 실행
```

---

## 15.6 OFFER_PACKAGING

| 항목 | 등급 |
|---|:---:|
| Offering eligibility | R |
| policy review | B |
| price mode | R |
| value/price evidence | R/C |
| benefit/discount cost | B if used |
| variable cost | B for net value |
| tracking | B |
| result source | B |
| owner | B |

최소 Readiness:

```text
D2 평가
D3 manual non-price
D4 cost-bearing
```

---

## 15.7 PARTNERSHIP_REFERRAL

| 항목 | 등급 |
|---|:---:|
| partner candidate/audience basis | R |
| partner owner | B |
| partner code/QR | B |
| result source | B |
| policy review | B |
| partner cost/compensation | B |
| budget cap | B |
| capacity | R |
| economics | B |

최소 Readiness:

```text
D3 평가
D4 실행
```

---

## 15.8 ACQUISITION

| 항목 | 등급 |
|---|:---:|
| external demand evidence | R |
| capacity | R |
| Offering eligibility | R |
| paid/organic channel capability | R |
| budget cap | B |
| contribution/economics | B |
| tracking | B |
| result source | B |
| owner | B |
| policy | B |

최소 Readiness:

```text
D3 후보 평가
D4 실행
```

---

## 15.9 CANCELLATION_RECOVERY

| 항목 | 등급 |
|---|:---:|
| cancellation/no-show evidence | R |
| same segment linkage | R |
| reminder/reschedule/waitlist capability | R/O |
| consent | B for contact |
| tracking | B |
| result source | B |
| owner | B |
| policy | B |
| economics | O |

최소 Readiness:

```text
D2 평가
D3 실행
```

---

## 15.10 NO_ACTION

| 항목 | 등급 |
|---|:---:|
| reason code | R |
| monitoring metric | R |
| review date | R |
| reopen trigger | R |
| current limitations | R |
| owner | O |
| result source | not applicable |

최소 Readiness:

```text
D0
```

---

# 16. Playbook Candidate Matrix

| Strategy | 초기 Playbook 후보 |
|---|---|
| DATA_COLLECTION | `PB_LOW_DEMAND_DATA_AUDIT_V1`, `PB_LOW_DEMAND_TRACKING_SETUP_V1` |
| CAPACITY_OPERATION | `PB_LOW_DEMAND_CAPACITY_REVIEW_V1`, `PB_OFFERING_SLOT_REALLOCATION_V1`, `PB_BOOKING_AVAILABILITY_AUDIT_V1` |
| RETENTION_REACTIVATION | `PB_LOW_DEMAND_REVISIT_COHORT_V1`, `PB_FRONT_DESK_REBOOKING_V1`, `PB_STAFF_CALLBACK_REVISIT_V1` |
| DISCOVERABILITY | `PB_BOOKING_PATH_VISIBILITY_V1`, `PB_SEARCH_INTENT_SLOT_CAPTURE_V1`, `PB_MAP_PROFILE_OFFERING_AUDIT_V1` |
| CONVERSION | `PB_BOOKING_FUNNEL_FRICTION_V1`, `PB_DEEP_LINK_SLOT_TEST_V1` |
| OFFER_PACKAGING | `PB_NON_DISCOUNT_VALUE_ADD_V1`, `PB_TIME_SLOT_OFFER_BUNDLE_V1`, `PB_VALUE_EXPLANATION_TEST_V1` |
| PARTNERSHIP_REFERRAL | `PB_TRACKED_LOCAL_PARTNERSHIP_V1` |
| ACQUISITION | `PB_CONTROLLED_SEARCH_ACQUISITION_V1` |
| CANCELLATION_RECOVERY | `PB_CANCELLATION_FLOW_REVIEW_V1`, `PB_WAITLIST_RECOVERY_V1`, `PB_RESCHEDULE_PATH_V1` |
| NO_ACTION | `PB_NO_ACTION_MONITORING_V1` |

이 ID는 다음 Action Playbook 문서에서 최종 확정한다.

---

# 17. LOW_DEMAND_SLOT 결정 흐름

```text
Cause Run blocked by data quality?
├─ yes → DATA_COLLECTION
└─ no
   ↓
Capacity known and available?
├─ no/unknown → CAPACITY_OPERATION or DATA_COLLECTION
└─ yes
   ↓
Reviewable RETENTION_GAP + cohort?
├─ yes → RETENTION_REACTIVATION candidate
└─ no
   ↓
Reviewable DISCOVERABILITY_GAP?
├─ yes → DISCOVERABILITY candidate
└─ no
   ↓
Funnel evidence + CONVERSION_FRICTION?
├─ yes → CONVERSION candidate
└─ no
   ↓
Offering/value evidence?
├─ yes → OFFER_PACKAGING candidate
└─ no
   ↓
External demand + D4 economics?
├─ yes → ACQUISITION/PARTNERSHIP candidate
└─ no
   ↓
Resolvable missing data?
├─ yes → DATA_COLLECTION
└─ no → NO_ACTION
```

실제 구현은 모든 후보를 생성한 뒤 Gate·Score로 비교한다. 위 흐름은 설명용 우선순위다.

---

# 18. 전략 제외 이유 Code

```text
DATA_QUALITY_BLOCKED
CAPACITY_UNKNOWN
CAPACITY_UNAVAILABLE
OFFERING_UNAVAILABLE
ELIGIBLE_COHORT_MISSING
CONSENT_UNKNOWN
CHANNEL_UNAVAILABLE
TRACKING_MISSING
RESULT_SOURCE_MISSING
POLICY_REVIEW_REQUIRED
ECONOMICS_UNKNOWN
ECONOMICS_INFEASIBLE
EXTERNAL_DEMAND_UNPROVEN
FUNNEL_DATA_MISSING
RECENT_DUPLICATE_ACTION
SCORE_BELOW_THRESHOLD
SUPERSEDED_BY_LOWER_COST_OPTION
NO_APPLICABLE_PLAYBOOK
```

사용자 UI에는 code와 설명을 함께 제공한다.

---

# 19. Alternative Comparison Dimension

```text
evidence_fit
expected_net_value
fixed_cost
variable_cost
capacity_fit
policy_risk
measurement_strength
time_to_learning
operational_burden
audience_scope
reusability
```

최소 비교:

- 선택 전략 vs 2위 전략
- 선택 전략 vs NO_ACTION
- paid 전략이면 저비용 전략과 비교

---

# 20. 시나리오

## A. Data Quality Conflict

```text
Selected
→ DATA_COLLECTION

Blocked
→ 모든 실행 전략
```

## B. Capacity False

```text
Selected
→ CAPACITY_OPERATION

Alternative
→ NO_ACTION

Excluded
→ RETENTION / DISCOVERABILITY / ACQUISITION
```

## C. Retention Ready, Economics Partial

```text
RETENTION_REACTIVATION
→ ELIGIBLE_WITH_LIMITATIONS

DISCOVERABILITY
→ ELIGIBLE or NEEDS_DATA

ACQUISITION
→ NEEDS_DATA
```

## D. Discoverability and Funnel Data

```text
DISCOVERABILITY
CONVERSION
→ 둘 다 score
→ 5점 미만 차이면 MULTIPLE_VALID_OPTIONS
```

## E. Demand Deficit + No External Demand

```text
ACQUISITION
→ INFEASIBLE/DEPRIORITIZED

CAPACITY_OPERATION 또는 NO_ACTION
→ 우선
```

## F. Complete D4 Paid Case

```text
ACQUISITION
→ economics/measurement/policy 통과
→ 다른 전략과 score 비교
```

## G. No Tracking

```text
실행 전략
→ NEEDS_DATA

DATA_COLLECTION
→ tracking setup
```

---

# 21. 구현 Checklist

## Mapping

- [ ] Cause code 모두 매핑
- [ ] PRIMARY/SECONDARY/CONDITIONAL/INHIBITORY
- [ ] 조건부 activation
- [ ] duplicate relation 없음

## Gate

- [ ] Data quality
- [ ] Capacity/Offering
- [ ] Consent/Policy
- [ ] Tracking/Measurement
- [ ] Economics

## Comparison

- [ ] 최소 2개 대안
- [ ] 선택·제외 이유
- [ ] NO_ACTION 비교
- [ ] paid vs low-cost 비교

## Privacy

- [ ] patient PII 없음
- [ ] customer token 출력 없음
- [ ] clinical targeting 없음

## Determinism

- [ ] stable candidate set
- [ ] stable score
- [ ] stable tie-break
- [ ] same input same output
