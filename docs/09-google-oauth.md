# Phase 8 — Google OAuth

## Concept

**OAuth 2.0 authorization code flow** lets users sign in with Google. Your server exchanges a one-time `code` for Google tokens, reads user profile, then issues **your own** JWT + refresh (same as password login).

Google proves identity — your app still owns sessions and permissions.

---

## Why authorization code flow?

| Approach | Problem |
|----------|---------|
| Implicit / frontend-only | Client secret can't stay secret; tokens exposed to XSS |
| **Authorization code** | Code exchanged server-side with `client_secret`; browser never sees secret |

---

## Config

`.env`:

```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=http://127.0.0.1:8000/oauth/google/callback
```

Google Cloud Console:
- OAuth 2.0 Client (Web application)
- Redirect URI must **exactly** match `.env` (`127.0.0.1` vs `localhost` matters)
- Consent screen: Testing = test users only; Production = any Google account

---

## Endpoints

| Method | Path | Action |
|--------|------|--------|
| GET | `/oauth/google/login` | Generate `state`, set cookie, redirect to Google |
| GET | `/oauth/google/callback` | Verify state, exchange code, login/register, return tokens |

**Don't test login in Swagger** — it 302 redirects to Google. Use a real browser.

---

## Flow

```
Browser → GET /oauth/google/login
       → Set-Cookie: oauth_state=random (path=/oauth)
       → 302 Google consent screen
       → User approves
       → GET /oauth/google/callback?code=...&state=...
       → Verify cookie state == query state (CSRF protection)
       → POST https://oauth2.googleapis.com/token (NOT auth URL)
       → GET Google userinfo (sub, email)
       → login_or_register_with_google()
       → Return access + refresh + set cookies
```

---

## Find-or-create user (`app/services/oauth_google.py`)

| Step | Condition | Action |
|------|-----------|--------|
| 1 | `google_sub` exists in DB | Login |
| 2 | Email exists, no conflicting `google_sub` | Link `google_sub`, set `is_verified=True`, keep password hash |
| 3 | New email | Create user (`hashed_password=None`, `is_verified=True`) |

### Linking (password user + Google same email)

One user row — both login methods work:
- Password login: `hashed_password` still set
- Google login: matches `google_sub`

### Conflicts

- Email already linked to **different** `google_sub` → 400
- `google_sub` already on **another** user → 400

### OAuth-only users

`hashed_password = NULL` — password login must reject with generic "Invalid credentials".

---

## OAuth `state` parameter

Random value stored in httpOnly cookie before redirect. On callback, compare cookie vs query param.

**Prevents login CSRF** — attacker can't drop their Google `code` on your callback and hijack a session.

**Cookie path** must cover callback URL (`path="/oauth"`).

---

## Key URLs

| Purpose | URL |
|---------|-----|
| Auth (redirect user) | `https://accounts.google.com/o/oauth2/v2/auth` |
| Token exchange | `https://oauth2.googleapis.com/token` |
| Userinfo | `https://www.googleapis.com/oauth2/v3/userinfo` |

Common bug: POSTing code to auth URL instead of token URL.

---

## Why issue your own tokens?

Google's access token is for **Google APIs**, not your RBAC/permissions/revoke model. Your JWT + refresh = one auth system for password + OAuth users.

---

## Interview points

1. **Why store `google_sub` not just email?** `sub` is stable; email can change.
2. **Why hash nothing for Google tokens in DB?** You don't store Google tokens — you use them once to get profile, then issue yours.
3. **redirect_uri exact match?** Google security — prevents code interception to attacker's app.

---

## Navigation

← [RBAC](08-rbac.md) | [Session Auth →](10-session-auth.md)
