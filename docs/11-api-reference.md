# API Reference

Base URL (local): `http://127.0.0.1:8000`

Interactive docs: `http://127.0.0.1:8000/docs`

---

## Health

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/health` | None | App alive |
| GET | `/ready` | None | DB connected |

---

## Auth (`/auth`)

| Method | Path | Auth | Rate limit | Description |
|--------|------|------|------------|-------------|
| POST | `/auth/register` | None | 5/min | Create account |
| POST | `/auth/login` | None | 5/min | Login → JWT + refresh cookie |
| POST | `/auth/refresh` | Refresh cookie + CSRF | 5/min | Rotate tokens |
| POST | `/auth/logout` | Refresh cookie + CSRF | — | Revoke refresh, clear cookies |
| POST | `/auth/logout-all` | Bearer JWT | — | Revoke all refresh tokens |
| POST | `/auth/verify-email` | None | 5/min | Request verification email |
| GET | `/auth/verify-email/{token}` | None | — | Confirm email |
| POST | `/auth/forgot-password` | None | 5/min | Request reset email |
| POST | `/auth/reset-password` | None | 5/min | Set new password |

### Login response

```json
{
  "access_token": "eyJ...",
  "refresh_token": "opaque...",
  "token_type": "Bearer",
  "csrf_token": "..."
}
```

Also sets httpOnly `refresh_token` and `csrf_token` cookies.

### Refresh / logout headers

```
X-CSRF-Token: <value from csrf_token cookie>
Cookie: refresh_token=...; csrf_token=...
```

---

## Users (`/users`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/users/me` | Bearer JWT | Current user profile |

```
Authorization: Bearer <access_token>
```

---

## Admin (`/admin`)

| Method | Path | Permission | Description |
|--------|------|------------|-------------|
| GET | `/admin/users` | `users:read` | List all users |
| DELETE | `/admin/users/{user_id}` | `users:delete` | Delete user (not admin) |

Requires Bearer JWT + role permission.

---

## OAuth (`/oauth`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/oauth/google/login` | None | Redirect to Google (browser only) |
| GET | `/oauth/google/callback` | OAuth state cookie | Google callback → tokens |

---

## Session (`/session`)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/session/login` | None | Login → session cookie |
| GET | `/session/me` | `session_id` cookie | Current user (session) |
| POST | `/session/logout` | `session_id` cookie | Revoke session |

---

## Common request bodies

### Register / Login

```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

### Forgot password

```json
{ "email": "user@example.com" }
```

### Reset password

```json
{
  "token": "raw-token-from-email",
  "new_password": "newsecurepass123"
}
```

---

## Status codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created (register) |
| 204 | No content (logout) |
| 400 | Bad request (validation, OAuth errors) |
| 401 | Invalid credentials / token |
| 403 | Forbidden (unverified, CSRF, permission) |
| 404 | Not found |
| 429 | Rate limit exceeded |

---

## Navigation

← [Session Auth](10-session-auth.md) | [Security Best Practices →](12-security-best-practices.md)
