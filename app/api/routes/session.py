from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_user_from_session, get_db
from app.core.cookies import clear_session_cookie, set_session_cookie
from app.core.rate_limit import limiter
from app.models.user import User
from app.schemas.user import LoginRequest, MessageResponse, UserRead
from app.services.session_auth import login_with_session, logout_session
from app.core.cookies import SESSION_COOKIE_NAME

router=APIRouter(
    prefix="/session",
    tags=["session"]
)

@router.post("/login",response_model=MessageResponse)
@limiter.limit("5/minute")
def session_login(
    request:Request,
    payload:LoginRequest,
    response:Response,
    db:Session=Depends(get_db)
):
    raw_session=login_with_session(db,payload)
    set_session_cookie(response,raw_session)
    return MessageResponse(message="logged in with session")

@router.get("/me",response_model=UserRead)
def session_me(current_user:User=Depends(get_current_user_from_session)):
    return current_user

@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
def session_logout(
    request:Request,
    response:Response,
    db:Session=Depends(get_db),
):
    raw=request.cookies.get(SESSION_COOKIE_NAME)
    if raw:
        logout_session(db,raw)
    clear_session_cookie(response)
    return None