---
title: "LOOFIO Recommendation Quality Bar v1"
version: "1.0"
date: "2026-08-17"
status: "결정론적 Recommendation 품질 Gate"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
depends_on:
  - "LOOFIO_RECOMMENDATION_PACKAGE_V2.md"
  - "LOOFIO_EXPERIMENT_DESIGN_V1.md"
  - "LOOFIO_ACTION_PLAYBOOK_V1.md"
  - "LOOFIO_STRATEGY_ENGINE_V1.md"
  - "LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md"
---

# LOOFIO Recommendation Quality Bar v1

## 1. 문서 목적

이 문서는 Recommendation Package가 고객에게 돈을 받고 제공할 수준의 **구체성·근거·경제성·실행 가능성·측정 가능성**을 갖췄는지 deterministic하게 평가하는 기준을 정의한다.

Quality Score는 다음을 측정한다.

> 이 Package가 근거를 왜곡하지 않고, 현재 사업장 조건에 맞는 실행 계획과 검증 방법을 충분히 포함하는가.

다음은 측정하지 않는다.

```text
전략 성공 확률
매출 증가 확률
ROI
원인 발생 확률
모델 지능
문장 아름다움
```

핵심 통과 기준:

```text
Total Score >= 75
AND
Hard Fail = 0
AND
모든 Section Floor 충족
```

---

# 2. Quality 평가 대상

```text
RecommendationPackageDraft
+ Source References
+ Policy Validation Result
+ Upstream Status
```

Quality Validator는 다음을 재계산하지 않는다.

- Opportunity Metric
- Cause Priority Score
- Strategy Priority Score
- Playbook Fit Score
- Experiment Result
- Economics source value

Validator는 값의 존재·출처·의미·상호 일관성을 평가한다.

---

# 3. Quality Result 상태

```text
NOT_EVALUATED
INVALID_INPUT
HARD_FAILED
SCORE_FAILED
PASSED
```

## `INVALID_INPUT`

Package schema 또는 source reference가 유효하지 않음.

## `HARD_FAILED`

Hard Fail 1개 이상.

Score는 참고용으로 계산할 수 있지만 통과할 수 없다.

## `SCORE_FAILED`

Hard Fail은 없지만:

```text
Total < 75
또는
Section Floor 미달
```

## `PASSED`

모든 통과 조건 충족.

Package는 다른 upstream blocker가 없다면 `READY_FOR_REVIEW`가 될 수 있다.

---

# 4. Quality Output Contract

```json
{
  "quality_result_id": "RQ_xxx",
  "validator_version": "recommendation-quality-v1",
  "package_id": "RPKG_01",
  "package_revision": 1,
  "status": "PASSED",
  "total_score": 82,
  "threshold": 75,
  "section_scores": {
    "evidence_linkage": 18,
    "specificity": 17,
    "economics_integrity": 14,
    "feasibility": 13,
    "measurement_design": 12,
    "alternative_comparison": 8
  },
  "section_floors": {
    "evidence_linkage": 14,
    "specificity": 14,
    "economics_integrity": 10,
    "feasibility": 10,
    "measurement_design": 10,
    "alternative_comparison": 6
  },
  "hard_failures": [],
  "warnings": [
    {
      "code": "QW_ECONOMICS_PARTIAL",
      "statement": "변동원가가 없어 순기여이익은 계산하지 않습니다."
    }
  ],
  "evaluated_at": "2026-08-17T17:10:00+09:00"
}
```

---

# 5. 평가 순서

```text
1. Schema Validation
2. Tenant / Source Integrity
3. Evidence Fidelity
4. Package Type Contract
5. Strategy / Playbook Eligibility
6. Policy / Privacy / Consent
7. Execution Completeness
8. Economics Integrity
9. Experiment / Measurement Integrity
10. Alternative Comparison
11. Hard Fail Aggregation
12. Section Score
13. Threshold / Floor
14. Final Status
```

Hard Gate를 Score보다 먼저 적용한다.

---

# 6. Score 구조

```text
Evidence Linkage        20
Specificity             20
Economics Integrity     20
Feasibility             15
Measurement Design      15
Alternative Comparison  10
Total                  100
```

## Section Floor

