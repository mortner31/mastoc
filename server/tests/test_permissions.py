"""
Tests pour les permissions et l'authentification.

Couvre les scenarios:
- API Key requise pour endpoints proteges
- JWT requis pour endpoints utilisateurs
- Admin requis pour endpoints admin
- Combinaisons JWT + API Key
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
from mastoc_api.models import User
from mastoc_api.models.base import UserRole


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


_test_db = None


def override_get_db():
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
    """DB pour les tests."""
    global _test_db
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


@pytest.fixture(scope="function")
def client_dev_mode(db_session):
    """Client en mode dev (sans API Key configuree)."""
    os.environ.pop("API_KEY", None)
    get_settings.cache_clear()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture(scope="function")
def client_prod_mode(db_session):
    """Client en mode prod (avec API Key configuree)."""
    os.environ["API_KEY"] = "secret-api-key-12345"
    get_settings.cache_clear()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    os.environ.pop("API_KEY", None)
    get_settings.cache_clear()


@pytest.fixture
def user_token(client_dev_mode, db_session):
    """Cree un user normal et retourne son token."""
    client_dev_mode.post("/api/auth/register", json={
        "email": "user@example.com",
        "username": "normaluser",
        "password": "password123",
        "full_name": "Normal User"
    })
    response = client_dev_mode.post("/api/auth/login", data={
        "username": "normaluser",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client_dev_mode, db_session):
    """Cree un admin et retourne son token."""
    client_dev_mode.post("/api/auth/register", json={
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "password123",
        "full_name": "Admin User"
    })
    user = db_session.query(User).filter(User.email == "admin@example.com").first()
    user.role = UserRole.ADMIN
    db_session.commit()

    response = client_dev_mode.post("/api/auth/login", data={
        "username": "adminuser",
        "password": "password123"
    })
    return response.json()["access_token"]


# === Tests Dev Mode (pas d'API Key) ===

def test_dev_mode_api_accessible(client_dev_mode):
    """En dev mode, API accessible sans API Key."""
    response = client_dev_mode.get("/api/sync/stats")
    assert response.status_code == 200


def test_dev_mode_climbs_accessible(client_dev_mode):
    """En dev mode, climbs accessible sans API Key."""
    response = client_dev_mode.get("/api/climbs")
    assert response.status_code == 200


# === Tests Prod Mode (API Key requise) ===

def test_prod_mode_without_key_returns_401(client_prod_mode):
    """En prod mode, 401 sans API Key."""
    response = client_prod_mode.get("/api/sync/stats")
    assert response.status_code == 401


def test_prod_mode_wrong_key_returns_403(client_prod_mode):
    """En prod mode, 403 avec mauvaise API Key."""
    response = client_prod_mode.get(
        "/api/sync/stats",
        headers={"X-API-Key": "wrong-key"}
    )
    assert response.status_code == 403


def test_prod_mode_correct_key_returns_200(client_prod_mode):
    """En prod mode, 200 avec bonne API Key."""
    response = client_prod_mode.get(
        "/api/sync/stats",
        headers={"X-API-Key": "secret-api-key-12345"}
    )
    assert response.status_code == 200


# === Tests JWT requis ===

def test_jwt_required_users_me(client_dev_mode):
    """GET /users/me requiert JWT."""
    response = client_dev_mode.get("/api/users/me")
    assert response.status_code == 401


def test_jwt_valid_access(client_dev_mode, user_token):
    """JWT valide donne acces."""
    response = client_dev_mode.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 200


def test_jwt_invalid_returns_401(client_dev_mode):
    """JWT invalide retourne 401."""
    response = client_dev_mode.get(
        "/api/users/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401


# === Tests Admin requis ===

def test_admin_only_list_users_forbidden_for_user(client_dev_mode, user_token):
    """GET /users interdit aux users normaux."""
    response = client_dev_mode.get(
        "/api/users",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 403


def test_admin_only_list_users_allowed_for_admin(client_dev_mode, admin_token):
    """GET /users autorise pour admin."""
    response = client_dev_mode.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
