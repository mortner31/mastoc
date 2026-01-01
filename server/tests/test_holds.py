"""
Tests pour les endpoints holds (/api/holds).
"""

import uuid
import pytest

from mastoc_api.models import Gym, Face, Hold


@pytest.fixture
def test_gym(db_session):
    """Cree un gym de test."""
    gym = Gym(
        id=uuid.uuid4(),
        display_name="Test Gym",
        location_string="Test Location",
    )
    db_session.add(gym)
    db_session.commit()
    return gym


@pytest.fixture
def test_face(db_session, test_gym):
    """Cree une face de test."""
    face = Face(
        id=uuid.uuid4(),
        stokt_id=uuid.uuid4(),
        gym_id=test_gym.id,
        picture_path="test/image.jpg",
        picture_width=1000,
        picture_height=1500,
    )
    db_session.add(face)
    db_session.commit()
    return face


@pytest.fixture
def test_holds(db_session, test_face):
    """Cree des holds de test."""
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


# === Tests List Holds ===

def test_list_holds_with_face_id(client, api_key_header, test_face, test_holds):
    """Liste des holds pour une face."""
    response = client.get(
        f"/api/holds?face_id={test_face.id}",
        headers=api_key_header
    )
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] == 5
    assert len(data["results"]) == 5


def test_list_holds_empty_face(client, api_key_header, test_face):
    """Liste vide pour une face sans holds."""
    response = client.get(
        f"/api/holds?face_id={test_face.id}",
        headers=api_key_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0
    assert data["results"] == []


def test_list_holds_missing_face_id(client, api_key_header):
    """Liste sans face_id retourne erreur."""
    response = client.get("/api/holds", headers=api_key_header)
    assert response.status_code == 422  # Validation error


def test_list_holds_nonexistent_face(client, api_key_header):
    """Liste pour une face inexistante."""
    fake_uuid = str(uuid.uuid4())
    response = client.get(
        f"/api/holds?face_id={fake_uuid}",
        headers=api_key_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 0


# === Tests Get Hold by ID ===

def test_get_hold_by_id_success(client, api_key_header, test_holds):
    """Recuperer un hold par ID."""
    hold = test_holds[0]
    response = client.get(
        f"/api/holds/{hold.id}",
        headers=api_key_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == hold.id
    assert "polygon_str" in data


def test_get_hold_by_id_not_found(client, api_key_header):
    """Hold inexistant."""
    response = client.get("/api/holds/999999", headers=api_key_header)
    assert response.status_code == 404


# === Tests Get Hold by Stokt ID ===

def test_get_hold_by_stokt_id_success(client, api_key_header, test_holds):
    """Recuperer un hold par stokt_id."""
    hold = test_holds[0]
    response = client.get(
        f"/api/holds/by-stokt-id/{hold.stokt_id}",
        headers=api_key_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stokt_id"] == hold.stokt_id


def test_get_hold_by_stokt_id_not_found(client, api_key_header):
    """stokt_id inexistant."""
    response = client.get(
        "/api/holds/by-stokt-id/999999",
        headers=api_key_header
    )
    assert response.status_code == 404
