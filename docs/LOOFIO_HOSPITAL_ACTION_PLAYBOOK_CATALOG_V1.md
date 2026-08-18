---
title: "LOOFIO Hospital Action Playbook Catalog v1"
version: "1.0"
date: "2026-08-17"
status: "초기 Hospital Appointment Playbook 카탈로그"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
depends_on:
  - "LOOFIO_ACTION_PLAYBOOK_V1.md"
  - "LOOFIO_STRATEGY_ENGINE_V1.md"
  - "LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md"
---

# LOOFIO Hospital Action Playbook Catalog v1

## 1. 문서 목적

이 문서는 Hospital Appointment MVP에서 사용할 초기 Playbook의 정식 ID, 적용 조건, 실행 단계, 추적·경제성·실험 계약을 정의한다.

현재 모든 Playbook의 lifecycle은 다음이다.

```text
DRAFT
```

이 문서는 설계 완료를 의미할 뿐, 내부 검증·Pilot·Active 상태를 의미하지 않는다.

---

# 2. 숫자형 별칭 정리

이전 기획의 숫자형 별칭은 다음 정식 ID로 연결한다.

| Legacy alias | Canonical playbook ID |
|---|---|
| `PB-01` | `PB_LOW_DEMAND_REVISIT_COHORT_V1` |
| `PB-02` | `PB_WAITLIST_RECOVERY_V1` |
| `PB-03` | `PB_CANCELLATION_FLOW_REVIEW_V1` |
| `PB-04` | `PB_SEARCH_INTENT_SLOT_CAPTURE_V1` |
| `PB-05` | `PB_BOOKING_FUNNEL_FRICTION_V1` |
| `PB-06` | `PB_FRONT_DESK_REBOOKING_V1` |
| `PB-07` | `PB_TRACKED_LOCAL_PARTNERSHIP_V1` |
| `PB-08` | `PB_NON_DISCOUNT_VALUE_ADD_V1` |
| `PB-09` | `PB_OFFERING_SLOT_REALLOCATION_V1` |
| `PB-10` | `PB_LOW_DEMAND_DATA_AUDIT_V1` |

숫자형 별칭은 신규 구현 key로 사용하지 않는다.

---

# 3. Registry Summary

## 3.1 Core Detailed v1

| ID | Strategy | Class | Primary scope | Minimum readiness | Status |
|---|---|---|---|---:|---|
| `PB_LOW_DEMAND_DATA_AUDIT_V1` | DATA_COLLECTION | DIAGNOSTIC | 데이터 품질 | D0 | DRAFT |
| `PB_LOW_DEMAND_TRACKING_SETUP_V1` | DATA_COLLECTION | DIAGNOSTIC | 추적·결과 연결 | D1 | DRAFT |
| `PB_LOW_DEMAND_CAPACITY_REVIEW_V1` | CAPACITY_OPERATION | OPERATIONAL | 목표 슬롯 capacity | D1 | DRAFT |
| `PB_OFFERING_SLOT_REALLOCATION_V1` | CAPACITY_OPERATION / OFFER_PACKAGING | OPERATIONAL | Offering-시간 적합성 | D2 | DRAFT |
| `PB_BOOKING_AVAILABILITY_AUDIT_V1` | CAPACITY_OPERATION | DIAGNOSTIC | 예약 노출·가용 상태 | D1 | DRAFT |
| `PB_LOW_DEMAND_REVISIT_COHORT_V1` | RETENTION_REACTIVATION | EXECUTION | 재방문 cohort | D3 | DRAFT |
| `PB_FRONT_DESK_REBOOKING_V1` | RETENTION_REACTIVATION | EXECUTION | 현장 다음 예약 | D2 | DRAFT |
| `PB_BOOKING_PATH_VISIBILITY_V1` | DISCOVERABILITY | OPERATIONAL | owned booking path | D2 | DRAFT |
| `PB_BOOKING_FUNNEL_FRICTION_V1` | CONVERSION | OPERATIONAL | 예약 funnel | D2 | DRAFT |
| `PB_NON_DISCOUNT_VALUE_ADD_V1` | OFFER_PACKAGING | EXECUTION | 비가격 부가가치 | D3~D4 | DRAFT |
| `PB_TRACKED_LOCAL_PARTNERSHIP_V1` | PARTNERSHIP_REFERRAL | EXECUTION | 추적 제휴 | D4 | DRAFT |
| `PB_NO_ACTION_MONITORING_V1` | NO_ACTION | HOLD | 실행 보류 | D0 | DRAFT |

