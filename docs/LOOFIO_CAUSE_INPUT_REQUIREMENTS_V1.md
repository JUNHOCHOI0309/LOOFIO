---
title: "LOOFIO Cause Input Requirements v1"
version: "1.0"
date: "2026-08-17"
status: "Cause별 Decision Input 매핑표"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
depends_on:
  - "LOOFIO_DECISION_INPUT_CONTRACT_V1.md"
  - "LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md"
---

# LOOFIO Cause Input Requirements v1

## 1. 문서 목적

이 문서는 각 Cause Candidate가 어떤 Decision Input을 요구하는지 `Required / Optional / Blocking`으로 연결한다.

표기:

```text
R
→ Candidate 평가와 점수에 필수

O
→ 없어도 평가 가능하지만 근거·완전성 향상

B
→ Candidate 생성에는 필수가 아니나 downstream Strategy/Playbook/Final Package 실행 차단

C
→ 조건부 Required. 해당 데이터 경로가 존재하거나 해당 Candidate를 활성화할 때 R로 승격
```

`C`는 구현 편의를 위한 보조 표기이며, 런타임에서는 조건이 충족되면 `R` 또는 `not_applicable`로 해석한다.

---

# 2. 공통 Required 입력

모든 Cause Analysis Run:

| Field Path | 등급 | 누락 동작 |
|---|:---:|---|
| `metadata.contract_version` | R | `INVALID_INPUT` |
| `metadata.tenant_id` | R | `INVALID_INPUT` |
| `metadata.business_id` | R | `INVALID_INPUT` |
| `metadata.opportunity_id` | R | `INVALID_INPUT` |
| `metadata.snapshot_at` | R | `INVALID_INPUT` |
| `metadata.business_timezone` | R | `TIMEZONE_REQUIRED` |
| `metadata.data_window_start` | R | `NEEDS_DATA` |
| `metadata.data_window_end` | R | `NEEDS_DATA` |
| `opportunity.type` | R | unsupported type |
| `opportunity.detector.version` | R | `NEEDS_DATA` |
| `opportunity.observation` | R | `NEEDS_DATA` |
| `opportunity.limitations` | R | 빈 배열 허용, field 자체는 필수 |
| `opportunity.segment.weekday` | R for slot causes | `NEEDS_DATA` |
| `opportunity.segment.start_hour` | R for slot causes | `NEEDS_DATA` |
| `opportunity.segment.end_hour` | R for slot causes | `NEEDS_DATA` |

---

# 3. Critical Data Quality Global Blockers

다음 상태는 사업 원인 Candidate를 우선순위화하기 전에 해결한다.

| Field / Condition | 결과 |
|---|---|
| tenant/business source conflict | `INVALID_INPUT` 또는 404 |
| invalid data window | `INVALID_INPUT` |
| timezone conflict | `BLOCKED_BY_DATA_QUALITY` |
| unsupported status mapping | `BLOCKED_BY_DATA_QUALITY` |
| Opportunity evidence source unreproducible | `BLOCKED_BY_DATA_QUALITY` |
| `data_quality.validation_status = conflicting` | `BLOCKED_BY_DATA_QUALITY` |
| source lineage unavailable + evidence ref 없음 | `BLOCKED_BY_DATA_QUALITY` |
| stale input beyond configured threshold | run `NEEDS_DATA` 또는 refresh |

---

# 4. DATA_QUALITY_ARTIFACT

## 4.1 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| `data_quality.import_status` | R | import 처리 상태 |
| `data_quality.validation_status` | R | validation 요약 |
| `data_quality.source_lineage_available` | R | Opportunity 근거 재현 가능 여부 |
| `data_quality.data_freshness_at` | R | 최신성 |
| `opportunity.detector.version` | R | 계산 규칙 버전 |
| `metadata.data_window_start/end` | R | 분석 범위 |

