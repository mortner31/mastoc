"""
Modèle Face (configuration de prises d'un mur).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base
from mastoc_api.models.base import DataSource


class Face(Base):
    """Face d'un mur avec configuration de prises."""

    __tablename__ = "faces"

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
    gym_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("gyms.id"),
        nullable=False
    )
    picture_path: Mapped[str] = mapped_column(String(500), nullable=False)
    picture_width: Mapped[int | None] = mapped_column(Integer)
    picture_height: Mapped[int | None] = mapped_column(Integer)
    feet_rules_options: Mapped[dict] = mapped_column(JSON, default=list)
    has_symmetry: Mapped[bool] = mapped_column(Boolean, default=False)
    source: Mapped[str] = mapped_column(
        String(20),
        default=DataSource.MASTOC.value
    )
    synced_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relations
    gym: Mapped["Gym"] = relationship(back_populates="faces")
    holds: Mapped[list["Hold"]] = relationship(back_populates="face")
    climbs: Mapped[list["Climb"]] = relationship(back_populates="face")

    def __repr__(self) -> str:
        return f"<Face {self.id}>"
