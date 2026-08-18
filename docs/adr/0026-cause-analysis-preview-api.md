# ADR 0026 — Cause Analysis Preview API

## Status

Accepted — 2026-08-18

## Context

B02는 `LOW_DEMAND_SLOT` Cause Analysis의 pure Domain을 제공하지만, 사용자 입력 Context와 현재 Opportunity를 안전하게 연결하는 HTTP 경로가 없었다. Client가 Opportunity Observation·Cause score를 제출하도록 하면 source of truth와 tenant scope가 훼손될 수 있고, Cause를 저장된 사실처럼 보이게 할 위험도 있다.

## Decision

- `POST /api/v1/opportunities/{opportunityId}/cause-analyses/preview`를 additive API로 제공한다.
- active tenant의 `owner`, `admin`, `marketer`만 preview를 실행한다. viewer는 실행할 수 없다.
- 서버가 Opportunity와 business scope를 조회하고, request의 Context에는 client가 지정할 수 없는 tenant, business, Opportunity, Observation, detector, snapshot ID를 결합한다.
- 서버가 결합한 Context의 canonical hash, `as_of`, Cause Analysis/Score version으로 deterministic preview ID와 input hash를 만든다.
- preview는 Cause Run을 DB에 저장하지 않고 외부 Action을 만들지 않는다. 다른 tenant Opportunity는 `404`, Hospital PII·clinical field는 `422`다.
- B03에서 Diagnostic Answer는 별도 resource로 저장하지 않는다. Context를 보완해 새 preview를 실행하는 방식만 허용한다.

## Consequences

- Cause Candidate는 계속 가설이며, server-bound Observation과 source reference를 가진 read-only preview 결과로만 반환된다.
- 동일 입력은 같은 결과를 반환하며 legacy Recommendation, Action, Result, Measurement API를 변경하지 않는다.
- Cause persistence, Diagnostic Answer history, Decision Context UI/API는 이후 additive 단계에서 구현한다.

## Rollback

새 endpoint와 application 경로를 비활성화해도 기존 `/api/v1` Recommendation·Action·Measurement 흐름과 DB schema에는 영향이 없다. 저장 부작용이나 migration이 없으므로 rollback은 이전 artifact로 되돌리는 것으로 충분하다.
