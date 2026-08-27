import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime,String ,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column
from app.db.session import Base 
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str]=mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str]=mapped_column(
        String(255),
        nullable=True,
    )
    is_active: Mapped[bool]=mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    is_verified: Mapped[bool]=mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    role_id:Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id"),
        nullable=False,
        index=True,
    )
    role:Mapped["Role|None"]=relationship(
        back_populates="users"
    )

    google_sub: Mapped[str]=mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
    )