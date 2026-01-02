"""
Modèle Hold (prise physique sur le mur).
"""

import uuid
from sqlalchemy import Integer, String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base


class Hold(Base):
    """Prise physique sur le mur."""

    __tablename__ = "holds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    stokt_id: Mapped[int | None] = mapped_column(
        Integer,
        unique=True,
        nullable=True,
        index=True,
        comment="ID Stokt (INTEGER sur Stokt)"
    )
    face_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("faces.id"),
        nullable=False
    )
    polygon_str: Mapped[str] = mapped_column(String(2000), nullable=False)
    centroid_x: Mapped[float | None] = mapped_column(Float)
    centroid_y: Mapped[float | None] = mapped_column(Float)
    path_str: Mapped[str | None] = mapped_column(String(5000))
    area: Mapped[float | None] = mapped_column(Float)
    # Tape lines for START holds
    center_tape_str: Mapped[str | None] = mapped_column(String(200))
    right_tape_str: Mapped[str | None] = mapped_column(String(200))
    left_tape_str: Mapped[str | None] = mapped_column(String(200))

    # Relations
    face: Mapped["Face"] = relationship(back_populates="holds")

    def __repr__(self) -> str:
        return f"<Hold {self.id} (stokt:{self.stokt_id})>"
