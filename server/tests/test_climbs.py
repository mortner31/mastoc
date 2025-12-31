"""
Tests pour les endpoints climbs.
"""

import uuid


def _setup_gym_face(client):
    """Helper pour créer gym + face."""
    gym_stokt_id = str(uuid.uuid4())
    face_stokt_id = str(uuid.uuid4())

    client.post(
        "/api/sync/import/gym",
        json={"stokt_id": gym_stokt_id, "display_name": "Test Gym"}
    )
    face_response = client.post(
        "/api/sync/import/face",
        json={
            "stokt_id": face_stokt_id,
            "gym_stokt_id": gym_stokt_id,
            "picture_path": "images/face.jpg",
        }
    )
    face_id = face_response.json()["id"]
    return face_id, face_stokt_id


def _create_climb(client, face_stokt_id, name="Test Bloc", grade_font="6A"):
    """Helper pour créer un climb."""
    climb_stokt_id = str(uuid.uuid4())
    response = client.post(
        "/api/sync/import/climb",
        json={
            "stokt_id": climb_stokt_id,
            "face_stokt_id": face_stokt_id,
            "name": name,
            "holds_list": "S1,S2,O3,T4",
            "grade_font": grade_font,
            "grade_ircra": 15.0,
        }
    )
    return response.json()["id"], climb_stokt_id


def test_list_climbs_empty(client):
    """Test liste climbs vide."""
    response = client.get("/api/climbs")
    assert response.status_code == 200
    data = response.json()
    assert data["results"] == []
    assert data["count"] == 0


def test_list_climbs(client):
    """Test liste climbs."""
    face_id, face_stokt_id = _setup_gym_face(client)
    _create_climb(client, face_stokt_id, "Bloc A")
    _create_climb(client, face_stokt_id, "Bloc B")

    response = client.get("/api/climbs")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["results"]) == 2


def test_list_climbs_pagination(client):
    """Test pagination des climbs."""
    face_id, face_stokt_id = _setup_gym_face(client)
    for i in range(5):
        _create_climb(client, face_stokt_id, f"Bloc {i}")

    # Page 1
    response = client.get("/api/climbs", params={"page": 1, "page_size": 2})
    data = response.json()
    assert data["count"] == 5
    assert len(data["results"]) == 2

    # Page 2
    response = client.get("/api/climbs", params={"page": 2, "page_size": 2})
    data = response.json()
    assert len(data["results"]) == 2


def test_get_climb_by_id(client):
    """Test récupération climb par ID."""
    face_id, face_stokt_id = _setup_gym_face(client)
    climb_id, _ = _create_climb(client, face_stokt_id, "Mon Bloc")

    response = client.get(f"/api/climbs/{climb_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Mon Bloc"


def test_get_climb_not_found(client):
    """Test climb inexistant."""
    fake_id = str(uuid.uuid4())
    response = client.get(f"/api/climbs/{fake_id}")
    assert response.status_code == 404


def test_get_climb_by_stokt_id(client):
    """Test récupération climb par stokt_id."""
    face_id, face_stokt_id = _setup_gym_face(client)
    climb_id, climb_stokt_id = _create_climb(client, face_stokt_id, "Mon Bloc")

    response = client.get(f"/api/climbs/by-stokt-id/{climb_stokt_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == climb_id


def test_delete_climb(client):
    """Test suppression d'un climb."""
    face_id, face_stokt_id = _setup_gym_face(client)
    climb_id, _ = _create_climb(client, face_stokt_id)

    response = client.delete(f"/api/climbs/{climb_id}")
    assert response.status_code == 204

    # Vérifier suppression
    response = client.get(f"/api/climbs/{climb_id}")
    assert response.status_code == 404


def test_update_stokt_id(client):
    """Test mise à jour du stokt_id (après push vers Stokt)."""
    face_id, face_stokt_id = _setup_gym_face(client)
    climb_id, _ = _create_climb(client, face_stokt_id)

    new_stokt_id = str(uuid.uuid4())
    response = client.patch(
        f"/api/climbs/{climb_id}/stokt-id",
        params={"stokt_id": new_stokt_id}
    )
    assert response.status_code == 200

    # Vérifier via by-stokt-id
    response = client.get(f"/api/climbs/by-stokt-id/{new_stokt_id}")
    assert response.status_code == 200
    assert response.json()["id"] == climb_id


def test_climb_response_includes_created_at(client):
    """Test que la réponse climb inclut created_at."""
    face_id, face_stokt_id = _setup_gym_face(client)
    climb_id, _ = _create_climb(client, face_stokt_id, "Bloc Test")

    response = client.get(f"/api/climbs/{climb_id}")
    assert response.status_code == 200
    data = response.json()
    assert "created_at" in data
    assert data["created_at"] is not None


def test_list_climbs_since_created_at(client):
    """Test filtrage par since_created_at."""
    from datetime import datetime, timedelta

    face_id, face_stokt_id = _setup_gym_face(client)
    _create_climb(client, face_stokt_id, "Bloc A")
    _create_climb(client, face_stokt_id, "Bloc B")

    # Tous les climbs
    response = client.get("/api/climbs")
    assert response.json()["count"] == 2

    # Filtrer par date future (aucun résultat)
    future_date = (datetime.utcnow() + timedelta(days=1)).isoformat()
    response = client.get("/api/climbs", params={"since_created_at": future_date})
    assert response.json()["count"] == 0

    # Filtrer par date passée (tous les résultats)
    past_date = (datetime.utcnow() - timedelta(days=1)).isoformat()
    response = client.get("/api/climbs", params={"since_created_at": past_date})
    assert response.json()["count"] == 2
