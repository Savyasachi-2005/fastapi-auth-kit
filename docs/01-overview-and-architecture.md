# Overview & Architecture

## What this project is

A **production-style authentication API** built with FastAPI, SQLAlchemy 2.0, PostgreSQL (Supabase), and Pydantic v2. It covers the full auth lifecycle: registration, login, JWT access tokens, refresh token rotation, cookies, CSRF, email verification, password reset, RBAC, Google OAuth, and classic session-cookie auth.

This is a **learning codebase** — you typed every line. The goal is to understand auth deeply enough to rebuild it from memory.

---

## Tech stack

| Layer | Technology |
|-------|------------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 (`Mapped`, `mapped_column`) |
| Database | PostgreSQL (Supabase) |
| Validation | Pydantic v2 |
| Password hashing | bcrypt |
| JWT | PyJWT |
| HTTP client (OAuth) | httpx |
| Rate limiting | slowapi |
| Server | uvicorn |

---

## Folder structure

```
app/
├── main.py                 # App entry, CORS, routers, create_all, RBAC seed
├── core/
│   ├── config.py           # Settings from .env (pydantic-settings)
│   ├── security.py         # bcrypt, JWT, token hashing
│   ├── cookies.py          # httpOnly refresh, CSRF, session cookies
│   ├── csrf.py             # Double-submit CSRF check
│   ├── rate_limit.py       # slowapi limiter
│   ├── tokens.py           # One-time token generators (verify, reset)
│   └── seed.py             # RBAC roles/permissions bootstrap
├── db/
│   └── session.py          # Engine, SessionLocal, Base
├── models/                 # SQLAlchemy tables
├── schemas/                # Pydantic request/response models
├── repo/                   # Database access (queries, CRUD)
├── services/               # Business logic
└── api/
    ├── deps.py             # get_db, get_current_user, require_permission
    └── routes/             # Thin HTTP handlers
```

### Why this layout?

| Layer | Responsibility |
|-------|----------------|
| **routes** | HTTP in/out only — parse body, call service, set cookies, return response |
| **services** | Business rules — login checks, token rotation, OAuth linking |
| **repo** | SQL only — no HTTP, no business decisions |
| **models** | Table shape |
| **schemas** | API contract (what clients send/receive) |
| **core** | Cross-cutting: config, crypto, cookies, CSRF |

---

## Request flow (general)

```
Client (browser / curl / mobile)
        │
        ▼
   FastAPI Router          ← rate limit, CORS
        │
        ▼
   Dependency injection    ← get_db, get_current_user, require_csrf
        │
        ▼
   Service layer           ← business logic
        │
        ▼
   Repo layer              ← SQLAlchemy queries
        │
        ▼
   PostgreSQL (Supabase)
```

---

## Two authentication styles in one app

| Style | Login endpoint | Credential on requests | Protected route |
|-------|----------------|------------------------|-----------------|
| **JWT** | `POST /auth/login` | `Authorization: Bearer <access_token>` | `GET /users/me` |
| **Session** | `POST /session/login` | `Cookie: session_id=...` | `GET /session/me` |

Both paths share the same `users` table and password verification. OAuth issues JWT + refresh (same as password login).

---

## Database tables

| Table | Purpose |
|-------|---------|
| `users` | Accounts (email, password hash, role, google_sub, flags) |
| `refresh_tokens` | Opaque refresh tokens (hashed), rotation, revoke |
| `auth_sessions` | Session-cookie auth (hashed session id) |
| `email_verification_tokens` | One-time email verify links |
| `password_reset_tokens` | One-time password reset links |
| `roles` | `user`, `admin` |
| `permissions` | `me:read`, `users:read`, `users:delete` |
| `role_permission` | Many-to-many join |

---

## Startup sequence (`main.py`)

1. Load settings from `.env`
2. `Base.metadata.create_all(bind=engine)` — create tables (dev only; use Alembic in production)
3. `seed_rbac()` — ensure roles and permissions exist
4. Register middleware (CORS) and routers
5. Attach rate limiter

---

## Environment variables

See `.env.example`. Key values:

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | `postgresql+psycopg://...` with `sslmode=require` for Supabase |
| `SECRET_KEY` | JWT signing key — must be strong in production |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Short-lived access JWT (default 15) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifetime (default 7) |
| `SESSION_EXPIRE_DAYS` | Session cookie lifetime (default 7) |
| `CORS_ORIGINS` | Comma-separated allowed frontend origins |
| `COOKIE_SECURE` | `true` in production (HTTPS only) |
| `GOOGLE_*` | OAuth client id, secret, redirect URI |

---

## Phases completed

| Phase | Topic |
|-------|-------|
| 1 | Foundation — config, DB, health |
| 2 | Registration + bcrypt |
| 3 | JWT login + protected routes |
| 4 | Refresh tokens + rotation + logout |
| 5 | CORS, cookies, CSRF, rate limiting |
| 6 | Email verification + password reset |
| 7 | RBAC (roles & permissions) |
| 8 | Google OAuth |
| 9 | Session-cookie auth |

---

## Next doc

→ [02 — Foundation](02-foundation.md)
