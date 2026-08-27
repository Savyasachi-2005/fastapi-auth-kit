from fastapi import APIRouter,Depends,HTTPException,status,Response
from sqlalchemy.orm import Session
from fastapi import Request
from fastapi.responses import RedirectResponse,JSONResponse
from app.core.config import get_settings
from app.core.cookies import set_refresh_cookie,set_csrf_cookie,new_csrf_token
from app.api.deps import get_db
from app.services.oauth_google import (
    build_google_auth_url,
    new_oauth_state,
    exchange_code_for_token,
    fetch_google_userinfo,
    login_or_register_with_google,
)
router=APIRouter(
    prefix="/oauth",
    tags=["oauth"],
)

OAUTH_STATE_COOKIE="oauth_state"
@router.get("/google/login")
def google_login(response:Response):
    state=new_oauth_state()
    response=RedirectResponse(build_google_auth_url(state),status_code=302)
    response.set_cookie(
        key=OAUTH_STATE_COOKIE,
        value=state,
        httponly=True,
        max_age=600,
        samesite="lax",
        path="/oauth",
    )
    return response

@router.get("/google/callback")
def google_callback(
    request:Request,
    response:Response,
    db:Session=Depends(get_db),
    code:str|None=None,
    state:str|None=None,
    error:str|None=None,
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {error}",
        )
    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required parameters",
        )
    cookie_state=request.cookies.get(OAUTH_STATE_COOKIE)
    if not cookie_state or cookie_state!=state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state",
        )
    google_tokens=exchange_code_for_token(code)
    profile=fetch_google_userinfo(google_tokens["access_token"])
    google_sub=profile.get("sub")
    email=profile.get("email")
    if not google_sub or not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google profile",
        )
    tokens=login_or_register_with_google(
        db,
        google_sub=google_sub,
        email=email
    )
    payload=tokens
    resp=JSONResponse(content=payload)
    set_refresh_cookie(response,tokens["refresh_token"])
    csrf=new_csrf_token()
    set_csrf_cookie(resp,csrf)
    tokens["csrf_token"]=csrf

    resp.delete_cookie(OAUTH_STATE_COOKIE,path="/oauth")

    return resp