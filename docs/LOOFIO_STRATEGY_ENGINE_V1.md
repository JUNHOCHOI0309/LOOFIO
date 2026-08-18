---
title: "LOOFIO Strategy Engine v1"
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
  - "LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md"
  - "LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md"
---

# LOOFIO Strategy Engine v1

## 1. 문서 목적

이 문서는 Cause Analysis에서 생성한 원인 가설과 사업장의 실제 제약을 바탕으로, 가능한 개입 전략을 생성·필터링·비교하는 Strategy Engine의 구현 계약을 정의한다.

현재 LOOFIO Hospital Appointment MVP는 다음 흐름까지 구현되어 있다.

```text
Appointment CSV
→ Normalization
→ Metrics
→ Detector
→ Opportunity
→ Evidence / Estimate / Score
→ Deterministic Manual Recommendation
→ Decision
→ Manual Action
→ Result
→ Baseline Measurement
```

새 의사결정 구조는 다음과 같다.

```text
Opportunity
→ Decision Context
→ Cause Analysis
→ Strategy Comparison
→ Action Playbook
→ Economics / Feasibility
→ Experiment
→ Recommendation Package
→ Quality Gate
```

Strategy Engine은 다음 질문에 답해야 한다.

```text
현재 Cause Candidate를 해결하기 위해 어떤 종류의 개입이 가능한가
각 전략이 현재 사업장 조건에서 실제로 실행 가능한가
어떤 데이터·정책·경제성·측정 제약 때문에 제외되는가
실행 전략이 없으면 무엇을 먼저 보완해야 하는가
아무 행동도 하지 않는 것이 더 나은가
```

핵심 원칙:

> Strategy Engine은 채널이나 문구를 즉시 선택하지 않는다.
> 먼저 개입의 종류를 비교하고, 실행 가능성과 경제성·측정 가능성을 통과한 전략만 Playbook 단계로 전달한다.

---

# 2. v1 범위

## 2.1 초기 범위

```text
Domain
→ Hospital Appointment MVP

Opportunity
→ LOW_DEMAND_SLOT

Cause Input
→ Cause Analysis v1

Mode
→ Deterministic

AI
→ 사용하지 않음

Execution
→ 없음
```

## 2.2 v1 이후 확장

```text
CANCELLATION_HOTSPOT
DORMANT_CUSTOMER
SERVICE_DEMAND_GAP
Historical Strategy Outcome
External Context
AI comparison wording
Persisted Strategy Run
```

## 2.3 비범위

Strategy Engine은 다음을 수행하지 않는다.

- Opportunity 재계산
- Cause 확정
- Playbook의 세부 실행 단계 생성
- 개별 고객 대상 목록 생성
- 광고 문구·콘텐츠 생성
- 외부 채널 실행
- ROI·Incrementality 확정
- 사용자 승인 대체
- 환자 임상정보 기반 전략 선택

---

# 3. 파이프라인 위치

```text
Opportunity
+ Cause Analysis Result
+ Decision Context Snapshot
+ Business Goal
+ Economics Context
+ Policy Context
+ Measurement Capability
        ↓
Strategy Input Validation
        ↓
Strategy Candidate Seeding
        ↓
Applicability Evaluation
        ↓
Hard Gate Evaluation
        ↓
Economics / Feasibility Evaluation
        ↓
Strategy Priority Score
        ↓
Alternative Comparison
        ↓
Provisional Selection
        ↓
Playbook Resolver
```

Cause Priority Score는 Strategy Priority Score로 복사하지 않는다.

Cause는 “왜 그랬을 가능성이 있는가”를 다루고, Strategy는 “무엇을 시도할 가치가 있는가”를 다룬다.

---

# 4. Source of Truth와 입력

## 4.1 Opportunity

```text
id
type
segment
observation
estimate(optional)
score
confidence
limitations
detector/version
```

## 4.2 Cause Analysis

```text
cause_analysis_id
version
run status
candidate code/status
review priority score
evidence refs
contradiction refs
missing required/optional inputs
downstream blockers
diagnostic answers
global limitations
```

## 4.3 Decision Context

```text
GoalContext
BusinessConstraintContext
EconomicsContext
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
DataQualityContext
```

## 4.4 Playbook Registry Metadata

Strategy Engine은 Playbook의 실제 실행 단계를 생성하지 않는다.

다음 메타데이터만 읽는다.

```text
playbook_id
version
status
strategy_family
applicable cause/opportunity
required readiness
preconditions
contraindications
policy tags
economics requirement
measurement requirement
```

## 4.5 금지 입력

