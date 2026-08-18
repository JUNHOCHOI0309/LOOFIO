---
title: "LOOFIO Implementation Backlog v1"
version: "1.0"
date: "2026-08-18"
status: "로컬 구현용 통합 Backlog"
base_repository: "JUNHOCHOI0309/LOOFIO"
base_branch: "main"
base_commit: "0c75e524af5e9baa896e5685103ce8afe858b5a0"
scope: "Hospital LOW_DEMAND_SLOT Decision Intelligence vertical slice"
---

# LOOFIO Implementation Backlog v1

## 1. 문서 목적

이 문서는 지금까지 분리해서 정의한 Decision Input, Cause, Strategy, Playbook, Experiment, Recommendation Package, Quality, Measurement, Channel Execution 작업을 **하나의 실행 순서와 의존관계**로 통합한다.

핵심 목표:

```text
LOW_DEMAND_SLOT Opportunity
→ Decision Context
→ Cause Analysis
→ Strategy Comparison
→ Playbook Instance
→ Experiment Draft
→ Recommendation Package
→ Quality Gate
→ 기존 Manual Action
→ Result / Measurement
```

첫 vertical slice에서는 LLM·공공데이터·실제 메시지/광고 Connector·Incrementality·다른 Opportunity·다른 Archetype을 제외한다.

## 2. 현재 기준

- 기준 `main`: `0c75e524af5e9baa896e5685103ce8afe858b5a0`
- 현재 구현: OAuth, Tenant, Hospital Appointment import, Metrics, 4개 Detector, Opportunity Score, deterministic Recommendation, Manual Action, Result, baseline Measurement, Dashboard, Regression CI
- 현재 CI 명령: `python -m pytest -q`, `npm run lint:web`, `npm run build:web`
- 현재 Source of Truth: migration → code → tests → CURRENT_IMPLEMENTATION_STATUS → API_CONTRACT

## 3. Backlog 사용 규칙

### 3.1 Priority

| Priority | 의미 |
|---|---|
| `P0` | 첫 deterministic vertical slice와 Manual Pilot에 필수 |
| `P1` | 첫 slice 직후 운영·UI·문서·현재 Measurement 연결 |
| `P2` | Persistence·고급 Measurement·Export 등 다음 단계 |
| `P3` | 실제 Connector·Kill switch·자동화 이전 Pilot |

### 3.2 Startability

| 값 | 의미 |
|---|---|
| `NOW` | 현재 상세 문서만으로 바로 시작 가능 |
| `AFTER_DEP` | 선행 Task 완료 후 시작 |
| `AFTER_DEP` | 설계 의존성은 2026-08-18 해제됨. 실제 시작은 선행 M1~M7 Task 완료 후 |
| `DEFERRED` | 첫 vertical slice 밖 |

### 3.3 완료의 최소 단위

모든 Task는 해당 범위에 맞게 다음을 충족해야 한다.

```text
contract / implementation / version
tests / tenant scope / PII validation
failure status / deterministic behavior
legacy regression / docs update
```

문서나 Pydantic schema만 존재한다고 완료가 아니다.

## 4. Canonical Task ID 정책

초기 Roadmap의 `DI-101~DI-605`는 개략 Epic ID였다. 상세 설계 문서에서 세분화한 ID를 Canonical로 사용한다.

| Retired / Alias | Canonical |
|---|---|
| `DI-101..DI-105` | `CA-001..CA-009` |
| `DI-201..DI-205` | `ST-001..ST-009` |
| `DI-301..DI-305` | `PB-001..PB-009 + PBC-001..PBC-008` |
| `DI-401..DI-405` | `EX-001..EX-010 + MF-001..MF-011` |
| `DI-501..DI-505` | `RP-001..RP-013 + RQ-001..RQ-016` |
| `DI-601..DI-605` | `UI-001..UI-007` |
| `EX-011` | `MF-005` |
| `PBC-010` | `RP-012 + CE-013` |
| `RP-015` | `UI-001..UI-007` |

`DI-001~DI-005`만 Decision Input의 Canonical ID로 유지한다.

## 5. Milestone Gate

| Milestone | 이름 | 범위 | 통과 조건 |
|---|---|---|---|
| `M1` | Contract Foundation | Decision Input·PII·공통 Fixture | D0~D4와 금지 입력이 deterministic하게 동작 |
| `M2` | Cause Preview Ready | LOW_DEMAND_SLOT Cause Analysis | Cause preview와 진단 질문·데이터 품질 Gate |
| `M3` | Strategy Preview Ready | 전략 후보·Hard Gate·대안 비교 | DATA_COLLECTION/NO_ACTION 포함 deterministic 비교 |
| `M4` | Playbook & Experiment Draft Ready | Core Playbook·Experiment Template | Playbook/Experiment preview와 Core 12 참조 무결성 |
| `M5` | Recommendation Package Preview Ready | Package·Quality Gate | 일반 조언이 실패하고 양질 Package가 READY_FOR_REVIEW |
| `M6` | Manual Pilot UI Ready | UI·Legacy Action handoff·전체 회귀 | 운영자가 Package를 검토·결정·Manual Action 생성 |
| `M7` | Measurement & Manual Execution Ready | Measurement adapter·Manual/Staff Execution | 실행 상태·결과·Grade C 측정이 연결 |
| `M8` | Persistence/API Ready | Data Schema·API 확정 후 저장 계층 | append-only migration과 versioned API |
| `M9` | Connector Pilot Ready | Approved Connector·Kill switch | 별도 승인된 1개 Provider Pilot |

## 6. 권장 구현 Batch

각 Batch는 하나의 PR 또는 검토 가능한 소규모 연속 커밋 단위로 사용한다.

| Batch | 범위 | Task | 산출물 |
|---|---|---|---|
| `B01` | Decision Contract | `DI-001..DI-005, QA-001, QA-003, QA-004` | 공통 value object와 D0~D4 |
| `B02` | Cause Pure Domain | `CA-001..CA-009` | LOW_DEMAND_SLOT Cause result |
| `B03` | Cause API & Regression | `CA-010..CA-012` | Preview endpoint와 회귀 |
| `B04` | Strategy Pure Domain | `ST-001..ST-009` | Gate·Score·대안·fallback |
| `B05` | Strategy API & Regression | `ST-010..ST-012` | Preview endpoint와 회귀 |
| `B06` | Playbook Framework & Catalog | `PB-001..PB-007, PBC-001..PBC-005, PBC-007..PBC-008` | Core Definition과 Instance |
| `B07` | Experiment Contract & Mapping | `EX-001..EX-009, EXM-001..EXM-009, PBC-006` | Core 12 Experiment Draft |
| `B08` | Playbook / Experiment Preview | `PB-008..PB-010, EX-012, EX-014..EX-015` | Resolver와 Experiment preview |
| `B09` | Package & Quality Core | `RP-001..RP-009, RQ-001..RQ-014` | Draft와 deterministic Quality |
| `B10` | End-to-end Package Preview | `RP-010..RP-013, RP-016..RP-017, RQ-015..RQ-017` | READY/NEEDS/REJECTED 결과 |
| `B11` | UI & Legacy Action Handoff | `UI-001..UI-009, QA-005..QA-008` | 운영자 검토→기존 Manual Action |
| `B12` | Current Measurement Adapter | `MF-001..MF-005, MF-008..MF-009, MF-015, MF-018..MF-020` | 기존 숫자 불변 + Grade C |
| `B13` | Manual / Staff Execution | `CE-001..CE-007, CE-009..CE-014, CE-020..CE-021` | Execution Package와 Staff Task |
| `B14` | Persistence | `EX-013, RP-014, MF-017, CE-015, DOC-003..DOC-006` | Schema/API 확정 후 migration |
| `B15` | Advanced Measurement / Connector | `MF-006..MF-014, MF-016, CE-008, CE-012, CE-016..CE-019` | P2/P3 별도 Pilot |

