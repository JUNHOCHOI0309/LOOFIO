# AGENTS.md — LOOFIO Repository Rules

## 0. 목적

이 파일은 LOOFIO 저장소에서 작업하는 사람과 AI 에이전트가 반드시 따라야 하는 최상위 개발 규칙이다.

LOOFIO의 제품 목적은 다음과 같다.

> 사업 데이터를 관찰하고, 아직 잡지 못한 매출 기회를 데이터에서 탐지하고, 실행 가능한 행동을 추천하고, 실행 결과를 측정하여 다음 판단을 개선한다.

핵심 루프:

```text
Observe
→ Opportunity
→ Recommendation
→ Decision
→ Action
→ Result
→ Measurement
→ Learn
```

LOOFIO의 핵심 결과물은 콘텐츠가 아니라 **다음 행동과 그 행동의 측정 가능한 결과**다.

---

# 1. 작업 전 필수 확인

구조적 변경 전 아래 문서를 순서대로 확인한다.

1. `docs/ARCHITECTURE.md`
2. `docs/DEPENDENCY_RULES.md`
3. `docs/API_CONTRACT.md`
4. `docs/PROHIBITED_CHANGES.md`
5. `docs/CODE_OWNERSHIP.md`
6. `docs/DEPLOYMENT_FLOW.md`

제품 데이터 구조를 수정할 때는 다음 기획 문서도 기준으로 삼는다.

- `LOOFIO_BUSINESS_TAXONOMY_V1.md`
- `LOOFIO_DATA_SCHEMA_V1.md`
- `LOOFIO_OPPORTUNITY_ENGINE_V1.md`
- `LOOFIO_TECH_ROADMAP_v1.md`

문서와 코드가 충돌하면 코드를 임의로 기준으로 삼지 않는다. 의도된 변경인지 먼저 판단하고 문서를 함께 수정한다.

---

# 2. 절대 유지해야 하는 제품 원칙

## 2.1 계산과 탐지는 deterministic backend가 수행한다

LLM이 직접 수행해서는 안 되는 작업:

- 매출 합계
- 증감률
- ROI
- 예약률
- 취소율
- 가동률
- 재방문 간격
- baseline
- Opportunity Score의 정량 계산
- 통계 검정
- Detector 조건 판정

LLM의 주 역할:

- 구조화된 분석 결과 설명
- 가능한 원인 가설
- 전략 제안
- 행동 제안
- 콘텐츠 생성

핵심 원칙:

> 코드가 기회를 탐지하고 AI는 이를 설명·전략화한다.

## 2.2 Observation / Estimate / Recommendation을 섞지 않는다

사용자에게 보여주는 모든 기회는 최소 다음 세 층을 구분한다.

```text
Observation
실제 데이터로 확인된 사실

Estimate
가정을 포함한 계산/추정

Recommendation
실행 제안
```

추정 매출을 실제 손실 또는 보장 매출로 표현하지 않는다.

## 2.3 Recommendation → Action → Result 연결을 끊지 않는다

추천을 저장하고 끝내지 않는다.

가능한 모든 실행은 다음 연결을 유지한다.

```text
Opportunity
→ Recommendation
→ User Decision
→ Action
→ Result
→ Measurement
```

이 연결 데이터는 LOOFIO의 핵심 장기 자산이다.

## 2.4 Human-in-the-loop가 기본이다

MVP에서 AI가 다음을 무승인으로 실행하지 않는다.

- 광고비 사용 또는 변경
- 고객 메시지 발송
- 외부 게시
- 쿠폰/프로모션 활성화
- 고객에게 직접 답변

자동화 수준을 높이는 변경은 별도 제품·안전 검토가 필요하다.

## 2.5 Tenant 격리는 기능이 아니라 불변조건이다

다른 tenant 또는 business의 원문 데이터가 다음 위치에서 섞이면 안 된다.

- 쿼리
- 캐시
- 검색/RAG
- 로그
- 파일 경로
- AI 컨텍스트
- 분석 결과
- 추천
- Export

모든 데이터 접근은 명시적인 tenant/business scope를 가져야 한다.

---

# 3. 아키텍처 원칙

기본 의존 방향:

```text
UI / Apps
    ↓
API / Application
    ↓
Domain / Analytics
    ↓
Ports / Contracts

Infrastructure / Connectors
    └──────────────→ Ports 구현
```

분석 파이프라인:

```text
Raw
→ Normalization
→ Domain
→ BusinessEvent
→ Metrics
→ Detectors
→ Scoring
→ Opportunity
→ AI Explanation / Recommendation
→ Decision
→ Action
→ Measurement
```

반대 방향 의존을 만들지 않는다.

세부 규칙은 `docs/DEPENDENCY_RULES.md`를 따른다.

---

# 4. 데이터 모델 규칙

## 4.1 `Appointment`는 전체 제품의 공통 루트가 아니다

`Appointment`는 `APPOINTMENT_SERVICE`의 첫 Domain Contract다.

다업종 확장은 다음처럼 Domain Adapter를 추가한다.

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

공통 분석 계층은 `BusinessEvent`, `Metric`, `Opportunity`, `Action`, `Measurement`를 중심으로 유지한다.

## 4.2 `Service` 대신 공통 개념은 `Offering`

상품, 서비스, 패키지, 회원권 등 판매 대상을 공통 표현할 때 `Offering`을 사용한다.

## 4.3 공식 직업분류와 LOOFIO Archetype을 분리한다

공식 KECO/KSCO 값은 원본 taxonomy로 보존한다.

LOOFIO의 `support_level`, `archetype`, `mapping_version`은 별도 해석 데이터다.

