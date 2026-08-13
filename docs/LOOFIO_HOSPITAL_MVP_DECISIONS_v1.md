---
title: "LOOFIO Hospital MVP 기술·제품 결정안"
version: "1.0"
date: "2026-08-13"
status: "MVP 1차 결정 확정"
---

# LOOFIO Hospital MVP 기술·제품 결정안 v1.0

## 1. 문서 목적

본 문서는 LOOFIO Hospital MVP를 실제 개발 단계로 전환하기 위해 지금까지 확정한 제품 범위, 기술 스택, 데이터 구조, UI 방향, 인증 구조, Opportunity Engine 우선순위, 인프라 구성을 정리한다.

LOOFIO의 핵심 제품 루프는 다음과 같다.

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

핵심 원칙은 다음과 같다.

> 코드가 데이터에서 기회를 탐지하고, AI는 그 기회를 설명하고 실행 가능한 행동으로 변환한다.

---

# 2. MVP 대상 의료 분야

LOOFIO Hospital MVP는 다음 5개 진료 분야를 우선 대상으로 한다.

1. 피부과
2. 성형외과
3. 정형외과
4. 안과
5. 이비인후과

공통 Archetype은 다음과 같이 둔다.

```text
APPOINTMENT_HEALTH
│
├─ DERMATOLOGY
├─ PLASTIC_SURGERY
├─ ORTHOPEDICS
├─ OPHTHALMOLOGY
└─ OTOLARYNGOLOGY
```

5개 진료과를 별도 제품으로 분리하지 않는다.

공통 Core는 유지하고 진료과에 따라 다음만 달라지도록 설계한다.

- Offering 구성
- 데이터 매핑 규칙
- Metric Adapter
- Detector 조건
- 마케팅 정책 및 금지 표현
- 외부 데이터 활용 방식

---

# 3. 제품 사용 환경

## 3.1 기본 방향

LOOFIO는 **PC 중심의 B2B SaaS**로 설계한다.

주요 사용 목적은 다음과 같다.

- 사업 현황 확인
- 예약 및 매출 기회 분석
- Opportunity 확인
- 추천 행동 검토
- 승인 / 수정 / 거절
- 데이터 업로드
- 캠페인 및 Action 확인
- Result / Measurement 조회
- 리포트 확인

모바일은 별도 Native App을 우선 개발하지 않는다.

```text
PC
→ 메인 업무 환경

Mobile
→ Responsive Web / PWA
→ 알림
→ Opportunity 조회
→ 간단 승인
→ 결과 확인
```

---

# 4. Frontend 기술 스택

## 4.1 Frontend

```text
Language
→ TypeScript

Framework
→ Next.js

UI
→ React

Styling
→ Tailwind CSS

UI Primitive
→ shadcn/ui 계열

Design Rule
→ Taste Skill
```

## 4.2 Backend

```text
Language
→ Python

Framework
→ FastAPI

Data / Analytics
→ Python

Validation
→ Pydantic
```

## 4.3 Database

```text
PostgreSQL
```

개발 단계에서는 Local PostgreSQL을 사용한다.

Staging / Production의 Managed PostgreSQL 공급자는 추후 결정한다.

---

# 5. UI / UX 방향

## 5.1 메인 디자인 레퍼런스

LOOFIO는 전통적인 관리도구보다 조금 더 세련되면서도, 정보 전달이 명확한 B2B SaaS UI를 목표로 한다.

핵심 특징:

```text
왼쪽 고정 Sidebar
+
넓은 Main Workspace
+
큰 페이지 제목
+
짧은 설명
+
상단 KPI Card
+
중앙 Chart
+
하단 Data Table
```

## 5.2 디자인 성격

```text
Professional
Calm
Data-centric
Minimal
High Information Density
```

과도한 장식과 애니메이션은 피한다.

## 5.3 기본 Visual Direction

```text
Background
→ #F8F9FC 계열

Card
→ White

Border
→ 매우 연한 Gray

Radius
→ 12~16px

Shadow
→ 약하게

Primary Accent
→ Purple / Indigo 계열 후보

Secondary Accent
→ Blue / Mint / Pink

Typography
→ 강한 Heading
→ 읽기 쉬운 Body

Spacing
→ 넉넉함

Motion
→ 낮음
```