## 7. 첫 vertical slice의 엄격한 범위

### 포함

```text
Decision Context request/preview
LOW_DEMAND_SLOT Cause preview
Strategy preview
Static Playbook registry
Experiment Draft preview
Recommendation Package + Quality preview
기존 Recommendation/Manual Action handoff
기존 Measurement adapter
Manual / Staff-operated execution contract
```

### 제외

```text
LLM
외부 공공데이터
실제 SMS/Kakao/Ads API
자동 실행
다른 Opportunity 유형
다른 Archetype
고급 Incrementality
```

## 8. Canonical Task Register

### 8.1 Decision Input

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `DI-001` | P0 | M1 | `NOW` | DecisionField 상태·출처·신선도 계약 | 없음 | known/unknown/N/A/conflicting/stale/restricted와 provenance value object<br>unknown과 0이 구분되고 known 값은 source를 요구한다. | 상태 전이·Money·timestamp·conflict unit test |
| `DI-002` | P0 | M1 | `AFTER_DEP` | DecisionContextSnapshot 스키마 | `DI-001` | Goal·Operation·Economics·Offering·Customer·Channel·Policy·Measurement context<br>LOW_DEMAND_SLOT 첫 slice에 필요한 최소 필드와 version/hash가 존재한다. | Pydantic validation·timezone·tenant/business contract test |
| `DI-003` | P0 | M1 | `AFTER_DEP` | D0~D4 Readiness evaluator | `DI-002` | deterministic readiness level과 available/blocked capability<br>같은 입력은 같은 readiness와 missing requirement를 반환한다. | D0~D4 golden fixtures·boundary test |
| `DI-004` | P0 | M1 | `AFTER_DEP` | Missing requirement resolver | `DI-003` | 필드·이유·담당자·수집법·완료규칙·해제 기능<br>NEEDS_DATA 결과가 일반 문구가 아니라 구조화 보완 계획을 가진다. | capacity·consent·tracking·economics missing matrix test |
| `DI-005` | P0 | M1 | `NOW` | Hospital PII·정책 입력 Validator | `DI-001`, `DI-002` | 금지 환자 PII/임상정보 field rejection과 policy defaults<br>환자 이름·연락처·진단·의무기록 입력은 422 또는 domain validation error다. | PII negative fixtures·cross-tenant validation |

### 8.2 Cause Analysis

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `CA-001` | P0 | M2 | `AFTER_DEP` | Cause taxonomy registry | `DI-002` | 10개 CauseCode와 stable order·core/conditional metadata<br>LOW_DEMAND_SLOT core 6개와 조건부 후보가 versioned registry에 존재한다. | uniqueness·stable-order test |
| `CA-002` | P0 | M2 | `AFTER_DEP` | R/O/B/C 입력 요구조건 모델 | `DI-001` | Required/Optional/Blocking/Conditional field-path rule<br>누락 상태에 따른 candidate와 downstream blocker 동작이 명시적이다. | requirement state matrix unit test |
| `CA-003` | P0 | M2 | `AFTER_DEP` | DataQualityContext resolver | `DI-002`, `DI-004` | import·mapping·timezone·coverage·freshness aggregate<br>critical conflict가 사업 Cause rank를 차단하고 DATA_QUALITY_ARTIFACT를 우선한다. | timezone/status/lineage conflict fixtures |
| `CA-004` | P0 | M2 | `AFTER_DEP` | LOW_DEMAND_SLOT candidate seeder | `CA-001`, `CA-003` | core·conditional candidate set과 related Opportunity linkage<br>동일 입력에 후보 set과 order가 동일하다. | core/conditional seed fixtures |
| `CA-005` | P0 | M2 | `AFTER_DEP` | Evidence·Contradiction mapper | `CA-004`, `DI-002` | Opportunity/Decision Context source refs 매핑<br>raw import를 직접 읽지 않고 모든 reviewable 후보에 source refs가 존재한다. | evidence fidelity·no-raw-access test |
| `CA-006` | P0 | M2 | `AFTER_DEP` | Cause candidate evaluator | `CA-002`, `CA-005` | REVIEWABLE/NEEDS_DATA/DEPRIORITIZED/NOT_APPLICABLE/BLOCKED<br>Required 누락과 downstream Blocking 누락을 구분한다. | candidate status matrix |
| `CA-007` | P0 | M2 | `AFTER_DEP` | Cause Priority Score v1 | `CA-006` | 35/20/20/15/10 deterministic score와 label<br>score는 확률로 노출되지 않고 Required 누락 시 null이다. | factor clamp·weight·tie test |
| `CA-008` | P0 | M2 | `AFTER_DEP` | Diagnostic Question generator | `CA-006`, `DI-004` | field-linked question·answer type·priority·readiness effect<br>질문은 PII를 요구하지 않고 critical→capacity→policy→tracking 순으로 정렬된다. | question template·ordering test |
| `CA-009` | P0 | M2 | `AFTER_DEP` | CauseAnalysisResult 계약 | `CA-007`, `CA-008` | run status·candidate·diagnostics·strategy handoff schema<br>Cause를 사실로 단정하지 않고 source/version/limitations를 보존한다. | schema·serialization golden test |
| `CA-010` | P0 | M2 | `AFTER_DEP` | Cause preview API | `CA-009`, `DI-005` | POST opportunity cause-analyses preview<br>무저장·동일 입력 동일 결과·tenant scope·PII reject가 동작한다. | API auth/404/422/idempotent preview test |
| `CA-011` | P0 | M2 | `AFTER_DEP` | Cause regression suite | `CA-010` | LOW_DEMAND_SLOT 7개 핵심 fixture와 legacy regression<br>기존 Opportunity·Recommendation·Action·Measurement 결과가 변하지 않는다. | python -m pytest -q 전체 회귀 |
| `CA-012` | P1 | M2 | `AFTER_DEP` | Cause ADR·상태 문서 갱신 | `CA-011` | ADR 0020 후보와 CURRENT_IMPLEMENTATION_STATUS 수정<br>코드·테스트가 반영된 범위만 구현 완료로 기록한다. | 문서 링크·버전 검증 |

