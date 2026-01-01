"""
Tests pour les endpoints utilisateurs (/api/users).

Note: Certains tests basiques (users/me, change_password) sont dans test_jwt_auth.py.
Ce fichier couvre les tests additionnels pour une couverture complete.
"""

import io
import pytest

from mastoc_api.models import User
from mastoc_api.models.base import UserRole


@pytest.fixture
def auth_token(client):
    """Cree un utilisateur et retourne son token."""
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
    return response.json()["access_token"]


@pytest.fixture
def admin_token(client, db_session):
    """Cree un admin et retourne son token."""
    # Creer l'utilisateur
    client.post("/api/auth/register", json={
        "email": "admin@example.com",
        "username": "adminuser",
        "password": "password123",
        "full_name": "Admin User"
    })
    # Promouvoir en admin directement dans la DB
    user = db_session.query(User).filter(User.email == "admin@example.com").first()
    user.role = UserRole.ADMIN
    db_session.commit()

    response = client.post("/api/auth/login", data={
        "username": "adminuser",
        "password": "password123"
    })
    return response.json()["access_token"]


# === Tests Update Profile ===

def test_update_profile_success(client, auth_token):
    """Mise a jour du profil reussie."""
    response = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"full_name": "New Name", "username": "newusername"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "New Name"
    assert data["username"] == "newusername"


def test_update_profile_partial(client, auth_token):
    """Mise a jour partielle (seulement full_name)."""
    response = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"full_name": "Only Name Changed"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Only Name Changed"
    assert data["username"] == "testuser"  # Inchange


def test_update_profile_duplicate_username(client, auth_token):
    """Username deja pris par un autre utilisateur."""
    # Creer un autre utilisateur
    client.post("/api/auth/register", json={
        "email": "other@example.com",
        "username": "otherusername",
        "password": "password123",
        "full_name": "Other User"
    })

    # Essayer de prendre son username
    response = client.patch(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_token}"},
        json={"username": "otherusername"}
    )
    assert response.status_code == 400
    assert "utilisateur" in response.json()["detail"].lower()


def test_update_profile_no_auth(client):
    """Mise a jour sans authentification."""
    response = client.patch("/api/users/me", json={"full_name": "New Name"})
    assert response.status_code == 401


# === Tests Avatar Upload ===

def test_upload_avatar_success(client, auth_token):
    """Upload d'avatar reussi."""
    # Creer une image PNG minimale valide
    png_data = (
        b'\x89PNG\r\n\x1a\n'  # PNG signature
        b'\x00\x00\x00\rIHDR'  # IHDR chunk
        b'\x00\x00\x00\x01\x00\x00\x00\x01'  # 1x1 pixels
        b'\x08\x02\x00\x00\x00\x90wS\xde'  # bit depth, color type, etc.
        b'\x00\x00\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18\xd8N'
        b'\x00\x00\x00\x00IEND\xaeB`\x82'  # IEND chunk
    )

    response = client.post(
        "/api/users/me/avatar",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("avatar.png", io.BytesIO(png_data), "image/png")}
    )
    assert response.status_code == 200
    assert "avatar" in response.json()["message"].lower()


def test_upload_avatar_too_large(client, auth_token):
    """Avatar trop volumineux (> 2MB)."""
    # Creer un fichier de 3MB
    large_data = b"x" * (3 * 1024 * 1024)

    response = client.post(
        "/api/users/me/avatar",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("avatar.jpg", io.BytesIO(large_data), "image/jpeg")}
    )
    assert response.status_code == 400
    assert "volumineux" in response.json()["detail"].lower()


def test_upload_avatar_invalid_format(client, auth_token):
    """Format d'avatar non supporte."""
    response = client.post(
        "/api/users/me/avatar",
        headers={"Authorization": f"Bearer {auth_token}"},
        files={"file": ("avatar.bmp", io.BytesIO(b"BM..."), "image/bmp")}
    )
    assert response.status_code == 400
    assert "format" in response.json()["detail"].lower()


def test_upload_avatar_no_auth(client):
    """Upload sans authentification."""
    response = client.post(
        "/api/users/me/avatar",
        files={"file": ("avatar.png", io.BytesIO(b"fake"), "image/png")}
    )
    assert response.status_code == 401


# === Tests Get User by ID ===

def test_get_user_by_id_success(client, auth_token):
    """Recuperer le profil public d'un utilisateur."""
    # D'abord, obtenir l'ID de l'utilisateur courant
    me_response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    user_id = me_response.json()["id"]

    # Recuperer le profil public (pas besoin d'auth)
    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["full_name"] == "Test User"
    # Le profil public ne contient pas l'email
    assert "email" not in data or data.get("email") is None


def test_get_user_by_id_not_found(client):
    """Utilisateur inexistant."""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/api/users/{fake_uuid}")
    assert response.status_code == 404


def test_get_user_avatar_not_found(client, auth_token):
    """Avatar inexistant."""
    me_response = client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    user_id = me_response.json()["id"]

    response = client.get(f"/api/users/{user_id}/avatar")
    assert response.status_code == 404


# === Tests List Users (Admin Only) ===

def test_list_users_admin_only(client, admin_token):
    """Liste des utilisateurs accessible aux admins."""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] >= 1  # Au moins l'admin


def test_list_users_forbidden_for_user(client, auth_token):
    """Liste interdite aux utilisateurs non-admin."""
    response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 403


def test_list_users_search(client, admin_token):
    """Recherche d'utilisateurs."""
    response = client.get(
        "/api/users?search=admin",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    # Devrait trouver l'admin
    assert any("admin" in u["full_name"].lower() or
               "admin" in (u.get("username") or "").lower()
               for u in data["results"])


def test_list_users_pagination(client, admin_token):
    """Pagination de la liste."""
    response = client.get(
        "/api/users?page=1&page_size=10",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 10
