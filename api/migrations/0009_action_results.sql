-- Additive, human-recorded results for completed Actions. Measurement is calculated deterministically from appointment data.

CREATE TABLE action_results (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id uuid NOT NULL,
    action_id uuid NOT NULL REFERENCES actions(id),
    result_version text NOT NULL,
    execution_summary text NOT NULL,
    measurement_start_at timestamptz NOT NULL,
    measurement_end_at timestamptz NOT NULL,
    actual_spend jsonb,
    outcome_notes text,
    recorded_by_user_id uuid NOT NULL REFERENCES users(id),
    recorded_at timestamptz NOT NULL DEFAULT now(),
    CHECK (measurement_end_at > measurement_start_at),
    UNIQUE (action_id, result_version)
);

CREATE INDEX action_results_tenant_action_idx ON action_results (tenant_id, action_id);
