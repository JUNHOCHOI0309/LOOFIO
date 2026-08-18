# LOOFIO 현재 구현 상태

- 기준일: 2026-08-18
- 기준 브랜치: `main`
- `code_baseline_commit`: `76fa387cfd2c80fbb06327fcd2dd34ff9d71dd2f`
- `source_document_alignment_commit`: `0c75e524af5e9baa896e5685103ce8afe858b5a0`
- `document_alignment_commit`: `0adeaae5866f37afb679336d20c28c3cfb2e5e17`
- 문서 패키지: `decision-intelligence-docs-v1`
- 제품 범위: Hospital Appointment MVP

이 문서는 기획 문서와 실제 코드 사이의 현재 상태를 연결하는 단일 기준이다.

```text
migration / code / test
→ 현재 구현 사실

Decision Intelligence 상세 문서
→ 목표 설계

문서 존재
!=
구현 완료
```

전체 문서 읽기 순서와 상태 분류는 `00_PLANNING_INDEX.md`, 확정·임시·미결정 사항은 `DECISION_REGISTER_V2.md`를 따른다.

---

## 1. 현재 동작하는 제품 루프

```text
Google/Naver OAuth 로그인
→ Tenant·병원 생성
→ 병원별 CSV 열·상태 매핑
→ Appointment 정규화·저장
→ Metric 계산
→ 4개 Detector 실행
→ Opportunity 저장·점수화
→ deterministic Recommendation 초안·사용자 결정
→ Manual Action 계획·상태 변경
→ Result 기록
→ 직전 동일 기간 Baseline과 Measurement 비교
→ Dashboard 이력 확인
```

현재 외부 메시지·광고·쿠폰·게시 채널은 호출하지 않는다.

현재 Measurement의 변화량은 단순 관찰 비교다.

```text
Observed Delta
!=
인과효과
!=
Incremental Revenue
!=
ROI
```

---

## 2. 기능별 현재 구현

| 영역 | 상태 | 현재 구현 |
|---|---|---|
| 인증 | 구현 | Google·Naver Authorization Code Flow, provider subject 매핑 |
| 로그인 유지 | 구현 | PostgreSQL 서버 세션, 서명된 opaque session cookie, 만료·철회 |
| Tenant/권한 | 구현 | `owner`, `admin`, `marketer`, `viewer`, active tenant 전환, query scope |
| 병원 사업장 | 구현 | Tenant 하위 Business·Location 생성 및 조회 |
| 데이터 입력 | 구현 | CSV inspect → preview → import, 열 매핑, 외부 상태 매핑, 매핑 재사용 |
| 정규화 | 구현 | `Hospital Appointment v1`, 상태 5종, 금액·시간 파싱, 오류 행 반환 |
| 데이터 안전 | 구현 | import idempotency, source lineage, 가명 customer token, 원문 PII guard |
| Metric Engine | 구현 | 예약·완료·취소·노쇼·실제 완료 매출, 요일×2시간 슬롯 집계 |
| LowDemandSlot | 구현 | 최소 관측 주와 상대 Demand Index 기반 Detector |
| RevenueGap | 구현 | 같은 요일 비교 시간대 결제 표본 기반 금액 Estimate v2 |
| CancellationHotspot | 구현 | 슬롯×Offering 예약 이탈률과 사업장 기준 비교 |
| DormantCustomer | 구현 | 명시적 기준일과 재방문 간격 기반 지연 Observation |
| ServiceDemandGap | 구현 | Offering 전체 비중과 슬롯 비중 비교 |
| Opportunity | 구현 | Detector version·evidence·limitations·Observation/Estimate 분리 저장 |
| Opportunity Score | 구현 | `opportunity-score-v1`, 35/30/20/15 구성요소·버전 저장 및 UI 표시 |
| Recommendation | 부분 구현 | 유형별 deterministic 수동 검토 초안과 결정 이력. LLM 호출 없음 |
| Action | 구현 | 승인된 Recommendation의 manual 계획, 단방향 상태 전이와 감사 이력 |
| Result | 구현 | 완료 Action의 실행 요약·측정 기간·실제 지출 기록 |
| Measurement | MVP 구현 | `same-window-prior-four-weeks-v2`, 직전 1~4주 동일 길이 창 평균과 signed delta |
| Dashboard | 구현 | Metric·Detector·Opportunity·Score·Recommendation·Action·Result·Measurement 표시 |
| Decision Input Contract | B01 구현 | immutable `DecisionField`, provenance·freshness, Decimal Money, LOW_DEMAND_SLOT `DecisionContextSnapshot`, D0~D4 Readiness, Missing Requirement, Hospital PII·tenant scope 검증 |
| Cause Analysis | B03 Preview API 구현 | B02 순수 Domain + server-scoped LOW_DEMAND_SLOT preview, deterministic input hash/preview ID, editor role·tenant/business scope, PII reject, no persistence |
| 회귀 검증 | 구현 | backend 99 tests, sample-pack 제품 루프, Cause HTTP 회귀, web typecheck/build |
| CI | 구현 | GitHub Actions `Regression checks`, `feature/fix/test/ci`와 `main` push 검사 |

