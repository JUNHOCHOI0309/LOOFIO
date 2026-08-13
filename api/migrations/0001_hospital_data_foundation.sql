-- LOOFIO Hospital MVP: additive initial data foundation.
-- Apply through the deployment migration workflow; never run ad hoc against production.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE tenants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email text NOT NULL UNIQUE,
    display_name text,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE tenant_members (
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    user_id uuid NOT NULL REFERENCES users(id),
    role text NOT NULL CHECK (role IN ('owner', 'admin', 'marketer', 'viewer')),
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (tenant_id, user_id)
);

CREATE TABLE businesses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL REFERENCES tenants(id),
    name text NOT NULL,
    medical_domain text NOT NULL,
    timezone text NOT NULL DEFAULT 'Asia/Seoul',
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (tenant_id, id)
);

CREATE TABLE locations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    name text NOT NULL,
    timezone text NOT NULL DEFAULT 'Asia/Seoul',
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (tenant_id, id)
);

CREATE TABLE offerings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    name text NOT NULL,
    offering_type text,
    price_mode text NOT NULL DEFAULT 'variable' CHECK (price_mode IN ('fixed', 'insured', 'variable')),
    list_price numeric(14, 2),
    duration_minutes integer CHECK (duration_minutes > 0),
    active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (tenant_id, id)
);

CREATE TABLE customers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    external_customer_token text NOT NULL,
    first_seen_at timestamptz,
    last_seen_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (tenant_id, business_id, external_customer_token),
    UNIQUE (tenant_id, id)
);

CREATE TABLE import_jobs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    source_system text NOT NULL,
    source_filename text NOT NULL,
    schema_version text NOT NULL DEFAULT 'hospital-import-v1',
    status text NOT NULL CHECK (status IN ('pending', 'validated', 'processing', 'completed', 'failed')),
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (tenant_id, id)
);

CREATE TABLE appointments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    location_id uuid,
    customer_id uuid,
    offering_id uuid,
    import_job_id uuid,
    source_system text NOT NULL,
    source_record_id text NOT NULL,
    visit_start_at timestamptz NOT NULL,
    visit_end_at timestamptz,
    offering_name text NOT NULL,
    status text NOT NULL CHECK (status IN ('booked', 'completed', 'cancelled', 'no_show', 'unknown')),
    paid_amount numeric(14, 2),
    currency char(3) NOT NULL DEFAULT 'KRW',
    schema_version text NOT NULL DEFAULT 'hospital-v1',
    ingested_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    FOREIGN KEY (tenant_id, location_id) REFERENCES locations(tenant_id, id),
    FOREIGN KEY (tenant_id, customer_id) REFERENCES customers(tenant_id, id),
    FOREIGN KEY (tenant_id, offering_id) REFERENCES offerings(tenant_id, id),
    FOREIGN KEY (tenant_id, import_job_id) REFERENCES import_jobs(tenant_id, id),
    UNIQUE (tenant_id, business_id, source_system, source_record_id)
);

CREATE INDEX appointments_tenant_business_visit_idx
    ON appointments (tenant_id, business_id, visit_start_at);
