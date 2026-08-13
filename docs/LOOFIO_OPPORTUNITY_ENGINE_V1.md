# LOOFIO Opportunity Engine v1

## 1. 문서 목적

이 문서는 LOOFIO의 초기 제품 방향과 MVP 분석 엔진 구조를 정리한 설계 문서다.

LOOFIO의 핵심 목표는 소상공인이 보유한 예약·매출·고객 데이터를 기반으로
**현재 놓치고 있는 매출 기회를 탐지하고, 실행 가능한 액션으로 변환하는 것**이다.

핵심 원칙은 다음과 같다.

> **AI가 기회를 임의로 만들어내는 것이 아니라, 코드가 데이터에서 기회를 탐지하고 AI는 이를 설명한다.**

---

# 2. 제품 핵심 방향

LOOFIO는 단순 마케팅 콘텐츠 생성 도구가 아니라 다음 흐름을 목표로 한다.

```text
사업장 데이터
    ↓
예약 / 매출 / 고객 데이터
    ↓
외부 데이터 결합
    ↓
지표 계산
    ↓
매출 기회 탐지
    ↓
실행 제안
    ↓
결과 측정
    ↓
다시 분석
```

이를 하나의 반복 구조로 정의한다.

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
   └──────────→ 다시 Observe
```

---

# 3. 현실적으로 받을 수 있는 소상공인 데이터

소상공인에게 많은 정보를 직접 입력하게 만드는 방식은 지양한다.

초기 입력은 최소화하고,
가능한 데이터는 예약 시스템, POS, Excel/CSV 또는 외부 데이터에서 가져온다.

## 3.1 사업자가 직접 입력하는 기본 정보

### 필수

- 업종
- 사업장 주소
- 영업시간
- 휴무일
- 주요 서비스
- 서비스 가격

### 권장

- 동시 서비스 가능 인원
- 직원 수
- 서비스별 예상 소요시간
- 현재 가장 해결하고 싶은 문제

예:

```text
신규 고객을 늘리고 싶음
재방문 고객을 늘리고 싶음
한가한 시간대 매출을 올리고 싶음
객단가를 높이고 싶음
AI가 문제를 찾아주길 원함
```

---

# 4. 데이터 입력 전략

초기 MVP에서는 직접 API 연동보다 다음 흐름을 우선한다.

```text
네이버 예약
POS
Excel
CSV
직접 입력
    │
    ▼
Import / Mapping Layer
    │
    ▼
LOOFIO 표준 데이터
```

핵심은 외부 시스템마다 다른 컬럼을
LOOFIO 내부 표준 스키마로 정규화하는 것이다.

예:

```text
원본: 이용일
→ visit_start_at

원본: 예약상품
→ service_name

원본: 예약상태
→ status

원본: 휴대폰번호
→ customer_key
```

---

# 5. LOOFIO Minimum Data Contract v1

LOOFIO의 표준 데이터 객체는 다음과 같이 구성한다.

```text
Business
Service
Appointment
Customer
Payment
External Context
```

---

# 6. Business

사업장 자체에 대한 정보다.

## 필수 필드

| 필드 | 설명 | 예시 |
|---|---|---|
| business_id | 내부 사업장 ID | BIZ_0001 |
| industry | 업종 | 미용실 |
| address | 사업장 주소 | 서울 마포구 |
| business_hours | 영업시간 | 10:00~20:00 |
| closed_days | 휴무일 | 일요일 |

## 권장 필드

| 필드 | 설명 |
|---|---|
| capacity | 동시 서비스 가능 고객 수 |
| employee_count | 직원 수 |

capacity는 실제 가동률 및 빈 슬롯 계산에 중요하다.

---

# 7. Service

사업장이 판매하는 서비스 또는 상품이다.

| 필드 | 필수 여부 | 설명 |
|---|---|---|
| service_id | 필수 | 서비스 ID |
| service_name | 필수 | 서비스명 |
| list_price | 필수 | 판매 가격 |
| duration_minutes | 권장 | 예상 서비스 시간 |
| category | 선택 | 서비스 카테고리 |

예:

```json
{
  "service_id": "S001",
  "service_name": "여성 커트",
  "list_price": 30000,
  "duration_minutes": 60
}
```

---

# 8. Appointment

LOOFIO MVP에서 가장 중요한 데이터다.

## 필수 필드

| 필드 | 설명 |
|---|---|
| appointment_id | 예약 식별자 |
| visit_start_at | 방문 또는 예약 시작 시간 |
| service_name | 서비스명 |
| status | 예약 상태 |

## 권장 필드

| 필드 | 설명 |
|---|---|
| customer_key | 고객 식별자 |
| staff_name | 담당 직원 |
| visit_end_at | 서비스 종료 시간 |
| booked_at | 예약 생성 시간 |
| listed_price | 정가 |
| paid_amount | 실제 결제 금액 |
| discount_amount | 할인 금액 |
| source | 데이터 출처 |
| source_record_id | 외부 시스템의 원본 ID |

---

# 9. 예약 상태 표준화

외부 시스템마다 다른 상태값을 LOOFIO 내부 값으로 통합한다.

```text
booked
completed
cancelled
no_show
unknown
```

예:

```text
이용완료
방문완료
결제완료
    ↓
