---
title: "LOOFIO Business Taxonomy v1"
version: "1.0"
date: "2026-08-13"
status: "초기 다업종 적용 분류안"
sources:
  - "한국고용직업분류 및 한국표준직업분류 연계표(2).csv"
  - "LOOFIO_TECH_ROADMAP_v1.md"
  - "LOOFIO_OPPORTUNITY_ENGINE_V1.md"
---

# LOOFIO Business Taxonomy v1

## 1. 문서 목적

본 문서는 LOOFIO가 특정 1개 업종에 고정되지 않고 가능한 한 다양한 소상공인·중소사업 유형을 지원하기 위한 **내부 사업 분류 계층**을 정의한다.

기준 원칙은 다음과 같다.

> **직업명 자체를 업종으로 사용하는 것이 아니라, 해당 직업이 실제 사업으로 운영될 때의 수익 구조와 운영 데이터 형태를 LOOFIO Business Archetype으로 변환한다.**

LOOFIO의 공통 제품 루프는 업종에 관계없이 유지한다.

```text
Observe
  ↓
Opportunity
  ↓
Action
  ↓
Result
  ↓
Learn
```

다만 업종·사업 유형에 따라 다음 세 요소가 달라진다.

1. 어떤 데이터를 받아야 하는가
2. 어떤 Metric을 계산해야 하는가
3. 어떤 Opportunity Detector를 활성화해야 하는가

---

# 2. 원본 분류표 해석 원칙

업로드된 연계표에는 한국고용직업분류와 한국표준직업분류의 **직업 세분류 450개**가 포함되어 있다.

이 문서의 `support_level`, `archetype_family`, `loofio_archetype`은 공식 분류체계가 아니라 **LOOFIO 제품 설계를 위해 추가한 내부 해석 계층**이다.

따라서 다음을 구분한다.

```text
공식 직업분류 코드/명칭
        ↓
LOOFIO 내부 사업 Archetype
        ↓
수익 단위
        ↓
필요 데이터
        ↓
활성 Detector
```

동일 직업이라도 실제 사업 운영 형태가 다르면 서로 다른 Archetype으로 재분류할 수 있다.

예를 들어 같은 디자인 계열이라도 다음처럼 달라질 수 있다.

- 시간 예약 중심 → `APPOINTMENT_SERVICE`
- 견적·납품 중심 → `PROJECT_SERVICE`
- 온라인 상품 판매 중심 → `WALKIN_COMMERCE`

따라서 **직업 코드는 온보딩의 출발점이지 최종 사업 모델 판정값이 아니다.**

---

# 3. Support Level

| Level | 분류 수 | 정의 |
|---|---|---|
| A | 17 | 현재 Opportunity Engine과 높은 호환성 |
| B | 154 | 소규모 데이터/Metric 어댑터로 확장 가능 |
| C | 211 | 별도 도메인 데이터·Detector가 필요한 장기 지원 |
| D | 68 | 사업 업종으로 직접 매핑하지 않거나 초기 상업 대상 제외 |

총 450개 세분류 중:

- **A+B+C: 382개**
- **D: 68개**

즉 v1 분류에서는 최대한 넓게 지원 범위를 유지하되, 현재 Opportunity Engine을 그대로 적용할 수 있는지와 별도 확장이 필요한지를 명시적으로 구분한다.

## Level A — Current Core

현재 `LOOFIO_OPPORTUNITY_ENGINE_V1`의 다음 Detector를 직접 또는 매우 작은 변형으로 활용할 수 있다.

- `LowDemandSlot`
- `CancellationHotspot`
- `DormantCustomer`
- `RevenueGap`
- `ServiceDemandGap`

## Level B — Adapter Extension

LOOFIO의 공통 루프는 그대로 사용할 수 있지만 `Appointment` 대신 `Sale`, `WorkOrder`, `Booking`, `Contract` 등 다른 운영 객체를 도입해야 한다.

## Level C — Domain Expansion

장기 지원 대상이다. 기존 Detector만으로는 충분하지 않으며 생산·수주·리드·프로젝트·계절성 등 별도 Metric과 Detector가 필요하다.

## Level D — Not Directly Mapped

공공·기관 고용 직무 또는 사무 지원 직무처럼 직업명 자체를 사업체의 수익모델로 직접 사용할 수 없는 항목이다.

D라고 해서 해당 조직 전체가 LOOFIO를 사용할 수 없다는 뜻은 아니다. **해당 직업 코드만으로 사업 모델을 판정하지 않는다는 의미**다.

---

# 4. LOOFIO Archetype Family

| Family | 운영 형태 | 예시 | Revenue Unit | 핵심 데이터 | Detector 방향 | 비고 |
|---|---|---|---|---|---|---|
| APPOINTMENT_SERVICE | 예약·시간 슬롯형 | 미용, 상담, 의료·재활 등 | 예약/방문/서비스 결제 | Appointment, Customer, Service, Payment | LowDemandSlot·CancellationHotspot·DormantCustomer·RevenueGap·ServiceDemandGap | 현재 MVP와 가장 높은 호환성 |
| MEMBERSHIP_SERVICE | 회원·회차·재등록형 | 학원, 강습, 피트니스 등 | 회원권/회차/수업 | Member, Session, Attendance, Payment | DormantCustomer·RevenueGap·ServiceDemandGap + 회차/갱신 Detector | 기존 Detector를 비교적 쉽게 재사용 |
| WALKIN_COMMERCE | 방문·주문·소매형 | 음식, 카페, 소매, 오락 등 | 주문/영수증/상품 판매 | Sale, Product, Customer(optional), TimeSlot | RevenueGap·ServiceDemandGap·DormantCustomer(식별 시) + 시간대 매출 Detector | Appointment 대신 Sales 중심 어댑터 필요 |
| RECURRING_SERVICE | 정기 방문·계약형 | 돌봄, 경비, 시설관리 등 | 계약/정기 방문/갱신 | Contract, Visit, Customer, Staff | DormantCustomer 변형·RevenueGap + Renewal/Utilization Detector | 계약·갱신 데이터 모델 추가 |
| LEAD_SERVICE | 리드·상담·계약형 | 전문서비스, 부동산, 영업 등 | 문의→상담→계약 | Lead, Consultation, Proposal, Contract, Revenue | 현재 Detector 일부만 재사용 + LeadConversionGap 필요 | 향후 핵심 확장군 |
| PROJECT_SERVICE | 견적·프로젝트형 | 건설, 디자인, IT 프로젝트, 행사 등 | 견적/계약/프로젝트 | Lead, Quote, Project, Milestone, Invoice | RevenueGap 변형 + Pipeline/Utilization/RepeatClient Detector | 프로젝트 파이프라인 모델 필요 |
| FIELD_SERVICE | 현장 설치·수리형 | 정비, 설치, 세탁·청소 등 | 작업건/출장/부품·서비스 | WorkOrder, Appointment, Customer, Service, Payment | LowDemandSlot·CancellationHotspot·DormantCustomer·RevenueGap | 예약형과 유사하나 WorkOrder 계층 필요 |
| ACCOMMODATION_TRAVEL | 숙박·여행 예약형 | 숙박, 여행상품 등 | 객실/예약/여행상품 | Inventory, Booking, Customer, Payment | LowDemandSlot(점유율)·CancellationHotspot·RevenueGap·DormantCustomer | 점유율·재고 단위 어댑터 필요 |
| TRANSPORT_LOGISTICS | 운행·배달형 | 택시, 화물, 택배 등 | 운행/배송건 | Trip, Delivery, Customer, TimeSlot, Revenue | 시간대 Demand·RevenueGap + Route/Utilization Detector | 운행·노선·거리 모델 필요 |
| MANUFACTURING_PRODUCTION | 생산·수주형 | 제조, 가공, 설비 생산 등 | 생산량/수주/출하 | Order, ProductionRun, Capacity, Inventory, Shipment | 현재 Detector 호환 낮음 + Capacity/Order/Inventory Gap 필요 | 별도 도메인 Detector 필요 |
| AGRI_PRIMARY | 농림어업 생산형 | 농업, 축산, 양식 등 | 생산/출하/시세 | Production, Harvest, Shipment, Price, Weather | 현재 Detector 호환 낮음 + Seasonal/Yield/Price Detector 필요 | 공공·기상 데이터 활용도가 큼 |
| TECHNICAL_B2B | 기술·시험·연구 B2B형 | 엔지니어링, 시험, R&D 등 | 프로젝트/시험/계약 | Lead, Project, TestJob, Invoice | Project 계열 Detector 필요 | B2B 프로젝트 모델로 통합 가능 |
| PERSONAL_BRAND | 개인 창작·브랜드형 | 예술가, 선수 등 | 공연/콘텐츠/계약/스폰서 | Project, Event, Audience, Contract | 현재 Detector 호환 낮음 | 장기 확장 |
| EMPLOYMENT_SUPPORT | 고용 직무 중심 | 사무원, 기관 종사원 등 | 해당 없음 | - | - | 사업 업종으로 직접 매핑하지 않음 |
| NONCOMMERCIAL_PUBLIC | 공공·비상업 역할 | 공무원, 군인, 경찰 등 | 해당 없음 | - | - | LOOFIO 상업 고객 분류에서 제외 |

## 4.1 설계 원칙

LOOFIO는 450개 직업마다 별도의 제품을 만들지 않는다.

```text
450개 직업분류
        ↓
Archetype Family
        ↓
공통 Data Contract
        ↓
Metric Adapter
        ↓
Detector Set
```

따라서 새로운 업종을 추가하는 작업은 가능하면 **새 제품 개발**이 아니라 다음 중 하나가 되어야 한다.

1. 기존 Archetype에 매핑
2. 기존 데이터 객체에 컬럼 추가
3. Metric Adapter 추가
4. Detector 추가

---

# 5. 현재 Opportunity Engine 호환성

표기:

- `◎` 높은 호환성
- `○` 어댑터를 거쳐 활용 가능
- `△` 개념 일부 재사용 가능
- `-` 별도 Detector가 더 적합