```text
raw CSV
환자 이름
전화번호·이메일 원문
주민등록번호
진단명
질병·증상
처방
검사 결과
의무기록
상담 원문
다른 tenant 데이터
```

---

# 5. Strategy 용어

## Strategy Family

개입의 큰 방향.

예:

```text
RETENTION_REACTIVATION
DISCOVERABILITY
CAPACITY_OPERATION
```

## Strategy Candidate

현재 Opportunity·Cause·Decision Context에서 검토 가능한 Strategy Family 인스턴스.

## Execution Strategy

직접적인 운영·마케팅 실험으로 이어질 수 있는 전략.

## Diagnostic Strategy

부족한 정보를 수집해 다음 의사결정을 가능하게 하는 전략.

## Hold Strategy

현재는 실행하지 않고 모니터링·재평가하는 전략.

## Hard Gate

점수 이전에 반드시 통과해야 하는 데이터·정책·경제성·측정 조건.

## Strategy Priority Score

통과한 실행 전략의 검토 우선순위를 나타내는 0~100 점수.

성공 확률·인과효과·매출 가치 자체가 아니다.

---

# 6. Strategy Class

```text
EXECUTION
OPERATIONAL
DIAGNOSTIC
HOLD
```

| Class | 설명 | Strategy |
|---|---|---|
| `EXECUTION` | 고객·시장·예약 경로에 개입 | RETENTION, DISCOVERABILITY, CONVERSION, OFFER_PACKAGING, PARTNERSHIP, ACQUISITION, CANCELLATION_RECOVERY |
| `OPERATIONAL` | 직원·capacity·Offering 운영을 조정 | CAPACITY_OPERATION |
| `DIAGNOSTIC` | 의사결정에 필요한 데이터를 보완 | DATA_COLLECTION |
| `HOLD` | 실행하지 않고 조건을 모니터링 | NO_ACTION |

`DIAGNOSTIC`과 `HOLD`는 실행 전략과 같은 점수로 단순 비교하지 않는다.

---

# 7. Strategy Taxonomy v1

## 7.1 `DATA_COLLECTION`

### 목적

Critical 또는 blocking 입력을 보완해 Cause·Strategy·Experiment 판단을 가능하게 한다.

### 유효 상황

- data quality conflict
- capacity unknown
- consent unknown
- tracking 없음
- result source 없음
- economics unknown
- funnel/channel evidence 없음

### 출력 예

```text
무엇을 수집할지
누가 확인할지
언제까지 확인할지
어느 DecisionField가 갱신되는지
수집 완료 후 어떤 Strategy를 다시 평가할지
```

### 금지

> 데이터를 더 모으세요.

처럼 필드·담당자·완료조건이 없는 조언.

---

## 7.2 `CAPACITY_OPERATION`

### 목적

마케팅 수요 확대보다 먼저 실제 판매 가능 시간·직원·공간·장비·Offering 가용성을 정리한다.

### 유효 상황

- capacity false/unknown
- eligible staff 부족
- Offering unavailable
- booking blackout
- same-day booking policy mismatch
- 목표 슬롯이 실제 예약 가능 상태가 아님

### 결과 방향

- 목표 슬롯 운영 확인
- staff/offering 배치 검토
- 예약 오픈 상태 수정
- Offering-slot 재배치
- 불필요한 수요 확대 중단

---

## 7.3 `RETENTION_REACTIVATION`

### 목적

기존 고객 중 재방문 가능성이 있는 비식별 cohort를 적법한 범위에서 목표 슬롯과 연결한다.

### 유효 상황

- `RETENTION_GAP` reviewable
- customer token/history/revisit interval 존재
- eligible cohort > 0
- capacity·Offering available
- consent/contact capability
- tracking/result source

### 채널은 Playbook 단계에서 선택한다.

```text
manual CRM review
approved messaging
front-desk rebooking
staff callback
```

### 금지

- 개별 환자 진단 기반 targeting
- 동의 상태 미확인 상태의 고객 연락
- 개별 customer token을 Recommendation에 노출

---

## 7.4 `DISCOVERABILITY`

### 목적

목표 Offering·시간대가 검색·지도·웹·예약 페이지·현장 안내에서 발견되는 정도를 개선한다.

### 유효 상황

- `DISCOVERABILITY_GAP` reviewable
- 목표 슬롯 실제 가용
- 발견 경로 존재 또는 설정 가능
- tracking/result source
- 정책 검토

### 예

```text
예약 페이지에서 잔여 슬롯 가시성 개선
Offering과 위치·시간 정보 정리
지도·플레이스 정보 정합성 검토
검색 의도와 예약 딥링크 연결
```

