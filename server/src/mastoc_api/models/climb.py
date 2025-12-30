"""
Modèle Climb (bloc d'escalade).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, Float, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base
from mastoc_api.models.base import DataSource


class Climb(Base):
    """Bloc d'escalade."""

    __tablename__ = "climbs"

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
        comment="Mapping vers Stokt (NULL si créé sur mastoc)"
    )
    face_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("faces.id"),
        nullable=False
    )
    setter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    holds_list: Mapped[str] = mapped_column(Text, nullable=False)
    mirror_holds_list: Mapped[str | None] = mapped_column(Text)
    grade_font: Mapped[str | None] = mapped_column(String(10))
    grade_ircra: Mapped[float | None] = mapped_column(Float)
    feet_rule: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)
    is_benchmark: Mapped[bool] = mapped_column(Boolean, default=False)

    # Stats (copiées depuis Stokt)
    climbed_by: Mapped[int] = mapped_column(Integer, default=0)
    total_likes: Mapped[int] = mapped_column(Integer, default=0)
    total_comments: Mapped[int] = mapped_column(Integer, default=0)

    # Métadonnées
    source: Mapped[str] = mapped_column(
        String(20),
        default=DataSource.MASTOC.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    synced_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        comment="Dernière sync avec Stokt"
    )

    # Données custom (mastoc only)
    personal_notes: Mapped[str | None] = mapped_column(Text)
    personal_rating: Mapped[int | None] = mapped_column(Integer)
    is_project: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relations
    face: Mapped["Face"] = relationship(back_populates="climbs")
    setter: Mapped["User | None"] = relationship(back_populates="climbs")

    def __repr__(self) -> str:
        return f"<Climb {self.name} ({self.grade_font})>"
