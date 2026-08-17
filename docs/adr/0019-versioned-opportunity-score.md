# ADR 0019 — Versioned Opportunity Score

- 상태: Accepted
- 기준일: 2026-08-17

## Context

Opportunity 목록에는 `score`가 있었지만 Detector별 임시 수식이 각 builder에 흩어져 있었다. 구성요소와 계산 버전이 저장되지 않아 서로 다른 기회 유형의 우선순위를 설명하거나 과거 결과를 재현하기 어려웠다.

## Decision

공통 deterministic scoring 모듈 `opportunity-score-v1`을 사용한다.

```text
Impact        35
Confidence    30
Persistence   20
Actionability 15
Total        100
```

각 Detector builder는 아래 0~1 factor만 결정하고, 공통 모듈이 범위를 0~1로 제한한 뒤 점수를 계산한다.

| Opportunity | Impact factor | Persistence factor | Actionability |
|---|---|---|---:|
| LowDemand + RevenueGap | 월 상단 Estimate ÷ 1,000,000원. Estimate가 없으면 `1 - DemandIndex` | 관측 주 ÷ 12 | 1.0 |
| CancellationHotspot | 전체 기준 대비 초과 예약 이탈률을 남은 비이탈 구간으로 정규화 | 관측 주 ÷ 12 | 0.9 |
| ServiceDemandGap | `1 - ShareIndex` | 관측 주 ÷ 12 | 0.8 |
| DormantCustomer | 1.3배 기준 초과분을 2.0배에서 상한 처리 | 재방문 간격 표본 ÷ 4 | 1.0 |

Confidence factor는 각 Detector가 이미 데이터 준비도와 표본으로 계산한 `confidence`를 그대로 사용한다. 점수는 후보 검토 순서를 정하는 상대 우선순위이며 성공 확률, 인과효과, 실제 손실 또는 보장 매출이 아니다.

`opportunities`에 `score_version`과 `score_breakdown`을 additive migration으로 추가한다. 기존 행의 점수는 재해석하지 않고 `legacy-unversioned-v0`로 표시하며 breakdown은 비어 있을 수 있다. 현재 Detector가 다시 탐지한 열린 Opportunity만 v1 점수로 갱신한다.

## Consequences

- API와 UI에서 점수의 네 구성요소와 버전을 설명할 수 있다.
- 모든 기회 유형이 같은 100점 가중치 체계를 사용한다.
- factor의 의미가 변경되면 새 score version을 만들고 과거 점수는 유지해야 한다.
- 유형 간 Impact proxy의 경제적 단위가 완전히 같지는 않으므로 점수 자체를 매출 가치로 사용하지 않는다.

## Risk self-review

- DB 변경은 컬럼 추가만 수행하며 기존 점수와 행을 삭제하거나 재계산하지 않는다.
- API 변경은 필드 추가이며 기존 `score`와 `confidence` 의미를 제거하지 않는다.
- tenant/business query와 PII 처리 범위는 변경하지 않는다.
- 점수 경계, 가중치 합계, 0~100 clamp, API total 일치를 회귀 테스트한다.

## Rollback

애플리케이션을 이전 버전으로 되돌려도 추가 컬럼은 기존 코드에 영향을 주지 않는다. 데이터 보존을 위해 컬럼을 즉시 삭제하지 않으며, 후속 contract migration 전까지 유지한다.