### 8.3 Strategy

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `ST-001` | P0 | M3 | `AFTER_DEP` | Strategy taxonomy·class registry | `CA-009` | 10개 StrategyFamily·4개 StrategyClass·readiness metadata<br>stable code/order와 DATA_COLLECTION·NO_ACTION이 존재한다. | registry uniqueness test |
| `ST-002` | P0 | M3 | `AFTER_DEP` | Cause→Strategy mapping | `ST-001`, `CA-001` | PRIMARY/SECONDARY/CONDITIONAL/INHIBITORY map<br>모든 Cause가 최소 한 전략 또는 명시적 hold/diagnostic으로 연결된다. | mapping completeness·duplicate test |
| `ST-003` | P0 | M3 | `AFTER_DEP` | Strategy candidate seeder | `ST-002` | core/conditional 후보·DATA_COLLECTION fallback·NO_ACTION comparator<br>LOW_DEMAND_SLOT에 기본 후보와 조건부 후보가 deterministic하게 생성된다. | candidate seed fixtures |
| `ST-004` | P0 | M3 | `AFTER_DEP` | Hard Gate evaluator | `ST-003`, `DI-003`, `DI-005` | data quality·capacity·policy·measurement·economics gate<br>blocked 전략은 score를 받지 않고 정확한 reason code를 가진다. | gate matrix test |
| `ST-005` | P0 | M3 | `AFTER_DEP` | Economics adapter | `DI-002` | complete/partial/unknown/N/A/infeasible와 break-even input<br>unknown을 0으로 처리하지 않고 paid 전략의 budget/cost 누락을 차단한다. | Decimal·unknown propagation test |
| `ST-006` | P0 | M3 | `AFTER_DEP` | Strategy Priority Score v1 | `ST-004`, `ST-005` | 25/20/15/15/10/10/5 score<br>eligible 실행·운영 전략에만 계산되고 점수 의미가 성공확률이 아니다. | weight·null·tie-break test |
| `ST-007` | P0 | M3 | `AFTER_DEP` | 대안 비교·선택 규칙 | `ST-006` | top vs second·NO_ACTION·저비용 대안 비교<br>65점·5점 gap 규칙과 MULTIPLE_VALID_OPTIONS가 동작한다. | selection boundary fixtures |
| `ST-008` | P0 | M3 | `AFTER_DEP` | DATA_COLLECTION·NO_ACTION fallback | `ST-004`, `DI-004` | 구조화 수집 계획과 monitoring/reopen plan<br>실행 전략이 없을 때 일반 문구가 아닌 owner·deadline·trigger를 반환한다. | fallback fixtures |
| `ST-009` | P0 | M3 | `AFTER_DEP` | Playbook handoff 계약 | `ST-007`, `ST-008` | selected/top strategies·blockers·candidate playbook IDs<br>Cause score를 Strategy score로 복사하지 않고 source refs를 보존한다. | handoff schema golden test |
| `ST-010` | P0 | M3 | `AFTER_DEP` | Strategy preview API | `ST-009`, `DI-005` | POST opportunity strategy-runs preview<br>무저장·tenant scope·PII reject·deterministic hash가 동작한다. | API contract test |
| `ST-011` | P0 | M3 | `AFTER_DEP` | Strategy regression suite | `ST-010` | data quality/capacity/retention/discoverability/economics fixtures<br>기존 Recommendation 흐름을 깨지 않는다. | python -m pytest -q |
| `ST-012` | P1 | M3 | `AFTER_DEP` | Strategy ADR·상태 문서 갱신 | `ST-011` | ADR과 CURRENT_IMPLEMENTATION_STATUS 수정<br>실제 반영된 version만 문서화한다. | 문서 link/version check |

### 8.4 Playbook Framework

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `PB-001` | P0 | M4 | `AFTER_DEP` | Definition·Applicability·Instance·Step 계약 | `ST-009` | Playbook 3계층과 step completion/failure schema<br>정의와 runtime tenant 값이 분리된다. | schema validation test |
| `PB-002` | P0 | M4 | `AFTER_DEP` | Canonical ID·version·legacy alias | `PB-001` | 설명형 playbook_id와 PB-01 alias map<br>신규 key/FK는 canonical ID만 사용하고 중복이 없다. | ID uniqueness·alias resolution test |
| `PB-003` | P0 | M4 | `AFTER_DEP` | Static registry | `PB-001`, `PB-002` | get/list/resolve/validate와 registry version<br>동일 registry version에서 조회 결과가 안정적이다. | registry query test |
| `PB-005` | P0 | M4 | `AFTER_DEP` | Applicability·contraindication Gate | `PB-003`, `ST-004` | readiness·required·precondition·contraindication·policy·tracking·economics<br>contraindication hit 시 instance 생성이 차단된다. | applicability matrix |
| `PB-006` | P0 | M4 | `AFTER_DEP` | Playbook Fit Score v1 | `PB-005`, `ST-006` | 25/20/15/15/10/10/5 fit score와 70/5 선택 규칙<br>Hard Gate 통과 후보에만 score가 계산된다. | threshold·tie fixtures |
| `PB-007` | P0 | M4 | `AFTER_DEP` | Playbook Instance builder | `PB-001`, `PB-005`, `PB-006` | target·slot·channel·steps·economics·experiment skeleton<br>PII 없이 business-specific runtime plan을 생성한다. | instance golden fixtures |
| `PB-008` | P0 | M4 | `AFTER_DEP` | Playbook resolver/instance preview API | `PB-007`, `DI-005` | strategy-run playbook preview와 instance preview<br>무저장·tenant scope·PII reject·deterministic 결과다. | API preview test |
| `PB-009` | P0 | M4 | `AFTER_DEP` | Core catalog 통합 | `PB-003`, `PBC-001`, `PBC-003`, `PBC-007`, `PBC-008` | Hospital Core 12개 registry load<br>모든 Core ID가 DRAFT로 조회되고 필수 계약을 가진다. | catalog completeness test |
| `PB-010` | P0 | M4 | `AFTER_DEP` | Playbook regression suite | `PB-008`, `PB-009` | Strategy handoff·generic advice·legacy Action 회귀<br>자동 실행이 발생하지 않고 기존 flow가 유지된다. | python -m pytest -q |
| `PB-004` | P1 | M4 | `AFTER_DEP` | Lifecycle·승격 Gate | `PB-003` | DRAFT→VALIDATED_INTERNAL→PILOT→ACTIVE·BLOCKED/DEPRECATED<br>문서 존재만으로 ACTIVE가 되지 않는다. | state transition test |

### 8.5 Playbook Catalog

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `PBC-001` | P0 | M4 | `AFTER_DEP` | Core 12 canonical registry rows | `PB-003` | 12개 정식 ID와 Strategy/Cause/Opportunity/readiness<br>정식 ID 12개가 unique하고 모두 DRAFT다. | catalog ID test |
| `PBC-003` | P0 | M4 | `AFTER_DEP` | Core 12 Definition fixtures | `PBC-001`, `PB-001` | required/precondition/contraindication/steps/economics/experiment/policy<br>각 Definition이 schema를 통과한다. | 12 definition fixture |
| `PBC-004` | P0 | M4 | `AFTER_DEP` | Definition validation fixtures | `PBC-003`, `PB-005` | 누락·잘못된 lifecycle·일반 조언 negative cases<br>불완전 Definition이 정확한 오류로 거부된다. | negative fixture |
| `PBC-005` | P0 | M4 | `AFTER_DEP` | Applicability fixtures | `PBC-003`, `PB-005` | eligible/needs-data/policy/contraindicated cases<br>사업장 Context별 적용 상태가 deterministic하다. | applicability fixture |
| `PBC-006` | P0 | M4 | `AFTER_DEP` | Experiment template reference validation | `PBC-003`, `EXM-001` | 모든 Core playbook의 template foreign reference 검증<br>누락·오타 template ID가 CI에서 실패한다. | reference integrity test |
| `PBC-007` | P0 | M4 | `AFTER_DEP` | Hospital policy tags | `PBC-001`, `DI-005` | manual approval·no clinical targeting·tracking/result policies<br>고객 접촉·비용 Playbook에 추가 태그가 적용된다. | policy tag completeness test |
| `PBC-008` | P0 | M4 | `AFTER_DEP` | Output Artifact schemas | `PBC-001`, `PB-001` | capacity/data/tracking/assignment/partner artifacts<br>각 blocking step이 검증 가능한 artifact를 참조한다. | artifact schema test |
| `PBC-002` | P1 | M4 | `AFTER_DEP` | Legacy PB-01~PB-10 alias map | `PB-002`, `PBC-001` | 과거 숫자 ID 호환 mapping<br>alias는 조회 호환에만 쓰이고 canonical key로 변환된다. | alias fixture |
| `PBC-009` | P2 | M8 | `AFTER_DEP` | Expansion Playbook index | `PBC-001` | P1/P2 상세화 대기 ID와 전제조건<br>미상세 Playbook이 Core 실행 후보로 선택되지 않는다. | registry status test |