## 5.4 Taste Skill 초기 설정 방향

```text
DESIGN_VARIANCE = 3
MOTION_INTENSITY = 2
VISUAL_DENSITY = 6~7
```

Taste Skill은 LOOFIO의 브랜드를 대신 결정하는 도구가 아니라, 프론트엔드 구현 시 레이아웃·타이포그래피·간격·모션 품질을 일관되게 유지하기 위한 디자인 규칙으로 사용한다.

---

# 6. Frontend Information Architecture

MVP 기준 Sidebar 구조는 다음을 우선한다.

```text
LOOFIO

Dashboard

Opportunities

Analytics

Customers

Actions

Data

Reports

Settings
```

추후 확장:

```text
Campaigns
Content
Notifications
Integrations
```

`Campaigns`와 `Content`는 초기에는 `Actions` 안에서 처리하고 기능이 커졌을 때 독립 메뉴로 분리할 수 있다.

---

# 7. Dashboard 방향

Dashboard는 단순 매출 조회 화면보다 **현재 발견된 사업 기회와 실행 상태**를 중심으로 구성한다.

예시:

```text
이번 달 발견된 매출 기회
₩1,420,000

Open Opportunities
7

실행 중
3

측정 완료
5
```

주요 카드 후보:

- 발견된 예상 기회 가치
- 예약률
- 방문 전환율
- 재방문율
- 실행된 Action
- 연결 매출
- 최근 Opportunity
- 최근 Measurement

중앙 영역:

- 예약률 추이
- 매출 추이
- 시간대별 수요
- Opportunity 유형 분포

하단:

- Opportunity 목록
- Action 상태
- 최근 캠페인 성과
- 최근 Result

---

# 8. Observation / Estimate / Recommendation 분리

LOOFIO의 UI에서는 다음 세 가지를 반드시 구분한다.

## Observation

실제 데이터로 확인된 사실.

예:

> 최근 12주 동안 화요일 14~16시 예약 발생량이 다른 화요일 시간대보다 41% 낮았습니다.

## Estimate

가정을 포함한 계산 또는 추정.

예:

> 다른 시간대 수준까지 예약이 증가한다고 가정하면 월 38~46만원 수준의 추가 매출 여지가 있습니다.

## Recommendation

실행 제안.

예:

> 해당 시간대에 재방문 가능 고객을 대상으로 제한된 프로모션을 테스트하는 것을 권장합니다.

추정값을 실제 손실 또는 보장 매출로 표시하지 않는다.

---

# 9. Tenant 구조

LOOFIO는 처음부터 Multi-Tenant 구조를 유지한다.

```text
User
 ↓
Tenant
 ↓
Business
 ↓
Location
```

예:

```text
Tenant
OO의료그룹

├─ Business
│   └─ OO피부과
│
├─ Location
│   ├─ 강남점
│   └─ 잠실점
│
└─ Users
    ├─ Owner
    ├─ Admin
    ├─ Marketer
    └─ Viewer
```

User는 여러 Tenant에 서로 다른 Role로 참여할 수 있다.

```text
User
│
├─ Tenant A / Owner
├─ Tenant B / Admin
└─ Tenant C / Viewer
```

Tenant isolation은 기능이 아니라 시스템의 불변조건으로 취급한다.

---

# 10. 인증

MVP 로그인 방식:

```text
Google OAuth
+
Naver Login
```

Social Login 계정과 Tenant는 동일 개념으로 처리하지 않는다.

```text
Google / Naver Account
        ↓
      User
        ↓
Tenant Membership
        ↓
      Tenant
        ↓
     Business
        ↓
     Location
```

Auth 구현체와 세션 방식은 실제 구현 ADR에서 추가 결정한다.

---

# 11. Hospital Domain Model

Hospital MVP는 병원 전용 독립 데이터 모델을 만드는 것이 아니라, LOOFIO 공통 Domain에 Hospital Adapter를 적용한다.

공통 구조:

```text
Business
Offering
Appointment
Customer
Payment
ExternalContext
MarketingProfile
Opportunity
Recommendation
Decision
Action
Result
Measurement
```

---

# 12. Hospital Data Contract v1

