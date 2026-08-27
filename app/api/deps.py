from collections.abc import AsyncGenerator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal

import uuid
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPBearer,HTTPAuthorizationCredentials
from sqlalchemy.orm import Session 
from collections.abc import Callable
from app.models.user import  User
from app.core.security import decode_access_token
from app.repo import user as user_repo

from fastapi import Request
from app.core.cookies import SESSION_COOKIE_NAME
from app.services.session_auth import get_user_for_session
bearer_scheme=HTTPBearer()

def get_db() -> AsyncGenerator[Session,None,None]:
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme),
    db:Session=Depends(get_db),
):
    token=credentials.credentials
    try:
        payload=decode_access_token(token)
        user_id=uuid.UUID(payload.get("sub"))
    except (ValueError,KeyError,TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"},
        )
    
    user = user_repo.get_by_id(db,user_id)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate":"Bearer"},
        )
    return user

def require_permission(permission_code:str)->Callable:
    def dependency(current_user:User=Depends(get_current_user))->User:
        role= current_user.role
        if role is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Enough Permissions",
            )
        codes={p.code for p in role.permissions}
        if permission_code not in codes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Enough Permissions",
            )
        return current_user
    return dependency

def get_current_user_from_session(
    request:Request,
    db:Session=Depends(get_db),
)->User:
    row=request.cookies.get(SESSION_COOKIE_NAME)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return get_user_for_session(db,row)