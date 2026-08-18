---
title: "LOOFIO API Contract — Decision Intelligence v1"
version: "1.0"
date: "2026-08-18"
status: "Preview-first and additive API proposal; not yet implemented"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
base_path: "/api/v1"
current_api_contract: "docs/API_CONTRACT.md"
initial_domain: "Hospital Appointment MVP"
initial_opportunity: "LOW_DEMAND_SLOT"
depends_on:
  - "API_CONTRACT.md"
  - "DECISION_REGISTER_V2.md"
  - "LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md"
  - "LOOFIO_IMPLEMENTATION_BACKLOG_V1.md"
  - "LOOFIO_DECISION_INPUT_CONTRACT_V1.md"
  - "LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md"
  - "LOOFIO_STRATEGY_ENGINE_V1.md"
  - "LOOFIO_ACTION_PLAYBOOK_V1.md"
  - "LOOFIO_EXPERIMENT_DESIGN_V1.md"
  - "LOOFIO_RECOMMENDATION_PACKAGE_V2.md"
  - "LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md"
  - "LOOFIO_MEASUREMENT_FRAMEWORK_V1.md"
  - "LOOFIO_CHANNEL_EXECUTION_V1.md"
---

# LOOFIO API Contract — Decision Intelligence v1

## 1. 문서 목적

이 문서는 현재 FastAPI `/api/v1` 계약을 유지하면서 Decision Intelligence를 다음 방식으로 추가하는 API 기준을 정의한다.

```text
Preview-first
→ Deterministic Contract 검증
→ Manual Action 호환
→ Additive Persistence
→ 승인 기반 Channel Execution
```

대상 파이프라인:

```text
Opportunity
→ Decision Context
→ Cause Analysis
→ Strategy Comparison
→ Playbook Resolution / Instance
→ Experiment Definition
→ Recommendation Package
→ Recommendation Quality
→ User Decision
→ Existing Manual Action
→ Execution Package
→ Measurement
```

이 문서의 신규 Endpoint는 현재 구현된 API가 아니다.

```text
현재 Source of Truth
→ FastAPI route
→ Pydantic schema
→ API tests
→ docs/API_CONTRACT.md

이 문서
→ 다음 구현을 위한 확정 API proposal
```

---

# 2. 현재 API Snapshot

현재 구현은 다음 리소스를 제공한다.

```text
auth
tenant
business
appointment import / mapping
metrics
detectors
opportunities
recommendations
actions
results
measurements
```

현재 핵심 계약:

```text
POST /businesses/{businessId}/opportunities/refresh
GET  /businesses/{businessId}/opportunities

POST /opportunities/{opportunityId}/recommendations/draft
GET  /opportunities/{opportunityId}/recommendations
POST /recommendations/{recommendationId}/decisions

POST  /recommendations/{recommendationId}/actions
GET   /recommendations/{recommendationId}/actions
GET   /businesses/{businessId}/actions
GET   /actions/{actionId}
PATCH /actions/{actionId}

POST /actions/{actionId}/results
GET  /actions/{actionId}/results
GET  /actions/{actionId}/measurements
```

현재 계약을 제거하거나 의미를 변경하지 않는다.

---

# 3. 가장 중요한 API 결정

## 3.1 클라이언트 계산 결과를 신뢰하지 않는다

클라이언트가 다음을 Request Body로 제출해 Source of Truth로 만들 수 없다.

```text
Opportunity Observation
Cause Candidate Score
Strategy Score
Playbook Fit Score
Experiment Evidence Grade
Recommendation Quality Score
Measurement Result
```

클라이언트가 제출할 수 있는 것은 다음과 같다.

```text
사업자가 제공한 Decision Context 값
Diagnostic Answer
허용된 Strategy / Playbook 선택 Override
기간·담당자·예산·성공 기준 같은 Runtime 값
사용자 Decision
Manual Result
```

서버는 Opportunity를 직접 로드하고 각 deterministic stage를 다시 계산한다.

## 3.2 Canonical Product Preview

제품 UI의 기본 Preview Endpoint:

```text
POST /api/v1/opportunities/{opportunityId}/recommendation-packages/preview
```

이 Endpoint가 서버 내부에서 다음을 계산한다.

```text
Decision Context
Cause
Strategy
Playbook
Experiment
Recommendation Package
Quality
```

Stage별 Preview Endpoint는 디버깅·점진적 UI·입력 보완에 사용한다.

## 3.3 이전 `decision-packages/preview` 초안은 사용하지 않는다

과거 설계에서 제안된:

```text
/opportunities/{id}/decision-packages/preview
```

는 정식 API가 아니다.

Canonical 명칭:

```text
/opportunities/{id}/recommendation-packages/preview
```

## 3.4 Persistence는 immutable resource와 revision

```text
Snapshot
Run
Definition
Package Version
Quality Result
Measurement Run
```

을 직접 수정하지 않는다.

수정은 새 Revision 또는 새 Run을 만든다.

---

# 4. 공통 API 원칙

## 4.1 Base

```text
/api/v1
```

## 4.2 Content Type

```text
application/json; charset=utf-8
```

