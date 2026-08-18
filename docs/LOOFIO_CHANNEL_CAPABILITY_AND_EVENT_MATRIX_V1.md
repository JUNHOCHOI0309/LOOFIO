---
title: "LOOFIO Channel Capability and Event Matrix v1"
version: "1.0"
date: "2026-08-18"
status: "채널별 실행·추적·결과 계약 매핑"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
depends_on:
  - "LOOFIO_CHANNEL_EXECUTION_V1.md"
  - "LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md"
  - "LOOFIO_MEASUREMENT_FRAMEWORK_V1.md"
---

# LOOFIO Channel Capability and Event Matrix v1

## 1. 문서 목적

이 문서는 각 온라인·오프라인 채널에서 허용되는 실행 수준, 승인, Tracking, 비용, 취소, Result Source와 Event를 한 표준으로 연결한다.

---

# 2. 상태 표기

```text
CURRENT
→ 현재 main에서 구현

V1
→ Decision Intelligence 첫 구현 목표

PILOT
→ 별도 Pilot 이후

FUTURE
→ 장기

BLOCKED
→ 현재 정책상 미허용
```

---

# 3. 전체 Capability Matrix

| Channel | 현재 | V1 목표 | 장기 | Tracking | Result Source | 비용 |
|---|---|---|---|---|---|---|
| `MANUAL_OPERATION` | CURRENT Manual Action | 구조화 Package | - | ACTION_ID | manual verified + Appointment | staff time |
| `FRONT_DESK` | 수동 기록 가능 | STAFF_OPERATED | - | ACTION_ID / manual tag | rebooking + completed Appointment | staff time |
| `CAPACITY_CONFIGURATION` | 수동 | STAFF_OPERATED | approved config connector | config version | capacity verification | staff time |
| `DATA_AUDIT` | 수동 | STAFF_OPERATED | - | audit ID | import/Opportunity regeneration | staff time |
| `TRACKING_SETUP` | 없음 | STAFF_OPERATED | - | test event | linkage verification | staff/tool cost |
| `BOOKING_PAGE` | 수동 외부 작업 | MANUAL / STAFF_OPERATED | APPROVED_CONNECTOR | source code / URL | booking + completed Appointment | setup/staff |
| `WEBSITE` | 없음 | COPY_EXPORT / MANUAL | APPROVED_CONNECTOR | UTM / URL | web + booking | setup/media |
| `NAVER_PLACE` | 없음 | COPY_EXPORT / MANUAL | provider feasibility 검토 | source URL/code | booking source | staff/media |
| `KAKAO` | 없음 | COPY_EXPORT | APPROVED_CONNECTOR | provider/action ID | delivery + booking | message |
| `SMS` | 없음 | COPY_EXPORT | APPROVED_CONNECTOR | provider message ID | delivery + booking | message |
| `EMAIL` | 없음 | COPY_EXPORT | APPROVED_CONNECTOR | provider message ID / UTM | delivery/click/booking | message/tool |
| `SEARCH_ADS` | 없음 | BLOCKED | PILOT approved connector | campaign/ad/click ID | spend + conversion | media |
| `SOCIAL_ADS` | 없음 | BLOCKED | PILOT approved connector | campaign/ad/click ID | spend + conversion | media |
| `ORGANIC_SOCIAL` | 없음 | COPY_EXPORT / MANUAL | APPROVED_CONNECTOR 후보 | UTM / post ID | click + booking | staff |
| `STAFF_CALLBACK` | 없음 | STAFF_OPERATED | - | task/action ID | call outcome + booking | staff |
| `WAITLIST` | 없음 | STAFF_OPERATED after domain | connector 후보 | action/source code | booking + completed | staff/message |
| `PARTNER_REFERRAL` | 없음 | STAFF_OPERATED | - | partner code / QR | completed booking | partner/staff |
| `TRACKED_PRINT` | 없음 | COPY_EXPORT / STAFF_OPERATED | - | QR / batch / location | scan + booking | print/staff |

---

# 4. 승인 Matrix

| Channel / Mode | 승인 단위 | 기본 승인 역할 | 재승인 Trigger |
|---|---|---|---|
| Manual operation | Single Action | owner/admin/marketer | scope/period 변경 |
| Staff task | Single batch/window | owner/admin/marketer | 대상·스크립트·기간 변경 |
| Copy export | Single export | owner/admin/marketer | row count/field set 변경 |
| Direct contact export | Single export | owner/admin 제한 | 대상/동의/field 변경 |
| Paid media | Single campaign | owner 기본 | 예산·target·creative·기간 변경 |
| Approved connector | Single action/batch | owner/admin 정책 | payload hash 변경 |
| Bounded automation | Automation policy | FUTURE owner | 정책 version/limit 변경 |

---

# 5. Tracking Matrix

| Channel | 필수 Tracking | 검증 |
|---|---|---|
| Front Desk | action ID + offer result field | test staff record |
| Staff Callback | task/action ID + call outcome | test task |
| Booking Page | unique URL/source code | test booking |
| Website | UTM + booking source | test navigation/booking |
| Naver Place | tracked destination/source | test path |
| Kakao/SMS/Email | provider message ID + booking source | test message if available |
| Search/Social Ads | campaign/ad/click/conversion ID | test conversion |
| Partner | partner code or QR | test scan/booking |
| Print | batch/location QR | test scan |
| No Action | monitoring metric + review trigger | scheduled review |

Tracking `none`은 실행형 Package를 차단한다.

---

# 6. Event Source Matrix

