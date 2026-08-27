from datetime import datetime,timezone

from fastapi import HTTPException,status
from sqlalchemy.orm import Session

from app.core.security import hash_token
from app.core.tokens import create_verification_token
from app.repo import user as user_repo
from app.repo import email_verification as verify_repo
from app.services.email import send_verification_email
from app.schemas.user import RequestVerifyEmail

def request_verify_email(db:Session,request:RequestVerifyEmail)->dict:
    user=user_repo.get_by_email(db,email=request.email)

    if user is not None and not user.is_verified:
        raw,token_hash,expires_at=create_verification_token()
        verify_repo.create(
            db,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        send_verification_email(email=request.email,raw_token=raw)
    return {"message":"If that email exists, we sent a verification link."}

def verify_email(db:Session,raw_token:str)->dict:
    token_hash=hash_token(raw_token)
    row=verify_repo.get_by_hash(db,token_hash=token_hash)

    if row is None or row.revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token."
        )
    expires_at=row.expires_at
    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)
    if expires_at<datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired vefification."
        )
    user=user_repo.get_by_id(db,row.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired verification token."
        )
    user.is_verified=True
    db.add(user)
    db.commit()
    verify_repo.revoke(db,row)

    return {"message":"Email verified successfully."}