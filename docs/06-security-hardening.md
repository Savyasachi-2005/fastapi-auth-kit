# Phase 5 — Security Hardening

## Concept

Production auth needs more than login/logout: **CORS** for browsers, **httpOnly cookies** for refresh tokens, **CSRF** protection for cookie-based mutations, and **rate limiting** against brute force.

---

## CORS (`main.py`)

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,   # required for cookies
    allow_methods=["*"],
    allow_headers=["*"],
)
```

| Setting | Why |
|---------|-----|
| `allow_origins` | Only your frontend domains |
| `allow_credentials=True` | Browser sends cookies cross-origin |

Frontend must use `credentials: "include"` in fetch.

---

## Cookies (`app/core/cookies.py`)

| Cookie | httpOnly | Path | Purpose |
|--------|----------|------|---------|
| `refresh_token` | Yes | `/auth` | Refresh token (not readable by JS) |
| `csrf_token` | No | `/auth` | CSRF double-submit (JS must read it) |
| `session_id` | Yes | `/` | Session auth (Phase 9) |

```python
response.set_cookie(
    key="refresh_token",
    value=raw_refresh,
    httponly=True,
    secure=COOKIE_SECURE,      # True in production (HTTPS)
    samesite=COOKIE_SAMESITE,  # "lax" or "strict"
    max_age=...,
    path="/auth",
)
```

**Cookie path matters** — refresh cookie at `/auth` is only sent to `/auth/*` routes. OAuth state cookie must match callback path (`/oauth`).

---

## CSRF — double submit (`app/core/csrf.py`)

When refresh token is in an httpOnly cookie, attackers can trick browsers into sending it (CSRF). Fix:

1. Server sets `csrf_token` cookie (readable by JS)
2. Client sends same value in `X-CSRF-Token` header
3. Server compares cookie vs header

```python
def require_csrf(request, x_csrf_token: str = Header(...)):
    cookie = request.cookies.get("csrf_token")
    if cookie != x_csrf_token:
        raise HTTPException(403, "CSRF check failed")
```

Protected routes: `POST /auth/refresh`, `POST /auth/logout`.

**Attackers can't read your cookies from another origin** (same-origin policy) — so they can't forge the header.

---

## Rate limiting (`app/core/rate_limit.py`)

```python
limiter = Limiter(key_func=get_remote_address)

@router.post("/login")
@limiter.limit("5/minute")
def login(...):
```

Slows brute-force password guessing and token spam.

---

## Security checklist (dev vs prod)

| Item | Dev | Production |
|------|-----|------------|
| `COOKIE_SECURE` | `false` | `true` |
| `SECRET_KEY` | any string | 32+ random bytes |
| HTTPS | optional | required |
| CORS origins | localhost | real domain only |
| Rate limits | 5/min | tune per endpoint |

---

## Interview points

1. **httpOnly vs secure vs samesite?** httpOnly = no JS access; secure = HTTPS only; samesite = cross-site send policy.
2. **Why CSRF only on cookie endpoints?** Bearer tokens in headers aren't auto-sent by browsers — CSRF is a cookie problem.
3. **Why rate limit login?** Password guessing is cheap at scale.

---

## Navigation

← [Refresh Tokens](05-refresh-tokens-and-logout.md) | [Account Flows →](07-account-flows.md)