### 8.6 Experiment

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `EX-001` | P0 | M4 | `AFTER_DEP` | ExperimentTemplate schema | `PB-001` | template ID/version·method·metric·guardrail·threshold·stop<br>Playbook과 분리된 공통 template 계약이 존재한다. | schema test |
| `EX-002` | P0 | M4 | `NOW` | Method·Evidence Grade enums | 없음 | 10개 Method와 Grade A~D·Precision 상태<br>Method별 Grade ceiling이 고정된다. | enum/ceiling test |
| `EX-003` | P0 | M4 | `AFTER_DEP` | Experiment Metric Catalog v1 | `EX-002` | count/rate/revenue/diagnostic/guardrail metric definitions<br>Primary Metric과 분자·분모·source가 versioned다. | metric registry test |
| `EX-004` | P0 | M4 | `AFTER_DEP` | ExperimentDefinition schema | `EX-001`, `EX-002`, `EX-003` | objective·population·assignment·treatment·comparison·schedule·metrics<br>실행 전 고정해야 할 필드가 모두 존재한다. | definition validation |
| `EX-006` | P0 | M4 | `AFTER_DEP` | Success Threshold·Stop Condition | `EX-004` | threshold type·guardrail·hard/soft stop schema<br>Primary success와 hard guardrail을 함께 판정할 수 있다. | threshold/stop validation |
| `EX-007` | P0 | M4 | `AFTER_DEP` | Assignment contract | `EX-004`, `DI-005` | assignment unit·stable HMAC rule·exclusion·freeze<br>raw 연락처 없이 동일 unit가 재현 가능하게 배정된다. | stable assignment·privacy test |
| `EX-008` | P0 | M4 | `AFTER_DEP` | Sample readiness·Precision rule | `EX-002`, `EX-007` | standard/exploratory/insufficient guidance<br>Grade와 Precision을 분리해 작은 표본을 INCONCLUSIVE로 처리할 수 있다. | sample boundary fixtures |
| `EX-012` | P0 | M4 | `AFTER_DEP` | Experiment preview API | `EX-004`, `EX-006`, `EX-007`, `EX-008`, `DI-005` | playbook instance experiment preview<br>무저장·tenant scope·deterministic draft다. | API contract test |
| `EX-014` | P0 | M4 | `AFTER_DEP` | Experiment fixtures·regression | `EX-012`, `EXM-008` | holdout/window/diagnostic/no-action fixtures<br>Core 12 template preview와 기존 API가 함께 통과한다. | python -m pytest -q |
| `EX-005` | P1 | M5 | `AFTER_DEP` | Experiment state machine | `EX-004` | DRAFT→APPROVED→RUNNING→COMPLETED/STOPPED/INVALIDATED<br>RUNNING 이후 immutable field 변경이 거부된다. | transition test |
| `EX-009` | P1 | M5 | `AFTER_DEP` | ExperimentResult 계약 | `EX-003`, `EX-004` | treatment/comparison outcome·cost·incident·source status<br>Actual과 Estimate를 분리해 수집한다. | result schema test |
| `EX-015` | P1 | M5 | `AFTER_DEP` | Experiment ADR·상태 문서 | `EX-014` | ADR 0023 후보와 CURRENT_IMPLEMENTATION_STATUS<br>구현된 Method만 상태 문서에 기록한다. | doc link/version test |
| `EX-010` | P2 | M7 | `AFTER_DEP` | Experiment Evaluation engine | `EX-006`, `EX-008`, `EX-009` | success/guardrail/grade/precision/decision<br>COMPLETED와 SUCCESS를 구분하고 INCONCLUSIVE/INVALIDATED를 반환한다. | evaluation fixtures |
| `EX-013` | P2 | M8 | `AFTER_DEP` | Experiment persistence implementation | `EX-005`, `EX-009`, `LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md`, `LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md` | definition/version/assignment/result/evaluation tables<br>append-only version과 tenant FK가 migration으로 구현된다. | migration·repository integration |

### 8.7 Experiment Mapping

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `EXM-001` | P0 | M4 | `AFTER_DEP` | Experiment template registry | `EX-001`, `PBC-001` | Core 12 template records<br>template ID가 unique하고 Playbook reference를 가진다. | registry test |
| `EXM-002` | P0 | M4 | `AFTER_DEP` | Playbook foreign reference validation | `EXM-001`, `PBC-001` | Playbook↔Template 참조 검사<br>누락 ID가 CI에서 실패한다. | foreign ref test |
| `EXM-003` | P0 | M4 | `AFTER_DEP` | Metric catalog reference validation | `EXM-001`, `EX-003` | Primary/secondary/guardrail metric 참조 검사<br>모든 Template가 존재하는 metric code를 사용한다. | metric ref test |
| `EXM-004` | P0 | M4 | `AFTER_DEP` | Method·Grade validation | `EXM-001`, `EX-002` | Method별 Grade ceiling 검증<br>Matched historical이 Grade A로 설정될 수 없다. | grade negative fixture |
| `EXM-005` | P0 | M4 | `AFTER_DEP` | Sample guidance mapping | `EX-008` | Playbook별 minimum unit/window guidance<br>작은 표본에서 자동으로 더 강한 Method를 선택하지 않는다. | sample mapping test |
| `EXM-006` | P0 | M4 | `AFTER_DEP` | Threshold·Stop templates | `EX-006` | Core 12 success form과 stop code<br>모든 실행형 Template에 success/stop이 존재한다. | completeness test |
| `EXM-007` | P0 | M4 | `AFTER_DEP` | Current Measurement fallback mapping | `EX-003`, `EX-002` | SAME_WINDOW_PRIOR_FOUR_WEEKS_V2 Grade C fallback<br>fallback이 Grade A/B 계산을 대체하지 않는다. | fallback mapping test |
| `EXM-008` | P0 | M4 | `AFTER_DEP` | Core 12 mapping fixtures | `EXM-002`, `EXM-003`, `EXM-004`, `EXM-005`, `EXM-006`, `EXM-007` | 12개 Template full fixtures<br>모든 Core Playbook이 정확히 하나의 기본 Template를 가진다. | fixture suite |
| `EXM-009` | P0 | M4 | `AFTER_DEP` | Mapping completeness CI | `EXM-008` | registry completeness validator<br>새 Core Playbook 추가 시 Template 누락이 CI에서 실패한다. | CI unit test |
| `EXM-010` | P1 | M5 | `AFTER_DEP` | Mapping 문서 갱신 | `EXM-009` | API/ADR/status link<br>실제 registry version과 문서 version이 일치한다. | doc check |

