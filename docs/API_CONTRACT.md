# LOOFIO API Contract v1

## 1. 상태

이 문서는 **API 호환성과 리소스 경계 계약**을 정의한다.

아직 백엔드 프레임워크, 인증 공급자, 실제 endpoint 세부 구현은 확정되지 않았다.

따라서 아래 리소스 경로는 v1 설계 기준이며 실제 구현 시 OpenAPI 문서로 고정한다.

---

# 2. API 원칙

Base:

```text
/api/v1
```

핵심 리소스 후보:

```text
/businesses
/imports
/opportunities
/recommendations
/actions
/measurements
```

API는 내부 테이블 구조를 그대로 노출하지 않는다.

---

# 3. Resource Rules

## Business

```text
GET    /api/v1/businesses/{businessId}
PATCH  /api/v1/businesses/{businessId}
```

## Imports

```text
POST   /api/v1/businesses/{businessId}/imports
GET    /api/v1/businesses/{businessId}/imports/{importId}
```

Appointment CSV의 구현 endpoint는 다음과 같다.

```text
POST   /api/v1/businesses/{businessId}/imports/appointments/inspect
POST   /api/v1/businesses/{businessId}/imports/appointments/preview
POST   /api/v1/businesses/{businessId}/imports/appointments
GET    /api/v1/businesses/{businessId}/imports/{importId}
GET    /api/v1/businesses/{businessId}/imports/appointments/mappings
POST   /api/v1/businesses/{businessId}/imports/appointments/mappings
```

저장 endpoint는 `multipart/form-data`의 `file`과 `Idempotency-Key` 헤더를 요구한다.
동일 tenant, business, key에 같은 파일과 같은 CSV 매핑을 다시 보내면 기존 import 결과를 반환하고, 파일 또는 매핑이 다르면 `IDEMPOTENCY_CONFLICT`를 반환한다.
유효하지 않은 행이 하나라도 있으면 예약 데이터를 부분 저장하지 않는다.

`inspect`는 CSV 헤더와 결정론적 alias 규칙만 사용해 열 매핑 제안을 반환한다. 제안은 저장되거나 적용되기 전에 사용자가 확인해야 한다.
매핑은 tenant/business 범위의 이름 있는 프로필로 저장하며, `preview`와 저장 요청의 multipart `mapping_id`로 재사용한다. 매핑은 `appointment_id`, `visit_start_at`, `offering_name`, `status`를 반드시 연결해야 한다.
평문 전화번호·이메일 등의 예상 밖 개인정보 열은 자동 매핑하거나 원본 이력에 보관하지 않는다.

## Opportunities

```text
GET    /api/v1/businesses/{businessId}/opportunities
GET    /api/v1/businesses/{businessId}/opportunities/{opportunityId}
```

Opportunity 생성은 기본적으로 backend detector job의 결과다.

클라이언트가 임의 수치를 넣어 Opportunity를 생성하는 endpoint는 두지 않는다.

## Metrics

```text
GET    /api/v1/businesses/{businessId}/metrics/appointments
```

이 endpoint는 저장된 Appointment를 deterministic하게 집계한 Observation을 반환한다.
`actual_revenue`는 `completed` 상태의 `paid_amount` 합계만 의미하며, 예상 매출이나 Opportunity 추정값이 아니다.
`start_at`, `end_at`을 지정할 때는 UTC offset을 포함한 ISO-8601 값을 사용한다.

## Detector Candidates

```text
GET    /api/v1/businesses/{businessId}/detectors/low-demand-slots
GET    /api/v1/businesses/{businessId}/detectors/revenue-gaps
GET    /api/v1/businesses/{businessId}/detectors/cancellation-hotspots
GET    /api/v1/businesses/{businessId}/detectors/dormant-customers?as_of_date=YYYY-MM-DD
GET    /api/v1/businesses/{businessId}/detectors/service-demand-gaps
```

