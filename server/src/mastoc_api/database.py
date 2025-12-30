"""
Configuration de la base de données SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from mastoc_api.config import get_settings


settings = get_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class pour tous les modèles SQLAlchemy."""
    pass


def get_db():
    """Dependency pour obtenir une session DB."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
