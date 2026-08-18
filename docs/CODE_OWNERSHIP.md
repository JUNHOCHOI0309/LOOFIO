# LOOFIO Code Ownership v2

- 기준일: 2026-08-18
- 기준 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`
- 상태: 역할 기반 logical ownership

실제 GitHub team/handle은 확정되지 않았다.
`.github/CODEOWNERS` 적용 전 placeholder를 실제 계정으로 바꿔야 한다.

---

# 1. Ownership 원칙

Owner의 책임:

- 설계 일관성
- 데이터·보안 영향
- API/DB 호환성
- deterministic 재현성
- version
- 테스트와 golden fixture
- 문서
- rollout/rollback
- 위험 승인

Ownership은 독점 개발 권한이 아니다.

---

# 1.1 Decision Intelligence Ownership

Decision Intelligence는 다음 책임을 분리한다.

```text
Decision Input / Cause Analysis / Strategy
Playbook / Experiment
Recommendation Package / Quality
AI Gateway / Explanation / Content
Action / Channel / Measurement
```

한 Owner가 전체 파이프라인을 검토할 수는 있지만, 계산·정책·실행·측정 관점을 하나로 합쳐 승인하지 않는다.

---

# 2. Logical Owners

## Repository Maintainer

범위:

```text
docs/
README
build/dependency config
cross-module architecture
```

책임:

- Source of Truth
- 문서 우선순위
- release gate
- cross-module change

## Core Platform Owner

범위:

```text
api/app/auth
tenant/business/location
offerings/customers
api/migrations
repository scope
```

책임:

- tenant isolation
- schema/migration
- auth/session
- PII boundary

## Data Ingestion Owner

범위:

```text
api/app/imports
mapping
normalization
lineage
sample-data
```

책임:

- CSV contract
- idempotency
- PII guard
- invalid row handling
- data quality

## Opportunity Intelligence Owner

범위:

```text
api/app/metrics
api/app/analytics/detectors
api/app/analytics/scoring
api/app/opportunities
```

책임:

- Metric
- Detector
- Evidence
- Estimate
- Opportunity Score
- version/regression

## Cause & Strategy Owner

목표 범위:

```text
decisioning/causes
decisioning/strategies
cause taxonomy
strategy mapping
economics/feasibility interfaces
```

책임:

- cause hypothesis semantics
- evidence/contradiction
- strategy alternatives
- no-action/data-collection
- deterministic scoring

## Playbook & Experiment Owner

목표 범위:

```text
playbook registry
applicability
experiment templates
evidence grade
success/stop
```

책임:

- Playbook status/version
- precondition/contraindication
- online/offline step quality
- experiment integrity
- quality of result source

## Recommendation Package & Quality Owner

목표 범위:

```text
future recommendation_packages
recommendation package assembler
quality validator
legacy recommendation adapter
```

책임:

- Package source·revision·status 계약
- 대안·선택 이유·실행 단계 조립
- Evidence fidelity와 limitation 전파
- Quality Score·Section Floor·Hard Fail
- Legacy Recommendation/Action 호환
- 근거 없는 수치와 일반 조언 차단

## AI Gateway & Content Owner

목표 범위:

```text
AI gateway / provider adapter
prompt / structured output schema
explanation / content / staff script draft
```

책임:

- provider abstraction
- 최소 AI context와 PII 차단
- structured output와 prompt version
- deterministic source fidelity
- cost / latency / failure isolation
- AI가 score·경제성·measurement를 계산하지 않도록 보장

## Action / Channel / Measurement Owner

범위:

```text
api/app/actions
api/app/results
future channel_execution
measurement methods
```

책임:

- approval
- Action state
- tracking
- Result
- baseline
- Evidence Grade
- economics output
- external execution safety

## Connector Owner

범위:

```text
external data
reservation/POS
weather/public data
messaging/ads
sync jobs
```

책임:

- provider contract
- OAuth/secret
- retry/rate limit
- external reference
- delivery/result event

## Product/UI Owner

범위:

```text
apps/web
Opportunity/Diagnosis/Plan/Action/Results UI
```

책임:

- semantic separation
- limitations/confidence/grade
- alternative comparison
- Quality status
- approval UX
- no causal overclaim

## Infrastructure/Security Owner

범위:

```text
CI/CD
staging/production
secrets
monitoring
backup/restore
security configuration
```

책임:

- deployment
- runtime isolation
- observability
- incident/rollback
- secure AI/connector config

---

# 3. Mandatory Review Matrix

| 변경 | 필수 Owner |
|---|---|
| AGENTS/Architecture/Dependency | Repository + 영향 Owner |
| Tenant/Auth/Session | Core + Security |
| PII/Tokenization | Core + Ingestion + Security |
| DB migration | Core + 영향 Domain Owner |
| Metric/Detector | Opportunity Intelligence |
| Opportunity Score | Opportunity Intelligence |
| Cause taxonomy/score | Cause & Strategy + Opportunity |
| Cause→Strategy mapping | Cause & Strategy |
| Strategy Score/Economics input | Cause & Strategy + Action/Measurement |
| Playbook 신규/변경 | Playbook & Experiment + 관련 Domain |
| Playbook ACTIVE 승격 | Playbook & Experiment + Product + Policy 영향 Owner |
| Experiment method/Grade | Playbook & Experiment + Measurement |
| Recommendation Package schema | Recommendation Package/Quality + API/Product |
| Recommendation Quality Bar | Recommendation Package/Quality + Playbook/Experiment + Product |
| AI provider/context/prompt | AI Gateway/Content + Security |
| External message/ad execution | Connector + Action/Measurement + Security |
| Offline partner execution | Action/Measurement + Product |
| Measurement/Incrementality | Action/Measurement |
| API breaking change | Repository + 영향 Owner |
| Deployment/Secret | Security |
| Prohibited Changes | Repository + 관련 Owner |

---

# 4. High-Risk Multi-Owner Rule

최소 2개 영역의 리뷰가 필요한 변경:

- patient/customer data를 AI에 더 많이 전송
- Quality Gate 완화
- Playbook contraindication 완화
- Hospital policy 변경
- 자동 메시지·광고·쿠폰
- budget automation
- Incremental Revenue 표시
- tenant isolation
- destructive migration
- production secret/auth
- offline partner compensation logic

1인 개발 단계에서도 PR/변경기록에 서로 다른 관점의 자기검토를 분리한다.

---

# 5. Playbook Ownership

각 Playbook은 메타데이터를 가진다.

```text
owner
version
status
last_reviewed_at
policy_tags
historical_execution_count
result_connection_rate
```

`ACTIVE` 승격은 단순 문서 작성이 아니라 내부 검증 또는 pilot 근거가 필요하다.

---

# 6. Quality Ownership

Recommendation Quality Validator의 규칙 변경은 일반 UI/문구 변경이 아니다.

필수 검토:

- Evidence
- Economics
- Experiment
- Policy
- Product UX

Quality score weight 변경 시 version을 올린다.

---

# 7. CODEOWNERS 적용 후보

현재 `main`에는 `.github/CODEOWNERS`와 `.github/CODEOWNERS.template`이 없다. 따라서 아래는 논리적 후보이며 실제 branch protection이 적용된 것으로 간주하지 않는다.

```text
/api/app/analytics/                 @OPPORTUNITY_OWNER
/api/app/decisioning/               @CAUSE_STRATEGY_OWNER
/api/app/playbooks/                 @PLAYBOOK_EXPERIMENT_OWNER
/api/app/recommendation_packages/   @RECOMMENDATION_PACKAGE_OWNER
/api/app/ai/                        @AI_GATEWAY_OWNER
/api/app/actions/                   @ACTION_MEASUREMENT_OWNER
/api/app/results/                   @ACTION_MEASUREMENT_OWNER
/api/migrations/                    @CORE_PLATFORM_OWNER
/apps/web/                          @PRODUCT_UI_OWNER
/docs/                              @REPOSITORY_MAINTAINER
```

실제 GitHub 사용자·팀이 확정되면 `.github/CODEOWNERS`를 새로 만들고 branch protection과 함께 검증한다.

---

# 8. Ownership 변경

1. 이 문서
2. CODEOWNERS
3. branch protection
4. alerts/runbook
5. Playbook metadata

순서로 갱신한다.
