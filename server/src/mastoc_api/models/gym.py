"""
Modèle Gym (salle d'escalade).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base
from mastoc_api.models.base import DataSource


class Gym(Base):
    """Salle d'escalade."""

    __tablename__ = "gyms"

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
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_string: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(
        String(20),
        default=DataSource.MASTOC.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # Relations
    faces: Mapped[list["Face"]] = relationship(back_populates="gym")

    def __repr__(self) -> str:
        return f"<Gym {self.display_name}>"
