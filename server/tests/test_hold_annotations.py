"""
Tests pour les endpoints hold_annotations (/api/holds/{id}/annotations).

ADR-008 : Hold Annotations (Annotations Crowd-Sourcées).
"""

import os
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from mastoc_api.database import Base, get_db
from mastoc_api.main import app
from mastoc_api.config import get_settings
from mastoc_api.models import Gym, Face, Hold, User, HoldAnnotation
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
def client(db_session):
    """Client en mode dev (sans API Key configuree)."""
    os.environ.pop("API_KEY", None)
    get_settings.cache_clear()
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def api_key_header():
    """Header API Key pour les tests."""
    return {"X-API-Key": "test-key"}


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
def test_hold(db_session, test_face):
    """Cree un hold de test."""
    hold = Hold(
        stokt_id=829001,
        face_id=test_face.id,
        polygon_str="100,200 150,200 150,250 100,250",
        centroid_x=125.0,
        centroid_y=225.0,
        area=2500.0,
    )
    db_session.add(hold)
    db_session.commit()
    return hold


@pytest.fixture
def user_token(client, db_session):
    """Cree un user normal et retourne son token."""
    client.post("/api/auth/register", json={
        "email": "user@example.com",
        "username": "normaluser",
        "password": "password123",
        "full_name": "Normal User"
    })
    response = client.post("/api/auth/login", data={
        "username": "normaluser",
        "password": "password123"
    })
    return response.json()["access_token"]


@pytest.fixture
def second_user_token(client, db_session):
    """Cree un second user et retourne son token."""
    client.post("/api/auth/register", json={
        "email": "user2@example.com",
        "username": "seconduser",
        "password": "password123",
        "full_name": "Second User"
    })
    response = client.post("/api/auth/login", data={
        "username": "seconduser",
        "password": "password123"
    })
    return response.json()["access_token"]


# === Tests GET annotations ===

def test_get_annotations_empty(client, api_key_header, test_hold):
    """GET annotations pour une prise sans annotations."""
    response = client.get(
        f"/api/holds/{test_hold.id}/annotations",
        headers=api_key_header
    )
    assert response.status_code == 200
    data = response.json()
    assert data["hold_id"] == test_hold.id
    assert data["consensus"]["total_annotators"] == 0
    assert data["user_annotation"] is None


def test_get_annotations_hold_not_found(client, api_key_header):
    """GET annotations pour une prise inexistante."""
    response = client.get(
        "/api/holds/999999/annotations",
        headers=api_key_header
    )
    assert response.status_code == 404


# === Tests PUT annotations ===

def test_put_annotation_requires_jwt(client, api_key_header, test_hold):
    """PUT annotation requiert JWT."""
    response = client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers=api_key_header,
        json={"grip_type": "reglette"}
    )
    assert response.status_code == 401


def test_put_annotation_create_success(client, test_hold, user_token):
    """PUT annotation cree une nouvelle annotation."""
    response = client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "grip_type": "reglette",
            "condition": "ok",
            "difficulty": "normale",
            "notes": "Test annotation"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grip_type"] == "reglette"
    assert data["condition"] == "ok"
    assert data["difficulty"] == "normale"
    assert data["notes"] == "Test annotation"


def test_put_annotation_update_success(client, test_hold, user_token):
    """PUT annotation met a jour une annotation existante."""
    # Premiere annotation
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "plat"}
    )
    # Mise a jour
    response = client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "reglette", "condition": "a_brosser"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["grip_type"] == "reglette"
    assert data["condition"] == "a_brosser"


def test_put_annotation_hold_not_found(client, user_token):
    """PUT annotation pour une prise inexistante."""
    response = client.put(
        "/api/holds/999999/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "reglette"}
    )
    assert response.status_code == 404


# === Tests DELETE annotations ===

def test_delete_annotation_requires_jwt(client, api_key_header, test_hold):
    """DELETE annotation requiert JWT."""
    response = client.delete(
        f"/api/holds/{test_hold.id}/annotations",
        headers=api_key_header
    )
    assert response.status_code == 401