## 4.2 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| `data_quality.mapping_profile_version` | O | mapping drift 확인 |
| `data_quality.valid_row_count` | O | 표본 확인 |
| `data_quality.rejected_row_count` | O | 누락 영향 |
| `data_quality.duplicate_row_count` | O | 중복 영향 |
| `data_quality.unknown_status_count` | O | status 품질 |
| `data_quality.missing_required_field_count` | O | 필수 누락 |
| `data_quality.timezone_validation_status` | O | 시간대 이상 |
| `data_quality.offering_resolution_rate` | O | Offering 매핑 |
| `data_quality.customer_token_coverage_rate` | O | Retention 분석 준비도 |
| `data_quality.payment_coverage_rate` | O | Revenue Estimate 준비도 |

## 4.3 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| critical timezone conflict | B | 모든 slot Strategy |
| required status mapping unresolved | B | 모든 business Cause rank |
| source lineage unavailable | B | Final Package |
| data freshness stale | B | 현재 실행 추천 |
| offering resolution conflict | B | Offering-specific Playbook |

## 4.4 Diagnostic

```text
최근 import에서 제외된 행이 있습니까?
외부 상태값이 내부 상태로 모두 확인됐습니까?
예약 시각 timezone이 사업장 timezone과 일치합니까?
Offering 이름이 일관되게 매핑됐습니까?
```

---

# 5. CAPACITY_OR_OPERATION_CONSTRAINT

## 5.1 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| `operation.target_weekday` | R | Opportunity segment와 일치 |
| `operation.target_start_hour` | R | 목표 시작 |
| `operation.target_end_hour` | R | 목표 종료 |
| `business_constraints.business_hours` | R | 실제 영업 여부 |
| `operation.slot_capacity_confirmed` | R | capacity 확인 여부 |
| `operation.offering_available` | R | Offering 제공 가능 여부 |

## 5.2 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| `operation.available_staff_count` | O | 인력 제약 |
| `operation.eligible_staff_count` | O | Offering 수행 인원 |
| `operation.max_concurrent_customers` | O | 동시 capacity |
| `operation.available_service_minutes` | O | 시간 capacity |
| `operation.booked_service_minutes` | O | 사용량 |
| `operation.room_available` | O | 공간 제약 |
| `operation.equipment_available` | O | 장비 제약 |
| `business_constraints.same_day_booking_allowed` | O | 당일 Action |
| `business_constraints.minimum_booking_lead_minutes` | O | 실행 timing |
| `business_constraints.temporary_constraints` | O | 예외 상황 |
| `business_constraints.staff_shortage_flag` | O | risk |

## 5.3 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| `slot_capacity_confirmed != known true` | B | demand expansion |
| `offering_available != known true` | B | Offering Playbook |
| `eligible_staff_count = 0` | B | 실행 |
| blackout overlap | B | 실행 |
| `policy.policy_review_status` unknown | B | external Action |
| `operation.operational_owner` unknown | B | Action handoff |

## 5.4 Supporting / Contradicting

Supporting:

```text
capacity false/zero
staff shortage
room/equipment unavailable
booking closed
blackout
```

Contradicting:

```text
capacity confirmed
staff/room/equipment sufficient
동일 조건의 다른 주에서 정상 예약
```

---

# 6. OFFER_SLOT_MISMATCH

## 6.1 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| `offering.offering_id` | R | 분석 대상 |
| `offering.offering_name` | R | 표시 |
| `offering.target_slot_available` | R | 목표 슬롯 제공 여부 |
| `opportunity.segment.weekday/start_hour/end_hour` | R | 슬롯 |
| `opportunity.observation`의 Offering-slot 비교값 | C | ServiceDemand evidence가 있을 때 R |

## 6.2 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| `offering.offering_category` | O | 유사 Offering 비교 |
| `offering.duration_minutes` | O | 슬롯 적합성 |
| `offering.price_mode` | O | 시간대·가격대 해석 |
| `offering.requires_appointment` | O | 예약 경로 |
| `operation.eligible_staff_count` | O | 인력 적합성 |
| Historical Offering-slot distribution | O | 반복 패턴 |
| Similar Offering slot distribution | O | 비교 |

## 6.3 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| `offering.status = needs_policy_review` | B | marketing Playbook |
| `marketing_enabled = false` | B | promotion |
| `target_slot_available != true` | B | target slot 실행 |
| duration unknown + capacity 계산 필요 | B | capacity-based Package |
| eligible staff 0 | B | 실행 |