## 3.2 Expansion Index

| ID | Strategy | 상세화 우선순위 | 상세화를 미룬 이유 |
|---|---|---:|---|
| `PB_STAFF_CALLBACK_REVISIT_V1` | RETENTION_REACTIVATION | P1 | 고객 접촉·동의·운영 부하 세부 필요 |
| `PB_SEARCH_INTENT_SLOT_CAPTURE_V1` | DISCOVERABILITY | P1 | 검색 데이터·정책·paid/organic 경계 필요 |
| `PB_MAP_PROFILE_OFFERING_AUDIT_V1` | DISCOVERABILITY | P1 | 외부 프로필 필드·검증 절차 필요 |
| `PB_DEEP_LINK_SLOT_TEST_V1` | CONVERSION | P1 | 예약 시스템별 딥링크 계약 필요 |
| `PB_TIME_SLOT_OFFER_BUNDLE_V1` | OFFER_PACKAGING | P1 | Offering·원가·정책 조합 필요 |
| `PB_VALUE_EXPLANATION_TEST_V1` | OFFER_PACKAGING | P1 | 표현 정책·funnel event 필요 |
| `PB_CHANNEL_SOURCE_REALLOCATION_V1` | DISCOVERABILITY | P2 | 채널별 attribution 필요 |
| `PB_CONTROLLED_SEARCH_ACQUISITION_V1` | ACQUISITION | P2 | D4 경제성·budget·policy·conversion 필요 |
| `PB_CANCELLATION_FLOW_REVIEW_V1` | CANCELLATION_RECOVERY | P1 | Cancellation Opportunity vertical slice 필요 |
| `PB_WAITLIST_RECOVERY_V1` | CANCELLATION_RECOVERY | P1 | waitlist domain contract 필요 |
| `PB_RESCHEDULE_PATH_V1` | CANCELLATION_RECOVERY | P1 | 변경·재예약 event 필요 |

Expansion ID는 Strategy 문서와의 참조 무결성을 위해 등록하되, v1 Core 구현 범위에는 포함하지 않는다.

---

# 4. 공통 Hospital Policy

모든 Core Playbook:

```text
HOSPITAL_MANUAL_APPROVAL_REQUIRED
NO_AUTOMATIC_EXTERNAL_EXECUTION
NO_CLINICAL_TARGETING
NO_PATIENT_PII_IN_PACKAGE
NO_MEDICAL_OUTCOME_GUARANTEE
NO_UNVERIFIED_BEFORE_AFTER_CLAIM
TRACKING_REQUIRED_FOR_EXECUTION
RESULT_SOURCE_REQUIRED_FOR_EXECUTION
```

고객 직접 연락 Playbook 추가 태그:

```text
CONSENT_REQUIRED_FOR_DIRECT_CONTACT
```

비용·혜택 Playbook 추가 태그:

```text
BUDGET_CAP_REQUIRED_FOR_PAID_ACTION
ECONOMICS_REQUIRED_FOR_DISCOUNT_OR_BENEFIT
```

---

# 5. PB_LOW_DEMAND_DATA_AUDIT_V1

## Identity

```text
playbook_code
→ PB_LOW_DEMAND_DATA_AUDIT

version
→ 1.0

strategy
→ DATA_COLLECTION

class
→ DIAGNOSTIC

legacy aliases
→ PB-10
```

## 목적

저수요 현상이 실제 사업 패턴인지, import·mapping·timezone·status·Offering resolution 문제인지 확인한다.

## 적용

```text
Opportunity
→ LOW_DEMAND_SLOT

Cause
→ DATA_QUALITY_ARTIFACT

Readiness
→ D0
```

## Required

- Opportunity evidence reference
- data window
- detector version
- import/validation status
- source lineage availability
- data freshness
- issue owner
- review deadline

## Preconditions

- 현재 데이터 source를 다시 확인할 수 있음
- critical PII를 export하지 않고 aggregate 품질 정보를 볼 수 있음

## Contraindications

- source system을 더 이상 접근할 수 없고 검증도 불가능
- tenant/business source가 혼합되어 복구 불가능
- 검토 과정이 raw patient data 추출을 요구

이 경우 `PB_NO_ACTION_MONITORING_V1` 또는 별도 데이터 재구축 결정으로 전환한다.

## 실행 단계

