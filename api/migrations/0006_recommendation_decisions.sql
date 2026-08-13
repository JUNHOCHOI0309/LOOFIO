-- Additive Recommendation drafts and human decision audit trail. No external action is created by this schema.

CREATE TABLE recommendations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    opportunity_id uuid NOT NULL REFERENCES opportunities(id),
    recommendation_version text NOT NULL,
    status text NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'approved', 'rejected', 'modified', 'later')),
    hypothesis text NOT NULL,
    action_type text NOT NULL,
    channel text NOT NULL,
    target_segment jsonb NOT NULL,
    expected_effect jsonb,
    confidence numeric(4, 3) NOT NULL,
    explanation text NOT NULL,
    limitations jsonb NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (opportunity_id, recommendation_version)
);

CREATE INDEX recommendations_tenant_opportunity_idx
    ON recommendations (tenant_id, opportunity_id, created_at ASC);

CREATE TABLE recommendation_decisions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    recommendation_id uuid NOT NULL REFERENCES recommendations(id),
    decision text NOT NULL CHECK (decision IN ('approved', 'rejected', 'modified', 'later')),
    reason_code text,
    reason_text text,
    modified_payload jsonb,
    decided_by_user_id uuid NOT NULL REFERENCES users(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id)
);

CREATE INDEX recommendation_decisions_recommendation_created_idx
    ON recommendation_decisions (recommendation_id, created_at DESC);
