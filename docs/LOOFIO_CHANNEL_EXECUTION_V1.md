---
title: "LOOFIO Channel Execution v1"
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
  - "LOOFIO_STRATEGY_ENGINE_V1.md"
  - "LOOFIO_ACTION_PLAYBOOK_V1.md"
  - "LOOFIO_EXPERIMENT_DESIGN_V1.md"
  - "LOOFIO_RECOMMENDATION_PACKAGE_V2.md"
  - "LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md"
  - "LOOFIO_MEASUREMENT_FRAMEWORK_V1.md"
---

# LOOFIO Channel Execution v1

## 1. 문서 목적

이 문서는 승인된 Recommendation Package와 Playbook Instance를 온라인·오프라인 채널에서 안전하고 추적 가능하게 실행하기 위한 Channel Execution 계약을 정의한다.

LOOFIO가 실행 계층에서 해결해야 하는 문제는 단순히 “메시지를 보냈다” 또는 “전단지를 배포했다”가 아니다.

```text
누가 승인했는가
어느 사업장·Offering·대상·기간인가
어느 채널에서 어떤 수준으로 실행하는가
예산 상한은 얼마인가
실제 실행이 몇 번 시도됐는가
외부 시스템에서 성공·실패·취소 상태는 무엇인가
어떤 Tracking 값으로 예약·완료 결과와 연결하는가
개인정보는 어디에서 처리하고 얼마나 보존하는가
재시도와 중복 실행을 어떻게 방지하는가
중단·취소·부분 실패를 어떻게 기록하는가
```

핵심 원칙:

> Channel Execution은 전략을 선택하는 계층이 아니다.
> 승인된 실행 계약을 Provider 또는 사람의 운영 절차로 전달하고, 전달 상태·비용·추적·결과 Event를 정확히 기록하는 계층이다.

---

# 2. 현재 구현 Snapshot

현재 `main`의 Action은 다음 계약을 사용한다.

```text
version
→ manual-action-v1

status
→ planned
→ in_progress
→ completed

또는

planned / in_progress
→ cancelled
```

현재 Action은:

- 승인된 Recommendation에서만 생성
- tenant scope 적용
- `owner`, `admin`, `marketer` 역할만 생성·상태 변경
- 제목, 실행 메모, 시작·종료 예정 시각, 계획 예산 저장
- 상태 변경 이력 저장
- 한 Recommendation·Action version당 중복 생성 방지
- 외부 Provider 호출 없음
- 결과는 Action이 `completed`일 때 수동 기록

현재 Result:

```text
execution_summary
measurement_start_at
measurement_end_at
actual_spend(optional)
outcome_notes
```

현재 구조는 폐기하지 않는다.

```text
현재 Action
→ Human-readable business execution lifecycle

새 Channel Execution
→ 실제 전달·Provider·오프라인 운영 시도 lifecycle
```

첫 구현은 현재 Manual Action 위에 additive하게 붙인다.

---

# 3. 실행 계층 위치

```text
Recommendation Package
→ User Decision
→ Action
→ Execution Package
→ Execution Attempt
→ Delivery / Operational Event
→ Outcome Linkage Event
→ Action Result
→ Measurement
```

각 계층의 책임:

| 계층 | 책임 |
|---|---|
| Recommendation Package | 왜·무엇을 실행할지 |
| Action | 사용자가 승인한 사업 실행 계획 |
| Execution Package | 채널별 실행에 필요한 고정 계약 |
| Execution Attempt | 실제 한 번의 실행 시도 |
| Delivery Event | 전달·게시·설치·통화 등 실행 상태 |
| Outcome Linkage Event | 예약·완료·비용·거부·오류 연결 |
| Result / Measurement | 관측 결과와 효과 해석 |

---

# 4. 실행 수준

```text
MANUAL
COPY_EXPORT
STAFF_OPERATED
APPROVED_CONNECTOR
BOUNDED_AUTOMATION
```

## 4.1 `MANUAL`

LOOFIO 밖에서 사람이 직접 실행한다.

예:

```text
운영자가 예약 경로를 수정
직원이 현장 재예약 안내
담당자가 제휴처를 방문
```

LOOFIO 역할:

- 실행 Checklist
- 담당자·기한
- Tracking 값
- 상태 기록
- Result 입력

현재 `manual-action-v1`과 가장 가까운 수준이다.

## 4.2 `COPY_EXPORT`

LOOFIO가 승인된 실행 자료를 생성하고 사용자가 외부 도구에 복사·업로드한다.

예:

```text
승인된 메시지 문구 복사
대상 조건 CSV export
QR·Partner code 자료 export
예약 링크 복사
```

LOOFIO가 실제 전송 버튼을 누르지 않는다.

필수:

- export audit
- 유효기간
- 최소 개인정보
- 대상 수
- checksum 또는 export ID
- 외부 실행 후 확인

## 4.3 `STAFF_OPERATED`

