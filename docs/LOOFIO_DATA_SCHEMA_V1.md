# LOOFIO Data Schema v1

- 기준일: 2026-08-17
- 구현 기준: `api/migrations/0001` ~ `0011`
- 대상: PostgreSQL Hospital Appointment MVP

이 문서는 현재 데이터 모델을 사람이 검토할 수 있도록 요약한다. 실행 가능한 최종 스키마의 source of truth는 순서가 고정된 `api/migrations/*.sql`이다.

## 1. Tenant와 인증

| 테이블 | 역할 | 핵심 제약 |
|---|---|---|
| `tenants` | 고객 조직 경계 | UUID PK |
| `users` | LOOFIO 사용자 | email은 OAuth 제공 여부에 따라 nullable |
| `tenant_members` | 사용자와 Tenant 역할 | `(tenant_id, user_id)` PK, 4개 role |
| `user_identities` | Google/Naver provider subject | provider+subject unique, OAuth token 미저장 |
| `sessions` | 서버 저장 로그인 세션 | opaque UUID, 만료·철회·active tenant |

브라우저 쿠키에는 서명된 session ID만 두고 사용자·역할·active tenant는 서버에서 확인한다.

## 2. 사업장과 운영 데이터

| 테이블 | 역할 | Tenant 격리 |
|---|---|---|
| `businesses` | 병원 사업장 | `tenant_id`, `(tenant_id, id)` unique |
| `locations` | 지점 | tenant+business 복합 FK |
| `offerings` | 진료·시술 Offering | tenant+business 복합 FK |
| `customers` | 가명 고객 | tenant+business+external token unique |
| `appointments` | 정규화 예약 | tenant+business scope, source record idempotency |

`appointments.status`는 `booked`, `completed`, `cancelled`, `no_show`, `unknown`만 허용한다. 실제 완료 매출은 `completed` 행의 `paid_amount`만 사용한다.

## 3. Import와 lineage

| 테이블 | 역할 |
|---|---|
| `import_jobs` | 파일·schema version·hash·처리 건수·idempotency 상태 |
| `import_rows` | source raw payload와 normalized payload의 행 단위 lineage |
| `appointment_import_mappings` | 병원별 외부 열/상태 매핑 재사용 |

Appointment import의 중복 기준은 `(tenant_id, business_id, source_system, source_record_id)`다. 오류 행은 API preview/import 결과로 반환하며 현재 `import_rows`에는 imported/duplicate 행만 저장한다.

## 4. Opportunity Intelligence

| 테이블 | 역할 |
|---|---|
| `opportunities` | Observation·Estimate·score·confidence·limitations·version 저장 |
| `opportunity_evidence` | evidence type+payload의 hash 기반 불변 근거 |
| `recommendations` | 버전별 deterministic 수동 Recommendation 초안 |
| `recommendation_decisions` | 승인·거절·수정·나중에 결정 이력 |

현재 Opportunity type은 `LOW_DEMAND_SLOT`, `CANCELLATION_HOTSPOT`, `DORMANT_CUSTOMER`, `SERVICE_DEMAND_GAP`이다. 열린 Opportunity만 같은 detector+version+natural key 충돌 시 갱신된다. `score_version`과 `score_breakdown`으로 점수 의미를 재현한다.

## 5. Action과 Measurement

| 테이블 | 역할 |
|---|---|
| `actions` | 승인된 Recommendation의 manual 실행 계획 |
| `action_status_events` | 상태 전이의 actor·note 감사 이력 |
| `action_results` | 완료 Action의 사람이 기록한 결과와 측정 창 |

Measurement는 별도 테이블에 저장하지 않는다. 요청 시 `action_results`의 측정 창과 정규화 Appointment를 사용해 deterministic하게 계산한다. 현재 method는 같은 길이의 직전 1~4주 창 평균이며 signed delta를 반환한다.

## 6. 의도적으로 아직 없는 테이블

- LLM prompt/output audit 및 AI job
- external signal·weather·public data
- channel connector execution·delivery event
- persisted metric snapshot·persisted measurement
- campaign·content·customer segment
- Sale·Membership·Lead 등 Appointment 외 Domain Object

이 항목을 추가할 때는 tenant scope, version, migration, PII와 rollback을 먼저 정의한다.

## 7. Migration 규칙

- 파일은 번호순 append-only다.
- 공유·운영 DB에서 직접 DDL을 실행하지 않는다.
- 애플리케이션보다 migration을 먼저 적용한다.
- 파괴적 변경은 expand/contract로 나눈다.
- 과거 Detector·Score·Measurement 의미는 새 버전으로 보존한다.
