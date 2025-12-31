"""
Modèle User (utilisateur).
"""

import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from mastoc_api.database import Base
from mastoc_api.models.base import DataSource, UserRole


class User(Base):
    """Utilisateur."""

    __tablename__ = "users"

    # Identifiants
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

    # Identité
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_path: Mapped[str | None] = mapped_column(String(500))

    # Auth mastoc (optionnel pour users importés de Stokt)
    email: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )
    username: Mapped[str | None] = mapped_column(
        String(100),
        unique=True,
        nullable=True,
        index=True
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[str] = mapped_column(
        String(20),
        default=UserRole.USER.value
    )

    # Métadonnées
    source: Mapped[str] = mapped_column(
        String(20),
        default=DataSource.MASTOC.value
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        onupdate=datetime.utcnow
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Reset password
    reset_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reset_token_expires: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relations
    climbs: Mapped[list["Climb"]] = relationship(back_populates="setter")

    def __repr__(self) -> str:
        return f"<User {self.full_name}>"

    @property
    def is_mastoc_user(self) -> bool:
        """True si l'utilisateur a un compte mastoc (email + password)."""
        return self.email is not None and self.password_hash is not None

    @property
    def is_admin(self) -> bool:
        """True si l'utilisateur est admin."""
        return self.role == UserRole.ADMIN.value
