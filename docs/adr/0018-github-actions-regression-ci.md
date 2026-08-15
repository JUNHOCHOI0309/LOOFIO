# ADR 0018 — GitHub Actions Regression CI v1

## Status

Accepted

## Context

LOOFIO의 backend 회귀 테스트와 견본 데이터 제품 루프 시뮬레이션, web typecheck/build는 로컬에서만 수동 실행되고 있었다. `main`에 병합되는 변경이 동일한 검증을 통과했는지 원격에서 재현할 기준이 필요하다.

## Decision

- GitHub Actions의 `.github/workflows/regression.yml`을 최소 회귀 검증 CI로 사용한다.
- `main`, `feature/**`, `fix/**`, `test/**`, `ci/**` push 및 수동 실행에서 CI를 실행한다. 현재 1인 로컬 merge 흐름에 맞춰 PR trigger는 요구하지 않는다.
- Backend job은 Python 3.12, `api/requirements-dev.txt`, 전체 `pytest`를 사용한다. 여기에는 sample-pack 제품 루프 시뮬레이션이 포함된다.
- Web job은 Node.js 22, root `package-lock.json`, workspace lint/build를 사용한다.
- workflow 권한은 repository contents 읽기로 제한하며, secrets·deployment·database migration·외부 실행을 수행하지 않는다.

## Self-review

- Infrastructure/Security 관점: 최소 권한을 사용하고 secret 또는 배포 credential을 참조하지 않으며, 동시 실행은 동일 branch의 오래된 job을 취소한다.
- Repository Maintainer 관점: local에서 이미 사용하는 전체 pytest와 web lint/build 명령을 고정된 런타임 버전으로 재현한다. CI 실패는 배포 성공을 의미하지 않으며 Staging/Production gate는 여전히 별도다.

## Rollback

workflow 파일을 비활성화 또는 제거해도 애플리케이션·DB·고객 데이터에는 영향이 없다. CI 오류는 workflow를 수정한 뒤 재실행한다.
