# Git 브랜치 운영 가이드
## `main + feature/* + 로컬 개발 → main 배포`

이 문서는 소규모~중소규모 웹 프로젝트에서 사용할 수 있는 단순하고 실용적인 Git 브랜치 운영 방식을 정리한다.

---

## 1. 기본 원칙

Git 브랜치와 실행 환경은 서로 다른 개념이다.

- **Git Branch**: 코드의 버전과 작업 흐름을 관리한다.
- **Local Environment**: 개발자의 PC에서 코드를 실행하고 테스트한다.
- **Production Environment**: 실제 사용자가 사용하는 운영 환경이다.

이 가이드에서는 별도의 `develop` 브랜치를 두지 않고 다음 구조를 사용한다.

```text
main
├── feature/login
├── feature/dashboard
├── feature/payment
├── fix/mobile-layout
└── refactor/api-client
```

`main`은 항상 배포 가능한 안정 상태를 유지하고, 실제 개발은 별도의 작업 브랜치에서 진행한다.

---

## 2. 전체 개발 흐름

```text
main
 │
 ├─ feature/* 브랜치 생성
 │
 ↓
로컬 환경에서 개발
 │
 ↓
로컬 테스트
 │
 ↓
commit
 │
 ↓
GitHub push
 │
 ↓
Pull Request
 │
 ↓
검토 / 테스트
 │
 ↓
main merge
 │
 ↓
CI/CD
 │
 ↓
Production 배포
```

핵심 원칙은 다음과 같다.

> `main`에서 직접 개발하지 않는다.  
> 작업 브랜치에서 개발한 뒤 검증이 끝난 코드만 `main`에 병합한다.

---

## 3. 브랜치 역할

### `main`

실제 서비스에 배포 가능한 안정 버전이다.

```text
main
└─ Production 배포 기준
```

권장 규칙:

- 직접 기능 개발 금지
- 가능하면 직접 `push` 금지
- Pull Request를 통해서만 변경
- 테스트를 통과한 코드만 병합
- 항상 실행 가능한 상태 유지

---

### `feature/*`

새 기능 개발용 브랜치다.

예:

```text
feature/login
feature/user-profile
feature/dashboard
feature/payment
feature/ai-parser
```

하나의 브랜치는 가급적 하나의 기능만 담당한다.

좋은 예:

```text
feature/login
```

좋지 않은 예:

```text
feature/login-dashboard-payment-admin
```

---

### `fix/*`

버그 수정용 브랜치다.

예:

```text
fix/login-error
fix/mobile-layout
fix/payment-validation
```

---

### `refactor/*`

기능 변화 없이 코드 구조를 개선할 때 사용한다.

```text
refactor/api-client
refactor/auth-service
```

---

### 선택적으로 사용할 수 있는 브랜치

필요한 경우 다음 규칙도 사용할 수 있다.

```text
docs/*
test/*
chore/*
```

예:

```text
docs/api-guide
test/login-service
chore/update-dependencies
```

---

## 4. 실제 작업 방법

새로운 기능을 만든다고 가정한다.

예:

```text
로그인 기능 개발
```

### Step 1. `main` 최신화

```bash
git switch main
git pull origin main
```

항상 최신 `main`에서 작업을 시작한다.

---

### Step 2. feature 브랜치 생성

```bash
git switch -c feature/login
```

구조:

```text
main
 └─ feature/login
```

이제 실제 개발은 `feature/login`에서 진행한다.

---

### Step 3. 로컬 환경에서 개발

예:

```text
localhost:3000
```

에서 애플리케이션을 실행하고 로그인 기능을 개발한다.

```text
feature/login
      │
      ↓
Local Environment
localhost:3000
```

여기서 여러 번 수정하고 테스트해도 `main`에는 영향을 주지 않는다.

---

### Step 4. 변경 내용 확인

```bash
git status
git diff
```

커밋하기 전에 어떤 파일이 변경되었는지 확인한다.

---

### Step 5. commit