| Event | Source 우선순위 |
|---|---|
| Attempt sent | Connector / manual user |
| Delivery accepted | Provider |
| Delivery delivered | Provider |
| Staff task completed | Assigned user |
| Link clicked | Provider/web analytics |
| QR scanned | Redirect/analytics |
| Booking created | Normalized booking/appointment |
| Appointment completed | Normalized Appointment |
| Revenue | completed Appointment paid amount / payment |
| Spend | Provider billing / manual verified |
| Complaint | Provider/manual support record |
| Consent withdrawn | CRM/provider/manual verified |
| Partner placement | Staff task/photo reference |
| Tracking verified | test event |

---

# 7. Event Normalization Matrix

## Provider Delivery 상태

| Provider status | 내부 Event |
|---|---|
| accepted / queued | `DELIVERY_ACCEPTED` |
| sent | `ATTEMPT_SENT` |
| delivered | `DELIVERY_DELIVERED` |
| bounced | `DELIVERY_BOUNCED` |
| rejected | `DELIVERY_REJECTED` |
| unknown / timeout | `DELIVERY_UNKNOWN` |

## Human Task 상태

| Task 상태 | 내부 Event |
|---|---|
| assigned | `TASK_ASSIGNED` |
| started | `TASK_STARTED` |
| done | `TASK_COMPLETED` |
| skipped | `TASK_SKIPPED` |
| failed | `TASK_FAILED` |

## Appointment 상태

| Appointment | 내부 Event |
|---|---|
| booked | `BOOKING_CREATED` |
| completed | `APPOINTMENT_COMPLETED` |
| cancelled | `APPOINTMENT_CANCELLED` |
| no_show | `NO_SHOW_RECORDED` |

---

# 8. Result Linkage Matrix

| Tracking | 내부 결과 연결 |
|---|---|
| ACTION_ID | Action 또는 source metadata 일치 |
| BOOKING_SOURCE_CODE | Appointment source field 일치 |
| UNIQUE_URL / UTM | Web event → booking session/source |
| PARTNER_CODE | Appointment source/partner mapping |
| QR | Redirect ID → booking source |
| PROVIDER_MESSAGE_ID | Delivery → click/source → booking |
| MANUAL_SOURCE_TAG | 사용자 검증 + source note |

`manual source tag`는 Evidence Grade·Source Quality가 낮을 수 있다.

---

# 9. Cost Matrix

| Channel | Cost Components |
|---|---|
| Manual/Staff | staff time |
| Copy Export | staff time, tool |
| SMS/Kakao/Email | message, platform, staff |
| Search/Social Ads | media, platform, creative, staff |
| Booking/Website | setup, development, staff |
| Partner | partner compensation, print, staff |
| Print | design, production, distribution, staff |
| Benefit Offering | benefit, variable service, staff |

모든 비용이 0원이라고 가정하지 않는다.

---

# 10. Retry / Cancel Matrix

| Channel | Retry | Cancel / Recall |
|---|---|---|
| Manual Task | 담당자 재배정·재시도 | 미수행 Task 취소 |
| Front Desk | 다음 eligible visit | 이미 안내한 내용 회수 불가 |
| Staff Callback | attempt cap 안에서 | 향후 Task 취소, 완료 통화 회수 불가 |
| Booking Config | 수정 재적용 | 이전 config rollback 가능 여부 |
| Message Connector | retryable provider errors만 | 송신 전 가능, 전달 후 회수 불가 |
| Email | provider 정책 | 일부 예약 취소, 전달 후 회수 불가 |
| Ads | API retry | pause/cancel future spend |
| Partner | staff follow-up | 자료 회수 Task |
| Print | 재배포 금지 기본 | 배포물 회수 제한 |
| Tracking Setup | test 재시도 | config rollback |

---

# 11. Playbook→Channel Matrix

| Playbook | Primary Channel | Support Channel |
|---|---|---|
| Data Audit | DATA_AUDIT | MANUAL_OPERATION |
| Tracking Setup | TRACKING_SETUP | BOOKING_PAGE / provider |
| Capacity Review | CAPACITY_CONFIGURATION | MANUAL_OPERATION |
| Offering Slot Reallocation | BOOKING_PAGE | FRONT_DESK |
| Booking Availability Audit | BOOKING_PAGE | WEBSITE / NAVER_PLACE |
| Revisit Cohort | external CRM manual / future message | BOOKING_PAGE |
| Front Desk Rebooking | FRONT_DESK | BOOKING_PAGE |
| Booking Path Visibility | BOOKING_PAGE | WEBSITE / NAVER_PLACE |
| Funnel Friction | BOOKING_PAGE / WEBSITE | TRACKING_SETUP |
| Non-discount Value Add | manual approved channel | BOOKING_PAGE |
| Local Partnership | PARTNER_REFERRAL | TRACKED_PRINT / QR |
| No Action Monitoring | MANUAL_OPERATION | Measurement |

---

# 12. Current MVP Adapter

현재 `manual-action-v1`을 다음처럼 해석한다.

```text
mode
→ MANUAL

channel
→ 기존 Recommendation channel 문자열

execution_package
→ 아직 없음

status
→ Action status

tracking
→ execution_notes 또는 future structured field

result
→ manual-action-result-v1
```

첫 구현에서는:

```text
기존 Action response 변경 없음
+
optional Execution Package preview
```

를 권장한다.

---

# 13. Matrix 완료조건

1. 모든 Core Channel의 현재/목표 상태
2. Approval
3. Tracking
4. Result Source
5. Cost
6. Retry
7. Cancel
8. Event normalization
9. Playbook mapping
10. Current Action adapter
