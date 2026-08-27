from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from app.models.user import User
from app.api.deps import get_db,get_current_user
from app.schemas.user import UserCreate,UserRead,LoginRequest,TokenResponse,RefreshRequest
from app.services.auth import register_user,login_user,refresh_access,logout_user,logout_all,delete_user
from fastapi import Request
from app.core.rate_limit import limiter
from fastapi import Response
from app.core.csrf import require_csrf
from app.core.cookies import set_refresh_cookie,clear_refresh_cookie,REFRESH_COOKIE_NAME,set_csrf_cookie,clear_csrf_cookie,new_csrf_token
from app.services.verification import request_verify_email,verify_email
from app.schemas.user import RequestVerifyEmail,MessageResponse
from app.services.password_reset import forgot_password,reset_password
from app.schemas.user import ForgotPasswordRequest,ResetPasswordRequest

router=APIRouter(
    prefix="/auth",
    tags=["auth"]
)
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
@limiter.limit("5/minute")
def register(request:Request,payload:UserCreate,db:Session=Depends(get_db))->UserRead:
    return register_user(db,payload)

@router.post("/login",response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request:Request,payload:LoginRequest,response:Response,db:Session=Depends(get_db)):
    tokens=login_user(db,payload)
    set_refresh_cookie(response,tokens["refresh_token"])
    csrf=new_csrf_token()
    set_csrf_cookie(response,csrf)
    tokens["csrf_token"]=csrf
    return tokens

@router.post("/refresh",response_model=TokenResponse)
@limiter.limit("5/minute")
def refresh(
    request:Request,
    response:Response,
    db:Session=Depends(get_db),
    payload:RefreshRequest|None=None,
    _:None=Depends(require_csrf),
    ):
    raw=_get_refresh_token(request,payload)
    tokens=refresh_access(db,RefreshRequest(refresh_token=raw))
    set_refresh_cookie(response,tokens["refresh_token"])
    csrf=new_csrf_token()
    set_csrf_cookie(response,csrf)
    tokens["csrf_token"]=csrf
    return tokens

def _get_refresh_token(request:Request,payload:RefreshRequest|None)->str:
    raw=request.cookies.get(REFRESH_COOKIE_NAME)
    if raw:
        return raw
    if payload and payload.refresh_token:
        return payload.refresh_token
    raise HTTPException(status_code=401,detail="Missing refresh token")

@router.post("/logout",status_code=status.HTTP_204_NO_CONTENT)
def logout(
    request:Request,
    response:Response,
    payload:RefreshRequest|None=None,
    db:Session=Depends(get_db),
    _:None=Depends(require_csrf),
    ):
    raw=_get_refresh_token(request,payload)
    logout_user(db,RefreshRequest(refresh_token=raw))
    clear_refresh_cookie(response)
    clear_csrf_cookie(response)
    return None

@router.post("/logout-all",status_code=status.HTTP_204_NO_CONTENT)
def logout_all_devices(
    db:Session=Depends(get_db),
    current_user:User=Depends(get_current_user),
):
    logout_all(db,current_user)
    return None

@router.post("/verify-email",response_model=MessageResponse)
@limiter.limit("5/minute")
def request_verify(
    request:Request,
    payload:RequestVerifyEmail,
    db:Session=Depends(get_db),
):
    return request_verify_email(db,payload)

@router.get("/verify-email/{token}",response_model=MessageResponse)
def verify_email_route(
    token:str,db:Session=Depends(get_db)
):
    return verify_email(db,token)

@router.post("/forgot-password",response_model=MessageResponse)
@limiter.limit("5/minute")
def forgot_password_route(
    request:Request,
    payload:ForgotPasswordRequest,
    db:Session=Depends(get_db),
):
    return forgot_password(db,payload)

@router.post("/reset-password",response_model=MessageResponse)
@limiter.limit("5/minute")
def reset_password_route(
    request:Request,
    payload:ResetPasswordRequest,
    db:Session=Depends(get_db),
):
    return reset_password(db,payload)

