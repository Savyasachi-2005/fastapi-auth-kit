import bcrypt
from datetime import datetime,timedelta,timezone
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.config import get_settings
import hashlib
import secrets

def hash_password(plain_password: str)->str:
    hashed=bcrypt.hashpw(
        plain_password.encode("utf-8"),
        bcrypt.gensalt(),
    )
    return hashed.decode("utf-8")

def verify_password(plain_password:str,hash_password:str)->bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hash_password.encode("utf-8"),
    )

def create_access_token(subject:str)->str:
    settings=get_settings()
    expire=datetime.now(timezone.utc)+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload={
        "sub":subject,
        "exp":expire,
        "type":"access",
    }
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def decode_access_token(token:str)->str:
    settings=get_settings()
    try:
        payload=jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except InvalidTokenError as exc:
        raise ValueError("Invalid token") from exc
    if payload.get("type")!="access":
        raise ValueError("Invalid token type")

    return payload

def hash_token(token:str)->str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def create_refresh_token()->tuple[str,datetime]:
    settings=get_settings()
    raw=secrets.token_urlsafe(32)
    expires_at=datetime.now(timezone.utc)+timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    return raw,expires_at

def create_session_id()->tuple[str,datetime]:
    settings=get_settings()
    raw=secrets.token_urlsafe(32)
    expires_at=datetime.now(timezone.utc)+timedelta(
        days=settings.SESSION_EXPIRE_DAYS
    )
    return raw,expires_at