| Section | Max | Floor |
|---|---:|---:|
| Evidence Linkage | 20 | 14 |
| Specificity | 20 | 14 |
| Economics Integrity | 20 | 10 |
| Feasibility | 15 | 10 |
| Measurement Design | 15 | 10 |
| Alternative Comparison | 10 | 6 |

Section Floor는 한 영역의 부실을 다른 점수로 감추지 못하게 한다.

---

# 7. Evidence Linkage — 20

## 7.1 Opportunity Observation / Estimate — 6

```text
6
→ 모든 핵심 수치가 source ref와 일치
→ Observation/Estimate 라벨 분리

4
→ 핵심 source는 있으나 일부 서술 reference 부족

2
→ source는 있으나 의미가 모호

0
→ 수치 출처 없음 또는 변경
```

## 7.2 Cause Evidence / Contradiction — 4

```text
4
→ Cause hypothesis, supporting, contradiction, missing data 포함

2
→ supporting은 있으나 contradiction/missing data 일부 누락

0
→ Cause를 사실로 단정
```

## 7.3 Limitation Propagation — 4

```text
4
→ upstream material limitation 모두 전파

2
→ 일부 경미한 limitation 누락

0
→ 결과를 유리하게 만들기 위해 material limitation 은폐
```

## 7.4 Numeric / Source Integrity — 6

```text
6
→ 새 숫자 없음, source/version/hash 일치

3
→ 계산 출처는 있으나 설명 미흡

0
→ AI/사용자 자유 입력으로 근거 없는 수치 생성
```

---

# 8. Specificity — 20

## 8.1 Target / Scope — 5

```text
5
→ inclusion/exclusion/size/privacy/source 명확

3
→ 대상은 있으나 제외·규모 일부 부족

0
→ "고객", "지역 사람" 수준의 일반 대상
```

Diagnostic/Hold Package:

```text
Target 대신 missing field / monitoring segment의 구체성을 평가
```

## 8.2 Offering / Slot / Channel Role — 4

```text
4
→ Offering·시간대·채널 역할 명확

2
→ 일부 scope 부족

0
→ "SNS/전단/홍보"만 나열
```

## 8.3 Steps / Owner / Schedule — 7

```text
7
→ completion rule이 있는 Step 3개 이상
→ owner
→ start/end 또는 deadline
→ 실행·검증·결과 수집 포함

4
→ 실행 단계는 있으나 담당·기한 일부 부족

0
→ 완료 여부를 판정할 수 없는 한 줄 조언
```

## 8.4 Tracking / Artifact — 4

```text
4
→ tracking과 blocking artifact 정의

2
→ tracking은 있으나 검증/산출물 부족

0
→ 결과 연결 경로 없음
```

---

# 9. Economics Integrity — 20

이 Section은 “수익성이 높다”를 평가하지 않는다.

> 비용·가치의 알려진 범위와 모르는 범위를 정직하고 일관되게 처리했는가.

## 9.1 Status / Provenance — 5

```text
5
→ complete/partial/unknown/N/A/infeasible와 source 명확

3
→ 상태는 있으나 source 일부 부족

0
→ 비용 상태를 숨김
```

## 9.2 Budget / Cost Components — 4

```text
4
→ 비용-bearing 전략에 budget cap과 주요 cost component 존재

2
→ 일부 비용 미상이며 명시됨

0
→ 유료 실행인데 budget cap 없음
```

Diagnostic/Hold:

```text
수집·운영 비용 또는 N/A 사유가 명확하면 만점 가능
```

## 9.3 Contribution / Unknown Integrity — 5

```text
5
→ complete cost에서만 contribution 계산
→ unknown은 0이 아님

3
→ revenue-only와 limitation 명확

0
→ 불완전 비용으로 순기여이익 계산
```

## 9.4 Break-even / Decision Relevance — 3

```text
3
→ 가능한 경우 break-even 또는 비용 판단 기준 존재
→ N/A면 합리적 사유 존재

1
→ 경제성 판단과 Strategy 선택 연결이 약함

0
→ 경제성 정보를 선택에 사용하지 않음
```

## 9.5 Actual / Estimate Separation — 3

```text
3
→ Actual, Opportunity Estimate, Observed Delta, Incremental을 분리

0
→ Estimate를 실제 매출·결과처럼 표시
```

---

# 10. Feasibility — 15

## 10.1 Capacity / Offering — 5