LOOFIO 안에서 업무 Queue·Checklist를 제공하지만 실행은 직원이 수행한다.

예:

```text
Front-desk rebooking
Staff callback
Waitlist recovery
Partner placement confirmation
```

필수:

- Task assignment
- 수행·미수행·실패 이유
- 고객 접촉 시 동의 검증
- 결과 Source
- 운영 부담 기록

## 4.4 `APPROVED_CONNECTOR`

사용자가 특정 Execution Package를 명시적으로 승인한 뒤 Connector가 외부 API를 호출한다.

예:

```text
승인된 SMS 1회 발송
예약 페이지 설정 변경
승인된 광고 실험 생성
```

현재 미구현이다.

필수:

- Provider-neutral Port
- Connector capability
- explicit approval
- secret reference
- idempotency
- budget cap
- dry-run/preview
- retry policy
- cancel path
- provider reference
- delivery/result webhook 또는 polling

## 4.5 `BOUNDED_AUTOMATION`

사전에 승인한 좁은 정책 범위 안에서 자동 실행한다.

예:

```text
특정 예산 이하
특정 Playbook
특정 기간
특정 대상 조건
```

현재 MVP에서 금지한다.

도입 전 필수:

- automation policy version
- per-business opt-in
- budget/volume/risk hard limits
- kill switch
- notification
- audit
- rollback/cancel
- incident runbook
- human override
- policy/legal review

---

# 5. 구현 단계별 허용 범위

## 현재

```text
MANUAL
```

## Decision Intelligence 첫 Vertical Slice

```text
MANUAL
COPY_EXPORT
STAFF_OPERATED
```

## Pilot 이후 후보

```text
APPROVED_CONNECTOR
```

## 별도 Phase

```text
BOUNDED_AUTOMATION
```

미구현 실행 수준을 UI에서 가능한 기능처럼 표시하지 않는다.

---

# 6. Channel Taxonomy

## 6.1 Online / Digital

```text
BOOKING_PAGE
WEBSITE
NAVER_PLACE
KAKAO
SMS
EMAIL
SEARCH_ADS
SOCIAL_ADS
ORGANIC_SOCIAL
CRM_EXPORT
```

## 6.2 Offline / Human-operated

```text
FRONT_DESK
STAFF_CALLBACK
WAITLIST
PARTNER_REFERRAL
TRACKED_PRINT
IN_STORE_SIGNAGE
MANUAL_OPERATION
```

## 6.3 System / Measurement Support

```text
TRACKING_SETUP
RESULT_SYNC
DATA_AUDIT
CAPACITY_CONFIGURATION
```

## 6.4 Channel Role

```text
DISCOVER
CONVERT
RETAIN
RECOVER
VERIFY
MEASURE
OPERATE
```

한 실행 패키지는 여러 채널을 가질 수 있지만 각 채널의 역할을 명시한다.

---

# 7. 실행 객체 모델

```text
Action
  └─ ExecutionPackage
       ├─ ExecutionTarget
       ├─ ExecutionAsset
       ├─ TrackingContract
       ├─ BudgetContract
       ├─ ApprovalContract
       ├─ ExecutionAttempt
       │    └─ ExecutionEvent
       └─ OutcomeLinkageEvent
```

## 7.1 `ExecutionPackage`

승인 가능한 채널 실행 계약.

## 7.2 `ExecutionAttempt`

실제 실행 시도 1회.

Connector retry 또는 직원 재시도는 별도 Attempt다.

## 7.3 `ExecutionEvent`

Attempt에서 발생한 상태 Event.

## 7.4 `OutcomeLinkageEvent`

예약·완료·비용·거부 등 결과를 Action과 연결하는 Event.

---

# 8. Execution Package Contract

```json
{
  "execution_package_id": "EXPKG_xxx",
  "execution_version": "channel-execution-v1",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "location_id": "LOC_01",
  "action_id": "ACT_01",
  "recommendation_package_id": "RPKG_01",
  "experiment_id": "EXP_01",
  "status": "READY_FOR_APPROVAL",
  "mode": "STAFF_OPERATED",
  "channel_type": "FRONT_DESK",
  "channel_role": "RETAIN",
  "owner": {
    "role": "front_desk",
    "user_id": null
  },
  "target": {},
  "offering_scope": [],
  "slot_scope": {},
  "assets": [],
  "tracking": {},
  "budget": {},
  "approval": {},
  "schedule": {},
  "provider": null,
  "idempotency": {},
  "retry_policy": {},
  "cancellation_policy": {},
  "result_contract": {},
  "privacy": {},
  "limitations": []
}
```

---

# 9. Execution Package 상태

```text
DRAFT
NEEDS_DATA
NEEDS_POLICY_REVIEW
READY_FOR_APPROVAL
APPROVED
SCHEDULED
RUNNING
PARTIALLY_COMPLETED
COMPLETED
FAILED
CANCEL_REQUESTED
CANCELLED
BLOCKED
EXPIRED
SUPERSEDED
```

