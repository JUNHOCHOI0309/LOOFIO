---
title: "LOOFIO Decision Input Contract v1"
version: "1.0"
date: "2026-08-17"
status: "로컬 구현용 상세 데이터 계약"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
initial_domain: "Hospital Appointment MVP"
---

# LOOFIO Decision Input Contract v1

## 1. 문서 목적

현재 Appointment CSV와 Opportunity 데이터는 **문제가 어디에서 관측되는지**를 찾는 데 충분하다.

하지만 다음 중 무엇이 더 적합한 해결책인지 판단하기에는 부족하다.

```text
재방문 고객군 활성화
검색·예약 경로 개선
검색광고
현장 재예약
대기 명단
지역 제휴
Offering 재배치
직원·capacity 조정
아무 행동도 하지 않음
추가 데이터 수집
```

이 문서는 Opportunity를 일반적인 조언이 아닌 **구체적이고 경제적이며 측정 가능한 Action Plan Package**로 변환하기 위해 필요한 입력값을 정의한다.

핵심 원칙:

> Recommendation 품질은 모델 성능보다 입력 데이터의 범위·출처·신선도·제약 표현에 먼저 제한된다.

---

# 2. 적용 위치

```text
Opportunity
+ Evidence
+ Limitations
        ↓
Decision Input Resolver
        ↓
Decision Context Snapshot
        ↓
Cause Analysis
        ↓
Strategy / Playbook / Economics / Experiment
```

`Decision Context`는 Opportunity의 Observation·Estimate를 수정하지 않는다.

---

# 3. 현재 Domain과 범위

초기 적용:

```text
APPOINTMENT_HEALTH
→ Hospital Appointment MVP
```

현재 사용 가능한 내부 데이터:

- Business
- Location
- Offering
- Customer token
- Appointment
- paid amount
- Opportunity
- Opportunity Evidence
- Recommendation decision
- Action
- Action Result
- baseline Measurement

현재 없는 데이터:

- 직원별 근무와 Offering 수행 가능 정보
- 실제 slot capacity
- Offering별 변동원가
- 마케팅 예산·최대 CAC
- 마케팅 동의/접촉 가능 상태
- 채널 연결·추적 능력
- 과거 캠페인 구조화 성과
- External Context
- persisted Decision Context

따라서 본 계약은 현재 DB에 존재하는 값을 재사용하면서 부족한 입력을 명시적으로 수집하는 additive 설계다.

---

# 4. 계약의 핵심 객체

```text
DecisionContextSnapshot
├─ Metadata
├─ GoalContext
├─ BusinessConstraintContext
├─ EconomicsContext
├─ OperationalCapacityContext
├─ OfferingEligibilityContext
├─ CustomerActivationContext
├─ ChannelCapabilityContext
├─ HistoricalActionContext
├─ ExternalContextSummary
├─ PolicyConstraintContext
├─ MeasurementCapabilityContext
├─ AssumptionRegistry
└─ DecisionReadiness
```

---

# 5. 공통 필드 상태

모든 중요 입력은 값만 저장하지 않고 상태·출처·시각을 함께 보존한다.

## 5.1 `DecisionField`

```json
{
  "status": "known",
  "value": 72,
  "source": {
    "type": "derived_metric",
    "reference": "customer-cohort-query-v1"
  },
  "observed_at": "2026-08-17T12:00:00+09:00",
  "verified_at": null,
  "confidence": 0.91,
  "notes": null
}
```

## 5.2 상태

```text
known
unknown
not_applicable
conflicting
stale
restricted
```

의미:

| 상태 | 의미 |
|---|---|
| `known` | 현재 판단에 사용할 수 있음 |
| `unknown` | 값이 없음 |
| `not_applicable` | 해당 사업·전략에 적용되지 않음 |
| `conflicting` | 서로 다른 출처가 충돌 |
| `stale` | 기준 시점보다 오래됨 |
| `restricted` | 법·정책·개인정보 이유로 사용 불가 |

## 5.3 Source Type

```text
user_entered
manual_verified
imported_csv
derived_metric
system_observed
external_api
connector
historical_action
policy_configuration
```