LowDemandSlot은 같은 요일의 관측된 2시간 슬롯과 비교해 상대 예약 수요가 낮은 후보를 반환한다.
최소 8주 관측과 `DemandIndex <= 0.65`가 필요하다. 반환값은 Observation 후보이며 Opportunity, 예상 매출, Recommendation을 의미하지 않는다.

RevenueGap은 LowDemandSlot 후보의 주간 예약 격차를 같은 요일 비교 시간대의 완료 결제금액 표본으로 환산한다. 완료 결제 표본이 최소 5건인 경우에만 50~100% 회복 시나리오의 월간 범위를 반환한다. 이 값은 Estimate이며 실제 손실·보장 매출·인과효과·ROI가 아니다. capacity 데이터가 없으므로 Capacity Gap을 계산하지 않는다.

CancellationHotspot은 요일·2시간 슬롯·Offering 조합에서 `cancelled + no_show` 예약 이탈률이 사업장 전체 이탈률의 1.5배 이상인 Observation 후보를 반환한다. 해당 조합의 예약 표본은 최소 15건이어야 한다. 결과는 원인, 고객 의도, 실제 손실, Recommendation이나 외부 실행을 뜻하지 않는다.

DormantCustomer는 필수 `as_of_date` 기준으로 가명 customer token의 마지막 완료 방문 이후 경과일을 계산한다. 개인 방문 간격을 우선하고, 표본이 부족하면 동일 Offering 고객군, 그다음 사업장 전체 고객군의 중앙 재방문 간격을 사용한다. 경과일이 해당 기준의 1.3배 이상이면 재방문 지연 Observation 후보로 반환한다. 이는 이탈·고객 의도·실제 손실을 뜻하지 않으며, 원문 연락처나 고객 메시지·외부 실행을 포함하지 않는다.

ServiceDemandGap은 Offering의 전체 예약 비중과 관측된 요일·2시간 슬롯의 예약 비중을 비교한다. 최소 8주 관측, Offering 예약 20건, 슬롯 예약 15건, 비교 기준 예약 5건을 충족한 뒤 슬롯 비중이 전체 비중의 50% 이하일 때만 상대 수요 저하 Observation 후보로 반환한다. 영업시간·capacity·실제 매출·원인·인과관계·Recommendation을 의미하지 않는다.

## Opportunities

```text
POST   /api/v1/businesses/{businessId}/opportunities/refresh
GET    /api/v1/businesses/{businessId}/opportunities
```

`refresh`는 tenant/business 범위의 Detector 후보를 Opportunity로 생성하거나 갱신한다. 현재 `low-demand-revenue-gap-v2`는 예약 수요 Observation과 같은 요일 비교 시간대의 RevenueGap Estimate를 결합한다. `cancellation-hotspot-v1`과 `service-demand-gap-v1`은 Observation 전용 Opportunity로 함께 갱신된다. `as_of_date`를 명시하면 `dormant-customer-v1`도 갱신된다. 과거 `low-demand-slot-v1` Opportunity는 재해석하지 않고 보존한다. 응답은 Observation, 가정 기반 Estimate, limitations, detector version, score, confidence를 분리한다.
Estimate는 실제 매출이나 보장값이 아니며, `Recommendation`이나 외부 실행을 포함하지 않는다.

## Recommendations

```text
POST   /api/v1/opportunities/{opportunityId}/recommendations/draft
GET    /api/v1/opportunities/{opportunityId}/recommendations
POST   /api/v1/recommendations/{recommendationId}/decisions
```

`draft`는 저장된 Opportunity의 Observation·Estimate·limitations만 이용해 재현 가능한 Recommendation 초안을 만들거나 기존 초안을 반환한다. LowDemand·RevenueGap은 수동 시간대 실험 가설을, CancellationHotspot·ServiceDemandGap은 수동 운영 검토를, DormantCustomer는 가명 코호트 수준의 수동 재방문 기록 검토만 제안한다. DormantCustomer Recommendation에는 개별 customer token·연락처·메시지 대상이 포함되지 않는다. 이 요청 및 `approved` 결정은 외부 채널 실행을 만들지 않는다.
Recommendation 초안과 결정은 `owner`, `admin`, `marketer` 역할만 생성할 수 있으며 `viewer`는 조회만 할 수 있다.

