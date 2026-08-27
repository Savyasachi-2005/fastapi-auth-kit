# Phase 2 — Registration & Password Hashing

## Concept

**Registration** creates a user row with a **hashed** password — never store plain text. **bcrypt** is a slow, adaptive hash designed for passwords.

---

## Why hash passwords?

If the database leaks, attackers get hashes — not usable passwords. bcrypt adds **salt** automatically and is **slow** to brute-force.

---

## User model (`app/models/user.py`)

Key columns:

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID | Primary key |
| `email` | String(255) | Unique, indexed |
| `hashed_password` | String(255) | Nullable (OAuth-only users have `NULL`) |
| `is_active` | Boolean | Admin can disable accounts |
| `is_verified` | Boolean | Email must be verified before login |
| `role_id` | UUID FK | Links to `roles` |
| `google_sub` | String | Google account id (Phase 8) |
| `created_at` | DateTime | Server default `now()` |

---

## Security helpers (`app/core/security.py`)

```python
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

Never log or return the plain password.

---

## Registration flow

```
POST /auth/register
  { "email": "...", "password": "..." }
        │
Pydantic validates (min 8 chars, valid email)
        │
Service: get_by_email → 400 if exists
        │
hash_password(password)
        │
repo.create_user(email, hashed_password, role_id="user")
        │
201 UserRead (no password in response)
```

### Service (`app/services/auth.py` — `register_user`)

1. Check email not taken
2. Load default `user` role from DB
3. Hash password
4. Insert user via repo

### Route (`POST /auth/register`)

- Rate limited: `5/minute`
- Returns `UserRead` schema (id, email, flags — no hash)

---

## Repo pattern (`app/repo/user.py`)

```python
def get_by_email(db, email) -> User | None:
    return db.query(User).filter(func.lower(User.email) == email.lower()).first()

def create_user(db, email, role_id, hashed_password=None, ...) -> User:
    user = User(...)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
```

**Case-insensitive email lookup** — `func.lower()` on both sides.

---

## Schemas (`app/schemas/user.py`)

| Schema | Use |
|--------|-----|
| `UserCreate` | Register body (email + password) |
| `UserRead` | Safe user response (`from_attributes=True`) |

---

## Interview points

1. **Why bcrypt over SHA-256?** SHA is fast — attackers can try billions of guesses. bcrypt is intentionally slow.
2. **Why separate schema from model?** API shouldn't expose internal columns; Pydantic validates input.
3. **Why repo layer?** Routes stay thin; SQL is testable and reusable.

---

## Navigation

← [Foundation](02-foundation.md) | [JWT & Protected Routes →](04-jwt-and-protected-routes.md)
