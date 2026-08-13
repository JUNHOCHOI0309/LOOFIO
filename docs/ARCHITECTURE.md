# LOOFIO Architecture v1

## 1. 목적

이 문서는 LOOFIO의 시스템 경계와 데이터 흐름을 정의한다.

핵심 제품 흐름:

```text
Business Data
+
External Context
        ↓
Deterministic Analytics
        ↓
Opportunity Detection
        ↓
AI Explanation / Recommendation
        ↓
User Decision
        ↓
Action
        ↓
Result
        ↓
Measurement
        ↓
Next Analysis
```

핵심 원칙:

> AI가 원본 데이터에서 기회를 임의 생성하지 않는다. 데이터 계층과 deterministic engine이 먼저 구조화된 사실과 후보 기회를 만든다.

---

# 2. Logical Architecture

```text
┌──────────────────────────────────────────────┐
│                   Apps / UI                  │
│ Dashboard · Opportunity · Action · Results  │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                  API Layer                   │
│ Auth · Validation · DTO · Idempotency        │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│              Application Layer               │
│ Use Cases · Transaction Boundary · Policies  │
└──────┬─────────┬──────────┬──────────┬────────┘
       ↓         ↓          ↓          ↓
   Business   Ingestion  Opportunity  Action/Measurement
       │         │          │          │
       └─────────┴──────┬───┴──────────┘
                        ↓
┌──────────────────────────────────────────────┐
│                Domain / Data                 │
│ Business · Offering · Customer · Domain Data│
│ BusinessEvent · Metrics · Opportunity        │
└──────────────────────┬───────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│                 Ports                        │
│ Repository · AI · External Data · Channels  │
└──────────────────────┬───────────────────────┘
                       ↑ implements
┌──────────────────────────────────────────────┐
│             Infrastructure / Adapters        │
│ PostgreSQL · CSV · Weather · Public API      │
│ Marketing Channel Connectors · AI Providers │
└──────────────────────────────────────────────┘
```

---

# 3. Runtime Data Flow

## 3.1 Import

```text
CSV / Excel / API
→ Raw Import
→ Validation
→ Column Mapping
→ Domain Normalizer
→ Domain Tables
→ BusinessEvent Projection
```

원본과 정규화 데이터는 분리한다.

## 3.2 Analytics

```text
Domain + BusinessEvent
→ Metric Engine
→ Metric Values
→ Detector
→ Opportunity Score / Confidence
→ Opportunity + Evidence
```

Metric과 Detector는 LLM 없이 재현 가능해야 한다.

## 3.3 Recommendation

```text
Opportunity
+ Evidence
+ Limitations
+ Business Context
+ Allowed Actions
→ AI Manager
→ Structured Recommendation
```

AI는 Observation의 숫자를 새로 만들지 않는다.

## 3.4 Action

```text
Recommendation
→ User Decision
→ Action Draft
→ User Approval
→ Manual or Connector Execution
```

MVP에서는 Human-in-the-loop가 기본이다.

## 3.5 Measurement

```text
Action
→ Result Collection
→ Baseline
→ Measurement
→ Incremental Estimate
→ Next Decision Context
```

---

# 4. Module Boundaries

권장 논리 모듈:

```text
/apps
/api

/modules
  /business
  /taxonomy
  /ingestion
  /sales
  /marketing
  /external-data

/analytics
  /metrics
  /detectors
  /scoring

/ai
  /gateway
  /explanation
  /recommendation
  /content

/measurement

/connectors
  /public-data
  /weather
  /reservation
  /analytics
  /advertising
  /messaging

/data
  /repositories
  /migrations

/jobs
/monitoring
```

실제 언어/프레임워크 구조는 달라질 수 있으나 **경계의 의미는 유지**한다.

---

# 5. Core Domain

## Tenant

보안 및 데이터 격리 경계.

## Business

분석의 최상위 사업장 단위.

## Offering

상품/서비스/패키지/회원권 등 판매 대상.

## Customer

사업장 내부에서 가명 식별되는 고객.

## Domain Object

사업 유형별 운영 객체.

예:

```text
Appointment
Sale
Membership
Contract
WorkOrder
Booking
Project
```

