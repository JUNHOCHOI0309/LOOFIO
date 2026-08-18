# ADR 0023 — 실행 전 Experiment 계약 고정

- 상태: Accepted
- 기준일: 2026-08-18
- 기준 문서 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`

## Context

실행 후 결과를 확인한 뒤 성공 지표, 비교 기간, 대상, 중단 기준을 정하면 유리한 결과만 선택해 해석할 수 있다. 현재 `same-window-prior-four-weeks-v2`는 유용한 관찰 비교이지만 동시 비교군이 없고 인과효과를 의미하지 않는다. Playbook을 고객에게 실행 가능한 추천으로 제공하려면 무엇을 어떻게 검증할지 실행 전에 고정해야 한다.

## Decision

실행 가능한 Playbook은 Action 전에 `ExperimentDefinition`을 가진다.

필수 계약:

```text
objective / hypothesis / estimand
population / exclusion
assignment unit and rule
treatment / comparison
start / end / attribution window
Primary Metric exactly one
secondary metrics / guardrails
success threshold
stop conditions
Tracking / Result Source
owner / approval
Evidence Grade plan / Precision status
```

Experiment 객체를 다음으로 분리한다.

```text
ExperimentTemplate
→ ExperimentDefinition
→ ExperimentRun
→ ExperimentResult
→ ExperimentEvaluation
```

`RUNNING` 이후 hypothesis, assignment, treatment, comparison, Primary Metric, success/stop, attribution, budget cap 같은 핵심 계약은 수정하지 않는다. 변경이 필요하면 기존 실험을 `STOPPED` 또는 `INVALIDATED`하고 새 Definition revision을 만든다.

Evidence Grade와 Precision을 분리한다.

```text
Grade A: Randomized comparison
Grade B: Prospective cluster/shift/alternating/route comparison
Grade C: Matched historical / prior-window comparison
Grade D: Before-after / diagnostic / manual attribution
```

현재 `same-window-prior-four-weeks-v2`는 기본 Grade C이며 조건이 약하면 D로 하향한다. Grade C/D 결과를 Incremental Revenue로 표시하지 않는다.

## Consequences

- 성공·실패·중단의 기준을 실행 전에 사용자와 합의할 수 있다.
- 작은 표본에서는 Grade가 높아도 Precision이 낮아 `INCONCLUSIVE`일 수 있다.
- Diagnostic와 `NO_ACTION`도 각각 검증·모니터링 계약을 가진다.
- Action Result와 현재 Measurement는 새 Experiment 구조의 fallback 및 adapter로 재사용한다.
- 실행 중 계약 변경과 contamination·displacement를 기록해야 한다.

## Risk self-review

- 작은 병원 데이터에서 강한 실험 설계가 어려울 수 있으므로 Grade C/D를 허용하되 표현을 제한한다.
- 표본 최소 가이드는 통계적 power 보장이 아니며 향후 별도 method version으로 확장한다.
- Experiment 설계가 운영 부담을 지나치게 높이지 않도록 Time to Learning과 staff burden을 Strategy·Playbook 단계에서 검토한다.
- 고객 직접 접촉 실험은 동의·정책·PII 제한을 먼저 통과해야 한다.

## Rollback

신규 Experiment 기반 실행을 비활성화하고 기존 Manual Action·Result·historical Measurement로 되돌린다. 이미 시작된 Experiment의 계약을 삭제하거나 결과에 맞게 수정하지 않는다.