## 6.4 Supporting / Contradicting

Supporting:

```text
Offering만 목표 슬롯에서 낮음
다른 Offering은 정상
duration/직원 배치 불일치
```

Contradicting:

```text
모든 Offering이 함께 낮음
Offering availability 정상
동일 Offering이 유사 주에서 정상
```

---

# 7. RETENTION_GAP

## 7.1 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| `customer_activation.customer_token_available` | R | 비식별 고객 연결 |
| `completed_visit_history_available` | R | 방문 이력 |
| `revisit_interval_available` | R | 재방문 기준 |
| `eligible_cohort_count` | R | aggregate cohort |
| `offering.offering_id` 또는 cohort scope | R | 대상 범위 |

## 7.2 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| `offering_history_available` | O | Offering별 cohort |
| `last_visit_available` | O | 지연 정도 |
| `recent_contact_history_available` | O | fatigue |
| `contactable_cohort_count` | O | 실제 가능 규모 |
| `waitlist_available` | O | 대기 명단 |
| Historical reactivation actions | O | 반복·성과 |
| `goal.primary_goal` | O | 우선순위 |

## 7.3 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| consent capability unknown/restricted | B | 고객 직접 연락 |
| contactable cohort = 0 | B | reactivation |
| recent contact history unknown | B/O | 반복 연락 Quality |
| contact channel unavailable | B | 실행 |
| action-level tracking 없음 | B | 실험 Package |
| result source 없음 | B | Final Package |
| individual token export requested | B | privacy reject |

## 7.4 Supporting / Contradicting

Supporting:

```text
eligible cohort > 0
expected revisit overdue
recent action 없음
목표 Offering history 존재
```

Contradicting:

```text
eligible cohort = 0
대부분 최근 방문
최근 동일 cohort Action 실행
재방문형 Offering이 아님
```

---

# 8. DISCOVERABILITY_GAP

## 8.1 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| `channels`에 발견 경로 1개 이상 | R | booking/web/place/search |
| target slot 또는 Offering visibility status | R | 노출 확인 |
| `measurement.result_source` 또는 booking source | R | 유입 결과 연결 |

## 8.2 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| booking link available | O | 경로 존재 |
| map/profile impressions | O | 지도 노출 |
| search impressions | O | 검색 노출 |
| website/landing visits | O | 웹 유입 |
| channel-level booking source | O | 유입→예약 |
| historical exposure action | O | 과거 실행 |
| local search trend | O | 수요 proxy |

## 8.3 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| tracking `none` | B | 실행 Package |
| booking link/route unavailable | B | digital conversion Action |
| paid budget cap 없음 | B | paid acquisition |
| channel owner 없음 | B | Action |
| policy unknown | B | external exposure |
| target slot not actually available | B | slot promotion |

## 8.4 Supporting / Contradicting

Supporting:

```text
slot/Offering visibility 없음
impression 낮음
검색 proxy는 있으나 booking 낮음
```

Contradicting:

```text
노출 충분
funnel conversion 낮음
지역 수요 proxy 낮음
capacity 닫힘
```

---

# 9. DEMAND_DEFICIT

## 9.1 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| `observation.observed_weeks` | R | 반복성 |
| `observation.demand_index` | R | 상대 수요 |
| `observation.average_appointments_per_week` | R | 실제 수준 |
| `observation.comparison_median_per_week` | R | 비교 기준 |
| target segment | R | 요일·시간대 |

## 9.2 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| longer historical window | O | 계절 반복 |
| Offering-wide pattern | O | 전반 수요 |
| holiday | O | 일정 보조 |
| weather | O | 외부 보조 |
| local event | O | 지역 보조 |
| search trend | O | 수요 proxy |
| footfall | O | 생활 수요 |
| trade area comparison | O | 지역 비교 |

## 9.3 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| data quality conflict | B | demand conclusion |
| capacity unknown/closed | B | demand conclusion |
| broader demand proxy 없음 | B/O | paid acquisition justification |
| observed weeks below detector threshold | B | current cause rank |
| external context stale | B/O | context-based explanation |

