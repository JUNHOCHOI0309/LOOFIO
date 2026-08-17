# Database migrations

Migration files are ordered, append-only PostgreSQL scripts. Apply them through the deployment pipeline using a database role with migration-only permissions.

Do not execute schema changes manually in an environment that contains shared or production data. The first migration is additive and creates the tenant-scoped Hospital MVP foundation.

`0011_version_opportunity_scores.sql`은 기존 점수를 재계산하지 않고 버전과 구성요소 컬럼만 추가한다. 애플리케이션 배포 전에 migration을 적용한다.
