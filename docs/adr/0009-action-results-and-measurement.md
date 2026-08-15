# ADR 0009 — 수동 Action Result와 비인과적 Measurement

## Status

Accepted

## Decision

- `completed` Action에만 실행 요약, 측정 기간, 선택적 실제 지출과 결과 메모를 한 번 기록한다.
- 실제 매출을 사용자가 직접 결과로 입력하지 않는다. 저장된 Appointment의 `completed` / `paid_amount`만 실제 완료 매출 Observation으로 집계한다.
- Measurement는 Result 기간과 같은 길이의 직전 1~4주 창을 baseline으로 하고, 평균 baseline과 단순 차이를 반환한다.
- 결과와 측정은 tenant·Action·business scope를 유지하며, `same-window-prior-four-weeks-v1` method version을 반환한다.
- 변화량은 인과효과, LOOFIO 기여도, Incremental Revenue, ROI로 표현하지 않는다.

## Consequences

- `Recommendation → Decision → Action → Result → Measurement`의 MVP 추적 경로가 완성된다.
- 날짜·날씨·행사·수용량·동시 시행 액션을 보정하지 않으므로, 고급 Incrementality는 별도 설계가 필요하다.

## Rollback

Migration은 additive다. Result/Measurement endpoint를 비활성화해도 기존 Action과 예약 데이터는 보존된다.
