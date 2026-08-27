# Phase 7 — RBAC (Roles & Permissions)

## Concept

**RBAC** = Role-Based Access Control. Users have a **role**; roles have **permissions**. Endpoints check permission codes instead of hardcoding "is admin".

---

## Why RBAC?

| Without RBAC | With RBAC |
|--------------|-----------|
| `if user.email == "admin@..."` | `require_permission("users:delete")` |
| Scattered role checks | Central permission map |
| Hard to add new roles | Add role + assign permissions in DB |

---

## Data model

```
users ──role_id──> roles ──role_permission──> permissions
```

| Role | Permissions |
|------|-------------|
| `user` | `me:read` |
| `admin` | `me:read`, `users:read`, `users:delete` |

### Models

- `app/models/roles.py` — `Role` (name, description)
- `app/models/permission.py` — `Permission` (code, description)
- `app/models/role_permission.py` — association table

### Seed (`app/core/seed.py`)

Runs on startup (`main.py` → `seed_rbac()`). Idempotent — creates roles/permissions if missing.

---

## Permission dependency (`app/api/deps.py`)

```python
def require_permission(permission_code: str):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        codes = {p.code for p in current_user.role.permissions}
        if permission_code not in codes:
            raise HTTPException(403, "Not Enough Permissions")
        return current_user
    return dependency
```

### Usage

```python
@router.get("/admin/users")
def list_users(_: User = Depends(require_permission("users:read"))):
    ...
```

Still requires valid JWT first (`get_current_user` is nested inside).

---

## Admin routes (`app/api/routes/admin.py`)

| Method | Path | Permission |
|--------|------|------------|
| GET | `/admin/users` | `users:read` |
| DELETE | `/admin/users/{user_id}` | `users:delete` |

Delete protection: cannot delete users with `admin` role.

---

## Flow

```
GET /admin/users
  Authorization: Bearer <jwt>
        │
get_current_user → load user + role + permissions (joinedload)
        │
require_permission("users:read")
        │
user_repo.list_users()
```

---

## Interview points

1. **Role vs permission?** Role = job title (admin, user). Permission = atomic action (`users:delete`).
2. **Why seed on startup?** Dev convenience; production should use migrations + admin setup script.
3. **How to promote user to admin?** Update `role_id` in DB to admin role uuid.

---

## Navigation

← [Account Flows](07-account-flows.md) | [Google OAuth →](09-google-oauth.md)
