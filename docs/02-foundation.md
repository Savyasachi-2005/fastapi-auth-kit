# Phase 1 — Foundation

## Concept

The **foundation** is everything auth sits on: virtual environment, dependencies, folder layout, configuration, database connection, and health endpoints. No auth logic yet — just proof the app boots and talks to Postgres.

---

## Why it matters

Without clean separation of config, DB, and routes, every new feature becomes a tangle. Production apps always isolate:

- **Secrets** → environment variables
- **DB wiring** → one module
- **HTTP surface** → thin routers

---

## Key files

### `app/core/config.py`

Uses **pydantic-settings** to load `.env`:

```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    # ...
```

`@lru_cache()` on `get_settings()` ensures settings are read once per process.

**Why pydantic-settings?** Type validation, defaults, and `extra="ignore"` so unknown env vars don't crash the app.

### `app/db/session.py`

```python
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
```

| Piece | Role |
|-------|------|
| **Engine** | Connection pool to Postgres |
| **SessionLocal** | Factory for per-request sessions |
| **Base** | Declarative base for all models |

`pool_pre_ping=True` — tests connections before use (avoids stale connections after DB restarts).

### `app/api/deps.py` — `get_db()`

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

**One session per request.** Never share a global session across concurrent requests — that causes transaction leaks and race conditions.

### Health routes (`app/api/routes/health.py`)

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | App is alive (no DB) |
| `GET /ready` | App + database connected (`SELECT 1`) |

`/ready` is what Kubernetes/load balancers use before sending traffic.

---

## Supabase connection notes

- Use **session pooler** on port **5432** if direct `db.*.supabase.co` fails DNS on Windows
- URL scheme: `postgresql+psycopg://` (psycopg v3)
- Append `?sslmode=require` for TLS

---

## Flow

```
Terminal: uvicorn app.main:app --reload
        │
FastAPI loads Settings from .env
        │
Engine connects to Supabase
        │
GET /health  → {"status": "ok"}
GET /ready   → {"database": "connected"}
```

---

## Interview points

1. **Engine vs Session** — Engine = connections; Session = one unit of work (queries + commit/rollback).
2. **Why `yield` in `get_db`?** — FastAPI runs `finally` after the response to close the session.
3. **Why env vars for secrets?** — Not in git; different values per environment without code changes.

---

## Navigation

← [Overview](01-overview-and-architecture.md) | [Registration & Passwords →](03-registration-and-passwords.md)
