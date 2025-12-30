"""
Modèle IdMapping (audit des synchronisations).
"""

import uuid
from datetime import datetime
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base


class IdMapping(Base):
    """Table de mapping explicite pour audit."""

    __tablename__ = "id_mappings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="climb, list, user, face, hold"
    )
    mastoc_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    stokt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    sync_direction: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="stokt_to_mastoc ou mastoc_to_stokt"
    )
    synced_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    def __repr__(self) -> str:
        return f"<IdMapping {self.entity_type} {self.mastoc_id} <-> {self.stokt_id}>"
