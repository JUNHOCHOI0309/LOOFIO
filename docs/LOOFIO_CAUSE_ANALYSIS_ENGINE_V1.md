---
title: "LOOFIO Cause Analysis Engine v1"
version: "1.0"
date: "2026-08-17"
status: "로컬 구현용 확정 설계안"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
initial_opportunity: "LOW_DEMAND_SLOT"
depends_on:
  - "LOOFIO_OPPORTUNITY_ENGINE_V1.md"
  - "LOOFIO_IMPLEMENTATION_ROADMAP_V2.md"
  - "LOOFIO_DECISION_INPUT_CONTRACT_V1.md"
---

# LOOFIO Cause Analysis Engine v1

## 1. 문서 목적

이 문서는 LOOFIO Opportunity Engine이 발견한 **현상**을 가능한 **원인 가설**로 구조화하는 Cause Analysis 계층의 구현 계약을 정의한다.

현재 Hospital Appointment MVP는 다음 범위까지 구현되어 있다.

```text
Appointment CSV
→ Normalization
→ Metrics
→ Detector
→ Opportunity
→ Evidence / Estimate / Score
→ Deterministic Manual Recommendation
```

현재 Recommendation은 안전한 수동 검토 초안이지만, Opportunity에서 곧바로 행동을 제안하기 때문에 다음 질문을 충분히 다루지 못한다.

```text
이 현상이 데이터 오류는 아닌가
실제 판매 가능한 capacity가 있었는가
Offering과 시간대가 맞지 않았는가
기존 고객의 재방문 문제가 있는가
검색·예약 경로에서 발견되지 않은 것인가
지역·시간대의 수요 자체가 낮은 것인가
```

Cause Analysis는 이 간극을 담당한다.

핵심 원칙:

> Opportunity는 무엇이 관측되었는지를 말한다.
> Cause Analysis는 왜 그런 현상이 발생했을 가능성이 있는지를 가설로 정리한다.
> Cause Candidate는 사실·인과관계·성공 확률이 아니다.

---

# 2. 범위

## 2.1 v1 구현 범위

```text
Domain
→ Hospital Appointment MVP

Opportunity
→ LOW_DEMAND_SLOT

Mode
→ Deterministic

Execution
→ None

AI
→ 사용하지 않음
```

## 2.2 v1 이후 확장 대상

```text
CANCELLATION_HOTSPOT
DORMANT_CUSTOMER
SERVICE_DEMAND_GAP
External Context
AI wording
Persisted Cause Run
User diagnostic answers
```

## 2.3 비범위

Cause Analysis는 다음을 수행하지 않는다.

- 원인 확정
- Strategy 선택
- Playbook 선택
- 고객 대상 선정
- 채널 선택
- 예산 계산
- 콘텐츠 생성
- 외부 실행
- ROI·Incrementality 계산
- 환자 임상정보 분석

---

# 3. 파이프라인 위치

```text
Opportunity
+ Opportunity Evidence
+ Opportunity Limitations
+ Decision Context Snapshot
        ↓
Cause Input Validation
        ↓
Candidate Seeding
        ↓
Evidence / Contradiction Mapping
        ↓
Input Requirement Evaluation
        ↓
Review Priority Score
        ↓
Diagnostic Question Generation
        ↓
Cause Analysis Result
        ↓
Strategy Engine
```

Cause Analysis는 Opportunity의 Observation·Estimate·Score를 수정하지 않는다.

---

# 4. Source of Truth와 입력 경계

## 4.1 Opportunity Source

Cause Analysis는 저장된 Opportunity의 다음 필드를 읽는다.

```text
id
type
status
segment
observation
estimate(optional)
score
scoring.version
confidence
limitations
detector.code
detector.version
first_detected_at
last_detected_at
```

## 4.2 Decision Context Source

`LOOFIO_DECISION_INPUT_CONTRACT_V1.md`의 다음 영역을 사용한다.

```text
Metadata
GoalContext
BusinessConstraintContext
OperationalCapacityContext
OfferingEligibilityContext
CustomerActivationContext
ChannelCapabilityContext
HistoricalActionContext
ExternalContextSummary
PolicyConstraintContext
MeasurementCapabilityContext
AssumptionRegistry
DecisionReadiness
```