| Family | LowDemandSlot | CancellationHotspot | DormantCustomer | RevenueGap | ServiceDemandGap |
|---|---|---|---|---|---|
| APPOINTMENT_SERVICE | ◎ | ◎ | ◎ | ◎ | ◎ |
| MEMBERSHIP_SERVICE | ○ | ○ | ◎ | ○ | ◎ |
| WALKIN_COMMERCE | ○ | △ | ○ | ◎ | ◎ |
| RECURRING_SERVICE | △ | △ | ◎ | ○ | ○ |
| LEAD_SERVICE | △ | - | ○ | ○ | △ |
| PROJECT_SERVICE | △ | △ | ○ | ○ | △ |
| FIELD_SERVICE | ◎ | ○ | ○ | ◎ | ○ |
| ACCOMMODATION_TRAVEL | ◎ | ◎ | ○ | ◎ | ○ |
| TRANSPORT_LOGISTICS | ○ | △ | ○ | ○ | ○ |
| MANUFACTURING_PRODUCTION | △ | - | △ | ○ | ○ |
| AGRI_PRIMARY | - | - | △ | △ | ○ |
| TECHNICAL_B2B | △ | - | ○ | ○ | △ |
| PERSONAL_BRAND | △ | △ | ○ | △ | △ |

현재 Opportunity Engine의 MVP 범위는 그대로 유지한다.

즉 v1에서는 다업종 전체를 동시에 구현하지 않고, **현재 Detector를 재사용할 수 있는 Family부터 구현 범위를 넓힌다.**

---

# 6. 업종에 따라 달라지는 입력

## 6.1 공통 Business Profile

모든 Archetype이 공유하는 최소 정보:

```text
business_id
business_name
occupation_code / occupation_name
archetype_family
loofio_archetype
address
business_hours
closed_days
primary_goal
```

## 6.2 Archetype별 핵심 운영 객체

```text
APPOINTMENT_SERVICE
→ Appointment

MEMBERSHIP_SERVICE
→ Membership + Session + Attendance

WALKIN_COMMERCE
→ Sale + Product

RECURRING_SERVICE
→ Contract + Visit

LEAD_SERVICE
→ Lead + Consultation + Contract

PROJECT_SERVICE
→ Quote + Project + Invoice

FIELD_SERVICE
→ WorkOrder + Appointment

ACCOMMODATION_TRAVEL
→ Inventory + Booking

TRANSPORT_LOGISTICS
→ Trip / Delivery

MANUFACTURING_PRODUCTION
→ Order + ProductionRun + Capacity + Inventory

AGRI_PRIMARY
→ Production + Harvest + Shipment + MarketPrice
```

이 구조 때문에 `Appointment`를 전체 LOOFIO의 최상위 공통 객체로 두어서는 안 된다.

최상위 공통 계층은 다음과 같이 구성한다.

```text
Business
 ├─ RevenueEvent
 ├─ Customer
 ├─ Offering
 ├─ Capacity
 ├─ MarketingAction
 ├─ ExternalContext
 ├─ Opportunity
 ├─ Recommendation
 └─ Measurement
```

각 Archetype 객체는 `RevenueEvent` 또는 별도 Domain Event를 통해 공통 Measurement 계층으로 연결한다.

---

# 7. Onboarding 분류 Flow

LOOFIO 가입 시 직업/업종 선택만으로 모든 것을 결정하지 않는다.

```text
1. 공식 분류 선택
        ↓
2. 기본 Archetype 후보 자동 제안
        ↓
3. "실제로 어떻게 돈을 버는지" 1~3문항 확인
        ↓
4. 최종 Archetype 결정
        ↓
5. 필요한 데이터 연결 방법 제시
        ↓
6. 활성화 가능한 Detector 결정
```

## 예시 A — 미용

```text
미용사
↓
APPOINTMENT_SERVICE
↓
예약 데이터를 연결해주세요
↓
LowDemandSlot
DormantCustomer
CancellationHotspot
RevenueGap
```

## 예시 B — 카페·음식

```text
음식 서비스
↓
WALKIN_COMMERCE
↓
POS / 시간대별 매출 데이터를 연결해주세요
↓
RevenueGap
ServiceDemandGap
시간대 매출 Detector
```

## 예시 C — 인테리어·시공

```text
건축 마감
↓
PROJECT_SERVICE
↓
문의 / 견적 / 계약 / 프로젝트 데이터를 연결해주세요
↓
PipelineGap
QuoteConversion
ProjectUtilization
RepeatClient
```

---

# 8. Capability Level과 Data Readiness

`Support Level`과 `Data Readiness`는 별개다.

예를 들어 `APPOINTMENT_SERVICE`는 지원 Level A라도 고객이 예약 데이터를 주지 않으면 실제 분석 능력은 낮다.

```text
Support Level
= LOOFIO가 해당 사업 모델을 얼마나 구현했는가

Data Readiness
= 해당 사업자가 얼마나 충분한 데이터를 제공했는가
```

최종 Capability는 두 값을 함께 사용한다.

예:

```text
APPOINTMENT_SERVICE
Support = A

예약 데이터 없음
Data Readiness = 1
→ 외부 데이터 + 기본 진단만 가능

예약 데이터 있음
Data Readiness = 2
→ LowDemandSlot 가능

Customer Key 있음
Data Readiness = 3
→ DormantCustomer 가능

결제 데이터 있음
Data Readiness = 4
→ 실제 RevenueGap 정밀도 상승
```

---

# 9. Database 반영 권장안

## 9.1 taxonomy tables

```text
occupation_taxonomy
business_archetypes
occupation_archetype_mappings
archetype_data_requirements
archetype_detector_compatibility
```

## 9.2 occupation_taxonomy

```text
id
keco_large_code
keco_large_name
keco_medium_code
keco_medium_name
keco_small_code
keco_small_name
keco_detail_code
keco_detail_name
ksco_detail_code
ksco_detail_name
```

## 9.3 occupation_archetype_mappings

```text
id
occupation_taxonomy_id
archetype_family
loofio_archetype
support_level
mapping_note
mapping_version
is_active
```

중요한 점은 원본 직업분류 행을 수정하지 않고 **LOOFIO 해석값을 별도 mapping table에 저장하는 것**이다.

향후 분류 기준이 바뀌어도 원본 코드와의 연결을 유지할 수 있다.

---

# 10. Opportunity Engine 연동

현재 엔진은 다음 흐름을 유지한다.

```text
Raw Data
↓
Normalization
↓
Metric Engine
↓
Opportunity Detector
↓
Opportunity Score
↓
AI Explanation
↓
User Action
```

추가되는 것은 `Archetype Router`다.

```text
Business
↓
Archetype Router
↓
Data Readiness
↓
Metric Adapter
↓
Compatible Detector Set
↓
Opportunity Engine
```

예:

```text
APPOINTMENT_SERVICE
→ appointment_metrics
→ low_demand_slot
→ dormant_customer

WALKIN_COMMERCE
→ sales_metrics
→ time_sales_gap
→ service_demand_gap

PROJECT_SERVICE
→ project_metrics
→ pipeline_gap
→ quote_conversion
```

---

# 11. 다음 Detector 확장 순서

MVP Detector는 현재 문서 기준으로 확정한다.

## v1 Current

```text
LowDemandSlot
RevenueGap
CancellationHotspot
DormantCustomer
ServiceDemandGap
```

## v1.x Adapter

다업종 확대 시 우선 검토:

```text
TimeSalesGap
MembershipRenewalGap
WorkOrderUtilizationGap
OccupancyGap
RepeatPurchaseGap
```

## v2 Domain Detector

```text
LeadConversionGap
QuoteConversionGap
PipelineGap
ContractRenewalRisk
ProjectUtilizationGap
ProductionCapacityGap
InventoryOpportunity
SeasonalDemandGap
YieldPriceOpportunity
```

새 Detector는 반드시 다음 구조를 유지한다.

```text
Observation
↓
Estimate
↓
Recommendation
```

---

# 12. 제품 정책

## 12.1 최대한 많은 업종을 수용한다

제품 초기 화면에서 특정 업종만 사용할 수 있다고 제한하지 않는다.

대신:

> **LOOFIO는 다양한 사업 형태를 지원하며, 연결된 데이터와 사업 운영 방식에 따라 발견할 수 있는 매출 기회가 달라집니다.**

라는 구조를 사용한다.

## 12.2 지원 범위를 과장하지 않는다

Level C 업종에 대해 현재 MVP 기능이 완전히 지원되는 것처럼 표시하지 않는다.

각 사업체에 대해:

```text
현재 분석 가능
추가 데이터 연결 시 가능
향후 지원 예정
```

을 구분한다.

## 12.3 직업과 사업체를 분리한다

직업분류는 사업자가 자신에게 가까운 항목을 찾기 위한 진입점이다.

실제 LOOFIO 분석은 **직업명보다 사업 운영 방식과 수익 이벤트**를 우선한다.

---

# 13. 분류 현황

## 13.1 Support Level 분포

| Level | Count |
|---|---|
| A | 17 |
| B | 154 |
| C | 211 |
| D | 68 |

## 13.2 Archetype Family 분포

| Archetype Family | 직업 세분류 수 |
|---|---|
| MANUFACTURING_PRODUCTION | 79 |
| PROJECT_SERVICE | 62 |
| EMPLOYMENT_SUPPORT | 45 |
| TECHNICAL_B2B | 41 |
| APPOINTMENT_SERVICE | 35 |
| WALKIN_COMMERCE | 32 |
| LEAD_SERVICE | 31 |
| FIELD_SERVICE | 31 |
| NONCOMMERCIAL_PUBLIC | 25 |
| MEMBERSHIP_SERVICE | 17 |
| PERSONAL_BRAND | 16 |
| RECURRING_SERVICE | 12 |
| AGRI_PRIMARY | 12 |
| TRANSPORT_LOGISTICS | 8 |
| ACCOMMODATION_TRAVEL | 4 |

이 분포는 원본 연계표의 업종 수를 의미하는 것이 아니라 **450개 직업 세분류를 LOOFIO 관점에서 어떻게 해석했는지**를 보여준다.

---

# 14. 개발 문서 순서 반영

기존 기술 로드맵의 문서 순서를 다음처럼 조정한다.

```text
01_PRODUCT_VISION.md
02_TECH_ROADMAP.md
03_BUSINESS_TAXONOMY.md      ← 현재 문서
04_DATA_SCHEMA.md
05_OPPORTUNITY_ENGINE.md
06_RECOMMENDATION_ENGINE.md
07_AI_ARCHITECTURE.md
08_MVP_SPEC.md
09_API_SPEC.md
10_MEASUREMENT_FRAMEWORK.md
```

다음 우선순위는 `04_DATA_SCHEMA.md`다.

다만 기존 `LOOFIO_OPPORTUNITY_ENGINE_V1.md`에 정의된 Minimum Data Contract를 폐기하지 않고, 이를 `APPOINTMENT_SERVICE`의 첫 번째 Domain Contract로 흡수한다.

---

# 15. v1 결정사항

