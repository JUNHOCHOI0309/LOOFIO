# ADR 0024 — Measurement 의미 계층 분리

- 상태: Accepted
- 기준일: 2026-08-18
- 기준 문서 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`

## Context

실행 기간의 매출, Opportunity 단계의 잠재 가치, 과거 기준선과의 차이, Tracking으로 연결된 결과, 비교군 기반 증분 추정, 비용을 제외한 기여가치는 서로 다른 의미다. 이를 모두 “LOOFIO가 만든 매출”로 합치면 제품 효과를 과장하고 잘못된 학습 데이터를 만든다.

현재 `same-window-prior-four-weeks-v2`는 완료 Appointment의 실제 매출과 직전 1~4주 baseline 평균의 signed delta를 제공하지만, Action의 인과효과나 Incremental Revenue를 계산하지 않는다.

## Decision

API·DB·UI에서 다음 의미를 별도 계약으로 유지한다.

```text
Actual Result
Opportunity Estimate
Baseline
Observed Delta
Attributed Result
Incremental Estimate
Net Contribution Estimate
```

정의:

- `Actual Result`: 실제 Source에서 관찰된 예약·완료·매출·비용.
- `Opportunity Estimate`: 탐지 시점의 가정 기반 잠재 범위.
- `Observed Delta`: 관찰값과 baseline의 단순 차이.
- `Attributed Result`: Tracking으로 Action에 연결된 결과. 증분을 의미하지 않는다.
- `Incremental Estimate`: 사전 정의된 Treatment와 Comparison의 차이를 이용한 추정.
- `Net Contribution Estimate`: 증분 Outcome과 완전한 비용 정보를 이용한 경제성 추정.

Grade C/D Measurement는 기본적으로 `incremental_estimate = null`을 유지한다.

비용 상태는 `VERIFIED`, `ESTIMATED`, `UNKNOWN`, `NOT_APPLICABLE`, `CONFLICTING`으로 구분하고 `UNKNOWN`을 0으로 처리하지 않는다. 주요 비용이 complete 또는 명시적 N/A일 때만 Net Contribution을 계산한다.

목표 슬롯 성과와 함께 다른 슬롯·Offering·전체 Business 결과를 확인해 displacement와 cannibalization을 숨기지 않는다.

## Consequences

- UI는 Actual, Estimate, Delta, Attributed, Incremental을 서로 다른 라벨로 표시한다.
- 현재 Measurement API의 숫자와 의미는 유지하고 Framework Adapter에서 Grade C와 limitation을 추가한다.
- 새로운 Measurement Method는 versioned Run으로 저장하며 과거 결과를 재해석하지 않는다.
- Decision Outcome Record는 Evidence Grade, Precision, economics status, limitations를 함께 보존한다.
- Fine-tuning 전에 의미가 안정된 Decision→Outcome 데이터셋을 만들 수 있다.

## Risk self-review

- 필드 수와 설명이 늘어나지만 제품 신뢰를 위해 의미 단순화보다 정확성을 우선한다.
- Attributed와 Incremental을 혼동하지 않도록 API contract test와 UI wording fixture를 둔다.
- 직원 시간·변동원가가 없는 경우 경제성 partial을 유지하며 임의 기본값을 넣지 않는다.
- External Context는 limitation과 비교 가능성 검토에 사용하며 완전한 인과 보정으로 표현하지 않는다.

## Rollback

신규 persisted Measurement와 UI를 비활성화하고 현재 `same-window-prior-four-weeks-v2` Response로 되돌린다. 이미 생성된 Measurement Run은 삭제하거나 의미를 변경하지 않는다.