## 5.4 Confidence

`confidence`는 입력값의 품질·완전성 힌트다.

원인 확률이나 성공 확률이 아니다.

---

# 6. Snapshot Metadata

## 필수

```text
contract_version
tenant_id
business_id
location_id(optional)
opportunity_id
snapshot_id
snapshot_at
business_timezone
data_window_start
data_window_end
```

## 권장

```text
generated_by
source_summary
readiness_version
validation_status
limitations
```

## 규칙

- 모든 timestamp는 UTC offset 포함
- business timezone 별도 유지
- 다른 tenant/business의 필드를 섞지 않음
- Snapshot은 생성 시점의 판단 근거로 불변 보존 가능해야 함

---

# 7. Goal Context

## 목적

사업자가 원하는 결과와 허용하지 않는 행동을 정의한다.

## 필드

```text
primary_goal
secondary_goals
priority_horizon
preferred_outcome_metric
risk_tolerance
no_discount_policy
maximum_discount_rate
brand_constraints
manual_only
```

## `primary_goal`

```text
FILL_LOW_DEMAND_SLOTS
REDUCE_CANCELLATION
IMPROVE_REVISIT
INCREASE_COMPLETED_APPOINTMENTS
INCREASE_CONTRIBUTION
IMPROVE_BOOKING_CONVERSION
COLLECT_MISSING_DATA
```

## 예

```json
{
  "primary_goal": "FILL_LOW_DEMAND_SLOTS",
  "no_discount_policy": true,
  "maximum_discount_rate": {
    "status": "not_applicable",
    "value": null
  },
  "manual_only": true
}
```

## 결측 정책

Goal이 없으면:

```text
→ Opportunity type 기반 임시 Goal
→ 사용자 확인 필요
→ 최종 Package status는 DRAFT 또는 NEEDS_DATA
```

---

# 8. Business Constraint Context

## 목적

마케팅보다 운영 제약이 먼저인 상황을 판정한다.

## 필드

```text
business_hours
closed_days
appointment_required
same_day_booking_allowed
minimum_booking_lead_minutes
cancellation_cutoff
service_blackout_periods
staff_shortage_flag
room_or_equipment_constraint
daily_capacity_hint
temporary_constraints
```

## 규칙

- `staff_shortage_flag = true`이면 demand generation 후보에 운영 risk penalty
- 목표 슬롯이 blackout이면 Action 추천 금지
- same-day booking 불가이면 잔여 슬롯 당일 광고 후보 제한
- 운영 제약이 `conflicting`이면 `CAPACITY_OPERATION` 또는 `DATA_COLLECTION` 우선

---

# 9. Economics Context

## 목적

추천 후보의 비용과 경제성을 비교한다.

## 9.1 공통 필드

```text
currency
budget_cap
media_budget_cap
message_cost_cap
partner_cost_cap
staff_time_hourly_cost
maximum_acquisition_cost
minimum_contribution_target
economics_status
```

## 9.2 Offering 단위

```text
offering_id
price_mode
list_price
expected_net_revenue_per_completion
variable_cost_per_completion
benefit_cost_per_completion
incremental_service_cost_per_completion
refund_or_cancellation_cost
```

## `price_mode`

Hospital Adapter:

```text
fixed
insured
variable
unknown
```

## 계산

```text
Contribution per Completion
=
Expected Net Revenue
- Variable Cost
- Benefit Cost
- Incremental Service Cost
```

## 상태

```text
complete
partial
unknown
infeasible
```

## 핵심 규칙

- `unknown` 비용을 0으로 처리하지 않음
- `list_price`만 있으면 revenue-only
- price mode가 `insured` 또는 `variable`이면 정가 기반 과도한 추정 금지
- 기여금액 <= 0이면 paid Strategy는 `infeasible`
- budget cap 없는 유료 실행은 Quality Hard Fail

## 예

