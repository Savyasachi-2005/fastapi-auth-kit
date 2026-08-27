# Security Best Practices & Production Checklist

## What you built (security features)

- [x] bcrypt password hashing
- [x] Short-lived JWT access tokens
- [x] Hashed refresh tokens with rotation
- [x] Refresh reuse detection → revoke all
- [x] httpOnly cookies for refresh + session
- [x] CSRF double-submit on cookie mutations
- [x] CORS with credentials
- [x] Rate limiting on auth endpoints
- [x] Email verification gate on login
- [x] One-time hashed tokens (verify, reset)
- [x] Password reset revokes all refresh tokens
- [x] RBAC permission checks
- [x] OAuth state parameter (CSRF)
- [x] Generic messages (no email enumeration)

---

## Production gaps (not yet in project)

| Item | Why | Recommendation |
|------|-----|----------------|
| **Alembic migrations** | `create_all` doesn't alter existing tables | Add Alembic; never `drop_all` in prod |
| **Real email** | Dev prints links | SendGrid, SES, Resend |
| **HTTPS** | Cookies/tokens over HTTP are sniffable | TLS everywhere; `COOKIE_SECURE=true` |
| **Strong SECRET_KEY** | Weak key = forged JWTs | `openssl rand -hex 32` |
| **Structured logging** | Debug auth failures | JSON logs, no passwords/tokens |
| **Account lockout** | Rate limit alone isn't enough | Temporary lock after N failures |
| **2FA / MFA** | Stolen password = full access | TOTP, WebAuthn |
| **Audit log** | Who deleted whom | Admin action table |
| **Token blocklist** | Instant JWT revoke | Redis denylist for access JWT |
| **Secrets manager** | `.env` in prod is fragile | AWS Secrets Manager, Vault |

---

## JWT vs Session — when to use what

| Scenario | Recommendation |
|----------|----------------|
| Public REST API + mobile apps | JWT Bearer |
| Same-site SSR web app | Session cookie |
| SPA on different domain | JWT + refresh in httpOnly cookie (your setup) |
| Need instant revoke on every request | Session or short JWT + blocklist |
| Microservices | JWT (shared secret or JWKS) |

---

## Cookie security recap

```
refresh_token  → httpOnly, Secure, SameSite=Lax, path=/auth
csrf_token     → NOT httpOnly (JS reads it), SameSite=Lax, path=/auth
session_id     → httpOnly, Secure, SameSite=Lax, path=/
oauth_state    → httpOnly, short TTL, path=/oauth
```

**SameSite=Lax** — blocks most CSRF; use `Strict` for higher security (may break some OAuth flows).

---

## Password rules

- Minimum 8 characters (increase to 12+ in production)
- Reject breached passwords (Have I Been Pwned API)
- OAuth-only users: `hashed_password=NULL`, reject password login

---

## OAuth security

- Never expose `GOOGLE_CLIENT_SECRET` to frontend
- Rotate client secret if leaked
- `redirect_uri` exact match in Console + `.env`
- Validate `state` on every callback

---

## Database security

- Use SSL (`sslmode=require`) for Supabase
- Least-privilege DB user (not superuser)
- Hash all opaque tokens at rest (refresh, session, verify, reset)

---

## Interview one-liner

> "I built defense in depth: hashed passwords, short JWTs, rotating hashed refresh tokens with reuse detection, CSRF on cookie endpoints, rate limits, RBAC, and OAuth with state validation — and I understand the tradeoffs between stateless JWT access and stateful session cookies."

---

## Navigation

← [API Reference](11-api-reference.md) | [README](../README.md)
