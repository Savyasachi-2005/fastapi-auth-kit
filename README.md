# AuthAPI — FastAPI Authentication Learning Project

A full-stack **authentication system** built step-by-step with FastAPI, SQLAlchemy 2.0, PostgreSQL (Supabase), and Pydantic v2. Covers registration, JWT, refresh tokens, cookies, CSRF, email verification, password reset, RBAC, Google OAuth, and session-cookie auth.

---

## Quick start

```powershell
# 1. Clone / open project
cd G:\FastAPI\Auth

# 2. Virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env — set DATABASE_URL, SECRET_KEY, FRONTEND_URL, GOOGLE_* 

# 5. Run server
uvicorn app.main:app --reload --port 8000
```

- **API docs:** http://127.0.0.1:8000/docs  
- **Health:** http://127.0.0.1:8000/health  
- **DB check:** http://127.0.0.1:8000/ready  

---

## Documentation (read in order)

Deep-dive notes for each phase. Start with overview, then follow the chain.

| # | Document | Topics |
|---|----------|--------|
| 1 | [Overview & Architecture](docs/01-overview-and-architecture.md) | Stack, folder structure, request flow, DB tables |
| 2 | [Foundation](docs/02-foundation.md) | Config, DB session, health endpoints, Supabase |
| 3 | [Registration & Passwords](docs/03-registration-and-passwords.md) | User model, bcrypt, `POST /auth/register` |
| 4 | [JWT & Protected Routes](docs/04-jwt-and-protected-routes.md) | Login, access tokens, `get_current_user` |
| 5 | [Refresh Tokens & Logout](docs/05-refresh-tokens-and-logout.md) | Rotation, reuse detection, logout-all |
| 6 | [Security Hardening](docs/06-security-hardening.md) | CORS, cookies, CSRF, rate limiting |
| 7 | [Account Flows](docs/07-account-flows.md) | Email verification, password reset |
| 8 | [RBAC](docs/08-rbac.md) | Roles, permissions, admin routes |
| 9 | [Google OAuth](docs/09-google-oauth.md) | Authorization code flow, account linking |
| 10 | [Session Auth](docs/10-session-auth.md) | Cookie sessions vs JWT comparison |
| 11 | [API Reference](docs/11-api-reference.md) | All endpoints, status codes, examples |
| 12 | [Security Best Practices](docs/12-security-best-practices.md) | Production checklist, interview summary |

---

## Architecture at a glance

```
app/
├── main.py              # Entry point, routers, create_all, RBAC seed
├── core/                # Config, security, cookies, CSRF, rate limit
├── db/                  # SQLAlchemy engine & session
├── models/              # Database tables
├── schemas/             # Pydantic request/response
├── repo/                # Data access layer
├── services/            # Business logic
└── api/
    ├── deps.py          # Dependencies (auth, permissions)
    └── routes/          # HTTP handlers
```

```
Client → Router → Depends (auth, db) → Service → Repo → PostgreSQL
```

---

## Auth methods in this project

| Method | Login | Credential | Profile endpoint |
|--------|-------|------------|------------------|
| **JWT** | `POST /auth/login` | `Authorization: Bearer` | `GET /users/me` |
| **Session** | `POST /session/login` | `session_id` cookie | `GET /session/me` |
| **Google OAuth** | `GET /oauth/google/login` | → issues JWT + refresh | `GET /users/me` |

---

## Key endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /auth/register` | Create account |
| `POST /auth/login` | Password login → JWT |
| `POST /auth/refresh` | Rotate refresh token |
| `POST /auth/logout` | Revoke refresh token |
| `GET /users/me` | Current user (JWT) |
| `GET /admin/users` | List users (RBAC) |
| `GET /oauth/google/login` | Google sign-in (browser) |
| `POST /session/login` | Session cookie login |
| `GET /session/me` | Current user (session) |

Full list → [API Reference](docs/11-api-reference.md)

---

## Environment variables

Copy `.env.example` to `.env`. Required:

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | `postgresql+psycopg://...?sslmode=require` |
| `SECRET_KEY` | JWT signing key |
| `FRONTEND_URL` | Base URL for email links |
| `GOOGLE_CLIENT_ID` | OAuth client id |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_REDIRECT_URI` | Must match Google Console |

See [Overview — Environment](docs/01-overview-and-architecture.md#environment-variables) for full list.

---

## Tech stack

- **FastAPI** — web framework  
- **SQLAlchemy 2.0** — ORM  
- **PostgreSQL** (Supabase) — database  
- **Pydantic v2** — validation  
- **bcrypt** — password hashing  
- **PyJWT** — access tokens  
- **httpx** — Google OAuth HTTP  
- **slowapi** — rate limiting  

---

## Learning path (phases 1–9)

All phases complete. Each doc maps to one phase:

1. Foundation → 2. Register → 3. JWT → 4. Refresh → 5. Hardening → 6. Account flows → 7. RBAC → 8. OAuth → 9. Sessions

Mentor continuity file: [`memory.md`](memory.md)  
Original teaching rules: [`preparation.md`](preparation.md)

---

## Testing tips (Windows)

PowerShell `curl` is not real curl. Use:

```powershell
curl.exe -c cookies.txt -X POST http://127.0.0.1:8000/session/login -H "Content-Type: application/json" -d "{\"email\":\"you@example.com\",\"password\":\"pass\"}"
```

JWT login:

```powershell
curl.exe -X POST http://127.0.0.1:8000/auth/login -H "Content-Type: application/json" -d "{\"email\":\"you@example.com\",\"password\":\"pass\"}"
```

Use the `access_token` from the response:

```powershell
curl.exe http://127.0.0.1:8000/users/me -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```



## License

Learning project — use and modify freely.
