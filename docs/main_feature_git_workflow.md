# Git 브랜치 운영 가이드

## `main + feature/* + 로컬 merge → main 배포`

이 문서는 LOOFIO의 단순한 1인 개발 Git 운영 방식이다. `main`은 배포 가능한 상태로 유지하고, 모든 기능 개발은 `feature/*` 등 작업 브랜치에서 수행한다. Pull Request는 기본 절차에 포함하지 않는다.

## 핵심 흐름

```text
main
  ↓
feature/* 생성
  ↓
로컬 개발·테스트
  ↓
commit / push
  ↓
로컬에서 main으로 merge
  ↓
main push
  ↓
CI/CD / Production 배포
```

Git 브랜치는 코드 이력을 관리하는 수단이고, Local 환경은 기능을 실행·검증하는 장소다. 환경 변수와 Secret은 브랜치가 아니라 환경별 설정으로 관리한다.

## 브랜치 역할

| 브랜치 | 용도 |
|---|---|
| `main` | 항상 배포 가능한 기준선. 직접 기능 개발 금지 |
| `feature/*` | 하나의 새 기능 개발 |
| `fix/*` | 버그 수정 |
| `refactor/*` | 기능 변화 없는 구조 개선 |
| `docs/*`, `test/*`, `chore/*` | 문서, 테스트, 설정성 변경 |

## 새 기능 작업 절차

1. 최신 `main`에서 시작한다.

   ```bash
   git switch main
   git pull origin main
   git switch -c feature/login
   ```

2. feature 브랜치에서 개발하고 로컬 검증한다. `main`에는 직접 기능을 작성하지 않는다.

3. 변경 범위를 확인하고 논리적인 단위로 커밋한다.

   ```bash
   git status
   git diff
   git add <intended-files>
   git commit -m "feat: 로그인 기능 추가"
   ```

4. feature 브랜치를 원격에 push한다.

   ```bash
   git push -u origin feature/login
   ```

5. merge 전에 최소한 다음을 확인한다.

   - 기능이 정상 작동하는가
   - lint, type check, unit test, build가 통과하는가
   - 불필요한 코드·디버깅 코드·Secret이 없는가
   - 기존 기능과 API 계약을 깨지 않는가
   - DB migration, tenant/권한, PII, Detector, 배포 관련 변경이면 `docs/AGENTS.md`의 추가 검토 요건을 충족하는가

6. 로컬에서 feature 브랜치를 `main`에 merge하고 `main`을 push한다.

   ```bash
   git switch main
   git pull origin main
   git merge --no-ff feature/login
   git push origin main
   ```

   `--no-ff`를 사용해 feature 단위의 merge 이력을 보존한다. 충돌이 나면 해결 후 관련 테스트를 다시 실행한다.

7. `main` 배포와 검증이 끝나면 작업 브랜치를 삭제한다.

   ```bash
   git branch -d feature/login
   git push origin --delete feature/login
   ```

## 긴급 수정

운영 장애도 `main`에서 직접 수정하지 않는다.

```bash
git switch main
git pull origin main
git switch -c fix/login-crash
```

수정·검증·commit·push 후 동일하게 로컬에서 `main`으로 merge한다.

## 환경 변수와 Secret

`.env`, `.env.local` 및 API Key, DB 비밀번호, Access Token, OAuth Client Secret은 커밋하지 않는다. Local과 Production은 서로 다른 환경 변수 및 Secret을 사용한다.

## Commit 메시지

Conventional Commits 형태를 권장한다.

```text
feat: 새로운 기능
fix: 버그 수정
refactor: 코드 구조 개선
docs: 문서 변경
test: 테스트 추가 또는 수정
chore: 설정 및 기타 작업
```

## 운영 규칙

1. `main`은 항상 배포 가능한 상태로 유지한다.
2. 실제 개발은 작업 브랜치에서만 수행한다.
3. 새 브랜치는 최신 `main`에서 생성한다.
4. 테스트가 성공한 변경만 로컬에서 `main`으로 merge한다.
5. `main` push를 Production 배포 기준으로 사용한다.
6. 병합·배포가 끝난 작업 브랜치는 삭제한다.
7. 복수 기능은 서로 다른 브랜치에서 독립적으로 개발하고, 각각 최신 `main`에 순차 merge한다.