## 12.1 공통 시스템 필드

LOOFIO가 수집 시 생성하는 시스템 필드:

```text
schema_version
tenant_id
business_id
location_id
source_system
source_record_id
ingested_at
updated_at
```

---

# 13. Business

병원 또는 의원의 사업체 정보.

## 필수

```text
hospital_name
hospital_type
medical_domain
display_specialty_main
address
business_hours
closed_days
```

## 권장

```text
display_specialties[]
phone_public
website_url
reservation_url
naver_place_url
kakao_place_url
doctor_count
employee_count
capacity_per_day
parking_available
reservation_required
```

---

# 14. Offering

공통 도메인 용어는 `Service`보다 `Offering`을 사용한다.

병원에서 Offering은 실제 분석과 마케팅의 대상이 되는 진료·검사·시술·수술·프로그램 등을 의미한다.

예:

```text
여드름 치료
피코토닝
보톡스
리프팅
백내장 검사
도수치료
코골이 검사
```

권장 필드:

```text
offering_id
offering_name
offering_category
specialty
offering_type
insurance_type
price_mode
list_price
duration_minutes
requires_appointment
active
marketing_enabled
```

`list_price`는 병원 Adapter에서 항상 필수로 요구하지 않는다.

예:

```text
price_mode = fixed
→ list_price 사용 가능

price_mode = insured
→ list_price = null 허용

price_mode = variable
→ list_price 선택
```

---

# 15. Appointment

Hospital MVP의 가장 중요한 Fact 데이터다.

## 필수

```text
appointment_id
visit_start_at
offering_name
status
```

## 권장

```text
visit_end_at
customer_token
staff_name
booked_at
listed_price
paid_amount
discount_amount
source
source_record_id
```

표준 상태:

```text
booked
completed
cancelled
no_show
unknown
```

---

# 16. Customer

Hospital MVP에서 Customer 객체는 최소한으로 유지한다.

수집하지 않는 것을 원칙으로 하는 데이터:

```text
환자 이름
주민등록번호
전화번호 원문
주소
진단명
질병
증상
처방
검사 결과
의무기록
상담 원문
```

대신 다음 구조를 사용한다.

```text
customer_key
first_seen_at
last_seen_at
visit_count
total_revenue
```

향후 CRM / Marketing 기능이 확장되면 다음을 추가할 수 있다.

```text
marketing_consent_status
marketing_consent_updated_at
marketing_consent_channels[]
```

고객 식별은 가능한 한 tokenization / HMAC 기반의 내부 key를 사용한다.

---

# 17. Payment

MVP의 절대 필수 데이터는 아니지만 매출 분석 정밀도를 높이기 위해 권장한다.

```text
transaction_id
paid_at
appointment_id
customer_key
offering_id
offering_name
listed_price
paid_amount
discount_amount
refund_amount
payment_status
source_record_id
```

표준 상태:

```text
paid
partial
refunded
cancelled
unknown
```

---

# 18. ExternalContext

ExternalContext는 병원이 직접 입력하는 데이터가 아니라 LOOFIO가 자동으로 보강한다.

후보:

```text
날씨
공휴일
요일
계절

지역 인구
연령 구조
상권 정보

지역 의료기관 수
동일 진료과 경쟁 병원 수

지역 행사
유동 인구
생활 인구
```

외부 Context는 내부 사업 데이터보다 우선하지 않는다.

```text
Internal Business Data
>
External Context
```

외부 데이터만으로 매출 효과를 단정하지 않는다.

---

# 19. MarketingProfile

MarketingProfile은 예약·매출 데이터와 별도의 LOOFIO 운영 설정이다.

예:

```yaml
primary_offerings:
  - 피코토닝
  - 리프팅
  - 여드름치료

target_regions:
  - 강남구
  - 서초구

brand_tone:
  - professional
  - friendly

content_channels:
  - naver_blog
  - instagram
  - naver_place

approval_mode: manual

prohibited_topics: []

required_disclaimers: []

content_approver_user_id: usr_xxx
```

초기에는 모든 외부 마케팅 실행에 Human Approval을 둔다.

```text
Generate
→ Compliance Check
→ User Approval
→ Execute
```

---