## 4.3 Raw Data 접근 금지

Cause Analysis가 직접 읽지 않는 것:

```text
raw CSV bytes
raw import rows 전체
환자 이름
전화번호·이메일 원문
진단명
질병·증상
처방
검사 결과
의무기록
상담 원문
다른 tenant 데이터
```

필요한 데이터 품질 정보는 aggregate `DataQualityContext`로 전달한다.

---

# 5. Decision Input Contract v1.1 보완안

`DATA_QUALITY_ARTIFACT`를 안전하게 평가하려면 기존 Decision Input Contract에 다음 aggregate 영역을 additive하게 보완하는 것이 필요하다.

```text
DataQualityContext
├─ import_status
├─ validation_status
├─ source_lineage_available
├─ mapping_profile_version
├─ valid_row_count
├─ rejected_row_count
├─ duplicate_row_count
├─ unknown_status_count
├─ missing_required_field_count
├─ timezone_validation_status
├─ offering_resolution_rate
├─ customer_token_coverage_rate
├─ payment_coverage_rate
├─ data_freshness_at
└─ limitations
```

초기 구현에서는 별도 DB 테이블 없이 현재 import·mapping·Opportunity metadata에서 request 시점에 계산할 수 있다.

상태는 기존 `DecisionField` 규칙을 따른다.

```text
known
unknown
not_applicable
conflicting
stale
restricted
```

---

# 6. 용어

## Observation

현재 데이터로 확인된 현상.

예:

> 최근 12주 화요일 14~16시 예약 발생량이 같은 요일 다른 시간대 중앙값보다 낮았다.

## Cause Candidate

Observation을 설명할 수 있는 검토 대상 가설.

예:

> 해당 시간대에 Offering을 제공할 capacity가 실제로 없었을 가능성.

## Supporting Evidence

후보를 우선 검토할 근거.

## Contradicting Evidence

후보의 설명력을 낮추는 근거.

## Missing Data

후보를 더 정확하게 평가하기 위해 필요한 정보.

## Diagnostic Question

Missing Data를 사용자 또는 시스템에서 보완하기 위한 구조화 질문.

## Review Priority Score

현재 데이터에서 어떤 Cause Candidate부터 검토할지 정하는 0~100 점수.

다음 의미가 아니다.

```text
원인 발생 확률
성공 확률
매출 가치
인과관계 강도
```

---

# 7. Cause Taxonomy v1

## 7.1 `DATA_QUALITY_ARTIFACT`

실제 사업 문제가 아니라 데이터 누락·중복·매핑·시간대·표본 오류로 현상이 만들어졌을 가능성.

대표 확인:

- import validation
- status mapping
- duplicate
- unknown status
- timezone
- source lineage
- offering resolution
- customer/payment coverage
- stale data

이 Candidate는 모든 Opportunity에서 우선 검토한다.

## 7.2 `CAPACITY_OR_OPERATION_CONSTRAINT`

마케팅 수요 문제가 아니라 직원·공간·장비·영업시간·예약 규칙 때문에 해당 슬롯을 실질적으로 판매할 수 없었을 가능성.

대표 확인:

- business hours
- blackout
- available staff
- eligible staff
- room/equipment
- same-day booking
- booking lead time
- temporary constraints

## 7.3 `OFFER_SLOT_MISMATCH`

Offering의 소요시간·가격대·고객 이용 목적·직원 가용성과 목표 시간대가 맞지 않았을 가능성.

대표 확인:

- Offering별 시간대 분포
- duration
- target slot availability
- Offering share
- eligible staff
- price mode
- historical slot performance

## 7.4 `RETENTION_GAP`

기존 고객이 예상 재방문 시점을 지나 돌아오지 않거나, 재방문 가능 고객군이 목표 슬롯과 연결되지 않은 가능성.

대표 확인:

- token availability
- completed visit history
- revisit interval
- eligible cohort
- offering history
- recent contact
- consent capability

## 7.5 `DISCOVERABILITY_GAP`

수요 가능성은 있으나 매장·Offering·목표 슬롯이 검색·지도·예약 페이지·현장 안내에서 충분히 발견되지 않은 가능성.

대표 확인:

