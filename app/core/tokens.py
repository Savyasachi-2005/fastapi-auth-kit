import secrets
from datetime import datetime,timezone,timedelta
from app.core.config import get_settings
from app.core.security import hash_token

def create_opaque_token()->tuple[str,str,datetime]:
    raw=secrets.token_bytes(32)
    return raw,hash_token(raw),datetime.now(timezone.utc)+timedelta(minutes=10)

def create_verification_token()->tuple[str,str,datetime]:
    settings=get_settings()
    raw=secrets.token_urlsafe(32)
    expires_at=datetime.now(timezone.utc)+timedelta(hours=settings.VERIFY_TOKEN_EXPIRE_HOURS)
    return raw,hash_token(raw),expires_at

def create_password_reset_token()->tuple[str,str,datetime]:
    settings=get_settings()
    raw=secrets.token_urlsafe(32)
    expires_at=datetime.now(timezone.utc)+timedelta(
        minutes=settings.RESET_TOKEN_EXPIRE_MINUTES
    )
    return raw,hash_token(raw),expires_at