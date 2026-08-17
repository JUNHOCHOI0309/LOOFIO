-- Additive score provenance for reproducible Opportunity priority ordering.

ALTER TABLE opportunities
    ADD COLUMN score_version text NOT NULL DEFAULT 'legacy-unversioned-v0',
    ADD COLUMN score_breakdown jsonb;