유료 광고를 자동으로 의미하지 않는다.

---

## 7.5 `CONVERSION`

### 목적

노출·문의·예약 시작은 있으나 예약 완료까지의 마찰을 줄인다.

### 유효 상황

- `CONVERSION_FRICTION` reviewable
- funnel 데이터 존재
- booking path owner 존재
- 목표 슬롯 가용
- tracking과 result source 존재

### 예

```text
예약 단계 축소
목표 Offering/슬롯 딥링크
예약 오류·가용성 표시 개선
CTA와 랜딩 경로 정리
```

---

## 7.6 `OFFER_PACKAGING`

### 목적

무작정 할인하지 않고 Offering의 구성·가치 전달·저비용 부가가치·시간대 적합성을 실험한다.

### 유효 상황

- `OFFER_SLOT_MISMATCH` 또는 `VALUE_OR_PRICE_FRICTION`
- Offering marketing eligibility
- economics 최소 partial
- policy review
- result source

### 예

```text
비가격 부가가치
시간대 전용 Offering 구성
Offering 설명 개선
관련 Offering 묶음 검토
```

### 금지

- 비용 계산 없는 할인
- 의료 결과 보장
- 정책 검토 없는 가격·혜택 표현

---

## 7.7 `PARTNERSHIP_REFERRAL`

### 목적

고객 동선이 겹치는 비경쟁 사업자·기관과 추적 가능한 추천 흐름을 만든다.

### 유효 상황

- local demand 또는 complementary audience 근거
- partner 후보/owner
- partner code·QR·source tracking
- 비용 또는 보상 정책
- result source
- policy review

### 예

```text
제휴처별 고유 QR
완료 예약 기준 보상
2~3개 제휴처 분리 실험
```

### 금지

- 추적 없는 대량 전단
- 제휴처별 결과 분리 불가
- 의료광고·개인정보 정책 미검토

---

## 7.8 `ACQUISITION`

### 목적

검증 가능한 외부 수요를 신규 고객 예약으로 전환한다.

### 유효 상황

- demand proxy 존재
- 목표 슬롯·Offering capacity 확인
- paid/organic channel capability
- budget cap
- economics D4 또는 동등 수준
- tracking/result source
- policy approved

### 제한

`DEMAND_DEFICIT`가 강한데 외부 수요 근거가 없으면 기본적으로 제외한다.

### 금지

- 경제성·tracking 없는 광고
- 클릭률만으로 성공 판단
- 실제 예약·완료 결과 미연결

---

## 7.9 `CANCELLATION_RECOVERY`

### 목적

예약은 있으나 취소·노쇼로 사라지는 capacity를 리마인드·재예약·대기 명단으로 회수한다.

### 유효 상황

- `CANCELLATION_LEAKAGE` reviewable
- cancellation/no-show evidence
- reminder/reschedule/waitlist capability
- consent/policy
- tracking/result source

### 예

```text
예약 확인 절차
취소 발생 시 waitlist 회수
재예약 흐름
취소 시간대별 운영 검토
```

---

## 7.10 `NO_ACTION`

### 목적

현재 정보·경제성·정책·capacity 조건에서 실행하지 않는 것이 더 합리적일 때, 명시적으로 보류하고 재평가 조건을 만든다.

### 필수 구성

```text
보류 이유
현재 차단 조건
모니터링 metric
재평가 날짜
재평가 trigger
현재 추정 한계
```

`NO_ACTION`은 분석 실패가 아니다.

---

# 8. Strategy Run 상태

```text
PENDING
COMPLETED
MULTIPLE_VALID_OPTIONS
NEEDS_DATA
NEEDS_POLICY_REVIEW
NO_EXECUTABLE_STRATEGY
INVALID_INPUT
FAILED
```

## `COMPLETED`

실행·운영 Strategy 하나를 잠정 선택했거나, `DATA_COLLECTION`/`NO_ACTION`을 명시적으로 선택.

## `MULTIPLE_VALID_OPTIONS`

상위 후보의 차이가 작아 하나를 자동 우선하지 않는 상태.

## `NEEDS_DATA`

실행 후보의 필수 입력이 부족하고, 구체적인 `DATA_COLLECTION` 전략을 반환.

## `NEEDS_POLICY_REVIEW`

정책 확인 전에는 전략을 실행 가능 상태로 만들 수 없음.

## `NO_EXECUTABLE_STRATEGY`

실행·운영 전략이 모두 infeasible 또는 blocked이고, 추가 데이터 수집도 현재 불가능.