def test_delete_annotation_success(client, test_hold, user_token):
    """DELETE annotation supprime l'annotation."""
    # Creer annotation
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "reglette"}
    )
    # Supprimer
    response = client.delete(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 204

    # Verifier suppression
    response = client.get(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.json()["user_annotation"] is None


def test_delete_annotation_not_found(client, test_hold, user_token):
    """DELETE annotation inexistante."""
    response = client.delete(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == 404


# === Tests Consensus ===

def test_consensus_single_vote(client, test_hold, user_token, api_key_header):
    """Consensus avec un seul vote."""
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "reglette", "condition": "ok"}
    )

    response = client.get(
        f"/api/holds/{test_hold.id}/annotations",
        headers=api_key_header
    )
    data = response.json()
    assert data["consensus"]["total_annotators"] == 1
    assert data["consensus"]["grip_type"] == "reglette"
    assert data["consensus"]["grip_type_votes"] == 1
    assert data["consensus"]["grip_type_confidence"] == 1.0
    assert data["consensus"]["condition"] == "ok"


def test_consensus_multiple_votes_same(client, test_hold, user_token, second_user_token, api_key_header):
    """Consensus avec plusieurs votes identiques."""
    # Premier vote
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "reglette"}
    )
    # Deuxieme vote identique
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {second_user_token}"},
        json={"grip_type": "reglette"}
    )

    response = client.get(
        f"/api/holds/{test_hold.id}/annotations",
        headers=api_key_header
    )
    data = response.json()
    assert data["consensus"]["total_annotators"] == 2
    assert data["consensus"]["grip_type"] == "reglette"
    assert data["consensus"]["grip_type_votes"] == 2
    assert data["consensus"]["grip_type_confidence"] == 1.0


def test_consensus_multiple_votes_different(client, test_hold, user_token, second_user_token, api_key_header):
    """Consensus avec votes differents."""
    # Premier vote
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "reglette"}
    )
    # Deuxieme vote different
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {second_user_token}"},
        json={"grip_type": "plat"}
    )

    response = client.get(
        f"/api/holds/{test_hold.id}/annotations",
        headers=api_key_header
    )
    data = response.json()
    assert data["consensus"]["total_annotators"] == 2
    # Mode = le premier trouve (ordre non garanti dans test)
    assert data["consensus"]["grip_type"] in ["reglette", "plat"]
    assert data["consensus"]["grip_type_votes"] == 1
    assert data["consensus"]["grip_type_confidence"] == 0.5


# === Tests Batch ===

def test_batch_annotations_empty(client, api_key_header, test_hold):
    """Batch pour des prises sans annotations."""
    response = client.post(
        "/api/holds/annotations/batch",
        headers=api_key_header,
        json={"hold_ids": [test_hold.id]}
    )
    assert response.status_code == 200
    data = response.json()
    assert str(test_hold.id) in data["annotations"]


def test_batch_annotations_with_data(client, test_hold, user_token, api_key_header):
    """Batch avec annotations."""
    # Creer annotation
    client.put(
        f"/api/holds/{test_hold.id}/annotations",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"grip_type": "bac"}
    )

    response = client.post(
        "/api/holds/annotations/batch",
        headers=api_key_header,
        json={"hold_ids": [test_hold.id]}
    )
    assert response.status_code == 200
    data = response.json()
    hold_data = data["annotations"][str(test_hold.id)]
    assert hold_data["consensus"]["grip_type"] == "bac"


def test_batch_annotations_max_limit(client, api_key_header):
    """Batch avec trop de hold_ids."""
    response = client.post(
        "/api/holds/annotations/batch",
        headers=api_key_header,
        json={"hold_ids": list(range(1001))}
    )
    assert response.status_code == 400


def test_batch_annotations_nonexistent_holds(client, api_key_header):
    """Batch ignore les holds inexistants."""
    response = client.post(
        "/api/holds/annotations/batch",
        headers=api_key_header,
        json={"hold_ids": [999999, 999998]}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["annotations"]) == 0