## Actions

```text
POST   /api/v1/recommendations/{recommendationId}/actions
GET    /api/v1/recommendations/{recommendationId}/actions
GET    /api/v1/businesses/{businessId}/actions
GET    /api/v1/actions/{actionId}
PATCH  /api/v1/actions/{actionId}
```

Action은 `approved` Recommendation에서만 생성한다. 현재 구현은 사람이 수행할 `manual` Action 계획과 상태 이력만 저장하며, 고객 메시지·광고·쿠폰·외부 채널을 호출하지 않는다.
Action 상태는 `planned → in_progress → completed` 또는 `planned/in_progress → cancelled`로만 변경할 수 있다. 완료·취소 상태는 다시 열 수 없으며, 상태 변경은 actor와 메모를 포함한 이력으로 보관한다.
사업장 Action 목록은 최신 실행/예정 시각 순으로 반환하며, active tenant 밖의 Action은 반환하지 않는다.

## Measurements

```text
POST   /api/v1/actions/{actionId}/results
GET    /api/v1/actions/{actionId}/results
GET    /api/v1/actions/{actionId}/measurements
```

`results`는 완료된 Action에 사람이 기록하는 실행 요약, 측정 기간, 선택적 실제 지출 및 메모다. 실제 매출은 이 입력값으로 받지 않고 저장된 Appointment로만 측정한다.
`measurements`는 Result의 측정 기간과 같은 길이의 직전 1~4주 창을 baseline으로 사용해 예약·완료·취소·실제 완료 매출의 관찰값과 단순 차이를 반환한다. `observed`와 `baseline_average`의 건수는 음수가 아니며, `change_from_baseline`은 기준선보다 낮을 때 음수가 될 수 있는 변화량이다. 이는 인과효과나 Incremental Revenue가 아니다. method version과 limitations를 응답에 포함한다.

---

# 4. ID Contract

리소스 ID는 client에게 **opaque string**으로 취급된다.

내부적으로 UUID를 사용하더라도 client가 UUID 구조나 생성 규칙에 의존하면 안 된다.

표시용 ID가 존재할 수 있다.

예:

```text
OPP-20260813-000134
```

표시용 ID와 내부 PK의 의미를 혼합하지 않는다.

---

# 5. Time Contract

API timestamp는 ISO-8601 offset 포함 형식을 사용한다.

예:

```text
2026-08-13T18:30:00+09:00
```

서버 내부 저장은 `timestamptz`를 기준으로 한다.

business timezone은 별도 속성으로 유지한다.

날짜/시간을 timezone 없는 문자열로 전송하지 않는다.

---

# 6. Money Contract

금액은 float로 의미를 전달하지 않는다.

권장 JSON:

```json
{
  "amount": "490000.00",
  "currency": "KRW"
}
```

실제 매출과 예상 기회를 반드시 구분한다.

```text
actual_revenue
estimated_value
incremental_estimate
```

을 같은 필드로 합치지 않는다.

---

# 7. Opportunity Contract

Opportunity 응답은 최소 다음 의미 계층을 유지한다.

```json
{
  "id": "opaque-id",
  "type": "LOW_DEMAND_SLOT",
  "status": "open",
  "score": 82.0,
  "confidence": 0.74,
  "observation": [],
  "estimate": {
    "value_low": {"amount": "380000.00", "currency": "KRW"},
    "value_high": {"amount": "460000.00", "currency": "KRW"}
  },
  "limitations": [],
  "detector": {
    "code": "LOW_DEMAND_SLOT",
    "version": "v1"
  }
}
```

`observation`의 숫자를 AI 생성 텍스트만으로 제공하지 않는다.

---

# 8. Recommendation Contract

권장 구조:

```json
{
  "id": "opaque-id",
  "opportunity_id": "opaque-id",
  "version": 1,
  "hypothesis": "possible cause",
  "action_type": "promotion",
  "channel": "kakao",
  "target_segment": {},
  "expected_effect": {
    "low": "5",
    "high": "12",
    "unit": "bookings"
  },
  "confidence": 0.68,
  "explanation": "..."
}
```