## 9.4 Supporting / Contradicting

Supporting:

```text
장기 반복
여러 Offering 동시 저하
외부 수요 proxy 저하
```

Contradicting:

```text
검색/유동 정상
노출·conversion 문제 존재
capacity 닫힘
데이터 오류
```

---

# 10. CONVERSION_FRICTION

## 10.1 Conditional Activation

다음 중 하나 이상이 `known`일 때 Candidate를 활성화한다.

```text
booking page visits
booking starts
booking completions
inquiries
inquiry-to-booking
booking errors
```

## 10.2 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| exposure/visit count | C | funnel 시작 |
| booking start or inquiry count | C | 중간 단계 |
| completed booking count | C | 결과 |
| period/segment alignment | R | Opportunity와 동일 범위 |

## 10.3 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| page error rate | O | 기술 마찰 |
| slot selection failure | O | 재고 노출 |
| CTA click | O | 단계 |
| device/source split | O | 세부 진단 |
| structured inquiry category | O | 문의 마찰 |

## 10.4 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| funnel tracking 없음 | B | conversion Strategy |
| booking path owner 없음 | B | 개선 Action |
| target slot unavailable | B | conversion test |
| result source 없음 | B | Experiment |

---

# 11. CHANNEL_MISMATCH

## 11.1 Conditional Activation

```text
channel-level exposure 또는 booking/result attribution 존재
```

## 11.2 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| channel type | C | 비교 단위 |
| exposure/reach | C | 도달 |
| completed booking/result | C | 결과 |
| attribution/tracking | C | 연결 |

## 11.3 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| audience capability | O | 대상 적합성 |
| channel cost | O | 경제성 |
| time-slot delivery | O | 시간 적합성 |
| historical channel result | O | 과거 비교 |
| partner/source code | O | 오프라인 비교 |

## 11.4 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| attribution 없음 | B | channel rank |
| budget cap 없음 | B | paid channel |
| owner 없음 | B | Action |
| policy unknown | B | external execution |

---

# 12. VALUE_OR_PRICE_FRICTION

## 12.1 Conditional Activation

다음 중 하나가 존재할 때 활성화한다.

```text
structured price/value inquiry
offer exposure and conversion
historical benefit test
price mode comparison
```

## 12.2 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| offering price mode | C | 가격 해석 |
| structured value/price signal | C | 근거 |
| outcome conversion | C | 결과 |

## 12.3 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| expected net revenue | O | 경제성 |
| variable cost | O | 기여가치 |
| benefit cost | O | 혜택 비용 |
| historical offer test | O | 근거 |
| value explanation availability | O | 정보 마찰 |

## 12.4 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| economics unknown | B | discount/benefit rank |
| discount policy forbidden | B | 할인 |
| policy review unknown | B | 의료 마케팅 |
| clinical/consultation raw text 필요 | B | 분석 자체 금지 |
| result source 없음 | B | 실험 |

---

# 13. CANCELLATION_LEAKAGE

## 13.1 Conditional Activation

```text
related CANCELLATION_HOTSPOT
또는
동일 segment의 disruption evidence
```

## 13.2 Required

| Field Path | 등급 | 설명 |
|---|:---:|---|
| appointment_count | C | 표본 |
| cancelled_count | C | 취소 |
| no_show_count | C | 노쇼 |
| disruption_rate | C | 이탈 |
| baseline_disruption_rate | C | 비교 |
| segment alignment | R | 동일 슬롯/Offering |

## 13.3 Optional

| Field Path | 등급 | 활용 |
|---|:---:|---|
| booked_at | O | lead time |
| cancellation timestamp | O | 취소 시점 |
| reminder status | O | 운영 |
| reschedule path | O | 회수 |
| waitlist capability | O | capacity 회수 |
| cancellation policy | O | 제약 |

## 13.4 Blocking