### 8.8 Recommendation Package

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `RP-001` | P0 | M5 | `AFTER_DEP` | Package Type·Status enum | `ST-001`, `PB-001`, `EX-004` | EXECUTION/OPERATIONAL/DIAGNOSTIC/HOLD와 lifecycle<br>Package Type별 상태 의미가 고정된다. | enum/transition test |
| `RP-002` | P0 | M5 | `AFTER_DEP` | Source Reference 계약 | `CA-009`, `ST-009`, `PB-007`, `EX-004` | upstream ID/version/hash source graph<br>Package가 원본 수치보다 source reference를 우선한다. | source integrity test |
| `RP-003` | P0 | M5 | `AFTER_DEP` | Package Draft schema | `RP-001`, `RP-002` | sources·diagnosis·alternatives·selected plan·economics·experiment·quality<br>네 Package Type을 표현할 수 있다. | schema golden test |
| `RP-004` | P0 | M5 | `AFTER_DEP` | Diagnosis assembler | `RP-003`, `CA-009` | Observation/Estimate/Cause/contradiction/missing info<br>upstream Observation을 변경하지 않고 limitation을 전파한다. | evidence fidelity fixture |
| `RP-005` | P0 | M5 | `AFTER_DEP` | Alternative assembler | `RP-003`, `ST-009` | selected vs second vs NO_ACTION comparison<br>최소 대안 비교 또는 단일 후보 사유가 존재한다. | alternative fixture |
| `RP-006` | P0 | M5 | `AFTER_DEP` | Selected Plan assembler | `RP-003`, `PB-007` | target·offering·slot·channels·steps·artifacts·owner·schedule<br>일반 조언이 아닌 완료 가능한 실행 계획을 만든다. | package-type fixture |
| `RP-007` | P0 | M5 | `AFTER_DEP` | Economics·Experiment adapter | `RP-003`, `ST-005`, `EX-004` | 경제성 상태와 experiment summary<br>Actual/Estimate/Contribution 의미가 섞이지 않는다. | economics/experiment schema test |
| `RP-008` | P0 | M5 | `AFTER_DEP` | Assumption·Limitation propagation | `RP-003`, `DI-002` | source-linked assumptions와 material limitations<br>blocking assumption이 proposed/expired면 ready 상태가 되지 않는다. | propagation test |
| `RP-009` | P0 | M5 | `AFTER_DEP` | Package status derivation | `RP-003`, `DI-004` | DRAFT/NEEDS_DATA/NEEDS_POLICY/QUALITY_REJECTED/READY<br>숨겨진 blocker 없이 deterministic status를 반환한다. | status matrix |
| `RP-010` | P0 | M5 | `AFTER_DEP` | Quality Validator integration | `RP-003`, `RQ-014` | quality result를 Package status와 연결<br>Hard Fail 또는 floor 미달 Package가 READY가 되지 않는다. | integration test |
| `RP-013` | P0 | M5 | `AFTER_DEP` | Recommendation Package preview API | `RP-004`, `RP-005`, `RP-006`, `RP-007`, `RP-008`, `RP-009`, `RP-010`, `DI-005` | end-to-end preview endpoint<br>동일 입력 동일 Package·Quality 결과, 저장/실행 없음. | API auth/tenant/PII/idempotent preview |
| `RP-016` | P0 | M5 | `AFTER_DEP` | Package fixtures·legacy regression | `RP-013`, `RP-012` | execution/operational/diagnostic/hold pass/fail fixtures<br>일반 조언·PII·estimate 혼합이 실패하고 legacy API가 통과한다. | python -m pytest -q |
| `RP-012` | P0 | M6 | `AFTER_DEP` | Legacy Recommendation adapter | `RP-010` | quality-passed Package→기존 Recommendation Draft<br>기존 Decision·Manual Action을 사용할 수 있고 expected effect는 source 없으면 null이다. | legacy schema/regression |
| `RP-011` | P1 | M6 | `AFTER_DEP` | Revision·SUPERSEDED 처리 | `RP-003`, `RP-009` | modified decision 시 새 immutable revision<br>원본 Observation과 versioned source가 덮어써지지 않는다. | revision test |
| `RP-017` | P1 | M6 | `AFTER_DEP` | Package ADR·상태 문서 | `RP-016` | ADR/current status/API links<br>실제 구현 범위만 완료 표시한다. | doc check |
| `RP-014` | P2 | M8 | `AFTER_DEP` | Package persistence implementation | `RP-011`, `LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md`, `LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md` | version/source/alternative/step/quality/decision tables<br>append-only revision과 tenant scope가 구현된다. | migration·repository test |

### 8.9 Recommendation Quality

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `RQ-001` | P0 | M5 | `AFTER_DEP` | Quality status·result schema | `RP-003` | NOT_EVALUATED/INVALID/HARD_FAILED/SCORE_FAILED/PASSED<br>Package revision별 deterministic result를 표현한다. | schema test |
| `RQ-002` | P0 | M5 | `AFTER_DEP` | Hard Fail registry | `RQ-001` | evidence·strategy·execution·economics·measurement·policy fail codes<br>Hard Fail은 점수로 상쇄되지 않는다. | registry completeness |
| `RQ-003` | P0 | M5 | `AFTER_DEP` | Warning registry | `RQ-001` | partial economics·Grade C/D·small sample 등 warnings<br>warning이 material limitation과 일치한다. | warning fixture |
| `RQ-004` | P0 | M5 | `AFTER_DEP` | Package Type별 품질 규칙 | `RQ-001`, `RP-001` | EXECUTION/OPERATIONAL/DIAGNOSTIC/HOLD 대체 계약<br>Type을 이유로 빈 Section을 허용하지 않는다. | type-specific fixtures |
| `RQ-005` | P0 | M5 | `AFTER_DEP` | Evidence Linkage scoring | `RQ-004`, `RP-002` | 20점 evidence/source/limitation/numeric integrity<br>Observation mutation과 invented number는 0점/Hard Fail이다. | evidence score test |
| `RQ-006` | P0 | M5 | `AFTER_DEP` | Specificity scoring | `RQ-004`, `RP-003` | target/scope·offering/channel·steps/owner/schedule·tracking<br>일반적인 조언은 section floor를 통과하지 못한다. | specificity fixtures |
| `RQ-007` | P0 | M5 | `AFTER_DEP` | Economics Integrity scoring | `RQ-004`, `RP-007` | status/source·budget·unknown·break-even·meaning separation<br>unknown 비용 0 처리와 incomplete net contribution을 거부한다. | economics score test |
| `RQ-008` | P0 | M5 | `AFTER_DEP` | Feasibility scoring | `RQ-004`, `PB-005` | capacity/offering·policy/consent·channel/owner·playbook<br>blocked/contraindicated Playbook은 0점과 Hard Fail이다. | feasibility fixtures |
| `RQ-009` | P0 | M5 | `AFTER_DEP` | Measurement Design scoring | `RQ-004`, `EX-004`, `EX-006` | primary/result·comparison/grade·success/stop·tracking<br>Grade 과장과 success/stop 누락을 차단한다. | measurement score test |
| `RQ-010` | P0 | M5 | `AFTER_DEP` | Alternative Comparison scoring | `RQ-004`, `RP-005` | candidate breadth·context comparison·NO_ACTION<br>단일 아이디어 즉시 추천이 floor를 통과하지 못한다. | alternative score test |
| `RQ-011` | P0 | M5 | `AFTER_DEP` | Section Floor·총점 계산 | `RQ-005`, `RQ-006`, `RQ-007`, `RQ-008`, `RQ-009`, `RQ-010` | 75점 threshold와 6개 floor<br>총점이 높아도 한 section floor 미달이면 실패한다. | threshold boundary test |
| `RQ-012` | P0 | M5 | `AFTER_DEP` | Generic advice structural validator | `RQ-006` | Type별 최소 step/owner/scope/tracking/success/stop 검사<br>문장 길이와 무관하게 구조 없는 조언을 Hard Fail 처리한다. | generic advice negative fixtures |
| `RQ-013` | P0 | M5 | `AFTER_DEP` | Policy·PII·tenant integration | `RQ-002`, `DI-005` | 정책/동의/PII/tenant hard gate<br>관리자도 Hard Fail을 override할 수 없다. | security negative test |
| `RQ-014` | P0 | M5 | `AFTER_DEP` | Deterministic quality result engine | `RQ-011`, `RQ-012`, `RQ-013`, `RQ-003` | hard fails·warnings·section scores·status<br>동일 Package revision과 validator version은 동일 결과다. | golden quality fixtures |
| `RQ-015` | P0 | M5 | `AFTER_DEP` | Package preview 품질 통합 | `RQ-014`, `RP-013` | preview response quality block<br>Quality 결과와 Package status가 일치한다. | API integration |
| `RQ-016` | P0 | M5 | `AFTER_DEP` | Quality regression suite | `RQ-014` | pass/generic/PII/consent/grade/diagnostic/hold fixtures<br>Hard Fail code distribution이 예상과 일치한다. | python -m pytest -q |
| `RQ-017` | P1 | M6 | `AFTER_DEP` | Quality ADR·상태 문서 | `RQ-016` | ADR 0022 후보와 current status<br>validator version·threshold·floor가 문서화된다. | doc check |