- booking link
- target slot visibility
- map/business profile exposure
- search impressions
- landing availability
- channel capability
- historical exposure action

## 7.6 `DEMAND_DEFICIT`

지역·요일·시간대 자체의 수요가 지속적으로 낮을 가능성.

대표 확인:

- repeated pattern
- observed weeks
- broader weekday comparison
- seasonal comparison
- holiday/weather/event
- search trend
- footfall

외부 Context가 없으면 가설로 유지할 수 있지만 확정할 수 없다.

## 7.7 `CONVERSION_FRICTION`

노출·방문·문의는 존재하지만 예약 완료로 전환되지 않는 가능성.

대표 확인:

- booking page visits
- booking starts
- completed bookings
- inquiry-to-booking
- unavailable slot display
- booking error
- CTA/landing path

Funnel 데이터가 없으면 기본 Candidate가 아니라 조건부 `NEEDS_DATA` Candidate로만 생성한다.

## 7.8 `CHANNEL_MISMATCH`

목표 고객·Offering·시간대와 현재 사용하는 채널의 도달 방식이 맞지 않는 가능성.

대표 확인:

- channel-level attribution
- channel audience
- booking source
- message reach
- paid/organic result
- partner source

채널 성과 데이터가 없으면 평가하지 않는다.

## 7.9 `VALUE_OR_PRICE_FRICTION`

가격·혜택·Offering 설명·가치 전달의 마찰로 예약이 발생하지 않는 가능성.

대표 확인:

- price mode
- structured inquiry category
- conversion by offer
- historical benefit test
- value explanation availability
- policy-safe offer eligibility

Hospital에서는 상담 원문이나 임상정보를 사용하지 않는다.

## 7.10 `CANCELLATION_LEAKAGE`

예약은 발생했지만 취소·노쇼로 목표 슬롯의 사용 가능 capacity가 소실된 가능성.

대표 확인:

- cancelled/no-show
- disruption rate
- cancellation timing
- reminder
- reschedule
- waitlist

`LOW_DEMAND_SLOT`만으로 기본 생성하지 않는다. 동일 구간의 `CANCELLATION_HOTSPOT` 또는 명확한 이탈 근거가 있을 때 조건부로 연결한다.

---

# 8. LOW_DEMAND_SLOT Candidate 정책

## 8.1 항상 Seed하는 Candidate

```text
DATA_QUALITY_ARTIFACT
CAPACITY_OR_OPERATION_CONSTRAINT
OFFER_SLOT_MISMATCH
RETENTION_GAP
DISCOVERABILITY_GAP
DEMAND_DEFICIT
```

Seed는 원인이 존재한다는 뜻이 아니다.

입력 부족 Candidate는 `NEEDS_DATA` 상태로 남는다.

## 8.2 조건부 Candidate

```text
CONVERSION_FRICTION
CHANNEL_MISMATCH
VALUE_OR_PRICE_FRICTION
CANCELLATION_LEAKAGE
```

생성 조건:

| Cause | 생성 조건 |
|---|---|
| `CONVERSION_FRICTION` | booking funnel 또는 inquiry→booking 데이터가 하나 이상 존재 |
| `CHANNEL_MISMATCH` | channel-level exposure/booking/result가 존재 |
| `VALUE_OR_PRICE_FRICTION` | price/value 관련 구조화 지표 또는 과거 실험이 존재 |
| `CANCELLATION_LEAKAGE` | 동일 segment의 cancellation evidence 또는 관련 Opportunity가 존재 |

조건이 충족되지 않으면 Candidate를 생략하거나 `NOT_APPLICABLE`로 저장하지 않고, 필요한 경우 Diagnostic Question으로만 남긴다.

---

# 9. Input Requirement 등급

각 Cause 입력은 세 등급으로 분류한다.

## 9.1 Required (`R`)

Candidate를 평가·점수화하는 데 반드시 필요한 값.

누락·conflicting·restricted이면:

```text
candidate.status = NEEDS_DATA
review_priority_score = null
```

## 9.2 Optional (`O`)

없어도 Candidate를 생성·평가할 수 있지만 Evidence Strength·Data Completeness·Diagnostic 품질을 높인다.

누락 시:

```text
candidate.status 유지
data_completeness 감소
missing_data에 추가 가능
```

