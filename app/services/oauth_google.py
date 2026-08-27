import secrets
import httpx 
from urllib.parse import urlencode

from fastapi import HTTPException,status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token,create_refresh_token,hash_token
from app.repo import user as user_repo
from app.repo import role as role_repo
from app.repo import refresh_token as refresh_token_repo

GOOGLE_AUTH_URL="https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL="https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL="https://www.googleapis.com/oauth2/v3/userinfo"

def build_google_auth_url(state:str)->str:
    settings=get_settings()
    params={
        "client_id":settings.GOOGLE_CLIENT_ID,
        "redirect_uri":settings.GOOGLE_REDIRECT_URI,
        "response_type":"code",
        "scope":"openid profile email",
        "access_type":"offline",
        "include_granted_scopes":"true",
        "state":state,
        "prompt":"consent",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def new_oauth_state()->str:
    return secrets.token_urlsafe(32)

def exchange_code_for_token(code:str)->dict:
    settings=get_settings()
    data={
        "code":code,
        "client_id":settings.GOOGLE_CLIENT_ID,
        "client_secret":settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri":settings.GOOGLE_REDIRECT_URI,
        "grant_type":"authorization_code",
    }
    with httpx.Client(timeout=20.0) as client:
        resp=client.post(GOOGLE_TOKEN_URL,data=data)
    if resp.status_code!=200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange Google code",
        )
    return resp.json()

def fetch_google_userinfo(access_token:str)->dict:
    with httpx.Client(timeout=20.0) as client:
        resp=client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization":f"Bearer {access_token}"},
        )
    if resp.status_code!=200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch Google userinfo",
        )
    return resp.json()

def _issue_app_tokens(db:Session,user)->dict:
    access_token=create_access_token(str(user.id))
    raw_refresh,expires_at=create_refresh_token()
    refresh_token_repo.create(
        db,
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=expires_at,
    )
    return {
        "access_token":access_token,
        "refresh_token":raw_refresh,
        "token_type":"Bearer",
    }

def login_or_register_with_google(db:Session,*,google_sub:str,email:str)->dict:
    user=user_repo.get_by_google_sub(db,google_sub)
    if user is not None:
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not active",
            )
        return _issue_app_tokens(db,user)
    user=user_repo.get_by_email(db,email)
    if user is not None:
        if user.google_sub is not None and user.google_sub!=google_sub:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account already linked to another user",
            )
        other=user_repo.get_by_google_sub(db,google_sub)
        if other is not None and other.id!=user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account already linked to another user",
            )
        user.google_sub=google_sub
        user.is_verified=True
        user_repo.save(db,user)
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not active",
            )
        return _issue_app_tokens(db,user)
    
    default_role=role_repo.get_by_name(db,"user")
    if default_role is None:
        raise HTTPException(
            status_code=500,
            detail="Default role not found",
        )
    user =user_repo.create_user(
        db,
        email=email,
        role_id=default_role.id,
        hashed_password=None,
        google_sub=google_sub,
        is_verified=True,
    )
    return _issue_app_tokens(db,user)
