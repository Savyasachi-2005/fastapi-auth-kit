from app.core.config import get_settings

def send_verification_email(*,email:str,raw_token:str)->None:
    settings=get_settings()
    link=f"{settings.FRONTEND_URL}/verify-email?token={raw_token}"
    print(f"[DEV EMAIL] To: {email}\nverify: {link}")

def send_password_reset_email(*,email:str,raw_token:str)->None:
    settings=get_settings()
    link=f"{settings.FRONTEND_URL}/reset-password?token={raw_token}"
    print(f"[DEV EMAIL] To: {email}\nreset: {link}")

    