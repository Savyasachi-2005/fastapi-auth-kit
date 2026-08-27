from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    APP_NAME: str= "AuthAPI"
    ENVIRONMENT: str="development"
    DATABASE_URL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int=15
    REFRESH_TOKEN_EXPIRE_DAYS: int=7
    ALGORITHM: str="HS256"
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    @property
    def cors_origins_list(self)->list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]
    COOKIE_SECURE:bool=False
    COOKIE_SAMESITE:str="lax"
    VERIFY_TOKEN_EXPIRE_HOURS:int=24
    FRONTEND_URL:str
    RESET_TOKEN_EXPIRE_MINUTES:int=30
    GOOGLE_CLIENT_ID:str
    GOOGLE_CLIENT_SECRET:str
    GOOGLE_REDIRECT_URI:str
    SESSION_EXPIRE_DAYS: int = 7
@lru_cache()
def get_settings() -> Settings:
    return Settings()