---

## 3. Detector와 Opportunity 계약

| Opportunity type | Detector version | Estimate | 현재 Recommendation |
|---|---|---|---|
| `LOW_DEMAND_SLOT` | `low-demand-revenue-gap-v2` | 결제 표본 충족 시 RevenueGap | `manual_time_slot_offer_test` |
| `CANCELLATION_HOTSPOT` | `cancellation-hotspot-v1` | 없음 | `manual_cancellation_flow_review` |
| `DORMANT_CUSTOMER` | `dormant-customer-v1` | 없음 | `manual_revisit_cohort_review` |
| `SERVICE_DEMAND_GAP` | `service-demand-gap-v1` | 없음 | `manual_offering_slot_review` |

모든 유형은 `opportunity-score-v1`으로 검토 우선순위를 계산한다.

```text
Opportunity Score
!=
성공 확률
!=
예상 매출
!=
Action 효과
```

---

## 4. 현재 데이터와 표본

프로젝트 표본은 `sample-data/appointments`에 보관한다.

- `loofio_appointment_sample_hospital_v1.csv`
- `hospital_revenue_gap_positive_v1.csv`
- `hospital_revenue_gap_sparse_payment_v1.csv`
- `hospital_operational_mix_v1.csv`

현재 회귀 테스트는 CSV parsing부터 Detector, Opportunity, Recommendation, Action, Result, Measurement까지 연결한다.

---

## 5. 현재 코드 위치

| 역할 | 실제 위치 |
|---|---|
| 웹 UI | `apps/web/app` |
| API routes | `api/app/api/routes` |
| OAuth·세션 | `api/app/auth` |
| CSV import·normalization | `api/app/imports` |
| Metrics | `api/app/metrics` |
| Detectors | `api/app/analytics/detectors` |
| Scoring | `api/app/analytics/scoring` |
| Opportunity | `api/app/opportunities` |
| Recommendation | `api/app/recommendations` |
| Action | `api/app/actions` |
| Result·Measurement | `api/app/results` |
| API schemas | `api/app/schemas` |
| Decision Input Domain | `api/app/decisioning` |
| Cause Analysis Domain | `api/app/decisioning/causes` |
| PostgreSQL migration | `api/migrations` |
| 회귀 테스트 | `api/tests` |

---

## 6. Decision Intelligence 문서·구현 상태

Decision Intelligence 설계 문서는 완료됐다. 아래 구현 상태는 실제 code·test·migration 유무를 별도로 표시한다.

