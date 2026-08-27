import uuid
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column,relationship

from app.db.session import Base
from app.models.role_permission import role_permission

class Permission(Base):
    __tablename__="permissions"

    id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    code:Mapped[str]=mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    description:Mapped[str|None]=mapped_column(
        String(255),nullable=True,
    )
    roles:Mapped[list["Role"]]=relationship(
        secondary=role_permission,
        back_populates="permissions"
    )