공식 코드를 LOOFIO 내부 의미로 덮어쓰지 않는다.

## 4.4 개인정보 최소화

고객 연락처 원문을 Core 분석 식별자로 사용하지 않는다.

가능하면:

```text
raw identifier
→ HMAC / tokenization
→ external_customer_token
→ internal customer_id
```

형태를 사용한다.

---

# 5. API 변경 규칙

API는 `docs/API_CONTRACT.md`를 따른다.

다음 변경은 breaking change로 취급한다.

- 기존 필수 필드 삭제
- 기존 필드 의미 변경
- enum 값의 의미 변경
- 성공 상태 코드의 의미 변경
- 기존 리소스 ID 의미 변경
- Observation/Estimate/Recommendation 구조 혼합
- pagination 의미 변경
- 화폐 단위/시간대 해석 변경

breaking change는 기존 `/api/v1`을 조용히 변경하지 말고 새 버전 또는 명시적 migration 경로가 필요하다.

---

# 6. Database 변경 규칙

모든 DB 변경은 migration으로 수행한다.

운영 DB에서 직접 DDL을 수정하지 않는다.

파괴적 변경은 기본적으로 expand/contract 패턴을 사용한다.

```text
1. 새 컬럼/테이블 추가
2. 양쪽 형식 호환 코드 배포
3. backfill
4. 읽기 경로 전환
5. 충분한 검증
6. 구 필드 제거
```

Detector 또는 Metric 결과의 의미가 바뀌면 관련 `version`도 변경한다.

과거 Opportunity를 현재 계산식으로 다시 해석해서는 안 된다.

---

# 7. AI 관련 규칙

애플리케이션 비즈니스 코드에 특정 모델명을 직접 박지 않는다.

권장:

```text
task_type / model_route
→ AI Gateway
→ provider/model 선택
```

AI 호출은 가능한 한 구조화된 입력과 출력 스키마를 사용한다.

AI 컨텍스트에는 필요한 최소 데이터만 전달한다.

개인정보·민감정보는 가능하면 제거/가명화 후 전달한다.

AI 설명이 deterministic 계산 결과와 불일치하면 계산 결과가 우선이다.

---

# 8. 테스트 요구사항

변경 범위에 따라 최소 다음을 검증한다.

## Metric / Detector

- 동일 입력 → 동일 결과
- 경계값
- 표본 부족
- 누락 데이터
- timezone
- cancelled/no_show 등 상태
- 금액/통화
- Detector version

## Ingestion / Normalization

- 중복 import
- idempotency
- 날짜 parsing
- 외부 상태값 mapping
- 필수 컬럼 누락
- customer tokenization
- 잘못된 row 격리

## Tenant

- 다른 tenant 데이터 접근 불가
- 다른 business 데이터 혼입 불가

## API

- contract test
- validation error
- backward compatibility
- idempotency가 필요한 write endpoint

## Recommendation

- Opportunity의 Observation 수치 임의 변경 금지
- limitations 누락 금지
- expected effect를 실제 결과로 표현하지 않는지 검증

---

# 9. 코드 리뷰가 반드시 필요한 변경

다음 변경은 단독으로 merge하지 않는다.

- DB migration
- tenant/auth/permission
- PII 처리
- Detector 계산식
- Opportunity Score
- Measurement/Incrementality
- API breaking change
- 외부 채널 실행
- 광고비/메시지 자동화
- AI 데이터 전송 범위
- Secret handling
- 배포 파이프라인
- `AGENTS.md` 및 `PROHIBITED_CHANGES.md`

구체적인 논리적 owner는 `docs/CODE_OWNERSHIP.md`를 따른다.

---

# 10. 완료 정의

작업은 코드가 동작한다고 끝난 것이 아니다.

필요한 경우 다음을 함께 완료한다.

- 코드
- 테스트
- migration
- API contract
- 문서
- metric/detector version
- 로그/모니터링
- 데이터 마이그레이션 또는 backfill 계획
- rollback 경로

---

# 11. 금지 변경

전체 목록은 `docs/PROHIBITED_CHANGES.md`를 따른다.

특히 아래는 금지한다.

1. 원본 예약/매출 데이터를 통째로 LLM에 전달하고 문제를 찾게 하는 것
2. LLM이 매출/ROI/증감률을 계산하는 것
3. tenant scope 없는 DB query
4. 고객 연락처 평문을 장기 분석 식별자로 사용하는 것
5. Estimate를 Actual Revenue로 표시하는 것
6. Detector 의미 변경 후 version을 유지하는 것
7. migration 없이 DB 구조를 운영에서 직접 변경하는 것
8. 사용자 승인 없이 MVP에서 외부 마케팅 액션을 실행하는 것
9. business logic에서 특정 AI provider/model에 강결합하는 것
10. API v1 계약을 공지 없이 깨뜨리는 것

---

# 12. 기술 결정 상태

현재 구현으로 확정된 선택:

- Backend: FastAPI / Pydantic / psycopg
- Frontend: Next.js / React / TypeScript
- Database: PostgreSQL
- Authentication: Google·Naver direct OAuth와 서버 저장 세션
- CI: GitHub Actions regression checks

다음은 이 파일에서 임의 확정하지 않는다.

- 클라우드·Production hosting 공급자
- 모니터링 공급자
- Secret Manager 공급자
- Queue·Cache 제품
- AI provider/model
- Production migration runner

새 선택과 기존 선택의 변경은 별도 ADR로 기록한다. 실제 구현 범위는 `CURRENT_IMPLEMENTATION_STATUS.md`를 따른다.