1. Opportunity의 data window·detector version·evidence source를 기록한다.
2. import validation 결과와 제외·중복·unknown status를 확인한다.
3. timezone과 business timezone의 일치 여부를 확인한다.
4. Offering mapping과 source record idempotency를 확인한다.
5. 필요한 correction을 적용하거나 correction request를 기록한다.
6. 동일 data window에서 import·Metric·Opportunity를 다시 계산한다.
7. 수정 전후 Opportunity의 재현 여부를 비교한다.

## 온라인·오프라인

온라인:

```text
관리 화면 validation summary
mapping profile 검토
재import
```

오프라인:

```text
병원 운영 담당자와 source system 상태값 확인
```

## Tracking

```text
audit_review_id
mapping_profile_version
import_job_id
opportunity_regeneration_id
```

## Economics

```text
status
→ not_applicable

회수 가능
→ 직원 검토 시간
```

직원 시간은 운영 부담 지표이며 매출 효과로 표시하지 않는다.

## Experiment Template

```text
EXP_DATA_QUALITY_DIAGNOSTIC_V1
```

Primary Metric:

```text
critical_data_quality_issues_resolved
```

Secondary:

```text
rejected_row_rate
unknown_status_rate
offering_resolution_rate
opportunity_reproducibility
```

Evidence Grade:

```text
D
```

## 성공

- critical issue가 resolved 또는 명확한 not-applicable로 판정
- Opportunity source가 재현됨
- 후속 Cause/Strategy를 다시 실행할 수 있음

## 중단

- source 접근 불가
- patient PII export 필요
- tenant/business 혼합 문제
- correction 후에도 evidence 재현 불가

## Output Artifacts

```text
data_quality_review
mapping_correction_summary
opportunity_reproduction_result
```

---

# 6. PB_LOW_DEMAND_TRACKING_SETUP_V1

## 목적

실행한 Action과 완료 예약·비용·채널 source를 연결할 최소 추적 구조를 만든다.

## 적용

```text
Strategy
→ DATA_COLLECTION

Blocker
→ tracking missing / result source missing

Readiness
→ D1
```

## Required

- 실행 예정 채널
- result source 후보
- tracking owner
- test event 가능 여부
- business/location scope

## Preconditions

- 최소 하나의 tracking method를 설정 가능
- source system에 test event 또는 manual tagging 가능

## Contraindications

- 추적값이 환자 PII를 포함
- 다른 tenant와 코드를 공유
- 결과 source를 검증할 수 없음

## 실행 단계

1. Action 단위 tracking type을 선택한다.
2. `action_id`, source code, UTM, QR, partner code 중 값을 만든다.
3. booking/result source에 해당 값을 전달하는 경로를 설정한다.
4. test event를 실행한다.
5. test event가 동일 business와 Action으로 연결되는지 확인한다.
6. 검증 결과와 limitations를 기록한다.

## Tracking

이 Playbook 자체의 추적:

```text
tracking_setup_id
test_event_id
verification_status
```

## Economics

```text
setup staff time
tracking tool cost(optional)
```

## Experiment Template

```text
EXP_TRACKING_VERIFICATION_V1
```

Primary Metric:

```text
verified_action_result_linkage
```

성공:

```text
test event 1건 이상
AND
정확한 tenant/business/action 연결
```

중단:

```text
cross-tenant collision
PII exposure
result source unsupported
```

Output:

```text
tracking_configuration
tracking_test_result
result_source_contract
```

---

# 7. PB_LOW_DEMAND_CAPACITY_REVIEW_V1

## 목적

목표 슬롯이 실제로 판매 가능한 capacity인지 확인하고, 마케팅보다 운영 조정이 먼저인지 판단한다.

## 적용

```text
Strategy
→ CAPACITY_OPERATION

Cause
→ CAPACITY_OR_OPERATION_CONSTRAINT

Readiness
→ D1
```

## Required

- target weekday/start/end
- business hours
- capacity state
- Offering availability
- operational owner

## Optional

- available staff
- eligible staff
- room/equipment
- available/booked service minutes
- same-day booking policy

## Preconditions

- 목표 슬롯과 Offering을 식별할 수 있음
- 운영 담당자가 확인 가능

## Contraindications

- 목표 슬롯이 의도적으로 닫혀 있고 변경 계획 없음
- 의료행위 적합성 판단을 LOOFIO에 요구
- staff personal sensitive data 필요

## 실행 단계

