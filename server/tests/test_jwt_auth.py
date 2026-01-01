"""
Tests pour l'authentification JWT (register, login, refresh, etc.).
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
def client():
    """Client de test avec DB fraîche (dev mode, pas d'API Key)."""
    os.environ.pop("API_KEY", None)
    get_settings.cache_clear()

    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()
    get_settings.cache_clear()


# === Tests Register ===

def test_register_success(client):
    """Inscription réussie."""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert data["full_name"] == "Test User"
    assert "id" in data


def test_register_duplicate_email(client):
    """Email déjà utilisé."""
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "user1",
        "password": "password123",
        "full_name": "User 1"
    })
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "user2",
        "password": "password123",
        "full_name": "User 2"
    })
    assert response.status_code == 400
    assert "email" in response.json()["detail"].lower()


def test_register_duplicate_username(client):
    """Username déjà pris."""
    client.post("/api/auth/register", json={
        "email": "user1@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "User 1"
    })
    response = client.post("/api/auth/register", json={
        "email": "user2@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "User 2"
    })
    assert response.status_code == 400
    assert "utilisateur" in response.json()["detail"].lower()


def test_register_password_too_short(client):
    """Mot de passe trop court."""
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "short",
        "full_name": "Test User"
    })
    assert response.status_code == 422  # Validation error


def test_register_invalid_email(client):
    """Email invalide."""
    response = client.post("/api/auth/register", json={
        "email": "not-an-email",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    assert response.status_code == 422


# === Tests Login ===

def test_login_success_with_email(client):
    """Login avec email."""
    # Créer le compte
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    # Login
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


def test_login_success_with_username(client):
    """Login avec username."""
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"


def test_login_wrong_password(client):
    """Mauvais mot de passe."""
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    response = client.post("/api/auth/login", data={
        "username": "test@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    """Utilisateur inexistant."""
    response = client.post("/api/auth/login", data={
        "username": "nobody@example.com",
        "password": "password123"
    })
    assert response.status_code == 401


# === Tests Refresh Token ===

def test_refresh_token_success(client):
    """Refresh token valide."""
    # Créer et connecter
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    refresh_token = login_response.json()["refresh_token"]

    # Refresh
    response = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_token_invalid(client):
    """Refresh token invalide."""
    response = client.post("/api/auth/refresh", json={
        "refresh_token": "invalid-token"
    })
    assert response.status_code == 401


# === Tests Protected Endpoints ===

def test_users_me_without_token(client):
    """Accès /users/me sans token."""
    response = client.get("/api/users/me")
    assert response.status_code == 401


def test_users_me_with_token(client):
    """Accès /users/me avec token."""
    # Créer et connecter
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Accéder au profil
    response = client.get("/api/users/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


# === Tests Password Change ===

def test_change_password_success(client):
    """Changement de mot de passe."""
    # Créer et connecter
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    # Changer le mot de passe
    response = client.post("/api/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "password123",
            "new_password": "newpassword456"
        }
    )
    assert response.status_code == 200

    # Vérifier qu'on peut se connecter avec le nouveau
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "newpassword456"
    })
    assert response.status_code == 200


def test_change_password_wrong_current(client):
    """Changement avec mauvais mot de passe actuel."""
    client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    })
    login_response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "password123"
    })
    token = login_response.json()["access_token"]

    response = client.post("/api/users/me/password",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "current_password": "wrongpassword",
            "new_password": "newpassword456"
        }
    )
    assert response.status_code == 400
