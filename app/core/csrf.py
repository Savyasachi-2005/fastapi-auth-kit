from fastapi import Request,status,Header,HTTPException
from app.core.cookies import CSRF_COOKIE_NAME

def require_csrf(
    request:Request,x_csrf_token:str|None=Header(default=None,alias="X-CSRF-Token"),
)->None:
    cookie_token=request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token or not x_csrf_token or cookie_token!=x_csrf_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CSRF check failed",
        )