## 9.3 Blocking (`B`)

Cause Candidate 자체의 생성에는 필수가 아니지만, 이 Candidate를 근거로 downstream Strategy·Playbook·Recommendation Package를 실행 가능한 상태로 만들 때 반드시 필요한 값.

누락 시:

```text
candidate는 REVIEWABLE 가능
downstream_blockers에 추가
Recommendation Package는 NEEDS_DATA 또는 NEEDS_POLICY_REVIEW
```

예:

```text
RETENTION_GAP 가설 생성
→ consent capability는 Cause 생성에는 필수 아님
→ 실제 고객 연락 Strategy에는 blocking
```

---

# 10. Cause Analysis Run 상태

```text
PENDING
COMPLETED
NEEDS_DATA
BLOCKED_BY_DATA_QUALITY
INVALID_INPUT
FAILED
```

## `COMPLETED`

최소 1개 `REVIEWABLE` Candidate와 구조화 Diagnostic 결과가 존재.

## `NEEDS_DATA`

Candidate는 생성됐지만 Required 입력 부족으로 모두 점수화 불가.

## `BLOCKED_BY_DATA_QUALITY`

critical data quality conflict 때문에 사업 원인 순위가 오해를 만들 가능성이 큼.

예:

```text
timezone conflicting
required status mapping missing
source lineage unavailable
data window invalid
```

이 상태에서도 `DATA_QUALITY_ARTIFACT` Candidate와 해결 질문은 반환한다.

## `INVALID_INPUT`

- Opportunity type 불일치
- tenant/business mismatch
- timezone 없는 timestamp
- contract version 미지원
- 금지 PII field

## `FAILED`

예상하지 못한 내부 오류.

---

# 11. Cause Candidate 상태

```text
REVIEWABLE
NEEDS_DATA
DEPRIORITIZED
NOT_APPLICABLE
BLOCKED
```

## `REVIEWABLE`

Required 입력이 충족되고 점수·근거·한계가 존재.

## `NEEDS_DATA`

Required 입력 부족.

## `DEPRIORITIZED`

강한 반대 근거가 있거나 우선순위가 낮음.

삭제하지 않고 비교 근거로 보존할 수 있다.

## `NOT_APPLICABLE`

명시적 조건상 해당 없음.

예:

```text
customer token 없음
+
customer reactivation 자체가 현재 사업에서 비적용
```

## `BLOCKED`

Critical data quality 문제로 현재 분석에서 평가하면 안 됨.

---

# 12. Output Contract

```json
{
  "id": "CAUSE_RUN_xxx",
  "version": "cause-analysis-v1",
  "status": "COMPLETED",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "opportunity_id": "OPP_01",
  "opportunity_type": "LOW_DEMAND_SLOT",
  "decision_context_snapshot_id": "DCTX_01",
  "generated_at": "2026-08-17T14:00:00+09:00",
  "candidates": [
    {
      "cause_code": "CAPACITY_OR_OPERATION_CONSTRAINT",
      "status": "REVIEWABLE",
      "hypothesis": "목표 슬롯에 실제 판매 가능한 직원·공간·Offering capacity가 제한되었을 가능성",
      "review_priority_score": 78.0,
      "score_version": "cause-priority-v1",
      "evidence_strength": "moderate",
      "supporting_evidence_refs": ["DCTX.operation.slot_capacity_confirmed"],
      "contradicting_evidence_refs": [],
      "required_inputs": [],
      "missing_optional_inputs": ["DCTX.operation.available_service_minutes"],
      "downstream_blockers": [],
      "diagnostic_question_ids": ["CQ_CAP_01"],
      "limitations": [
        "Cause Candidate는 원인 확정 또는 성공 확률이 아닙니다."
      ]
    }
  ],
  "recommended_diagnostics": [],
  "global_limitations": [],
  "next_stage": {
    "strategy_ready": true,
    "blocked_reasons": []
  }
}
```

---

# 13. Cause Priority Score v1

## 13.1 변경 결정

초기 초안의 `Actionability` 요소는 Cause Score에서 제거한다.

이유:

```text
Cause Analysis
→ 왜 그랬을 가능성이 있는가

Strategy Engine
→ 무엇을 할 수 있는가
```

