-- Additive human-managed Action plans. This schema does not contain an external execution connector or payload.

CREATE TABLE actions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    recommendation_id uuid NOT NULL REFERENCES recommendations(id),
    action_version text NOT NULL,
    status text NOT NULL DEFAULT 'planned' CHECK (status IN ('planned', 'in_progress', 'completed', 'cancelled')),
    action_type text NOT NULL,
    channel text NOT NULL,
    title text NOT NULL,
    execution_notes text,
    planned_start_at timestamptz NOT NULL,
    planned_end_at timestamptz,
    planned_budget jsonb,
    created_by_user_id uuid NOT NULL REFERENCES users(id),
    started_at timestamptz,
    completed_at timestamptz,
    cancelled_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id),
    UNIQUE (recommendation_id, action_version)
);

CREATE INDEX actions_tenant_business_status_idx ON actions (tenant_id, business_id, status, planned_start_at ASC);

CREATE TABLE action_status_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    business_id uuid NOT NULL,
    action_id uuid NOT NULL REFERENCES actions(id),
    status text NOT NULL CHECK (status IN ('planned', 'in_progress', 'completed', 'cancelled')),
    note text,
    changed_by_user_id uuid NOT NULL REFERENCES users(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (tenant_id, business_id) REFERENCES businesses(tenant_id, id)
);

CREATE INDEX action_status_events_action_created_idx ON action_status_events (action_id, created_at ASC);