## `INVALID_INPUT`

tenant/business mismatch, 지원하지 않는 version, 필수 Cause Result 없음 등.

---

# 9. Strategy Candidate 상태

```text
ELIGIBLE
ELIGIBLE_WITH_LIMITATIONS
NEEDS_DATA
NEEDS_POLICY_REVIEW
INFEASIBLE
NOT_APPLICABLE
DEPRIORITIZED
```

잠정 선택 여부는 별도 필드로 저장한다.

```text
selected = true / false
```

`selected`는 사용자 승인이나 실행을 의미하지 않는다.

---

# 10. Strategy Engine 처리 순서

```text
1. Opportunity / Cause / Decision Context validation
2. Critical Data Quality Gate
3. Cause→Strategy mapping
4. Strategy candidate seeding
5. Applicability evaluation
6. Capacity / Offering Gate
7. Policy / Consent Gate
8. Tracking / Measurement Gate
9. Economics Gate
10. Candidate status determination
11. EXECUTION / OPERATIONAL candidate scoring
12. Alternative comparison
13. Provisional selection
14. Diagnostic/Hold fallback
15. Playbook candidate handoff
```

---

# 11. Hard Gate

점수 계산 전에 적용한다.

## 11.1 Global Data Quality Gate

다음이면 실행 전략 전체를 보류한다.

```text
Cause Run = BLOCKED_BY_DATA_QUALITY
critical timezone conflict
Opportunity evidence source 재현 불가
tenant/business source conflict
required status mapping unresolved
```

결과:

```text
DATA_COLLECTION selected
또는
NO_ACTION if correction impossible
```

## 11.2 Capacity Gate

수요 확대형 전략:

```text
RETENTION_REACTIVATION
DISCOVERABILITY
CONVERSION
OFFER_PACKAGING
PARTNERSHIP_REFERRAL
ACQUISITION
```

필수:

```text
target slot capacity = known true
Offering available = known true
eligible staff/capacity not zero
blackout 없음
```

## 11.3 Policy / Consent Gate

고객 접촉:

```text
verified consent capability
allowed channel
manual approval
```

외부 마케팅:

```text
policy review approved
Offering marketing enabled
prohibited claim 없음
```

## 11.4 Measurement Gate

최종 실행 후보:

```text
result source
action-level tracking
primary metric 가능
owner
기간 설정 가능
```

없으면 `DATA_COLLECTION` 또는 `NEEDS_DATA`.

## 11.5 Economics Gate

비용이 발생하는 전략:

```text
budget cap
cost status
contribution 또는 revenue-only limitation
```

유료 Acquisition·Partner·혜택 전략:

```text
economics.status = complete
또는
정책상 허용된 partial + 명시적 limitation
```

`unknown`을 0으로 통과시키지 않는다.

---

# 12. 후보 생성 정책

## 12.1 Cause Mapping 기반

Strategy는 Cause Candidate와 mapping relation이 있을 때 seed한다.

Relation:

```text
PRIMARY
SECONDARY
CONDITIONAL
INHIBITORY
```

- `PRIMARY`: 해당 Cause의 기본 개입 방향
- `SECONDARY`: 다른 조건과 함께 검토
- `CONDITIONAL`: 명시적 데이터·정책 조건 충족 시 생성
- `INHIBITORY`: 해당 Cause가 강할수록 전략을 억제

상세는 `LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md`.

## 12.2 `DATA_COLLECTION`

다음이면 seed한다.

```text
Cause Candidate NEEDS_DATA
Critical blocker 존재
Strategy candidate blocking input 존재
Decision Readiness < required level
```

## 12.3 `NO_ACTION`

모든 Strategy Run에 comparator로 seed한다.

선택 가능 조건:

- 실행 후보가 모두 infeasible/blocked
- opportunity value 대비 실행 비용 과도
- evidence가 약하고 학습 비용도 큼
- policy상 실행 불가
- monitoring으로 충분

---

# 13. 실행 전략과 Diagnostic/Hold 비교 방식

`DATA_COLLECTION`과 `NO_ACTION`을 실행 Strategy와 같은 100점 점수로 비교하지 않는다.

## 13.1 우선 순서

```text
A. Critical data quality/blocking input 존재
→ DATA_COLLECTION

B. 실행/운영 Candidate 중 ELIGIBLE 존재
→ Strategy Score 비교

C. 실행 Candidate 없음 + 해결 가능한 missing data 존재
→ DATA_COLLECTION

D. 실행 Candidate 없음 + 추가 데이터 수집 가치 낮음
→ NO_ACTION
```