Expected Effect는 estimate다.

실제 결과는 Action Result/Measurement에서만 반환한다.

현재 모든 Recommendation은 `manual` channel만 제공한다. LowDemand·RevenueGap은 `manual_time_slot_offer_test`, CancellationHotspot은 `manual_cancellation_flow_review`, DormantCustomer는 `manual_revisit_cohort_review`, ServiceDemandGap은 `manual_offering_slot_review`를 사용한다. 대상 고객과 혜택을 설정하거나 외부 채널을 실행하지 않으며, Action에서는 내부 실행 계획과 예정 예산만 기록할 수 있다.

---

# 9. Decision Contract

```json
{
  "decision": "approved",
  "reason_code": null,
  "reason_text": null,
  "modified_payload": {}
}
```

허용 값:

```text
approved
rejected
modified
later
```

이 값은 장기 학습 데이터이므로 의미를 임의 변경하지 않는다.

---

# 10. Error Contract

일관된 구조를 사용한다.

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

권장 범주:

```text
VALIDATION_ERROR
AUTHENTICATION_REQUIRED
FORBIDDEN
NOT_FOUND
CONFLICT
IDEMPOTENCY_CONFLICT
RATE_LIMITED
EXTERNAL_PROVIDER_ERROR
INTERNAL_ERROR
```

내부 stack trace나 secret을 API 응답으로 반환하지 않는다.

---

# 11. Validation Contract

서버가 최종 검증 책임을 가진다.

클라이언트 validation만 믿지 않는다.

예:

- business 접근 권한
- datetime
- status enum
- money
- target segment
- action type
- decision
- idempotency key

---

# 12. Idempotency

중복 실행 비용이 큰 POST는 Idempotency 지원을 우선한다.

대상 후보:

- import 생성
- 외부 Action 실행
- 결제/외부 provider sync
- 캠페인 실행

헤더 예:

```text
Idempotency-Key: <client-generated-key>
```

동일 key + 동일 scope에서 payload가 다르면 conflict 처리한다.

---

# 13. Pagination

목록 API는 cursor pagination을 우선한다.

예:

```json
{
  "data": [],
  "page": {
    "next_cursor": "...",
    "has_more": true
  }
}
```

구현 시 offset을 사용하더라도 공개 contract에서 pagination 의미를 안정적으로 유지한다.

---

# 14. Tenant / Authorization Contract

모든 business resource는 인증된 사용자의 tenant 권한 안에서만 접근 가능하다.

client가 `tenant_id`를 임의로 바꿔 다른 조직 데이터에 접근할 수 있는 구조를 만들지 않는다.

권한 실패는 존재 여부를 과도하게 노출하지 않는 정책을 고려한다.

---

# 15. Versioning

`/api/v1`의 breaking change는 금지한다.

Non-breaking 예:

- optional response field 추가
- 새로운 endpoint 추가
- 새로운 capability 추가

주의가 필요한 변경:

- 새로운 enum 값 추가
- pagination behavior 변경
- validation 강화

Breaking 예:

- 필드 삭제
- 필드 타입 변경
- 의미 변경
- required field 추가
- status 의미 변경

Breaking이 필요하면 `/api/v2` 또는 명시적 migration 전략을 사용한다.

---

# 16. Contract Tests

API 구현은 다음 contract test를 둔다.

- auth/tenant
- success response schema
- validation errors
- enum
- money
- timezone
- idempotency
- pagination
- backward compatibility

OpenAPI가 추가되면 CI에서 schema diff를 검사하는 방향을 권장한다.

---

# 17. 아직 미확정

다음은 구현 시 결정한다.

- OAuth/JWT/session 방식
- API Gateway
- rate limit 수치
- upload 방식(presigned URL 등)
- async job polling/webhook
- OpenAPI generation tool

이 항목을 임의로 본 계약의 확정 사실처럼 취급하지 않는다.