### 8.10 Decision UI

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `UI-001` | P1 | M6 | `AFTER_DEP` | Opportunity detail Decision Input panel | `DI-003`, `RP-013` | 필요 시 질문·readiness·missing input UI<br>거대 온보딩 대신 blocking 질문을 단계적으로 표시한다. | web component test·npm run lint:web·build:web |
| `UI-002` | P1 | M6 | `AFTER_DEP` | Cause evidence·diagnostic view | `CA-010` | Observation/Cause/contradiction/missing data 분리<br>Cause가 확정 원인처럼 보이지 않는다. | UI snapshot/accessibility |
| `UI-003` | P1 | M6 | `AFTER_DEP` | Strategy comparison view | `ST-010` | top alternatives·selection/exclusion·NO_ACTION<br>score를 성공 확률로 표시하지 않는다. | UI state fixture |
| `UI-004` | P1 | M6 | `AFTER_DEP` | Playbook·Experiment summary view | `PB-008`, `EX-012` | steps·tracking·economics·method·grade·success/stop<br>실행 준비와 blocker를 한 화면에서 확인할 수 있다. | UI integration test |
| `UI-005` | P1 | M6 | `AFTER_DEP` | Recommendation Package·Quality view | `RP-013`, `RQ-015` | Package sections·quality score/floors/hard fail<br>QUALITY_REJECTED를 최종 추천처럼 강조하지 않는다. | UI pass/fail fixture |
| `UI-006` | P1 | M6 | `AFTER_DEP` | Decision·수정·revision flow | `RP-011`, `RP-013` | approve/reject/modified/later와 reason<br>수정 시 새 revision과 Quality 재평가를 유도한다. | form/transition test |
| `UI-007` | P1 | M6 | `AFTER_DEP` | 기존 Manual Action handoff | `RP-012`, `UI-005` | Quality-passed Package에서 기존 Action 생성<br>기존 Action API와 상태 전이가 유지된다. | end-to-end manual flow |
| `UI-009` | P1 | M6 | `AFTER_DEP` | Web accessibility·typecheck·build regression | `UI-001`, `UI-002`, `UI-003`, `UI-004`, `UI-005`, `UI-006`, `UI-007` | keyboard/labels/type safety/build<br>기존 Dashboard가 깨지지 않고 lint/build가 통과한다. | npm run lint:web && npm run build:web |
| `UI-008` | P2 | M7 | `AFTER_DEP` | Result·Measurement interpretation view | `MF-016` | Actual/Delta/Grade/Precision/Economics/limitations<br>Grade C/D에서 인과 표현을 사용하지 않는다. | UI measurement fixtures |

### 8.11 Measurement

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `MF-001` | P1 | M7 | `AFTER_DEP` | Measurement 의미·Value Object | `EX-003`, `RP-003` | Actual/Estimate/Baseline/Delta/Attributed/Incremental/Net Contribution<br>서로 다른 의미를 같은 필드로 합치지 않는다. | serialization/semantic test |
| `MF-002` | P1 | M7 | `AFTER_DEP` | Measurement Method taxonomy | `EX-002` | A~D method codes와 ceiling<br>current method가 SAME_WINDOW_PRIOR_FOUR_WEEKS_V2로 등록된다. | method registry test |
| `MF-003` | P1 | M7 | `AFTER_DEP` | Measurement Metric Catalog v1 | `EX-003` | count/rate/revenue/economics/operational/guardrail metrics<br>metric version과 source·denominator가 고정된다. | catalog test |
| `MF-004` | P1 | M7 | `AFTER_DEP` | MeasurementDefinition schema | `EX-004`, `MF-001`, `MF-002`, `MF-003` | method·metric·window·comparison·attribution·cost<br>계산 입력과 version을 재현할 수 있다. | schema test |
| `MF-005` | P1 | M7 | `AFTER_DEP` | 현재 Measurement adapter | `MF-004`, `EXM-007`, `EXISTING_MEASUREMENT` | same-window 결과를 framework output으로 감싸기<br>기존 숫자·3개 limitation·API 의미가 변하지 않고 Grade C를 부여한다. | existing measurement golden regression |
| `MF-008` | P1 | M7 | `AFTER_DEP` | Evidence Grade·Precision evaluator | `EX-002`, `EX-008` | method grade와 UNKNOWN/INSUFFICIENT/LOW/MODERATE/HIGH<br>Grade와 Precision이 독립적으로 계산된다. | precision fixtures |
| `MF-009` | P1 | M7 | `AFTER_DEP` | Result Source 품질 | `EX-009` | VERIFIED/PARTIAL/MISSING/CONFLICTING/STALE/UNVERIFIED<br>Primary source missing/conflicting이면 INCONCLUSIVE/INVALIDATED다. | source quality matrix |
| `MF-015` | P1 | M7 | `AFTER_DEP` | Measurement Output contract | `MF-005`, `MF-008`, `MF-009` | framework output schema<br>current adapter와 future treatment/control을 같은 의미 계층으로 표현한다. | schema test |
| `MF-018` | P1 | M7 | `AFTER_DEP` | User-facing wording rules | `MF-015` | Grade별 허용 문구와 actual/estimate labels<br>Grade C/D에서 'LOOFIO가 만든 매출'을 표시하지 않는다. | wording fixtures |
| `MF-019` | P1 | M7 | `AFTER_DEP` | Measurement fixtures·regression | `MF-005`, `MF-015`, `MF-018` | current adapter·positive/negative delta·missing payment<br>기존 API와 숫자가 유지된다. | python -m pytest -q |
| `MF-020` | P1 | M7 | `AFTER_DEP` | Measurement ADR·상태 문서 | `MF-019` | ADR/current status/API docs<br>실제 구현 Method만 완료 표시한다. | doc check |
| `MF-006` | P2 | M7 | `AFTER_DEP` | Treatment/Control calculator | `EX-007`, `EX-009`, `MF-003` | rate/count 차이와 incremental outcome candidate<br>sample/denominator·contamination 정보를 함께 반환한다. | randomized fixtures |
| `MF-007` | P2 | M7 | `AFTER_DEP` | Historical baseline calculator | `MF-002`, `MF-003` | matched historical·prior-four-weeks baseline<br>baseline=0·window 부족·scope mismatch를 안전 처리한다. | historical boundary tests |
| `MF-010` | P2 | M7 | `AFTER_DEP` | Cost capture contract | `DI-002` | planned/actual·cost type·status·source<br>unknown 비용이 0으로 저장되지 않는다. | cost schema test |
| `MF-011` | P2 | M7 | `AFTER_DEP` | Economics calculator | `MF-006`, `MF-010` | contribution·incremental revenue·net contribution·break-even<br>complete cost에서만 net contribution을 계산한다. | Decimal/economics fixtures |
| `MF-012` | P2 | M7 | `AFTER_DEP` | Contamination·Displacement evaluator | `EX-007`, `MF-006` | assignment contamination·other slot/offering/business total<br>목표 슬롯 이동을 신규 성과로 중복 계산하지 않는다. | displacement fixtures |
| `MF-013` | P2 | M7 | `AFTER_DEP` | Guardrail evaluator | `EX-006`, `MF-009` | PASSED/BREACHED/UNKNOWN/N/A<br>Hard Guardrail breach 시 success candidate가 불가하다. | guardrail test |
| `MF-014` | P2 | M7 | `AFTER_DEP` | Measurement decision engine | `MF-006`, `MF-007`, `MF-008`, `MF-009`, `MF-011`, `MF-012`, `MF-013` | success/no-effect/harmful/inconclusive/invalidated 등<br>데이터 실패와 명확한 무효 결과를 구분한다. | decision golden fixtures |
| `MF-016` | P2 | M7 | `AFTER_DEP` | Measurement preview API | `MF-015`, `MF-014`, `DI-005` | experiment measurement preview<br>재계산이 기존 결과를 덮어쓰지 않는다. | API test |
| `MF-017` | P2 | M8 | `AFTER_DEP` | Measurement persistence implementation | `MF-015`, `LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md`, `LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md` | definition/run/metrics/cost/evaluation/outcome tables<br>새 Run append-only와 tenant scope가 구현된다. | migration/repository |

