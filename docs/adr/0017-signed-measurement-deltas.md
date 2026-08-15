# ADR 0017 — Signed Measurement Deltas v2

## Status

Accepted

## Context

견본 데이터 제품 루프 시뮬레이션에서 측정 창의 예약·취소·노쇼 건수가 baseline 평균보다 낮아질 때 `change_from_baseline`이 음수가 된다. 기존 `MeasurementMetrics`는 관찰값을 표현하는 타입이라 모든 건수에 0 이상 제약이 있었고, 이 정상적인 감소를 반환하지 못하고 validation error가 발생했다.

## Decision

- 관찰값과 baseline 평균에는 기존의 0 이상 `MeasurementMetrics`를 유지한다.
- `change_from_baseline`에는 음수 변화를 허용하는 `MeasurementDelta`를 사용한다.
- 측정 방법 버전을 `same-window-prior-four-weeks-v2`로 올린다.
- 변화량은 단순 관찰 차이이며 인과효과·Incremental Revenue·ROI가 아니라는 기존 limitation을 유지한다.

## Self-review

- Action/Measurement 관점: 감소한 예약·완료·취소·노쇼 수가 오류 없이 반환되고, 기존 양수 변화 응답도 유지되는지 확인했다.
- API 관점: 필드 이름과 관찰값 구조는 유지하고, `change_from_baseline`의 유효 범위를 올바르게 확장했다. 소비자는 method version으로 해석 차이를 구분할 수 있다.

## Rollback

문제가 발생하면 Measurement endpoint를 비활성화하거나 forward fix한다. 이미 기록된 Result와 Action은 수정·삭제하지 않는다.
