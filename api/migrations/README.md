# Database migrations

Migration files are ordered, append-only PostgreSQL scripts. Apply them through the deployment pipeline using a database role with migration-only permissions.

Do not execute schema changes manually in an environment that contains shared or production data. The first migration is additive and creates the tenant-scoped Hospital MVP foundation.