## BusinessEvent

다업종 데이터를 공통 Analytics 계층으로 전달하는 Fact Stream.

## Opportunity

Detector가 생성한 매출 기회 후보.

## Recommendation

Opportunity를 실행 가능한 행동으로 바꾼 제안.

## Action

실제로 실행된 또는 실행 예정인 행동.

## Measurement

실행 전후 결과를 비교한 측정 객체.

---

# 6. Archetype Architecture

공식 직업분류는 최종 실행 로직이 아니다.

```text
KECO / KSCO
→ Archetype Candidate
→ Revenue Model Confirmation
→ Final Business Archetype
→ Data Readiness
→ Metric Adapter
→ Detector Set
```

새 업종 지원 시 가능한 한 기존 Archetype을 재사용한다.

새 Archetype 추가는 새로운 테이블을 만드는 것보다 먼저 다음을 검토한다.

1. 기존 Domain Object로 표현 가능한가?
2. BusinessEvent로 표준화 가능한가?
3. 기존 Metric Adapter를 재사용 가능한가?
4. 기존 Detector를 재사용 가능한가?

---

# 7. AI Boundary

AI는 시스템의 판단 전체가 아니다.

```text
Raw Data
  X
  └─> LLM 직접 분석 금지

Raw Data
→ Deterministic Processing
→ Structured Opportunity
→ LLM
```

AI Gateway 뒤에 provider를 숨긴다.

```text
task_type
quality_tier
structured_schema
budget
→ AI Gateway
→ provider/model
```

특정 모델은 교체 가능해야 한다.

---

# 8. Database Boundary

PostgreSQL 기준.

계층:

```text
Core
Taxonomy
Ingestion
Domain
Analytics
Opportunity
Action
Measurement
AI/Audit
```

DB 구조의 세부 계약은 `LOOFIO_DATA_SCHEMA_V1.md`를 따른다.

---

# 9. External Data Boundary

외부 데이터는 Context다.

예:

- 날씨
- 공휴일
- 지역 행사
- 생활인구
- 상권
- 경쟁 업종 분포

외부 Context만으로 매출 효과를 단정하지 않는다.

```text
Internal Business Data > External Context
```

외부 데이터는 가설 설명과 조건 보정에 사용한다.

---

# 10. Security Boundary

반드시 분리하는 범위:

```text
Tenant A
  Business A1
  Business A2

Tenant B
  Business B1
```

기본 규칙:

- Repository query는 tenant scope 필수
- File path/cached key에 tenant/business scope 포함
- AI context에 다른 tenant 데이터 포함 금지
- OAuth/secret 평문 DB 저장 금지
- 고객 식별자는 tokenized key 우선

---

# 11. Failure Isolation

AI 실패가 Opportunity 생성 자체를 취소하면 안 된다.

```text
Detector Success
→ Opportunity Persisted
→ AI Recommendation Failed

결과:
Opportunity는 남아 있어야 함
Recommendation만 retry
```

외부 채널 실행 실패 역시 추천/Opportunity 기록을 삭제하지 않는다.

---

# 12. Versioned Intelligence

다음은 버전이 필요하다.

```text
taxonomy mapping
normalizer
metric
detector
score
prompt
recommendation schema
measurement method
```

목적은 과거 의사결정을 재현하는 것이다.

---

# 13. MVP Architecture Scope

MVP에서 우선 완성할 경로:

```text
CSV/Excel
→ Appointment Normalization
→ BusinessEvent
→ Metrics
→ LowDemandSlot / RevenueGap
→ Opportunity
→ AI Recommendation
→ User Decision
→ Manual Action
→ Result Input
→ Measurement
```

그 이후:

- CancellationHotspot
- DormantCustomer
- ServiceDemandGap
- 자동 Connector
- 다른 Archetype Adapter

순서로 확장한다.

---

# 14. 아직 확정되지 않은 구현

이 문서는 다음을 특정 제품으로 확정하지 않는다.

- 웹 프레임워크
- API 프레임워크
- Queue
- Cache
- Cloud
- Auth
- CI/CD
- Monitoring vendor

해당 결정은 ADR로 추가한다.
