import uuid
from datetime import datetime,timezone
from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken
from app.api.deps import get_db
def create(
    db:Session,
    *,
    user_id:uuid.UUID,
    token_hash:str,
    expires_at:datetime,
)->RefreshToken:
    row=RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked=False,
        )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def get_by_hash(db:Session,token_hash:str)->RefreshToken|None:
    return (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash==token_hash).first()
    )

def revoke(db:Session,row:RefreshToken,*,replaced_by:uuid.UUID|None=None)->None:
    row.revoked=True
    if replaced_by is not None:
        row.replaced_by=replaced_by
    db.add(row)
    db.commit()

def revoke_all_for_user(db:Session,user_id:uuid.UUID)->None:
    db.query(RefreshToken).filter(RefreshToken.user_id==user_id,RefreshToken.revoked.is_(False)).update({"revoked":True})
    db.commit()