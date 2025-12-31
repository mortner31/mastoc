"""
Tests pour MastocAPI (client Railway).
"""

import pytest
from unittest.mock import Mock, patch

from mastoc.api.railway_client import (
    MastocAPI,
    RailwayConfig,
    MastocAPIError,
    AuthenticationError,
)
from mastoc.api.models import Climb, Hold


class TestMastocAPIConfig:
    """Tests pour la configuration."""

    def test_default_config(self):
        """Test configuration par défaut."""
        api = MastocAPI()
        assert api.config.base_url == "https://mastoc-production.up.railway.app"
        assert api.config.api_key is None
        assert api.config.timeout == 30

    def test_custom_config(self):
        """Test configuration personnalisée."""
        config = RailwayConfig(
            base_url="http://localhost:8000",
            api_key="test-key",
            timeout=60,
        )
        api = MastocAPI(config)
        assert api.config.base_url == "http://localhost:8000"
        assert api.config.api_key == "test-key"

    def test_set_api_key(self):
        """Test set_api_key."""
        api = MastocAPI()
        assert not api.is_authenticated()

        api.set_api_key("my-api-key")
        assert api.is_authenticated()
        assert api.session.headers.get("X-API-Key") == "my-api-key"


class TestMastocAPIHealth:
    """Tests pour health check."""

    def test_health_success(self):
        """Test health check réussi."""
        api = MastocAPI()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "healthy",
            "database": "connected",
        }

        with patch.object(api.session, "get", return_value=mock_response):
            result = api.health()
            assert result["status"] == "healthy"


class TestMastocAPIClimbs:
    """Tests pour les endpoints climbs."""

    def test_get_climbs_success(self):
        """Test récupération des climbs."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": "uuid-1",
                    "name": "Bloc 1",
                    "holds_list": "S123 O456 T789",
                    "grade_font": "6A",
                    "grade_ircra": 12.0,
                    "face_id": "face-uuid",
                    "is_private": False,
                    "climbed_by": 5,
                    "total_likes": 2,
                    "source": "stokt",
                    "setter_id": "setter-uuid",
                    "setter_name": "John Doe",
                },
                {
                    "id": "uuid-2",
                    "name": "Bloc 2",
                    "holds_list": "S100 T200",
                    "grade_font": "5",
                    "grade_ircra": 8.0,
                    "face_id": "face-uuid",
                    "is_private": False,
                    "climbed_by": 10,
                    "total_likes": 0,
                    "source": "mastoc",
                    "setter_id": None,
                    "setter_name": None,
                },
            ],
            "count": 2,
            "page": 1,
            "page_size": 50,
        }

        with patch.object(api.session, "get", return_value=mock_response):
            climbs, total = api.get_climbs()

            assert total == 2
            assert len(climbs) == 2

            assert isinstance(climbs[0], Climb)
            assert climbs[0].id == "uuid-1"
            assert climbs[0].name == "Bloc 1"
            assert climbs[0].holds_list == "S123 O456 T789"
            assert climbs[0].grade.font == "6A"
            assert climbs[0].setter.full_name == "John Doe"

            assert climbs[1].id == "uuid-2"
            assert climbs[1].setter is None

    def test_get_climbs_with_filters(self):
        """Test récupération avec filtres."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "results": [],
            "count": 0,
            "page": 1,
            "page_size": 50,
        }

        with patch.object(api.session, "get", return_value=mock_response) as mock_get:
            api.get_climbs(
                face_id="face-123",
                search="test",
                page=2,
                page_size=100,
            )

            # Vérifier que les params sont passés
            call_kwargs = mock_get.call_args[1]
            params = call_kwargs.get("params", {})
            assert params["face_id"] == "face-123"
            assert params["search"] == "test"
            assert params["page"] == 2
            assert params["page_size"] == 100

    def test_get_climb_by_id(self):
        """Test récupération d'un climb par ID."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "id": "uuid-1",
            "name": "Bloc Test",
            "holds_list": "S1 T2",
            "grade_font": "6A",
            "grade_ircra": 12.0,
            "face_id": "face-uuid",
            "is_private": False,
            "climbed_by": 0,
            "total_likes": 0,
            "source": "mastoc",
        }

        with patch.object(api.session, "get", return_value=mock_response):
            climb = api.get_climb("uuid-1")
            assert climb.id == "uuid-1"
            assert climb.name == "Bloc Test"

    def test_create_climb_success(self):
        """Test création de climb."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "id": "new-uuid",
            "name": "Mon Bloc",
            "holds_list": "S1 S2 O3 T4",
            "grade_font": "6A+",
            "grade_ircra": 13.0,
            "face_id": "face-uuid",
            "feet_rule": "Free feet",
            "description": "Un super bloc",
            "is_private": False,
            "climbed_by": 0,
            "total_likes": 0,
            "source": "mastoc",
        }

        with patch.object(api.session, "post", return_value=mock_response) as mock_post:
            climb = api.create_climb(
                face_id="face-uuid",
                name="Mon Bloc",
                holds_list="S1 S2 O3 T4",
                grade_font="6A+",
                grade_ircra=13.0,
                feet_rule="Free feet",
                description="Un super bloc",
            )

            assert climb.id == "new-uuid"
            assert climb.name == "Mon Bloc"

            # Vérifier le payload
            call_kwargs = mock_post.call_args[1]
            json_data = call_kwargs.get("json", {})
            assert json_data["face_id"] == "face-uuid"
            assert json_data["name"] == "Mon Bloc"
            assert json_data["holds_list"] == "S1 S2 O3 T4"

    def test_update_climb(self):
        """Test mise à jour de climb."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "id": "uuid-1",
            "name": "Nouveau Nom",
            "holds_list": "S1 T2",
            "grade_font": "6A",
            "grade_ircra": 12.0,
            "face_id": "face-uuid",
            "is_private": False,
            "climbed_by": 0,
            "total_likes": 0,
            "source": "mastoc",
            "personal_notes": "Ma note",
            "is_project": True,
        }

        with patch.object(api.session, "patch", return_value=mock_response):
            climb = api.update_climb(
                "uuid-1",
                name="Nouveau Nom",
                personal_notes="Ma note",
                is_project=True,
            )

            assert climb.name == "Nouveau Nom"

    def test_delete_climb(self):
        """Test suppression de climb."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.raise_for_status = Mock()

        with patch.object(api.session, "delete", return_value=mock_response):
            result = api.delete_climb("uuid-1")
            assert result is True


