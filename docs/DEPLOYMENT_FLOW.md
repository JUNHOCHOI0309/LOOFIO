# LOOFIO Deployment Flow v1

## 1. 상태

현재 LOOFIO의 실제 클라우드와 컨테이너 플랫폼은 확정되지 않았다. 회귀 검증 CI는 GitHub Actions를 사용한다.

따라서 이 문서는 **공급자 독립적인 배포 계약**을 정의하며, CI의 최소 구현 범위만 명시한다.

현재 `.github/workflows/regression.yml`은 `main`, `feature/**`, `fix/**`, `test/**`, `ci/**` push와 수동 실행에서 다음을 수행한다.

- Python 3.12에서 전체 backend test와 sample-pack 제품 루프 회귀 테스트
- Node.js 22에서 web typecheck와 production build

이 workflow는 배포·migration·secret 접근을 수행하지 않는다. Staging/Production 배포 방식은 별도 결정이 필요하다.

---

# 2. 환경

최소 환경:

```text
Local / Test
↓
Staging
↓
Production
```

가능하면 Preview 환경을 PR 단위로 추가한다.

Production과 Staging은 데이터/secret을 분리한다.

운영 고객 데이터를 Staging에 그대로 복사하지 않는다.

---

# 3. Git Flow

권장 기본 흐름:

```text
feature/fix branch
→ Pull Request
→ CI
→ Review
→ main merge
→ Staging deploy
→ Smoke/Integration
→ Production approval
→ Production deploy
```

장기 release branch 전략이 필요해지기 전에는 단순한 main 중심 흐름을 우선한다.

실제 branch policy는 저장소 설정과 함께 확정한다.

---

# 4. Pull Request Gate

merge 전 최소 확인:

- unit test
- lint/format
- type/static check(사용 언어가 지원하는 경우)
- dependency/security scan
- API contract test
- migration validation
- tenant isolation 관련 테스트
- Detector snapshot/regression test(관련 변경 시)

중요 파일 변경 시 CODEOWNERS review를 추가한다.

---

# 5. Migration Gate

DB migration이 포함되면 반드시 분리 확인한다.

## Safe 기본

- additive table
- nullable column
- new index
- compatible enum strategy

## Risky

- column rename
- type change
- NOT NULL 즉시 추가
- large backfill
- table/column drop
- unique constraint 추가

Risky migration은 expand/contract를 기본으로 한다.

대용량 index/backfill은 production lock/부하를 검토한다.

---

# 6. Staging Deploy

Staging 배포 후 확인:

```text
Health
Auth
Tenant isolation
DB migration
CSV import
Normalization
Metric
Detector
Opportunity
Recommendation
Decision
Action
Measurement
```

모든 배포에서 전체 E2E가 필요하지는 않지만 변경 영역의 핵심 경로는 smoke test한다.

---

# 7. Production Approval Gate

다음 변경은 production 수동 승인 단계를 요구한다.

- DB migration
- auth/permission
- tenant boundary
- customer PII
- Detector/Score
- Measurement/Incrementality
- external channel execution
- AI provider 데이터 정책 영향
- secret/infrastructure
- API breaking/migration

초기 1인 개발에서도 자동 production push보다 확인 단계를 둔다.

---

# 8. Production Deploy

권장 순서:

```text
1. release artifact 고정
2. config/secret validation
3. backward-compatible migration
4. application deploy
5. health check
6. smoke test
7. metric/log 확인
8. release 기록
```

artifact는 Staging에서 검증한 동일 버전을 Production에 사용한다.

Production에서 다시 build하여 다른 결과물을 만들지 않는 방향을 권장한다.

---

# 9. Post-Deploy Checks

최소 관찰:

- error rate
- latency
- DB connection
- job failure
- import failure
- AI request failure/cost
- connector errors
- Detector candidate 급증/급감
- tenant isolation/security alert

Detector 변경 시 단순 서버 health만 보지 않는다.

분석 결과 분포 변화도 확인한다.

---

# 10. Rollback

코드 rollback과 데이터 rollback을 구분한다.

## Code

이전 안정 artifact로 되돌린다.

## Database

무조건 down migration을 실행하지 않는다.

데이터 손실 위험이 있다면 forward fix를 우선한다.

## Detector / AI

버전별 feature flag 또는 runtime config가 가능하면 이전 버전으로 되돌릴 수 있게 한다.

## External Action

이미 고객에게 발송/게시된 행동은 코드 rollback으로 취소되지 않을 수 있다.

Action 상태와 외부 execution reference를 이용해 별도 운영 대응한다.

---

# 11. Hotfix

긴급 수정:

```text
incident
→ short-lived hotfix branch
→ 최소 CI
→ 필수 review
→ production
→ main에 반드시 반영
→ 사후 기록
```

운영 서버만 직접 고치고 저장소에 반영하지 않는 방식을 금지한다.

---

# 12. Secret

금지:

- repository commit
- Docker image bake-in
- frontend bundle
- 로그 출력

사용:

- 환경별 secret store
- 최소 권한
- rotation 가능
- 접근 감사

실제 Secret Manager 제품은 추후 결정한다.

---

# 13. Feature Rollout

고위험 기능은 가능하면 단계 배포한다.

예:

```text
internal
→ selected test businesses
→ limited %
→ general
```

대상:

- 새 Detector
- Recommendation 전략
- 외부 자동 실행
- Measurement 방법
- 새 AI model route

---

# 14. Release Record

각 production release에 최소 기록:

```text
version/commit
deployed_at
migration
changed detectors
changed prompts/models
API changes
known limitations
rollback path
owner
```

과거 Opportunity/Recommendation을 재현하기 위해 Intelligence version 변경도 기록한다.

---

# 15. 배포 실패 기준

다음은 배포 실패로 간주한다.

- tenant 데이터 노출 가능성
- migration 오류
- 핵심 import 실패
- Opportunity 결과 비정상 급변
- API contract 위반
- 고객 승인 없는 외부 action 실행
- AI 응답이 deterministic 숫자를 오염
- secrets 노출

이 경우 새 기능 유지보다 rollback/disable을 우선한다.