```bash
git add .
git commit -m "feat: 로그인 기능 추가"
```

가능하면 하나의 커밋에는 하나의 논리적인 변경사항을 담는다.

예:

```text
feat: 로그인 API 추가
feat: 로그인 UI 추가
fix: 잘못된 로그인 오류 처리
```

---

### Step 6. GitHub에 push

처음 push하는 경우:

```bash
git push -u origin feature/login
```

이후에는:

```bash
git push
```

만 사용하면 된다.

---

## 5. Pull Request

GitHub에서 다음 Pull Request를 생성한다.

```text
feature/login
      ↓
     main
```

PR에서는 다음 내용을 확인한다.

- 기능이 정상 작동하는가
- 불필요한 코드가 들어가지 않았는가
- 기존 기능을 깨뜨리지 않는가
- 테스트가 통과하는가
- 환경 변수나 비밀키가 포함되지 않았는가
- 디버깅용 코드가 남아 있지 않은가

---

## 6. main 병합

검토가 끝나면:

```text
feature/login → main
```

으로 병합한다.

권장 방식:

```text
Squash and merge
```

작은 프로젝트에서는 여러 개발 중간 커밋을 하나로 정리할 수 있어서 관리하기 편하다.

예:

```text
feature/login

commit 1: 로그인 UI
commit 2: 수정
commit 3: 또 수정
commit 4: 버그 수정
commit 5: 테스트 수정

↓ Squash

main

feat: 로그인 기능 추가
```

---

## 7. Production 배포

`main`에 병합되면 CI/CD가 자동으로 실제 서버에 배포하도록 구성할 수 있다.

```text
GitHub main
     │
     ↓
GitHub Actions
     │
     ├─ Build
     ├─ Test
     └─ Deploy
          │
          ↓
      Production
```

예:

```text
main
 ↓
Vercel / Cloudflare / AWS / GCP
 ↓
https://example.com
```

따라서 구조는 다음과 같다.

```text
feature/*
   │
   │ 개발
   ↓
Local
   │
   │ PR
   ↓
main
   │
   │ CI/CD
   ↓
Production
```

---

## 8. main 배포 실패에 대비하기

`main`이 실제 Production과 직접 연결되어 있다면 병합 전에 최소한 다음 검증을 수행하는 것이 좋다.

```text
PR 생성
 │
 ├─ lint
 ├─ type check
 ├─ unit test
 ├─ build test
 └─ 필요 시 manual check
 │
 ↓
main merge
```

예:

```bash
npm run lint
npm run typecheck
npm run test
npm run build
```

모든 검사가 성공한 경우에만 `main`으로 병합하는 방식이 안전하다.

---

## 9. 배포 후 feature 브랜치 삭제

병합이 끝난 브랜치는 삭제한다.

로컬:

```bash
git switch main
git pull origin main
git branch -d feature/login
```

원격 브랜치:

```bash
git push origin --delete feature/login
```

GitHub PR 화면에서 `Delete branch`를 사용해도 된다.

---

## 10. 다음 기능 개발

다음 기능을 시작할 때 다시 최신 `main`을 기준으로 브랜치를 만든다.

```bash
git switch main
git pull origin main
git switch -c feature/dashboard
```

전체 흐름은 반복된다.

```text
main
 ↓
feature/dashboard
 ↓
로컬 개발
 ↓
commit
 ↓
push
 ↓
PR
 ↓
main
 ↓
배포
```

---

# 11. 여러 기능을 동시에 개발하는 경우

예를 들어 로그인과 대시보드를 동시에 개발한다면:

```text
                main
                 │
        ┌────────┴────────┐
        │                 │
 feature/login    feature/dashboard
        │                 │
   로컬 개발          로컬 개발
        │                 │
        └──── PR ─────────┘
                 │
                 ↓
                main
```

각 기능은 서로 다른 브랜치에서 관리한다.

---

# 12. 긴급 버그 수정

Production에서 문제가 발생하면 `main`에서 바로 수정하지 않고 별도 브랜치를 만든다.