```json
{
  "economics_status": "partial",
  "budget_cap": {
    "status": "known",
    "value": {
      "amount": "150000.00",
      "currency": "KRW"
    },
    "source": {
      "type": "user_entered",
      "reference": "decision-context-form"
    }
  },
  "offering_economics": [
    {
      "offering_id": "OFFER_01",
      "price_mode": "fixed",
      "expected_net_revenue_per_completion": {
        "status": "known",
        "value": {
          "amount": "80000.00",
          "currency": "KRW"
        }
      },
      "variable_cost_per_completion": {
        "status": "unknown",
        "value": null
      }
    }
  ]
}
```

---

# 10. Operational Capacity Context

## 목적

실제로 판매 가능한 capacity가 있는지 판단한다.

## 필드

```text
target_weekday
target_start_hour
target_end_hour
slot_capacity_confirmed
available_staff_count
max_concurrent_customers
available_service_minutes
booked_service_minutes
offering_available
eligible_staff_count
room_available
equipment_available
operational_owner
capacity_source
```

## 권장 상세

```text
staff_id를 직접 AI에 전달하지 않고 aggregate count 사용
Offering별 수행 가능 인원
휴게시간
예외 휴무
당일 운영 변경
```

## 규칙

```text
capacity 미상
→ Demand expansion final recommendation 금지
→ CAPACITY_OPERATION / DATA_COLLECTION 후보

offering_available = false
→ 해당 Offering Playbook 제외

eligible_staff_count = 0
→ 실행 불가

slot_capacity_confirmed = true
AND
offering_available = true
→ target slot Playbook 검토 가능
```

## Hospital 제한

- 직원의 개인 민감정보를 Decision Context에 저장하지 않음
- 직원명 대신 집계 또는 내부 key 사용
- 의료행위 적합성 판단은 LOOFIO가 수행하지 않음

---

# 11. Offering Eligibility Context

## 목적

어떤 Offering을 어떤 방식으로 실행안에 사용할 수 있는지 정의한다.

## 필드

```text
offering_id
offering_name
offering_category
offering_type
price_mode
duration_minutes
requires_appointment
active
marketing_enabled
target_slot_available
discount_allowed
maximum_discount_rate
benefit_allowed
policy_tags
prohibited_claim_tags
```

## 상태

```text
eligible
needs_policy_review
not_available
not_marketing_enabled
insufficient_data
```

## 규칙

- `marketing_enabled = false`면 마케팅 Playbook 제외
- `needs_policy_review`면 Package status `NEEDS_POLICY_REVIEW`
- discount forbidden이면 비가격 Playbook만 허용
- duration이 없으면 capacity 정밀 계산 제한
- Offering이 없는 Strategy는 Data Collection 또는 general operation review로 제한

---

# 12. Customer Activation Context

## 목적

재방문·대기 명단·고객 메시지 Playbook의 적용 가능성을 판단한다.

## 사용 가능한 비식별 정보

```text
customer_token_available
completed_visit_history_available
offering_history_available
last_visit_available
revisit_interval_available
eligible_cohort_count
recent_contact_history_available
marketing_consent_status_available
contactable_cohort_count
waitlist_available
```

## 금지 데이터

```text
환자 이름
전화번호 원문
이메일 원문
주민등록번호
진단명
질병·증상
처방
검사 결과
의무기록
상담 원문
```

## 마케팅 동의 상태

```text
verified_allowed
verified_denied
unknown
not_required_for_manual_review
restricted
```

## 규칙

```text
customer token 없음
→ cohort-level reactivation 불가

동의 상태 unknown
→ 실제 고객 연락 Action 불가
→ manual review 또는 consent data collection만 가능

contactable cohort = 0
→ reactivation 제외

recent contact history 없음
→ fatigue guardrail 불완전
→ Quality penalty 또는 NEEDS_DATA
```

## 출력은 aggregate

```text
eligible_cohort_count = 72
contactable_cohort_count = 61
recently_contacted_count = 14
```

개별 token 목록은 Recommendation Package에 포함하지 않는다.

---

# 13. Channel Capability Context

## 목적

온라인·오프라인 실행 가능성과 추적 가능성을 표현한다.

## Channel Type

```text
MANUAL
BOOKING_PAGE
WEBSITE
NAVER_PLACE
KAKAO
SMS
EMAIL
SEARCH_ADS
SOCIAL_ADS
ORGANIC_SOCIAL
FRONT_DESK
STAFF_CALLBACK
WAITLIST
PARTNER_REFERRAL
TRACKED_PRINT
```

