# LOOFIO Deployment Flow v2

- 기준일: 2026-08-18
- 기준 커밋: `0c75e524af5e9baa896e5685103ce8afe858b5a0`
- 상태: 현재 GitHub Actions CI + 목표 Staging/Production Gate

## 1. 현재 상태

현재 구현:

```text
GitHub Actions Regression checks
backend tests
sample pack product loop
web typecheck/build
main / feature / fix / test / ci push checks
```

아직 미구현:

```text
Staging
Production deploy
Managed secret
Production migration runner
Monitoring
Backup/restore automation
External channel execution
```

---

# 2. 환경

목표:

```text
Local / Test
→ Preview(optional)
→ Staging
→ Production
```

Staging과 Production은 DB·secret·OAuth callback·external account를 분리한다.

운영 환자·고객 원문 데이터를 Staging에 그대로 복사하지 않는다.

---

# 3. Git Flow

## 현재 1인 개발 흐름

```text
feature/fix branch
→ local test
→ branch push
→ GitHub Actions regression
→ local --no-ff merge to main
→ main push
→ GitHub Actions regression
→ branch delete
```

현재 Pull Request는 필수 절차가 아니다. 상세 명령은 `main_feature_git_workflow.md`를 따른다.

## 목표 협업·배포 흐름

```text
feature/fix branch
→ Pull Request
→ CI
→ Logical Owner Review
→ main
→ Staging deploy
→ Smoke / Intelligence Regression
→ Production approval
→ Production deploy
```

Production 연결 전에는 목표 흐름을 현재 배포 기능으로 표현하지 않는다.

---

# 4. Pull Request Gate

공통:

- backend tests
- frontend typecheck/build
- lint/static check
- migration ordering/validation
- tenant isolation
- API contract
- security/dependency scan
- sample-data regression

Decision Intelligence 변경 시 추가:

- Cause evidence fixture
- cause-not-fact test
- Strategy alternative/rank fixture
- `NO_ACTION` / `DATA_COLLECTION` case
- Playbook applicability/contraindication
- Economics unknown/zero
- Experiment completeness
- Evidence Grade
- Recommendation Quality score
- Hard Fail
- AI invented numeric value = 0
- legacy Recommendation/Action compatibility

---

# 5. Migration Gate

Safe additive:

```text
new nullable table/column
new version field
new index
new optional API relation
```

Risky:

```text
rename/type change
NOT NULL on existing rows
drop
large backfill
FK rewrite
legacy Recommendation/Action relation replacement
```

Risky migration은 expand/contract로 나눈다.

Decision Intelligence entity 추가 시 확인:

```text
tenant/business FK
version
source refs
status
audit
idempotency
retention
rollback/forward-fix
```

---

# 6. Intelligence Compatibility Gate

다음 version 변경을 별도로 검토한다.

```text
metric
detector
opportunity score
cause analysis
cause score
strategy mapping/score
playbook
experiment template
recommendation package
quality validator
AI prompt/model route
channel contract
measurement method
```

새 version이 과거 record를 조용히 재해석하지 않는지 확인한다.

---

# 7. Staging Smoke

최소:

```text
Health
OAuth / Session
Tenant isolation
Migration
CSV inspect / preview / import
Mapping reuse
Metrics
4 Detectors
Opportunity refresh / score
Legacy Recommendation / Decision
Manual Action / Result / Measurement
```

Decision Intelligence 구현 후 추가:

```text
Cause Analysis
Strategy alternatives
Playbook resolution
Experiment draft
Recommendation Package
Quality Gate
Fallback
```

---

# 8. Recommendation Quality Release Gate

다음 중 하나라도 실패하면 Recommendation v2 rollout을 중단한다.

- numeric evidence mismatch
- cause fact assertion
- Quality Hard Fail bypass
- target/period/budget/metric 누락
- unknown economics→0
- Playbook contraindication 위반
- Experiment success/stop 누락
- Hospital policy violation
- cross-tenant context
- legacy flow regression

---

# 9. Production Approval

수동 승인 필수:

- DB migration
- auth/session
- tenant
- PII/AI context
- Detector/Score
- Cause/Strategy rules
- Playbook ACTIVE 승격
- Quality weight/threshold
- Experiment/Measurement method
- external action
- secret/infrastructure
- API compatibility

---

# 10. Production Deploy 순서

```text
1. immutable artifact
2. config/secret validation
3. compatible migration
4. backend deploy
5. frontend deploy
6. health
7. smoke
8. intelligence distribution check
9. logs/metrics
10. release record
```

Staging에서 검증한 동일 artifact를 사용한다.

---

# 11. Post-Deploy Monitoring

기본:

- error/latency
- DB/session
- import failure
- Detector candidate distribution
- Opportunity count/score distribution
- Action/Result/Measurement failure
- tenant/security alert

Decision Intelligence:

- Cause run failure
- top cause distribution
- Strategy rank distribution
- no-action rate
- Playbook selection
- Quality pass/reject/hard fail
- AI failure/cost
- numeric mismatch
- package acceptance/modification
- result connection

변화가 크면 제품 개선으로 단정하지 않고 regression 여부를 먼저 확인한다.

---

# 12. Feature Rollout

```text
disabled
→ internal fixtures
→ selected test businesses
→ pilot
→ limited rollout
→ general
```

Playbook도 별도 상태를 가진다.

```text
DRAFT
VALIDATED_INTERNAL
PILOT
ACTIVE
```

새 Playbook을 전체 tenant에 즉시 활성화하지 않는다.

---

# 13. Rollback / Disable

코드:

- 이전 artifact

DB:

- destructive down migration보다 forward-fix 우선

Intelligence:

- version/feature flag로 이전 rule·Playbook·Quality validator
- new package generation disable
- legacy deterministic recommendation fallback

AI:

- provider disable
- deterministic template fallback

External Action:

- 이미 발송·게시된 결과는 코드 rollback으로 취소되지 않음
- execution reference와 운영 절차로 대응

---

# 14. Release Record

필수:

```text
commit / artifact
deployed_at
migration
API change
metric/detector/score version
cause/strategy version
playbook additions/status
experiment version
recommendation package version
quality validator version
AI provider/model/prompt
measurement method
known limitations
rollout scope
rollback/disable path
owner
```

---

# 15. 배포 실패 기준

- tenant/PII 노출
- migration failure
- import corruption
- deterministic numeric mismatch
- Quality Gate bypass
- generic recommendation final 노출
- policy violation
- unapproved external execution
- API contract violation
- secret exposure
- result/measurement semantic corruption

새 기능 유지보다 disable/rollback을 우선한다.

---

# 16. Hotfix

```text
incident
→ hotfix branch
→ minimum CI
→ mandatory review
→ deploy
→ main 반영
→ postmortem / release record
```

운영만 직접 수정하고 repository에 반영하지 않는 방식을 금지한다.