# 20. CSV Import v1

초기에는 API 연동보다 CSV / Excel 업로드를 우선한다.

## 20.1 `hospital.csv`

```text
hospital_name
hospital_type
display_specialty_main
address
business_hours
closed_days
phone_public
website_url
reservation_url
```

## 20.2 `offerings.csv`

```text
offering_id
offering_name
offering_category
specialty
offering_type
insurance_type
price_mode
list_price
duration_minutes
active
```

## 20.3 `appointments.csv`

가장 중요한 파일:

```text
appointment_id
visit_start_at
visit_end_at
offering_name
status
customer_token
staff_name
booked_at
listed_price
paid_amount
discount_amount
source
source_record_id
```

## 20.4 `payments.csv`

초기 MVP에서는 Appointment에 `paid_amount`를 포함하는 방식으로 시작할 수 있다.

별도 Payment import는 v1.1 이후 분리 가능하다.

---

# 21. 데이터 Import Flow

```text
Hospital Source
    │
    ├── hospital.csv
    ├── offerings.csv
    └── appointments.csv
             │
             ▼
       Column Mapper
             │
             ▼
      Hospital Adapter
             │
             ▼
       Normalization
             │
             ▼
       Domain Tables
             │
             ▼
      BusinessEvent
             │
             ▼
          Metrics
             │
             ▼
     Opportunity Engine
```

Raw Import와 Normalized Domain은 분리한다.

---

# 22. Opportunity Engine 출시 순서

## v0.1

```text
LowDemandSlot
+
RevenueGap
```

핵심 질문:

```text
언제 예약이 반복적으로 낮은가?
+
그 구간은 어느 정도 경제적 기회인가?
```

## v0.2

```text
CancellationHotspot
```

핵심 질문:

```text
어떤 요일 / 시간대 / Offering에서
취소 또는 노쇼가 비정상적으로 높은가?
```

## v0.3

```text
DormantCustomer
```

핵심 질문:

```text
예상 재방문 시기를 넘긴 고객이 있는가?
```

## v0.4

```text
ServiceDemandGap
```

공통 명칭은 향후 `OfferingDemandGap`으로 변경 검토 가능.

핵심 질문:

```text
어떤 Offering이 특정 시간대나 고객군에서
충분히 활용되지 않고 있는가?
```

---

# 23. Opportunity Pipeline

```text
Raw Import
    ↓
Normalization
    ↓
BusinessEvent
    ↓
Metric Engine
    ↓
Detector
    ↓
Scoring
    ↓
Opportunity
    ↓
AI Explanation
    ↓
Recommendation
    ↓
User Decision
    ↓
Action
    ↓
Result
    ↓
Measurement
```

Detector는 LLM 없이 재현 가능해야 한다.

---

# 24. AI 역할

AI는 다음 역할에 집중한다.

```text
Opportunity 설명
가능한 원인 가설
실행 전략 제안
대상 고객 제안
채널 제안
콘텐츠 생성
```

AI가 직접 최종 계산하지 않는 값:

```text
매출
증감률
ROI
예약률
취소율
가동률
재방문 간격
baseline
Opportunity Score
통계 검정
```

---

# 25. 인프라

## 25.1 Local

```text
Frontend
→ Local Next.js

Backend
→ Local FastAPI

Database
→ Local PostgreSQL

Storage
→ Local 또는 R2 Dev Bucket
```

## 25.2 Staging

```text
Frontend
→ Cloudflare

Backend
→ Render

Database
→ Managed PostgreSQL
→ 공급자 추후 결정

Storage
→ Cloudflare R2 Staging
```

## 25.3 Production

```text
Frontend
→ Cloudflare

Backend
→ Render

Database
→ Managed PostgreSQL
→ 공급자 추후 결정

Storage
→ Cloudflare R2 Production
```

Local PostgreSQL은 개발 환경 전용으로 사용한다.

---

# 26. 배포 환경

기본 환경:

```text
Local / Test
↓
Staging
↓
Production
```

Production과 Staging은 다음을 분리한다.

- Database
- Secret
- R2 Bucket
- OAuth Credentials
- Environment Variables
- Logging / Monitoring

운영 데이터를 그대로 Staging에 복사하지 않는다.