1. 목표 슬롯이 영업시간과 일치하는지 확인한다.
2. 해당 Offering의 직원·공간·장비 가용성을 aggregate로 확인한다.
3. 예약 페이지와 운영 스케줄의 가용 상태가 일치하는지 확인한다.
4. 실제 판매 가능 capacity를 `known true/false/unknown`으로 기록한다.
5. false이면 원인과 변경 가능성을 기록한다.
6. true이면 수요 관련 Strategy를 다시 평가한다.

## 채널

```text
오프라인 운영 검토
예약 관리 화면
```

고객 대상 채널은 사용하지 않는다.

## Economics

```text
status
→ partial / not_applicable

optional
→ staff schedule cost
→ unused capacity estimate
```

unused capacity estimate를 실제 손실로 표시하지 않는다.

## Experiment Template

```text
EXP_CAPACITY_DIAGNOSTIC_V1
```

Primary:

```text
sellable_slot_status_verified
```

Secondary:

```text
booking_availability_mismatch_count
eligible_staff_count
available_service_minutes
```

Evidence Grade:

```text
D
```

성공:

- capacity state와 source가 known
- 수요 확대 가능/불가가 명확
- 다음 Strategy blocker 해소

중단:

- 운영 source 충돌
- Offering eligibility 미확인
- policy review 필요

---

# 8. PB_OFFERING_SLOT_REALLOCATION_V1

## 목적

목표 시간대에 Offering·소요시간·직원 배치·예약 노출 우선순위를 조정해 슬롯 적합성을 실험한다.

## 적용

```text
Strategy
→ CAPACITY_OPERATION / OFFER_PACKAGING

Cause
→ OFFER_SLOT_MISMATCH

Readiness
→ D2
```

## Required

- target slot
- Offering ID/name
- target slot availability
- Offering-slot evidence
- capacity confirmed
- operational owner
- result source

## Preconditions

- 최소 2개 비교 가능한 Offering 또는 current/default configuration 존재
- 가격·혜택 변경 없이도 우선순위 조정 가능

## Contraindications

- Offering policy status blocked
- eligible staff 0
- target slot unavailable
- 결과를 Offering별로 분리할 수 없음

## 실행 단계

1. 목표 슬롯의 Offering별 예약 비중과 완료 건수를 확인한다.
2. 해당 시간대에 실제 제공 가능한 Offering을 분리한다.
3. 변경 후보를 1개 또는 제한된 수로 선택한다.
4. 예약 페이지·직원 안내·표시 우선순위를 변경한다.
5. 한 번에 가격·채널·Offering을 동시에 바꾸지 않는다.
6. treatment/comparison 기간을 번갈아 운영한다.
7. 완료 예약과 다른 Offering의 displacement를 함께 측정한다.

## 채널

온라인:

```text
booking page ordering
Offering visibility
```

오프라인:

```text
front-desk 안내 우선순위
직원 운영표
```

## Economics

- 기본은 비유료 운영 실험
- 가격 변경 시 별도 `PB_TIME_SLOT_OFFER_BUNDLE_V1` 또는 `PB_NON_DISCOUNT_VALUE_ADD_V1` 필요
- contribution 정보가 있으면 slot-level contribution을 secondary로 사용

## Experiment Template

```text
EXP_SLOT_REALLOCATION_ALTERNATING_V1
```

권장 방식:

```text
Alternating Time Window
Matched Historical Window
```

Primary:

```text
target_slot_completed_appointments
```

Guardrails:

```text
other_offering_displacement
cancellation_rate
staff_overtime
```

성공:

- 설정된 최소 completed appointment 개선
- displacement가 설정 한도 이내
- 운영 incident 없음

중단:

- 직원 capacity 초과
- 다른 Offering의 완료 예약 급감
- policy issue
- result source 연결 실패

---

# 9. PB_BOOKING_AVAILABILITY_AUDIT_V1

## 목적

운영상 판매 가능한 슬롯이 온라인·내부 예약 화면에서도 실제 예약 가능하게 표시되는지 확인한다.

## 적용

```text
Strategy
→ CAPACITY_OPERATION

Cause
→ CAPACITY_OR_OPERATION_CONSTRAINT / DISCOVERABILITY_GAP

Readiness
→ D1
```

## Required

- target slot
- Offering
- operational availability
- booking path
- test owner

## Preconditions

- 예약 흐름을 test booking 또는 비결제 검증으로 확인 가능

## Contraindications

- 실제 환자 정보를 test에 사용
- 운영 중복 예약 위험
- test event를 취소·제거할 절차 없음

## 실행 단계