| 영역 | 문서 상태 | 구현 상태 |
|---|---|---|
| Planning / Decision | Planning Index, Decision Register, Roadmap, Backlog 완료 | 미구현 |
| Decision Input | D0~D4, 상태·출처·신선도 계약 완료 | B01 순수 Domain 구현·21개 전용 테스트, API/persistence 미구현 |
| Cause Analysis | Cause taxonomy·Evidence·Diagnostic·Score 설계 완료 | B03 Preview API·무저장 HTTP 회귀 구현·12개 전용/HTTP 테스트, persistence·Diagnostic Answer 저장 미구현 |
| Strategy | Hard Gate·대안 비교·DATA_COLLECTION·NO_ACTION 설계 완료 | 미구현 |
| Playbook | Definition·Applicability·Instance, Hospital Core 12개 설계 완료 | 미구현 |
| Experiment | Method·Grade·Precision·Success·Stop 계약 완료 | 미구현 |
| Recommendation Package | Package Type·Revision·Legacy Adapter 설계 완료 | 미구현 |
| Recommendation Quality | 75점·Section Floor·Hard Fail v1 설계 완료 | 미구현 |
| Measurement Framework | Actual·Estimate·Delta·Incremental·Economics 의미 분리 설계 완료 | 미구현 |
| Channel Execution | Manual·Copy·Staff·Connector 수준과 Event 계약 완료 | 미구현 |
| DI Data Schema | `0012~0020` additive proposal 완료 | migration 미작성 |
| DI API Contract | Preview-first·Persistence·Execution API proposal 완료 | Cause Preview endpoint 1개 구현, 나머지 미구현 |
| ADR | `0020~0025` Decision Intelligence 목표 결정 기록 완료 | Cause Preview 구현 경계는 ADR 0026으로 기록 |

---

## 7. 아직 구현하지 않은 범위

- Decision Context Preview API·Cause Diagnostic Answer 저장·사용자 입력 UI·persistence
- Strategy Engine, Hard Gate, Strategy Score
- Versioned Playbook Registry Runtime과 Instance
- Experiment Definition·Assignment·Evaluation
- Recommendation Package v2와 Quality Validator
- Decision Intelligence Preview API
- Decision Intelligence `0012~0020` migration
- Package 기반 UI와 기존 Manual Action Adapter
- Measurement Framework Adapter·Treatment/Comparison 계산
- Structured Manual/Staff Execution Package
- 실제 AI Gateway, provider adapter, LLM 설명·콘텐츠
- Excel import와 예약/POS API connector
- 날씨·공휴일·상권·지역 행사 등 External Context
- 고객 메시지, 광고, 쿠폰, 게시 등 외부 채널 실행
- 자동 실행·예산 통제·queue·kill switch
- 인과 추론, Production Grade Incrementality, ROI
- Appointment 외 다른 Archetype adapter
- Staging/Production 배포와 운영 monitoring

---

## 8. 다음 구현 우선순위

실제 로컬 구현은 `LOOFIO_IMPLEMENTATION_BACKLOG_V1.md`를 따른다.

```text
B01 Decision Contract 완료
→ DI-001~DI-005
→ QA-001 / QA-003 / QA-004의 Domain 범위

B02 Cause Pure Domain 완료
→ CA-001~CA-009

B03 Cause Preview / Regression 완료
→ CA-010~CA-012

B04 Strategy Pure Domain
→ ST-001~ST-009

B05 Strategy Preview / Regression
→ ST-010~ST-012

B06~B10 Playbook / Experiment / Package / Quality Preview

B11 UI / 기존 Manual Action Handoff

B12~B13 Current Measurement Adapter / Manual·Staff Execution

M8 Persistence
→ migration preflight
→ 0012~0020 단계 적용
```

AI는 deterministic Package와 Quality Preview가 안정된 뒤 별도 Epic으로 연결한다.

### B01 구현 경계

구현:

