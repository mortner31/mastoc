"""
Modèle User (utilisateur).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base
from mastoc_api.models.base import DataSource


class User(Base):
    """Utilisateur."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    stokt_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        unique=True,
        nullable=True,
        index=True,
        comment="Mapping vers Stokt"
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_path: Mapped[str | None] = mapped_column(String(500))
    source: Mapped[str] = mapped_column(
        String(20),
        default=DataSource.MASTOC.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relations
    climbs: Mapped[list["Climb"]] = relationship(back_populates="setter")

    def __repr__(self) -> str:
        return f"<User {self.full_name}>"
