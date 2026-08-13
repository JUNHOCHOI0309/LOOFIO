-- Additive persistence for deterministic low-demand Opportunity observations.

CREATE TABLE opportunities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    opportunity_type text NOT NULL CHECK (opportunity_type IN ('LOW_DEMAND_SLOT')),
    status text NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved', 'dismissed')),
    detector_code text NOT NULL,
    detector_version text NOT NULL,
    natural_key text NOT NULL,
    segment jsonb NOT NULL,
    observation jsonb NOT NULL,
    estimate jsonb,
    score numeric(5, 2) NOT NULL,
    confidence numeric(4, 3) NOT NULL,
    limitations jsonb NOT NULL,
    first_detected_at timestamptz NOT NULL DEFAULT now(),
    last_detected_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (tenant_id, business_id, detector_code, detector_version, natural_key)
);

CREATE INDEX opportunities_tenant_business_status_idx
    ON opportunities (tenant_id, business_id, status, last_detected_at DESC);

CREATE TABLE opportunity_evidence (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    opportunity_id uuid NOT NULL REFERENCES opportunities(id),
    evidence_hash text NOT NULL,
    evidence_type text NOT NULL,
    payload jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (opportunity_id, evidence_hash)
);
