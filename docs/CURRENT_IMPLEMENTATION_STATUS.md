# LOOFIO 현재 구현 상태

- 기준일: 2026-08-17
- 기준 브랜치: `main`
- 기준 커밋: `b7cc45d` (`merge: add versioned opportunity scoring`)
- 제품 범위: Hospital Appointment MVP

이 문서는 기획 문서와 실제 코드 사이의 현재 상태를 연결하는 단일 기준이다. 장기 방향은 기술 로드맵과 Opportunity Engine 문서를 따르고, 실제 제공 기능을 판단할 때는 이 문서를 먼저 확인한다.

## 1. 현재 동작하는 제품 루프

```text
Google/Naver OAuth 로그인
→ Tenant·병원 생성
→ 병원별 CSV 열·상태 매핑
→ Appointment 정규화·저장
→ Metric 계산
→ 4개 Detector 실행
→ Opportunity 저장·점수화
→ 수동 Recommendation 초안·사용자 결정
→ Manual Action 계획·상태 변경
→ Result 기록
→ 직전 동일 기간 Baseline과 Measurement 비교
→ Dashboard 이력 확인
```

외부 메시지·광고·쿠폰·게시 채널은 호출하지 않는다. Measurement의 변화량은 단순 관찰 비교이며 인과효과나 Incremental Revenue가 아니다.

## 2. 기능별 상태

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
| LowDemandSlot | 구현 | 최소 관측 주와 상대 Demand Index 기반 `low-demand-slot-v1` |
| RevenueGap | 구현 | 같은 요일 비교 시간대 결제 표본 기반 금액 Estimate v2 |
| CancellationHotspot | 구현 | 슬롯×Offering 예약 이탈률과 사업장 기준 비교 |
| DormantCustomer | 구현 | 명시적 기준일과 재방문 간격 기반 지연 Observation |
| ServiceDemandGap | 구현 | Offering 전체 비중과 슬롯 비중 비교 |
| Opportunity | 구현 | Detector version·evidence·limitations·Observation/Estimate 분리 저장 |
| Opportunity Score | 구현 | `opportunity-score-v1`, 35/30/20/15 구성요소·버전 저장 및 UI 표시 |
| Recommendation | 부분 구현 | 유형별 deterministic 수동 검토 초안과 결정 이력. LLM 호출은 없음 |
| Action | 구현 | 승인된 Recommendation의 manual 계획, 단방향 상태 전이와 감사 이력 |
| Result | 구현 | 완료 Action의 실행 요약·측정 기간·실제 지출 기록 |
| Measurement | MVP 구현 | 직전 1~4주 동일 길이 창의 평균과 signed delta 계산 |
| Dashboard | 구현 | Metric·Detector·Opportunity·Score·Recommendation·Action·Result·Measurement 표시 |
| 회귀 검증 | 구현 | backend 66 tests, sample pack 제품 루프, web typecheck/build |
| CI | 구현 | GitHub Actions `Regression checks`, `feature/fix/test/ci`와 `main` push 검사 |

## 3. Detector와 Opportunity 계약

| Opportunity type | Detector version | Estimate | 현재 Recommendation |
|---|---|---|---|
| `LOW_DEMAND_SLOT` | `low-demand-revenue-gap-v2` | 결제 표본 충족 시 RevenueGap | `manual_time_slot_offer_test` |
| `CANCELLATION_HOTSPOT` | `cancellation-hotspot-v1` | 없음 | `manual_cancellation_flow_review` |
| `DORMANT_CUSTOMER` | `dormant-customer-v1` | 없음 | `manual_revisit_cohort_review` |
| `SERVICE_DEMAND_GAP` | `service-demand-gap-v1` | 없음 | `manual_offering_slot_review` |

모든 유형은 `opportunity-score-v1`으로 검토 우선순위를 계산한다. 점수는 성공 확률이나 매출 가치가 아니다.

## 4. 데이터와 표본

프로젝트 표본은 `sample-data/appointments`에 보관한다.

- `loofio_appointment_sample_hospital_v1.csv`: Hospital v1 기본 계약
- `hospital_revenue_gap_positive_v1.csv`: 결제 표본이 충분한 RevenueGap 양성 시나리오
- `hospital_revenue_gap_sparse_payment_v1.csv`: 결제 표본 부족으로 Estimate를 생략하는 시나리오
- `hospital_operational_mix_v1.csv`: 여러 Offering·취소·재방문 패턴이 섞인 전체 제품 루프

회귀 테스트는 CSV parsing부터 Detector, Opportunity, Recommendation, Action, Result, Measurement까지 연결한다.

## 5. 코드 위치

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
| PostgreSQL migration | `api/migrations` |
| 회귀 테스트 | `api/tests` |

## 6. 아직 구현하지 않은 범위

- 실제 AI Gateway, provider adapter, LLM 기반 구조화 설명·추천
- Excel 파일 import와 예약/POS API connector
- 날씨·공휴일·상권·지역 행사 등 External Context
- 고객 메시지, 광고, 쿠폰, 게시 등 외부 채널 실행
- 자동 실행·예산 통제·예약 실행·재시도 queue
- 인과 추론, Incrementality, ROI, A/B test
- Appointment 외 Sale·Membership·Lead 등 다른 Archetype adapter
- Staging/Production 배포, Secret Manager, migration 자동 실행
- 운영 monitoring, error tracking, backup/restore 자동화

## 7. 다음 구현 우선순위

1. Opportunity의 숫자를 바꾸지 않는 structured AI Explanation/Recommendation contract
2. provider 중립 AI Gateway와 실패 격리·감사·재시도 경계
3. Staging 배포 및 migration/smoke-test 자동화
4. 실제 병원 CSV 변형 표본 확대와 mapping 회귀 시나리오 강화
5. 외부 Context를 원인 확정이 아닌 가설 보조 정보로 연결

## 8. 문서 해석 규칙

- `ADR`은 해당 시점의 의사결정 기록이므로 현재 상태에 맞춰 과거 문장을 수정하지 않는다.
- 구현 여부는 이 문서와 코드·migration·test를 함께 확인한다.
- API 필드와 의미는 `API_CONTRACT.md`가 우선한다.
- 제품의 장기 목표와 미구현 범위는 `LOOFIO_TECH_ROADMAP_v1.md`를 따른다.
- Detector 계산 근거는 `LOOFIO_OPPORTUNITY_ENGINE_V1.md`와 관련 ADR을 따른다.
