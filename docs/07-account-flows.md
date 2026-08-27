# Phase 6 — Email Verification & Password Reset

## Concept

Two **one-time token** flows:

1. **Email verification** — prove the user owns the email before login
2. **Password reset** — secure way to set a new password without knowing the old one

Both use the same pattern: generate random token → store **hash** in DB → send **raw** token via email (dev: `print` to console).

---

## Shared token pattern

```
Generate: raw = secrets.token_urlsafe(32)
Store:    token_hash = SHA-256(raw)
Send:     link with raw token (email or console)
Verify:   hash(incoming) → lookup row → check expiry + revoked
Use once: revoke row after success
```

Files: `app/core/tokens.py`, `app/core/security.py` (`hash_token`).

---

## Email verification

### Request link

```
POST /auth/verify-email
  { "email": "user@example.com" }
        │
If user exists AND not verified:
  create email_verification_tokens row
  send_verification_email(email, raw_token)
        │
Always return: "If that email exists, we sent a verification link."
```

**Never reveal** whether an email is registered (prevents enumeration).

### Confirm

```
GET /auth/verify-email/{token}
        │
hash(token) → lookup row
Check not revoked, not expired
        │
user.is_verified = True
revoke token row
```

### Login gate

`login_user` rejects unverified users with `403 Please verify your email`.

---

## Password reset

### Request reset

```
POST /auth/forgot-password
  { "email": "..." }
        │
If user exists:
  create password_reset_tokens row
  send_password_reset_email(email, raw_token)
        │
Return generic message
```

### Reset password

```
POST /auth/reset-password
  { "token": "...", "new_password": "..." }
        │
hash(token) → lookup row
Check expiry, not revoked
        │
user.hashed_password = hash_password(new_password)
revoke reset token
revoke_all refresh tokens (force re-login everywhere)
```

**Revoking all refresh tokens** after password reset is critical — old sessions must die.

---

## Email service (`app/services/email.py`)

Dev mode prints links to console:

```
Verify: {FRONTEND_URL}/verify?token=...
Reset:  {FRONTEND_URL}/reset?token=...
```

Production: swap for SendGrid, SES, Resend, etc.

---

## Tables

| Table | Columns (key) |
|-------|---------------|
| `email_verification_tokens` | user_id, token_hash, expires_at, revoked |
| `password_reset_tokens` | user_id, token_hash, expires_at, revoked |

---

## Interview points

1. **Why hash one-time tokens?** Same reason as refresh — DB leak shouldn't give usable links.
2. **Why generic "email sent" message?** Prevents attackers from discovering registered emails.
3. **Why revoke refresh on password reset?** Attacker with stolen session shouldn't keep access after victim resets password.

---

## Navigation

← [Security Hardening](06-security-hardening.md) | [RBAC →](08-rbac.md)
