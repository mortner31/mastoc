"""
Tests pour les endpoints de synchronisation.
"""

import uuid


def test_sync_stats_empty(client):
    """Test stats avec base vide."""
    response = client.get("/api/sync/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["gyms"] == 0
    assert data["faces"] == 0
    assert data["holds"] == 0
    assert data["climbs"] == 0
    assert data["users"] == 0


def test_import_gym(client):
    """Test import d'un gym."""
    gym_id = str(uuid.uuid4())
    response = client.post(
        "/api/sync/import/gym",
        json={
            "stokt_id": gym_id,
            "display_name": "Test Gym",
            "location_string": "Paris, France",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert "id" in data

    # Vérifier les stats
    stats = client.get("/api/sync/stats").json()
    assert stats["gyms"] == 1


def test_import_gym_duplicate(client):
    """Test import d'un gym déjà existant."""
    gym_id = str(uuid.uuid4())

    # Premier import
    client.post(
        "/api/sync/import/gym",
        json={"stokt_id": gym_id, "display_name": "Test Gym"}
    )

    # Deuxième import (même stokt_id)
    response = client.post(
        "/api/sync/import/gym",
        json={"stokt_id": gym_id, "display_name": "Test Gym Updated"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "exists"


def test_import_user(client):
    """Test import d'un user."""
    user_id = str(uuid.uuid4())
    response = client.post(
        "/api/sync/import/user",
        json={
            "stokt_id": user_id,
            "full_name": "John Doe",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"

    # Vérifier les stats
    stats = client.get("/api/sync/stats").json()
    assert stats["users"] == 1


def test_import_face(client):
    """Test import d'une face."""
    # D'abord créer un gym
    gym_stokt_id = str(uuid.uuid4())
    client.post(
        "/api/sync/import/gym",
        json={"stokt_id": gym_stokt_id, "display_name": "Test Gym"}
    )

    # Puis importer une face
    face_id = str(uuid.uuid4())
    response = client.post(
        "/api/sync/import/face",
        json={
            "stokt_id": face_id,
            "gym_stokt_id": gym_stokt_id,
            "picture_path": "images/face.jpg",
            "picture_width": 1000,
            "picture_height": 1500,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"

    stats = client.get("/api/sync/stats").json()
    assert stats["faces"] == 1


def test_import_face_gym_not_found(client):
    """Test import d'une face sans gym."""
    face_id = str(uuid.uuid4())
    response = client.post(
        "/api/sync/import/face",
        json={
            "stokt_id": face_id,
            "gym_stokt_id": str(uuid.uuid4()),  # Gym inexistant
            "picture_path": "images/face.jpg",
        }
    )
    assert response.status_code == 404


def test_import_hold(client):
    """Test import d'un hold."""
    # Setup: gym + face
    gym_stokt_id = str(uuid.uuid4())
    face_stokt_id = str(uuid.uuid4())

    client.post(
        "/api/sync/import/gym",
        json={"stokt_id": gym_stokt_id, "display_name": "Test Gym"}
    )
    client.post(
        "/api/sync/import/face",
        json={
            "stokt_id": face_stokt_id,
            "gym_stokt_id": gym_stokt_id,
            "picture_path": "images/face.jpg",
        }
    )

    # Import hold
    response = client.post(
        "/api/sync/import/hold",
        json={
            "stokt_id": 123,
            "face_stokt_id": face_stokt_id,
            "polygon_str": "100,100 200,100 200,200 100,200",
            "centroid_x": 150.0,
            "centroid_y": 150.0,
            "area": 10000.0,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"

    stats = client.get("/api/sync/stats").json()
    assert stats["holds"] == 1


def test_import_climb(client):
    """Test import d'un climb."""
    # Setup: gym + face + user
    gym_stokt_id = str(uuid.uuid4())
    face_stokt_id = str(uuid.uuid4())
    user_stokt_id = str(uuid.uuid4())
    climb_stokt_id = str(uuid.uuid4())

    client.post(
        "/api/sync/import/gym",
        json={"stokt_id": gym_stokt_id, "display_name": "Test Gym"}
    )
    client.post(
        "/api/sync/import/face",
        json={
            "stokt_id": face_stokt_id,
            "gym_stokt_id": gym_stokt_id,
            "picture_path": "images/face.jpg",
        }
    )
    client.post(
        "/api/sync/import/user",
        json={"stokt_id": user_stokt_id, "full_name": "Setter Pro"}
    )

    # Import climb
    response = client.post(
        "/api/sync/import/climb",
        json={
            "stokt_id": climb_stokt_id,
            "face_stokt_id": face_stokt_id,
            "setter_stokt_id": user_stokt_id,
            "name": "Test Bloc",
            "holds_list": "S123,S124,O125,T126",
            "grade_font": "6A+",
            "grade_ircra": 15.5,
            "feet_rule": "free",
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"

    stats = client.get("/api/sync/stats").json()
    assert stats["climbs"] == 1


def test_import_climb_update(client):
    """Test mise à jour d'un climb existant."""
    # Setup
    gym_stokt_id = str(uuid.uuid4())
    face_stokt_id = str(uuid.uuid4())
    climb_stokt_id = str(uuid.uuid4())

    client.post(
        "/api/sync/import/gym",
        json={"stokt_id": gym_stokt_id, "display_name": "Test Gym"}
    )
    client.post(
        "/api/sync/import/face",
        json={
            "stokt_id": face_stokt_id,
            "gym_stokt_id": gym_stokt_id,
            "picture_path": "images/face.jpg",
        }
    )

    # Premier import
    client.post(
        "/api/sync/import/climb",
        json={
            "stokt_id": climb_stokt_id,
            "face_stokt_id": face_stokt_id,
            "name": "Test Bloc",
            "holds_list": "S123,T124",
            "climbed_by": 5,
            "total_likes": 2,
        }
    )

    # Deuxième import (mise à jour stats)
    response = client.post(
        "/api/sync/import/climb",
        json={
            "stokt_id": climb_stokt_id,
            "face_stokt_id": face_stokt_id,
            "name": "Test Bloc",
            "holds_list": "S123,T124",
            "climbed_by": 10,
            "total_likes": 5,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "updated"

    # Toujours 1 seul climb
    stats = client.get("/api/sync/stats").json()
    assert stats["climbs"] == 1
