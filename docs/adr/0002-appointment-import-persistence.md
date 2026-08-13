# ADR 0002: Appointment CSV persistence and idempotency

## Status

Accepted — 2026-08-13

## Context

Appointment CSV preview alone cannot create the Hospital MVP's normalized data foundation. Persisted imports need source lineage, tenant/business isolation, and protection against retry-driven duplicates.

## Decision

- A CSV is validated and normalized deterministically before any domain write.
- Invalid rows reject the whole persistence request; the preview endpoint remains available for row-level correction.
- `import_jobs` records the file hash, idempotency key, and import counts. `import_rows` stores only an allowlisted source payload plus normalized payload and outcome.
- Appointments use the existing `(tenant_id, business_id, source_system, source_record_id)` uniqueness boundary. Re-upload under a new idempotency key records duplicate outcomes without duplicating appointments.
- The request's signed server session supplies the active tenant. Every business/import query includes tenant and business scope.
- The first implementation accepts businesses with exactly one registered location. It retains `location_key` as source lineage, but rejects multi-location imports until explicit external-location mapping is introduced.

## Consequences

- Existing CSV contracts remain compatible; optional fields are validated when supplied.
- The migration is additive. Rollback is a forward fix: do not drop import history in a shared or production database.
- Raw payload retention is intentionally allowlisted to avoid persisting unexpected plaintext personal data from arbitrary CSV columns.