1. 운영 스케줄의 가용 상태를 확인한다.
2. 사용자 관점에서 예약 페이지를 연다.
3. 목표 Offering·시간대가 선택 가능한지 확인한다.
4. 모바일·데스크톱 또는 주요 경로별 차이를 확인한다.
5. 예약 시작·완료 단계의 오류를 기록한다.
6. 수정 후 동일 경로를 재검증한다.

## Tracking

```text
availability_audit_id
test_booking_id
booking_path_version
```

## Experiment Template

```text
EXP_BOOKING_AVAILABILITY_BEFORE_AFTER_V1
```

Primary:

```text
verified_bookable_target_slot
```

Secondary:

```text
path_error_count
steps_to_slot
test_completion_time
```

성공:

- 운영 availability와 booking availability 일치
- test path 완료
- tracking/result source 작동

중단:

- 이중 예약 위험
- 운영 데이터 충돌
- test booking 정리 불가

---

# 10. PB_LOW_DEMAND_REVISIT_COHORT_V1

## 목적

재방문 예상 시점을 지난 비식별 고객 cohort 중 목표 Offering과 관련된 대상에게, 적법한 수동 실행으로 저수요 슬롯 예약 가능성을 검증한다.

## 적용

```text
Strategy
→ RETENTION_REACTIVATION

Cause
→ RETENTION_GAP

Readiness
→ D3 실행
→ D4 경제성 비교
```

## Required

- customer token capability
- completed visit history
- revisit interval
- eligible cohort count
- target Offering
- target slot capacity
- Offering eligibility
- consent capability
- contact channel
- tracking
- result source
- owner
- period

## Preconditions

- contactable cohort > 0
- 최근 접촉 제외 가능
- 목표 슬롯 실제 가용
- manual approval
- 개별 PII는 실행 환경에서만 처리

## Contraindications

- consent unknown/denied
- capacity unavailable
- contact fatigue 확인 불가
- 최근 동일 cohort Action
- clinical condition targeting
- tracking 없음

## Target Template

포함:

```text
재방문 기준 초과
목표 Offering 이력
최근 동일 Action 없음
마케팅 가능 상태
```

제외:

```text
이미 목표 슬롯 예약
동의 거부
최근 설정 기간 내 접촉
정책상 제외
```

Recommendation Package에는 aggregate count만 포함한다.

## 실행 단계

1. aggregate eligible cohort와 제외 수를 확인한다.
2. 실행 시스템에서 실제 contactable cohort를 검증한다.
3. treatment/comparison 방식을 설정한다.
4. 목표 슬롯·Offering이 연결된 예약 경로를 준비한다.
5. 승인된 수동 채널에서 1회 실행한다.
6. 반복 발송은 별도 승인 없이는 하지 않는다.
7. 예약 생성과 목표 슬롯 완료 예약을 수집한다.
8. 거부·취소·다른 슬롯 이동을 함께 확인한다.

## 채널

```text
manual approved CRM/message
staff callback expansion candidate
front-desk rebooking companion
```

## Economics

Cost:

```text
message
benefit
staff review time
additional service
```

Variable cost가 없으면 revenue-only.

## Experiment Template

```text
EXP_REVISIT_HOLDOUT_V1
```

Sample guidance:

```text
cohort >= 40
→ randomized holdout 검토

20~39
→ exploratory holdout / Grade B

< 20
→ matched historical / Grade C
```

Primary:

```text
completed_revisit_appointments_in_target_slot
```

Secondary:

```text
bookings_created
cancellation_rate
actual_revenue
contact_refusal_rate
```

Guardrails:

```text
complaint
refusal/unsubscribe
customer fatigue
slot displacement
staff overload
```

성공:

- runtime에서 설정한 completed appointment threshold 충족
- 비용-bearing이면 economics 조건 충족
- guardrail 악화 없음

중단:

- 거부·complaint threshold 초과
- capacity 부족
- 예산/비용 상한 도달
- tracking 실패
- 잘못된 cohort 확인

---

# 11. PB_FRONT_DESK_REBOOKING_V1

## 목적

방문 완료 시점에 Offering별 다음 예약 선택지를 안내하고, 강요 없이 현장 재예약 여부를 구조화해 기록한다.

## 적용

```text
Strategy
→ RETENTION_REACTIVATION

Cause
→ RETENTION_GAP

Readiness
→ D2
```

## Required

- Offering별 재방문 검토 기준
- front-desk owner
- 기록 필드
- target slot availability
- result source

