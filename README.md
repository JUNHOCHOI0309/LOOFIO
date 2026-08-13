# LOOFIO

LOOFIO Hospital MVP의 초기 모노레포입니다. 사업 데이터를 기반으로 기회를 탐지하고, 승인된 행동과 결과 측정까지 연결하는 B2B SaaS를 만듭니다.

## 구성

- `apps/web`: Next.js 기반 운영 UI
- `api`: FastAPI 기반 API 및 향후 분석 애플리케이션
- `docker-compose.yml`: 로컬 PostgreSQL 16
- `docs`: 제품·아키텍처·운영 계약

## 로컬 시작

1. 환경 변수를 준비합니다.

   ```powershell
   Copy-Item .env.example .env
   ```

2. PostgreSQL을 실행합니다.

   ```powershell
   docker compose up -d postgres
   ```

3. 웹 의존성을 설치하고 개발 서버를 실행합니다.

   ```powershell
   npm install
   npm run dev:web
   ```

4. 별도 터미널에서 Python 가상환경과 API를 실행합니다.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r api/requirements-dev.txt
   uvicorn app.main:app --app-dir api --reload --port 8000
   ```

- 웹: `http://localhost:3000`
- API 문서: `http://localhost:8000/docs`
- 상태 확인: `http://localhost:8000/api/v1/health`

API 테스트는 프로젝트 루트에서 다음 명령으로 실행합니다.

```powershell
.\.venv\Scripts\python -m pytest
```

## Direct OAuth 설정

인증은 FastAPI backend가 처리하는 Google/Naver Authorization Code Flow를 사용합니다. `.env.example`을 `.env`로 복사한 뒤, 다음 값을 환경별 Secret으로 설정합니다.

- `SESSION_SECRET`: 환경마다 다른 고엔트로피 문자열
- `SESSION_COOKIE_SECURE`: local은 `false`, HTTPS 운영 환경은 `true`
- `APP_ORIGIN`, `API_ORIGIN`
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET`
- `NAVER_OAUTH_CLIENT_ID`, `NAVER_OAUTH_CLIENT_SECRET`

로컬 callback URL은 다음과 같이 등록합니다.

```text
http://localhost:8000/api/v1/auth/google/callback
http://localhost:8000/api/v1/auth/naver/callback
```

OAuth Secret은 repository 또는 frontend 환경 변수에 넣지 않습니다.

## 운영 원칙

구현 전에 `docs/AGENTS.md`와 관련 계약 문서를 따릅니다. 특히 Opportunity의 수치 계산과 탐지는 deterministic backend가 수행하며, AI는 구조화된 결과를 설명하고 행동을 제안합니다.