```text
5
→ capacity와 Offering availability 확인

3
→ 일부 user-confirmed assumption

0
→ 판매 불가 상태 또는 확인 없음
```

## 10.2 Policy / Consent — 4

```text
4
→ policy/consent 상태 적합

2
→ manual-only 제한으로 실행 가능

0
→ 검토 필요·금지 상태
```

## 10.3 Channel / Owner — 3

```text
3
→ 실제 가능한 channel/execution mode/owner

1
→ owner 또는 channel 세부 부족

0
→ 구현되지 않은 connector를 실행 가능처럼 표시
```

## 10.4 Playbook Eligibility — 3

```text
3
→ lifecycle/applicability/precondition 통과, contraindication 없음

1
→ limitation이 있으나 허용 상태

0
→ contraindication 또는 blocked/deprecated Playbook
```

---

# 11. Measurement Design — 15

## 11.1 Primary Metric / Result Source — 4

```text
4
→ Primary 하나, 정의·source 명확

2
→ Metric은 있으나 source/분모 일부 부족

0
→ 클릭·조회만으로 예약 성공을 판단하거나 Primary 없음
```

## 11.2 Comparison / Evidence Grade — 4

```text
4
→ method/comparison/grade ceiling/precision 명확

2
→ historical comparison만 있고 limitation 명확

0
→ 비교 기준 없음 또는 Grade 과장
```

## 11.3 Success / Stop / Guardrail — 4

```text
4
→ 사전 고정 success, hard stop, guardrail

2
→ 일부 조건 부족

0
→ 결과를 본 뒤 판단하거나 stop 없음
```

## 11.4 Attribution / Tracking / Period — 3

```text
3
→ period, attribution, tracking, result linkage

1
→ 기간은 있으나 linkage 약함

0
→ 언제·어디까지 결과를 볼지 없음
```

---

# 12. Alternative Comparison — 10

## 12.1 Candidate Breadth — 4

```text
4
→ 최소 2개 대안 또는 단일 후보의 구조화된 사유

2
→ 후보는 있으나 제외 논리 부족

0
→ 한 가지 아이디어만 바로 추천
```

## 12.2 Context-specific Comparison — 3

```text
3
→ 비용·capacity·policy·measurement 차이를 현재 사업장 값으로 비교

1
→ 일반적 장단점

0
→ 비교 없음
```

## 12.3 NO_ACTION / Lower-cost Comparator — 3

```text
3
→ 선택 전략과 NO_ACTION 또는 저비용 대안 비교

1
→ 존재만 표시

0
→ 실행하지 않을 선택지를 배제
```

---

# 13. Package Type별 점수 해석

## 13.1 EXECUTION

전체 Section을 일반 규칙대로 평가.

## 13.2 OPERATIONAL

Economics는 운영비·직원 시간·비용 N/A의 정직성을 평가.
고객 Target 대신 operation scope를 평가.

## 13.3 DIAGNOSTIC

Economics는 수집 비용과 학습 가치의 정직성을 평가.
Measurement는 field verification과 readiness 변화로 평가.
Target 대신 missing field plan을 평가.

## 13.4 HOLD

Economics는 실행하지 않는 비용 판단과 N/A 처리.
Measurement는 monitoring metric·review date·reopen trigger.
Target/channel은 N/A지만 보류 범위가 구체적이어야 한다.

Package Type을 이유로 빈 Section을 허용하지 않는다.
각 Type에 맞는 대체 계약이 있어야 한다.

---

# 14. Hard Fail Registry

Hard Fail이 하나라도 있으면 `PASSED` 불가.

## 14.1 Source / Evidence

| Code | 조건 |
|---|---|
| `QH_E01_SOURCE_REFERENCE_MISSING` | 핵심 Observation·Estimate·Cause source ref 없음 |
| `QH_E02_OBSERVATION_MUTATED` | upstream Observation 값 변경 |
| `QH_E03_INVENTED_NUMERIC_VALUE` | deterministic source 없는 수치 생성 |
| `QH_E04_CAUSE_PRESENTED_AS_FACT` | Cause hypothesis를 확정 원인으로 표현 |
| `QH_E05_MATERIAL_LIMITATION_DROPPED` | material limitation 누락 |

## 14.2 Strategy / Playbook