## Preconditions

- 방문 중 또는 종료 시 수동 안내 가능
- 직원 교육·스크립트 승인
- 재예약을 강제하지 않음

## Contraindications

- 의료적 재방문 판단을 마케팅 규칙으로 대체
- 직원 성과압박으로 과도한 권유
- 기록 경로 없음
- target slot availability 미확인

## 실행 단계

1. 적용 Offering과 제외 Offering을 정한다.
2. 정책상 허용되는 중립적 안내 문구를 승인한다.
3. 대상 방문 종료 시 다음 예약 선택지를 제시한다.
4. 제안 여부·수락 여부·예약 슬롯을 기록한다.
5. treatment/comparison staff·시간대를 설정한다.
6. 완료 재방문과 취소를 확인한다.
7. 직원별 결과는 교육 개선용으로 사용하고 환자 압박 지표로 사용하지 않는다.

## Experiment Template

```text
EXP_FRONT_DESK_REBOOKING_ALTERNATING_V1
```

방법:

```text
Alternating Time Window
Staff/Shift Split
Matched Historical
```

Primary:

```text
on_site_rebooking_rate
```

Secondary:

```text
completed_revisit_rate
cancellation_rate
staff_offer_rate
```

Guardrails:

```text
complaint
staff burden
policy incident
```

성공:

- 설정된 재예약률 개선
- 완료 재방문 연결 가능
- complaint/policy incident 없음

중단:

- 강요 complaint
- staff overload
- Offering 기준 불명확
- 결과 연결 실패

---

# 12. PB_BOOKING_PATH_VISIBILITY_V1

## 목적

목표 Offering·시간대가 병원 소유 또는 통제 가능한 예약 경로에서 명확히 발견되도록 정리한다.

## 적용

```text
Strategy
→ DISCOVERABILITY

Cause
→ DISCOVERABILITY_GAP

Readiness
→ D2
```

## Required

- target slot availability
- Offering eligibility
- owned booking path
- path owner
- tracking/result source
- policy status

## Preconditions

- 예약 페이지·웹·프로필 중 하나 이상 수정 가능
- 변경 전후 상태를 캡처·검증 가능

## Contraindications

- target slot unavailable
- prohibited claim 필요
- tracking 없음
- 외부 플랫폼 정책상 수정 불가

## 실행 단계

1. 현재 예약 경로와 목표 Offering·시간대 노출 상태를 기록한다.
2. 누락·불일치·불필요한 단계 한 가지를 선택한다.
3. Offering·위치·예약 가능 정보의 사실 일치를 확인한다.
4. 목표 슬롯으로 가는 경로를 짧게 만든다.
5. source tracking을 설정한다.
6. 한 번에 하나의 주요 경로 변경만 실행한다.
7. 예약 완료와 path error를 비교한다.

## 채널

```text
BOOKING_PAGE
WEBSITE
NAVER_PLACE 또는 business profile
```

유료 광고는 별도 Playbook이다.

## Experiment Template

```text
EXP_BOOKING_VISIBILITY_BEFORE_AFTER_V1
```

Primary:

```text
completed_bookings_from_target_path
```

Secondary:

```text
path_visits
booking_starts
steps_to_book
```

Evidence Grade ceiling:

```text
B if controlled path split
C if matched historical
D if simple before/after
```

중단:

- target slot capacity 변경
- tracking failure
- 정책 issue
- booking error 증가

---

# 13. PB_BOOKING_FUNNEL_FRICTION_V1

## 목적

예약 경로의 단계별 이탈을 측정하고 가장 큰 마찰 한 가지를 줄인다.

## 적용

```text
Strategy
→ CONVERSION

Cause
→ CONVERSION_FRICTION

Readiness
→ D2 평가
→ D3 실행
```

## Required

- funnel start/end metrics
- period/segment alignment
- booking path owner
- target slot availability
- tracking
- result source

## Preconditions

- 최소 두 개 funnel 단계 측정 가능
- 한 번에 한 가지 변경 가능

## Contraindications

- funnel 유입 자체가 없음
- capacity unavailable
- 모든 단계가 추적 불가
- patient PII를 분석 event로 전송

## 실행 단계

1. funnel 단계를 고정한다.
2. 단계별 volume·conversion을 계산한다.
3. 가장 큰 drop-off 한 곳을 선택한다.
4. 변경 가설과 영향을 받지 않아야 할 guardrail을 정한다.
5. treatment/comparison 또는 전후 비교를 설정한다.
6. 변경을 적용한다.
7. booking completion과 오류·문의량을 확인한다.

