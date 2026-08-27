from fastapi import APIRouter,Depends,HTTPException
from app.core.config import get_settings
from app.api.deps import get_db
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import get_settings
router=APIRouter(tags=["health"])

@router.get("/health")
def health_check():
    settings=get_settings()
    return {
        "status": "ok",
        "app":settings.APP_NAME,
        "environment":settings.ENVIRONMENT,
    }
@router.get("/ready")
def ready_check(db:Session=Depends(get_db)):
    settings=get_settings()
    try:
        db.execute(text("SELECT 1"))
        return {
            "status":"ok",
            "database":"connected",
            "app":settings.APP_NAME,
            "environment":settings.ENVIRONMENT,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {e}",
            headers={"X-Error": "Database connection failed"},
        )
    finally:
        db.close()