Actionability를 Cause Score에 포함하면 해결하기 쉬운 원인을 실제 근거보다 높게 평가할 수 있다.

## 13.2 구성

```text
Evidence Support        35
Pattern Consistency     20
Data Completeness       20
Contradiction Absence   15
Testability             10
Total                  100
```

## 13.3 계산

각 factor는 0~1이다.

```text
Score
=
Evidence Support × 35
+
Pattern Consistency × 20
+
Data Completeness × 20
+
Contradiction Absence × 15
+
Testability × 10
```

소수점 둘째 자리 반올림.

## 13.4 필수 규칙

- Required 입력이 충족되지 않으면 score는 `null`
- score는 probability가 아님
- factor 계산은 deterministic
- 같은 입력은 같은 score
- score version 저장
- AI가 factor·score 계산 금지

## 13.5 Evidence Strength Label

```text
strong
moderate
weak
insufficient
```

권장 매핑:

```text
strong
→ Evidence Support >= 0.75
→ Data Completeness >= 0.75
→ Required 모두 충족

moderate
→ Evidence Support >= 0.50
→ Required 모두 충족

weak
→ Evidence Support < 0.50
→ Required 모두 충족

insufficient
→ Required 누락
```

---

# 14. Candidate별 요구 입력 요약

상세 필드 경로는 `LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md`를 따른다.

| Cause | Required 핵심 | Optional 핵심 | Downstream Blocking 핵심 |
|---|---|---|---|
| DATA_QUALITY_ARTIFACT | data window, detector version, validation summary | rejection/duplicate/coverage | unresolved critical conflict |
| CAPACITY_OR_OPERATION_CONSTRAINT | target slot, business hours, capacity state | staff/room/equipment detail | offering availability, policy, owner |
| OFFER_SLOT_MISMATCH | target offering, slot, offering-slot evidence | duration, category, historical shares | eligibility, target-slot availability |
| RETENTION_GAP | token/history/revisit/cohort capability | offering history, recent contact | consent, contact channel, tracking |
| DISCOVERABILITY_GAP | target slot visibility or exposure capability | search/map/landing metrics | tracking, policy, budget for paid action |
| DEMAND_DEFICIT | repeated low pattern and comparison | weather/event/search/footfall | broader demand proxy before acquisition claim |
| CONVERSION_FRICTION | funnel exposure/start/completion | UX error, inquiry conversion | tracking, booking path ownership |
| CHANNEL_MISMATCH | channel-level exposure/result | audience/channel history | attribution/tracking |
| VALUE_OR_PRICE_FRICTION | structured price/value evidence | historical benefit test | economics and policy |
| CANCELLATION_LEAKAGE | cancellation/no-show evidence | reminder/waitlist/reschedule | policy and tracking |

---

# 15. Candidate별 핵심 규칙

## 15.1 DATA_QUALITY_ARTIFACT

### 우선 조건

다음 중 하나면 높은 우선순위:

```text
validation_status = conflicting
timezone validation failure
unknown status 비율이 기준 초과
offering resolution rate 저하
source lineage 없음
data stale
```

### Global Blocking

다음은 전체 분석을 `BLOCKED_BY_DATA_QUALITY`로 전환할 수 있다.

- data window invalid
- tenant/business source conflict
- timezone conflict
- required status mapping missing
- source data version unknown
- Opportunity evidence source를 재현할 수 없음

### 진단 질문

- 최근 import에서 제외된 행이 있습니까?
- 외부 상태값이 내부 5개 상태로 모두 확인됐습니까?
- 예약 시각의 timezone이 사업장 시간대와 일치합니까?
- Offering 이름이 하나의 Offering으로 일관되게 매핑됐습니까?

## 15.2 CAPACITY_OR_OPERATION_CONSTRAINT

### Supporting

- slot capacity unknown 또는 0
- staff shortage
- eligible staff 0/unknown
- room/equipment unavailable
- blackout
- target slot이 실제 booking UI에서 닫힘

### Contradicting

- capacity confirmed
- Offering available
- eligible staff sufficient
- room/equipment available
- 동일 조건의 다른 주에서 정상 예약 발생

### 주의

capacity가 없었다면 “수요 부족”이 아니라 “판매 불가 슬롯”일 수 있다.