기존 Appointment CSV Endpoint만 `multipart/form-data`를 유지한다.

## 4.3 Pydantic

신규 Request Model:

```python
model_config = ConfigDict(extra="forbid")
```

를 기본으로 한다.

알 수 없는 필드를 조용히 무시하지 않는다.

## 4.4 Direct Resource Response

현재 API와 마찬가지로 단일 Resource는 별도 `data` Envelope 없이 직접 반환한다.

```json
{
  "id": "...",
  "contract_version": "...",
  "status": "..."
}
```

Error만 공통 Error Envelope를 사용한다.

## 4.5 List Response

현재 Array Response는 변경하지 않는다.

신규 Persistence List는 Cursor Envelope를 사용한다.

```json
{
  "items": [],
  "next_cursor": null,
  "limit": 50
}
```

---

# 5. 인증과 Tenant

## 5.1 현재 방식

```text
Signed session cookie
→ server-side session
→ active tenant
```

모든 Decision Intelligence API는 `require_active_tenant_user`와 동일한 인증 경계를 사용한다.

## 5.2 Out-of-scope Resource

다른 Tenant의 Resource ID를 요청하면:

```text
404 NOT_FOUND
```

를 기본으로 사용한다.

존재 여부를 노출하지 않는다.

## 5.3 Provider Webhook

향후 Provider Webhook은 Browser Session을 사용하지 않는다.

```text
Provider signature
Timestamp / replay protection
Provider account mapping
Event dedupe key
```

가 필요하다.

---

# 6. 역할과 권한

현재 역할:

```text
owner
admin
marketer
viewer
```

## 6.1 권한 Matrix

| 작업 | owner | admin | marketer | viewer |
|---|:---:|:---:|:---:|:---:|
| 현재·저장된 분석 조회 | ✅ | ✅ | ✅ | ✅ |
| Stage / Package Preview 실행 | ✅ | ✅ | ✅ | ❌ |
| Context Snapshot·Run 생성 | ✅ | ✅ | ✅ | ❌ |
| Diagnostic Answer | ✅ | ✅ | ✅ | ❌ |
| Package Decision | ✅ | ✅ | ✅ | ❌ |
| Manual Action 생성 | ✅ | ✅ | ✅ | ❌ |
| Manual/Staff Execution Package | ✅ | ✅ | ✅ | ❌ |
| 비용 없는 Manual 실행 승인 | ✅ | ✅ | 정책에 따라 | ❌ |
| Budget-bearing 실행 승인 | ✅ | 정책에 따라 | 기본 ❌ | ❌ |
| Connector 연결·삭제 | ✅ | ✅ | ❌ | ❌ |
| Hard Fail Override | ❌ | ❌ | ❌ | ❌ |

## 6.2 Business Execution Policy

향후 다음 범위를 Business Policy로 제한할 수 있다.

```text
marketer budget approval limit
allowed channel
manual-only
connector allowed
maximum batch size
```

Policy가 없으면 더 보수적인 기본값을 사용한다.

---

# 7. Request ID

Request Header:

```text
X-Request-ID
```

- 선택 입력.
- 없으면 서버가 UUID를 생성한다.
- Error Envelope의 `request_id`에 항상 포함한다.
- 신규 API는 성공 Response Header에도 같은 값을 반환하는 것을 권장한다.
- Request ID는 Idempotency Key가 아니다.

---

# 8. Idempotency

## 8.1 Header

```text
Idempotency-Key
```

권장 형식:

```text
8~128자
A-Z a-z 0-9 . _ : -
```

## 8.2 필수 Endpoint

다음 쓰기 요청에서 필수다.

```text
Snapshot / Run / Instance / Definition / Package 생성
Decision
Revision
Approval
State Transition
Execution
Cancel
Measurement Persistence / Recalculation
Channel Connection
```

Preview는 저장·부작용이 없으므로 요구하지 않는다.

## 8.3 Scope

```text
active tenant
+ route operation
+ parent resource
+ Idempotency-Key
```

## 8.4 Replay

같은 Key + 같은 canonical Request Hash:

```text
기존 결과 반환
HTTP 200
replayed = true
```

최초 생성:

```text
HTTP 201
replayed = false
```

같은 Key + 다른 Request Hash:

```text
HTTP 409
IDEMPOTENCY_CONFLICT
```

## 8.5 Async Execution

Connector 실행 최초 요청:

```text
HTTP 202
```

Replay는 기존 Attempt/Command를 반환한다.

## 8.6 Retention

정확한 Idempotency Record 보존 기간은 운영·개인정보 정책에서 확정한다.

안전한 Client Retry Window보다 짧아서는 안 된다.

---

# 9. Preview Contract

## 9.1 공통 Response Metadata

```json
{
  "preview": {
    "preview_id": "PRV_xxx",
    "persisted": false,
    "input_hash": "sha256...",
    "generated_at": "2026-08-18T12:00:00+09:00",
    "as_of": "2026-08-18T12:00:00+09:00",
    "engine_versions": {}
  }
}
```

## 9.2 Preview ID

Preview ID는 deterministic hash 기반 표시용 ID다.