completed
```

---

# 10. Customer

고객 데이터는 직접 입력받기보다 예약 및 결제 데이터에서 생성한다.

개인정보 자체보다 동일 고객을 식별할 수 있는 값이 중요하다.

예:

```text
010-1234-5678
    ↓
Hash / Tokenize
    ↓
C_8F91A72
```

Customer에서 계산할 수 있는 항목:

- 최초 방문일
- 마지막 방문일
- 방문 횟수
- 평균 재방문 간격
- 누적 매출
- 선호 서비스
- 최근 미방문 기간

---

# 11. Payment

POS 등 실제 결제 정보가 있을 때 추가한다.

MVP 필수 데이터는 아니다.

예:

```text
transaction_id
paid_at
appointment_id
customer_key
service
amount
discount
payment_status
```

Payment 데이터가 존재하면
예약 중심 분석을 실제 매출 중심 분석으로 확장할 수 있다.

---

# 12. External Context

사업자가 직접 입력하지 않는 외부 환경 데이터다.

예:

- 상권
- 유동인구
- 지역 인구
- 연령대
- 경쟁 업체
- 날씨
- 공휴일
- 지역 행사
- 관광객
- 상권 변화

외부 데이터는 주로 Business.address를 기준으로 결합한다.

---

# 13. 데이터 준비도

LOOFIO는 데이터 양에 따라 분석 수준이 달라진다.

## Level 1

```text
업종
주소
영업시간
서비스
가격
```

가능한 분석:

- 외부 상권 기반 분석
- 기본 사업장 진단

신뢰도: 낮음

## Level 2

```text
+ 예약 데이터
```

가능한 분석:

- 요일별 예약량
- 시간대별 예약량
- 취소율
- 저수요 시간대

신뢰도: 중간

## Level 3

```text
+ Customer Key
```

가능한 분석:

- 신규 / 기존 고객
- 재방문율
- 재방문 주기
- 장기 미방문 고객

신뢰도: 높음

## Level 4

```text
+ 결제 데이터
```

가능한 분석:

- 실제 객단가
- 시간대별 매출
- 서비스별 매출
- 예상 기회 매출

---

# 14. Opportunity Engine 구조

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

---

# 15. 핵심 설계 원칙

## 15.1 LLM이 직접 원본 데이터를 분석하지 않는다

잘못된 방식:

```text
예약 데이터 10,000건
    ↓
LLM
    ↓
"문제점을 찾아줘"
```

권장 방식:

```text
예약 데이터
    ↓
Backend / SQL / Python
    ↓
Metric 계산
    ↓
Opportunity 탐지
    ↓
구조화된 JSON
    ↓
LLM
    ↓