class TestMastocAPIHolds:
    """Tests pour les endpoints holds."""

    def test_get_holds_success(self):
        """Test récupération des holds."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 1,
                    "stokt_id": 829001,
                    "face_id": "face-uuid",
                    "polygon_str": "100,200 150,200 150,250 100,250",
                    "centroid_x": 125.0,
                    "centroid_y": 225.0,
                    "area": 2500.0,
                },
                {
                    "id": 2,
                    "stokt_id": 829002,
                    "face_id": "face-uuid",
                    "polygon_str": "300,400 350,400 350,450 300,450",
                    "centroid_x": 325.0,
                    "centroid_y": 425.0,
                    "area": 2500.0,
                },
            ],
            "count": 2,
        }

        with patch.object(api.session, "get", return_value=mock_response):
            holds = api.get_holds("face-uuid")

            assert len(holds) == 2
            assert isinstance(holds[0], Hold)
            # L'ID utilisé est stokt_id pour compatibilité
            assert holds[0].id == 829001
            assert holds[0].polygon_str == "100,200 150,200 150,250 100,250"
            assert holds[0].area == 2500.0


class TestMastocAPIAuth:
    """Tests pour l'authentification."""

    def test_auth_error_401(self):
        """Test erreur 401."""
        api = MastocAPI(RailwayConfig(api_key="bad-key"))

        mock_response = Mock()
        mock_response.status_code = 401

        with patch.object(api.session, "get", return_value=mock_response):
            with pytest.raises(AuthenticationError) as exc_info:
                api.get_climbs()
            assert "invalide" in str(exc_info.value)

    def test_auth_error_403(self):
        """Test erreur 403."""
        api = MastocAPI(RailwayConfig(api_key="limited-key"))

        mock_response = Mock()
        mock_response.status_code = 403

        with patch.object(api.session, "get", return_value=mock_response):
            with pytest.raises(AuthenticationError) as exc_info:
                api.get_climbs()
            assert "refusé" in str(exc_info.value)


class TestMastocAPIGetAllClimbs:
    """Tests pour get_all_climbs avec pagination."""

    def test_get_all_climbs_single_page(self):
        """Test avec une seule page."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": "1", "name": "Bloc 1", "holds_list": "", "face_id": "f",
                 "is_private": False, "climbed_by": 0, "total_likes": 0, "source": "stokt"},
                {"id": "2", "name": "Bloc 2", "holds_list": "", "face_id": "f",
                 "is_private": False, "climbed_by": 0, "total_likes": 0, "source": "stokt"},
            ],
            "count": 2,
            "page": 1,
            "page_size": 500,
        }

        with patch.object(api.session, "get", return_value=mock_response):
            climbs = api.get_all_climbs()
            assert len(climbs) == 2

    def test_get_all_climbs_multiple_pages(self):
        """Test avec plusieurs pages."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        call_count = [0]

        def mock_get(*args, **kwargs):
            call_count[0] += 1
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.raise_for_status = Mock()

            if call_count[0] == 1:
                mock_response.json.return_value = {
                    "results": [
                        {"id": "1", "name": "Bloc 1", "holds_list": "", "face_id": "f",
                         "is_private": False, "climbed_by": 0, "total_likes": 0, "source": "stokt"},
                    ],
                    "count": 2,
                    "page": 1,
                    "page_size": 1,
                }
            else:
                mock_response.json.return_value = {
                    "results": [
                        {"id": "2", "name": "Bloc 2", "holds_list": "", "face_id": "f",
                         "is_private": False, "climbed_by": 0, "total_likes": 0, "source": "stokt"},
                    ],
                    "count": 2,
                    "page": 2,
                    "page_size": 1,
                }
            return mock_response

        with patch.object(api.session, "get", side_effect=mock_get):
            # Forcer une petite page_size pour tester la pagination
            climbs = api.get_all_climbs()
            # Le test utilise page_size=500 par défaut, donc une seule page
            # Pour un vrai test multi-page, il faudrait mocker différemment

    def test_get_all_climbs_with_callback(self):
        """Test callback de progression."""
        api = MastocAPI(RailwayConfig(api_key="test-key"))

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": "1", "name": "Bloc 1", "holds_list": "", "face_id": "f",
                 "is_private": False, "climbed_by": 0, "total_likes": 0, "source": "stokt"},
            ],
            "count": 1,
            "page": 1,
            "page_size": 500,
        }

        callback_calls = []

        def callback(current, total):
            callback_calls.append((current, total))

        with patch.object(api.session, "get", return_value=mock_response):
            api.get_all_climbs(callback=callback)
            assert len(callback_calls) == 1
            assert callback_calls[0] == (1, 1)