## 13.2 이유

경제적 개입과 데이터 수집은 목적이 다르다.

하나의 점수로 섞으면 저비용 데이터 수집이 항상 높아지거나, 반대로 매출 Estimate가 큰 실행 전략이 필수 데이터 부족을 무시할 수 있다.

---

# 14. Strategy Priority Score v1

## 14.1 적용 대상

```text
EXECUTION
OPERATIONAL
```

상태가 다음일 때만 계산한다.

```text
ELIGIBLE
ELIGIBLE_WITH_LIMITATIONS
```

`NEEDS_DATA`, `INFEASIBLE`, `NEEDS_POLICY_REVIEW`는 score를 `null`로 둔다.

## 14.2 구성

```text
Expected Net Value       25
Evidence Fit             20
Operational Feasibility  15
Measurement Feasibility  15
Policy / Brand Safety    10
Time to Learning         10
Learning Value            5
Total                   100
```

## 14.3 의미

> 현재 조건에서 먼저 검토할 가치가 있는 실행 전략의 순위.

다음 의미가 아니다.

```text
성공 확률
ROI
인과효과
예약 증가율
매출 보장
```

---

# 15. Score Factor 규칙

## 15.1 Expected Net Value — 25

### factor `1.0`

- 하한 기준 Net Contribution > 0
- 최소 기여목표 충족
- break-even이 현실적 target 이내

### factor `0.75`

- 기여금액은 양수
- 하한이 없거나 일부 비용만 추정
- 실행비 회수 가능성이 명시적 가정 안에서 존재

### factor `0.50`

- Revenue-only 또는 partial economics
- 비유료·수동 전략
- 순기여가치로 표시하지 않음

### factor `0.25`

- 경제성 정보가 매우 제한적이나 고정비가 사실상 없는 운영 진단

### `null`

- 비용-bearing 전략에서 경제성 unknown
- paid budget cap 없음
- 기여금액 계산 불가

### factor `0`

- contribution <= 0
- 실행 비용이 opportunity estimate 상한보다 큼
- 현재 조건 `infeasible`

`null`이면 score를 계산하지 않는다.

---

## 15.2 Evidence Fit — 20

Cause relation weight:

```text
PRIMARY     1.00
SECONDARY   0.70
CONDITIONAL 0.50
INHIBITORY -1.00
```

기본 factor:

```text
max(
  normalized cause review priority
  × relation weight
)
```

보조:

```text
추가 REVIEWABLE supporting cause 1개당 +0.05
최대 +0.10
```

0~1 clamp.

Cause Score는 확률이 아니라 review priority임을 유지한다.

---

## 15.3 Operational Feasibility — 15

```text
1.00
→ capacity/offering/owner 모두 known true

0.75
→ minor optional gaps, manual execution 가능

0.50
→ scale 제한 또는 운영 부담 높음

0.25
→ 실행은 가능하나 주요 assumption이 user-confirmed 수준

0
→ capacity/Offering/owner 불가
```

---

## 15.4 Measurement Feasibility — 15

```text
1.00
→ action-level tracking + result source + Grade A/B 설계 가능

0.75
→ tracking + result source + Grade C

0.50
→ baseline + manual attribution, Grade D

0.25
→ result source는 있으나 action linkage 약함

null
→ result source 없음
```

`null`은 final execution Strategy를 `NEEDS_DATA`로 전환한다.

---

## 15.5 Policy / Brand Safety — 10

```text
1.00
→ approved

0.80
→ manual-only + approved

0.50
→ 제한적 표현·채널로만 가능

null
→ needs review

0
→ blocked
```

`null`이면 `NEEDS_POLICY_REVIEW`.

---

## 15.6 Time to Learning — 10

첫 신뢰 가능한 결과까지의 예상 기간.

```text
<= 14 days → 1.00
<= 30 days → 0.75
<= 60 days → 0.50
> 60 days  → 0.25
unknown    → 0.25 with limitation
```

## 15.7 Learning Value — 5

```text
1.00
→ 여러 Strategy 판단을 동시에 개선하는 핵심 불확실성 해소

0.75
→ 동일 Playbook/채널에 재사용 가능

0.50
→ 현재 Opportunity에만 유용

0.25
→ 정보 증가가 작음
```

---

# 16. 선택 규칙

## 16.1 최소 기준

```text
minimum_score_for_selection = 65
```

## 16.2 단일 잠정 선택

```text
top score >= 65
AND
top - second >= 5
```

결과:

```text
run.status = COMPLETED
selected_strategy = top
```

## 16.3 복수 유효 옵션