## 채널별 필드

```text
channel_type
connection_status
execution_mode
approval_status
tracking_capability
booking_link_available
audience_capability
budget_cap
owner
policy_status
last_verified_at
limitations
```

## `connection_status`

```text
connected
available_manual
not_connected
unavailable
unknown
```

## `execution_mode`

```text
manual
copy_export
approved_connector
automatic
```

현재 MVP에서 `automatic`은 허용하지 않는다.

## `tracking_capability`

```text
UTM
unique_url
booking_source_code
coupon_code
partner_code
QR
action_id
manual_source_tag
none
```

## 규칙

- tracking `none`이면 실행보다 tracking 설정 우선
- owner 없으면 executable Package 불가
- approved connector가 없더라도 manual/copy-export Playbook은 가능
- 채널 연결만으로 Strategy 적합성을 판단하지 않음
- paid channel은 budget cap 필수

---

# 14. Historical Action Context

## 목적

이미 실행했던 행동과 반복 실패를 고려한다.

## 필드

```text
action_id
recommendation_version
strategy_family
playbook_id
channel
target_definition
start_at
end_at
planned_budget
actual_spend
result_source
primary_metric
observed_result
measurement_method
evidence_grade
decision
modification_summary
limitations
```

## 집계

```text
historical_execution_count
acceptance_rate
modification_rate
completion_rate
result_connection_rate
playbook_result_summary
channel_result_summary
```

## 규칙

- 현재 단순 baseline 결과를 causal evidence로 사용하지 않음
- Grade C/D 결과는 historical support로 제한
- 과거 실패가 데이터 실패인지 행동 실패인지 구분
- 같은 고객군 과도한 반복 접촉 방지

---

# 15. External Context Summary

## 목적

Cause와 Measurement limitation을 보조한다.

## Context Type

```text
HOLIDAY
WEATHER
LOCAL_EVENT
FOOTFALL
TRADE_AREA
SEARCH_TREND
```

## 필드

```text
context_type
provider
valid_from
valid_to
geo_scope
normalized_metrics
quality_status
source_reference
limitations
```

## 규칙

- `External Context != Cause`
- provider 실패 시 Opportunity·Detector 실패 금지
- 유효기간이 지나면 stale
- 내부 사업 데이터보다 우선하지 않음
- 첫 버전에서는 Holiday/Weather/Event만 검토

---

# 16. Policy Constraint Context

## 목적

Hospital에서 허용되지 않는 targeting·표현·자동화를 방지한다.

## 필드

```text
domain
policy_review_status
marketing_enabled_offerings
prohibited_targeting
prohibited_claims
allowed_channels
manual_approval_required
legal_review_required
consent_requirement
data_retention_rule
```

## 상태

```text
approved
needs_review
restricted
blocked
unknown
```

## 기본 Hospital 정책

```text
manual approval required
patient clinical targeting prohibited
automatic message/ad execution prohibited
patient PII in AI context prohibited
medical outcome guarantee prohibited
unverified before/after claim prohibited
```

## 규칙

- policy unknown이면 외부 실행 Package 금지
- blocked Offering/claim이 있으면 Playbook 제외
- 사용자 승인만으로 법적 적합성을 자동 보장하지 않음

---

# 17. Measurement Capability Context

## 목적

추천 실행 후 결과를 회수할 수 있는지 판단한다.

## 필드

```text
result_source
baseline_available
customer_level_result_linkage
action_level_tracking
target_slot_result_available
actual_spend_available
cost_data_available
comparison_methods_available
minimum_observation_window
data_delay
```

## Result Source 후보

```text
normalized_completed_appointments
payment_transactions
booking_source_code
coupon_redemption
partner_code
manual_verified_result
connector_delivery_event
```

## 규칙

```text
result_source 없음
→ Quality Hard Fail

baseline 없음
→ Diagnostic 또는 Grade D

action-level tracking 없음
→ Incremental 해석 금지

actual spend 없음
→ Net contribution 금지
```