```bash
git switch main
git pull origin main
git switch -c fix/login-crash
```

수정 후:

```text
fix/login-crash
      ↓
      PR
      ↓
     main
      ↓
Production
```

---

# 13. 환경 변수 관리

환경별 설정은 Git 브랜치가 아니라 환경 변수로 관리한다.

예:

```text
Local
.env.local

Production
Hosting Service Environment Variables
```

예:

```env
DATABASE_URL=...
API_KEY=...
OPENAI_API_KEY=...
```

`.env` 파일은 Git에 올리지 않는다.

`.gitignore`:

```gitignore
.env
.env.local
.env.*.local
```

특히 다음과 같은 정보는 repository에 커밋하지 않는다.

- API Key
- DB Password
- Access Token
- Secret Key
- OAuth Client Secret

---

# 14. 권장 브랜치 네이밍

```text
feature/*
fix/*
refactor/*
docs/*
test/*
chore/*
```

예:

```text
feature/user-login
feature/analytics-dashboard

fix/mobile-menu
fix/payment-error

refactor/api-service

docs/deployment-guide

test/auth-service

chore/update-packages
```

---

# 15. 권장 Commit Message

Conventional Commits 형태를 사용할 수 있다.

```text
feat: 새로운 기능
fix: 버그 수정
refactor: 코드 구조 개선
docs: 문서 변경
test: 테스트 추가/수정
chore: 설정 및 기타 작업
```

예:

```text
feat: 사용자 로그인 기능 추가
fix: 모바일 메뉴가 닫히지 않는 문제 수정
refactor: API 요청 모듈 분리
docs: 로컬 개발 가이드 추가
test: 로그인 서비스 테스트 추가
chore: 패키지 버전 업데이트
```

---

# 16. 권장 GitHub 설정

`main` 브랜치에는 Branch Protection을 적용하는 것이 좋다.

예:

```text
main
├─ 직접 push 제한
├─ Pull Request 필수
├─ CI 테스트 성공 필수
└─ merge 후 branch 삭제
```

혼자 개발하는 프로젝트에서도 실수로 `main`을 깨뜨리는 상황을 줄일 수 있다.

---

# 17. 최종 구조

```text
                        GitHub
                           │
                         main
                           │
                  Production 배포
                           │
                    실제 사용자 서비스


개발 시작
   │
   ↓
main 최신화
   │
   ↓
feature/* 생성
   │
   ↓
로컬 개발
   │
   ↓
로컬 테스트
   │
   ↓
commit
   │
   ↓
push
   │
   ↓
Pull Request
   │
   ↓
CI / 코드 검토
   │
   ↓
main merge
   │
   ↓
Production 자동 배포
```

---

# 18. 핵심 운영 규칙

1. `main`은 항상 배포 가능한 상태로 유지한다.
2. 실제 개발은 `feature/*`, `fix/*` 등의 작업 브랜치에서 한다.
3. 새 브랜치는 항상 최신 `main`에서 생성한다.
4. 개발과 테스트는 Local 환경에서 수행한다.
5. 변경사항은 GitHub에 push하고 Pull Request를 생성한다.
6. 테스트가 성공한 코드만 `main`에 병합한다.
7. `main` 병합을 Production 배포 기준으로 사용한다.
8. 환경 설정과 Secret은 브랜치가 아닌 환경 변수로 관리한다.
9. 병합된 작업 브랜치는 삭제한다.
10. 프로젝트 규모가 커지기 전까지 불필요하게 브랜치 구조를 복잡하게 만들지 않는다.

---

# 19. 한 줄 정리

```text
main
  = 안정적이고 배포 가능한 코드

feature/*
  = 기능 개발 코드

Local
  = feature 브랜치를 개발하고 테스트하는 장소

Production
  = main이 실제 실행되는 환경
```

따라서 기본 개발 프로세스는 다음과 같다.

```text
main
 → feature/*
 → Local 개발/테스트
 → Commit
 → Push
 → Pull Request
 → main Merge
 → Production Deploy
```
