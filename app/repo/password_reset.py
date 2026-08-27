import uuid 
from datetime import datetime

from sqlalchemy.orm import Session 

from app.models.password_reset_token import PasswordResetToken

def create(
    db:Session,
    *,
    user_id:uuid.UUID,
    token_hash:str,
    expires_at:datetime,
)->PasswordResetToken:
    row=PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def get_by_hash(db:Session,token_hash:str)->PasswordResetToken|None:
    return (
        db.query(PasswordResetToken).filter(PasswordResetToken.token_hash==token_hash).first()
    )

def revoke(db:Session,row:PasswordResetToken)->None:
    row.revoked=True
    db.add(row)
    db.commit()