### 8.12 Channel Execution

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `CE-001` | P1 | M7 | `AFTER_DEP` | Execution mode·channel·role enums | `EXISTING_ACTION` | MANUAL/COPY_EXPORT/STAFF_OPERATED/APPROVED_CONNECTOR/BOUNDED_AUTOMATION<br>현재 허용·미구현·금지 수준을 구분한다. | enum/capability test |
| `CE-002` | P1 | M7 | `AFTER_DEP` | ExecutionPackage schema | `RP-003`, `RP-012`, `CE-001` | target·asset·tracking·budget·approval·retry·result contract<br>Action과 채널 실행 계약이 분리된다. | schema test |
| `CE-003` | P1 | M7 | `AFTER_DEP` | Execution state machine | `CE-002` | DRAFT~COMPLETED/FAILED/CANCELLED/BLOCKED/EXPIRED<br>부분 완료와 unknown 상태를 표현하고 기존 Action 상태와 매핑한다. | transition test |
| `CE-004` | P1 | M7 | `AFTER_DEP` | Approval scope hash·expiry | `CE-002` | target/asset/channel/schedule/budget/tracking hash<br>승인 후 scope 변경 시 재승인을 요구한다. | hash/reapproval test |
| `CE-005` | P1 | M7 | `AFTER_DEP` | Target·Privacy contract | `CE-002`, `DI-005` | aggregate/tokenized/external-managed target<br>Package·UI에 환자 PII가 없고 frozen target을 임의 확대하지 않는다. | privacy fixtures |
| `CE-006` | P1 | M7 | `AFTER_DEP` | Execution Asset contract | `CE-002` | message/script/link/QR/partner card/checklist/config assets<br>미승인·expired asset을 실행할 수 없다. | asset state test |
| `CE-007` | P1 | M7 | `AFTER_DEP` | Tracking contract | `CE-002`, `EX-004` | action/source/UTM/QR/partner/provider IDs와 test event<br>Tracking 미검증 Package는 실행 준비 상태가 아니다. | tracking test |
| `CE-009` | P1 | M7 | `AFTER_DEP` | Idempotency contract | `CE-002` | logical key·request hash·provider/internal dedupe<br>same key same payload replay, different payload conflict다. | idempotency test |
| `CE-010` | P1 | M7 | `AFTER_DEP` | Attempt·Event schema | `CE-003`, `CE-009` | attempt status와 append-only execution events<br>occurred/recorded time·source·dedupe·provider ref를 보존한다. | event schema/state test |
| `CE-011` | P1 | M7 | `AFTER_DEP` | Staff-operated Task schema | `CE-003`, `CE-005` | front desk/capacity/data audit task<br>담당·기한·결과 code·retry/skip reason을 기록한다. | task workflow fixture |
| `CE-013` | P1 | M7 | `AFTER_DEP` | 현재 Manual Action adapter | `CE-002`, `EXISTING_ACTION` | manual-action-v1을 mode=MANUAL package로 해석<br>기존 API·상태·idempotency가 유지된다. | legacy action regression |
| `CE-014` | P1 | M7 | `AFTER_DEP` | Execution Package preview API | `CE-004`, `CE-005`, `CE-006`, `CE-007`, `CE-009`, `CE-010`, `CE-011`, `CE-013`, `DI-005` | Action execution package preview<br>무저장·tenant scope·PII reject·동일 입력 동일 결과다. | API preview test |
| `CE-020` | P1 | M7 | `AFTER_DEP` | Execution fixtures·regression | `CE-014`, `CE-013` | manual/staff/idempotency/cancel/privacy fixtures<br>현재 Action/Result/Measurement 회귀가 통과한다. | python -m pytest -q |
| `CE-021` | P1 | M7 | `AFTER_DEP` | Execution ADR·상태 문서 | `CE-020` | ADR/current status/API docs<br>현재 허용 mode만 구현 완료로 표시한다. | doc check |
| `CE-008` | P2 | M7 | `AFTER_DEP` | Budget·Cost contract | `CE-002`, `MF-010` | planned/reserved/spent/remaining과 hard cap<br>비용-bearing 실행이 cap을 초과할 수 없다. | budget boundary test |
| `CE-012` | P2 | M7 | `AFTER_DEP` | Outcome linkage | `CE-007`, `CE-010`, `MF-009` | execution event→booking/completion/spend/guardrail link<br>attributed와 incremental을 구분한다. | linkage fixtures |
| `CE-015` | P2 | M8 | `AFTER_DEP` | Execution persistence implementation | `CE-014`, `LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md`, `LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md` | package/version/attempt/event/task/tracking/budget/outcome tables<br>append-only event와 tenant scope가 migration으로 구현된다. | migration/repository |
| `CE-018` | P2 | M8 | `AFTER_DEP` | PII 없는 Export·Audit | `CE-005`, `CE-006`, `DI-005` | minimal export·checksum·expiry·download audit<br>직접 연락처 export는 기본 차단되고 만료 후 삭제 정책이 있다. | export security test |
| `CE-016` | P3 | M9 | `DEFERRED` | Provider-neutral Connector Port | `CE-009`, `CE-010` | validate/preview/execute/status/cancel/cost/events<br>Core decision logic이 Provider SDK에 의존하지 않는다. | fake connector contract test |
| `CE-017` | P3 | M9 | `DEFERRED` | Channel capability contract | `CE-016` | provider별 preview/idempotency/cancel/event/test support<br>지원하지 않는 capability를 런타임에 차단한다. | capability fixture |
| `CE-019` | P3 | M9 | `DEFERRED` | Cancel·Pause·Kill switch | `CE-003`, `CE-016` | global/tenant/business/channel/package stop<br>미래 실행을 차단하고 이미 전달된 결과를 삭제하지 않는다. | cancel/kill fixtures |

### 8.13 Cross-cutting QA

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `QA-001` | P0 | M1 | `AFTER_DEP` | Golden fixture library | `DI-002` | LOW_DEMAND_SLOT canonical Context·Opportunity·Package fixtures<br>모듈별 fixture가 동일 source IDs/version을 재사용한다. | fixture checksum test |
| `QA-003` | P0 | M1 | `NOW` | Tenant isolation matrix | `DI-002` | 모든 preview·store·export cross-tenant negative test<br>다른 tenant의 존재·데이터가 노출되지 않는다. | 404/403 isolation fixtures |
| `QA-004` | P0 | M1 | `AFTER_DEP` | Hospital PII negative corpus | `DI-005` | 이름·전화·이메일·주민번호·진단·의무기록 corpus<br>모든 계약·API·export가 금지 필드를 거부한다. | parameterized negative tests |
| `QA-002` | P0 | M5 | `AFTER_DEP` | Determinism regression | `CA-009`, `ST-009`, `PB-007`, `EX-004`, `RP-003`, `RQ-014` | same input same output/hash suite<br>순서·score·status·Package가 반복 실행에서 동일하다. | repeat-run golden test |
| `QA-005` | P0 | M6 | `AFTER_DEP` | Legacy API regression | `RP-012`, `CE-013`, `MF-005` | 기존 Recommendation/Action/Result/Measurement 계약<br>기존 endpoints와 숫자·상태 의미가 유지된다. | python -m pytest -q |
| `QA-006` | P0 | M6 | `AFTER_DEP` | Backend·Web CI Gate 유지 | `UI-009`, `QA-005` | pytest·web lint·web build<br>현재 GitHub Actions regression 명령이 모두 통과한다. | python -m pytest -q; npm run lint:web; npm run build:web |
| `QA-007` | P1 | M6 | `AFTER_DEP` | Recommendation semantic wording tests | `RQ-012`, `MF-018` | Cause fact·success probability·Grade C causal wording 금지<br>금지 문구 fixture가 validator/UI에서 실패한다. | wording snapshot tests |
| `QA-008` | P1 | M6 | `AFTER_DEP` | Hospital CSV variation sample pack 확장 | `QA-001` | 정상·열변형·상태·timezone·sparse payment·duplicate·PII samples<br>import idempotency와 Decision Input readiness 변화가 검증된다. | sample-pack regressions |

