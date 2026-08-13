# ADR 0001 — Direct OAuth authentication

- Status: Accepted
- Date: 2026-08-13

## Context

LOOFIO Hospital MVP requires Google and Naver login. User identity, Tenant membership, and provider account are separate concerns. The product requires the FastAPI backend to own authorization decisions and tenant isolation.

## Decision

Use provider-hosted OAuth 2.0 Authorization Code flows with the FastAPI API as the confidential client and callback handler.

- Google: OpenID Connect scopes `openid email profile`
- Naver: Naver Login profile endpoint
- Callback state is held in a signed, `HttpOnly`, `SameSite=Lax` session cookie.
- The API redirects to the frontend only after processing the callback, so authorization codes are not exposed to frontend routes.
- Store only provider, provider subject, and optional profile details needed for account linking. Do not persist provider access or refresh tokens for login.
- Persist user and Tenant membership through the `users`, `user_identities`, and `tenant_members` tables. Tenant authorization remains a server-side check.

## Consequences

- OAuth Client IDs and Secrets must be registered in Google Cloud and NAVER Developers and supplied through environment-specific secret storage.
- Every environment requires a distinct high-entropy `SESSION_SECRET`. `SESSION_COOKIE_SECURE` is false only for local HTTP and must be true in HTTPS production.
- OAuth provider redirects must match the configured callback exactly.
- This decision does not authorize external marketing actions; approval requirements remain unchanged.

## References

- [Google OAuth web server flow](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Google OpenID Connect reference](https://developers.google.com/identity/openid-connect/reference)
- [NAVER Developers](https://developers.naver.com/main/)