---

# 18. Assumption Registry

## 목적

명시적으로 확인되지 않은 가정을 숨기지 않는다.

## 필드

```text
assumption_id
statement
status
source
impact_area
validation_method
owner
expires_at
```

## 상태

```text
proposed
user_confirmed
data_supported
rejected
expired
```

## 예

```text
A-001
"화요일 14~16시에 해당 Offering을 실제로 제공할 수 있다"
→ user_confirmed

A-002
"재방문 고객에게 1회 연락이 가능한 동의 상태다"
→ proposed
```

`proposed` 가정에 의존하는 실행안은 Quality penalty 또는 `NEEDS_DATA`가 된다.

---

# 19. Decision Readiness

## D0 — Opportunity Only

보유:

```text
Opportunity
Evidence
Limitations
```

가능:

- Cause 후보 초안
- missing data
- diagnostic question

불가:

- 실행 가능한 Recommendation
- 경제성
- 고객 targeting
- paid channel

## D1 — Diagnostic Ready

추가:

```text
Business goal
Offering
Basic operating constraints
```

가능:

- Cause 우선순위
- Capacity/Data Collection 전략
- 운영 진단 Playbook

불가:

- 완전한 실행 패키지

## D2 — Strategy Ready

추가:

```text
Offering eligibility
Capacity status
Available channels
Policy status
```

가능:

- 전략 후보 비교
- 비고객 접촉 Playbook
- 실행 가능성 판정

제한:

- 고객 cohort activation
- 정확한 economics

## D3 — Experiment Ready

추가:

```text
target population or cohort count
marketing/consent capability
tracking
owner
period
result source
budget status
```

가능:

- Experiment Draft
- Recommendation Package
- Quality validation

## D4 — Economics Ready

추가:

```text
revenue
variable cost
benefit cost
media/message/partner/staff cost
actual spend collection
```

가능:

- contribution estimate
- break-even
- economics-based strategy rank
- 결과 후 net contribution 분석

## Readiness 출력

```json
{
  "level": "D2",
  "version": "decision-readiness-v1",
  "available_capabilities": [
    "cause_analysis",
    "strategy_comparison",
    "operational_playbook"
  ],
  "blocked_capabilities": [
    "customer_reactivation",
    "economics_ranking",
    "experiment_ready_package"
  ],
  "missing_requirements": [
    "marketing_consent_capability",
    "action_level_tracking",
    "result_source"
  ]
}
```

---

# 20. Opportunity별 최소 입력

## LOW_DEMAND_SLOT

### Cause Analysis

```text
target slot
offering
observed weeks
demand index
limitations
business hours
capacity status
```

### Strategy Comparison

```text
goal
offering eligibility
capacity
customer activation capability
channels
policy
budget status
```

### Full Package

```text
owner
period
tracking
result source
experiment comparison
success/stop
economics status
```

## CANCELLATION_HOTSPOT

추가:

```text
cancellation/no-show split
booking lead time
reminder status
reschedule path
waitlist capability
cancellation policy
```

## DORMANT_CUSTOMER

추가:

```text
customer token
revisit interval
eligible cohort
marketing consent capability
recent contact
contact channel
completed revisit result source
```

## SERVICE_DEMAND_GAP

추가:

```text
offering availability
duration
eligible staff
time-slot visibility
price/value presentation
channel-specific offering exposure
```

---

# 21. Missing Data Behavior Matrix

| Missing Input | 금지되는 결과 | 우선 반환 |
|---|---|---|
| Capacity | 수요 확대 final recommendation | Capacity review / data collection |
| Offering eligibility | 해당 Offering 실행 | Policy/availability review |
| Customer token | 재방문 cohort targeting | Non-customer strategy |
| Consent capability | 고객 직접 연락 | Consent data collection / manual review |
| Channel tracking | 실행 효과 측정 | Tracking setup |
| Budget cap | Paid media 실행 | Budget input request |
| Variable cost | Net contribution | Revenue-only / unknown |
| Result source | Final executable package | Measurement setup |
| Owner | Action handoff | Owner assignment |
| Policy review | External execution | NEEDS_POLICY_REVIEW |
| Conflicting data | Cause 확정 | DATA_QUALITY_ARTIFACT |
| Stale context | 현재 근거로 사용 | Refresh request |