자연어 설명 및 액션 제안
```

---

# 16. Metric Engine

Detector보다 먼저 공통 지표를 계산한다.

예:

- 요일별 예약 건수
- 시간대별 예약 건수
- 서비스별 예약 건수
- 평균 객단가
- 시간대별 취소율
- 고객별 방문 횟수
- 고객별 마지막 방문일
- 고객별 평균 재방문 간격
- 시간대별 가동률
- 시간대별 매출

---

# 17. 기본 분석 단위

MVP 기본값:

```text
요일 × 2시간 단위
```

예:

```text
월 10~12시
월 12~14시
월 14~16시
월 16~18시
월 18~20시
```

분석 데이터 기간:

```text
최소: 최근 8주
권장: 최근 12주
```

---

# 18. Detector 1 — LowDemandSlot

목적:

> 반복적으로 예약 수요가 낮은 시간대를 탐지한다.

capacity 데이터가 없다면 상대 수요를 이용한다.

## Demand Index

```text
DemandIndex =
해당 시간대 평균 예약 수
÷
비교 시간대 중앙값
```

예:

```text
화요일 14~16시 평균 예약 = 1.7
화요일 비교 시간대 중앙값 = 4.0

DemandIndex = 0.425
```

MVP 후보 조건 예시:

```text
관측 주차 >= 8
AND
DemandIndex <= 0.65
```

---

# 19. Capacity 기반 LowDemandSlot

capacity와 서비스 시간이 있다면 실제 가동률을 계산한다.

예:

```text
직원 3명
분석 시간 2시간

총 가능 시간 = 360분
실제 예약 시간 = 120분

Occupancy Rate = 33.3%
```

capacity 데이터가 있을 때는
단순 예약 수보다 가동률을 우선 사용한다.

---

# 20. Detector 2 — CancellationHotspot

목적:

> 특정 요일, 시간대, 서비스에서 반복적으로 높은 취소율을 탐지한다.

계산식:

```text
CancellationRate =
취소 예약 수
÷
전체 예약 수
```

절대값만 사용하지 않고
사업장 전체 취소율과 비교한다.

예:

```text
전체 취소율 = 8%
금요일 18~20시 = 27%
```

후보 조건 예시:

```text
예약 샘플 >= 15
AND
시간대 취소율 >= 전체 취소율 × 1.5
```

---

# 21. Detector 3 — DormantCustomer

목적:

> 평소 재방문할 시기를 지났지만 아직 방문하지 않은 고객을 탐지한다.

기준 우선순위:

```text
1. 고객 개인 재방문 주기
2. 동일 서비스 고객 재방문 주기
3. 전체 매장 재방문 주기
```

## Overdue Ratio

```text
OverdueRatio =
마지막 방문 후 경과일
÷
예상 재방문 주기
```

예:

```text
예상 재방문 = 56일
현재 경과 = 84일

OverdueRatio = 1.5
```

후보 기준 예시:

```text
1.3 이상 → 재방문 지연
2.0 이상 → 장기 미방문
```

'이탈'이라고 단정하지 않는다.

---

# 22. Detector 4 — RevenueGap

목적:

> 저수요 시간대 또는 미사용 capacity를 금액으로 환산한다.

## Benchmark Gap

capacity가 없을 때:

```text
다른 시간대 평균 예약
-
현재 예약
```

차이에 평균 객단가를 곱해
추가 매출 가능성을 추정한다.

예:

```text
평균 예약 차이 = 2.3건
평균 객단가 = 42,000원

주당 기회 = 96,600원
월 환산 ≈ 415,000원
```

표현은 다음과 같이 한다.

> 다른 시간대 수준까지 예약이 증가한다고 가정할 경우 약 42만원의 추가 매출 여지가 있습니다.

'매출 손실'이라고 단정하지 않는다.

---

# 23. Capacity Gap

실제 예약 가능 capacity가 있는 경우:

```text
Available Capacity
-
Booked Capacity
```

예:

```text
가능 시간 = 360분
예약 시간 = 120분

