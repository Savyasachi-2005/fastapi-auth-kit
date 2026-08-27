from datetime import datetime,timezone

from fastapi import HTTPException,status
from sqlalchemy.orm import Session

from app.core.security import hash_token,hash_password
from app.core.tokens import create_password_reset_token
from app.repo import user as user_repo,password_reset as reset_repo,refresh_token as refresh_token_repo
from app.services.email import send_password_reset_email
from app.schemas.user import ForgotPasswordRequest,ResetPasswordRequest

def forgot_password(db:Session,payload:ForgotPasswordRequest)->dict:
    user=user_repo.get_by_email(db,email=payload.email)

    if user is not None:
        raw,token_hash,expires_at=create_password_reset_token()
        reset_repo.create(
            db,
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        send_password_reset_email(email=user.email,raw_token=raw)
    return {"message":"Password reset email sent"}

def reset_password(
    db:Session,
    payload:ResetPasswordRequest
)->dict:
    token_hash=hash_token(payload.token)
    row=reset_repo.get_by_hash(db,token_hash=token_hash)

    if row is None or row.revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token",
        )
    
    expires_at=row.expires_at
    if expires_at.tzinfo is None:
        expires_at=expires_at.replace(tzinfo=timezone.utc)
    if expires_at<datetime.now(timezone.utc):
        reset_repo.revoke(db,row)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expired",
        )
    
    user=user_repo.get_by_id(db,row.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )
    user.hashed_password=hash_password(payload.new_password)
    db.add(user)
    db.commit()

    reset_repo.revoke(db,row)
    refresh_token_repo.revoke_all_for_user(db,user.id)

    return {"message":"Password reset successful"}
