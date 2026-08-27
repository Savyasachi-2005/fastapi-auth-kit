import uuid
from datetime import datetime,timedelta

from sqlalchemy import Boolean,String,DateTime,ForeignKey,func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped,mapped_column

from app.db.session import Base

class RefreshToken(Base):
    __tablename__="refresh_tokens"

    id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str]=mapped_column(
        String(64),
        unique=True,
        index=True,
        nullable=False,
    )
    expires_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    revoked: Mapped[bool]=mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    created_at: Mapped[datetime]=mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    replaced_by: Mapped[uuid.UUID | None]=mapped_column(
        UUID(as_uuid=True),
        ForeignKey("refresh_tokens.id",ondelete="SET NULL"),
        nullable=True,
    )