## 상태 의미

### `DRAFT`

채널 계약을 조립 중.

### `NEEDS_DATA`

Tracking·담당자·기간·예산·대상·Result Source 부족.

### `NEEDS_POLICY_REVIEW`

정책·동의·Offering 마케팅 검토 필요.

### `READY_FOR_APPROVAL`

실행에 필요한 계약이 완성됐지만 아직 사용자 승인 전.

### `APPROVED`

권한 있는 사용자가 이 Package version과 범위를 승인.

### `SCHEDULED`

실행 시간 또는 Staff Task가 예약됨.

### `RUNNING`

최소 1개 Attempt 진행 중 또는 Staff 운영 시작.

### `PARTIALLY_COMPLETED`

대상·제휴처·작업 일부 완료, 일부 실패·보류.

### `COMPLETED`

계약된 실행 범위가 끝났고 Result 수집 단계로 이동.

성과가 좋았다는 의미가 아니다.

### `FAILED`

실행 완료 불가.

### `CANCEL_REQUESTED`

외부 시스템 또는 직원 Queue에 취소 요청 전달.

### `CANCELLED`

더 이상 새 실행이 발생하지 않는 상태.

이미 전달된 메시지·게시물·인쇄물은 회수되지 않을 수 있다.

### `BLOCKED`

보안·정책·Provider·Tracking 문제로 실행 금지.

### `EXPIRED`

승인 유효기간 또는 실행 기간 만료.

### `SUPERSEDED`

새 Package revision이 기존 Package를 대체.

---

# 10. 현재 Action 상태와 매핑

현재 Action 상태는 유지한다.

```text
planned
in_progress
completed
cancelled
```

권장 매핑:

| Execution Package | Action |
|---|---|
| DRAFT / NEEDS_* / READY_FOR_APPROVAL / APPROVED / SCHEDULED | `planned` |
| RUNNING / PARTIALLY_COMPLETED / CANCEL_REQUESTED | `in_progress` |
| COMPLETED | `completed` |
| CANCELLED / EXPIRED before execution | `cancelled` |
| FAILED | 자동 Action 종결 금지, 사용자 검토 후 `cancelled` 또는 재시도 |
| BLOCKED | `planned` 유지 또는 사용자 취소 |

Action은 사업 계획 상태이고 Execution은 채널 전달 상태이므로 완전히 동일시하지 않는다.

---

# 11. Action 생성 전제

현재 규칙을 유지한다.

```text
승인된 Recommendation
→ Action 생성 가능
```

Package 기반 장기 규칙:

```text
Recommendation Package APPROVED
+
Quality PASSED
+
Experiment APPROVED
+
Execution Package Contract ready
→ Action 또는 Execution Package 생성
```

Hard Fail 또는 `NEEDS_*` 상태에서 실행 Package를 만들지 않는다.

---

# 12. Approval Contract

```json
{
  "required": true,
  "approval_type": "SINGLE_ACTION",
  "status": "pending",
  "approved_by_user_id": null,
  "approved_at": null,
  "approved_scope_hash": null,
  "expires_at": "2026-08-25T00:00:00+09:00",
  "revoked_at": null
}
```

## Approval Type

```text
SINGLE_ACTION
SINGLE_BATCH
SCHEDULED_WINDOW
AUTOMATION_POLICY
```

현재 허용:

```text
SINGLE_ACTION
SINGLE_BATCH for manual/copy export
```

미허용:

```text
AUTOMATION_POLICY
```

## 승인 Hash

다음 값의 Hash를 승인한다.

```text
target scope
assets
channel
schedule
budget cap
tracking
experiment
provider account
```

승인 후 이 값이 바뀌면 재승인한다.

---

# 13. 권한 Matrix

현재 역할:

```text
owner
admin
marketer
viewer
```

권장:

| 작업 | owner | admin | marketer | viewer |
|---|:---:|:---:|:---:|:---:|
| Package 조회 | ✅ | ✅ | ✅ | ✅ |
| Manual/Staff Package 생성 | ✅ | ✅ | ✅ | ❌ |
| Copy Export 생성 | ✅ | ✅ | ✅ | ❌ |
| 실행 승인 | ✅ | ✅ | 조건부 | ❌ |
| Budget-bearing 실행 승인 | ✅ | 정책에 따라 | ❌ 기본 | ❌ |
| Connector 실행 | ✅ | 조건부 | ❌ 기본 | ❌ |
| 상태·결과 기록 | ✅ | ✅ | ✅ | ❌ |
| Automation Policy | 향후 | 향후 | ❌ | ❌ |

`marketer`의 예산·외부 실행 승인 범위는 별도 Business Policy로 설정한다.

---

# 14. Target Contract

```text
target_type
selection_source
inclusion
exclusion
estimated_count
frozen_count
privacy_mode
consent_status
freshness
source refs
```

## Target Type

