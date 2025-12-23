"""
Tests pour les méthodes CRUD de l'API StoktAPI (TODO 10).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mastoc.api.client import StoktAPI, StoktAPIError, AuthenticationError
from mastoc.api.models import Climb


class TestCreateClimb:
    """Tests pour create_climb()."""

    def test_create_climb_success(self):
        """Test création de climb réussie."""
        api = StoktAPI()
        api.token = "test-token"

        # Mock response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "new-climb-id",
            "name": "Test Bloc",
            "holdsList": "S1 S2 O3 T4",
            "feetRule": "",
            "faceId": "face-123",
            "wallId": "wall-456",
            "wallName": "Mur Principal",
            "dateCreated": "2025-12-23",
            "isPrivate": False,
        }

        with patch.object(api.session, 'post', return_value=mock_response):
            payload = {
                "name": "Test Bloc",
                "holdsList": {"start": ["1", "2"], "others": ["3"], "top": ["4"], "feetOnly": []},
                "grade": {"gradingSystem": "Font", "value": "6a"},
            }
            result = api.create_climb("face-123", payload)

            assert isinstance(result, Climb)
            assert result.id == "new-climb-id"
            assert result.name == "Test Bloc"

    def test_create_climb_with_all_options(self):
        """Test création avec toutes les options."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "climb-full",
            "name": "Bloc Complet",
            "holdsList": "S1 S2 O3 F4 T5",
            "feetRule": "Free feet",
            "faceId": "face-123",
            "wallId": "wall-456",
            "wallName": "Mur",
            "dateCreated": "2025-12-23",
            "isPrivate": True,
        }

        with patch.object(api.session, 'post', return_value=mock_response):
            payload = {
                "name": "Bloc Complet",
                "holdsList": {
                    "start": ["1", "2"],
                    "others": ["3"],
                    "top": ["5"],
                    "feetOnly": ["4"]
                },
                "grade": {"gradingSystem": "Font", "value": "7a"},
                "description": "Un bloc difficile",
                "isPrivate": True,
                "feetRule": "Free feet",
            }
            result = api.create_climb("face-123", payload)

            assert result.name == "Bloc Complet"
            assert result.is_private == True
            assert result.feet_rule == "Free feet"

    def test_create_climb_auth_required(self):
        """Test que l'authentification est requise."""
        api = StoktAPI()
        # Pas de token

        with pytest.raises(AuthenticationError):
            api.create_climb("face-123", {"name": "Test"})

    def test_create_climb_sends_json(self):
        """Test que le payload est envoyé en JSON."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "new-id",
            "name": "Test",
            "holdsList": "S1 S2 T3",
            "feetRule": "",
            "faceId": "face-123",
            "wallId": "wall-456",
            "wallName": "Mur",
            "dateCreated": "2025-12-23",
        }

        with patch.object(api.session, 'post', return_value=mock_response) as mock_post:
            payload = {"name": "Test"}
            api.create_climb("face-123", payload)

            # Vérifier que json= est utilisé (pas data=)
            call_kwargs = mock_post.call_args[1]
            assert "json" in call_kwargs
            assert call_kwargs["json"] == payload


class TestUpdateClimb:
    """Tests pour update_climb()."""

    def test_update_climb_success(self):
        """Test modification de climb réussie."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "climb-123",
            "name": "Nouveau Nom",
            "holdsList": "S1 S2 T3",
            "feetRule": "",
            "faceId": "face-123",
            "wallId": "wall-456",
            "wallName": "Mur",
            "dateCreated": "2025-12-23",
        }

        with patch.object(api.session, 'patch', return_value=mock_response):
            payload = {"name": "Nouveau Nom"}
            result = api.update_climb("face-123", "climb-123", payload)

            assert result.name == "Nouveau Nom"

    def test_update_climb_partial(self):
        """Test modification partielle (un seul champ)."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "climb-123",
            "name": "Original",
            "holdsList": "S1 S2 T3",
            "feetRule": "New feet rule",
            "faceId": "face-123",
            "wallId": "wall-456",
            "wallName": "Mur",
            "dateCreated": "2025-12-23",
        }

        with patch.object(api.session, 'patch', return_value=mock_response):
            # Modifier seulement feetRule
            payload = {"feetRule": "New feet rule"}
            result = api.update_climb("face-123", "climb-123", payload)

            assert result.feet_rule == "New feet rule"


class TestDeleteClimb:
    """Tests pour delete_climb()."""

    def test_delete_climb_success(self):
        """Test suppression réussie."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 204

        with patch.object(api.session, 'delete', return_value=mock_response):
            result = api.delete_climb("climb-123")
            assert result == True

    def test_delete_climb_endpoint(self):
        """Test que le bon endpoint est appelé."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 204

        with patch.object(api.session, 'delete', return_value=mock_response) as mock_delete:
            api.delete_climb("climb-xyz")

            # Vérifier l'URL
            call_args = mock_delete.call_args
            assert "api/climbs/climb-xyz" in call_args[0][0]


class TestSetClimbPrivacy:
    """Tests pour set_climb_privacy()."""

    def test_set_private(self):
        """Test passage en privé."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(api.session, 'patch', return_value=mock_response) as mock_patch:
            result = api.set_climb_privacy("climb-123", is_private=True)

            assert result == True
            call_kwargs = mock_patch.call_args[1]
            assert call_kwargs["json"] == {"is_private": True}

    def test_set_public(self):
        """Test passage en public."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200

        with patch.object(api.session, 'patch', return_value=mock_response) as mock_patch:
            result = api.set_climb_privacy("climb-123", is_private=False)

            assert result == True
            call_kwargs = mock_patch.call_args[1]
            assert call_kwargs["json"] == {"is_private": False}


class TestGetClimbPermissions:
    """Tests pour get_climb_permissions()."""

    def test_get_permissions(self):
        """Test récupération des permissions."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "canDelete": True,
            "canEditHolds": True,
            "canEditNameAndGrade": True,
            "canHide": False,
            "canSetPrivate": True,
            "canSetPublic": False,
        }

        with patch.object(api.session, 'get', return_value=mock_response):
            result = api.get_climb_permissions("climb-123")

            assert result["canDelete"] == True
            assert result["canEditHolds"] == True
            assert result["canSetPublic"] == False

    def test_get_permissions_no_edit(self):
        """Test permissions sans droits d'édition."""
        api = StoktAPI()
        api.token = "test-token"

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "canDelete": False,
            "canEditHolds": False,
            "canEditNameAndGrade": False,
            "canHide": False,
            "canSetPrivate": False,
            "canSetPublic": False,
        }

        with patch.object(api.session, 'get', return_value=mock_response):
            result = api.get_climb_permissions("climb-xyz")

            assert all(not v for v in result.values())
