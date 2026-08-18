# LOOFIO Dependency Rules v2

- 기준일: 2026-08-18
- 기준 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`
- 상태: 현재 모듈 경계 + Decision Intelligence 추가 규칙

## 1. 목적

LOOFIO가 특정 AI 모델·광고 채널·데이터 공급자에 강결합되지 않으면서, 각 의사결정 단계가 자기 책임만 수행하도록 의존 방향을 정의한다.

---

# 2. 기본 방향

```text
Apps / UI
  ↓
API
  ↓
Application
  ↓
Domain / Analytics / Decision Intelligence
  ↓
Ports / Contracts

Infrastructure / AI / Connectors
  → Ports 구현
```

안쪽 계층은 provider SDK와 HTTP controller를 알지 않는다.

---

# 3. 정상 데이터 의존 흐름

```text
Raw Import
→ Normalized Domain
→ Metric
→ Detector
→ Opportunity
→ Cause Candidate
→ Strategy Candidate
→ Playbook Resolution
→ Economics / Feasibility
→ Experiment
→ Recommendation Package
→ Quality Result
→ User Decision
→ Action
→ Result
→ Measurement
```

허용되는 backward feedback:

```text
Decision / Result / Measurement
→ 다음 분석의 historical context
```

과거 결과는 새 Opportunity의 사실을 직접 덮어쓰지 않고 versioned context로 사용한다.

---

# 4. 허용 관계

| From | To | 허용 |
|---|---|---|
| Apps/UI | API contract | ✅ |
| API route | Application use case | ✅ |
| Application | Domain / Port | ✅ |
| Normalizer | Domain contract | ✅ |
| Metrics | normalized Domain | ✅ |
| Detector | metric DTO | ✅ |
| Opportunity | detector/scoring output | ✅ |
| Cause Analysis | Opportunity/Evidence/aggregate context | ✅ |
| Strategy Engine | Cause/constraints/economics port | ✅ |
| Playbook Resolver | Strategy + registry + policy | ✅ |
| Economics | explicit cost/value inputs | ✅ |
| Experiment Designer | Playbook + deterministic metric catalog | ✅ |
| Recommendation Package Assembler | Cause/Strategy/Playbook/Experiment outputs | ✅ |
| Quality Validator | Recommendation Package | ✅ |
| Action | approved Recommendation Package or legacy approved Recommendation | ✅ |
| Channel Execution | approved Action + Connector Port | ✅ |
| Measurement | Action/Result/baseline/context | ✅ |
| AI Adapter | AI Port + provider SDK | ✅ |
| Connector | Connector Port + provider SDK | ✅ |
| Infrastructure | Repository/Secret/Queue Port | ✅ |

---

# 5. 금지 관계

| From | To | 금지 이유 |
|---|---|---|
| Metric / Detector | LLM or HTTP | 계산 재현성 훼손 |
| Opportunity | Content Generator | 탐지와 실행 혼합 |
| Cause Analysis | Raw Import 전체 | 정규화·Evidence 경계 우회 |
| Cause Analysis | Cause fact assertion | 가설을 사실로 오염 |
| Strategy Engine | AI Provider SDK | ranking 재현성·교체성 훼손 |
| Strategy Engine | Channel execution implementation | 선택과 실행 결합 |
| Playbook Definition | tenant-specific customer/data | registry 오염 |
| Playbook | unversioned free text only | 재현·평가 불가 |
| Economics | AI-generated numeric values | 비용·가치 신뢰성 훼손 |
| Experiment | AI text as metric source | 성공 판정 재현성 훼손 |
| Recommendation Package Assembler | Raw rows / DB arbitrary query | 이전 단계 우회 |
| Recommendation Package Assembler | Opportunity numeric recalculation | Source of Truth 중복 |
| Quality Validator | provider-specific output semantics | 공급자 강결합 |
| Channel Connector | Opportunity 판단 | 수집/실행과 의사결정 혼합 |
| Channel Execution | approval bypass | 제품 안전 위반 |
| Measurement | Recommendation Estimate as Actual | 실제·추정 혼합 |
| UI | Database | API/authorization 우회 |
| Tenant A context | Tenant B data | 격리 위반 |

---

# 6. Opportunity Engine

```text
metrics
→ detectors
→ scoring
→ opportunity persistence
```

허용:

- pure domain type
- metric DTO
- detector config
- time/money utility

금지:

- AI SDK
- prompt
- content
- channel connector
- external ad API
- user messaging
- Playbook selection

---

# 7. Cause Analysis

입력:

```text
Opportunity
Evidence
Limitations
Metric Summary
Business / Offering / Operational aggregate
External Context(optional)
```

Cause module은 다음 Port를 통해 aggregate context를 받는다.

```text
BusinessContextReader
OperationalConstraintReader
HistoricalActionSummaryReader
ExternalContextReader
```

Raw import repository를 직접 호출하지 않는다.

Cause wording에 AI를 사용하더라도 candidate seed·evidence refs·missing data·score는 구조화된 결과가 우선이다.

---

# 8. Strategy Engine

```text
Cause Candidate
+ Business Constraints
+ Economics Inputs
+ Available Channels
+ Policy
→ Strategy Candidates
```

Strategy ranking은 provider-neutral deterministic rule/score로 시작한다.

AI는 selection reason 문장만 보조할 수 있다.

Strategy module이 직접 광고 캠페인·고객 메시지·Playbook step을 생성하지 않는다.

---

# 9. Action Playbook

Playbook Definition은 versioned registry다.

허용:

- archetype
- opportunity/cause/strategy code
- required data
- precondition/contraindication
- step template
- economics template
- experiment template
- policy tags

금지:

- 특정 tenant ID
- 특정 고객 ID
- 특정 병원명
- runtime 예산
- 실제 대상 cohort
- 외부 provider credential

Runtime 값은 `PlaybookInstance` 또는 Recommendation Package에 저장한다.

---

# 10. Economics / Feasibility

Economics module은 explicit value object를 사용한다.

```text
Money
CostComponent
ContributionAssumption
CapacityConstraint
BudgetCap
```

`unknown`과 `0`은 다른 값이다.

LLM이나 자연어 설명에서 비용을 parse해 Source of Truth로 사용하지 않는다.

---

# 11. Experiment Design

Experiment Designer는 Metric Catalog와 비교 방식 Contract에 의존한다.

금지:

- prompt 문장으로 primary metric 결정
- 결과가 나온 뒤 success threshold 변경
- Evidence Grade를 UI에서만 임의 변경
- Action result를 직접 수정

Experiment은 실행 전에 versioned definition으로 고정한다.

---

# 12. Recommendation Package Assembler

Recommendation Package Assembler는 조립 계층이다.

```text
Opportunity
Cause Analysis
Strategy Comparison
Playbook Instance
Economics
Experiment
Channel Plan
→ Recommendation Package
```

Recommendation Package Assembler가 다음을 수행하면 안 된다.

- Detector 재실행
- raw data query
- cost invent
- success metric 변경
- Playbook contraindication 우회
- approval 생성

---

# 13. Recommendation Quality

Quality Validator는 deterministic rule을 우선한다.

입력:

```text
Recommendation Package
+ Source References
+ Policy Result
```

출력:

```text
score
section breakdown
hard failures
status
validator version
```

Quality Validator는 AI의 자기평가 점수를 사용하지 않는다.

---

# 14. AI Dependency

```text
Application / Recommendation Package Assembler
→ AI Port
← AI Adapter
  → Provider SDK