```text
DecisionField known/unknown/not_applicable/conflicting/stale/restricted
known provenance·offset timestamp
Money Decimal/KRW validation
LOW_DEMAND_SLOT 최소 DecisionContextSnapshot
canonical SHA-256 snapshot hash
safe Hospital policy defaults
D0~D4 deterministic Readiness
구조화 Missing Requirement plan
cross-tenant/business scope guard와 provenance validation
Hospital PII·임상 필드 rejection
LOW_DEMAND_SLOT Context·Opportunity·Package reference golden fixtures
```

의도적으로 제외:

```text
API endpoint
database migration/persistence
Cause/Strategy/Playbook/Experiment/Package runtime
LLM 또는 외부 channel
```

B01 코드 기준 커밋은 `37b4d05253a9325445742d7ec7a016cde88e6e79`다.

### B02 구현 경계

구현:

```text
LOW_DEMAND_SLOT core Cause 6개와 조건부 Cause 4개 registry
Required / Optional / Blocking 입력 규칙
DataQualityContext와 critical conflict gate
Evidence·Contradiction source reference mapping
REVIEWABLE / NEEDS_DATA / DEPRIORITIZED / BLOCKED 상태
Cause Priority Score v1 (35/20/20/15/10)
PII 없는 Diagnostic Question과 deterministic 정렬
CauseAnalysisResult 및 Strategy handoff contract
```

의도적으로 제외:

```text
Cause Preview API와 저장
Raw CSV 또는 import repository 직접 접근
LLM cause wording·scoring
Strategy 선택·Playbook 실행
```

B02 코드 기준 커밋은 `3caa72a8a6f1b63d2d3d3970b02396aeae10fdd1`다.

### B03 구현 경계

구현:

```text
POST /api/v1/opportunities/{opportunityId}/cause-analyses/preview
Cause Preview request/response Pydantic contract
server-side Opportunity / tenant / business scope binding
server-controlled Opportunity Observation·detector metadata·evidence reference
deterministic as_of-aware Cause Run, input hash, preview ID
owner/admin/marketer authorization, cross-tenant 404, Hospital PII 422
no persistence / no external execution HTTP regression
```

의도적으로 제외:

```text
Decision Context Preview API
Diagnostic Answer의 별도 저장·patch endpoint
Cause Analysis persistence/migration
Strategy 선택·Playbook 실행
```

B03 코드 기준 커밋은 `76fa387cfd2c80fbb06327fcd2dd34ff9d71dd2f`다.

---

## 9. 문서 해석 규칙

- `00_PLANNING_INDEX.md`는 문서 상태와 읽기 순서의 단일 진입점이다.
- `DECISION_REGISTER_V2.md`는 확정·임시·미결정·폐기 결정을 관리한다.
- 기존 `ADR 0001~0019`는 과거 시점의 기록이므로 수정하지 않는다.
- `ADR 0020~0025`는 목표 Decision Intelligence 구조를 결정하지만 구현 완료를 뜻하지 않는다. `ADR 0026`은 B03의 실제 Preview 경계를 기록한다.
- 현재 구현 여부는 migration·code·test와 본 문서를 함께 확인한다.
- 현재 API 필드와 의미는 `API_CONTRACT.md`가 우선한다.
- 신규 목표 API는 `LOOFIO_API_CONTRACT_DECISION_INTELLIGENCE_V1.md`를 따른다.
- 현재 DB 구조는 `LOOFIO_DATA_SCHEMA_V1.md`가 설명하며 migration이 최종 기준이다.
- 신규 목표 DB는 `LOOFIO_DATA_SCHEMA_DECISION_INTELLIGENCE_V1.md`의 proposal을 따른다.
- Detector 계산 근거는 `LOOFIO_OPPORTUNITY_ENGINE_V1.md`와 관련 ADR을 따른다.

---

## 10. 문서 반영 후 확인

Decision Intelligence 문서 본문을 반영한 commit은 다음과 같다.

```text
document_alignment_commit: 0adeaae5866f37afb679336d20c28c3cfb2e5e17
```

문서 반영만으로 기능 상태 표의 `미구현`을 `구현`으로 바꾸지 않는다.