### 8.14 Documentation

| ID | P | M | 시작 | 작업 | 의존성 | 산출물 / Acceptance | 테스트 |
|---|:---:|:---:|---|---|---|---|---|
| `DOC-001` | P1 | M6 | `AFTER_DEP` | Decision Intelligence ADR 세트 | `CA-012`, `ST-012`, `RQ-017`, `EX-015` | ADR 0020~0023 후보<br>계층·Playbook·Quality·Experiment 결정을 append-only 기록한다. | ADR link check |
| `DOC-002` | P1 | M6 | `AFTER_DEP` | CURRENT_IMPLEMENTATION_STATUS 갱신 규칙 | `QA-006` | code baseline/document alignment commit 분리<br>기획만 있는 기능을 구현 완료로 표시하지 않는다. | status consistency check |
| `DOC-005` | P1 | M6 | `AFTER_DEP` | Planning Index·Decision Register 링크 | `PLANNING_INDEX`, `DECISION_REGISTER` | 문서 읽기 순서와 확정/미결정 연결<br>모든 상세 설계가 인덱스에서 접근 가능하다. | broken link check |
| `DOC-003` | P2 | M8 | `AFTER_DEP` | API Contract 반영 | `LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md` | 새 preview/persistence endpoint를 현재 API 문서와 정렬<br>현재 /api/v1 의미와 legacy endpoint를 깨지 않는다. | OpenAPI/contract diff |
| `DOC-004` | P2 | M8 | `AFTER_DEP` | Data Schema 반영 | `LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md` | Decision Intelligence migration source-of-truth 연결<br>제안 테이블과 실제 migration을 구분한다. | migration index check |
| `DOC-006` | P2 | M8 | `AFTER_DEP` | 최종 구현 문서 freeze checklist | `DOC-001`, `DOC-002`, `DOC-003`, `DOC-004`, `DOC-005` | version/status/source-of-truth 검토<br>로컬 구현 시작 시 충돌·중복 ID가 없다. | manifest validation |

## 9. Epic별 Acceptance Gate

### Decision Input

- 같은 입력은 같은 D0~D4를 반환한다.
- `unknown`, `0`, `not_applicable`, `conflicting`, `stale`, `restricted`를 구분한다.
- Capacity·Consent·Tracking·Result Source·Economics 누락은 downstream 기능을 정확히 차단한다.
- Hospital PII·임상정보는 contract 단계에서 거부한다.

### Cause Analysis

- Core Cause 6개와 조건부 Cause가 stable order로 생성된다.
- Cause는 사실이나 확률로 표시되지 않는다.
- Required·Optional·Blocking 입력과 Evidence·Contradiction이 연결된다.
- Critical Data Quality 문제는 사업 Cause rank보다 우선한다.

### Strategy

- Hard Gate가 Score보다 먼저 적용된다.
- 최소 2개 후보 또는 단일 후보의 구조화된 사유가 존재한다.
- `DATA_COLLECTION`, `NO_ACTION`, `CAPACITY_OPERATION`이 정상 결과다.
- 유료 전략은 예산·경제성·Tracking·정책이 없으면 선택되지 않는다.

### Playbook / Experiment

- Definition·Applicability·Instance가 분리된다.
- Core 12 Playbook은 canonical ID, DRAFT lifecycle, policy tags, Tracking, success/stop을 가진다.
- Experiment Primary Metric은 하나이고 실행 후 핵심 계약을 바꾸지 않는다.
- Grade와 Precision을 분리하며 current Measurement는 Grade C/D fallback이다.

### Recommendation Package / Quality

- Source ID/version/hash를 보존하고 upstream 수치를 변경하지 않는다.
- Target·Offering·Slot·Owner·기간·Tracking·Result Source·Success·Stop이 Type에 맞게 존재한다.
- `Total >= 75`, Hard Fail 0, 모든 Section Floor 통과가 필요하다.
- 일반 조언·PII·정책 위반·unknown=0·Grade 과장은 Hard Fail이다.

### Measurement / Execution

- Actual·Estimate·Delta·Attributed·Incremental·Net Contribution을 분리한다.
- 현재 Measurement 숫자와 API는 adapter 전후에 동일하다.
- Action과 Execution Package/Attempt/Event를 분리한다.
- Manual·Staff 실행부터 시작하고 Connector·Automation은 별도 Pilot로 유지한다.

## 10. Release Gate 체크리스트

### M5 Package Preview Gate

```text
[ ] 동일 입력 동일 Package/Quality
[ ] 입력 부족 → 정확한 NEEDS_DATA
[ ] 정책 미완료 → NEEDS_POLICY_REVIEW
[ ] 경제성 불가 → NO_ACTION 또는 저비용 전략
[ ] 일반 조언 → QUALITY_REJECTED
[ ] Cross-tenant 접근 불가
[ ] Patient PII 없음
[ ] 기존 Recommendation API 회귀 없음
```

### M6 Manual Pilot UI Gate

```text
[ ] 운영자가 Cause·대안·Playbook·Experiment를 검토 가능
[ ] 수정 시 새 revision과 재검증
[ ] Quality-passed Package만 기존 Manual Action으로 handoff
[ ] python -m pytest -q
[ ] npm run lint:web
[ ] npm run build:web
```

### M7 Measurement / Manual Execution Gate

```text
[ ] 기존 same-window-prior-four-weeks-v2 숫자 불변
[ ] Evidence Grade C와 Precision 표시
[ ] Manual/Staff Execution Package 상태 추적
[ ] Tracking·Result Source 확인
[ ] Actual Spend와 unknown 비용 구분
[ ] Action→Result→Measurement 연결
```

## 11. Branch / Commit 권장

현재 저장소의 CI가 `main`, `feature/**`, `fix/**`, `test/**`, `ci/**`를 검사하므로 로컬 구현 시 다음 형식을 권장한다.

```text
feature/decision-input-contract
feature/cause-analysis
feature/strategy-engine
feature/playbook-experiment
feature/recommendation-package
feature/decision-ui
feature/measurement-adapter
feature/manual-execution-package
```

커밋은 Task ID를 포함한다.

```text
feat(decisioning): add DecisionField states [DI-001]
feat(cause): seed low-demand causes [CA-004]
test(quality): reject generic advice [RQ-012]
```

## 12. Backlog 운영 규칙

- Task 완료 전 선행 의존성을 우회하지 않는다.
- API/Persistence 설계 문서는 완료됐다. 실제 Persistence Task는 선행 Preview·Manual Pilot Gate를 우회하지 않는다.
- Task 범위가 바뀌면 기존 ID 의미를 바꾸기보다 새 Task 또는 ADR을 만든다.
- `CURRENT_IMPLEMENTATION_STATUS.md`는 코드·migration·test 완료 후에만 갱신한다.
- LLM은 M5 deterministic Package가 안정된 뒤 별도 Epic으로 추가한다.
- External Context·다른 Opportunity·다른 Archetype은 첫 slice 밖이다.

## 13. 문서 계약 완료와 구현 시작

다음 문서 계약은 모두 완료됐다.

```text
00_PLANNING_INDEX.md
DECISION_REGISTER_V2.md
LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md
LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md
```

따라서 문서 의존성은 해제됐다. 로컬 구현은 `B01 — Decision Contract`부터 시작한다.

Persistence Task는 문서 완료만으로 시작하지 않고 다음 조건을 요구한다.

```text
M1~M7 선행 Task
Preview 회귀
Manual Action 호환
Migration preflight
```

## 14. Validation Summary

- Canonical tasks: **169개**
- Missing dependency references: **0개**
- Cycle nodes: **0개**
- Alias/retired ranges: **9개**