| Code | 조건 |
|---|---|
| `QH_S01_ALTERNATIVE_COMPARISON_MISSING` | 대안 비교 또는 단일 후보 사유 없음 |
| `QH_S02_SELECTED_STRATEGY_NOT_ELIGIBLE` | selected Strategy가 blocked/infeasible |
| `QH_S03_PLAYBOOK_NOT_ELIGIBLE` | Playbook이 eligible 상태 아님 |
| `QH_S04_CONTRAINDICATION_HIT` | 명시적 적용 금지 조건 발생 |
| `QH_S05_NO_ACTION_REVIEW_TRIGGER_MISSING` | HOLD에 재평가 기준 없음 |
| `QH_S06_DATA_COLLECTION_PLAN_INCOMPLETE` | Diagnostic에 field/owner/method/rule 없음 |

## 14.3 Execution Completeness

| Code | 조건 |
|---|---|
| `QH_X01_GENERIC_ADVICE_ONLY` | 구조화 실행 없이 일반 조언만 존재 |
| `QH_X02_TARGET_OR_SCOPE_UNDEFINED` | Type별 대상/운영/결측 범위 없음 |
| `QH_X03_OFFERING_OR_SLOT_UNDEFINED` | 필요한 Offering·시간대 범위 없음 |
| `QH_X04_OWNER_MISSING` | 실행·수집·모니터링 담당자 없음 |
| `QH_X05_SCHEDULE_OR_DEADLINE_MISSING` | 기간·기한·재검토일 없음 |
| `QH_X06_EXECUTION_STEPS_INCOMPLETE` | Type별 최소 실행 Step 미충족 |
| `QH_X07_TRACKING_MISSING` | 실행형 Package Tracking 없음 |
| `QH_X08_RESULT_SOURCE_MISSING` | 결과 데이터 source 없음 |

## 14.4 Economics

| Code | 조건 |
|---|---|
| `QH_C01_UNKNOWN_TREATED_AS_ZERO` | unknown 비용을 0으로 계산 |
| `QH_C02_BUDGET_CAP_MISSING` | 비용-bearing 실행에 budget cap 없음 |
| `QH_C03_COST_STATUS_MISSING` | 비용 상태 없음 |
| `QH_C04_NET_CONTRIBUTION_WITH_INCOMPLETE_COSTS` | incomplete cost로 net contribution 계산 |
| `QH_C05_ACTUAL_ESTIMATE_MIXED` | Actual과 Estimate 의미 혼합 |

## 14.5 Experiment / Measurement

| Code | 조건 |
|---|---|
| `QH_M01_PRIMARY_METRIC_MISSING` | Primary Metric 없음 |
| `QH_M02_COMPARISON_MISSING` | 실행형 실험에 비교 방법·fallback 없음 |
| `QH_M03_SUCCESS_THRESHOLD_MISSING` | 성공조건 없음 |
| `QH_M04_STOP_CONDITION_MISSING` | 중단조건 없음 |
| `QH_M05_PERIOD_OR_ATTRIBUTION_MISSING` | 기간·attribution 없음 |
| `QH_M06_EVIDENCE_GRADE_OVERSTATED` | Method보다 높은 Grade |
| `QH_M07_EXPERIMENT_CONTRACT_MUTATED` | RUNNING 이후 핵심 계약 변경 |

## 14.6 Policy / Security

| Code | 조건 |
|---|---|
| `QH_P01_POLICY_REVIEW_REQUIRED` | 정책 검토가 미완료인데 실행 가능 표시 |
| `QH_P02_CONSENT_REQUIRED` | 고객 접촉에 동의 상태 미확인 |
| `QH_P03_PATIENT_PII_PRESENT` | Package에 환자 PII 포함 |
| `QH_P04_CLINICAL_TARGETING_PRESENT` | 진단·질병·임상정보 기반 Targeting |
| `QH_P05_PROHIBITED_CLAIM_PRESENT` | 의료 결과 보장·검증되지 않은 주장 |
| `QH_P06_AUTOMATIC_EXECUTION_UNAPPROVED` | 미구현·미승인 자동 실행 |
| `QH_P07_TENANT_SCOPE_MISMATCH` | 다른 tenant/business source 혼합 |

---

# 15. Generic Advice 판정

키워드만으로 판정하지 않고 구조를 평가한다.

다음 중 하나면 `QH_X01_GENERIC_ADVICE_ONLY` 후보:

```text
실행 Step < Package Type 최소 기준
owner 없음
기간/기한 없음
target/scope 없음
tracking/result source 없음
success/stop 없음
```

예:

```text
SNS를 강화하세요.
→ Hard Fail

화요일 오후를 홍보하세요.
→ Hard Fail

제휴 마케팅을 해보세요.
→ Hard Fail
```

문장이 길어도 구조가 없으면 통과하지 못한다.

---

# 16. Package Type 최소 Step 기준

## EXECUTION

최소 5개:

```text
validate
prepare
measurement setup
manual execution
result collection / stop handling
```

## OPERATIONAL

최소 4개:

```text
current state verify
change/configure
reverify
result/guardrail review
```

## DIAGNOSTIC

최소 4개:

```text
missing field identify
collect/fix
verify
rerun downstream stage
```

## HOLD

최소 3개:

```text
monitor metric
review trigger
rerun decisioning
```

---

# 17. Warning Registry

Warning은 통과를 자동 차단하지 않지만 Limitations에 표시한다.

```text
QW_ECONOMICS_PARTIAL
QW_EVIDENCE_GRADE_C
QW_EVIDENCE_GRADE_D
QW_PRECISION_LOW
QW_SMALL_SAMPLE
QW_EXTERNAL_CONTEXT_MISSING
QW_HISTORICAL_OUTCOME_SPARSE
QW_MANUAL_EXECUTION_ONLY
QW_RESULT_DELAY
QW_STAFF_TIME_UNKNOWN
QW_PAYMENT_COVERAGE_PARTIAL
QW_PILOT_PLAYBOOK
QW_MULTIPLE_VALID_OPTIONS
```

Warning을 숨기면 `MATERIAL_LIMITATION_DROPPED`가 될 수 있다.

---

# 18. Policy Validator와 Quality Score

Policy·PII·tenant 위반을 점수로 상쇄하지 않는다.

```text
Policy Hard Fail
→ 즉시 HARD_FAILED
```

Quality Score 100이어도 Hard Fail이 있으면 실패다.

---

# 19. Manual Override 정책

v1에서는 Hard Fail을 일반 사용자나 관리자 권한으로 override할 수 없다.

해결 방식:

```text
입력 수정
Strategy/Playbook 변경
Experiment 재정의
새 Package revision
Quality 재평가
```

정책 예외가 정말 필요하다면:

- 별도 Governance/Legal review
- ADR
- 새로운 정책 version
- 새 Package

가 필요하다.

Quality result를 수동으로 `PASSED`로 바꾸는 API는 두지 않는다.

---

# 20. Quality와 Package Status 연결

```text
Quality NOT_EVALUATED
→ Package DRAFT

Quality HARD_FAILED
→ Package QUALITY_REJECTED

Quality SCORE_FAILED
→ Package QUALITY_REJECTED

Quality PASSED
+ upstream policy/data ready
→ READY_FOR_REVIEW

Quality PASSED
+ missing policy
→ NEEDS_POLICY_REVIEW

Quality PASSED
+ blocking data
→ NEEDS_DATA
```

Quality는 upstream blocker를 지우지 않는다.

---

# 21. AI 출력 품질 규칙

향후 AI가 설명·문구를 생성하더라도:

```text
source numbers read-only
new numeric claim prohibited
Cause fact assertion prohibited
Package structure 변경 금지
Hard Gate 우회 금지
Quality self-score 금지
```

AI가 제공할 수 있는 것:

```text
설명 문장
대안 비교 표현
직원 스크립트 초안
정책 범위 내 콘텐츠 초안
```

모든 AI 출력은 Package source와 validator를 통과해야 한다.

---

# 22. Quality Validator Determinism

동일 입력:

```text
Package revision
Source refs/hashes
Policy result
Validator version
```

동일 결과:

- hard failures
- warnings
- section scores
- total
- status

Score weight·floor·Hard Fail rule이 바뀌면 validator version을 올린다.

---

# 23. API 후보

## Preview 결과에 포함

```text
POST /api/v1/opportunities/{opportunityId}/recommendation-packages/preview
```

## 재평가

```text
POST /api/v1/recommendation-packages/{packageId}/revalidate
GET  /api/v1/recommendation-packages/{packageId}/quality
```

Quality result는 Package revision별 불변 기록으로 저장한다.

---

# 24. DB 후보