```text
AGGREGATE_COHORT
TOKENIZED_INTERNAL_COHORT
BOOKING_PATH_AUDIENCE
TIME_SLOT
STAFF_SHIFT
PARTNER_LIST
PUBLIC_AUDIENCE
NONE
```

## Privacy Mode

```text
aggregate
tokenized_internal
external_system_managed
public
not_applicable
```

## 규칙

- Recommendation/UI 기본은 aggregate.
- 개별 연락처는 LOOFIO Package에 포함하지 않는다.
- Export가 필요하면 적법한 Source System에서 처리하거나 별도 단기 Export 계약을 사용한다.
- Target frozen 이후 임의 추가 금지.
- 동의 거부·이미 예약·최근 접촉 등 제외 기준 적용.
- 개인 임상정보 Targeting 금지.

---

# 15. Export Contract

`COPY_EXPORT`에서 사용한다.

```json
{
  "export_id": "EXPFILE_xxx",
  "export_type": "TARGET_REFERENCE",
  "format": "csv",
  "row_count": 61,
  "field_set_version": "channel-export-minimal-v1",
  "generated_at": "2026-08-18T09:00:00+09:00",
  "expires_at": "2026-08-19T09:00:00+09:00",
  "checksum": "...",
  "downloaded_by_user_id": null,
  "downloaded_at": null,
  "retention_policy": "delete_after_expiry",
  "contains_direct_contact": false
}
```

## 원칙

- 최소 Field.
- Contact 정보 Export는 기본 금지.
- 필요 시 외부 CRM이 Target 조건을 해석하는 reference만 Export.
- Download audit.
- 만료.
- 재다운로드 정책.
- 로컬 파일 삭제 안내.
- Export 파일을 AI 입력으로 사용 금지.

---

# 16. Asset Contract

```text
asset_id
asset_type
version
status
content hash
language
channel compatibility
policy status
approved by/at
expires at
source package
```

## Asset Type

```text
MESSAGE_DRAFT
STAFF_SCRIPT
BOOKING_LINK
LANDING_COPY
QR_CODE
PARTNER_CARD
TRACKED_PRINT_ARTWORK
CHECKLIST
CONFIGURATION_CHANGE
```

## 상태

```text
DRAFT
NEEDS_POLICY_REVIEW
APPROVED
REJECTED
EXPIRED
SUPERSEDED
```

승인되지 않은 Asset을 실행하지 않는다.

---

# 17. Tracking Contract

```json
{
  "tracking_type": "BOOKING_SOURCE_CODE",
  "tracking_value": "ACT-01-R1",
  "verification_status": "VERIFIED",
  "test_event_id": "TEVT_01",
  "source_system": "appointment_import",
  "result_linkage": {
    "event": "appointment_completed",
    "field": "source_code"
  },
  "expires_at": "2026-09-30T00:00:00+09:00"
}
```

## Tracking Type

```text
ACTION_ID
UTM
UNIQUE_URL
BOOKING_SOURCE_CODE
COUPON_CODE
PARTNER_CODE
QR
MANUAL_SOURCE_TAG
PROVIDER_CAMPAIGN_ID
PROVIDER_MESSAGE_ID
```

## 규칙

- 실행형 Package는 최소 하나.
- Test Event 검증.
- PII 포함 금지.
- tenant/business scope.
- Provider ID와 내부 Action ID 분리.
- Tracking 없음 → `NEEDS_DATA`.
- 추적 실패 → 신규 실행 중지 또는 `PAUSE_AND_REVIEW`.

---

# 18. Budget Contract

```json
{
  "currency": "KRW",
  "planned_budget_cap": "120000.00",
  "spent_amount": "0.00",
  "reserved_amount": "0.00",
  "remaining_amount": "120000.00",
  "cost_components": [],
  "hard_stop_on_cap": true,
  "approved_by_user_id": "USER_01"
}
```

## 규칙

- 비용-bearing 실행은 cap 필수.
- `unknown` 비용은 0이 아님.
- Planned / Reserved / Actual 분리.
- Connector는 실행 전 remaining budget 확인.
- 초과 요청은 거부.
- Provider 비용 지연이 있으면 `spend_status = delayed`.
- 실제 비용 반영 전 Net Contribution 확정 금지.

---

# 19. Idempotency Contract

중복 외부 실행을 방지한다.

```text
idempotency_scope
idempotency_key
request_hash
provider_support
first_attempt_at
replay_count
result reference
```

## Scope 후보

```text
tenant + execution_package + channel + batch
tenant + action + target unit
tenant + provider account + scheduled window
```

## 규칙

- 같은 Key + 같은 Payload → 기존 결과 반환.
- 같은 Key + 다른 Payload → Conflict.
- Provider가 Idempotency를 지원하지 않으면 내부 dedupe store 사용.
- Timeout 후 Provider 결과 확인 없이 즉시 재시도 금지.
- Manual/Staff Task도 중복 Task 생성 방지.
- Retry마다 새 Attempt ID, 같은 logical idempotency key.

---

