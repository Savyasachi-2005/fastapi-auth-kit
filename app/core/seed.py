from sqlalchemy.orm import Session

from app.repo import role as role_repo,permission as permission_repo
from app.db.session import SessionLocal

DEFAULT_PERMISSIONS=[
    ("me:read","Read own profile"),
    ("users:read","List Users"),
    ("users:delete","Delete Users"),
]

USER_PERMISSIONS={"me:read"}
ADMIN_PERMISSIONS={"me:read","users:read","users:delete"}

def seed_rbac()->None:
    db:Session=SessionLocal()
    try:
        user_role=role_repo.get_by_name(db,"user")
        if user_role is None:
            user_role=role_repo.create(db,name="user",description="Default user")
        admin_role=role_repo.get_by_name(db,"admin")
        if admin_role is None:
            admin_role=role_repo.create(db,name="admin",description="Administrator")
        
        perms_by_code={}
        for code,description in DEFAULT_PERMISSIONS:
            perm=permission_repo.get_by_code(db,code)
            if perm is None:
                perm=permission_repo.create(db,code=code,description=description)
            perms_by_code[code]=perm

        user_role.permissions=[perms_by_code[c] for c in USER_PERMISSIONS]
        admin_role.permissions=[perms_by_code[c] for c in ADMIN_PERMISSIONS]
        db.add(user_role)
        db.add(admin_role)
        db.commit()
    finally:
        db.close()