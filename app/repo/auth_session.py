import uuid
from datetime import datetime 
from sqlalchemy.orm import Session
from app.models.auth_session import AuthSession

def create(
    db:Session,
    *,
    user_id:uuid.UUID,
    session_hash:str,
    expires_at:datetime,
)->AuthSession:
    row=AuthSession(
        user_id=user_id,
        session_hash=session_hash,
        expires_at=expires_at,
        revoked=False,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row

def revoke(db:Session,row:AuthSession)->None:
    row.revoked=True
    db.add(row)
    db.commit()

def get_by_hash(db:Session,session_hash:str)->AuthSession|None:
    return (
        db.query(AuthSession).filter(AuthSession.session_hash==session_hash).first()
    )

def revoke_all_for_user(db:Session,user_id:uuid.UUID)->None:
    db.query(AuthSession).filter(AuthSession.user_id==user_id,AuthSession.revoked.is_(False),).update({"revoked":True})
    db.commit()