# 20. Retry Policy

```json
{
  "mode": "BOUNDED",
  "max_attempts": 3,
  "retryable_errors": [
    "TIMEOUT",
    "RATE_LIMIT",
    "PROVIDER_5XX"
  ],
  "non_retryable_errors": [
    "POLICY_REJECTED",
    "INVALID_TARGET",
    "CONSENT_MISSING",
    "BUDGET_EXCEEDED"
  ],
  "backoff": "exponential_with_jitter",
  "verify_before_retry": true
}
```

## 원칙

- 재시도 가능한 오류만.
- max attempts.
- exponential backoff.
- Provider에서 이미 성공했는지 조회.
- 실패 원문에 Secret·PII 저장 금지.
- 최종 실패 시 사용자에게 다음 행동 제시.
- Staff Task 재시도는 담당자 변경·기한 연장 등을 Event로 기록.

---

# 21. Execution Attempt Contract

```json
{
  "attempt_id": "EXATT_xxx",
  "execution_package_id": "EXPKG_01",
  "attempt_number": 1,
  "status": "SUCCEEDED",
  "mode": "MANUAL",
  "provider": null,
  "started_at": "2026-08-18T10:00:00+09:00",
  "completed_at": "2026-08-18T10:15:00+09:00",
  "idempotency_key": "...",
  "provider_reference": null,
  "delivered_count": 1,
  "failed_count": 0,
  "cost": null,
  "error": null
}
```

## Attempt 상태

```text
PENDING
STARTED
AWAITING_PROVIDER_CONFIRMATION
SUCCEEDED
PARTIALLY_SUCCEEDED
FAILED_RETRYABLE
FAILED_FINAL
CANCELLED
UNKNOWN
```

`UNKNOWN`은 Timeout 이후 Provider 성공 여부를 확인하지 못한 상태다.
이 상태에서 중복 실행을 방지한다.

---

# 22. Execution Event Taxonomy

## Lifecycle

```text
EXECUTION_PACKAGE_CREATED
EXECUTION_PACKAGE_APPROVED
EXECUTION_SCHEDULED
EXECUTION_STARTED
EXECUTION_PAUSED
EXECUTION_RESUMED
EXECUTION_COMPLETED
EXECUTION_FAILED
EXECUTION_CANCEL_REQUESTED
EXECUTION_CANCELLED
EXECUTION_EXPIRED
```

## Attempt / Delivery

```text
ATTEMPT_CREATED
ATTEMPT_SENT
ATTEMPT_ACKNOWLEDGED
DELIVERY_ACCEPTED
DELIVERY_DELIVERED
DELIVERY_FAILED
DELIVERY_BOUNCED
DELIVERY_REJECTED
DELIVERY_UNKNOWN
```

## Human-operated

```text
TASK_ASSIGNED
TASK_STARTED
TASK_COMPLETED
TASK_SKIPPED
TASK_FAILED
CALL_ATTEMPTED
CALL_CONNECTED
CALL_NOT_REACHED
FRONT_DESK_OFFER_RECORDED
WAITLIST_CONTACT_RECORDED
PARTNER_MATERIAL_PLACED
PARTNER_MATERIAL_REMOVED
```

## Tracking / Outcome

```text
TRACKING_TESTED
TRACKING_VERIFIED
TRACKING_FAILED
LINK_CLICKED
QR_SCANNED
BOOKING_STARTED
BOOKING_CREATED
APPOINTMENT_COMPLETED
APPOINTMENT_CANCELLED
NO_SHOW_RECORDED
SPEND_RECORDED
COMPLAINT_RECORDED
CONSENT_WITHDRAWN
```

---

# 23. Event Contract

```json
{
  "event_id": "EXEVT_xxx",
  "event_version": "channel-execution-event-v1",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "execution_package_id": "EXPKG_01",
  "attempt_id": "EXATT_01",
  "action_id": "ACT_01",
  "event_type": "TASK_COMPLETED",
  "occurred_at": "2026-08-18T10:15:00+09:00",
  "recorded_at": "2026-08-18T10:16:00+09:00",
  "source": "manual_user",
  "source_reference": null,
  "actor": {
    "type": "user",
    "id": "USER_01"
  },
  "quantity": 1,
  "money": null,
  "metadata": {},
  "dedupe_key": "..."
}
```

## 규칙

- Append-only.
- Event 발생 시각과 기록 시각 분리.
- Source reference.
- Dedupe key.
- PII 최소화.
- Event 수정 대신 correction event 또는 superseding event.
- tenant/business scope.

---

# 24. Outcome Linkage

```text
Execution Event
→ Tracking Value
→ Booking / Appointment / Payment Event
→ Action / Experiment Result
```

## Link 상태

```text
VERIFIED
PARTIAL
UNVERIFIED
CONFLICTING
MISSING
```

## 규칙