---

# 22. Progressive Input UX

처음부터 모든 입력을 요구하지 않는다.

## Onboarding 최소 입력

```text
primary goal
main offerings
business hours
no-discount preference
current channels
budget band(optional)
manual-only preference
```

## Opportunity 발견 시 질문

LOW_DEMAND_SLOT 예:

```text
1. 해당 시간대에 실제 예약 가능한 여유가 있습니까?
2. 해당 Offering을 제공할 직원·공간이 있습니까?
3. 재방문 고객군을 비식별 방식으로 구분할 수 있습니까?
4. 고객 연락 동의 상태를 확인할 수 있습니까?
5. 예약 완료를 Action과 연결할 추적 수단이 있습니까?
6. 실행 비용 상한은 얼마입니까?
7. Offering 1건의 변동원가 또는 최소 허용 수익을 아십니까?
8. 이 실행을 담당할 역할은 누구입니까?
```

## Just-in-time 원칙

질문의 목적과 영향도 함께 표시한다.

예:

> 변동원가를 입력하면 광고보다 재방문 실험이 실제로 경제적인지 비교할 수 있습니다. 입력하지 않아도 분석은 가능하지만 순기여이익은 계산하지 않습니다.

---

# 23. API Contract 후보

현재 API에 additive하게 추가한다.

## Business Decision Context

```text
GET  /api/v1/businesses/{businessId}/decision-context
PUT  /api/v1/businesses/{businessId}/decision-context
```

## Opportunity Snapshot

```text
POST /api/v1/opportunities/{opportunityId}/decision-context/preview
POST /api/v1/opportunities/{opportunityId}/decision-context/snapshots
GET  /api/v1/opportunities/{opportunityId}/decision-context/snapshots
```

## 최초 구현 권장

Persistence 전에 다음 endpoint 하나로 검증한다.

```text
POST /api/v1/opportunities/{opportunityId}/recommendation-packages/preview
```

요청에 Decision Context를 포함하고, 저장·외부 실행 없이 Package 결과를 반환한다.

---

# 24. DB Schema 후보

Persistence가 필요해질 때 검토한다.

```text
business_decision_profiles
business_operational_constraints
business_channel_capabilities
offering_economics
offering_decision_eligibility
customer_activation_capabilities
decision_context_snapshots
decision_context_field_sources
decision_assumptions
```

## 공통 제약

- tenant_id
- business_id
- version
- status
- source/provenance
- observed_at
- updated_at
- audit
- no raw patient PII

## Snapshot

Recommendation Package가 어떤 입력으로 만들어졌는지 재현하기 위해 불변 Snapshot을 우선한다.

---

# 25. Validation Rules

## Time

- ISO-8601 offset
- end >= start
- business timezone 존재

## Money

- Decimal string
- currency `KRW` 초기 지원
- negative reject
- unknown과 0 분리

## Capacity

- nonnegative
- target slot과 일치
- offering availability 필수

## Customer

- aggregate count만 Package에 전달
- raw identifier reject
- consent status 필수

## Channel

- paid channel budget cap
- execution owner
- tracking capability
- approval status

## Policy

- Hospital default manual approval
- clinical targeting reject
- guarantee claim reject

## Provenance

- important known field는 source 필수
- stale/conflict는 Known으로 승격하지 않음

---

# 26. 보안·개인정보

## AI Context에 포함하지 않음

```text
patient name
raw phone
raw email
resident registration number
diagnosis
symptom
prescription
test result
medical record
consultation text
```

## Core 원칙

```text
tenant scope
business scope
tokenized customer identity
aggregate cohort
minimum retention
audited export
```

## Offline Execution

직원용 대상 목록이 필요하면:

- Recommendation Package와 분리
- 짧은 보존기간
- 접근권한
- export audit
- 원문 연락처는 기존 적법한 CRM에서 처리

---

# 27. 첫 LOW_DEMAND_SLOT Context 예

