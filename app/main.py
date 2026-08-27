from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth as auth_router,users as users_router
from app.api.routes import health as health_router
from app.core.config import get_settings
from app.db.session import engine,Base
from app.models import User,RefreshToken,Permission,Role,AuthSession
from app.core.seed import seed_rbac
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limit import limiter
from app.api.routes import admin as admin_router
from app.api.routes import oauth as oauth_router
from app.api.routes import session as session_router
settings=get_settings()
# Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
seed_rbac()
app=FastAPI(
    title=settings.APP_NAME
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.limiter=limiter
app.add_exception_handler(RateLimitExceeded,_rate_limit_exceeded_handler)
app.include_router(health_router.router)
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(admin_router.router)
app.include_router(oauth_router.router)

app.include_router(session_router.router)