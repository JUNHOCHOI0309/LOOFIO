-- Additive, tenant-scoped reusable mappings from an external CSV header to Hospital Appointment v1 fields.

CREATE TABLE appointment_import_mappings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    name text NOT NULL,
    column_mapping jsonb NOT NULL,
    status_mapping jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (tenant_id, business_id, name)
);

CREATE INDEX appointment_import_mappings_tenant_business_idx
    ON appointment_import_mappings (tenant_id, business_id, updated_at DESC);