| Field / Condition | 등급 | 차단 대상 |
|---|:---:|---|
| reminder/policy unknown | B/O | 구체적 개선 Action |
| waitlist tracking 없음 | B | 회수 Experiment |
| result source 없음 | B | 측정 |
| customer contact consent unknown | B | reminder 연락 |

---

# 14. Diagnostic Question 우선순위 Matrix

| Priority | 질문 대상 | 예 |
|---:|---|---|
| 1 | Critical data quality | timezone·status mapping·lineage |
| 2 | Capacity / availability | 실제 판매 가능한 슬롯인가 |
| 3 | Offering fit | 해당 Offering을 제공할 수 있는가 |
| 4 | Policy / consent | 고객 접촉·마케팅 가능 여부 |
| 5 | Tracking / result | 결과 연결 수단이 있는가 |
| 6 | Economics | 비용·기여금액을 아는가 |
| 7 | Channel/funnel | 발견·예약 경로 데이터가 있는가 |
| 8 | External context | 날씨·행사·유동 정보가 있는가 |

---

# 15. LOW_DEMAND_SLOT 최소 Context Matrix

첫 vertical slice에서 구현할 최소 필드:

| Field | 등급 | 사용 Cause |
|---|:---:|---|
| Opportunity observation/segment | R | 전체 |
| Data window/detector version | R | 전체 |
| Data quality validation/freshness | R | DATA_QUALITY |
| Business hours | R | CAPACITY |
| Slot capacity confirmed | R | CAPACITY |
| Offering available | R | CAPACITY, OFFER_SLOT |
| Offering id/name | R | OFFER_SLOT, RETENTION |
| Customer token capability | R | RETENTION |
| Eligible cohort count | R | RETENTION |
| Consent capability | B | RETENTION Strategy |
| Manual channel | B | Action |
| Tracking capability | B | Experiment |
| Execution owner | B | Action |
| Result source | B | Package |
| Budget status | B for paid | Economics |
| Variable cost | O/B | Net contribution |

---

# 16. 런타임 처리 규칙

```text
1. Opportunity common fields 검증
2. Critical data quality 평가
3. Core Candidate seed
4. Conditional Candidate activation
5. 각 Candidate의 R 평가
6. R 충족 시 Evidence/Contradiction mapping
7. O로 completeness 보정
8. B를 downstream_blockers에 기록
9. score 계산
10. diagnostic question 생성
11. deterministic sort
12. Strategy handoff
```

정렬:

```text
status priority
→ REVIEWABLE
→ NEEDS_DATA
→ DEPRIORITIZED
→ NOT_APPLICABLE
→ BLOCKED

그 안에서
→ review_priority_score desc
→ taxonomy stable order
```

---

# 17. 구현 검증 Checklist

## Contract

- [ ] 모든 field path가 Decision Input Contract에 존재하거나 additive amendment로 명시됨
- [ ] R/O/B/C 의미가 코드 enum과 일치
- [ ] unknown과 0 분리
- [ ] stale/conflicting/restricted 처리

## Privacy

- [ ] patient name 없음
- [ ] raw phone/email 없음
- [ ] diagnosis/clinical data 없음
- [ ] individual customer token 출력 없음

## Determinism

- [ ] same input hash → same Candidate order
- [ ] same score version
- [ ] AI 미사용
- [ ] tie-break 고정

## Downstream

- [ ] Blocking이 Strategy/Package에 전달
- [ ] Cause가 Strategy를 선택하지 않음
- [ ] Quality Gate가 blocker를 우회하지 않음

---

# 18. 다음 확장

이 매핑 확정 후 Strategy Engine에서 다음을 연결한다.

```text
Cause
→ Strategy Family
→ Required Decision Readiness
→ Economics requirement
→ Playbook candidates
→ Exclusion reasons
```

예:

```text
RETENTION_GAP
→ RETENTION_REACTIVATION
→ D3 이상
→ consent + tracking + result source
→ PB-01 / PB-06

CAPACITY_OR_OPERATION_CONSTRAINT
→ CAPACITY_OPERATION
→ D1 이상
→ paid economics 불필요
→ PB-11

DATA_QUALITY_ARTIFACT
→ DATA_COLLECTION
→ D0
→ PB-10
```