## Experiment Template

```text
EXP_FUNNEL_SINGLE_CHANGE_V1
```

Primary:

```text
booking_completion_rate
```

Secondary:

```text
booking_start_rate
steps_to_complete
time_to_book
inquiry_to_booking
```

Guardrails:

```text
booking_error
support_inquiry
cancellation
```

중단:

- 오류 증가
- capacity mismatch
- tracking event 누락
- 여러 변경이 동시에 발생

---

# 14. PB_NON_DISCOUNT_VALUE_ADD_V1

## 목적

가격 할인 대신 정책상 허용되고 원가가 확인된 저비용 부가가치·편의·예약 우선권 등을 제한적으로 비교한다.

## 적용

```text
Strategy
→ OFFER_PACKAGING

Cause
→ VALUE_OR_PRICE_FRICTION / OFFER_SLOT_MISMATCH

Readiness
→ D3 manual
→ D4 economics
```

## Required

- Offering eligibility
- benefit candidate
- benefit cost
- price mode
- policy approval
- target slot capacity
- tracking/result source
- budget cap
- owner

## Preconditions

- 부가가치가 의료 결과 보장이 아님
- 실제 제공 가능
- 비용과 운영 부담을 계산 가능
- 비교 조건 존재

## Contraindications

- benefit cost unknown
- policy blocked
- contribution <= 0
- 임상 결과·우월성 주장 필요
- 직원 capacity 초과

## 실행 단계

1. 허용 가능한 부가가치 후보를 제한된 수로 정한다.
2. 비용·제공 capacity·정책을 검토한다.
3. 할인·부가가치·무혜택 중 실제 비교 가능한 조건을 고른다.
4. 대상과 Offering을 고정한다.
5. treatment/comparison을 설정한다.
6. 예약 완료와 실제 비용을 수집한다.
7. revenue-only와 net contribution을 구분한다.

## Experiment Template

```text
EXP_NON_DISCOUNT_VALUE_ADD_V1
```

Primary:

```text
completed_appointments_in_target_slot
```

Secondary:

```text
net_contribution_if_available
benefit_cost
cancellation_rate
```

Guardrails:

```text
complaint
staff burden
policy incident
displacement
```

중단:

- 비용 상한 초과
- 기여금액 비양수
- policy issue
- capacity 부족
- 결과 연결 실패

---

# 15. PB_TRACKED_LOCAL_PARTNERSHIP_V1

## 목적

고객 동선이 겹치고 경쟁하지 않는 제휴 후보와 고유 코드·QR을 사용해 완료 예약까지 추적 가능한 소규모 제휴 실험을 만든다.

## 적용

```text
Strategy
→ PARTNERSHIP_REFERRAL

Cause
→ DISCOVERABILITY_GAP / DEMAND_DEFICIT conditional

Readiness
→ D4
```

## Required

- partner candidate basis
- partner owner
- policy approval
- target Offering/slot capacity
- partner-specific tracking
- result source
- compensation/cost
- budget cap
- experiment period

## Preconditions

- 제휴처별 결과를 분리 가능
- 보상 조건이 문서화
- Offering 표현 정책 검토
- 대량 무추적 배포가 아님

## Contraindications

- 고유 코드/QR 없음
- 비용·보상 unknown
- 제휴처별 결과 분리 불가
- 임상정보 공유
- 환자 PII 전달
- 경쟁·브랜드·정책 위험 unresolved

## 실행 단계

1. 고객 동선이 겹치는 비경쟁 제휴 유형을 정의한다.
2. 3~5개 후보를 shortlist한다.
3. 정책·운영 적합성을 검토한다.
4. 제휴처별 고유 partner code/QR을 만든다.
5. 카운터 카드·직원 안내·예약 경로를 준비한다.
6. 제한된 수의 제휴처로 pilot한다.
7. 실제 설치·안내 시작일과 비용을 기록한다.
8. 완료 예약·비용을 제휴처별 비교한다.
9. 유지·중단 대상을 분리한다.

## Experiment Template

```text
EXP_PARTNER_CODE_SPLIT_V1
```

Primary:

```text
completed_bookings_by_partner
```

Secondary:

```text
cost_per_completed_booking
net_contribution_by_partner
code_scan_to_booking
```

Guardrails:

```text
policy incident
partner complaint
untracked referral
capacity overload
```

중단:

