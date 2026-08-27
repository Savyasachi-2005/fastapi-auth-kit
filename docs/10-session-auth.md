# Phase 9 — Session-Cookie Authentication

## Concept

**Session auth** stores login state **on the server**. The browser gets an opaque `session_id` cookie; every request looks up that id in the database to find the user.

This contrasts with JWT access tokens, which are verified without a DB hit.

---

## JWT vs Session (summary)

| | JWT access | Session cookie |
|--|------------|----------------|
| Credential | `Authorization: Bearer` header | `session_id` httpOnly cookie |
| Server state | None (verify signature) | DB row per session |
| Revoke | Wait for expiry or blocklist | Delete/revoke row instantly |
| DB per request | No | Yes |
| Best for | APIs, mobile, SPAs | SSR sites, admin panels |

**Your app is a hybrid:** short JWT access + DB-backed refresh + optional session path for learning.

---

## AuthSession model (`auth_sessions` table)

| Column | Purpose |
|--------|---------|
| `session_hash` | SHA-256 of raw session id |
| `user_id` | Owner |
| `expires_at` | TTL |
| `revoked` | Logout flag |

Class name `AuthSession` — not `Session` (clashes with SQLAlchemy).

---

## Endpoints

| Method | Path | Action |
|--------|------|--------|
| POST | `/session/login` | Verify password → create row → set cookie |
| GET | `/session/me` | Cookie → DB lookup → return user |
| POST | `/session/logout` | Revoke row → clear cookie |

---

## Flow

```
POST /session/login
  { email, password }
        │
Same checks as JWT login (password, verified, active)
        │
create_session_id() → raw + expires_at
session_repo.create(session_hash=hash(raw))
        │
Set-Cookie: session_id=<raw>  (httpOnly, path=/)

GET /session/me
  Cookie: session_id=<raw>
        │
get_current_user_from_session (FastAPI Depends)
  request.cookies.get("session_id")
  get_user_for_session(db, raw)
        │
hash → lookup row → check revoked, expiry → load user
```

### Dependency injection

```python
@router.get("/me")
def session_me(current_user: User = Depends(get_current_user_from_session)):
    return current_user
```

You don't pass `request` in the route — FastAPI injects it into the dependency automatically.

---

## Logout

```
POST /session/logout
        │
hash cookie value → revoke row
clear_session_cookie(response)
```

After logout, `/session/me` returns 401.

---

## Testing on Windows PowerShell

`curl` is an alias for `Invoke-WebRequest`. Use **`curl.exe`** for cookie flags:

```powershell
curl.exe -c cookies.txt -X POST http://127.0.0.1:8000/session/login `
  -H "Content-Type: application/json" `
  -d "{\"email\":\"you@example.com\",\"password\":\"yourpass\"}"

curl.exe -b cookies.txt http://127.0.0.1:8000/session/me
```

Or use `Invoke-RestMethod -WebSession $session` to keep cookies in memory.

---

## Interview points

1. **Why hash session id in DB?** Same as refresh tokens — DB leak shouldn't give usable cookies.
2. **Why httpOnly on session_id?** XSS can't steal the cookie via JavaScript.
3. **When pick sessions over JWT?** Instant revoke, server-controlled sessions, traditional web apps.

---

## Navigation

← [Google OAuth](09-google-oauth.md) | [API Reference →](11-api-reference.md)
