# AGENTS.md — LOOFIO Repository Rules v2

- 기준일: 2026-08-18
- 기준 브랜치: `main`
- 문서 정렬 기준 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`
- 상태: 현재 구현 불변조건 + Decision Intelligence 목표 설계

## 0. 목적

이 파일은 LOOFIO 저장소에서 작업하는 사람과 AI 에이전트가 반드시 따라야 하는 최상위 개발 규칙이다.

LOOFIO의 제품 목적은 다음과 같다.

> 사업 데이터를 관찰하고, 아직 잡지 못한 매출 기회를 데이터에서 탐지한 뒤, 가능한 원인과 대안을 비교하고, 경제성·실행 가능성·측정 계획이 포함된 행동 패키지를 제안하며, 실행 결과를 다음 판단에 반영한다.

목표 제품 루프:

```text
Observe
→ Opportunity
→ Cause Analysis
→ Strategy Comparison
→ Action Playbook
→ Economics / Feasibility
→ Experiment Design
→ Recommendation Package
→ User Decision
→ Action
→ Result
→ Measurement
→ Learn
```

현재 구현은 `Opportunity → deterministic Recommendation Draft → Decision → Manual Action → Result → Measurement`까지다.
새 Cause·Strategy·Playbook·Experiment·Recommendation Package 문서는 **목표 설계**이며, migration·code·test가 반영되기 전에는 구현 완료로 간주하지 않는다.

LOOFIO의 핵심 결과물은 콘텐츠가 아니라 다음이다.

> **왜 이 행동이 1순위인지 설명할 수 있고, 담당자가 바로 실행할 수 있으며, 비용과 결과를 측정할 수 있는 Action Plan Package**

---

# 1. 작업 전 필수 확인

구조적 변경 전 다음 순서로 확인한다.

1. `docs/00_PLANNING_INDEX.md`
2. `docs/CURRENT_IMPLEMENTATION_STATUS.md`
3. `docs/DECISION_REGISTER_V2.md`
4. `docs/AGENTS.md`
5. `docs/PROHIBITED_CHANGES.md`
6. `docs/ARCHITECTURE.md`
7. `docs/DEPENDENCY_RULES.md`
8. `docs/API_CONTRACT.md`
9. `docs/CODE_OWNERSHIP.md`
10. `docs/DEPLOYMENT_FLOW.md`

제품·데이터·Decision Intelligence 구조를 수정할 때는 다음 문서를 함께 확인한다.

```text
현재 제품·데이터
├─ LOOFIO_TECH_ROADMAP_v1.md
├─ LOOFIO_BUSINESS_TAXONOMY_V1.md
├─ LOOFIO_DATA_SCHEMA_V1.md
└─ LOOFIO_OPPORTUNITY_ENGINE_V1.md

다음 구현
├─ LOOFIO_IMPLEMENTATION_ROADMAP_V2.md
├─ LOOFIO_IMPLEMENTATION_BACKLOG_V1.md
├─ LOOFIO_DECISION_INPUT_CONTRACT_V1.md
├─ LOOFIO_CAUSE_ANALYSIS_ENGINE_V1.md
├─ LOOFIO_CAUSE_INPUT_REQUIREMENTS_V1.md
├─ LOOFIO_STRATEGY_ENGINE_V1.md
├─ LOOFIO_CAUSE_TO_STRATEGY_MAPPING_V1.md
├─ LOOFIO_ACTION_PLAYBOOK_V1.md
├─ LOOFIO_HOSPITAL_ACTION_PLAYBOOK_CATALOG_V1.md
├─ LOOFIO_EXPERIMENT_DESIGN_V1.md
├─ LOOFIO_PLAYBOOK_EXPERIMENT_MAPPING_V1.md
├─ LOOFIO_RECOMMENDATION_PACKAGE_V2.md
├─ LOOFIO_RECOMMENDATION_QUALITY_BAR_V1.md
├─ LOOFIO_MEASUREMENT_FRAMEWORK_V1.md
├─ LOOFIO_CHANNEL_EXECUTION_V1.md
├─ LOOFIO_CHANNEL_CAPABILITY_AND_EVENT_MATRIX_V1.md
├─ LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md
└─ LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md
```

Source of Truth:

```text
현재 구현 여부
1. Migration
2. Code
3. Tests
4. CURRENT_IMPLEMENTATION_STATUS.md
5. 현재 API / Data Schema 문서

