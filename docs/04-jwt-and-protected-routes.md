# Phase 3 — JWT Login & Protected Routes

## Concept

A **JWT (JSON Web Token)** is a signed string: `header.payload.signature`. After login, the client sends it on every request:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

The server verifies the signature with `SECRET_KEY` and reads `sub` (user id) from the payload.

---

## Why JWT?

HTTP is **stateless** — the server doesn't remember prior requests. JWT proves "this user logged in recently" without a DB lookup on every request (for access tokens).

---

## Token creation (`app/core/security.py`)

```python
def create_access_token(subject: str) -> str:
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": subject,      # user id as string
        "exp": expire,       # expiry (PyJWT validates)
        "type": "access",    # prevent refresh token misuse
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

```python
def decode_access_token(token: str) -> dict:
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    if payload.get("type") != "access":
        raise ValueError("Invalid token type")
    return payload
```

**Always pass `algorithms=[...]`** — prevents algorithm confusion attacks.

---

## Login flow

```
POST /auth/login
  { "email", "password" }
        │
get_by_email → verify_password
        │
Check is_verified, is_active
        │
Reject if hashed_password is None (OAuth-only user)
        │
create_access_token(user.id)
create_refresh_token() → store hash in DB (Phase 4)
        │
Return { access_token, refresh_token, token_type: "Bearer" }
```

---

## Protected route dependency (`app/api/deps.py`)

```python
def get_current_user(
    credentials = Depends(HTTPBearer()),
    db = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    user_id = UUID(payload["sub"])
    user = user_repo.get_by_id(db, user_id)
    if user is None or not user.is_active:
        raise HTTPException(401, ...)
    return user
```

### Usage

```python
@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
```

FastAPI injects the dependency **before** your handler runs. You never pass the token manually in the route.

---

## Flow diagram

```
Client                    API                     DB
  │                        │                       │
  │ POST /auth/login       │                       │
  │───────────────────────>│ verify password       │
  │                        │──────────────────────>│
  │<───────────────────────│ access + refresh      │
  │                        │                       │
  │ GET /users/me          │                       │
  │ Authorization: Bearer  │                       │
  │───────────────────────>│ decode JWT → user id  │
  │                        │──────────────────────>│
  │<───────────────────────│ UserRead              │
```

---

## Interview points

1. **What's in the JWT payload?** `sub`, `exp`, `type` — never put secrets or PII in JWT (it's base64, not encrypted).
2. **What if JWT is stolen?** Short TTL limits damage; refresh rotation + logout help; HTTPS prevents network sniffing.
3. **Bearer scheme?** Tells clients to send `Authorization: Bearer <token>`.

---

## Navigation

← [Registration](03-registration-and-passwords.md) | [Refresh Tokens →](05-refresh-tokens-and-logout.md)