Unused Capacity = 240분
```

시간당 평균 매출이 45,000원이라면

```text
240분 = 4시간
기회 가치 ≈ 180,000원
```

---

# 24. Detector 5 — ServiceDemandGap

목적:

> 서비스별로 특정 요일 또는 시간대에 반복되는 수요 패턴을 탐지한다.

예:

```text
화요일 14~16시

커트    50%
염색    30%
펌      15%
클리닉   5%
```

반면 저녁 시간대:

```text
클리닉 25%
```

이런 경우:

> 클리닉 예약은 오후 18시 이후에 집중되는 경향이 있습니다.

까지는 말할 수 있다.

하지만

> 오후에 클리닉을 할인하면 매출이 증가한다.

와 같은 인과관계는 데이터 검증 없이 단정하지 않는다.

---

# 25. 결과 표현 규칙

모든 결과는 세 층으로 분리한다.

## Observation

실제 데이터로 확인된 사실.

예:

> 화요일 14~16시 예약 발생량이 다른 화요일 시간대보다 41% 낮습니다.

## Estimate

가정을 포함한 추정값.

예:

> 다른 시간대 수준까지 예약이 증가한다면 월 약 38~46만원의 추가 매출 여지가 있습니다.

## Recommendation

실행 제안.

예:

> 해당 시간대 재방문 가능 고객에게 한정 프로모션을 테스트해보세요.

Observation, Estimate, Recommendation은 UI에서도 분리한다.

---

# 26. Opportunity Score

발견된 기회가 여러 개일 때 우선순위를 정한다.

총점 100점.

```text
Impact        35점
Confidence    30점
Persistence   20점
Actionability 15점
```

## Impact

기회의 잠재 가치.

- 예상 매출
- 대상 고객 수
- 예약량 차이
- unused capacity

## Confidence

분석 신뢰도.

가점 요소:

- 분석 기간이 충분함
- 표본 수가 충분함
- 실제 결제 데이터 존재
- capacity 존재
- 고객 식별 가능

## Persistence

현상이 반복되는 정도.

예:

```text
최근 12주 중 9주에서 동일 현상 발생
```

## Actionability

사업자가 실제 행동으로 옮기기 쉬운 정도.

높음:

- 장기 미방문 고객
- 특정 저수요 시간대

낮음:

- 지역 인구 감소
- 거시적인 상권 변화

---

# 27. Confidence 표시

신뢰도는 사용자에게 반드시 노출한다.

예:

```text
신뢰도 높음
91%
```

설명:

> 최근 16주의 예약 1,284건과 실제 결제 데이터를 기준으로 계산했습니다.

또는:

```text
신뢰도 중간
63%
```

설명:

> 직원별 근무시간 정보가 없어 실제 빈 슬롯이 아닌 예약 발생량을 기준으로 분석했습니다.

---

# 28. Opportunity 표준 데이터 구조

예시:

```json
{
  "opportunity_id": "OPP_000134",
  "business_id": "BIZ_001",
  "type": "LOW_DEMAND_SLOT",

  "segment": {
    "weekday": "TUE",
    "start_hour": 14,
    "end_hour": 16
  },

  "observation": {
    "actual": 1.7,
    "benchmark": 4.0,
    "difference_pct": -57.5
  },

  "estimated_value": {
    "monthly_low": 380000,
    "monthly_high": 460000,
    "currency": "KRW"
  },

  "score": 82,
  "confidence": 0.74,

  "sample": {
    "weeks": 12,
    "appointments": 318
  },

  "limitations": [
    "직원별 근무시간 데이터 없음"
  ]
}
```

---

# 29. AI의 역할

LLM은 다음 세 역할만 담당한다.

## 1. 설명

무슨 현상이 발견됐는지
사업자가 이해하기 쉬운 언어로 설명한다.

## 2. 원인 가설

가능한 원인을 제시하되
사실과 가설을 명확하게 구분한다.

## 3. 행동 제안

실제로 테스트할 수 있는 액션을 제안한다.

예:

```text
재방문 고객 대상 프로모션
저수요 시간대 한정 혜택
취소 빈도가 높은 시간대 리마인드 강화
```

---

# 30. 사용자 화면 예시

```text
매출 기회 #1