```text
fetch 가능한 저장 Resource ID가 아님
```

## 9.3 Request 원칙

각 Stage Preview는 다음을 받는다.

```text
contract_version
as_of
decision_context
diagnostic_answers(optional)
selection_overrides(optional)
runtime_overrides(optional)
```

다음은 받지 않는다.

```text
client-computed Cause score
client-computed Strategy score
client-computed Quality result
client-computed Measurement
```

## 9.4 Stage Recompute

Stage Preview는 필요한 upstream을 서버에서 다시 계산한다.

예:

```text
Strategy Preview
→ Opportunity load
→ Decision Context validate
→ Cause calculate
→ Strategy calculate
```

Client가 이전 Cause Response 전체를 다시 제출할 필요가 없다.

---

# 10. 공통 Value Contract

## 10.1 ID

ID는 opaque string이다.

Client가 UUID 구조에 의존하지 않는다.

## 10.2 Version

필드 이름을 구분한다.

```text
contract_version
engine_version
score_version
definition_version
validator_version
revision
```

단순 `version: 1`처럼 의미가 불명확한 필드를 신규 계약에서 피한다.

## 10.3 Time

```text
ISO-8601 + UTC offset
```

예:

```text
2026-08-18T14:00:00+09:00
```

Timezone 없는 datetime은 422다.

## 10.4 Date

날짜 의미만 필요한 경우:

```text
YYYY-MM-DD
```

## 10.5 Money

```json
{
  "amount": "120000.00",
  "currency": "KRW"
}
```

JSON float를 사용하지 않는다.

## 10.6 Field Status

```json
{
  "status": "known",
  "value": 72,
  "source": {
    "type": "derived_metric",
    "reference": "cohort-query-v1"
  },
  "observed_at": "2026-08-18T10:00:00+09:00"
}
```

지원:

```text
known
unknown
not_applicable
conflicting
stale
restricted
```

```text
status = unknown, value = null
```

과:

```text
status = known, value = 0
```

을 구분한다.

---

# 11. Pagination

신규 List Endpoint:

```text
limit
cursor
status(optional)
created_after(optional)
created_before(optional)
```

## 기본값

```text
limit = 50
max = 100
```

## Cursor

- opaque string.
- Client가 내용을 해석하지 않는다.
- 기본 정렬은 `created_at DESC, id DESC`.
- Event는 `occurred_at ASC, id ASC`를 기본으로 할 수 있다.

## Response

```json
{
  "items": [],
  "next_cursor": "opaque-or-null",
  "limit": 50
}
```

---

# 12. Optimistic Concurrency

Immutable Resource는 Update하지 않는다.

상태 변경·Decision·Revision Request는 다음을 포함한다.

```text
expected_revision
expected_status
```

불일치:

```text
409 RESOURCE_VERSION_CONFLICT
```

예:

```json
{
  "expected_revision": 2,
  "decision": "approved"
}
```

승인 후 Scope Hash가 달라지면:

```text
409 APPROVED_SCOPE_CHANGED
```

---

# 13. Error Envelope

현재 API v1의 Error Envelope를 유지한다.

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "요청을 처리할 수 없습니다.",
    "details": [],
    "request_id": "..."
  }
}
```

## HTTP Mapping

| HTTP | 의미 |
|---:|---|
| 400 | 잘못된 명령·형식 외 domain error |
| 401 | 로그인 필요 |
| 403 | 역할·active tenant·policy 권한 부족 |
| 404 | Resource 없음 또는 Tenant 밖 |
| 409 | 상태·revision·idempotency·중복 충돌 |
| 410 | 사용 종료된 외부 Link 등 선택적 사용 |
| 413 | Payload/Export 제한 초과 |
| 422 | Pydantic·시간·Money·PII·Domain validation |
| 429 | API 또는 Provider Rate Limit |
| 502 | Provider invalid upstream response |
| 503 | Store·Provider 일시 불가 |

Internal Stack·Secret·Raw Provider Error·PII를 반환하지 않는다.

---

# 14. Domain Error Code

## 공통

```text
AUTHENTICATION_REQUIRED
ACTIVE_TENANT_REQUIRED
FORBIDDEN
NOT_FOUND
VALIDATION_ERROR
PII_FIELD_REJECTED
TENANT_SCOPE_MISMATCH
IDEMPOTENCY_CONFLICT
RESOURCE_VERSION_CONFLICT
RESOURCE_SUPERSEDED
RESOURCE_EXPIRED
```

## Decision Context

```text
DECISION_CONTEXT_INVALID
DECISION_CONTEXT_STALE
DECISION_CONTEXT_CONFLICTING
UNSUPPORTED_DECISION_CONTEXT_VERSION
```

## Cause

```text
CAUSE_ANALYSIS_NOT_READY
CAUSE_ANALYSIS_BLOCKED_BY_DATA_QUALITY
CAUSE_ANALYSIS_INPUT_REQUIRED
CAUSE_ANALYSIS_STORAGE_UNAVAILABLE
```

## Strategy

```text
STRATEGY_INPUT_INSUFFICIENT
STRATEGY_POLICY_REVIEW_REQUIRED
STRATEGY_ECONOMICS_INPUT_REQUIRED
NO_EXECUTABLE_STRATEGY
STRATEGY_STORAGE_UNAVAILABLE
```

## Playbook

```text
PLAYBOOK_NOT_FOUND
PLAYBOOK_NOT_APPLICABLE
PLAYBOOK_INPUT_REQUIRED
PLAYBOOK_POLICY_REVIEW_REQUIRED
PLAYBOOK_CONTRAINDICATED
PLAYBOOK_BLOCKED
PLAYBOOK_DEPRECATED
NO_APPLICABLE_PLAYBOOK
```

## Experiment

```text
EXPERIMENT_INPUT_REQUIRED
EXPERIMENT_PRIMARY_METRIC_REQUIRED
EXPERIMENT_SUCCESS_THRESHOLD_REQUIRED
EXPERIMENT_STOP_CONDITION_REQUIRED
EXPERIMENT_ASSIGNMENT_INVALID
EXPERIMENT_IMMUTABLE_AFTER_START
EXPERIMENT_RESULT_SOURCE_REQUIRED
EXPERIMENT_STORAGE_UNAVAILABLE
```

## Recommendation Package / Quality

```text
RECOMMENDATION_PACKAGE_SOURCE_INVALID
RECOMMENDATION_PACKAGE_SOURCE_STALE
RECOMMENDATION_PACKAGE_INPUT_REQUIRED
RECOMMENDATION_PACKAGE_POLICY_REVIEW_REQUIRED
RECOMMENDATION_PACKAGE_QUALITY_FAILED
RECOMMENDATION_PACKAGE_IMMUTABLE
RECOMMENDATION_PACKAGE_STORAGE_UNAVAILABLE