## 15.3 OFFER_SLOT_MISMATCH

### Supporting

- 목표 Offering의 slot share가 전체 share보다 지속적으로 낮음
- duration이 목표 슬롯과 맞지 않음
- 해당 Offering의 eligible staff가 특정 시간대에 없음
- 다른 Offering은 같은 슬롯에서 정상

### Contradicting

- 동일 Offering이 다른 유사 주에서 정상
- target slot availability와 staff가 충분
- 모든 Offering이 동일하게 낮음

## 15.4 RETENTION_GAP

### Supporting

- 예상 재방문 시점이 지난 고객군 존재
- 목표 Offering 이용 이력 cohort 존재
- 목표 슬롯과 재방문 가능 고객군을 연결 가능
- 최근 재방문 Action 없음

### Contradicting

- eligible cohort 0
- 대부분 최근 방문
- 이미 최근 동일 cohort에 Action 실행
- Offering이 재방문형이 아님

### Privacy

개별 고객 식별자는 Cause 결과에 포함하지 않는다.

## 15.5 DISCOVERABILITY_GAP

### Supporting

- booking link/slot 노출 없음
- 지도·플레이스·웹에서 목표 Offering/시간대가 보이지 않음
- 노출 지표 낮음
- 검색 수요 proxy는 있으나 예약 유입이 낮음

### Contradicting

- 노출은 충분하지만 booking conversion이 낮음
- paid/organic 유입은 정상
- 해당 시간대 검색 수요 proxy도 낮음

## 15.6 DEMAND_DEFICIT

### Supporting

- 장기 반복
- 비교 시간대 대비 지속적 저하
- 여러 Offering이 동시에 낮음
- 외부 수요 proxy도 낮음

### Contradicting

- 검색·유동은 정상
- 노출이나 예약 경로 문제 존재
- capacity가 실제로 닫혀 있었음
- 데이터 품질 문제

## 15.7 CONVERSION_FRICTION

### Supporting

- 노출/페이지 방문은 있으나 booking completion 낮음
- booking start 대비 completion 낮음
- target slot 선택 불가
- 오류·이탈 증가

### Contradicting

- funnel 유입 자체가 낮음
- booking completion 정상
- capacity 없음

## 15.8 CHANNEL_MISMATCH

### Supporting

- 특정 채널 유입은 많지만 완료 예약 낮음
- 다른 채널에서 같은 Offering 전환이 더 높음
- 목표 시간대 source mix가 비효율적

### Contradicting

- 채널별 전환 차이가 없음
- attribution 부족
- 모든 채널에서 동일한 수요 저하

## 15.9 VALUE_OR_PRICE_FRICTION

### Supporting

- 가격·가치 정보 노출 후 conversion 저하
- 과거 비가격 가치 보강 실험에서 개선
- 동일 Offering의 조건별 conversion 차이

### Contradicting

- 가격/가치 노출 전 단계부터 유입 없음
- offering availability/capacity 문제
- structured evidence 없음

## 15.10 CANCELLATION_LEAKAGE

### Supporting

- 동일 slot/offering의 disruption rate 상승
- booked는 있으나 completed가 낮음
- 관련 CancellationHotspot 존재

### Contradicting

- 예약 생성 자체가 낮음
- cancellation/no-show 정상
- capacity가 닫혀 있음

---

# 16. Diagnostic Question Contract

```json
{
  "id": "CQ_CAP_01",
  "cause_code": "CAPACITY_OR_OPERATION_CONSTRAINT",
  "field_path": "operation.slot_capacity_confirmed",
  "question": "화요일 14~16시에 해당 Offering을 실제로 제공할 수 있었습니까?",
  "answer_type": "boolean_with_unknown",
  "priority": "blocking",
  "why_needed": "수요 부족과 판매 불가 슬롯을 구분하기 위해 필요합니다.",
  "allowed_answers": [true, false, "unknown"],
  "pii_class": "none",
  "readiness_effect": {
    "known_true": "cause-evaluable",
    "known_false": "capacity-cause-supported",
    "unknown": "strategy-blocked"
  }
}
```

## Answer Type

```text
boolean_with_unknown
integer_nonnegative
decimal_money
enum
datetime_with_offset
date_range
multi_select
free_text_limited
```

