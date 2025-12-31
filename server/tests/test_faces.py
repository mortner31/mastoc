"""
Tests pour les endpoints faces.
"""

import uuid
import pytest
from fastapi.testclient import TestClient

from mastoc_api.main import app
from mastoc_api.models import Gym, Face, Hold


@pytest.fixture
def test_gym(db_session):
    """Crée un gym de test."""
    gym = Gym(
        id=uuid.uuid4(),
        name="Test Gym",
        display_name="Test Gym",
        location_string="Test Location",
    )
    db_session.add(gym)
    db_session.commit()
    return gym


@pytest.fixture
def test_face(db_session, test_gym):
    """Crée une face de test."""
    face = Face(
        id=uuid.uuid4(),
        stokt_id=uuid.uuid4(),
        gym_id=test_gym.id,
        picture_path="test/image.jpg",
        picture_width=1000,
        picture_height=1500,
        feet_rules_options=["Free feet", "Feet follow hands"],
        has_symmetry=False,
    )
    db_session.add(face)
    db_session.commit()
    return face


@pytest.fixture
def test_holds(db_session, test_face):
    """Crée des holds de test."""
    holds = []
    for i in range(5):
        hold = Hold(
            stokt_id=829000 + i,
            face_id=test_face.id,
            polygon_str=f"100,{200+i*50} 150,{200+i*50} 150,{250+i*50} 100,{250+i*50}",
            centroid_x=125.0,
            centroid_y=225.0 + i * 50,
            area=2500.0,
        )
        holds.append(hold)
        db_session.add(hold)
    db_session.commit()
    return holds


class TestListFaces:
    """Tests pour GET /api/faces."""

    def test_list_faces_empty(self, client, api_key_header):
        """Test liste vide."""
        response = client.get("/api/faces", headers=api_key_header)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_faces_with_data(self, client, api_key_header, test_face, test_holds):
        """Test liste avec données."""
        response = client.get("/api/faces", headers=api_key_header)
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 1
        assert data[0]["picture_path"] == "test/image.jpg"
        assert data[0]["holds_count"] == 5


class TestGetFace:
    """Tests pour GET /api/faces/{id}."""

    def test_get_face_not_found(self, client, api_key_header):
        """Test face non trouvée."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/faces/{fake_id}", headers=api_key_header)
        assert response.status_code == 404

    def test_get_face_success(self, client, api_key_header, test_face, test_holds):
        """Test récupération face."""
        response = client.get(f"/api/faces/{test_face.id}", headers=api_key_header)
        assert response.status_code == 200

        data = response.json()
        assert data["picture_path"] == "test/image.jpg"
        assert data["picture_width"] == 1000
        assert data["holds_count"] == 5


class TestGetFaceSetup:
    """Tests pour GET /api/faces/{id}/setup."""

    def test_get_face_setup_not_found(self, client, api_key_header):
        """Test setup face non trouvée."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/faces/{fake_id}/setup", headers=api_key_header)
        assert response.status_code == 404

    def test_get_face_setup_success(self, client, api_key_header, test_face, test_holds):
        """Test setup complet."""
        response = client.get(f"/api/faces/{test_face.id}/setup", headers=api_key_header)
        assert response.status_code == 200

        data = response.json()

        # Vérifier la structure
        assert "id" in data
        assert "picture" in data
        assert "holds" in data
        assert "feet_rules_options" in data

        # Vérifier picture
        assert data["picture"]["name"] == "test/image.jpg"
        assert data["picture"]["width"] == 1000
        assert data["picture"]["height"] == 1500

        # Vérifier holds
        assert len(data["holds"]) == 5
        assert data["holds"][0]["polygon_str"].startswith("100,")
        assert data["holds"][0]["centroid_str"] == "125.0 225.0"

        # Vérifier feet_rules_options
        assert "Free feet" in data["feet_rules_options"]

    def test_get_face_setup_no_holds(self, client, api_key_header, test_face):
        """Test setup sans holds."""
        response = client.get(f"/api/faces/{test_face.id}/setup", headers=api_key_header)
        assert response.status_code == 200

        data = response.json()
        assert data["holds"] == []


class TestGetFaceSetupByStoktId:
    """Tests pour GET /api/faces/by-stokt-id/{id}/setup."""

    def test_get_by_stokt_id_not_found(self, client, api_key_header):
        """Test stokt_id non trouvé."""
        fake_id = str(uuid.uuid4())
        response = client.get(
            f"/api/faces/by-stokt-id/{fake_id}/setup",
            headers=api_key_header
        )
        assert response.status_code == 404

    def test_get_by_stokt_id_success(self, client, api_key_header, test_face, test_holds):
        """Test récupération par stokt_id."""
        response = client.get(
            f"/api/faces/by-stokt-id/{test_face.stokt_id}/setup",
            headers=api_key_header
        )
        assert response.status_code == 200

        data = response.json()
        assert len(data["holds"]) == 5
