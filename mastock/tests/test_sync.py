"""Tests pour le module de synchronisation."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from mastock.db import Database, ClimbRepository, HoldRepository
from mastock.api.client import StoktAPI, AuthenticationError
from mastock.api.models import Climb, Hold, Face, Grade, ClimbSetter, FacePicture, Wall
from mastock.core.sync import SyncManager, SyncResult


@pytest.fixture
def temp_db():
    """Crée une base de données temporaire."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink(missing_ok=True)


@pytest.fixture
def mock_api():
    """Crée une API mockée."""
    api = Mock(spec=StoktAPI)
    api.is_authenticated.return_value = True
    return api


@pytest.fixture
def sample_climbs():
    """Liste de climbs de test."""
    return [
        Climb(
            id=f"climb-{i}",
            name=f"Test Climb {i}",
            holds_list="S829279 O828906 T829009",
            feet_rule="Tous pieds",
            face_id="face-id",
            wall_id="wall-id",
            wall_name="Test Wall",
            date_created=f"2025-12-{10+i}T10:00:00",
            climbed_by=i * 2,
            total_likes=i,
            grade=Grade(ircra=16 + i, hueco=f"V{i}", font=f"6{chr(65+i)}", dankyu="")
        )
        for i in range(5)
    ]


@pytest.fixture
def sample_face():
    """Face de test avec prises."""
    return Face(
        id="face-id",
        gym="Test Gym",
        wall="Test Wall",
        is_active=True,
        total_climbs=100,
        picture=FacePicture(name="test.jpg", width=2263, height=3000),
        holds=[
            Hold(id=829279, area=1000, polygon_str="100,100 200,200",
                 touch_polygon_str="", path_str="", centroid_str="150 150"),
            Hold(id=828906, area=800, polygon_str="300,300 400,400",
                 touch_polygon_str="", path_str="", centroid_str="350 350"),
            Hold(id=829009, area=1200, polygon_str="500,500 600,600",
                 touch_polygon_str="", path_str="", centroid_str="550 550"),
        ]
    )


@pytest.fixture
def sample_wall(sample_face):
    """Wall de test."""
    return Wall(
        id="wall-id",
        name="Test Wall",
        is_active=True,
        faces=[sample_face]
    )


class TestSyncResult:
    def test_init(self):
        """Teste l'initialisation de SyncResult."""
        result = SyncResult()
        assert result.climbs_added == 0
        assert result.climbs_updated == 0
        assert result.holds_added == 0
        assert result.errors == []
        assert result.success is True

    def test_repr(self):
        """Teste la représentation string."""
        result = SyncResult()
        result.climbs_added = 10
        result.holds_added = 50
        repr_str = repr(result)
        assert "added=10" in repr_str
        assert "holds=50" in repr_str