- 비용 상한 도달
- 설정 기간 내 추적 완료 예약 없음
- source code 오염
- 정책·브랜드 issue
- capacity 부족

---

# 16. PB_NO_ACTION_MONITORING_V1

## 목적

현재 실행의 기대가치·근거·capacity·정책·측정 조건이 부족할 때 비용을 쓰지 않고 명시적인 재평가 조건을 유지한다.

## 적용

```text
Strategy
→ NO_ACTION

Readiness
→ D0
```

## Required

- reason code
- monitoring metric
- segment
- review date
- reopen trigger
- current limitation

## Preconditions

- 현재 실행 보류의 이유를 구조화 가능
- 재평가 시점 또는 trigger 설정 가능

## Contraindications

- critical safety issue를 단순 모니터링으로 미룸
- data quality correction이 가능한데 담당자를 지정하지 않음
- 긴급 운영 문제를 방치

## 실행 단계

1. 보류 reason code를 선택한다.
2. 현재 실행 후보의 blocker와 비용을 기록한다.
3. 관찰할 Metric과 segment를 고정한다.
4. 재평가 날짜를 정한다.
5. 재개 trigger를 설정한다.
6. 해당 시점에 Opportunity·Cause·Strategy를 다시 실행한다.

## Reason Code

```text
ECONOMICS_INFEASIBLE
INSUFFICIENT_EVIDENCE
POLICY_BLOCKED
CAPACITY_UNAVAILABLE
OPPORTUNITY_TOO_SMALL
MEASUREMENT_NOT_POSSIBLE
DUPLICATE_RECENT_ACTION
TEMPORARY_CONSTRAINT
```

## Experiment Template

```text
EXP_NO_ACTION_MONITORING_V1
```

Primary:

```text
configured_monitoring_metric
```

Success:

- 불필요한 비용 집행 없음
- 재평가가 설정 시점에 실행됨
- reopen trigger 여부가 기록됨

중단:

- safety/operational issue 발생
- 새로운 critical data 도착
- capacity/policy 상태 변화

Economics:

```text
not_applicable
```

---

# 17. Expansion Playbook 상세화 Gate

Expansion ID를 상세화하려면 다음이 필요하다.

## 고객 접촉형

```text
consent capability
contact fatigue
manual owner
tracking
result source
policy
```

대상:

```text
PB_STAFF_CALLBACK_REVISIT_V1
PB_WAITLIST_RECOVERY_V1
PB_RESCHEDULE_PATH_V1
```

## 유료·획득형

```text
D4 economics
budget cap
external demand
conversion tracking
policy
```

대상:

```text
PB_CONTROLLED_SEARCH_ACQUISITION_V1
PB_SEARCH_INTENT_SLOT_CAPTURE_V1
```

## 외부 플랫폼형

```text
provider field contract
profile/landing version
tracking
change audit
```

대상:

```text
PB_MAP_PROFILE_OFFERING_AUDIT_V1
PB_DEEP_LINK_SLOT_TEST_V1
PB_CHANNEL_SOURCE_REALLOCATION_V1
```

## Offering 표현형

```text
policy-safe content contract
economics
experiment
result source
```

대상:

```text
PB_TIME_SLOT_OFFER_BUNDLE_V1
PB_VALUE_EXPLANATION_TEST_V1
```

## 취소 회수형

```text
Cancellation vertical slice
reminder/reschedule/waitlist domain
consent
tracking
```

대상:

```text
PB_CANCELLATION_FLOW_REVIEW_V1
PB_WAITLIST_RECOVERY_V1
PB_RESCHEDULE_PATH_V1
```

---

# 18. Catalog 구현 Backlog

```text
PBC-001 canonical registry rows
PBC-002 legacy alias map
PBC-003 core 12 Definition fixtures
PBC-004 validation fixtures
PBC-005 applicability fixtures
PBC-006 experiment template reference validation
PBC-007 policy tags
PBC-008 output artifact schemas
PBC-009 expansion index
PBC-010 existing Manual Action adapter
```

---

# 19. Core Catalog 완료조건

1. Core 12 정식 ID
2. 숫자형 alias mapping
3. 모든 Playbook status=DRAFT
4. Strategy/Cause/Opportunity mapping
5. minimum readiness
6. Required/Precondition/Contraindication
7. online/offline steps
8. tracking/result source
9. economics status
10. experiment template
11. success/stop
12. policy tags
13. output artifacts
14. Hospital PII 미사용
15. 자동 실행 없음