다음 구현 설계
1. 00_PLANNING_INDEX.md
2. DECISION_REGISTER_V2.md
3. IMPLEMENTATION_ROADMAP_V2.md
4. IMPLEMENTATION_BACKLOG_V1.md
5. 상세 Domain 문서
```

기획 문서가 존재한다는 이유만으로 현재 API·DB·UI의 구현 상태를 변경해서 기록하지 않는다.

---

# 2. 절대 유지해야 하는 제품 원칙

## 2.1 계산과 탐지는 deterministic backend가 수행한다

LLM이 최종 계산하거나 판정해서는 안 되는 작업:

- 매출 합계
- 증감률
- ROI
- 예약률
- 취소율
- 가동률
- 재방문 간격
- baseline
- Opportunity Score
- Cause Candidate Score의 정량 구성
- Strategy Score의 정량 구성
- Recommendation Quality Score
- 기여이익 계산
- 비용 합산
- 통계 검정
- Detector 조건 판정
- 성공·중단 조건 충족 판정
- Measurement 수치

LLM의 허용 역할:

- 구조화된 Observation 설명
- 원인 **가설**의 읽기 쉬운 표현
- Strategy·Playbook 대안 비교 설명
- 사업장별 실행 문구·직원 스크립트·콘텐츠 초안
- 제한사항과 추가 확인 질문 표현

핵심 원칙:

> 코드가 사실·수치·후보·검증을 관리하고, AI는 구조화된 결과를 설명하고 표현한다.

## 2.2 의미 계층을 섞지 않는다

다음 의미는 API·DB·UI·문서에서 분리한다.

```text
Observation
실제 데이터에서 확인된 현상

Cause Hypothesis
가능한 원인 가설. 사실이 아님

Estimate
가정이 포함된 잠재 가치·범위

Strategy Candidate
가능한 개입 방향

Recommendation Package
선택 이유·실행·경제성·실험이 포함된 계획

Actual Result
실제로 관측된 실행 결과