class TestSyncManager:
    def test_get_sync_status_empty(self, temp_db, mock_api):
        """Teste le statut sur base vide."""
        manager = SyncManager(mock_api, temp_db)
        status = manager.get_sync_status()

        assert status["last_sync"] is None
        assert status["climb_count"] == 0
        assert status["hold_count"] == 0
        assert status["is_synced"] is False

    def test_get_sync_status_synced(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste le statut après synchronisation."""
        # Peupler la base
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_climbs:
            climb_repo.save_climb(climb)

        temp_db.set_last_sync()

        manager = SyncManager(mock_api, temp_db)
        status = manager.get_sync_status()

        assert status["last_sync"] is not None
        assert status["climb_count"] == 5
        assert status["hold_count"] == 3
        assert status["is_synced"] is True

    def test_needs_sync_empty(self, temp_db, mock_api):
        """Teste needs_sync sur base vide."""
        manager = SyncManager(mock_api, temp_db)
        assert manager.needs_sync() is True

    def test_needs_sync_recent(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste needs_sync après sync récente."""
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_climbs:
            climb_repo.save_climb(climb)

        temp_db.set_last_sync()

        manager = SyncManager(mock_api, temp_db)
        assert manager.needs_sync() is False

    def test_sync_full(self, temp_db, mock_api, sample_climbs, sample_wall, sample_face):
        """Teste la synchronisation complète."""
        mock_api.get_gym_walls.return_value = [sample_wall]
        mock_api.get_face_setup.return_value = sample_face
        mock_api.get_all_gym_climbs.return_value = sample_climbs

        manager = SyncManager(mock_api, temp_db)
        progress_calls = []
        result = manager.sync_full(
            callback=lambda c, t, m: progress_calls.append((c, t, m))
        )

        assert result.success is True
        assert result.climbs_added == 5
        assert result.holds_added == 3
        assert temp_db.get_climb_count() == 5
        assert temp_db.get_last_sync() is not None
        assert len(progress_calls) > 0

    def test_sync_full_with_clear(self, temp_db, mock_api, sample_climbs, sample_wall, sample_face):
        """Teste la synchronisation avec suppression des données."""
        # Peupler d'abord
        climb_repo = ClimbRepository(temp_db)
        climb_repo.save_climb(sample_climbs[0])
        assert temp_db.get_climb_count() == 1

        mock_api.get_gym_walls.return_value = [sample_wall]
        mock_api.get_face_setup.return_value = sample_face
        mock_api.get_all_gym_climbs.return_value = sample_climbs

        manager = SyncManager(mock_api, temp_db)
        result = manager.sync_full(clear_existing=True)

        assert result.success is True
        assert temp_db.get_climb_count() == 5

    def test_sync_full_auth_error(self, temp_db, mock_api):
        """Teste la gestion des erreurs d'authentification."""
        mock_api.get_gym_walls.side_effect = AuthenticationError("Token expiré")

        manager = SyncManager(mock_api, temp_db)
        result = manager.sync_full()

        assert result.success is False
        assert len(result.errors) > 0
        assert "authentification" in result.errors[0].lower()

    def test_sync_incremental_no_previous(self, temp_db, mock_api, sample_climbs, sample_wall, sample_face):
        """Teste sync incrémentale sans sync précédente."""
        mock_api.get_gym_walls.return_value = [sample_wall]
        mock_api.get_face_setup.return_value = sample_face
        mock_api.get_all_gym_climbs.return_value = sample_climbs

        manager = SyncManager(mock_api, temp_db)
        result = manager.sync_incremental()

        # Doit faire une sync complète
        assert result.success is True
        assert result.climbs_added == 5

    def test_sync_incremental_with_new_climbs(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste sync incrémentale avec nouveaux climbs."""
        # Sync initiale
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_climbs[:3]:
            climb_repo.save_climb(climb)
        temp_db.set_last_sync()

        # API retourne 5 climbs (2 nouveaux)
        mock_api.get_all_gym_climbs.return_value = sample_climbs

        manager = SyncManager(mock_api, temp_db)
        result = manager.sync_incremental()

        assert result.success is True
        assert result.climbs_added == 2
        assert result.climbs_updated == 0

    def test_sync_incremental_with_updates(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste sync incrémentale avec mises à jour."""
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_climbs:
            climb_repo.save_climb(climb)
        temp_db.set_last_sync()

        # Modifier un climb (plus de likes)
        updated_climbs = sample_climbs.copy()
        updated_climbs[0] = Climb(
            id=sample_climbs[0].id,
            name=sample_climbs[0].name,
            holds_list=sample_climbs[0].holds_list,
            feet_rule=sample_climbs[0].feet_rule,
            face_id=sample_climbs[0].face_id,
            wall_id=sample_climbs[0].wall_id,
            wall_name=sample_climbs[0].wall_name,
            date_created=sample_climbs[0].date_created,
            climbed_by=sample_climbs[0].climbed_by,
            total_likes=sample_climbs[0].total_likes + 10,  # Modifié
            grade=sample_climbs[0].grade
        )

        mock_api.get_all_gym_climbs.return_value = updated_climbs

        manager = SyncManager(mock_api, temp_db)
        result = manager.sync_incremental()

        assert result.success is True
        assert result.climbs_added == 0
        assert result.climbs_updated == 1

    def test_climb_changed_detection(self, temp_db, mock_api, sample_climbs):
        """Teste la détection de changement de climb."""
        manager = SyncManager(mock_api, temp_db)

        original = sample_climbs[0]

        # Même climb
        same = Climb(
            id=original.id, name=original.name, holds_list=original.holds_list,
            feet_rule=original.feet_rule, face_id=original.face_id,
            wall_id=original.wall_id, wall_name=original.wall_name,
            date_created=original.date_created, climbed_by=original.climbed_by,
            total_likes=original.total_likes, total_comments=original.total_comments
        )
        assert manager._climb_changed(original, same) is False

        # Climb avec plus de likes
        modified = Climb(
            id=original.id, name=original.name, holds_list=original.holds_list,
            feet_rule=original.feet_rule, face_id=original.face_id,
            wall_id=original.wall_id, wall_name=original.wall_name,
            date_created=original.date_created, climbed_by=original.climbed_by,
            total_likes=original.total_likes + 5, total_comments=original.total_comments
        )
        assert manager._climb_changed(original, modified) is True