```text
recommendation_package_quality_results
recommendation_quality_hard_failures
recommendation_quality_warnings
recommendation_quality_section_scores
```

주요 필드:

```text
id
tenant_id
business_id
package_id
package_revision
validator_version
status
total_score
threshold
source_hash
evaluated_at
```

---

# 25. 테스트 Fixture

## Pass — Execution

- source refs 일치
- retention Strategy eligible
- Playbook eligible
- Target/Owner/Period
- Tracking/Result
- Experiment/Success/Stop
- economics partial limitation

기대:

```text
PASSED
total >= 75
warnings = economics partial
```

## Fail — Generic Advice

```text
"화요일 오후 홍보를 강화하세요."
```

기대:

```text
QH_X01_GENERIC_ADVICE_ONLY
QH_X02_TARGET_OR_SCOPE_UNDEFINED
QH_X04_OWNER_MISSING
QH_X07_TRACKING_MISSING
QH_M01_PRIMARY_METRIC_MISSING
```

## Fail — Estimate as Actual

기대:

```text
QH_C05_ACTUAL_ESTIMATE_MIXED
```

## Fail — Consent Unknown

고객 직접 연락 Package:

```text
QH_P02_CONSENT_REQUIRED
```

## Fail — Diagnostic Vague

```text
"데이터를 더 모으세요."
```

기대:

```text
QH_S06_DATA_COLLECTION_PLAN_INCOMPLETE
QH_X01_GENERIC_ADVICE_ONLY
```

## Pass — HOLD

- reason
- monitoring metric
- review date
- reopen trigger
- limitations

Economics N/A.

기대:

```text
PASSED 가능
```

## Fail — Grade Overstatement

Matched Historical인데 Grade A:

```text
QH_M06_EVIDENCE_GRADE_OVERSTATED
```

---

# 26. Regression 테스트

- 기존 Opportunity 값 불변
- 기존 Recommendation endpoint 불변
- 기존 Action/Result/Measurement 불변
- Quality 실패 Package가 Action으로 변환되지 않음
- 수정 후 새 revision·재평가
- cross-tenant 404
- patient PII 422
- unknown과 0 분리
- 동일 입력 동일 score

---

# 27. 운영 지표

Quality Engine 자체의 품질을 추적한다.

```text
quality_pass_rate
hard_fail_rate
hard_fail_code_distribution
score_fail_rate
section_score_distribution
package_revision_count
manual_modification_rate
ready_to_approved_rate
approved_to_action_rate
result_connection_rate
```

높은 pass rate 자체가 목표는 아니다.
실행 가능한 Package와 결과 연결 품질이 함께 개선되어야 한다.

---

# 28. 로컬 구현 Backlog

```text
RQ-001 Quality status/schema
RQ-002 Hard Fail registry
RQ-003 Warning registry
RQ-004 Package Type rules
RQ-005 Evidence scoring
RQ-006 Specificity scoring
RQ-007 Economics scoring
RQ-008 Feasibility scoring
RQ-009 Measurement scoring
RQ-010 Alternative scoring
RQ-011 Section floors / total
RQ-012 Generic advice structural validator
RQ-013 Policy integration
RQ-014 Deterministic result
RQ-015 Preview API integration
RQ-016 Fixtures / Regression
RQ-017 ADR / Current Status update
```

---

# 29. 완료조건

Recommendation Quality Bar v1 완료조건:

1. Hard Fail registry
2. Warning registry
3. 6개 Section Score
4. Section Floor
5. Total threshold 75
6. Package Type별 평가
7. Generic advice 구조 판정
8. Unknown/Actual/Estimate 의미 검증
9. Policy/PII/tenant Hard Gate
10. Experiment Grade·Success·Stop 검증
11. 수동 override 금지
12. deterministic validator
13. Package status 연결
14. AI self-score 금지
15. 회귀 Fixture
16. 코드 구현 후 CURRENT_IMPLEMENTATION_STATUS 갱신

---


# 30. 구현 연결

Measurement Framework·Channel Execution·통합 Backlog·Data Schema·API Contract가 완료됐다.

구현 기준:

```text
RQ-001~RQ-017
→ RP-010 / RP-013 통합
→ UI-005 Quality 표시
```

첫 Pilot 후에만 `recommendation-quality-v2`의 threshold·weight·section floor 변경을 검토한다.