---

# 27. 저장소 권장 구조

초기에는 Microservice보다 Modular Monolith를 우선한다.

```text
/apps
  /web

/api

/modules
  /business
  /taxonomy
  /ingestion
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

/data
  /repositories
  /migrations

/jobs

/monitoring
```

논리적 계층:

```text
Apps / UI
    ↓
API
    ↓
Application
    ↓
Domain / Analytics
    ↓
Ports

Infrastructure / Connectors
    → Ports 구현
```

---

# 28. API 기본 구조

Base:

```text
/api/v1
```

주요 리소스:

```text
/businesses
/imports
/opportunities
/recommendations
/actions
/measurements
```

향후 추가:

```text
/customers
/offerings
/reports
/integrations
```

API는 내부 DB 테이블 구조를 그대로 노출하지 않는다.

---

# 29. MVP 핵심 사용자 Flow

```text
1. Google / Naver 로그인
        ↓
2. Tenant 생성 또는 참가
        ↓
3. Business / Location 생성
        ↓
4. 병원 기본 정보 입력
        ↓
5. Offering 입력 / Import
        ↓
6. Appointment CSV 업로드
        ↓
7. Column Mapping
        ↓
8. Normalization
        ↓
9. Metric 계산
        ↓
10. Opportunity 탐지
        ↓
11. Dashboard 표시
        ↓
12. Recommendation 생성
        ↓
13. 사용자 승인 / 수정 / 거절 / 나중에
        ↓
14. Action 실행
        ↓
15. Result 입력 / 재수집
        ↓
16. Measurement
```

---

# 30. 개발 순서

현재 결정안을 기준으로 다음 순서로 진행한다.

```text
제품 / 기술 결정
        ↓
Hospital Domain Model
        ↓
PostgreSQL Schema
        ↓
CSV Import Contract
        ↓
Column Mapping
        ↓
FastAPI API Contract
        ↓
Frontend IA
        ↓
Dashboard Wireframe
        ↓
Metric Engine
        ↓
LowDemandSlot
        ↓
RevenueGap
        ↓
AI Recommendation
        ↓
Opportunity → Action → Result
        ↓
Measurement
```

---

# 31. 다음 개발 우선순위

## Priority 1

Hospital Domain Model을 실제 PostgreSQL Schema로 변환한다.

주요 테이블 후보:

```text
tenants
users
tenant_members

businesses
locations

offerings
customers
appointments
payments

raw_import_files
import_jobs
import_rows

business_events

metric_values
revenue_opportunities
opportunity_evidence

ai_recommendations
recommendation_decisions

actions
results
measurements

marketing_profiles
```

## Priority 2

`appointments.csv`의 실제 Import Schema와 Column Mapping 규칙을 확정한다.

## Priority 3

FastAPI Pydantic Schema 및 `/api/v1` OpenAPI 계약을 정의한다.

## Priority 4

첨부된 B2B SaaS 디자인 레퍼런스를 기준으로 Dashboard / Opportunity 화면 Wireframe을 작성한다.

## Priority 5

LowDemandSlot + RevenueGap를 deterministic backend로 구현한다.

---

# 32. 아직 추후 결정할 항목

다음은 지금 확정하지 않는다.

```text
Managed PostgreSQL 공급자
Auth 구현 라이브러리 / 서비스
CI/CD 세부 제품
Monitoring 제품
Secret Manager
Queue / Background Job 제품
Cache 제품
최종 LOOFIO Brand Color
```

이 항목은 실제 구현 시점에 ADR로 별도 결정한다.

---

# 33. 현재 MVP 정의

LOOFIO Hospital MVP는 다음 질문에 답할 수 있어야 한다.

> 현재 이 병원에서 반복적으로 놓치고 있는 예약·매출 기회는 무엇인가?

그리고 단순히 기회만 보여주는 것이 아니라 다음 흐름을 끝까지 연결해야 한다.

```text
Observation
↓
Estimate
↓
Recommendation
↓
Decision
↓
Action
↓
Result
↓
Measurement
```

첫 번째 MVP는 많은 기능보다 이 폐쇄 루프를 하나의 실제 병원 데이터에서 안정적으로 완성하는 것을 목표로 한다.
