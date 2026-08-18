# ADR 0022 — Recommendation Quality Gate v1

- 상태: Accepted
- 기준일: 2026-08-18
- 기준 문서 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`

## Context

Recommendation이 길거나 자연스럽게 작성됐다는 이유만으로 고객에게 제공할 수준이라고 판단할 수 없다. 근거, 대상, 실행 단계, 경제성, 측정, 대안 비교가 없는 일반 조언은 실제 실행을 시작하기 어렵고 효과도 검증할 수 없다. 또한 정책·PII·추적·경제성 오류는 총점이 높더라도 허용할 수 없다.

## Decision

Recommendation Package는 deterministic Quality Validator를 통과해야 `READY_FOR_REVIEW`가 될 수 있다.

v1 기준은 다음과 같다.

```text
Total Score >= 75
AND
Hard Fail = 0
AND
모든 Section Floor 충족
```

점수 구성:

```text
Evidence Linkage        20
Specificity             20
Economics Integrity     20
Feasibility             15
Measurement Design      15
Alternative Comparison  10
Total                   100
```

Section Floor:

```text
Evidence Linkage        14 / 20
Specificity             14 / 20
Economics Integrity     10 / 20
Feasibility             10 / 15
Measurement Design      10 / 15
Alternative Comparison   6 / 10
```

Hard Fail은 다음 범주를 포함한다.

- Source 누락, Observation 변경, 근거 없는 숫자 생성
- Cause를 사실로 표현하거나 material limitation 제거
- 대안 비교 없음, 실행 불가 Strategy·Playbook 선택, Contraindication 위반
- Target·Owner·기간·단계·Tracking·Result Source 누락
- `unknown` 비용을 0으로 처리하거나 불완전 비용으로 순기여가치 계산
- Primary Metric·비교·성공·중단·Attribution 누락, Evidence Grade 과장
- 정책·동의 미완료, 환자 PII, 임상 Targeting, 승인 없는 자동 실행

Hard Fail을 일반 사용자나 관리자가 수동으로 `PASSED`로 바꾸는 Override API는 만들지 않는다. 입력·Strategy·Playbook·Experiment를 수정해 새 Package revision을 생성하고 다시 평가한다.

Quality v1의 threshold·weight·floor는 첫 Pilot 후 versioned 재검토 대상이다. Quality Score는 성공 확률이나 ROI가 아니다.

## Consequences

- 품질이 낮은 초안은 `NEEDS_DATA`, `NEEDS_POLICY_REVIEW`, `QUALITY_REJECTED` 상태로 남는다.
- Package Type이 `DIAGNOSTIC` 또는 `HOLD`여도 Type에 맞는 구체적 수집·모니터링 계약이 필요하다.
- Quality Result는 Package revision·validator version·source hash별 불변 기록으로 저장한다.
- AI는 Quality를 자기평가하거나 Hard Fail을 우회할 수 없다.
- UI는 총점뿐 아니라 Section Floor, Hard Fail, Warning을 표시해야 한다.

## Risk self-review

- 초기 수치가 실제 사용자 가치와 완전히 일치하지 않을 수 있으므로 `recommendation-quality-v1`으로 버전 관리하고 Pilot 데이터를 통해 조정한다.
- 높은 통과율 자체를 목표로 삼지 않고 승인·수정·실행·결과 연결률을 함께 본다.
- Validator 오류가 기존 제품을 중단하지 않도록 legacy Recommendation fallback을 유지한다.
- 정책·PII Hard Fail은 점수 조정 대상이 아니다.

## Rollback

신규 Package의 final 노출과 Package 기반 Action 생성을 중단하고 legacy Recommendation 흐름으로 되돌린다. Hard Fail을 우회하는 방식으로 rollback하지 않는다. 기존 Quality Result는 감사 목적으로 유지한다.