```text
top score >= 65
AND
top - second < 5
```

결과:

```text
run.status = MULTIPLE_VALID_OPTIONS
selected_strategy = null
top alternatives = 2
```

Recommendation Package에서 사용자에게 차이를 보여준다.

## 16.4 기준 미달

```text
모든 eligible score < 65
```

다음 순서:

1. 해결 가능한 blocking input이 있으면 `DATA_COLLECTION`
2. 운영 제약 정리가 필요하면 `CAPACITY_OPERATION`
3. 둘 다 아니면 `NO_ACTION`

## 16.5 Tie-break

점수가 같으면:

```text
1. Policy Safety
2. Measurement Feasibility
3. 낮은 고정 실행비
4. 빠른 Time to Learning
5. 높은 Learning Value
6. stable taxonomy order
```

---

# 17. Strategy Run Output Contract

```json
{
  "id": "STRATEGY_RUN_xxx",
  "version": "strategy-engine-v1",
  "status": "COMPLETED",
  "tenant_id": "TENANT_01",
  "business_id": "BIZ_01",
  "opportunity_id": "OPP_01",
  "cause_analysis_id": "CAUSE_RUN_01",
  "decision_context_snapshot_id": "DCTX_01",
  "generated_at": "2026-08-17T15:00:00+09:00",
  "candidates": [
    {
      "strategy_family": "RETENTION_REACTIVATION",
      "strategy_class": "EXECUTION",
      "status": "ELIGIBLE",
      "selected": true,
      "supporting_cause_refs": [
        "CAUSE_RUN_01:RETENTION_GAP"
      ],
      "inhibitory_cause_refs": [],
      "required_inputs": [],
      "missing_inputs": [],
      "blockers": [],
      "economics_status": "partial",
      "measurement_status": "grade_b_possible",
      "policy_status": "approved_manual_only",
      "score": 74.25,
      "score_version": "strategy-priority-v1",
      "score_breakdown": {
        "expected_net_value": 12.5,
        "evidence_fit": 16.0,
        "operational_feasibility": 15.0,
        "measurement_feasibility": 11.25,
        "policy_safety": 8.0,
        "time_to_learning": 7.5,
        "learning_value": 4.0,
        "total": 74.25
      },
      "selection_reason": "기존 고객 cohort와 목표 슬롯 capacity가 확인되고, 수동 비교 실험이 가능합니다.",
      "exclusion_reasons": [],
      "playbook_candidates": [
        "PB_LOW_DEMAND_REVISIT_COHORT_V1"
      ],
      "limitations": [
        "변동원가가 없어 순기여이익은 계산하지 않습니다."
      ]
    }
  ],
  "selected_strategy": "RETENTION_REACTIVATION",
  "alternative_comparison": [],
  "next_stage": {
    "playbook_resolution_ready": true,
    "blocked_reasons": []
  },
  "global_limitations": []
}
```

---

# 18. Alternative Comparison Contract

모든 Run은 최소 2개 실행·운영 후보를 비교하거나 단일 후보 이유를 남긴다.

```json
{
  "strategy_a": "RETENTION_REACTIVATION",
  "strategy_b": "DISCOVERABILITY",
  "differences": [
    {
      "dimension": "economics",
      "preferred": "RETENTION_REACTIVATION",
      "reason": "유료 매체비 없이 수동 cohort 실험이 가능합니다."
    },
    {
      "dimension": "measurement",
      "preferred": "RETENTION_REACTIVATION",
      "reason": "대상 cohort와 완료 예약을 비교할 수 있습니다."
    },
    {
      "dimension": "reach",
      "preferred": "DISCOVERABILITY",
      "reason": "신규 수요까지 포괄할 수 있으나 현재 검색 노출 데이터가 부족합니다."
    }
  ]
}
```

일반적인 장점·단점이 아니라 현재 Decision Context에 연결한다.

---

# 19. LOW_DEMAND_SLOT 기본 후보

## Core

```text
CAPACITY_OPERATION
RETENTION_REACTIVATION
DISCOVERABILITY
DATA_COLLECTION
NO_ACTION
```

## Conditional

```text
CONVERSION
OFFER_PACKAGING
PARTNERSHIP_REFERRAL
ACQUISITION
CANCELLATION_RECOVERY
```

조건은 `LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md`를 따른다.

---

# 20. Strategy별 Downstream Readiness

