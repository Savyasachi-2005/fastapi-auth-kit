import uuid

from sqlalchemy import Column,ForeignKey,Table 
from sqlalchemy.dialects.postgresql import UUID
from app.db.session import Base

role_permission=Table(
    "role_permission",
    Base.metadata,
    Column("role_id",UUID(as_uuid=True),ForeignKey("roles.id",ondelete="CASCADE"),primary_key=True),
    Column("permission_id",UUID(as_uuid=True),ForeignKey("permissions.id",ondelete="CASCADE"),primary_key=True)

)