화요일 오후 예약이 반복적으로 낮습니다.

[관측 사실]
최근 12주 동안 화요일 14~16시 예약량은
다른 화요일 시간대보다 평균 57% 낮았습니다.

[예상 기회]
현재 평균 객단가를 기준으로
월 38~46만원 수준의 추가 매출 여지가 있습니다.

[신뢰도]
74% · 중간

직원별 근무시간 정보가 없어
실제 빈 슬롯이 아닌 예약 발생량을 기준으로 계산했습니다.

[추천 실험]
재방문 가능성이 높은 고객에게
화요일 14~16시 전용 혜택을 제공하고
4주간 예약률 변화를 측정해보세요.
```

---

# 31. MVP 구현 우선순위

## Phase 1

```text
Normalization
    ↓
Metric Engine
    ↓
LowDemandSlot
    ↓
RevenueGap
```

목표:

- Excel/CSV 업로드
- 컬럼 매핑
- 예약 데이터 정규화
- 시간대별 수요 계산
- 저수요 구간 탐지
- 예상 매출 기회 계산

## Phase 2

```text
CancellationHotspot
DormantCustomer
```

## Phase 3

```text
ServiceDemandGap
Opportunity Score
AI Recommendation
```

---

# 32. 첫 MVP 성공 기준

테스트용 실제 또는 샘플 사업장 데이터를 입력했을 때:

- 예약 Excel/CSV 업로드 성공
- 주요 컬럼 자동 매핑
- 최소 8~12주 지표 생성
- 최소 1개의 Opportunity 탐지
- 발견 근거를 숫자로 설명
- 예상 매출 기회 계산
- 데이터 부족 시 한계 표시
- 동일 데이터 입력 시 동일 Detector 결과 출력
- AI 설명과 실제 계산값이 불일치하지 않음

---

# 33. 권장 백엔드 모듈 구조

향후 실제 구현 시 다음 형태를 기준으로 한다.

```text
/database
/import
/normalization
/metrics
/detectors
/scoring
/ai
```

예:

```text
/import
  csv_importer
  excel_importer
  column_mapper

/normalization
  appointment_normalizer
  status_normalizer
  customer_tokenizer

/metrics
  demand_metrics
  cancellation_metrics
  customer_metrics
  revenue_metrics

/detectors
  low_demand_slot
  revenue_gap
  cancellation_hotspot
  dormant_customer
  service_demand_gap

/scoring
  opportunity_score
  confidence_score

/ai
  opportunity_explanation
  action_recommendation
```

---

# 34. 현재 결정된 핵심 원칙

1. 소상공인에게 요구하는 데이터는 최소화한다.
2. Excel/CSV 기반 데이터 업로드부터 시작한다.
3. 다양한 외부 데이터는 LOOFIO 내부 표준 형식으로 변환한다.
4. 예약 데이터가 MVP의 핵심 데이터다.
5. 개인정보 저장은 최소화하고 고객 식별 키 중심으로 사용한다.
6. 계산과 탐지는 deterministic backend에서 수행한다.
7. AI는 숫자 계산보다 해석과 설명에 집중한다.
8. Observation / Estimate / Recommendation을 구분한다.
9. 모든 추정에는 신뢰도와 데이터 한계를 함께 표시한다.
10. 기회 발견 이후 실행 결과를 다시 분석하는 Loop를 만든다.

---

# 35. 다음 개발 단계

다음 단계에서는 실제 구현 가능한 수준으로 다음 항목을 정의한다.

1. PostgreSQL DB Schema
2. CSV / Excel Import Schema
3. Column Mapping 규칙
4. Metric Engine 상세 계산식
5. LowDemandSlotDetector 의사코드
6. RevenueGapDetector 의사코드
7. Opportunity Score 계산식
8. REST API 구조
9. 샘플 데이터셋
10. PoC 테스트 시나리오

이 단계가 완료되면 실제 백엔드 구현으로 넘어갈 수 있다.