```json
{
  "contract_version": "decision-input-v1",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "opportunity_id": "OPP_01",
  "snapshot_at": "2026-08-17T12:00:00+09:00",
  "business_timezone": "Asia/Seoul",
  "goal": {
    "primary_goal": "FILL_LOW_DEMAND_SLOTS",
    "no_discount_policy": true,
    "manual_only": true
  },
  "operation": {
    "target_weekday": "TUE",
    "target_start_hour": 14,
    "target_end_hour": 16,
    "slot_capacity_confirmed": {
      "status": "known",
      "value": true,
      "source": {
        "type": "manual_verified",
        "reference": "owner-confirmation"
      }
    },
    "offering_available": {
      "status": "known",
      "value": true
    }
  },
  "customer_activation": {
    "customer_token_available": true,
    "eligible_cohort_count": {
      "status": "known",
      "value": 72
    },
    "marketing_consent_status_available": {
      "status": "unknown",
      "value": null
    }
  },
  "channels": [
    {
      "channel_type": "MANUAL",
      "connection_status": "available_manual",
      "execution_mode": "manual",
      "tracking_capability": "action_id",
      "owner": "marketer"
    }
  ],
  "economics": {
    "economics_status": "partial",
    "budget_cap": {
      "status": "known",
      "value": {
        "amount": "120000.00",
        "currency": "KRW"
      }
    },
    "variable_cost_per_completion": {
      "status": "unknown",
      "value": null
    }
  },
  "measurement": {
    "result_source": "normalized_completed_appointments",
    "baseline_available": true,
    "action_level_tracking": true
  }
}
```

예상 Readiness:

```text
D2 Strategy Ready
```

차단:

```text
customer reactivation execution
net contribution estimate
```

부족:

```text
marketing consent capability
variable cost
```

---

# 28. 테스트 시나리오

## Scenario A — D0

입력:

```text
Opportunity only
```

결과:

```text
Cause candidates
Missing requirements
No executable recommendation
```

## Scenario B — Capacity Unknown

결과:

```text
CAPACITY_OPERATION / DATA_COLLECTION 우선
Demand generation final package 금지
```

## Scenario C — Consent Unknown

결과:

```text
Customer activation Playbook 제외
Non-contact strategy만 허용
```

## Scenario D — Tracking None

결과:

```text
Tracking setup Playbook
Quality Hard Fail
```

## Scenario E — Economics Partial

결과:

```text
Revenue-only estimate
No net contribution
```

## Scenario F — Economics Infeasible

결과:

```text
NO_ACTION 또는 비가격 운영 전략
```

## Scenario G — Complete D4

결과:

```text
Strategy comparison
Playbook
Experiment
Quality validation
Contribution estimate
READY_FOR_REVIEW 가능
```

## Scenario H — PII Input

입력:

```text
patient_name
phone
diagnosis
```

결과:

```text
422 validation error
No persistence
Audit-safe error
```

## Scenario I — Cross Tenant

결과:

```text
404 또는 forbidden policy
No existence leak
```

---

# 29. Definition of Done

Decision Input Contract v1 완료조건:

1. 중요 필드에 status/provenance 지원
2. unknown과 0 구분
3. D0~D4 deterministic Readiness
4. Opportunity별 missing requirement
5. capacity/consent/tracking/policy gate
6. Money/time validation
7. Hospital PII rejection
8. tenant/business scope
9. first LOW_DEMAND_SLOT fixture
10. Cause/Strategy/Playbook에서 동일 Contract 사용
11. Snapshot 재현성
12. API 문서와 테스트
13. CURRENT_IMPLEMENTATION_STATUS 갱신

---

# 30. 당장 구현할 최소 subset

첫 vertical slice에서 다음만 구현한다.

```text
Metadata
Goal
Target slot capacity
Offering availability
Eligible revisit cohort count
Consent capability
Manual channel
Tracking capability
Execution owner
Budget cap
Basic offering economics
Result source
Readiness
```

이 subset이 안정된 뒤 다음을 추가한다.

```text
Historical actions
External context
Multiple paid channels
Partner economics
Staff time cost
Advanced policy configuration
```
