-- Additive persistence for normalized appointment CSV imports.
-- Raw row payloads retain source lineage; normalized values remain in domain tables.

ALTER TABLE import_jobs
    ADD COLUMN idempotency_key text,
    ADD COLUMN content_sha256 text,
    ADD COLUMN total_rows integer NOT NULL DEFAULT 0,
    ADD COLUMN imported_rows integer NOT NULL DEFAULT 0,
    ADD COLUMN duplicate_rows integer NOT NULL DEFAULT 0,
    ADD COLUMN invalid_rows integer NOT NULL DEFAULT 0,
    ADD COLUMN completed_at timestamptz;

CREATE UNIQUE INDEX import_jobs_tenant_business_idempotency_idx
    ON import_jobs (tenant_id, business_id, idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE TABLE import_rows (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    import_job_id uuid NOT NULL REFERENCES import_jobs(id),
    row_number integer NOT NULL CHECK (row_number > 0),
    raw_payload jsonb NOT NULL,
    normalized_payload jsonb NOT NULL,
    outcome text NOT NULL CHECK (outcome IN ('imported', 'duplicate')),
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (import_job_id, row_number)
);

CREATE INDEX import_rows_tenant_business_job_idx
    ON import_rows (tenant_id, business_id, import_job_id);
