"""
Configuration des tests pytest pour mastoc-api.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mastoc_api.database import Base, get_db
from mastoc_api.main import app
from mastoc_api.config import get_settings


# Base de donnees SQLite en memoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Session partagee pour les tests (permet aux fixtures de partager les donnees)
_test_db = None


def override_get_db():
    """Surcharge pour utiliser la DB de test."""
    global _test_db
    if _test_db is not None:
        yield _test_db
    else:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()


@pytest.fixture(scope="function")
def db_session():
    """Cree une DB fraiche pour chaque test."""
    global _test_db
    # Nettoyer settings cache
    os.environ.pop("API_KEY", None)
    get_settings.cache_clear()

    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    _test_db = db
    yield db
    _test_db = None
    db.close()
    Base.metadata.drop_all(bind=engine)
    get_settings.cache_clear()


# Alias pour compatibilite
@pytest.fixture(scope="function")
def db(db_session):
    """Alias de db_session."""
    return db_session


@pytest.fixture(scope="function")
def client(db_session):
    """Client de test avec DB fraiche."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def api_key_header():
    """Header API Key pour les tests (dev mode = pas de verification)."""
    return {"X-API-Key": "test-key"}