| Strategy | 최소 Readiness | Final Package 권장 |
|---|---:|---:|
| DATA_COLLECTION | D0 | D0 |
| CAPACITY_OPERATION | D1 | D1~D2 |
| RETENTION_REACTIVATION | D2 평가 | D3 실행 |
| DISCOVERABILITY | D2 평가 | D3 실행 |
| CONVERSION | D2 평가 | D3 실행 |
| OFFER_PACKAGING | D2 평가 | D3~D4 실행 |
| PARTNERSHIP_REFERRAL | D2 평가 | D3~D4 실행 |
| ACQUISITION | D3 평가 | D4 실행 |
| CANCELLATION_RECOVERY | D2 평가 | D3 실행 |
| NO_ACTION | D0 | D0 |

---

# 21. `DATA_COLLECTION` 상세 계약

`DATA_COLLECTION`은 다음 필수 항목을 갖는다.

```text
missing_field_paths
why_needed
owner
collection_method
deadline
verification_rule
updated_readiness_target
strategies_to_rerun
```

예:

```json
{
  "strategy_family": "DATA_COLLECTION",
  "collection_plan": [
    {
      "field_path": "operation.slot_capacity_confirmed",
      "why_needed": "판매 불가 슬롯과 수요 부족을 구분합니다.",
      "owner": "business_owner",
      "collection_method": "manual_confirmation",
      "deadline": "2026-08-19",
      "verification_rule": "known boolean with source",
      "unblocks": ["CAPACITY_OPERATION", "RETENTION_REACTIVATION"]
    }
  ]
}
```

---

# 22. `NO_ACTION` 상세 계약

```text
reason_codes
monitoring_metric
monitoring_segment
review_at
reopen_triggers
current_limitations
```

Reason Code:

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

Reopen Trigger 예:

```text
Demand Index가 연속 4주 기준 이하
capacity가 다시 확보됨
변동원가 입력 완료
추적 수단 설정 완료
정책 검토 완료
```

---

# 23. Playbook Handoff

Strategy Engine은 다음을 Playbook Resolver에 전달한다.

```text
strategy_run_id
selected strategy 또는 top alternatives
supporting causes
blockers
decision readiness
economics status
measurement status
policy status
target segment
offering scope
slot scope
preferred execution mode
candidate playbook IDs
```

Playbook Resolver가 다음을 결정한다.

- 구체적 online/offline steps
- experiment template
- success/stop default
- policy tag
- asset requirement

---

# 24. API 후보

## 24.1 Preview

```text
POST /api/v1/opportunities/{opportunityId}/strategy-runs/preview
```

Request:

```json
{
  "cause_analysis": {},
  "decision_context": {},
  "as_of": "2026-08-17T15:00:00+09:00"
}
```

특성:

- persistence 없음
- 외부 실행 없음
- 동일 입력 → 동일 결과
- owner/admin/marketer
- tenant/business mismatch 404
- PII field 422
- 기존 `/recommendations/draft` 유지

## 24.2 Persistence 이후

```text
POST /api/v1/opportunities/{opportunityId}/strategy-runs
GET  /api/v1/opportunities/{opportunityId}/strategy-runs
GET  /api/v1/strategy-runs/{strategyRunId}
```

---

# 25. DB 후보

Preview 단계에서는 불필요하다.

Persistence 시:

```text
strategy_runs
strategy_candidates
strategy_cause_links
strategy_score_breakdowns
strategy_comparisons
```

공통:

```text
tenant_id
business_id
opportunity_id
cause_analysis_id
decision_context_snapshot_id
version
status
input_hash
generated_at
limitations
```

과거 Run을 현재 규칙으로 덮어쓰지 않는다.

---

# 26. Determinism

동일 입력:

```text
Opportunity
Cause Analysis
Decision Context
Playbook Registry metadata
Strategy rules version
Strategy score version
as_of
```

동일 결과:

- Candidate set
- status
- blockers
- score
- order
- comparison
- selection

Deterministic ID는 input hash 기반으로 생성할 수 있다.

---

# 27. 오류 계약

```text
OPPORTUNITY_NOT_FOUND
CAUSE_ANALYSIS_NOT_READY
DECISION_CONTEXT_INVALID
STRATEGY_INPUT_INSUFFICIENT
POLICY_REVIEW_REQUIRED
ECONOMICS_INPUT_REQUIRED
MEASUREMENT_SETUP_REQUIRED
NO_APPLICABLE_PLAYBOOK
TENANT_SCOPE_MISMATCH
PII_FIELD_REJECTED
UNSUPPORTED_STRATEGY_VERSION
STRATEGY_ENGINE_INTERNAL_ERROR
```

기존 API Error Envelope를 따른다.

---

# 28. 테스트 전략

## 28.1 Taxonomy