Measurement
baseline과 비교한 해석
```

금지 표현:

```text
원인은 X입니다.
X원을 잃고 있습니다.
이 행동으로 매출이 Y% 증가합니다.
```

근거 수준이 충분하지 않다면 다음처럼 표시한다.

```text
가능성이 있습니다.
먼저 검토할 가치가 있는 가설입니다.
다른 시간대 수준을 가정한 Estimate입니다.
현재 결과는 관찰 비교이며 인과효과가 아닙니다.
```

## 2.3 Opportunity는 해결책을 선택하지 않는다

Opportunity Engine 책임:

```text
Observation
Estimate(optional)
Evidence
Limitations
Score / Confidence
```

Opportunity Detector가 다음을 결정하면 안 된다.

- 원인 확정
- 채널 선택
- 고객 대상 선택
- 할인 여부
- 캠페인 문구
- 실행 예산
- 최종 Playbook

Opportunity 출력은 Cause Analysis 입력으로 전달한다.

## 2.4 Cause는 사실이 아니라 검증 가능한 가설이다

Cause Analysis는 다음을 포함한다.

- cause code
- hypothesis
- supporting evidence
- contradicting evidence
- missing data
- diagnostic questions
- testability
- limitations

모든 분석에서 `DATA_QUALITY_ARTIFACT` 가능성을 먼저 또는 함께 검토한다.

## 2.5 최종 Recommendation은 일반 조언이어서는 안 된다

다음 수준의 문장은 최종 Recommendation으로 승인하지 않는다.

```text
홍보를 강화하세요.
SNS를 활용하세요.
프로모션을 진행하세요.
전단지를 배포하세요.
휴면 고객에게 연락하세요.
```

완성된 Recommendation Package는 최소 다음 질문에 답해야 한다.

1. 어떤 Opportunity인가
2. 가능한 원인은 무엇인가
3. 무엇을 추가 확인해야 하는가
4. 어떤 전략을 비교했는가
5. 왜 1순위를 선택했는가
6. 정확히 누구에게 실행하는가
7. 어떤 Offering을 다루는가
8. 온라인·오프라인 중 어떤 채널을 어떤 역할로 사용하는가
9. 언제 시작하고 종료하는가
10. 예산·혜택 원가·운영 부담은 얼마인가
11. 누가 실행하는가
12. primary metric은 무엇인가
13. 어떤 비교 방법을 사용하는가
14. 성공조건은 무엇인가
15. 중단조건은 무엇인가
16. 결과를 어떤 데이터로 회수하는가

## 2.6 Recommendation Quality Bar를 통과해야 한다

최종 Recommendation 제안 기준:

```text
Quality Score >= 75
AND
Hard Fail = 0
AND
모든 Section Floor 충족
```

Quality 영역:

```text
Evidence Linkage        20
Specificity             20
Economics Integrity     20
Feasibility             15
Measurement Design      15
Alternative Comparison  10
```

Hard Fail 예:

- 대상 없음
- 실행 기간 없음
- 비용이 없고 `unknown` 표시도 없음
- measurement metric 없음
- 성공·중단조건 없음
- Opportunity Evidence와 무관함
- AI가 수치를 임의 생성
- result source 없음
- 정책·capacity 미검토
- 대안 비교 없음 또는 단일 후보 사유 없음

Quality Bar를 통과하지 못한 결과는 다음 중 하나로만 표시한다.

```text
DRAFT
NEEDS_DATA
NEEDS_POLICY_REVIEW
QUALITY_REJECTED
```

최종 실행 추천으로 노출하지 않는다.

## 2.7 대안을 비교하고 `NO_ACTION`을 허용한다

최종 추천 전 최소 2개 Strategy 후보를 비교한다.

예:

```text
RETENTION_REACTIVATION
DISCOVERABILITY / ACQUISITION
PARTNERSHIP_REFERRAL
CAPACITY_OPERATION
DATA_COLLECTION
NO_ACTION
```

후보가 하나뿐이면 이유를 기록한다.

경제성이 없거나 데이터가 부족하면 다음도 유효한 결과다.

```text
NO_ACTION
DATA_COLLECTION
CAPACITY_OPERATION
```

LOOFIO는 항상 광고·할인·메시지를 권하지 않는다.

## 2.8 Playbook은 versioned registry에서 선택한다

자유형 AI 아이디어보다 `Action Playbook`을 우선한다.

모든 Playbook은 다음을 가진다.

- version
- applicable archetype
- applicable opportunity/cause/strategy
- required data
- preconditions
- contraindications
- online/offline steps
- economics model
- experiment template
- success conditions
- stop conditions
- policy tags
- status

상태:

```text
DRAFT
VALIDATED_INTERNAL
PILOT
ACTIVE
DEPRECATED
BLOCKED
```

근거가 약한 Playbook을 `ACTIVE`로 표시하지 않는다.

## 2.9 경제성의 `unknown`을 0으로 처리하지 않는다

최소 비용 후보:

```text
media spend
message cost
benefit/discount cost
partner cost
staff time
additional service cost
```

가능한 경우:

```text
Contribution per Conversion
=
Net Revenue
- Variable Cost
- Benefit Cost
- Incremental Service Cost
```

```text
Net Contribution Estimate
=
Incremental Conversion Estimate
× Contribution per Conversion
- Media Cost
- Partner Cost
- Extra Staff Cost
```

마진·원가가 없으면 `revenue-only estimate` 또는 `unknown`으로 표시한다.
순기여이익처럼 표현하지 않는다.

## 2.10 성공·중단조건이 없는 행동은 실험이 아니다

모든 실행 계획은 최소 다음을 가진다.

- population
- treatment
- comparison
- start/end
- primary metric
- attribution window
- guardrails
- success threshold
- stop conditions
- result source
- owner
- approval

비교 설계:

```text
Randomized Holdout
Alternating Time Window
Matched Historical Window
Before/After Exploratory
Partner/Channel Split
```

Evidence Grade를 숨기지 않는다.

```text
A: 강한 비교설계
B: 합리적인 비교군/교대설계
C: 동일 요일·시간대 baseline
D: 단순 전후·수동 귀속
```

Grade C/D 결과를 Incremental Revenue로 단정하지 않는다.

## 2.11 Recommendation → Action → Result 연결을 끊지 않는다

장기 핵심 데이터:

```text
Opportunity
→ Cause
→ Strategy
→ Playbook
→ Experiment
→ Recommendation Package
→ User Decision
→ Action
→ Costs
→ Result
→ Measurement
→ Evidence Grade
```

추천 문구만 저장하는 것으로 충분하지 않다.

## 2.12 Human-in-the-loop가 기본이다

MVP에서 사용자 승인 없이 다음을 실행하지 않는다.

- 광고비 사용 또는 변경
- 고객 메시지 발송
- 외부 게시
- 쿠폰·혜택 활성화
- 고객 직접 응답
- 제휴 비용 확정
- 외부 계정 설정 변경

현재 Hospital MVP는 다음까지만 허용한다.

```text
manual action planning
copy/export
staff-operated execution
result recording
```

## 2.13 Tenant 격리는 기능이 아니라 불변조건이다

다른 tenant 또는 business의 데이터가 다음 위치에서 섞이면 안 된다.

- query
- cache
- search/RAG
- logs
- file path
- AI context
- Cause/Strategy candidate
- Playbook resolution
- Recommendation Package
- Action target
- Result/Measurement
- export

모든 데이터 접근은 명시적인 tenant/business scope를 가져야 한다.

---

# 3. 아키텍처 원칙

기본 의존 방향:

```text
UI / Apps
    ↓
