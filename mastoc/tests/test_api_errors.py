"""
Tests pour la gestion des erreurs API et configuration.

Ces tests verifient la configuration de MastocAPI et AuthenticationError.
"""

import pytest
from unittest.mock import Mock, patch
import requests

from mastoc.api.railway_client import MastocAPI, RailwayConfig, MastocAPIError, AuthenticationError


# === Tests Configuration ===

def test_api_key_in_headers():
    """API Key est incluse dans les headers."""
    config = RailwayConfig(
        base_url="https://test.example.com",
        api_key="my-secret-key"
    )
    api = MastocAPI(config)

    assert api.session.headers.get("X-API-Key") == "my-secret-key"


def test_is_authenticated_with_api_key():
    """is_authenticated retourne True avec API Key."""
    config = RailwayConfig(api_key="test-key")
    api = MastocAPI(config)

    assert api.is_authenticated() is True


def test_is_authenticated_without_api_key():
    """is_authenticated retourne False sans API Key."""
    config = RailwayConfig(api_key=None)
    api = MastocAPI(config)

    assert api.is_authenticated() is False


def test_set_api_key():
    """set_api_key met a jour les headers."""
    config = RailwayConfig(api_key=None)
    api = MastocAPI(config)

    assert api.session.headers.get("X-API-Key") is None

    api.set_api_key("new-key")

    assert api.session.headers.get("X-API-Key") == "new-key"
    assert api.config.api_key == "new-key"


def test_default_config():
    """Config par defaut utilise Railway production."""
    api = MastocAPI()

    assert "railway.app" in api.config.base_url


def test_url_construction():
    """URL est construite correctement."""
    config = RailwayConfig(base_url="https://test.example.com")
    api = MastocAPI(config)

    url = api._url("api/climbs")

    assert url == "https://test.example.com/api/climbs"


def test_url_with_trailing_slash():
    """URL fonctionne avec ou sans trailing slash."""
    config = RailwayConfig(base_url="https://test.example.com/")
    api = MastocAPI(config)

    # La construction d'URL fonctionne meme avec trailing slash
    url = api._url("api/climbs")
    assert "api/climbs" in url


# === Tests Exceptions ===

def test_authentication_error_is_mastoc_api_error():
    """AuthenticationError herite de MastocAPIError."""
    assert issubclass(AuthenticationError, MastocAPIError)


def test_authentication_error_message():
    """AuthenticationError a un message."""
    error = AuthenticationError("Test error")
    assert str(error) == "Test error"


def test_mastoc_api_error_message():
    """MastocAPIError a un message."""
    error = MastocAPIError("API failed")
    assert str(error) == "API failed"


# === Tests Auth Manager Integration ===

def test_set_auth_manager():
    """set_auth_manager definit l'auth manager."""
    api = MastocAPI()

    mock_auth = Mock()
    mock_auth.access_token = "jwt-token"
    mock_auth.is_authenticated = True

    api.set_auth_manager(mock_auth)

    assert api._auth_manager == mock_auth


def test_current_user_from_auth_manager():
    """current_user vient de l'auth manager."""
    api = MastocAPI()

    mock_user = Mock()
    mock_user.full_name = "Test User"

    mock_auth = Mock()
    mock_auth.current_user = mock_user

    api.set_auth_manager(mock_auth)

    assert api.current_user == mock_user


def test_current_user_none_without_auth_manager():
    """current_user est None sans auth manager."""
    api = MastocAPI()

    assert api.current_user is None
