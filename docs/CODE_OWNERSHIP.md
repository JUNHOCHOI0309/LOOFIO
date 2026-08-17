# LOOFIO Code Ownership v1

## 1. 목적

LOOFIO 코드의 변경 책임과 필수 리뷰 영역을 논리적으로 정의한다.

현재 실제 GitHub 팀/사용자 이름은 확정되지 않았으므로 이 문서는 **역할 기반 ownership**을 정의한다.

실제 저장소에서는 `.github/CODEOWNERS.template`의 placeholder를 실제 GitHub handle/team으로 치환한다.

## 1.1 현재 코드 경로 대응

| Logical owner | 현재 경로 |
|---|---|
| Repository Maintainer | `/`, `docs`, `.github`, dependency manifest |
| Core Platform | `api/app/auth`, `api/app/api/dependencies.py`, business store, `api/migrations` |
| Data/Ingestion | `api/app/imports`, import routes/schemas, `sample-data` |
| Opportunity Intelligence | `api/app/metrics`, `api/app/analytics`, `api/app/opportunities` |
| Recommendation/Action | `api/app/recommendations`, `api/app/actions` |
| Measurement | `api/app/results` |
| Web Product | `apps/web/app` |

1인 개발 단계의 실제 merge 방식은 `main_feature_git_workflow.md`를 따른다. 중요 계산·migration 변경은 ADR 또는 현재 상태 문서에 위험 관점 자기검토를 남긴다.

---

# 2. Ownership 원칙

Ownership은 독점 개발 권한이 아니다.

Owner의 책임:

- 설계 일관성
- 보안/데이터 영향 검토
- API/DB 호환성
- 테스트 충분성
- 관련 문서 갱신
- 위험 변경 승인

다른 개발자가 코드를 수정할 수 있지만 중요 영역은 해당 논리적 Owner 리뷰를 거친다.

---

# 3. Logical Owners

## Repository Maintainer

범위:

```text
/
AGENTS.md
docs/
build configuration
dependency manifest
```

책임:

- 전체 구조
- 문서 우선순위
- cross-module 변경
- 릴리즈 기준

## Core Platform Owner

범위:

```text
/modules/business
/modules/taxonomy
/data/repositories
/data/migrations
auth / tenant boundary
```

책임:

- Tenant isolation
- DB schema
- Business/Offering/Customer
- migration 호환성

## Data Ingestion Owner

범위:

```text
/modules/ingestion
/import
/normalization
/connectors/* input side
```

책임:

- CSV/Excel/API import
- column mapping
- idempotency
- PII/tokenization
- source lineage

## Opportunity Intelligence Owner

범위:

```text
/analytics/metrics
/analytics/detectors
/analytics/scoring
/ai/opportunity (설명이 아니라 orchestration인 경우)
```

책임:

- Metric 정의
- Detector 계산
- Opportunity Score
- Confidence
- deterministic 재현성
- versioning

## AI Recommendation Owner

범위:

```text
/ai/gateway
/ai/explanation
/ai/recommendation
/ai/content
prompt/schema
```

책임:

- 모델 추상화
- structured output
- prompt version
- hallucination guard
- cost/latency
- AI 데이터 최소화

## Action & Measurement Owner

범위:

```text
/modules/marketing
/measurement
/action
/results
```

책임:

- Recommendation → Action
- Action status
- Result
- baseline
- Measurement
- Incremental estimate 표현

## Connector Owner

범위:

```text
/connectors
/jobs/sync
```

책임:

- 외부 API
- OAuth/secret
- retry
- rate limit
- provider compatibility
- 외부 실행 안전성

## Product/UI Owner

범위:

```text
/apps
frontend
dashboard
opportunity/action/results UI
```

책임:

- Observation/Estimate/Recommendation 구분
- Confidence/limitations 노출
- 사용자 승인 흐름
- API contract 준수

## Infrastructure/Security Owner

범위:

```text
deployment
CI/CD
secrets
monitoring
infrastructure
security config
```

책임:

- 배포
- secret
- runtime isolation
- backup/restore
- observability
- incident 대응

---

# 4. Mandatory Review Matrix

| 변경 | 필수 Owner |
|---|---|
| `AGENTS.md` | Repository Maintainer |
| Architecture/Dependency | Repository Maintainer + 영향 영역 Owner |
| Tenant/Auth | Core Platform + Infrastructure/Security |
| DB migration | Core Platform |
| PII/Customer token | Core Platform + Data Ingestion + Security |
| Metric | Opportunity Intelligence |
| Detector | Opportunity Intelligence |
| Opportunity Score/Confidence | Opportunity Intelligence |
| AI provider/model routing | AI Recommendation |
| Prompt structured schema | AI Recommendation |
| Recommendation 행동 정책 | AI Recommendation + Action/Measurement |
| 외부 메시지/광고 실행 | Connector + Action/Measurement + Security |
| Measurement/Incrementality | Action/Measurement |
| Public API breaking change | Repository Maintainer + 영향 Owner |
| Deployment pipeline | Infrastructure/Security |
| Prohibited changes 문서 | Repository Maintainer + 관련 Owner |

---

# 5. High-Risk Two-Owner Rule

다음 변경은 최소 2개 논리 영역의 리뷰를 요구한다.

- 고객 데이터 외부 AI 전송 범위 증가
- 자동 광고 집행
- 자동 고객 메시지
- Tenant isolation 변경
- 데이터 삭제/보존 정책
- 실제 매출 귀속/Incrementality 계산
- 대규모 destructive migration
- API 인증 방식
- 운영 secret 처리

팀 규모가 1명인 동안에도 PR 설명에 **두 관점의 체크리스트**를 별도로 작성하여 자기 검토한다.

---

# 6. CODEOWNERS 적용

현재 template:

```text
.github/CODEOWNERS.template
```

실제 저장소 연결 후:

```text
.github/CODEOWNERS
```

로 복사하고 placeholder를 GitHub 사용자/팀으로 변경한다.

예:

```text
/analytics/detectors/ @loofio-opportunity
/ai/                   @loofio-ai
/data/migrations/      @loofio-core
```

실제 handle이 확정되기 전 가짜 팀명을 CODEOWNERS에 넣어 merge 보호가 작동한다고 가정하지 않는다.

---

# 7. Ownership 변경

새 팀이 생기거나 모듈이 분리될 경우:

1. 이 문서 수정
2. CODEOWNERS 수정
3. branch protection 확인
4. 관련 runbook/alert ownership 수정

순서로 반영한다.
