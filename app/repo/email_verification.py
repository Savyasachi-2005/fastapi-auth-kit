import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.email_verification_token import EmailVerificationToken

def create(
    db:Session,
    *,
    user_id:uuid.UUID,
    token_hash:str,
    expires_at:datetime,
)->EmailVerificationToken:
    row=EmailVerificationToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def get_by_hash(db:Session,token_hash:str)->EmailVerificationToken|None:
    return (
        db.query(EmailVerificationToken).filter(EmailVerificationToken.token_hash==token_hash).first()
    )

def revoke(db:Session,row:EmailVerificationToken)->None:
    row.revoked=True
    db.add(row)
    db.commit()