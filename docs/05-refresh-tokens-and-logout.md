# Phase 4 — Refresh Tokens, Rotation & Logout

## Concept

**Access tokens** are short-lived (15 min). **Refresh tokens** are long-lived opaque strings stored **hashed** in the DB. When access expires, the client exchanges a refresh token for a new access + refresh pair (**rotation**).

---

## Why refresh tokens?

| Problem | Solution |
|---------|----------|
| Long-lived JWT in browser = stolen token works for days | Short access JWT (15 min) |
| Short JWT = user logs in constantly | Refresh token gets new access silently |
| Stolen refresh token | Store hash in DB → revoke on logout / reuse detection |

---

## Refresh token model (`refresh_tokens` table)

| Column | Purpose |
|--------|---------|
| `token_hash` | SHA-256 of raw token (never store raw) |
| `user_id` | Owner |
| `expires_at` | TTL |
| `revoked` | Invalidated flag |
| `replaced_by` | Points to new token after rotation (audit trail) |

---

## Token helpers (`app/core/security.py`)

```python
def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_refresh_token() -> tuple[str, datetime]:
    raw = secrets.token_urlsafe(32)
    expires_at = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return raw, expires_at
```

Client gets **raw** token once. DB stores **hash** only.

---

## Refresh flow (rotation)

```
POST /auth/refresh
  Cookie: refresh_token=...  OR  body { refresh_token }
  Header: X-CSRF-Token: ...    (Phase 5)
        │
hash incoming token → lookup row
        │
If revoked → REUSE ATTACK → revoke ALL user tokens → 401
If expired → revoke row → 401
        │
Create NEW refresh row
Revoke OLD row (replaced_by = new id)
        │
Return new access + new refresh
Set cookies
```

### Reuse detection

If an attacker steals a refresh token and the real user already rotated it, the old token is `revoked`. Using it triggers **revoke_all_for_user** — forces re-login everywhere.

---

## Logout

| Endpoint | Auth | Action |
|----------|------|--------|
| `POST /auth/logout` | Refresh cookie + CSRF | Revoke one refresh row, clear cookies |
| `POST /auth/logout-all` | Bearer access JWT | Revoke all refresh tokens for user |

---

## Flow diagram

```
Login
  ├─ access JWT (15 min, stateless)
  └─ refresh opaque (7 days, DB row)

Access expires
  └─ POST /refresh → new pair, old refresh revoked

Logout
  └─ refresh row revoked, cookies cleared
```

---

## Interview points

1. **Why hash refresh tokens like passwords?** DB leak shouldn't give usable tokens.
2. **Rotation vs reuse?** Rotation = new token each refresh. Reuse of revoked token = possible theft → nuke all sessions.
3. **Why opaque refresh vs JWT refresh?** Server can revoke instantly; JWT refresh can't be revoked without a blocklist.

---

## Navigation

← [JWT](04-jwt-and-protected-routes.md) | [Security Hardening →](06-security-hardening.md)