RECOMMENDATION_QUALITY_HARD_FAILED
RECOMMENDATION_QUALITY_SCORE_FAILED
```

## Execution

```text
EXECUTION_APPROVAL_REQUIRED
EXECUTION_APPROVED_SCOPE_CHANGED
EXECUTION_TRACKING_REQUIRED
EXECUTION_TRACKING_NOT_VERIFIED
EXECUTION_BUDGET_REQUIRED
EXECUTION_BUDGET_EXCEEDED
EXECUTION_CHANNEL_NOT_AVAILABLE
EXECUTION_CONNECTOR_NOT_CONNECTED
EXECUTION_PROVIDER_TIMEOUT
EXECUTION_PROVIDER_RATE_LIMIT
EXECUTION_PROVIDER_REJECTED
EXECUTION_STATUS_UNKNOWN
EXECUTION_CANCEL_NOT_SUPPORTED
EXECUTION_STORAGE_UNAVAILABLE
```

## Measurement

```text
MEASUREMENT_RESULT_SOURCE_REQUIRED
MEASUREMENT_RESULT_SOURCE_CONFLICT
MEASUREMENT_WINDOW_INVALID
MEASUREMENT_BASELINE_UNAVAILABLE
MEASUREMENT_COMPARISON_INVALID
MEASUREMENT_ECONOMICS_INCOMPLETE
MEASUREMENT_INVALIDATED
MEASUREMENT_STORAGE_UNAVAILABLE
```

---

# 15. Decision Context Preview

```text
POST /api/v1/opportunities/{opportunityId}/decision-context/preview
```

## Request

```json
{
  "contract_version": "decision-input-v1",
  "as_of": "2026-08-18T12:00:00+09:00",
  "decision_context": {
    "goal": {
      "primary_goal": "FILL_LOW_DEMAND_SLOTS",
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
      }
    }
  }
}
```

## Response

```json
{
  "preview": {},
  "opportunity_id": "OPP_01",
  "decision_context": {},
  "readiness": {
    "level": "D2",
    "version": "decision-readiness-v1",
    "available_capabilities": [],
    "blocked_capabilities": [],
    "missing_requirements": []
  },
  "validation": {
    "status": "valid",
    "warnings": []
  }
}
```

---

# 16. Cause Preview

```text
POST /api/v1/opportunities/{opportunityId}/cause-analyses/preview
```

Request는 Decision Context Preview와 같은 Context를 사용하며 선택적 Diagnostic Answer를 추가할 수 있다.

```json
{
  "contract_version": "cause-preview-v1",
  "as_of": "...",
  "decision_context": {},
  "diagnostic_answers": [
    {
      "question_code": "CQ_CAP_01",
      "answer": true,
      "source": {
        "type": "user_entered",
        "reference": "preview-form"
      }
    }
  ]
}
```

Response:

```text
preview
decision_context summary
cause_analysis
├─ status
├─ version
├─ candidates
├─ recommended_diagnostics
├─ limitations
└─ next_stage
```

---

# 17. Strategy Preview

```text
POST /api/v1/opportunities/{opportunityId}/strategy-runs/preview
```

Response:

```text
cause summary
strategy run
├─ candidates
├─ selected_strategy
├─ alternative_comparisons
├─ DATA_COLLECTION / NO_ACTION plan
└─ playbook candidate IDs
```

Client가 `selected_strategy`를 강제 제출하지 않는다.

선택 Override가 필요하면:

```json
{
  "selection_overrides": {
    "strategy_family": "DISCOVERABILITY"
  }
}
```

서버가 해당 전략이 `ELIGIBLE` 또는 허용된 limitation 상태인지 검증한다.

불가능한 Override:

```text
422 SELECTED_STRATEGY_NOT_ELIGIBLE
```

---

# 18. Playbook Resolution Preview

```text
POST /api/v1/opportunities/{opportunityId}/playbook-resolutions/preview
```

Request:

```json
{
  "contract_version": "playbook-resolution-preview-v1",
  "as_of": "...",
  "decision_context": {},
  "selection_overrides": {
    "strategy_family": "RETENTION_REACTIVATION",
    "playbook_id": "PB_LOW_DEMAND_REVISIT_COHORT_V1"
  },
  "runtime": {
    "owner_role": "marketer",
    "planned_start_at": "...",
    "planned_end_at": "..."
  }
}
```

Response:

```text
applicability_results
selected_playbook
playbook_instance
missing_inputs
blockers
fit score
```

Playbook Definition의 canonical ID와 version/hash를 포함한다.

---

# 19. Experiment Preview

```text
POST /api/v1/opportunities/{opportunityId}/experiments/preview
```

Request는 Context와 선택 Override, Runtime Experiment 값을 받는다.

```json
{
  "contract_version": "experiment-preview-v1",
  "as_of": "...",
  "decision_context": {},
  "selection_overrides": {
    "strategy_family": "RETENTION_REACTIVATION",
    "playbook_id": "PB_LOW_DEMAND_REVISIT_COHORT_V1"
  },
  "experiment_overrides": {
    "planned_start_at": "...",
    "planned_end_at": "...",
    "success_threshold": {
      "threshold_type": "ABSOLUTE_DELTA_AT_LEAST",
      "value": 3
    }
  }
}
```

서버가 다음을 계산한다.

```text
Method
Assignment
Grade Ceiling
Precision Status
Primary Metric
Comparison
Guardrails
Stop Conditions
Attribution
```

---

# 20. Recommendation Package Preview — Canonical

```text
POST /api/v1/opportunities/{opportunityId}/recommendation-packages/preview
```

## Request

```json
{
  "contract_version": "decision-intelligence-preview-v1",
  "as_of": "2026-08-18T12:00:00+09:00",
  "decision_context": {},
  "diagnostic_answers": [],
  "selection_overrides": {
    "strategy_family": null,
    "playbook_id": null
  },
  "runtime_overrides": {
    "owner_role": "marketer",
    "planned_start_at": "2026-08-20T00:00:00+09:00",
    "planned_end_at": "2026-09-03T00:00:00+09:00",
    "budget_cap": {
      "status": "known",
      "value": {
        "amount": "120000.00",
        "currency": "KRW"
      }
    },
    "success_threshold": null
  }
}
```

## Response

```json
{
  "preview": {},
  "decision_context": {},
  "cause_analysis": {},
  "strategy_run": {},
  "playbook_resolution": {},
  "experiment_definition": {},
  "recommendation_package": {
    "status": "READY_FOR_REVIEW",
    "package_type": "EXECUTION"
  },
  "quality": {
    "status": "PASSED",
    "total_score": 82,
    "hard_failures": [],
    "warnings": []
  }
}
```

## Status

Preview Response의 Package 상태:

```text
NEEDS_DATA
NEEDS_POLICY_REVIEW
QUALITY_REJECTED
READY_FOR_REVIEW
```

Preview 자체는 승인되지 않는다.

---

# 21. Preview 단계의 최소 구현 순서

```text
1. recommendation-packages/preview
2. cause-analyses/preview
3. strategy-runs/preview
4. playbook-resolutions/preview
5. experiments/preview
6. decision-context/preview
```

코드 내부는 하위 단계부터 구현하지만 제품 UI에서는 end-to-end Preview를 먼저 사용할 수 있다.

---

# 22. Persistence — Decision Context

## Create Snapshot

```text
POST /api/v1/opportunities/{opportunityId}/decision-context/snapshots
```

Header:

```text
Idempotency-Key
```

Response:

```json
{
  "snapshot": {},
  "replayed": false
}
```

최초:

```text
201
```

Replay:

```text
200
```

Snapshot은 immutable이다.

## List / Get

```text
GET /opportunities/{opportunityId}/decision-context/snapshots
GET /decision-context-snapshots/{snapshotId}
```

---

# 23. Persistence — Cause

## Create

```text
POST /opportunities/{opportunityId}/cause-analyses
```

Request:

```json
{
  "contract_version": "create-cause-analysis-v1",
  "decision_context_snapshot_id": "DCTX_01",
  "as_of": "..."
}
```

Client가 Candidate나 Score를 제출하지 않는다.

## Diagnostic Answer

```text
POST /cause-analyses/{causeAnalysisId}/diagnostic-answers
```

Answer는 append-only다.

답변 후 재분석은:

```text
새 Cause Analysis Run 생성
```

으로 처리한다.

기존 Run을 수정하지 않는다.

---

# 24. Persistence — Strategy

```text
POST /opportunities/{opportunityId}/strategy-runs
```

Request:

```json
{
  "contract_version": "create-strategy-run-v1",
  "decision_context_snapshot_id": "DCTX_01",
  "cause_analysis_id": "CAUSE_01",
  "as_of": "..."
}
```

Client가 Strategy Score를 제출하지 않는다.

---

# 25. Persistence — Playbook Instance

```text
POST /strategy-runs/{strategyRunId}/playbook-instances
```

Request:

```json
{
  "contract_version": "create-playbook-instance-v1",
  "selected_strategy_family": "RETENTION_REACTIVATION",
  "selected_playbook_id": "PB_LOW_DEMAND_REVISIT_COHORT_V1",
  "runtime": {
    "owner_role": "marketer",
    "planned_start_at": "...",
    "planned_end_at": "..."
  }
}
```

서버가 Applicability와 Fit을 다시 검증한다.

수정:

```text
POST /playbook-instances/{id}/revisions
```

으로 새 immutable revision을 만든다.

---

# 26. Persistence — Experiment

```text
POST /playbook-instances/{id}/experiments
```

필수:

```text
Primary Metric 1개
Treatment
Comparison 또는 허용된 Diagnostic/Hold 대체 계약
Success
Stop
기간
Tracking/Result Source
```

State:

```text
POST /experiments/{id}/state-transitions
```

Request:

```json
{
  "expected_status": "READY_FOR_APPROVAL",
  "expected_revision": 1,
  "to_status": "APPROVED",
  "note": null
}
```

`RUNNING` 이후 immutable field 변경은 409다.

---

# 27. Persistence — Recommendation Package

## Canonical Create

```text
POST /opportunities/{opportunityId}/recommendation-packages
```

제품 UI는 모든 upstream row를 직접 조립하지 않는다.

Request는 다음 중 하나를 사용한다.

### Existing Snapshot 사용

```json
{
  "contract_version": "create-recommendation-package-v2",
  "decision_context_snapshot_id": "DCTX_01",
  "selection_overrides": {},
  "runtime_overrides": {},
  "persist_upstream": true
}
```

### Inline Context + Persist

```json
{
  "contract_version": "create-recommendation-package-v2",
  "decision_context": {},
  "selection_overrides": {},
  "runtime_overrides": {},
  "persist_upstream": true
}
```

Server가 Cause·Strategy·Applicability·Experiment를 계산하고 create-or-get한다.

Client가 source Run ID를 직접 조합하는 advanced Endpoint는 v1 Public API에 두지 않는다.

## Response

```json
{
  "package": {},
  "package_version": {},
  "quality": {},
  "sources": {},
  "replayed": false
}
```

Package가 Quality에 실패해도 저장할 수 있다.

```text
status = QUALITY_REJECTED
```

Action 생성은 불가하다.

---

# 28. Package Revision과 Decision

## Revision

```text
POST /recommendation-packages/{packageId}/revisions
```

Request:

```json
{
  "expected_revision": 1,
  "modifications": {
    "planned_start_at": "...",
    "planned_end_at": "...",
    "owner_role": "marketer",
    "budget_cap": null
  }
}
```

허용된 필드만 수정 가능하다.

Observation·Source·Policy Hard Constraint는 수정할 수 없다.

## Decision

```text
POST /recommendation-package-versions/{versionId}/decisions
```

```json
{
  "expected_revision": 2,
  "expected_status": "READY_FOR_REVIEW",
  "decision": "approved",
  "reason_code": null,
  "reason_text": null,
  "modifications": null
}
```

`modified`는 새 revision을 생성한다.

---

# 29. Quality

```text
GET /recommendation-package-versions/{versionId}/quality
```

Quality Result는 immutable이다.

재검증:

```text
POST /recommendation-package-versions/{versionId}/revalidations
```

새 Validator Version 또는 같은 Version의 source hash 변경이 있을 때 새 Result를 만든다.

Hard Fail을 `PASSED`로 바꾸는 Override Endpoint는 두지 않는다.

---

# 30. Package에서 기존 Action 생성

```text
POST /recommendation-package-versions/{versionId}/actions
```

필수:

```text
Package decision = approved
Package status = APPROVED
Quality = PASSED
Hard Fail = 0
Experiment approval 또는 Package Type별 대체 계약
```

Response는 현재 `ActionCreateResult`와 호환되는 구조를 권장한다.

내부적으로:

```text
Package
→ legacy adapter
→ current Recommendation
→ current Action
```

을 사용할 수 있다.

---

# 31. Execution Package

## Preview

```text
POST /actions/{actionId}/execution-packages/preview
```

## Create

```text
POST /actions/{actionId}/execution-packages
```

첫 M8 지원:

```text
MANUAL
COPY_EXPORT
STAFF_OPERATED
```

미지원:

```text
APPROVED_CONNECTOR
BOUNDED_AUTOMATION
```

미지원 Mode 제출:

```text
422 EXECUTION_CHANNEL_NOT_AVAILABLE
```

---

# 32. Execution Approval

```text
POST /execution-packages/{id}/approvals
```

Request:

```json
{
  "expected_status": "READY_FOR_APPROVAL",
  "approved_scope_hash": "...",
  "approval_type": "SINGLE_ACTION",
  "expires_at": "..."
}
```

서버가 계산한 Scope Hash와 일치해야 한다.

Budget-bearing 실행은 권한 정책을 추가 확인한다.

---

# 33. Execution State·Attempt·Cancel

## State Transition

```text
POST /execution-packages/{id}/state-transitions
```

Manual/Staff 상태 변경에 사용한다.

## Connector Execute — Future

```text
POST /execution-packages/{id}/execute
```

```text
202 Accepted
```

Response:

```json
{
  "attempt": {
    "id": "EXATT_01",
    "status": "PENDING"
  },
  "replayed": false
}
```

## Cancel

```text
POST /execution-packages/{id}/cancel-requests
```

취소 결과:

```text
CANCELLED_FULL
CANCELLED_FUTURE_ONLY
CANCEL_REQUESTED_PROVIDER
CANNOT_RECALL
CANCEL_FAILED
```

이미 전달된 결과를 삭제하지 않는다.

---

# 34. Staff Task

```text
GET /businesses/{businessId}/execution-tasks
POST /execution-tasks/{taskId}/state-transitions
```

Task State:

```text
assigned
in_progress
completed
skipped
failed
cancelled
```

Task 결과 Payload에는 환자 PII를 넣지 않는다.

---

# 35. Execution Event

```text
GET /execution-packages/{id}/events
GET /execution-packages/{id}/attempts
```

Event 정렬:

```text
occurred_at ASC
id ASC
```

Provider Webhook은 append-only Event를 만들며:

```text
tenant + dedupe_key
```

로 중복을 방지한다.

---

# 36. Measurement

## 현재 유지

```text
GET /actions/{actionId}/measurements
```

현재 method version:

```text
same-window-prior-four-weeks-v2
```

Response 의미를 변경하지 않는다.

## Framework Preview

```text
POST /actions/{actionId}/measurements/framework-preview
```

현재 Result·Appointment를 읽어:

```text
method = SAME_WINDOW_PRIOR_FOUR_WEEKS_V2
evidence_grade = C
incremental_estimate = null
```

인 새 Framework 표현을 반환한다.

## Persist

```text
POST /experiments/{experimentId}/measurements
```

현재 Result Source가 닫힌 후 호출한다.

## History

```text
GET /actions/{actionId}/measurement-history
```

저장된 Measurement Run을 최신 계산 시각 순으로 조회한다. 현재 legacy GET 결과를 자동 backfill하지 않는다.

## Recalculation

```text
POST /measurements/{measurementId}/recalculations
```

기존 결과를 수정하지 않고 새 Run을 만든다.

---

# 37. Measurement Response 의미

```json
{
  "id": "MEAS_01",
  "measurement_version": "measurement-framework-v1",
  "method": {
    "code": "SAME_WINDOW_PRIOR_FOUR_WEEKS_V2",
    "version": "2"
  },
  "status": "COMPLETED",
  "decision": "NO_CLEAR_EFFECT",
  "evidence_grade": "C",
  "precision_status": "LOW",
  "actual_result": {},
  "baseline": {},
  "observed_delta": {},
  "attributed_result": null,
  "incremental_estimate": null,
  "economics": {
    "status": "partial",
    "net_contribution_estimate": null
  },
  "limitations": []
}
```

Actual·Estimate·Delta·Incremental을 같은 field로 합치지 않는다.

---

# 38. CORS·Router 구현 정렬

현재 `main.py`는:

```text
allow_methods = GET, POST
```

로 설정되어 있지만 현재 API에는:

```text
PATCH /actions/{actionId}
```

가 존재한다.

Browser Cross-Origin 호출을 지원하려면 최소 다음 정렬이 필요하다.

```text
GET
POST
PATCH
DELETE
OPTIONS
```

신규 API는 상태 변경을 대부분 `POST .../state-transitions`로 설계했지만, 현재 PATCH와 향후 Channel Connection DELETE를 위해 CORS 설정을 갱신한다.

허용 Header:

```text
Content-Type
Idempotency-Key
X-Request-ID
```

Provider Webhook Signature Header는 Browser CORS와 별도 처리한다.

## Router 분리 권장

```text
api/app/api/routes/
├─ decision_context.py
├─ cause_analyses.py
├─ strategy_runs.py
├─ playbooks.py
├─ experiments.py
├─ recommendation_packages.py
├─ execution.py
└─ measurements_v2.py
```

하나의 `decisioning.py`에 모든 Route를 넣지 않는다.

---

# 39. Store / Application 경계

Route가 직접 다음을 계산하지 않는다.

```text
Cause
Strategy
Playbook Fit
Quality Score
Measurement
```

권장:

```text
Route
→ Application Use Case
→ Domain Engine / Port
→ Store
```

Preview도 Store를 전혀 사용하지 않는 것이 아니라 Opportunity·현재 Domain Data를 읽을 수 있다.

저장 부작용만 만들지 않는다.

---

# 40. HTTP Status 요약

| 작업 | 최초 | Replay | 주요 실패 |
|---|---:|---:|---|
| Preview | 200 | 200 | 404/422/503 |
| Persist Create | 201 | 200 | 409/422/503 |
| Decision / Approval | 201 | 200 | 409/422 |
| State Transition | 200 | 200 | 409 |
| Connector Execute | 202 | 200 | 409/422/429/502/503 |
| Cancel Request | 202 | 200 | 409/422 |
| GET | 200 | N/A | 404/503 |
| DELETE Connection | 204 | 204 | 404/409 |

---

# 41. OpenAPI 규칙

각 신규 Route는 명시적 `operation_id`를 가진다.

예:

```text
preview_recommendation_package
create_recommendation_package
decide_recommendation_package
create_execution_package
create_measurement_run
```

## CI

권장:

```text
OpenAPI snapshot 생성
→ schema diff
→ Breaking change 검사
```

Breaking:

- required field 추가
- field 삭제
- type/meaning 변경
- enum 제거
- status semantics 변경
- error code meaning 변경

Additive:

- optional field
- 새 Endpoint
- 새 enum value가 기존 Client에 안전한 경우
- 새 Warning code

---

# 42. Compatibility

## 유지

```text
현재 /api/v1 Endpoint
현재 Error Envelope
현재 Money/Time 의미
현재 Recommendation Decision
현재 Manual Action
현재 Action Result
현재 Measurement Response
```

## 신규

```text
Preview Endpoint
Cursor List Envelope
Package Revision
Quality Result
Execution Package
Measurement Framework
```

## 금지

```text
현재 /recommendations/draft 삭제
Action FK 의미 즉시 교체
현재 Measurement를 Incremental로 재해석
과거 Recommendation을 Package v2로 자동 변환
```

---

# 43. API 구현 순서

## M1~M5

```text
recommendation-packages/preview
cause-analyses/preview
strategy-runs/preview
playbook-resolutions/preview
experiments/preview
decision-context/preview
```

## M6

```text
Package→Legacy Action
UI Decisions
```

## M7

```text
execution-packages/preview
measurements/framework-preview
```

## M8

```text
Snapshot / Run / Revision Persistence
Cursor List / Get
Package Decision
Manual/Staff Execution
Measurement Run
```

## M9

```text
Channel Connection
Approved Connector
Provider Webhook
```

---

# 44. API Contract Test Matrix

## Common

```text
401 no session
403 active tenant / role
404 cross-tenant
422 extra field / PII / timezone / money
409 idempotency / revision / status
503 store unavailable
```

## Preview

- 같은 입력 → 같은 preview_id·hash·score·status
- 저장 Row 증가 없음
- 외부 실행 없음
- client-computed score field 거부

## Persistence

- 최초 201
- Replay 200 + replayed=true
- 다른 Payload 409
- source ID/version/hash
- immutable revision

## Package / Quality

- 일반 조언 → QUALITY_REJECTED
- Hard Fail → Action 생성 금지
- modified → 새 revision
- stale source → revalidation 필요

## Execution

- approval scope hash
- tracking verified
- budget cap
- duplicate attempt
- partial success
- cancel recall limitation

## Measurement

- current legacy 숫자 불변
- Grade C adapter
- incremental null for Grade C/D
- unknown cost != zero
- result source conflict

---

# 45. 첫 Vertical Slice 완료조건

1. Canonical end-to-end Preview가 동작한다.
2. Opportunity는 server-side로 로드한다.
3. Client-computed Score를 받지 않는다.
4. PII extra field를 거부한다.
5. Cause·Strategy·Playbook·Experiment·Package·Quality가 같은 Source Hash 체인을 가진다.
6. 입력 부족은 구체적인 NEEDS_DATA를 반환한다.
7. 일반 조언은 QUALITY_REJECTED다.
8. Quality-passed Package를 기존 Manual Action으로 연결한다.
9. 기존 Endpoint와 Response 의미가 변하지 않는다.
10. 전체 Backend·Web 회귀가 통과한다.

---

# 46. Definition of Done

본 API Contract 구현 완료 조건:

1. 신규 Pydantic model에 extra forbid 적용
2. Preview Endpoint와 deterministic hash
3. 권한 Matrix
4. Tenant 404
5. PII validation
6. Idempotency semantics
7. Cursor pagination
8. Revision / expected status
9. Stable Error Envelope
10. Source/version/hash
11. Legacy compatibility
12. OpenAPI operation_id
13. Contract tests
14. CORS 정렬
15. Data Schema migration과 FK 정렬
16. CURRENT_IMPLEMENTATION_STATUS 갱신
17. 기존 API_CONTRACT에서 본 문서 링크
18. Planning Index 상태 갱신

---

# 47. 문서 작업 종료 기준

이 문서까지 완료하면 로컬 구현 전 핵심 문서 7개 추가 작업은 완료된다.

다음은 문서 신규 작성보다:

```text
GitHub docs 반영
Governance/current status 정렬
ADR 0020+
로컬 구현 B01부터 시작
```

의 단계다.