- Attributed 결과와 Incremental 결과 구분.
- 동일 Appointment를 여러 Action에 중복 귀속하지 않도록 precedence 또는 multi-touch 상태 명시.
- v1은 복잡한 multi-touch attribution을 구현하지 않는다.
- 직접 Tracking 일치가 없으면 `manual_verified` 또는 `unverified`.
- 환자 PII 없이 internal source record 또는 tokenized linkage 사용.

---

# 25. Cancellation Contract

## Cancel 대상

```text
미실행 Task
예약된 Connector Job
아직 전달되지 않은 Batch
향후 노출
```

## 취소 불가능할 수 있는 대상

```text
이미 전달된 SMS/Email
이미 게시된 외부 콘텐츠
이미 인쇄·배포된 자료
이미 수행된 Staff Call
```

## 취소 결과

```text
CANCELLED_FULL
CANCELLED_FUTURE_ONLY
CANCEL_REQUESTED_PROVIDER
CANNOT_RECALL
CANCEL_FAILED
```

## 규칙

- 취소가 이미 발생한 결과를 삭제하지 않는다.
- Experiment contamination/partial exposure로 기록.
- 게시물 제거가 가능하면 별도 remove attempt.
- Partner material 회수는 Staff Task.
- Budget reserve 해제.
- 사용자에게 회수 불가 범위를 명확히 표시.

---

# 26. Pause / Kill Switch

Connector 또는 Automation 도입 전 필수.

## Scope

```text
global
tenant
business
channel
provider account
playbook
execution package
```

## Trigger

```text
security incident
policy incident
complaint threshold
budget anomaly
tracking failure
provider error spike
tenant request
```

## 동작

```text
new execution block
scheduled job cancel request
current attempts pause if possible
alert
audit event
manual review
```

현재 Manual MVP에서는 Package를 `BLOCKED` 또는 `CANCELLED`로 처리한다.

---

# 27. Online Channel 계약

## 27.1 `BOOKING_PAGE`

목적:

```text
Offering·슬롯 가시성
딥링크
Booking Source Code
Funnel Tracking
```

실행 수준:

```text
MANUAL
STAFF_OPERATED
향후 APPROVED_CONNECTOR
```

필수:

- target slot availability
- Offering policy
- tracking
- booking test
- rollback/config backup

## 27.2 `WEBSITE`

필수:

- owned page
- approved asset
- UTM/source code
- versioned change
- rollback
- funnel event

## 27.3 `NAVER_PLACE`

현재:

```text
manual / copy-export 계획
```

향후 Connector 가능 여부는 별도 Provider 계약 검토.

필수:

- factual Offering/location data
- prohibited claim check
- change screenshot/reference
- result source

## 27.4 `KAKAO`, `SMS`, `EMAIL`

현재:

```text
copy_export 또는 external-system-managed manual
```

필수:

- consent verified
- suppression list
- recent-contact guardrail
- one-time approval
- send cap
- refusal/unsubscribe result
- provider message ID if connector
- no clinical targeting

## 27.5 `SEARCH_ADS`, `SOCIAL_ADS`

현재 미구현.

필수:

- D4 economics
- external demand evidence
- budget cap
- conversion tracking
- policy review
- campaign/ad group/creative version
- experiment
- spend sync
- pause/cancel
- no automatic budget increase

## 27.6 `ORGANIC_SOCIAL`

조회·좋아요만으로 성공 판정하지 않는다.

필수:

- approved content
- target path tracking
- booking/result source
- manual posting reference

---

# 28. Offline Channel 계약

## 28.1 `FRONT_DESK`

필수:

- approved neutral script
- eligible visit rule
- offer recorded
- rebooking result
- complaint/policy guardrail
- staff burden

## 28.2 `STAFF_CALLBACK`

필수:

- consent/contact capability
- task assignment
- attempt count limit
- outcome code
- no clinical targeting
- call result
- stop on refusal

## 28.3 `WAITLIST`

필수:

- waitlist eligibility
- slot availability
- contact order rule
- consent
- first-accept rule
- double-booking prevention
- result linkage

## 28.4 `PARTNER_REFERRAL`

필수:

- partner ID
- unique QR/code
- placement confirmation
- compensation contract
- result source
- removal/expiry
- no patient data sharing

## 28.5 `TRACKED_PRINT`

필수:

- distribution location ID
- batch ID
- QR/code
- quantity
- placed/removed date
- cost
- policy-approved copy

금지:

```text
추적 없는 대량 전단
배포 수량만 성과로 표시
```

---

# 29. Result Collection

Channel Execution은 다음 결과를 Measurement에 전달한다.

```text
execution attempts
delivery counts
task completion
tracking verification
attributed bookings
completed appointments
cancellation/no-show
actual spend
complaint/refusal
policy incident
operational burden
```

## Result Source

```text
provider webhook
provider polling
normalized appointment
payment
manual verified result
staff task result
partner code
booking source code
```

## Source 상태

```text
VERIFIED
PARTIAL
UNVERIFIED
MISSING
CONFLICTING
STALE
```

---