```

AI Gateway task 예:

```text
cause_hypothesis_wording
alternative_comparison_explanation
action_plan_explanation
content_draft
```

금지:

```text
detector_calculation
economics_calculation
experiment_result
quality_score
```

---

# 15. Channel Execution / Connector

```text
Approved Action
→ Execution Port
← Online / Offline Connector
```

Connector 책임:

- provider DTO
- API call
- rate limit
- retry
- external reference
- delivery/result event

Connector가 결정하지 않는 것:

- Opportunity
- Cause
- Strategy
- target rationale
- budget policy
- Measurement interpretation

오프라인 실행도 Connector와 유사한 tracking contract를 사용한다.

---

# 16. Measurement

```text
Action
+ Result
+ Baseline
+ External Context
+ Cost
→ Measurement
```

Measurement는 AI 설명을 Source of Truth로 사용하지 않는다.

Grade C/D를 causal effect로 승격하지 않는다.

---

# 17. Shared/Common 제한

허용:

- time/date
- money
- ID
- pagination
- generic errors
- validation primitives
- version type

금지:

- Cause rule
- Strategy rule
- Playbook
- economics formula
- experiment method
- AI prompt
- Connector rule
- repository implementation

---

# 18. Circular Dependency

예:

```text
strategy → playbook → strategy
```

발생 시:

1. immutable contract 추출
2. application orchestration으로 이동
3. registry port 분리
4. module boundary 재검토

DI container로 숨기지 않는다.

---

# 19. 테스트 경계

다음은 DB·HTTP·AI 없이 pure test가 가능해야 한다.

- Detector
- Opportunity Score
- Cause candidate seeding/scoring
- Cause→Strategy mapping
- Strategy Score
- Playbook applicability
- Economics calculation
- Experiment validation
- Recommendation Quality Score

Repository/AI/Connector는 integration/contract test에서 검증한다.

---

# 20. 현재 코드와 목표 모듈

현재:

```text
api/app/analytics
api/app/opportunities
api/app/recommendations
api/app/actions
api/app/results
```

목표는 additive 확장이다.

기존 module을 즉시 삭제·이동하거나 기존 endpoint를 깨지 않는다.

---

# 21. 변경 규칙

새 dependency 추가 전 확인:

- 어느 계층인가
- deterministic stage를 vendor에 묶는가
- tenant/PII 영향
- versioning 필요
- test isolation 가능
- fallback 가능
- rollback/disable 가능
- 기존 `/api/v1` 호환성

새 외부 SDK는 Core/Analytics/Decision Logic에 직접 추가하지 않는다.
