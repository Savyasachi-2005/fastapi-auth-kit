from datetime import datetime,timezone

from fastapi import HTTPException,status
from sqlalchemy.orm import Session

from app.core.security import (
    create_session_id,
    hash_token,
    verify_password
)
from app.repo import auth_session as session_repo
from app.repo import user as user_repo
from app.schemas.user import LoginRequest

def login_with_session(db:Session,request:LoginRequest)->str:
    user=user_repo.get_by_email(db,request.email)

    if(
        user is None or user.hashed_password is None 
        or not verify_password(request.password,user.hashed_password)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email to login"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    raw_session,expires_at=create_session_id()
    session_repo.create(
        db,
        user_id=user.id,
        session_hash=hash_token(raw_session),
        expires_at=expires_at,
    )
    return raw_session

def logout_session(db:Session,raw_session:str)->None:
    row=session_repo.get_by_hash(db,hash_token(raw_session))
    if row is not None and not row.revoked:
        session_repo.revoke(db,row)

def get_user_for_session(db:Session,raw_session:str):
    row=session_repo.get_by_hash(db,hash_token(raw_session))

    if row is None or row.revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
    
    now=datetime.now(timezone.utc)
    if row.expires_at<now:
        session_repo.revoke(db,row)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired",
        )

    user=user_repo.get_by_id(db,row.user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
    
    return user