# 30. Privacy / Retention

## Core

- 환자 이름·전화·이메일·진단·의무기록을 Execution Package에 저장하지 않는다.
- 직접 연락은 기존 적법한 CRM 또는 Connector 내부 최소 처리.
- LOOFIO는 aggregate 또는 tokenized target reference를 우선한다.
- Export와 Staff Task는 목적 제한과 만료.
- 로그에 메시지 본문·연락처·Secret을 남기지 않는다.

## Retention 후보

| 데이터 | 기본 정책 후보 |
|---|---|
| Execution Package | 장기 감사 |
| Attempt / Event | 장기 감사 |
| Provider Reference | 필요한 기간 |
| Target aggregate | 장기 가능 |
| Tokenized assignment | 실험+법정/정책 기간 |
| Direct-contact export | 매우 짧은 만료 |
| Delivery webhook raw payload | 정규화 후 단기 |
| Secret / OAuth token | Secret Manager, DB 평문 금지 |

실제 기간은 법·보안 정책 문서에서 확정한다.

---

# 31. Provider-neutral Port

```text
validate_capability()
preview()
execute()
get_status()
cancel()
fetch_cost()
fetch_delivery_events()
fetch_outcome_events()
```

## Connector가 결정하지 않는 것

- Strategy
- Playbook
- Target rationale
- Budget policy
- Experiment
- Measurement interpretation
- Quality Result

## Connector가 책임지는 것

- Provider DTO
- Request mapping
- Authentication
- Idempotency
- Rate limit
- Retry
- Provider reference
- Error normalization
- Delivery/result normalization

---

# 32. Capability Contract

```json
{
  "channel_type": "SMS",
  "provider": "provider_x",
  "execution_modes": [
    "COPY_EXPORT",
    "APPROVED_CONNECTOR"
  ],
  "supports_preview": true,
  "supports_idempotency": true,
  "supports_cancel_before_send": true,
  "supports_delivery_event": true,
  "supports_click_event": false,
  "supports_cost_sync": true,
  "supports_test_mode": true,
  "policy_status": "not_connected"
}
```

Capability를 코드에서 가정하지 않고 런타임에 검증한다.

---

# 33. Failure Isolation

```text
Recommendation Package 성공
→ Execution Package 실패
```

여도 앞선 분석 기록을 삭제하지 않는다.

```text
Execution Attempt 실패
→ 다른 Attempt 가능
→ Package 상태·Event 보존
```

Provider 장애가:

- Opportunity
- Cause
- Strategy
- Playbook
- Experiment Definition

을 rollback하지 않는다.

---

# 34. API 후보

## 현재 유지

```text
POST  /api/v1/recommendations/{recommendationId}/actions
GET   /api/v1/recommendations/{recommendationId}/actions
GET   /api/v1/businesses/{businessId}/actions
GET   /api/v1/actions/{actionId}
PATCH /api/v1/actions/{actionId}
POST  /api/v1/actions/{actionId}/results
```

## Execution Package Preview

```text
POST /api/v1/actions/{actionId}/execution-packages/preview
```

## Persistence

```text
POST /api/v1/actions/{actionId}/execution-packages
GET  /api/v1/actions/{actionId}/execution-packages
GET  /api/v1/execution-packages/{executionPackageId}
POST /api/v1/execution-packages/{executionPackageId}/approve
POST /api/v1/execution-packages/{executionPackageId}/schedule
POST /api/v1/execution-packages/{executionPackageId}/execute
POST /api/v1/execution-packages/{executionPackageId}/cancel
GET  /api/v1/execution-packages/{executionPackageId}/events
GET  /api/v1/execution-packages/{executionPackageId}/attempts
```

## Human Tasks

```text
GET  /api/v1/businesses/{businessId}/execution-tasks
PATCH /api/v1/execution-tasks/{taskId}
```

## Connector

```text
GET  /api/v1/businesses/{businessId}/channel-capabilities
POST /api/v1/businesses/{businessId}/channel-connections
DELETE /api/v1/businesses/{businessId}/channel-connections/{id}
```

모두 아직 proposal이다.

---

# 35. DB 후보

```text
execution_packages
execution_package_versions
execution_targets
execution_assets
execution_approvals
execution_attempts
execution_events
execution_tasks
execution_tracking_contracts
execution_budget_records
execution_cost_records
execution_provider_references
execution_outcome_links
channel_connections
channel_capabilities
export_jobs
```

## 일반 컬럼

```text
tenant_id
business_id
action_id
recommendation_package_id
experiment_id
version
status
mode
channel_type
provider
source_hash
created_at
approved_at
started_at
completed_at
cancelled_at
```

---

# 36. Determinism과 Audit

동일 Package 생성 입력:

```text
Action
Recommendation Package version
Playbook Instance version
Experiment Definition version
Channel Capability version
Execution Assembler version
as_of
```

동일 Preview 결과.

실제 Attempt는 시간·Provider 결과에 따라 달라진다.

