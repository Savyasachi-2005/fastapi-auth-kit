from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from app.core.config import get_settings
Settings=get_settings()

engine=create_engine(
    Settings.DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal=sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)

class Base(DeclarativeBase):
    pass
