from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db,require_permission
from app.models.user import User
from app.repo import user as user_repo
from app.schemas.user import UserRead,MessageResponse
from app.api.deps import require_permission
import uuid
from app.core.rate_limit import limiter
from fastapi import Request
from app.services.auth import delete_user
router=APIRouter(
    prefix="/admin",
    tags=["admin"],
)

@router.get("/users",response_model=list[UserRead])
def list_all_users(
    db:Session=Depends(get_db),
    _:User=Depends(require_permission("users:read")),
):
    return user_repo.list_users(db)

@router.delete("/users/{user_id}",response_model=MessageResponse)
@limiter.limit("5/minute")
def delete_user_route(
    request:Request,
    user_id:uuid.UUID,
    db:Session=Depends(get_db),
    _:None=Depends(require_permission("users:delete")),
):
    return delete_user(db,user_id)