- code unique
- class 고정
- stable order
- description과 readiness 존재

## 28.2 Mapping

- Cause relation 존재
- PRIMARY/SECONDARY/CONDITIONAL/INHIBITORY
- 조건부 activation
- duplicate mapping 없음

## 28.3 Gate

- data quality block
- capacity false/unknown
- consent unknown
- tracking 없음
- policy unknown
- economics unknown
- result source 없음

## 28.4 Score

- factor clamp
- null propagation
- fixed weight
- deterministic tie-break
- probability 표현 없음

## 28.5 Selection

- top >=65 and gap >=5
- multiple valid options
- score below threshold
- DATA_COLLECTION fallback
- NO_ACTION fallback
- economics infeasible

## 28.6 Privacy / Tenant

- cross tenant 404
- patient PII 422
- customer token 출력 없음
- clinical data 사용 없음

## 28.7 Regression

- Opportunity 불변
- Cause Result 불변
- 기존 Recommendation/Action/Result/Measurement 불변

---

# 29. 주요 Fixture

## Case A — Critical Data Quality

결과:

```text
DATA_COLLECTION selected
execution strategies blocked
```

## Case B — Capacity False

결과:

```text
CAPACITY_OPERATION selected
마케팅 확대 전략 infeasible/not applicable
```

## Case C — Retention Ready

조건:

```text
eligible cohort
consent
manual channel
tracking
capacity
```

결과:

```text
RETENTION_REACTIVATION top candidate
PB-01 candidate
```

## Case D — Discoverability Ready

조건:

```text
slot available
visibility gap
booking source tracking
```

결과:

```text
DISCOVERABILITY candidate
```

## Case E — Two Close Alternatives

결과:

```text
MULTIPLE_VALID_OPTIONS
top 2 alternatives
```

## Case F — Paid Acquisition Economics Unknown

결과:

```text
ACQUISITION NEEDS_DATA
score null
```

## Case G — Economics Infeasible

결과:

```text
NO_ACTION 또는 저비용 OPERATIONAL 전략
```

## Case H — No Tracking

결과:

```text
DATA_COLLECTION
tracking setup
```

---

# 30. 로컬 구현 Backlog

## ST-001 — Strategy Taxonomy

- StrategyFamily
- StrategyClass
- stable registry
- readiness metadata

## ST-002 — Cause Mapping

- relation enum
- mapping table
- condition evaluator
- inhibitory mapping

## ST-003 — Candidate Seeder

- core/conditional candidate
- DATA_COLLECTION
- NO_ACTION comparator

## ST-004 — Hard Gate

- data quality
- capacity
- policy/consent
- measurement
- economics

## ST-005 — Economics Adapter

- status
- break-even
- net value factor
- unknown propagation

## ST-006 — Score v1

- factors
- weights
- null behavior
- tie-break

## ST-007 — Alternative Comparison

- dimension differences
- selected/excluded reason
- multiple valid options

## ST-008 — Fallback

- DATA_COLLECTION plan
- NO_ACTION monitoring plan

## ST-009 — Handoff

- Playbook candidate IDs
- readiness/blockers
- selected/top alternatives

## ST-010 — Preview API

- auth
- tenant
- deterministic hash
- no persistence

## ST-011 — Regression

- fixtures
- existing Recommendation compatibility
- sample pack

## ST-012 — Documentation

- API contract
- ADR candidate
- status update after code

---

# 31. 완료조건

Strategy Engine v1 완료조건:

1. Strategy Family 10개 정의
2. Class 4개 정의
3. Cause→Strategy relation 정의
4. Hard Gate가 Score보다 먼저 적용
5. DATA_COLLECTION/NO_ACTION 별도 fallback
6. EXECUTION/OPERATIONAL에만 Score 적용
7. Score v1과 factor 규칙 고정
8. 최소 선택 점수와 복수 옵션 규칙
9. 선택·제외 이유 구조화
10. Playbook candidate handoff
11. tenant/business 격리
12. Hospital PII 미사용
13. 동일 입력 동일 결과
14. 기존 Recommendation API 유지
15. 코드 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 32. 구현 연결

Action Playbook·Experiment·Recommendation Package·Quality 설계는 완료됐다.

로컬 구현은 다음 순서로 진행한다.

```text
LOOFIO_IMPLEMENTATION_BACKLOG_V1.md
→ ST-001~ST-012
→ PB-001~PB-010
→ PBC-001~PBC-009
```

Strategy Preview가 안정되기 전에는 Playbook Persistence나 AI 연결로 건너뛰지 않는다.
