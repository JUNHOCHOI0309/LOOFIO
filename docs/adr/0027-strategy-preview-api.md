# ADR 0027 — Strategy Preview API

## Status

Accepted — 2026-08-18

## Context

B04는 `LOW_DEMAND_SLOT`의 Cause-to-Strategy pure Domain을 제공하지만, 현재 Opportunity와 사용자가 보완한 Decision Context를 tenant 범위 안에서 결합해 Strategy 후보를 검토할 HTTP 경로가 없었다. Client가 Cause Analysis나 Strategy score를 제출하게 하면 서버의 Opportunity observation, Cause 근거, tenant/business scope가 서로 어긋날 수 있고, Preview 결과를 저장된 실행 지시처럼 오해할 위험이 있다.

## Decision

- `POST /api/v1/opportunities/{opportunityId}/strategy-runs/preview`를 additive API로 제공한다.
- active tenant의 `owner`, `admin`, `marketer`만 Preview를 실행한다. `viewer`는 실행할 수 없다.
- 서버가 Opportunity와 business scope를 조회하고, client가 제어할 수 없는 tenant, business, Opportunity, Observation, detector, snapshot ID를 Context에 결합한다.
- 서버는 결합한 Context로 Cause Analysis를 먼저 재계산하고, 그 결과만 Strategy Domain에 전달한다. Client는 Cause Analysis, Strategy Run, 선택 결과를 제출하거나 변경할 수 없다.
- 서버는 canonical Context hash, `as_of`, Cause/Strategy engine version으로 deterministic preview ID와 input hash를 만든다.
- Preview는 Cause Analysis나 Strategy Run을 DB에 저장하지 않고 Playbook, Action 또는 외부 채널 실행을 만들지 않는다. 다른 tenant Opportunity는 `404`, Hospital PII·clinical field는 `422`다.
- B05에는 Strategy selection override나 Strategy Run persistence를 포함하지 않는다.

## Consequences

- Strategy 후보와 `DATA_COLLECTION`/`NO_ACTION` fallback은 현재 입력과 Cause 가설에 연결된 read-only 결과다. 성공 확률, ROI 또는 자동 실행 지시가 아니다.
- 동일 입력은 동일 결과를 반환하며 기존 Recommendation, Action, Result, Measurement API와 DB schema를 변경하지 않는다.
- Playbook resolution, selection override, Decision Context 입력 UI, persistence와 실행 승인은 이후 additive 단계에서 구현한다.

## Rollback

새 endpoint와 application 경로를 비활성화해도 기존 `/api/v1` Recommendation·Action·Measurement 흐름과 DB schema에는 영향이 없다. 저장 부작용이나 migration이 없으므로 rollback은 이전 artifact로 되돌리는 것으로 충분하다.
