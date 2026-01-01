"""Tests pour le module de synchronisation."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from mastoc.db import Database, ClimbRepository, HoldRepository
from mastoc.api.client import StoktAPI, AuthenticationError
from mastoc.api.models import Climb, Hold, Face, Grade, ClimbSetter, FacePicture, Wall
from mastoc.core.sync import SyncManager, SyncResult


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

    def test_calculate_max_age_recent_sync(self, temp_db, mock_api):
        """Teste le calcul de max_age pour une sync récente."""
        manager = SyncManager(mock_api, temp_db)

        # Sync il y a 2 jours -> max_age = 7 (minimum)
        last_sync = datetime.now() - timedelta(days=2)
        max_age = manager._calculate_max_age(last_sync)
        assert max_age == 7  # Minimum de 7 jours

    def test_calculate_max_age_old_sync(self, temp_db, mock_api):
        """Teste le calcul de max_age pour une sync ancienne."""
        manager = SyncManager(mock_api, temp_db)

        # Sync il y a 15 jours -> max_age = 16 (15 + 1)
        last_sync = datetime.now() - timedelta(days=15)
        max_age = manager._calculate_max_age(last_sync)
        assert max_age == 16

    def test_calculate_max_age_custom_minimum(self, temp_db, mock_api):
        """Teste le calcul de max_age avec minimum personnalisé."""
        manager = SyncManager(mock_api, temp_db)

        # Sync il y a 2 jours avec minimum 14
        last_sync = datetime.now() - timedelta(days=2)
        max_age = manager._calculate_max_age(last_sync, min_days=14)
        assert max_age == 14

    def test_sync_incremental_uses_max_age(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste que sync_incremental utilise max_age dynamique."""
        # Setup initial
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_climbs:
            climb_repo.save_climb(climb)

        # Simuler une sync il y a 3 jours
        old_sync = datetime.now() - timedelta(days=3)
        temp_db.set_last_sync(old_sync)

        mock_api.get_all_gym_climbs.return_value = sample_climbs

        manager = SyncManager(mock_api, temp_db)
        result = manager.sync_incremental()

        # Vérifier que l'API a été appelée avec max_age (7 minimum)
        mock_api.get_all_gym_climbs.assert_called_once()
        call_args = mock_api.get_all_gym_climbs.call_args
        assert call_args.kwargs.get('max_age') == 7  # min_days par défaut


# =============================================================================
# Tests Social Refresh (TODO 18)
# =============================================================================

class TestSocialRefresh:
    """Tests pour le rafraîchissement des compteurs sociaux."""

    def test_refresh_social_counts(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste le rafraîchissement des compteurs d'un climb."""
        # Setup: sauvegarder un climb avec des compteurs initiaux
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        climb = sample_climbs[0]
        climb_repo.save_climb(climb)

        # Mock: API retourne de nouveaux compteurs
        mock_api.get_climb_social_stats.return_value = {
            "climbed_by": 15,
            "total_likes": 25,
            "total_comments": 5
        }

        manager = SyncManager(mock_api, temp_db)
        stats = manager.refresh_social_counts(climb.id)

        # Vérifier les stats retournées
        assert stats["climbed_by"] == 15
        assert stats["total_likes"] == 25
        assert stats["total_comments"] == 5

        # Vérifier que la BD a été mise à jour
        updated_climb = climb_repo.get_climb(climb.id)
        assert updated_climb.climbed_by == 15
        assert updated_climb.total_likes == 25
        assert updated_climb.total_comments == 5

    def test_refresh_all_social_counts(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste le rafraîchissement batch de tous les climbs."""
        # Setup: sauvegarder plusieurs climbs
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_climbs[:3]:
            climb_repo.save_climb(climb)

        # Mock: API retourne des compteurs différents pour chaque climb
        mock_api.get_climb_social_stats.return_value = {
            "climbed_by": 10,
            "total_likes": 20,
            "total_comments": 3
        }

        manager = SyncManager(mock_api, temp_db)
        result = manager.refresh_all_social_counts(delay_seconds=0)  # Pas de délai pour les tests

        assert result["total"] == 3
        assert result["updated"] == 3
        assert result["errors"] == []

        # Vérifier que l'API a été appelée 3 fois
        assert mock_api.get_climb_social_stats.call_count == 3

    def test_refresh_all_social_counts_with_error(self, temp_db, mock_api, sample_climbs, sample_face):
        """Teste le refresh batch avec une erreur sur un climb."""
        # Setup
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_climbs[:2]:
            climb_repo.save_climb(climb)

        # Mock: première réussite, deuxième échec
        mock_api.get_climb_social_stats.side_effect = [
            {"climbed_by": 10, "total_likes": 20, "total_comments": 3},
            Exception("API error")
        ]

        manager = SyncManager(mock_api, temp_db)
        result = manager.refresh_all_social_counts(delay_seconds=0)

        assert result["total"] == 2
        assert result["updated"] == 1
        assert len(result["errors"]) == 1
        assert "API error" in result["errors"][0]

    def test_update_social_counts_repository(self, temp_db, sample_climbs, sample_face):
        """Teste la mise à jour directe des compteurs via le repository."""
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        climb = sample_climbs[0]
        climb_repo.save_climb(climb)

        # Mise à jour directe
        climb_repo.update_social_counts(
            climb.id,
            climbed_by=100,
            total_likes=50,
            total_comments=10
        )

        # Vérifier
        updated = climb_repo.get_climb(climb.id)
        assert updated.climbed_by == 100
        assert updated.total_likes == 50
        assert updated.total_comments == 10
