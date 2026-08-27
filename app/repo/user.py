from sqlalchemy.orm import Session,joinedload
from sqlalchemy import func
from app.models import User
from app.models.roles import Role
from app.models.permission import Permission
import uuid
def get_by_email(db:Session,email:str)->User|None:
    return db.query(User).filter(func.lower(User.email)==email.lower()).first()

def create_user(
    db:Session,
    email:str,
    role_id:uuid.UUID,
    hashed_password:str|None=None,
    *,
    google_sub:str|None=None,
    is_verified:bool=False,
    )->User:
    user=User(
        email=email,
        hashed_password=hashed_password,
        role_id=role_id,
        google_sub=google_sub,
        is_verified=is_verified,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_by_id(db:Session,user_id:uuid.UUID)->User|None:
    return db.query(User).options(joinedload(User.role).joinedload(Role.permissions),).filter(User.id==user_id).first()

def list_users(db:Session)->list[User]:
    return db.query(User).order_by(User.created_at.desc()).all()

def delete(db:Session,user=User)->None:
    db.delete(user)
    db.commit()
    return {"message":"User deleted successfully"}
    
def get_by_google_sub(db:Session,google_sub:str)->User|None:
    return db.query(User).filter(User.google_sub==google_sub).first()

def save(db:Session,user:User)->User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user