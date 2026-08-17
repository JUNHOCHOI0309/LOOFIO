# LOOFIO Project Governance v1

이 디렉터리는 LOOFIO의 제품 기획을 실제 개발 규칙으로 고정하기 위한 프로젝트 운영 문서 묶음이다.

## 기준 문서

이 운영 문서는 다음 LOOFIO 기획 문서를 기준으로 작성되었다.

- `LOOFIO_TECH_ROADMAP_v1.md`
- `LOOFIO_BUSINESS_TAXONOMY_V1.md`
- `LOOFIO_DATA_SCHEMA_V1.md`
- `LOOFIO_OPPORTUNITY_ENGINE_V1.md`
- `CURRENT_IMPLEMENTATION_STATUS.md`

## 문서 목록

| 파일 | 역할 |
|---|---|
| `docs/CURRENT_IMPLEMENTATION_STATUS.md` | 실제 구현·검증·미구현 범위의 현재 기준 |
| `docs/LOOFIO_DATA_SCHEMA_V1.md` | migration 기준 현재 PostgreSQL 데이터 모델 |
| `AGENTS.md` | 저장소 전체 개발 규칙과 AI/사람 개발자 공통 지침 |
| `docs/ARCHITECTURE.md` | 시스템 경계, 데이터 흐름, 모듈 역할 |
| `docs/DEPENDENCY_RULES.md` | 모듈 간 허용/금지 의존성 |
| `docs/CODE_OWNERSHIP.md` | 논리적 코드 오너십 및 리뷰 책임 |
| `docs/API_CONTRACT.md` | API 호환성·버전·리소스 계약 |
| `docs/PROHIBITED_CHANGES.md` | 명시적으로 금지하는 변경 |
| `docs/DEPLOYMENT_FLOW.md` | 개발→검증→스테이징→운영 배포 흐름 |
| `.github/CODEOWNERS.template` | 실제 GitHub CODEOWNERS 작성용 템플릿 |

## 문서 우선순위

충돌 시 다음 순서를 따른다.

1. 법적·보안 요구사항
2. `AGENTS.md`
3. `docs/PROHIBITED_CHANGES.md`
4. `docs/API_CONTRACT.md`
5. `docs/CURRENT_IMPLEMENTATION_STATUS.md` — 구현 여부 판단에 한함
6. `docs/ARCHITECTURE.md`
7. `docs/DEPENDENCY_RULES.md`
8. `docs/CODE_OWNERSHIP.md`
9. `docs/DEPLOYMENT_FLOW.md`
10. 개별 구현 문서와 코드 주석

제품 정의나 데이터 모델 자체를 바꿔야 한다면 운영 문서를 우회해서 코드부터 수정하지 않는다. 먼저 관련 기획 문서와 본 운영 문서를 함께 갱신한다.

## 현재 확정된 구현 선택

- Frontend: Next.js 16 / React / TypeScript
- Backend: FastAPI / Pydantic / psycopg
- Database: PostgreSQL 16
- Authentication: Google·Naver direct OAuth와 서버 저장 세션
- CI: GitHub Actions regression workflow
- Local orchestration: Docker Compose PostgreSQL

결정 근거와 변경 이력은 `docs/adr`에 보존한다.

## 아직 확정하지 않은 것

다음은 현재 기획 자료에서 확정되지 않았으므로 이 문서 묶음에서도 특정 제품으로 고정하지 않는다.

- 클라우드/호스팅 공급자
- 모니터링 제품
- Secret Manager 제품
- Production 배포·migration 실행 제품
- 실제 GitHub 사용자/팀 CODEOWNERS

이 항목은 구현 단계에서 ADR 또는 별도 기술결정 문서로 확정한다.