`free_text_limited`는 운영 메모에만 사용하고 환자 상담·임상정보를 받지 않는다.

## Priority

```text
required
blocking
optional
```

## 질문 정렬

```text
1. data quality critical
2. capacity / offering availability
3. policy / consent
4. tracking / result source
5. economics
6. optional context
```

---

# 17. Cause→Strategy Handoff Contract

Cause Analysis는 Strategy를 선택하지 않는다.

전달:

```text
cause_analysis_id
version
candidate list
candidate status
review priority
evidence refs
contradiction refs
missing required/optional inputs
downstream blockers
diagnostic answers
global limitations
```

Strategy Engine은 다음을 별도로 고려한다.

```text
business goal
economics
capacity
channel
policy
measurement
playbook applicability
```

Cause Score를 Strategy Score로 복사하지 않는다.

---

# 18. API 후보

## 18.1 Preview 우선

```text
POST /api/v1/opportunities/{opportunityId}/cause-analyses/preview
```

Request:

```json
{
  "decision_context": {},
  "as_of": "2026-08-17T14:00:00+09:00"
}
```

특성:

- persistence 없음
- 외부 실행 없음
- 동일 입력 → 동일 결과
- owner/admin/marketer
- viewer는 향후 조회-only endpoint에서만 허용 검토
- tenant/business mismatch는 404
- PII field는 422

## 18.2 Persistence 이후

```text
POST /api/v1/opportunities/{opportunityId}/cause-analyses
GET  /api/v1/opportunities/{opportunityId}/cause-analyses
GET  /api/v1/cause-analyses/{causeAnalysisId}
POST /api/v1/cause-analyses/{causeAnalysisId}/diagnostic-answers
```

기존 `/recommendations/draft`는 제거하지 않는다.

---

# 19. DB 후보

첫 preview에서는 DB 없이 시작한다.

Persistence 단계에서 검토:

```text
cause_analysis_runs
cause_candidates
cause_evidence_links
cause_diagnostic_questions
cause_diagnostic_answers
```

## 공통 필드

```text
id
tenant_id
business_id
opportunity_id
decision_context_snapshot_id
version
status
input_hash
generated_at
created_by_user_id(optional)
limitations
```

## 불변성

동일 run의 Candidate 결과를 update로 덮어쓰기보다 새 version/run을 생성한다.

---

# 20. Determinism

동일한 다음 입력은 동일 결과를 반환해야 한다.

```text
Opportunity payload
Decision Context payload
Cause rules version
Score version
as_of
```

Deterministic ID 후보:

```text
sha256(
  tenant_id
  + business_id
  + opportunity_id
  + decision_context_hash
  + cause_analysis_version
  + as_of
)
```

`as_of`가 달라지면 freshness·historical context가 달라질 수 있으므로 다른 결과를 허용한다.

---

# 21. 오류 계약

```text
INVALID_OPPORTUNITY_TYPE
OPPORTUNITY_NOT_FOUND
DECISION_CONTEXT_INVALID
TENANT_SCOPE_MISMATCH
UNSUPPORTED_CONTRACT_VERSION
PII_FIELD_REJECTED
TIMEZONE_REQUIRED
CRITICAL_DATA_QUALITY_CONFLICT
INSUFFICIENT_EVIDENCE
CAUSE_ANALYSIS_INTERNAL_ERROR
```

Error envelope는 기존 API 계약을 따른다.

---

# 22. 테스트 전략

## 22.1 Unit

### Taxonomy

- 모든 code unique
- description/hypothesis template 존재
- taxonomy order 고정

### Requirement Evaluator

- R 누락 → `NEEDS_DATA`
- O 누락 → score 가능
- B 누락 → downstream blocker
- conflicting/stale/restricted 처리

### Scoring

- factor clamp
- weighted total
- Required 누락 시 score null
- deterministic tie-break
- probability wording 없음

### Diagnostic Questions

- missing field별 정확한 질문
- priority 정렬
- PII 질문 없음
- 동일 입력 동일 질문

## 22.2 LOW_DEMAND_SLOT Fixtures

### Case 1 — Complete Capacity

```text
capacity confirmed
offering available
eligible staff sufficient
```

기대:

- capacity Candidate 반대 근거
- 다른 Candidate 우선 검토

