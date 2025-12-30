"""
Tests pour l'authentification par API Key.
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


# Base de données SQLite en mémoire pour les tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client_no_auth():
    """Client sans API Key configurée (dev mode)."""
    # S'assurer que API_KEY n'est pas définie
    os.environ.pop("API_KEY", None)
    get_settings.cache_clear()

    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture(scope="function")
def client_with_auth():
    """Client avec API Key configurée."""
    os.environ["API_KEY"] = "test-secret-key-12345"
    get_settings.cache_clear()

    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    os.environ.pop("API_KEY", None)
    get_settings.cache_clear()


# === Tests sans auth (dev mode) ===

def test_health_public(client_no_auth):
    """Health endpoint est toujours public."""
    response = client_no_auth.get("/health")
    assert response.status_code == 200


def test_api_without_key_dev_mode(client_no_auth):
    """En dev mode (pas d'API_KEY), l'API est accessible."""
    response = client_no_auth.get("/api/sync/stats")
    assert response.status_code == 200


# === Tests avec auth activée ===

def test_health_still_public_with_auth(client_with_auth):
    """Health reste public même avec auth activée."""
    response = client_with_auth.get("/health")
    assert response.status_code == 200


def test_api_without_key_returns_401(client_with_auth):
    """Sans API Key, retourne 401."""
    response = client_with_auth.get("/api/sync/stats")
    assert response.status_code == 401
    assert "API Key manquante" in response.json()["detail"]


def test_api_with_wrong_key_returns_403(client_with_auth):
    """Avec mauvaise API Key, retourne 403."""
    response = client_with_auth.get(
        "/api/sync/stats",
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 403
    assert "API Key invalide" in response.json()["detail"]


def test_api_with_correct_key_returns_200(client_with_auth):
    """Avec bonne API Key, retourne 200."""
    response = client_with_auth.get(
        "/api/sync/stats",
        headers={"X-API-Key": "test-secret-key-12345"}
    )
    assert response.status_code == 200


def test_climbs_protected(client_with_auth):
    """Endpoint climbs est protégé."""
    # Sans key
    response = client_with_auth.get("/api/climbs")
    assert response.status_code == 401

    # Avec key
    response = client_with_auth.get(
        "/api/climbs",
        headers={"X-API-Key": "test-secret-key-12345"}
    )
    assert response.status_code == 200


def test_holds_protected(client_with_auth):
    """Endpoint holds est protégé."""
    response = client_with_auth.get("/api/holds")
    assert response.status_code == 401


def test_sync_import_protected(client_with_auth):
    """Endpoints d'import sont protégés."""
    response = client_with_auth.post(
        "/api/sync/import/gym",
        json={"stokt_id": "test", "display_name": "Test"}
    )
    assert response.status_code == 401