1. 특정 1개 업종만을 LOOFIO의 제품 범위로 고정하지 않는다.
2. 450개 직업 세분류를 LOOFIO 내부 Archetype으로 매핑한다.
3. 직업분류와 사업 수익모델을 동일하게 취급하지 않는다.
4. 최대한 많은 분류를 장기 지원 범위에 남긴다.
5. 현재 Opportunity Engine은 그대로 MVP 기준으로 사용한다.
6. 다업종 지원은 `Archetype Router + Metric Adapter + Detector Set` 구조로 확장한다.
7. 공통 DB의 중심은 `Appointment`가 아니라 `Business + Revenue/Domain Event + Opportunity + Action + Measurement`다.
8. 공식 분류 원본과 LOOFIO 해석값을 DB에서 분리한다.
9. Level C는 지원 예정이지 현재 기능 지원 완료를 뜻하지 않는다.
10. 다음 설계 문서는 다업종을 수용하는 `DATA_SCHEMA`다.

---

# Appendix A. 450개 직업 세분류 전체 LOOFIO 매핑

> 아래 `Family`, `Archetype`, `Support`는 공식 분류가 아니라 LOOFIO v1 내부 기획값이다.

| KECO | 한국고용직업분류 세분류명 | KSCO | 한국표준직업분류 세분류명 | Family | Archetype | Support | LOOFIO 매핑 메모 |
|---|---|---|---|---|---|---|---|
| 0111 | 의회의원·고위공무원 및 공공단체임원 | 1110 | 의회의원·고위공무원 및 공공단체임원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0112 | 기업 고위임원 | 1120 | 기업 고위 임원 | LEAD_SERVICE | BUSINESS_ADMIN_B2B | C | 관리 직무 자체는 사업 업종이 아니므로 실제 수익모델 확인 필요 |
| 0121 | 정부행정 관리자 | 1211 | 정부행정 관리자 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0122 | 경영지원 관리자 | 1212 | 경영 지원 관리자 | LEAD_SERVICE | BUSINESS_ADMIN_B2B | C | 관리 직무 자체는 사업 업종이 아니므로 실제 수익모델 확인 필요 |
| 0123 | 마케팅·광고·홍보 관리자 | 1220 | 마케팅 및 광고·홍보 관리자 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | C | 마케팅·광고 서비스업으로 가능하나 직업 자체는 업종 아님 |
| 0124 | 금융·보험 관리자 | 1320 | 보험 및 금융 관리자 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | C | 금융·보험 서비스업으로 가능하나 규제 검토 필요 |
| 0131 | 연구 관리자 | 1311 | 연구 관리자 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 연구·R&D 사업으로 확장 가능 |
| 0132 | 교육 관리자 | 1312 | 교육 관리자 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육기관 운영형으로 적용 가능하나 기관 데이터 모델 필요 |
| 0133 | 법률·경찰·소방·교도 관리자 | 1313 | 법률·경찰·소방 및 교도 관리자 | LEAD_SERVICE | BUSINESS_ADMIN_B2B | C | 관리 직무 자체는 사업 업종이 아니므로 실제 수익모델 확인 필요 |
| 0134 | 보건·의료 관리자 | 1331 | 보건 의료 관련 관리자 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | C | 보건·의료 기관 운영 가능하나 규제·데이터 제약 검토 필요 |
| 0135 | 사회복지 관리자 | 1332 | 사회 복지 관련 관리자 | RECURRING_SERVICE | RECURRING_CARE_SERVICE | C | 사회복지 서비스 운영형으로 확장 가능 |
| 0136 | 예술·디자인·방송 관리자 | 1340 | 문화·예술 관련 관리자 | PROJECT_SERVICE | PROJECT_CREATIVE | C | 예술·디자인·방송 프로젝트 사업으로 확장 가능 |
| 0137 | 정보통신 관리자 | 1350 | 정보 통신 관련 관리자 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | IT 서비스·프로젝트 사업으로 확장 가능 |
| 0139 | 부동산·조사·인력알선 및 기타 전문서비스 관리자 | 1390 | 기타 전문 서비스 관리자 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 부동산·인력·조사 등 리드 기반 서비스로 적용 가능 |
| 0141 | 미용·여행·숙박·스포츠 관리자 | 1521 | 숙박·여행·오락 및 스포츠 관련 관리자 | APPOINTMENT_SERVICE | APPOINTMENT_PERSONAL_OR_LEISURE | B | 서비스 운영형 사업으로 적용 가능하나 실제 업종 확인 필요 |
| 0142 | 음식서비스 관리자 | 1522 | 음식 서비스 관련 관리자 | WALKIN_COMMERCE | FOOD_WALKIN | B | 음식서비스 운영형 사업으로 적용 가능 |
| 0143 | 경비·청소 관리자 | 1530 | 환경·청소 및 경비 관련 관리자 | RECURRING_SERVICE | RECURRING_FACILITY_CARE | B | 경비·청소 계약형 운영으로 적용 가능 |
| 0151 | 영업·판매 관리자 | 1511 | 영업 및 판매 관련 관리자 | WALKIN_COMMERCE | RETAIL_OR_SALES | B | 판매·고객서비스 사업으로 적용 가능 |
| 0152 | 운송 관리자 | 1512 | 운송관련 관리자 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | B | 운송 운영형 사업으로 적용 가능 |
| 0159 | 기타 판매 및 고객서비스 관리자 | 1590 | 기타 판매 및 고객 서비스 관리자 | WALKIN_COMMERCE | RETAIL_OR_SALES | B | 판매·고객서비스 사업으로 적용 가능 |
| 0161 | 건설·채굴 관리자 | 1411 | 건설 및 광업 관련 관리자 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | C | 프로젝트형 사업으로 확장 가능 |
| 0162 | 전기·가스·수도 관리자 | 1412 | 전기·가스 및 수도 관련 관리자 | MANUFACTURING_PRODUCTION | PRODUCTION_OR_TECH_OPERATIONS | C | 생산·설비 운영형으로 도메인별 확장 필요 |
| 0163 | 제조·생산 관리자 | 1413 | 제품 생산 관련 관리자 | MANUFACTURING_PRODUCTION | PRODUCTION_OR_TECH_OPERATIONS | C | 생산·설비 운영형으로 도메인별 확장 필요 |
| 0169 | 기타 건설·전기 및 제조 관리자 | 1490 | 기타 건설·전기 및 생산 관련 관리자 | MANUFACTURING_PRODUCTION | PRODUCTION_OR_TECH_OPERATIONS | C | 생산·설비 운영형으로 도메인별 확장 필요 |
| 0210 | 정부·공공행정 전문가 | 2620 | 정부 및 공공 행정 전문가 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0221 | 경영·진단 전문가 | 2715 | 경영 및 진단 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0222 | 인사·노무 전문가 | 2711 | 인사 및 노사 관련 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0231 | 회계사 | 2712 | 회계사 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0232 | 세무사 | 2713 | 세무사 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0233 | 관세사 | 2714 | 관세사 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0234 | 감정 전문가 | 2741 | 감정 관련 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0241 | 광고·홍보 전문가 | 2733 | 광고 및 홍보 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0242 | 조사 전문가 | 2734 | 조사 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0243 | 상품 기획자 | 2731 | 상품 기획 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | C | 독립 전문서비스·프로젝트 사업으로 적용 가능 |
| 0244 | 행사 기획자 | 2735 | 행사 기획자 | PROJECT_SERVICE | EVENT_PROJECT | B | 행사 기획 프로젝트형 사업으로 적용 가능 |
| 0251 | 조세행정 사무원 | 3111 | 조세행정 사무원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0252 | 관세행정 사무원 | 3112 | 관세행정 사무원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0253 | 병무행정 사무원 | 3113 | 병무행정 사무원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0254 | 국가·지방행정 사무원 | 3114 | 국가 및 지방 행정 사무원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0255 | 공공행정 사무원 | 3115 | 공공행정 사무원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 0261 | 기획·마케팅 사무원 | 3121 | 기획 및 마케팅 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0262 | 인사·교육·훈련 사무원 | 3122 | 인사 및 교육·훈련 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0263 | 총무 사무원 및 대학 행정조교 | 3127 | 총무 사무원 및 대학 행정조교 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0264 | 감사 사무원 | 3302 | 감사 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0271 | 회계 사무원 | 3131 | 회계 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0272 | 경리 사무원 | 3132 | 경리 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0281 | 무역 사무원 | 3125 | 무역 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0282 | 운송 사무원 | 3126 | 운송 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0283 | 자재·구매·물류 사무원 | 3123 | 자재 관리 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0284 | 생산·품질 사무원 | 3124 | 생산 및 품질 관리 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0291 | 안내·접수원 및 전화교환원 | 3922 | 안내·접수원 및 전화교환원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0292 | 고객 상담원 및 모니터 요원 | 3991 | 고객 상담 및 모니터 요원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0293 | 통계 사무원 | 3910 | 통계 관련 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0294 | 비서 | 3141 | 비서 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0295 | 전산자료 입력원 및 사무 보조원 | 3142 | 전산 자료 입력원 및 사무 보조원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0299 | 기타 사무원 | 3999 | 기타 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 사무 직무 자체를 고객 사업 업종으로 직접 사용하기 어려움 |
| 0311 | 투자·신용 분석가 | 2721 | 투자 및 신용 분석가 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0312 | 자산 운용가 | 2722 | 자산 운용가 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0313 | 보험·금융상품 개발자 | 2723 | 보험 및 금융 상품 개발자 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0314 | 증권·외환 딜러 | 2724 | 증권 및 외환 딜러 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0315 | 손해사정사 | 2725 | 손해 사정사 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | C | 리드·상담 기반 금융/보험 서비스로 확장 가능하나 규제 검토 필요 |
| 0319 | 기타 금융·보험 전문가 | 2729 | 기타 금융 및 보험 관련 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | C | 리드·상담 기반 금융/보험 서비스로 확장 가능하나 규제 검토 필요 |
| 0321 | 은행 사무원 | 3203 | 은행 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0322 | 증권 사무원 | 3204 | 증권 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0323 | 보험 심사원 및 사무원 | 3202 | 보험 심사원 및 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0324 | 출납창구 사무원 | 3201 | 출납 창구 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0325 | 수금원 및 신용 추심원 | 3205 | 수금원 및 신용 추심원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0329 | 기타 금융 사무원 | 3209 | 기타 금융 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_OR_REGULATED_FINANCE | D | 기관 고용 또는 고규제 금융 직무 성격이 강함 |
| 0331 | 대출 및 신용카드 모집인 | 5104 | 대출 및 신용카드 모집인 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | C | 리드·상담 기반 금융/보험 서비스로 확장 가능하나 규제 검토 필요 |
| 0332 | 보험 모집인 및 투자 권유 대행인 | 5103 | 보험 모집인 및 투자 권유 대행인 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | C | 리드·상담 기반 금융/보험 서비스로 확장 가능하나 규제 검토 필요 |
| 1101 | 인문과학 연구원 | 2121 | 인문과학 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 연구·시험·전문서비스형 사업으로 확장 가능 |
| 1102 | 사회과학 연구원 | 2122 | 사회과학 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 연구·시험·전문서비스형 사업으로 확장 가능 |
| 1211 | 자연과학 연구원 | 2112 | 자연과학연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 연구·시험·전문서비스형 사업으로 확장 가능 |
| 1212 | 자연과학 시험원 | 2133 | 자연과학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 연구·시험·전문서비스형 사업으로 확장 가능 |
| 1221 | 생명과학 연구원 | 2111 | 생명과학 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 연구·시험·전문서비스형 사업으로 확장 가능 |
| 1222 | 생명과학 시험원 | 2131 | 생명과학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 연구·시험·전문서비스형 사업으로 확장 가능 |
| 1223 | 농림어업 시험원 | 2132 | 농림·어업 관련 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 연구·시험·전문서비스형 사업으로 확장 가능 |
| 1311 | 컴퓨터 하드웨어 기술자 및 연구원 | 2211 | 컴퓨터 하드웨어 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 기술 서비스/프로젝트형 적용 가능 |
| 1312 | 통신공학 기술자 및 연구원 | 2212 | 통신공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 기술 서비스/프로젝트형 적용 가능 |
| 4152 | 패션 디자이너 | 2852 | 패션 디자이너 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 1320 | 컴퓨터시스템 전문가 | 2221 | 컴퓨터 시스템 전문가 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 기술 서비스/프로젝트형 적용 가능 |
| 1331 | 시스템 소프트웨어 개발자 | 2222 | 시스템 소프트웨어 개발자 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1332 | 응용 소프트웨어 개발자 | 2223 | 응용 소프트웨어 개발자 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1333 | 웹 개발자 | 2224 | 웹 개발자 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1339 | 기타 컴퓨터 전문가 및 소프트웨어 전문가 | 2229 | 기타 컴퓨터 시스템 및 소프트웨어 전문가 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1341 | 데이터 전문가 | 2231 | 데이터 전문가 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1342 | 네트워크 시스템 개발자 | 2232 | 네트워크 시스템 개발자 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1343 | 정보시스템 운영자 | 2241 | 정보 시스템 운영자 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 기술 서비스/프로젝트형 적용 가능 |
| 1344 | 웹 운영자 | 2242 | 웹 운영자 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1349 | 기타 데이터 및 네트워크 전문가 | 2239 | 기타 데이터 및 네트워크 관련 전문가 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1350 | 정보보안 전문가 | 2233 | 정보 보안 전문가 | PROJECT_SERVICE | PROJECT_TECH_B2B | C | 프로젝트·계약형 IT 서비스로 확장 가능 |
| 1360 | 통신·방송송출 장비 기사 | 2250 | 통신 및 방송 송출 장비 기사 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 기술 서비스/프로젝트형 적용 가능 |
| 1401 | 건축가 | 2311 | 건축가 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | C | 설계·측량·조경 등 프로젝트 수익모델로 확장 가능 |
| 1402 | 건축공학 기술자 | 2312 | 건축공학 기술자 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 건설 기술 서비스형으로 확장 가능 |
| 1403 | 토목공학 기술자 | 2313 | 토목공학기술자 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 건설 기술 서비스형으로 확장 가능 |
| 1404 | 조경 기술자 | 2314 | 조경 기술자 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | C | 설계·측량·조경 등 프로젝트 수익모델로 확장 가능 |
| 1405 | 도시·교통 전문가 | 2315 | 도시 및 교통 관련 전문가 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | C | 설계·측량·조경 등 프로젝트 수익모델로 확장 가능 |
| 1406 | 측량·지리정보 전문가 | 2316 | 측량 및 지리 정보 전문가 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | C | 설계·측량·조경 등 프로젝트 수익모델로 확장 가능 |
| 1407 | 건설자재 시험원 | 2317 | 건설자재 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 건설 기술 서비스형으로 확장 가능 |
| 1511 | 기계공학 기술자 및 연구원 | 2351 | 기계공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1512 | 로봇공학 기술자 및 연구원 | 2352 | 로봇공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1513 | 기계·로봇공학 시험원 | 2353 | 기계 및 로봇공학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1521 | 금속·재료공학 기술자 및 연구원 | 2331 | 금속·재료 공학 연구원 및 기술자 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1522 | 금속·재료공학 시험원 | 2332 | 금속 및 재료공학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1531 | 전기공학 기술자 및 연구원 | 2341 | 전기공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1532 | 전자공학 기술자 및 연구원 | 2342 | 전자공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1533 | 전기·전자공학 시험원 | 2343 | 전기 및 전자공학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1541 | 화학공학 기술자 및 연구원 | 2321 | 화학공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1542 | 화학공학 시험원 | 2322 | 화학공학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1551 | 가스·에너지공학 기술자 및 연구원 | 2372 | 가스·에너지 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1552 | 가스·에너지공학 시험원 | 2374 | 가스 및 에너지 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1553 | 환경공학 기술자 및 연구원 | 2371 | 환경공학기술자및연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1554 | 환경공학 시험원 | 2373 | 환경공학시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1555 | 보건위생·환경 검사원 | 2365 | 보건 위생 및 환경 검사원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1561 | 섬유공학 기술자 및 연구원 | 2392 | 섬유공학기술자및연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1562 | 섬유공학 시험원 | 2394 | 섬유공학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1571 | 식품공학 기술자 및 연구원 | 2391 | 식품공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1572 | 식품공학 시험원 | 2393 | 식품공학 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1581 | 방재 기술자 및 연구원 | 2361 | 방재 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1582 | 소방공학 기술자 및 연구원 | 2362 | 소방공학 기술자 및 연구원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1583 | 소방공학 시험원 | 2363 | 소방공학시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1584 | 산업 안전원 및 위험 관리원 | 2364 | 산업 안전 및 위험 관리원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1585 | 비파괴 검사원 | 2366 | 비파괴 검사원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1591 | 제도사 | 2395 | 제도사 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 1599 | 기타 인쇄·목재 등 공학 기술자 및 시험원 | 2399 | 기타 공학 관련 기술자 및 시험원 | TECHNICAL_B2B | TECHNICAL_B2B_SERVICE | C | 엔지니어링·시험·검사·R&D 서비스로 도메인 확장 필요 |
| 2111 | 대학 교수 | 2511 | 대학교수 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육 서비스로 확장 가능하나 고용 직무와 사업체 운영을 구분해야 함 |
| 2112 | 대학 시간강사 | 2512 | 대학 시간강사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육 서비스로 확장 가능하나 고용 직무와 사업체 운영을 구분해야 함 |
| 2121 | 중·고등학교 교사 | 2521 | 중·고등학교 교사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육 서비스로 확장 가능하나 고용 직무와 사업체 운영을 구분해야 함 |
| 2122 | 초등학교 교사 | 2522 | 초등학교 교사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육 서비스로 확장 가능하나 고용 직무와 사업체 운영을 구분해야 함 |
| 2123 | 특수교육 교사 | 2523 | 특수교육 교사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육 서비스로 확장 가능하나 고용 직무와 사업체 운영을 구분해야 함 |
| 2129 | 기타 교사 | 2599 | 기타 교사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육 서비스로 확장 가능하나 고용 직무와 사업체 운영을 구분해야 함 |
| 2130 | 유치원 교사 | 2530 | 유치원 교사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | C | 교육 서비스로 확장 가능하나 고용 직무와 사업체 운영을 구분해야 함 |
| 2141 | 문리·어학 강사 | 2541 | 문리 및 어학 강사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | A | 수업·회차·재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 2142 | 컴퓨터 강사 | 2542 | 컴퓨터 강사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | A | 수업·회차·재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 2143 | 기술·기능계 강사 | 2543 | 기술 및 기능계 강사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | A | 수업·회차·재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 2144 | 예능 강사 | 2544 | 예능 강사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | A | 수업·회차·재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 2145 | 학습지·교육교구 방문강사 | 2545 | 학습지 및 교육 교구 방문강사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | A | 수업·회차·재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 2149 | 기타 문리·기술 및 예능 강사 | 2549 | 기타 문리·기술 및 예능 강사 | MEMBERSHIP_SERVICE | MEMBERSHIP_EDUCATION | A | 수업·회차·재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 2151 | 장학관·연구관 및 교육 전문가 | 2591 | 장학관·연구관 및 교육 관련 전문가 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 교육 지원 직무 자체는 사업 업종으로 직접 매핑하기 어려움 |
| 2152 | 대학 교육 조교(연구 조교(RA) 포함) | 2592 | 대학 교육 조교 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 교육 지원 직무 자체는 사업 업종으로 직접 매핑하기 어려움 |
| 2153 | 교사보조 및 보육보조 서비스 종사원 | 4212 | 보육 및 교사 보조 서비스 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 교육 지원 직무 자체는 사업 업종으로 직접 매핑하기 어려움 |
| 2211 | 판사 및 검사 | 2611 | 판사 및 검사 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 2212 | 변호사 | 2612 | 변호사 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 상담→수임→반복 의뢰의 리드/프로젝트 구조로 적용 가능 |
| 2213 | 법무사 및 집행관 | 2613 | 법무사 및 집행관 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 상담→수임→반복 의뢰의 리드/프로젝트 구조로 적용 가능 |
| 2214 | 변리사 | 2614 | 변리사 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 상담→수임→반복 의뢰의 리드/프로젝트 구조로 적용 가능 |
| 2219 | 기타 법률 전문가 | 2619 | 기타 법률 전문가 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 상담→수임→반복 의뢰의 리드/프로젝트 구조로 적용 가능 |
| 2220 | 법률 사무원 | 3301 | 법률 관련 사무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 법률 사무 직무 자체는 사업체 업종이 아님 |
| 2311 | 사회복지사 | 2471 | 사회복지사 | RECURRING_SERVICE | RECURRING_CARE_SERVICE | C | 복지 서비스 운영에 적용 가능하나 기관/공공 영역 구분 필요 |
| 2312 | 상담 전문가 | 2474 | 상담 전문가 | APPOINTMENT_SERVICE | APPOINTMENT_PROFESSIONAL | A | 상담·예약·재방문 구조로 현재 엔진 활용 가능 |
| 2313 | 청소년 지도사 | 2475 | 청소년 지도사 | RECURRING_SERVICE | RECURRING_CARE_SERVICE | C | 복지 서비스 운영에 적용 가능하나 기관/공공 영역 구분 필요 |
| 2314 | 직업상담사 | 2473 | 직업상담사 | APPOINTMENT_SERVICE | APPOINTMENT_PROFESSIONAL | A | 상담·예약·재방문 구조로 현재 엔진 활용 가능 |
| 2315 | 시민단체 활동가 | 2476 | 시민 단체 활동가 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 수익형 소상공인 사업 분류로 직접 적용하기 어려움 |
| 2321 | 보육교사 | 2472 | 보육교사 | RECURRING_SERVICE | RECURRING_CARE_SERVICE | B | 정기 이용·재등록·수용능력 기반 서비스로 적용 가능 |
| 2329 | 기타 사회복지 종사원 | 2479 | 기타 사회복지 관련 종사원 | RECURRING_SERVICE | RECURRING_CARE_SERVICE | C | 복지 서비스 운영에 적용 가능하나 기관/공공 영역 구분 필요 |
| 2331 | 성직자 | 2481 | 성직자 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 수익형 소상공인 사업 분류로 직접 적용하기 어려움 |
| 2339 | 기타 종교 종사원 | 2489 | 기타 종교 관련 종사원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 수익형 소상공인 사업 분류로 직접 적용하기 어려움 |
| 2401 | 경찰관 및 수사관 | 4111 | 경찰관 및 수사관 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 2402 | 소방관 | 4112 | 소방관 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 2403 | 교도관 및 소년원학교 교사 | 4113 | 소년원 학교 교사 및 교도관 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 2501 | 영관급 이상 장교 | A011 | 영관급 이상 장교 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 2502 | 위관급 장교 | A012 | 위관급 장교 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 2503 | 부사관 | A020 | 부사관 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 2509 | 기타 군인 | A090 | 기타 군인 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 3011 | 전문 의사 | 2411 | 전문 의사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3012 | 일반 의사 | 2412 | 일반 의사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3013 | 한의사 | 2413 | 한의사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3014 | 치과 의사 | 2414 | 치과 의사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3020 | 수의사 | 2415 | 수의사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3030 | 약사 및 한약사 | 2420 | 약사 및 한약사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3040 | 간호사 | 2430 | 간호사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3050 | 영양사 | 2440 | 영양사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3061 | 임상병리사 | 2451 | 임상병리사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3062 | 방사선사 | 2452 | 방사선사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3063 | 치과기공사 | 2453 | 치과기공사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3064 | 치과위생사 | 2454 | 치과위생사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3065 | 물리 및 작업 치료사 | 2456 | 물리 및 작업 치료사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3066 | 임상심리사 | 2457 | 임상심리사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3067 | 재활공학 기사 | 2455 | 재활공학 기사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3069 | 기타 치료·재활사 및 의료기사 | 2459 | 기타 치료·재활사 및 의료기사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3071 | 응급구조사 | 2461 | 응급 구조사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3072 | 위생사 | 2462 | 위생사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3073 | 안경사 | 2463 | 안경사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3074 | 의무기록사 | 2464 | 의무 기록사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3075 | 간호조무사 | 2465 | 간호조무사 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 3076 | 안마사 | 2466 | 안마사 | APPOINTMENT_SERVICE | APPOINTMENT_HEALTH | B | 예약·재방문·서비스 매출 구조로 적용 가능하나 의료/의약 규제 검토 필요 |
| 3079 | 기타 보건·의료 종사원 | 4219 | 기타 돌봄 및 보건 서비스 종사원 | APPOINTMENT_SERVICE | HEALTH_EMPLOYMENT_OR_CLINIC_SUPPORT | C | 의료기관 운영 데이터에 포함 가능하나 직무 자체와 사업체 구분 필요 |
| 4111 | 작가 | 2811 | 작가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4112 | 번역가 및 통역가 | 2814 | 번역가 및 통역가 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4113 | 출판물 전문가 | 2812 | 출판물 전문가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4120 | 기자 및 언론 전문가 | 2813 | 기자 및 언론 관련 전문가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4131 | 학예사 및 문화재 보존원 | 2821 | 학예사 및 문화재 보존원 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4132 | 사서 및 기록물 관리사 | 2822 | 사서 및 기록물 관리사 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4141 | 화가 및 조각가 | 2841 | 화가 및 조각가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4142 | 사진작가 및 사진사 | 2842 | 사진기자 및 사진가 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4143 | 만화가 및 만화영화 작가 | 2843 | 만화가 및 만화영화 작가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4144 | 국악인 및 전통 예능인 | 2844 | 국악 및 전통 예능인 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4145 | 지휘자, 작곡가 및 연주가 | 2845 | 지휘자·작곡가및연주가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4146 | 가수 및 성악가 | 2846 | 가수 및 성악가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4147 | 무용가 및 안무가 | 2847 | 무용가 및 안무가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4149 | 기타 시각 및 공연 예술가 | 2849 | 기타 시각 및 공연 예술가 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4151 | 제품 디자이너 | 2851 | 제품 디자이너 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4153 | 실내장식 디자이너 | 2853 | 실내장식 디자이너 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4154 | 시각 디자이너 | 2854 | 시각 디자이너 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4155 | 미디어 콘텐츠 디자이너 | 2855 | 미디어 콘텐츠 디자이너 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4161 | 감독 및 기술감독 | 2831 | 감독 및 기술 감독 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4162 | 배우 및 모델 | 2832 | 배우 및 모델 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4163 | 아나운서 및 리포터 | 2833 | 아나운서 및 리포터 | PERSONAL_BRAND | PERSONAL_BRAND_PROJECT | C | 개인 창작/공연 수익모델은 별도 프로젝트·브랜드 모델 필요 |
| 4164 | 촬영 기사 | 2834 | 촬영기사 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4165 | 음향·녹음 기사 | 2835 | 음향 및 녹음 기사 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4166 | 영상·녹화·편집 기사 | 2836 | 영상·녹화 및 편집 기사 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4167 | 조명·영사 기사 | 2837 | 조명기사 및 영사기사 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4169 | 기타 연극·영화·방송 종사원 | 2839 | 기타 연극·영화 및 영상 관련 종사원 | PROJECT_SERVICE | PROJECT_CREATIVE | B | 프로젝트·예약·견적 기반 창작 서비스로 적용 가능 |
| 4171 | 공연·영화 및 음반 기획자 | 2881 | 공연·영화 및 음반 기획자 | PROJECT_SERVICE | EVENT_PROJECT | B | 행사·콘텐츠 프로젝트·계약형으로 적용 가능 |
| 4172 | 연예인매니저 및 스포츠매니저 | 2882 | 연예인 및 스포츠 매니저 | PROJECT_SERVICE | EVENT_PROJECT | B | 행사·콘텐츠 프로젝트·계약형으로 적용 가능 |
| 4201 | 스포츠 감독 및 코치 | 2861 | 스포츠 감독 및 코치 | MEMBERSHIP_SERVICE | MEMBERSHIP_FITNESS | A | 회차·예약·회원 재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 4202 | 직업 운동선수 | 2862 | 직업 운동선수 | PERSONAL_BRAND | PERSONAL_BRAND_EVENT | C | 개인 브랜드·스폰서·경기 수익모델로 별도 모델 필요 |
| 4203 | 경기 심판 및 경기 기록원 | 2863 | 경기 심판 및 경기 기록원 | PROJECT_SERVICE | EVENT_PROJECT | C | 경기·이벤트 단위 데이터 모델이 필요 |
| 4204 | 스포츠강사, 레크리에이션강사 및 기타 관련 전문가 | 2869 | 기타 스포츠 및 레크리에이션 관련 전문가 | MEMBERSHIP_SERVICE | MEMBERSHIP_FITNESS | A | 회차·예약·회원 재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 4209 | 기타 스포츠 및 여가서비스 종사원 | 4329 | 기타 여가서비스 종사원 | MEMBERSHIP_SERVICE | MEMBERSHIP_FITNESS | A | 회차·예약·회원 재등록 구조가 있어 현재 엔진과 높은 호환성 |
| 5111 | 이용사 | 4221 | 이용사 | APPOINTMENT_SERVICE | APPOINTMENT_PERSONAL | A | 예약·재방문·서비스별 객단가 구조로 MVP와 직접 호환 |
| 5112 | 미용사 | 4222 | 미용사 | APPOINTMENT_SERVICE | APPOINTMENT_PERSONAL | A | 예약·재방문·서비스별 객단가 구조로 MVP와 직접 호환 |
| 5113 | 피부 및 체형 관리사 | 4223 | 피부 및 체형 관리사 | APPOINTMENT_SERVICE | APPOINTMENT_PERSONAL | A | 예약·재방문·서비스별 객단가 구조로 MVP와 직접 호환 |
| 5114 | 메이크업 아티스트 및 분장사 | 4224 | 메이크업 아티스트 및 분장사 | APPOINTMENT_SERVICE | APPOINTMENT_PERSONAL | A | 예약·재방문·서비스별 객단가 구조로 MVP와 직접 호환 |
| 5115 | 반려동물 미용 및 관리 종사원 | 4291 | 반려동물 미용 및 관리 종사원 | APPOINTMENT_SERVICE | APPOINTMENT_PERSONAL | A | 예약·재방문·서비스별 객단가 구조로 MVP와 직접 호환 |
| 5119 | 기타 미용 서비스원 | 4229 | 기타 미용 관련 서비스 종사원 | APPOINTMENT_SERVICE | APPOINTMENT_PERSONAL | A | 예약·재방문·서비스별 객단가 구조로 MVP와 직접 호환 |
| 5121 | 결혼상담원 및 웨딩플래너 | 4231 | 결혼상담원 및 웨딩플래너 | PROJECT_SERVICE | EVENT_PROJECT | B | 예약·상담·행사일·계약금 구조로 적용 가능 |
| 5122 | 혼례 종사원 | 4232 | 혼례 종사원 | PROJECT_SERVICE | EVENT_PROJECT | B | 예약·상담·행사일·계약금 구조로 적용 가능 |
| 5123 | 장례 지도사 및 장례 상담원 | 4233 | 장례 상담원 및 장례 지도사 | PROJECT_SERVICE | EVENT_PROJECT | B | 예약·상담·행사일·계약금 구조로 적용 가능 |
| 5124 | 점술가 및 민속신앙 종사원 | 4292 | 점술가 및 민속신앙 종사원 | APPOINTMENT_SERVICE | APPOINTMENT_PROFESSIONAL | B | 상담/예약 기반 개인서비스로 적용 가능 |
| 5129 | 기타 개인 생활 서비스원 | 4293 | 개인 생활 서비스 종사원 | APPOINTMENT_SERVICE | APPOINTMENT_PROFESSIONAL | B | 상담/예약 기반 개인서비스로 적용 가능 |
| 5211 | 여행상품 개발자 | 2732 | 여행 상품 개발자 | ACCOMMODATION_TRAVEL | TRAVEL_BOOKING | B | 상품·예약·취소·재구매 구조로 적용 가능 |
| 5212 | 여행 사무원 | 3921 | 여행 사무원 | ACCOMMODATION_TRAVEL | TRAVEL_BOOKING | B | 상품·예약·취소·재구매 구조로 적용 가능 |
| 5213 | 여행 안내원 및 해설사 | 4321 | 여가 및 관광 서비스 종사원 | ACCOMMODATION_TRAVEL | TRAVEL_BOOKING | B | 상품·예약·취소·재구매 구조로 적용 가능 |
| 5221 | 항공기 객실승무원 | 4311 | 항공기 객실 승무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 운송기관 종사 직무 자체는 사업 업종으로 직접 매핑하기 어려움 |
| 5222 | 선박·열차 객실승무원 | 4312 | 선박 및 열차 객실 승무원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 운송기관 종사 직무 자체는 사업 업종으로 직접 매핑하기 어려움 |
| 5230 | 숙박시설 서비스원 | 4322 | 숙박시설 서비스 종사원 | ACCOMMODATION_TRAVEL | ACCOMMODATION | B | 객실/일자별 점유율·취소·재방문 분석으로 확장 가능 |
| 5240 | 오락시설 서비스원 | 4323 | 오락시설 서비스 종사원 | WALKIN_COMMERCE | LEISURE_BOOKING_OR_WALKIN | B | 시간대 수요·예약 또는 입장 매출 분석으로 적용 가능 |
| 5311 | 주방장 및 요리 연구가 | 2870 | 주방장 및 요리 연구가 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5312 | 한식 조리사 | 4411 | 한식 조리사 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5313 | 중식 조리사 | 4412 | 중식 조리사 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5314 | 양식 조리사 | 4413 | 양식 조리사 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5315 | 일식 조리사 | 4414 | 일식 조리사 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5316 | 바텐더 | 4421 | 바텐더 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5317 | 음료 조리사 | 4415 | 음료 조리사 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5319 | 기타 조리사 | 4419 | 기타 조리사 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | B | 시간대별 매출·상품수요·재방문 분석으로 현재 루프 확장 가능 |
| 5321 | 패스트푸드 준비원 | 9521 | 패스트푸드 준비원 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | C | 사업 운영 데이터에는 포함되나 해당 직무 자체는 업종이 아님 |
| 5322 | 접객원(홀서빙원) | 4422 | 웨이터 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | C | 사업 운영 데이터에는 포함되나 해당 직무 자체는 업종이 아님 |
| 5323 | 주방 보조원 | 9522 | 주방 보조원 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | C | 사업 운영 데이터에는 포함되나 해당 직무 자체는 업종이 아님 |
| 5324 | 음식 배달원 | 9223 | 음식 배달원 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | C | 사업 운영 데이터에는 포함되나 해당 직무 자체는 업종이 아님 |
| 5329 | 기타 음식 서비스 종사원 | 4429 | 기타 음식 서비스 종사원 | WALKIN_COMMERCE | FOOD_WALKIN_DELIVERY | C | 사업 운영 데이터에는 포함되나 해당 직무 자체는 업종이 아님 |
| 5411 | 경호원 | 4121 | 경호원 | RECURRING_SERVICE | RECURRING_FACILITY_SERVICE | B | 계약·현장·인력가동률·갱신 기반 서비스로 적용 가능 |
| 5412 | 청원경찰 | 4122 | 청원경찰 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 5413 | 시설·특수 경비원 | 4123 | 시설 및 특수 경비원 | RECURRING_SERVICE | RECURRING_FACILITY_SERVICE | B | 계약·현장·인력가동률·갱신 기반 서비스로 적용 가능 |
| 5419 | 기타 경호·보안 종사원 | 4129 | 기타 경호 및 보안 관련 종사원 | RECURRING_SERVICE | RECURRING_FACILITY_SERVICE | B | 계약·현장·인력가동률·갱신 기반 서비스로 적용 가능 |
| 5420 | 경비원(건물 관리원) | 9421 | 건물 관리원 | RECURRING_SERVICE | RECURRING_FACILITY_SERVICE | B | 계약·현장·인력가동률·갱신 기반 서비스로 적용 가능 |
| 5501 | 요양 보호사 및 간병인 | 4211 | 돌봄 서비스 종사원 | RECURRING_SERVICE | RECURRING_CARE_SERVICE | B | 정기 방문·시간 슬롯·재계약 구조로 적용 가능 |
| 5502 | 육아 도우미 | 9512 | 육아 도우미 | RECURRING_SERVICE | RECURRING_CARE_SERVICE | B | 정기 방문·시간 슬롯·재계약 구조로 적용 가능 |
| 5611 | 청소원 | 9411 | 청소원 | FIELD_SERVICE | FIELD_HOME_SERVICE | B | 예약/방문·반복 이용·작업건 단위로 적용 가능 |
| 5612 | 환경미화원 및 재활용품 수거원 | 9412 | 환경미화원 및 재활용품 수거원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 5613 | 배관 세정원 및 방역원 | 7991 | 배관 세정원 및 방역원 | FIELD_SERVICE | FIELD_HOME_SERVICE | B | 예약/방문·반복 이용·작업건 단위로 적용 가능 |
| 5614 | 구두 미화원 | 9991 | 구두 미화원 | FIELD_SERVICE | FIELD_HOME_SERVICE | B | 예약/방문·반복 이용·작업건 단위로 적용 가능 |
| 5615 | 세탁원(다림질원) | 9992 | 세탁원 및 다림질원 | FIELD_SERVICE | FIELD_HOME_SERVICE | B | 예약/방문·반복 이용·작업건 단위로 적용 가능 |
| 5616 | 가사 도우미 | 9511 | 가사 도우미 | FIELD_SERVICE | FIELD_HOME_SERVICE | B | 예약/방문·반복 이용·작업건 단위로 적용 가능 |
| 5621 | 계기 검침원 및 가스 점검원 | 9921 | 계기 검침원 및 가스 점검원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 5622 | 자동판매기 관리원 | 9922 | 자동판매기 관리원 | FIELD_SERVICE | FIELD_HOME_SERVICE | B | 예약/방문·반복 이용·작업건 단위로 적용 가능 |
| 5623 | 주차 관리·안내원 | 9923 | 주차 관리원 및 안내원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 5624 | 검표원 | 9422 | 검표원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 5629 | 기타 서비스 단순 종사원 | 9999 | 기타 서비스 관련 단순 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 공공·시설 고용 직무 성격이 강하거나 직접 사업 매핑이 약함 |
| 6110 | 부동산 컨설턴트 및 중개인 | 2745 | 부동산 컨설턴트 및 중개사 | LEAD_SERVICE | LEAD_PROFESSIONAL_SERVICE | B | 문의→상담→계약 전환 구조로 적용 가능 |
| 6121 | 기술 영업원 | 2743 | 기술 영업원 | LEAD_SERVICE | LEAD_SALES | B | 리드→상담→계약/구매 전환 분석으로 확장 가능 |
| 6122 | 해외 영업원 | 2742 | 해외 영업원 | LEAD_SERVICE | LEAD_SALES | B | 리드→상담→계약/구매 전환 분석으로 확장 가능 |
| 6123 | 자동차 영업원 | 5101 | 자동차 영업원 | LEAD_SERVICE | LEAD_SALES | B | 리드→상담→계약/구매 전환 분석으로 확장 가능 |
| 6124 | 제품·광고 영업원 | 5102 | 제품및광고영업원 | LEAD_SERVICE | LEAD_SALES | B | 리드→상담→계약/구매 전환 분석으로 확장 가능 |
| 6125 | 상품 중개인 및 경매사 | 2744 | 상품 중개인 및 경매사 | LEAD_SERVICE | LEAD_SALES | B | 리드→상담→계약/구매 전환 분석으로 확장 가능 |
| 6129 | 기타 기술 영업·중개 종사원 | 2749 | 기타 기술 영업 및 중개 관련 종사원 | LEAD_SERVICE | LEAD_SALES | B | 리드→상담→계약/구매 전환 분석으로 확장 가능 |
| 6130 | 텔레마케터 | 5313 | 텔레마케터 | LEAD_SERVICE | LEAD_SALES | B | 리드→상담→계약/구매 전환 분석으로 확장 가능 |
| 6140 | 소규모 상점 경영 및 일선 관리 종사원 | 5211 | 소규모 상점 경영 및 일선 관리 종사원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6151 | 상점 판매원 | 5212 | 상점 판매원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6152 | 통신 기기·서비스 판매원 | 5311 | 단말기 및 통신 서비스 판매원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6153 | 온라인 판매원 | 5312 | 온라인쇼핑판매원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6154 | 상품 대여원 | 5220 | 상품 대여원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6155 | 노점 및 이동 판매원 | 5322 | 노점 및 이동 판매원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6156 | 방문 판매원 | 5321 | 방문 판매원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6157 | 주유원(가스충전원) | 9531 | 주유원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6161 | 매장 계산원 및 요금 정산원 | 5214 | 매장 계산원 및 요금 정산원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6162 | 매표원 및 복권 판매원 | 5213 | 매표원 및 복권 판매원 | WALKIN_COMMERCE | RETAIL_COMMERCE | B | 시간대·상품·재구매·객단가 분석으로 적용 가능 |
| 6171 | 홍보 도우미 및 판촉원 | 5323 | 홍보 도우미 및 판촉원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | C | 판매 활동 데이터에는 포함되나 직무 자체는 업종과 다름 |
| 6179 | 기타 판매 단순 종사원 | 9539 | 기타 판매 관련 단순 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | C | 판매 활동 데이터에는 포함되나 직무 자체는 업종과 다름 |
| 6211 | 항공기 조종사 | 2381 | 항공기 조종사 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | C | 운항·운송 사업으로 가능하나 인허가·기업형 운영 제약 큼 |
| 6212 | 선장, 항해사 및 도선사 | 2382 | 선장·항해사 및 도선사 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | C | 운항·운송 사업으로 가능하나 인허가·기업형 운영 제약 큼 |
| 6213 | 철도·전동차 기관사 | 8710 | 철도 및 전동차 기관사 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 대중교통·기관 고용 직무 성격이 강함 |
| 6214 | 관제사 | 2383 | 관제사 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 대중교통·기관 고용 직무 성격이 강함 |
| 6219 | 기타 철도운송 종사원 | 8720 | 철도운송 관련 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 대중교통·기관 고용 직무 성격이 강함 |
| 6221 | 택시 운전원 | 8731 | 택시 운전원 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | B | 운행/배달 건·시간대 수요·재구매 분석으로 확장 가능 |
| 6222 | 버스 운전원 | 8732 | 버스 운전원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 대중교통·기관 고용 직무 성격이 강함 |
| 6223 | 화물차·특수차 운전원 | 8733 | 화물차및특수차운전원 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | B | 운행/배달 건·시간대 수요·재구매 분석으로 확장 가능 |
| 6229 | 기타 자동차 운전원 | 8739 | 기타 자동차 운전원 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | B | 운행/배달 건·시간대 수요·재구매 분석으로 확장 가능 |
| 6230 | 물품이동장비 조작원(크레인·호이스트·지게차) | 8740 | 물품 이동 장비 조작원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 대중교통·기관 고용 직무 성격이 강함 |
| 6241 | 택배원 | 9222 | 택배원 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | B | 운행/배달 건·시간대 수요·재구매 분석으로 확장 가능 |
| 6242 | 우편물 집배원 | 9221 | 우편집배원 | NONCOMMERCIAL_PUBLIC | NONCOMMERCIAL_OR_PUBLIC_ROLE | D | 공공·고용 역할 성격이 강해 사업 업종으로 직접 매핑하지 않음 |
| 6243 | 선박승무원 및 관련 종사원(선박객실 승무원 제외) | 8760 | 선박승무원및관련종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 대중교통·기관 고용 직무 성격이 강함 |
| 6244 | 하역·적재 종사원 | 9210 | 하역 및 적재 단순 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 대중교통·기관 고용 직무 성격이 강함 |
| 6249 | 기타 배달원 | 9229 | 기타 배달원 | TRANSPORT_LOGISTICS | TRANSPORT_DELIVERY | B | 운행/배달 건·시간대 수요·재구매 분석으로 확장 가능 |
| 7011 | 강구조물 가공원 및 건립원 | 7811 | 강구조물가공원및건립원 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7012 | 경량철골공 | 7812 | 경량 철골공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7013 | 철근공 | 7821 | 철근공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7014 | 콘크리트공 | 7822 | 콘크리트공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7015 | 건축 석공 | 7823 | 건축 석공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7016 | 건축 목공 | 7824 | 건축 목공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7017 | 조적공 및 석재부설원 | 7825 | 조적공 및 석재 부설원 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7019 | 기타 건설 구조 기능원 | 7829 | 기타 건설 관련 기능 종사원 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7021 | 미장공 | 7831 | 미장공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7022 | 방수공 | 7832 | 방수공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7023 | 단열공 | 7833 | 단열공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7024 | 바닥재 시공원 | 7834 | 바닥재시공원 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7025 | 도배공 및 유리 부착원 | 7835 | 도배공 및 유리 부착원 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7026 | 건축 도장공 | 7836 | 건축 도장공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7027 | 새시 조립·설치원 | 7837 | 새시 조립 및 설치원 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7029 | 기타 건축 마감 기능원 | 7839 | 기타 건축 마감 관련 기능 종사원 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7031 | 건설 배관공 | 7921 | 건설 배관공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7032 | 공업 배관공 | 7922 | 공업 배관공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7039 | 기타 배관공 | 7929 | 기타 배관공 | PROJECT_SERVICE | CONSTRUCTION_PROJECT | B | 견적·현장·공정·재의뢰 기반 프로젝트 서비스로 적용 가능 |
| 7040 | 건설·채굴 기계 운전원 | 8750 | 건설 및 채굴기계 운전원 | FIELD_SERVICE | FIELD_EQUIPMENT_SERVICE | C | 장비 임대/작업건 사업으로 확장 가능하나 직무 확인 필요 |
| 7051 | 광원, 채석원 및 석재 절단원 | 7841 | 광원·채석원 및 석재 절단원 | MANUFACTURING_PRODUCTION | PRODUCTION_OR_RESOURCE | C | 채굴·토목 생산/프로젝트형으로 별도 모델 필요 |
| 7052 | 철로 설치·보수원 | 7842 | 철로 설치 및 보수원 | MANUFACTURING_PRODUCTION | PRODUCTION_OR_RESOURCE | C | 채굴·토목 생산/프로젝트형으로 별도 모델 필요 |
| 7059 | 기타 채굴·토목 종사원 | 7849 | 기타 채굴 및 토목 관련 종사원 | MANUFACTURING_PRODUCTION | PRODUCTION_OR_RESOURCE | C | 채굴·토목 생산/프로젝트형으로 별도 모델 필요 |
| 7060 | 건설·채굴 단순 종사원 | 9100 | 건설 및 광업 단순 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 단순 종사 직무 자체는 사업 업종으로 직접 매핑하기 어려움 |
| 8111 | 공업기계 설치·정비원 | 7531 | 공업기계 설치 및 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8112 | 승강기 설치·정비원 | 7532 | 승강기 설치 및 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8113 | 물품이동장비 설치·정비원 | 7533 | 물품 이동 장비 설치 및 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8114 | 냉동·냉장·공조기 설치·정비원 | 7534 | 냉동·냉장·공조기 설치 및 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8115 | 보일러 설치·정비원 | 7535 | 보일러 설치 및 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8116 | 건설·광업 기계 설치·정비원 | 7536 | 건설 및 광업기계 설치 및 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8119 | 농업용 및 기타 기계장비 설치·정비원 | 7539 | 농업용 및 기타 기계장비 설치 및 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8121 | 항공기 정비원 | 7521 | 항공기 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8122 | 선박 정비원 | 7522 | 선박 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8123 | 철도기관차·전동차 정비원 | 7523 | 철도 기관차 및 전동차 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8124 | 자동차 정비원 | 7510 | 자동차 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8129 | 기타 운송장비 정비원 | 7529 | 기타 운송장비 정비원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 작업예약·수리건·재방문·부품매출 구조로 적용 가능 |
| 8131 | 금형원 | 7411 | 금형원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8132 | 금속 공작기계 조작원 | 8510 | 금속 공작 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8140 | 냉·난방 설비 조작원 | 8520 | 냉난방 관련 설비 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8150 | 자동조립라인·산업용로봇 조작원 | 8530 | 자동 조립라인 및 산업용로봇 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8161 | 일반기계 조립원 | 8544 | 일반기계 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8162 | 금속기계부품 조립원 | 8550 | 금속기계 부품 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8171 | 자동차 조립원 | 8541 | 자동차 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8172 | 자동차 부분품 조립원 | 8542 | 자동차 부품 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8173 | 운송장비 조립원 | 8543 | 운송장비조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산 capacity·주문·재고 중심 Detector가 필요 |
| 8211 | 금속가공 제어장치 조작원 | 8414 | 금속가공 관련 제어 장치 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8212 | 금속가공 기계 조작원 | 8415 | 금속가공 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8221 | 판금원 | 7422 | 판금원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8222 | 판금기조작원 | 8417 | 판금기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8223 | 제관원 | 7421 | 제관원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8224 | 제관기조작원 | 8416 | 제관기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8231 | 단조원 | 7413 | 단조원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8232 | 단조기조작원 | 8412 | 단조기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8233 | 주조원 | 7412 | 주조원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8234 | 주조기조작원 | 8411 | 주조기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8241 | 용접원 | 7430 | 용접원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8242 | 용접기조작원 | 8413 | 용접기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8251 | 도장원(도장기조작원) | 8421 | 도장기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8252 | 도금·금속분무기 조작원 | 8422 | 도금 및 금속 분무기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8261 | 유리·유리제품 생산기계 조작원 | 8431 | 유리 제조 및 가공기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8623 | 재봉사 | 7213 | 재봉사 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8262 | 점토제품 생산기계 조작원 | 8432 | 점토제품 생산기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8263 | 시멘트·광물제품 생산기계 조작원 | 8433 | 시멘트 및 광물제품 제조기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8264 | 광석·석제품 생산기계 조작원 | 8434 | 광석 및 석제품 가공기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8269 | 기타 비금속제품 생산기계 조작원 | 8439 | 기타 비금속제품 관련 생산기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·수주·재고 중심 Detector가 필요 |
| 8311 | 산업 전기공 | 7621 | 산업 전기공 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·재방문 구조로 적용 가능 |
| 8312 | 내선 전기공 | 7622 | 내선 전기공 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·재방문 구조로 적용 가능 |
| 8313 | 외선 전기공 | 7623 | 외선 전기공 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·재방문 구조로 적용 가능 |
| 8321 | 사무용 전자기기 설치·수리원 | 7611 | 사무용 전자기기 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·재방문 구조로 적용 가능 |
| 8322 | 가전제품 설치·수리원 | 7612 | 가전제품 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·재방문 구조로 적용 가능 |
| 8329 | 기타 전기·전자 기기 설치·수리원 | 7619 | 기타 전기·전자기기 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·재방문 구조로 적용 가능 |
| 8330 | 발전·배전 장치 조작원 | 8610 | 발전 및 배전장치 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 설비/생산 운영형 Detector가 필요 |
| 8340 | 전기·전자 설비 조작원 | 8620 | 전기 및 전자설비 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 설비/생산 운영형 Detector가 필요 |
| 8351 | 전기 부품·제품 생산기계 조작원 | 8631 | 전기 부품 및 제품 제조 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 설비/생산 운영형 Detector가 필요 |
| 8352 | 전자 부품·제품 생산기계 조작원 | 8632 | 전자 부품 및 제품 제조 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 설비/생산 운영형 Detector가 필요 |
| 8360 | 전기·전자 부품·제품 조립원 | 8640 | 전기·전자 부품 및 제품 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 설비/생산 운영형 Detector가 필요 |
| 8411 | 컴퓨터 설치·수리원 | 7711 | 컴퓨터 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·고객 재의뢰 구조로 적용 가능 |
| 8412 | 이동전화기 수리원 | 7712 | 이동전화기 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·고객 재의뢰 구조로 적용 가능 |
| 8419 | 기타 정보통신기기 설치·수리원 | 7719 | 기타 정보 통신기기 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·고객 재의뢰 구조로 적용 가능 |
| 8421 | 방송장비 설치·수리원 | 7721 | 방송 및 관련 장비 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·고객 재의뢰 구조로 적용 가능 |
| 8422 | 통신장비 설치·수리원 | 7722 | 통신 및 관련 장비 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·고객 재의뢰 구조로 적용 가능 |
| 8423 | 방송·통신·인터넷 케이블 설치·수리원 | 7723 | 통신·방송 및 인터넷케이블 설치 및 수리원 | FIELD_SERVICE | FIELD_MAINTENANCE | B | 설치·수리 작업건·고객 재의뢰 구조로 적용 가능 |
| 8511 | 석유·천연가스 제조 제어장치 조작원 | 8311 | 석유 및 천연가스 제조 관련 제어 장치 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8512 | 화학물 가공장치 조작원 | 8312 | 화학물 가공 장치 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8519 | 기타 석유·화학물 가공장치 조작원 | 8319 | 기타 석유 및 화학물 가공 장치 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8521 | 타이어·고무제품 생산기계 조작원 | 8322 | 타이어 및 고무제품 생산기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8522 | 플라스틱제품 생산기계 조작원 | 8323 | 플라스틱제품 생산기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8523 | 화학제품 생산기계 조작원(고무·플라스틱 제외) | 8321 | 화학제품 생산기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8524 | 고무·플라스틱 제품 조립원 | 8324 | 고무 및 플라스틱제품 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8531 | 상·하수도 처리장치 조작원 | 8810 | 상하수도 처리 장치 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8532 | 재활용 처리장치·소각로 조작원 | 8820 | 재활용 처리 및 소각로 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·처리량·가동률 중심 도메인 모델이 필요 |
| 8611 | 섬유 제조기계 조작원 | 8211 | 섬유 제조 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·주문 중심 Detector가 필요 |
| 8612 | 직조기·편직기 조작원 | 8221 | 직조기 및 편직기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·주문 중심 Detector가 필요 |
| 8613 | 표백·염색기 조작원 | 8212 | 표백 및 염색 관련 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·주문 중심 Detector가 필요 |
| 8621 | 패턴사 | 7211 | 패턴사 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8622 | 재단사 | 7212 | 재단사 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8629 | 기타 섬유·가죽 기능원 | 7219 | 기타 섬유 및 가죽 관련 기능 종사원 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8631 | 한복 제조원 | 7221 | 한복 제조원 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8632 | 양장·양복 제조원 | 7222 | 양장 및 양복 제조원 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8633 | 모피·가죽의복 제조원 | 7223 | 모피 및 가죽 의복 제조원 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8634 | 의복·가죽·모피 수선원 | 7224 | 의복·가죽 및 모피 수선원 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8639 | 기타 의복 제조원 | 7229 | 기타 의복 제조 관련 기능 종사원 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8641 | 제화원 | 7214 | 제화원 | MANUFACTURING_PRODUCTION | MANUFACTURING_OR_CUSTOM_PRODUCTION | C | 맞춤제작·수선은 서비스형, 대량생산은 생산형으로 추가 구분 필요 |
| 8642 | 신발 제조기계 조작원 및 조립원 | 8222 | 신발 제조기 조작원 및 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·주문 중심 Detector가 필요 |
| 8643 | 세탁 기계 조작원 | 8230 | 세탁 관련 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·주문 중심 Detector가 필요 |
| 8649 | 기타 직물·신발 기계 조작원 및 조립원 | 8229 | 기타 직물 및 신발관련 기계 조작원 및 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·가동률·주문 중심 Detector가 필요 |
| 8711 | 제과·제빵원 | 7101 | 제빵사 및 제과원 | WALKIN_COMMERCE | FOOD_PRODUCTION_RETAIL | B | 생산량·상품판매·반복구매를 결합해 적용 가능 |
| 8712 | 떡 제조원 | 7102 | 떡 제조원 | WALKIN_COMMERCE | FOOD_PRODUCTION_RETAIL | B | 생산량·상품판매·반복구매를 결합해 적용 가능 |
| 8721 | 정육원 및 도축원 | 7103 | 정육가공원 및 도축원 | WALKIN_COMMERCE | FOOD_PRODUCTION_RETAIL | B | 생산량·상품판매·반복구매를 결합해 적용 가능 |
| 8722 | 김치·밑반찬 제조 종사원 | 7105 | 김치 및 밑반찬 제조 종사원 | WALKIN_COMMERCE | FOOD_PRODUCTION_RETAIL | B | 생산량·상품판매·반복구매를 결합해 적용 가능 |
| 8723 | 식품·담배 등급원 | 7104 | 식품 및 담배 등급원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산설비·주문·재고 중심 Detector가 필요 |
| 8729 | 기타 식품 가공 종사원 | 7109 | 기타 식품가공 관련 종사원 | WALKIN_COMMERCE | FOOD_PRODUCTION_RETAIL | B | 생산량·상품판매·반복구매를 결합해 적용 가능 |
| 8731 | 육류·어패류·낙농품 가공기계 조작원 | 8113 | 육류·어패류 및 낙농품 가공 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산설비·주문·재고 중심 Detector가 필요 |
| 8732 | 제분·도정 기계 조작원 | 8111 | 제분 및 도정 관련 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산설비·주문·재고 중심 Detector가 필요 |
| 8733 | 곡물 가공제품 기계 조작원 | 8112 | 곡물가공제품 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산설비·주문·재고 중심 Detector가 필요 |
| 8734 | 과실·채소 기계 조작원 | 8114 | 과실 및 채소 가공 관련 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산설비·주문·재고 중심 Detector가 필요 |
| 8735 | 음료 제조기계 조작원 | 8120 | 음료제조관련기계조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산설비·주문·재고 중심 Detector가 필요 |
| 8739 | 기타 식품 가공 기계 조작원 | 8190 | 기타 식품가공 관련 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산설비·주문·재고 중심 Detector가 필요 |
| 8811 | 인쇄기계 조작원 | 8921 | 인쇄기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8812 | 사진 인화·현상기 조작원(사진수정 포함) | 8922 | 사진 인화 및 현상기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8821 | 목재 가공기계 조작원 | 8911 | 목재가공 관련 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8822 | 펄프·종이 제조장치 조작원 | 8913 | 펄프 및 종이 제조 장치 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8823 | 종이제품 생산기계 조작원 | 8914 | 종이제품 생산기 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8829 | 기타 목재·종이 기계 조작원 | 8919 | 기타 목재 및 종이 관련 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8831 | 가구 제조·수리원 | 7302 | 가구 제조 및 수리원 | PROJECT_SERVICE | CUSTOM_PRODUCTION_PROJECT | B | 주문제작·수리·견적·반복구매 구조로 적용 가능 |
| 8832 | 가구 조립원 | 8912 | 가구 조립원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8833 | 목제품 제조원 | 7301 | 목제품 제조 관련 종사원 | PROJECT_SERVICE | CUSTOM_PRODUCTION_PROJECT | B | 주문제작·수리·견적·반복구매 구조로 적용 가능 |
| 8841 | 공예원 | 7911 | 공예원 | PROJECT_SERVICE | CUSTOM_PRODUCTION_PROJECT | B | 주문제작·수리·견적·반복구매 구조로 적용 가능 |
| 8842 | 귀금속·보석 세공원 | 7912 | 귀금속 및 보석 세공원 | PROJECT_SERVICE | CUSTOM_PRODUCTION_PROJECT | B | 주문제작·수리·견적·반복구매 구조로 적용 가능 |
| 8851 | 악기 제조원 및 조율사 | 7303 | 악기 제조 및 조율사 | PROJECT_SERVICE | CUSTOM_PRODUCTION_PROJECT | B | 주문제작·수리·견적·반복구매 구조로 적용 가능 |
| 8852 | 간판 제작·설치원 | 7304 | 간판 제작 및 설치원 | PROJECT_SERVICE | CUSTOM_PRODUCTION_PROJECT | B | 주문제작·수리·견적·반복구매 구조로 적용 가능 |
| 8853 | 유리기능, 복사, 수제 제본 등 기타 기능 종사원 | 7999 | 기타 기능 관련 종사원 | PROJECT_SERVICE | CUSTOM_PRODUCTION_PROJECT | B | 주문제작·수리·견적·반복구매 구조로 적용 가능 |
| 8859 | 주입·포장·상표부착기 및 기타 기계 조작원 | 8990 | 기타 기계 조작원 | MANUFACTURING_PRODUCTION | MANUFACTURING_PRODUCTION | C | 생산·주문·가동률 중심 Detector가 필요 |
| 8900 | 제조 단순 종사원 | 9300 | 제조 관련 단순 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 단순 생산 직무 자체는 사업체 업종으로 직접 매핑하기 어려움 |
| 9011 | 곡식작물 재배원 | 6111 | 곡식작물 재배원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9012 | 채소·특용작물 재배원 | 6112 | 채소 및 특용작물 재배원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9013 | 과수작물 재배원 | 6113 | 과수작물 재배원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9014 | 원예작물 재배원 | 6121 | 원예작물 재배원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9015 | 조경원 | 6122 | 조경원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9021 | 낙농 종사원 | 6131 | 낙농업 관련 종사원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9022 | 가축 사육 종사원 | 6132 | 가축 사육 종사원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9029 | 기타 사육 종사원 | 6139 | 기타 사육 관련 종사원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9031 | 조림·산림경영인 및 벌목원 | 6201 | 조림·산림경영인 및 벌목원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9039 | 임산물 채취 및 기타 임업 종사원 | 6209 | 임산물 채취 및 기타 임업 관련 종사원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9041 | 양식원 | 6301 | 양식원 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9042 | 어부 및 해녀 | 6302 | 어부 및 해녀 | AGRI_PRIMARY | AGRI_PRIMARY_PRODUCTION | C | 생산·출하·시세·계절성 중심 별도 Opportunity Detector가 필요 |
| 9050 | 농림어업 단순 종사원 | 9910 | 농림·어업 관련 단순 종사원 | EMPLOYMENT_SUPPORT | EMPLOYMENT_SUPPORT_ROLE | D | 단순 종사 직무 자체는 사업 업종으로 직접 매핑하기 어려움 |

---

# Appendix B. 분류 검토 원칙

다음 조건이 발견되면 개별 매핑을 재검토한다.

- 같은 직업 코드가 실제로 서로 다른 수익모델을 갖는 경우
- 프랜차이즈/개인사업/기관고용 여부에 따라 데이터 구조가 크게 달라지는 경우
- 인허가·광고·의료·금융 등 규제 때문에 추천 가능 범위가 달라지는 경우
- 실제 고객 인터뷰에서 직업명과 사업자 자가 인식이 크게 다른 경우
- 새로운 Detector가 추가되어 Support Level을 상향할 수 있는 경우

모든 변경은 `mapping_version`으로 추적한다.
