from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from datetime import datetime,timezone
from app.core.security import hash_password,verify_password,create_access_token,hash_token,create_refresh_token
from app.repo import user as user_repo
from app.repo import role as role_repo
from app.schemas.user import UserCreate ,LoginRequest,RefreshRequest
from app.models.user import User 
from app.repo import refresh_token as refresh_token_repo
import uuid
def register_user(db:Session,user:UserCreate)->User:
    existing=user_repo.get_by_email(db,user.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    default_role=role_repo.get_by_name(db,"user")
    if default_role is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role not found"
        )
    hashed=hash_password(user.password)
    return user_repo.create_user(
        db,email=user.email,
        hashed_password=hashed,
        role_id=default_role.id,
    )

def login_user(db:Session,request:LoginRequest)->dict:
    user=user_repo.get_by_email(db,request.email)
    if user is None or user.hashed_password is None or not verify_password(request.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate":"Bearer"},
        )
    if user is None or not verify_password(request.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate":"Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email to login.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    access=create_access_token(str(user.id))
    raw_refresh,expires_at=create_refresh_token()
    refresh_token_repo.create(
        db,
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=expires_at,
    )
    return {"access_token":access,"refresh_token":raw_refresh,"token_type":"Bearer"}

def refresh_access(db:Session,payload:RefreshRequest)->dict:
    token_hash=hash_token(payload.refresh_token)
    row=refresh_token_repo.get_by_hash(db,token_hash)

    if row is None :
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    if row.revoked:
        refresh_token_repo.revoke_all_for_user(db,row.user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    now=datetime.now(timezone.utc)
    expires_at=row.expires_at
    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)
    if expires_at<now:
        refresh_token_repo.revoke(db,row)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )
    user=user_repo.get_by_id(db,row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    access=create_access_token(str(user.id))
    raw_refresh,new_expires=create_refresh_token()
    new_row=refresh_token_repo.create(
        db,
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=new_expires,
    )
    refresh_token_repo.revoke(db,row,replaced_by=new_row.id)

    return {
        "access_token":access,
        "refresh_token":raw_refresh,
        "token_type":"bearer"
    }
def logout_user(db:Session,payload:RefreshRequest)->None:
    token_hash=hash_token(payload.refresh_token)
    row=refresh_token_repo.get_by_hash(db,token_hash)
    if row is not None and not row.revoked:
        refresh_token_repo.revoke(db,row)
        return {"message":"Logged out successfully"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
    )

def logout_all(db:Session,user:User)->None:
    refresh_token_repo.revoke_all_for_user(db,user.id)

def delete_user(db:Session,user_id:uuid.UUID)->None:
    user=user_repo.get_by_id(db,user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    if user.role is not None and user.role.name=="admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete admin user",
        )
    
    user_repo.delete(db,user)
    return {"message":"User deleted successfully"}