### Case 2 — Capacity Unknown

기대:

- capacity Candidate `NEEDS_DATA`
- blocking diagnostic question
- demand expansion strategy blocked

### Case 3 — Capacity False

기대:

- capacity Candidate 높은 우선순위
- Demand Deficit보다 먼저 검토
- 마케팅 실행이 아니라 operation review handoff

### Case 4 — Eligible Revisit Cohort

기대:

- Retention Candidate reviewable
- consent unknown이면 downstream blocker
- individual token 없음

### Case 5 — Data Conflict

기대:

- run `BLOCKED_BY_DATA_QUALITY`
- DATA_QUALITY_ARTIFACT reviewable
- 다른 Candidate blocked
- diagnostic question 반환

### Case 6 — Discoverability Data Present

기대:

- Discoverability Candidate score
- funnel data가 있으면 Conversion Candidate 조건부 생성

### Case 7 — Demand Deficit Support

기대:

- repeated pattern + broader proxy
- demand Candidate reviewable
- 인과 문구 없음

## 22.3 Security

- cross tenant 404
- raw patient fields 422
- raw customer token 결과 미포함
- clinical input reject
- audit-safe error

## 22.4 Regression

- Opportunity payload 불변
- existing recommendation endpoint 불변
- existing Action/Result/Measurement 불변
- current test suite green

---

# 23. 로컬 구현 Backlog

## CA-001 — Taxonomy

- CauseCode enum
- metadata registry
- stable order
- default/conditional candidate sets

## CA-002 — Input Requirement Model

- `R/O/B` enum
- field path
- state handling
- applicability condition
- missing behavior

## CA-003 — Data Quality Context

- import aggregate resolver
- validation summary
- freshness
- coverage rates
- critical conflict policy

## CA-004 — LOW_DEMAND_SLOT Candidate Seeder

- core candidates
- conditional candidates
- related Opportunity linkage
- deterministic order

## CA-005 — Evidence Mapper

- Opportunity evidence refs
- Decision Context refs
- supporting/contradicting mapping
- no raw data access

## CA-006 — Candidate Evaluator

- Required/Optional/Blocking
- status
- missing data
- downstream blockers

## CA-007 — Cause Priority Score v1

- factors
- weights
- labels
- version
- test fixtures

## CA-008 — Diagnostic Questions

- templates
- answer types
- priority
- readiness effects

## CA-009 — Result Contract

- Pydantic schema
- status
- candidates
- diagnostics
- strategy handoff

## CA-010 — Preview API

- authorization
- tenant scope
- PII reject
- deterministic input hash
- no persistence

## CA-011 — Regression

- LOW_DEMAND_SLOT fixtures
- existing recommendation compatibility
- sample pack integration

## CA-012 — Documentation

- API_CONTRACT proposal
- CURRENT_IMPLEMENTATION_STATUS after code
- ADR 0020 candidate

---

# 24. 완료조건

Cause Analysis Engine v1은 다음을 모두 충족할 때 완료다.

1. `LOW_DEMAND_SLOT` core Candidate 6개 정의
2. conditional Candidate 정책 정의
3. 모든 Candidate에 R/O/B mapping
4. Required 누락과 Blocking 누락 구분
5. DATA_QUALITY_ARTIFACT 선행 검토
6. Cause Priority Score versioning
7. Cause는 사실·확률로 표시하지 않음
8. Diagnostic Question 구조화
9. Decision Context만 사용하고 Raw CSV 직접 접근 없음
10. Hospital PII/clinical data 사용 없음
11. 동일 입력에 동일 결과
12. Strategy handoff 계약
13. Preview API contract
14. tenant isolation test
15. 기존 Opportunity·Recommendation·Action 회귀 통과
16. 코드 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 25. 구현 연결

Cause 이후의 Strategy·Playbook·Experiment·Recommendation Package·Quality 설계는 모두 완료됐다.

로컬 구현은 다음 순서로 진행한다.

```text
LOOFIO_IMPLEMENTATION_BACKLOG_V1.md
→ CA-001~CA-012
→ ST-001~ST-012
```

구현 완료 여부는 migration·code·test와 `CURRENT_IMPLEMENTATION_STATUS.md`로 판단한다.
