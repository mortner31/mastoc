"""
Tests pour le gestionnaire d'authentification AuthManager.
"""

import json
import time
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile

from mastoc.core.auth import AuthManager, AuthError, TokenInfo, UserProfile


@pytest.fixture
def temp_auth_file(tmp_path):
    """Cree un fichier auth temporaire."""
    auth_file = tmp_path / "auth.json"
    return auth_file


@pytest.fixture
def auth_manager(temp_auth_file):
    """AuthManager avec fichier temporaire."""
    manager = AuthManager(base_url="https://test.example.com")
    manager.AUTH_FILE = temp_auth_file
    return manager


@pytest.fixture
def mock_login_response():
    """Reponse mock pour login."""
    return {
        "access_token": "test-access-token",
        "refresh_token": "test-refresh-token",
        "expires_in": 86400,
        "user_id": "user-123",
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "role": "user",
    }


# === Tests Login ===

def test_login_success(auth_manager, mock_login_response):
    """Login reussi."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response

        result = auth_manager.login("test@example.com", "password123")

        assert result is True
        assert auth_manager.is_authenticated
        assert auth_manager.current_user.email == "test@example.com"


def test_login_wrong_password(auth_manager):
    """Login avec mauvais mot de passe."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {
            "detail": "Identifiants incorrects"
        }

        with pytest.raises(AuthError) as exc:
            auth_manager.login("test@example.com", "wrongpassword")

        assert "incorrect" in str(exc.value).lower()


def test_login_user_not_found(auth_manager):
    """Login utilisateur inexistant."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 401
        mock_post.return_value.json.return_value = {
            "detail": "Utilisateur non trouve"
        }

        with pytest.raises(AuthError):
            auth_manager.login("nobody@example.com", "password")


def test_login_network_error(auth_manager):
    """Login avec erreur reseau."""
    import requests as req
    with patch("requests.post") as mock_post:
        mock_post.side_effect = req.RequestException("Connection refused")

        with pytest.raises(AuthError) as exc:
            auth_manager.login("test@example.com", "password")

        assert "connexion" in str(exc.value).lower()


# === Tests Register ===

def test_register_success(auth_manager):
    """Inscription reussie."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 201
        mock_post.return_value.json.return_value = {
            "id": "user-456",
            "email": "new@example.com",
            "username": "newuser",
            "full_name": "New User",
        }

        profile = auth_manager.register(
            email="new@example.com",
            username="newuser",
            password="password123",
            full_name="New User"
        )

        assert profile.email == "new@example.com"
        assert profile.username == "newuser"


def test_register_duplicate_email(auth_manager):
    """Inscription avec email deja pris."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "detail": "Email deja utilise"
        }

        with pytest.raises(AuthError) as exc:
            auth_manager.register(
                email="existing@example.com",
                username="newuser",
                password="password123",
                full_name="New User"
            )

        assert "email" in str(exc.value).lower()


# === Tests Token Persistence ===

def test_token_persistence_save(auth_manager, mock_login_response, temp_auth_file):
    """Les tokens sont sauvegardes apres login."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response

        auth_manager.login("test@example.com", "password123")

    assert temp_auth_file.exists()
    data = json.loads(temp_auth_file.read_text())
    assert data["access_token"] == "test-access-token"
    assert data["email"] == "test@example.com"


def test_token_persistence_load(temp_auth_file):
    """Les tokens sont charges au demarrage."""
    # Preparer le fichier
    token_data = {
        "access_token": "saved-token",
        "refresh_token": "saved-refresh",
        "expires_at": time.time() + 3600,
        "user_id": "user-789",
        "email": "saved@example.com",
        "username": "saveduser",
        "full_name": "Saved User",
        "role": "user",
    }
    temp_auth_file.parent.mkdir(parents=True, exist_ok=True)
    temp_auth_file.write_text(json.dumps(token_data))

    # Creer le manager
    manager = AuthManager(base_url="https://test.example.com")
    manager.AUTH_FILE = temp_auth_file
    manager._load_tokens()

    assert manager.is_authenticated
    assert manager.current_user.email == "saved@example.com"


# === Tests Token Refresh ===

def test_token_refresh_success(auth_manager, mock_login_response):
    """Refresh token reussi."""
    # D'abord login
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response
        auth_manager.login("test@example.com", "password123")

    # Puis refresh
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            "access_token": "new-access-token",
            "refresh_token": "new-refresh-token",
            "expires_in": 86400,
        }

        result = auth_manager.refresh()

        assert result is True
        assert auth_manager._token_info.access_token == "new-access-token"


def test_token_refresh_expired(auth_manager, mock_login_response):
    """Refresh avec token expire -> logout."""
    # D'abord login
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response
        auth_manager.login("test@example.com", "password123")

    # Puis refresh echoue
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 401

        result = auth_manager.refresh()

        assert result is False
        assert not auth_manager.is_authenticated


# === Tests Logout ===

def test_logout_clears_tokens(auth_manager, mock_login_response, temp_auth_file):
    """Logout supprime les tokens."""
    # Login d'abord
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response
        auth_manager.login("test@example.com", "password123")

    assert auth_manager.is_authenticated

    # Logout
    auth_manager.logout()

    assert not auth_manager.is_authenticated
    assert auth_manager.current_user is None
    assert not temp_auth_file.exists()


# === Tests Profile ===

def test_get_profile_authenticated(auth_manager, mock_login_response):
    """Get profile quand authentifie."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response
        auth_manager.login("test@example.com", "password123")

    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": "user-123",
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "role": "user",
            "avatar_path": "/avatars/user-123.jpg",
        }

        profile = auth_manager.get_profile()

        assert profile.email == "test@example.com"
        assert profile.avatar_path == "/avatars/user-123.jpg"


def test_get_profile_not_authenticated(auth_manager):
    """Get profile sans authentification."""
    profile = auth_manager.get_profile()
    assert profile is None


# === Tests Change Password ===

def test_change_password_success(auth_manager, mock_login_response):
    """Changement de mot de passe reussi."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response
        auth_manager.login("test@example.com", "password123")

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200

        result = auth_manager.change_password("password123", "newpassword456")

        assert result is True


def test_change_password_wrong_current(auth_manager, mock_login_response):
    """Changement avec mauvais mot de passe actuel."""
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_login_response
        auth_manager.login("test@example.com", "password123")

    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {
            "detail": "Mot de passe actuel incorrect"
        }

        with pytest.raises(AuthError) as exc:
            auth_manager.change_password("wrongpassword", "newpassword456")

        assert "incorrect" in str(exc.value).lower()
