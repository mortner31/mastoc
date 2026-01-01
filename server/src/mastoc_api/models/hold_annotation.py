"""
Modèle HoldAnnotation (annotation de prise par un utilisateur).

ADR-008 : Système d'annotations crowd-sourcées avec consensus.
"""

import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base


class HoldGripType(str, Enum):
    """Type de préhension de la prise."""
    PLAT = "plat"
    REGLETTE = "reglette"
    BI_DOIGT = "bi_doigt"
    TRI_DOIGT = "tri_doigt"
    MONO_DOIGT = "mono_doigt"
    PINCE = "pince"
    COLONNETTE = "colonnette"
    INVERSE = "inverse"
    BAC = "bac"
    PRISE_VOLUME = "prise_volume"
    MICRO = "micro"
    AUTRE = "autre"


class HoldCondition(str, Enum):
    """État de maintenance de la prise."""
    OK = "ok"
    A_BROSSER = "a_brosser"
    SALE = "sale"
    TOURNEE = "tournee"
    USEE = "usee"
    CASSEE = "cassee"


class HoldRelativeDifficulty(str, Enum):
    """Difficulté relative de la prise par rapport au bloc."""
    FACILE = "facile"
    NORMALE = "normale"
    DURE = "dure"


class HoldAnnotation(Base):
    """Annotation d'une prise par un utilisateur."""

    __tablename__ = "hold_annotations"
    __table_args__ = (
        UniqueConstraint("hold_id", "user_id", name="uq_hold_user_annotation"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    hold_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("holds.id"),
        nullable=False,
        index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    # Dimensions d'annotation (toutes optionnelles)
    grip_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Type de préhension"
    )
    condition: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="État de maintenance"
    )
    difficulty: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Difficulté relative"
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Notes libres"
    )

    # Métadonnées
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow
    )

    # Relations
    hold: Mapped["Hold"] = relationship()
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<HoldAnnotation hold={self.hold_id} user={self.user_id}>"