API / Application
    ↓
Domain / Analytics / Decision Intelligence
    ↓
Ports / Contracts

Infrastructure / Connectors / AI Providers
    └──────────────────────────────→ Ports 구현
```

의사결정 파이프라인:

```text
Raw
→ Normalization
→ Domain
→ Metrics
→ Detectors
→ Opportunity
→ Cause Analysis
→ Strategy Comparison
→ Playbook Resolution
→ Economics / Feasibility
→ Experiment Design
→ Recommendation Package Assembly
→ Quality Validation
→ User Decision
→ Action / Channel Execution
→ Result
→ Measurement
```

반대 방향 의존을 만들지 않는다.

세부 규칙은 `docs/DEPENDENCY_RULES.md`를 따른다.

---

# 4. 데이터 모델 규칙

## 4.1 `Appointment`는 전체 제품 공통 루트가 아니다

`Appointment`는 Hospital `APPOINTMENT_SERVICE`의 첫 Domain Contract다.

다업종 확장은 Domain Adapter 방식으로 추가한다.

```text
Appointment
Sale
Membership
WorkOrder
Booking
Project
ProductionRun
...
```

공통 계층:

```text
Business
Offering
Customer
BusinessEvent
Metric
Opportunity
CauseCandidate
StrategyCandidate
Playbook
Experiment
RecommendationPackage
Action
Result
Measurement
```

## 4.2 공통 판매 대상은 `Offering`

상품·서비스·패키지·회원권 등 판매 대상을 공통 표현할 때 `Offering`을 사용한다.

## 4.3 공식 직업분류와 Business Archetype을 분리한다

KECO/KSCO 원본 taxonomy를 보존한다.

LOOFIO의 `support_level`, `archetype`, `mapping_version`은 별도 해석 계층이다.

## 4.4 개인정보 최소화

가능하면:

```text
raw identifier
→ HMAC / tokenization
→ external_customer_token
→ internal customer_id
```

Hospital Cause·Strategy·Recommendation에서 다음을 사용하지 않는다.

- 환자 이름
- 주민등록번호
- 전화번호 원문
- 진단명
- 질병·증상
- 처방
- 검사 결과
- 의무기록
- 상담 원문

## 4.5 현재 DB Source of Truth

실행 가능한 현재 스키마의 Source of Truth는 순서가 고정된 `api/migrations/*.sql`이다.

다음은 목표 설계의 additive 후보이며, migration이 생기기 전에는 존재한다고 가정하지 않는다.

```text
cause_analysis_runs
cause_candidates
strategy_runs
strategy_candidates
playbook_definitions
experiments
recommendation_packages
recommendation_quality_results
```

---

# 5. API 변경 규칙

API는 `docs/API_CONTRACT.md`를 따른다.

기존 `/api/v1`의 현재 Recommendation·Action 흐름을 즉시 제거하지 않는다.

새 Decision Intelligence API는 additive/optional 방식으로 추가한다.

Breaking change:

- 기존 필드 삭제·타입·의미 변경
- existing enum 의미 변경
- Observation/Estimate/Cause/Actual 혼합
- current `/recommendations/draft` 제거
- 현재 manual Action 상태 의미 변경
- Measurement method 의미 변경
- pagination/time/money contract 변경

전환 원칙:

```text
기존 Recommendation Draft 유지
→ 새 Recommendation Package 병렬 추가
→ UI/API 병렬 검증
→ migration/compatibility window
→ 별도 결정 후 전환
```

---

# 6. Database 변경 규칙

모든 DB 변경은 append-only migration으로 수행한다.

파괴적 변경은 expand/contract를 사용한다.

새 intelligence entity 추가 시 필수:

- tenant/business scope
- input/source reference
- version
- status
- created_at
- limitations
- actor/audit가 필요한지
- retry/idempotency
- retention
- rollback/forward-fix

과거 Opportunity·Recommendation·Measurement를 새 의미로 조용히 재해석하지 않는다.

---

# 7. AI 관련 규칙

비즈니스 코드에 provider/model명을 직접 고정하지 않는다.

```text
task_type / model_route
→ AI Gateway
→ provider adapter
```

AI 입력:

```text
Opportunity
Evidence
Limitations
Cause/Strategy/Playbook structured data
Business policy
Aggregate context
```

AI가 직접 받지 않는 입력:

```text
Raw CSV 전체
환자 PII
임상정보
비정규화 원문
다른 tenant 데이터
```

AI 출력은 다음 검증을 통과해야 한다.

1. Schema Validation
2. Evidence Fidelity
3. Playbook Compliance
4. Economics Integrity
5. Execution Completeness
6. Policy Safety
7. Recommendation Quality Bar

AI 실패 시 deterministic fallback을 유지한다.

현재 deterministic manual Recommendation은 삭제하지 않고 fallback과 baseline으로 유지한다.

---

# 8. 테스트 요구사항

## Metric / Detector

- 동일 입력 → 동일 결과
- 경계값
- 표본 부족
- 상태/timezone/money
- detector version
- score breakdown

## Ingestion / Normalization

- idempotency
- mapping
- raw PII guard
- invalid row 원자성
- source lineage
- duplicate 처리

## Cause Analysis

- Opportunity Evidence 밖의 사실 생성 금지
- `DATA_QUALITY_ARTIFACT` 검토
- cause를 사실로 단정하지 않음
- contradiction/missing data
- diagnostic question schema

## Strategy

- 최소 2개 후보 또는 단일 후보 이유
- `NO_ACTION`/`DATA_COLLECTION` 허용
- economics unknown 보존
- deterministic ranking 재현성
- policy/capacity 반영

## Playbook

- version/status
- required/precondition/contraindication
- online/offline steps
- economics/measurement template
- success/stop
- tenant-specific hardcoding 금지

## Experiment

- population/treatment/comparison
- primary metric 하나
- attribution window
- guardrails
- success/stop
- evidence grade
- 작은 표본의 과장 방지

## Recommendation Package

- Observation 숫자 불변
- evidence refs
- alternative comparison
- target/channel/time/budget/owner
- result source
- Quality Score >= 75
- Hard Fail = 0
- AI invented numeric value = 0

## Tenant / Security

- cross-tenant access 불가
- AI context 격리
- Playbook resolver scope
- export/action target 격리

## API

- existing contract backward compatibility
- new endpoint schema
- idempotency
- authorization
- version
- error code

## Measurement

- Actual/Estimate/Observed Delta/Incremental 분리
- cost unknown 보존
- displacement 확인
- Grade C/D 인과 표현 금지
- method/version 보존

---

# 9. 코드 리뷰가 반드시 필요한 변경

다음 변경은 단독으로 merge하지 않는다.

- DB migration
- tenant/auth/permission
- PII 처리
- Detector·Opportunity Score
- Cause taxonomy/score
- Cause→Strategy mapping
- Strategy Score
- Playbook 추가·상태 승격
- economics formula
- Experiment method/Evidence Grade
- Recommendation Quality Bar
- AI context/provider/prompt/schema
- 외부 채널 실행
- 광고비·메시지·제휴 자동화
- Measurement/Incrementality
- API breaking change
- Deployment/security/secrets
- `AGENTS.md`, `PROHIBITED_CHANGES.md`, `ARCHITECTURE.md`

논리적 owner는 `docs/CODE_OWNERSHIP.md`를 따른다.

---

# 10. 완료 정의

Decision Intelligence 관련 작업은 다음이 함께 완료되어야 한다.

- domain contract
- deterministic logic
- version
- persistence/migration가 필요한 경우 migration
- API contract
- validation
- golden fixtures
- regression tests
- audit/log
- UI status wording
- fallback
- rollback/disable 경로
- CURRENT_IMPLEMENTATION_STATUS 갱신

문서 작성만으로 구현 완료가 아니다.

---

# 11. 금지 변경 요약

전체 목록은 `docs/PROHIBITED_CHANGES.md`를 따른다.

특히 금지:

1. 일반 조언을 최종 유료 Recommendation으로 표시
2. Cause를 사실로 확정
3. 대안 비교 없이 1순위 선택
4. economics unknown을 0으로 처리
5. 성공·중단조건 없는 실행
6. 추적 없는 온라인·오프라인 집행
7. Quality Gate 우회
8. LLM이 수치·경제성·실험 결과 계산
9. Grade C/D를 Incremental Revenue로 표현
10. 사용자 승인 없는 외부 Action
11. tenant scope 없는 데이터 접근
12. 기존 `/api/v1` 계약을 조용히 파괴

---

# 12. 기술 결정 상태

현재 구현으로 확정:

- Backend: FastAPI / Pydantic / psycopg
- Frontend: Next.js / React / TypeScript
- Database: PostgreSQL
- Authentication: Google·Naver direct OAuth + 서버 저장 세션
- CI: GitHub Actions regression checks
- Current execution: manual Action
- Current Measurement: deterministic pre/post baseline comparison

미확정 또는 미구현:

- AI provider/model
- Cause/Strategy/Playbook persistence
- Recommendation Package API
- External Context provider
- Production cloud/hosting
- Monitoring
- Secret Manager
- Queue/cache
- Production migration runner
- External channel automation

새 선택과 기존 선택의 변경은 ADR로 기록한다.