Audit 필수:

```text
who
what
when
approved scope
attempt
provider reference
cost
status
cancel
result linkage
```

---

# 37. Error Contract

```text
EXECUTION_PACKAGE_INPUT_REQUIRED
EXECUTION_PACKAGE_POLICY_REVIEW_REQUIRED
EXECUTION_PACKAGE_APPROVAL_REQUIRED
EXECUTION_PACKAGE_EXPIRED
EXECUTION_PACKAGE_IMMUTABLE
EXECUTION_TARGET_INVALID
EXECUTION_ASSET_NOT_APPROVED
EXECUTION_TRACKING_REQUIRED
EXECUTION_TRACKING_NOT_VERIFIED
EXECUTION_BUDGET_REQUIRED
EXECUTION_BUDGET_EXCEEDED
EXECUTION_CHANNEL_NOT_AVAILABLE
EXECUTION_CONNECTOR_NOT_CONNECTED
EXECUTION_IDEMPOTENCY_CONFLICT
EXECUTION_PROVIDER_TIMEOUT
EXECUTION_PROVIDER_RATE_LIMIT
EXECUTION_PROVIDER_REJECTED
EXECUTION_STATUS_UNKNOWN
EXECUTION_CANCEL_NOT_SUPPORTED
EXECUTION_RESULT_SOURCE_REQUIRED
TENANT_SCOPE_MISMATCH
PII_FIELD_REJECTED
UNSUPPORTED_EXECUTION_VERSION
EXECUTION_INTERNAL_ERROR
```

---

# 38. 테스트 전략

## Current Action Compatibility

- approved Recommendation only
- owner/admin/marketer
- planned→in_progress→completed/cancelled
- replay/idempotent Action creation
- Result only after completed
- existing API unchanged

## Package

- mode/channel/status
- approval hash
- target/privacy
- tracking
- budget
- schedule
- assets
- result source

## Idempotency / Retry

- same key same payload
- same key different payload conflict
- timeout verify-before-retry
- provider duplicate prevention
- max attempts

## State

- valid transitions
- partial success
- failure
- cancel
- expire
- supersede
- Action mapping

## Channel

- online/offline matrix
- connector capability
- staff task
- export expiry
- partner tracking

## Security

- tenant/business
- patient PII
- consent
- Secret leakage
- export audit
- cross-tenant code collision

## Measurement

- delivery vs outcome
- attributed vs incremental
- actual spend
- result source
- complaint/guardrail
- Experiment linkage

---

# 39. 로컬 구현 Backlog

```text
CE-001 Execution mode/channel/role enums
CE-002 Execution Package schema
CE-003 State machine
CE-004 Approval hash/expiry
CE-005 Target/privacy contract
CE-006 Asset contract
CE-007 Tracking contract
CE-008 Budget/cost contract
CE-009 Idempotency
CE-010 Attempt/Event schema
CE-011 Human Task schema
CE-012 Outcome linkage
CE-013 Current Action adapter
CE-014 Preview API
CE-015 Persistence proposal
CE-016 Connector Port
CE-017 Capability contract
CE-018 Export/audit
CE-019 Cancel/kill switch
CE-020 Fixtures/regression
CE-021 ADR/current status update
```

---

# 40. 첫 구현 순서

## Step 1 — Manual Execution Package

현재 Manual Action을 구조화한다.

```text
Action
→ Execution Package mode=MANUAL
→ Tracking/Owner/Schedule/Result Source
```

## Step 2 — Staff-operated Task

```text
FRONT_DESK
CAPACITY_REVIEW
DATA_AUDIT
```

부터 시작한다.

## Step 3 — Copy Export

PII 없는 Asset·Tracking 자료부터.

## Step 4 — Provider-neutral Port

실제 Provider 없이 Fake Connector Contract 테스트.

## Step 5 — Approved Connector 1개

Pilot·정책·보안 검토 후 별도 결정.

---

# 41. 완료조건

Channel Execution v1 완료조건:

1. 실행 수준 5개
2. Channel Taxonomy
3. Action과 Execution 상태 분리
4. Execution Package/Attempt/Event
5. 승인 Scope Hash와 만료
6. 대상·Asset·Tracking
7. Budget·Cost
8. Idempotency·Retry
9. Partial failure·Unknown status
10. Cancel/Recall 한계
11. 온라인·오프라인 계약
12. Result Event 연결
13. Privacy·Retention
14. Provider-neutral Port
15. Failure isolation
16. 현재 Manual Action 호환
17. 자동 실행 MVP 금지
18. tenant/PII 안전
19. 회귀 테스트
20. 코드 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 42. 구현 연결

통합 Backlog·Data Schema·API Contract가 완료됐다.

첫 구현 범위:

```text
CE-001~CE-007
CE-009~CE-014
CE-020~CE-021
```

`APPROVED_CONNECTOR`와 `BOUNDED_AUTOMATION`은 M9 이전에 구현하지 않는다.
