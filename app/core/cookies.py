from fastapi import Response
from app.core.config import get_settings
import secrets
REFRESH_COOKIE_NAME="refresh_token"
CSRF_COOKIE_NAME="csrf_token"
SESSION_COOKIE_NAME = "session_id"
def set_refresh_cookie(response:Response,raw_refresh:str)->None:
    settings=get_settings()
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS*24*60*60,
        path="/auth"
    )

def clear_refresh_cookie(response:Response)->None:
    settings=get_settings()
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path="/auth",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        httponly=True,
    )

def set_csrf_cookie(response:Response,csrf_token:str)->None:
    settings=get_settings()
    response.set_cookie(
        key=CSRF_COOKIE_NAME,
        value=csrf_token,
        httponly=False,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS*24*60*60,
        path="/auth"
    )

def clear_csrf_cookie(response:Response)->None:
    settings=get_settings()
    response.delete_cookie(
        key=CSRF_COOKIE_NAME,
        path="/auth",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )

def new_csrf_token()->str:
    return secrets.token_urlsafe(32)

def set_session_cookie(response:Response,raw_session:str)->None:
    settings=get_settings()
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=raw_session,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.SESSION_EXPIRE_DAYS*24*60*60,
        path="/"
    )

def clear_session_cookie(response:Response)->None:
    settings=get_settings()
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        httponly=True,
    )

