-- Direct OAuth identity mapping. This migration is additive.
-- Tokens are deliberately not stored; LOOFIO only needs the provider subject for sign-in.

CREATE TABLE user_identities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id),
    provider text NOT NULL CHECK (provider IN ('google', 'naver')),
    provider_subject text NOT NULL,
    email_at_link_time text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    UNIQUE (provider, provider_subject),
    UNIQUE (user_id, provider)
);
