"""Tests d'intégration pour l'application mastoc."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch

from mastoc.db import Database, ClimbRepository, HoldRepository
from mastoc.api.client import StoktAPI, MONTOBOARD_GYM_ID
from mastoc.api.models import Climb, Hold, Face, Grade, ClimbSetter, FacePicture, Wall
from mastoc.core import SyncManager, ClimbFilter, ClimbFilterService


@pytest.fixture
def temp_db():
    """Base de données temporaire."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink(missing_ok=True)


@pytest.fixture
def sample_data():
    """Données de test complètes."""
    setter1 = ClimbSetter(id="s1", full_name="Alice", avatar=None)
    setter2 = ClimbSetter(id="s2", full_name="Bob", avatar=None)

    face = Face(
        id="face-1",
        gym="Gym",
        wall="Wall",
        is_active=True,
        total_climbs=10,
        picture=FacePicture(name="pic.jpg", width=2263, height=3000),
        holds=[
            Hold(id=100, area=1000, polygon_str="0,0 100,0 100,100 0,100",
                 touch_polygon_str="", path_str="", centroid_str="50 50"),
            Hold(id=101, area=800, polygon_str="200,0 300,0 300,100 200,100",
                 touch_polygon_str="", path_str="", centroid_str="250 50"),
            Hold(id=102, area=600, polygon_str="400,0 500,0 500,100 400,100",
                 touch_polygon_str="", path_str="", centroid_str="450 50"),
        ]
    )

    climbs = [
        Climb(
            id="c1", name="Easy", holds_list="S100 T102",
            feet_rule="Tous pieds", face_id="face-1", wall_id="w1", wall_name="Wall",
            date_created="2025-12-10T10:00:00", setter=setter1,
            grade=Grade(ircra=16, hueco="V2", font="6A", dankyu="")
        ),
        Climb(
            id="c2", name="Medium", holds_list="S100 O101 T102",
            feet_rule="Pieds des mains", face_id="face-1", wall_id="w1", wall_name="Wall",
            date_created="2025-12-11T10:00:00", setter=setter1,
            grade=Grade(ircra=18, hueco="V4", font="6B+", dankyu="")
        ),
        Climb(
            id="c3", name="Hard", holds_list="S101 T102",
            feet_rule="Sans pieds", face_id="face-1", wall_id="w1", wall_name="Wall",
            date_created="2025-12-12T10:00:00", setter=setter2,
            grade=Grade(ircra=20, hueco="V6", font="7A", dankyu="")
        ),
    ]

    return {"face": face, "climbs": climbs, "setters": [setter1, setter2]}


@pytest.fixture
def populated_db(temp_db, sample_data):
    """Base de données peuplée."""
    hold_repo = HoldRepository(temp_db)
    hold_repo.save_face(sample_data["face"])

    climb_repo = ClimbRepository(temp_db)
    for climb in sample_data["climbs"]:
        climb_repo.save_climb(climb)

    temp_db.set_last_sync()
    return temp_db


class TestFullWorkflow:
    """Tests du workflow complet de l'application."""

    def test_initial_sync_populates_db(self, temp_db, sample_data):
        """Teste que la sync initiale peuple la base."""
        api = Mock(spec=StoktAPI)
        api.get_gym_walls.return_value = [
            Wall(id="w1", name="Wall", is_active=True, faces=[sample_data["face"]])
        ]
        api.get_face_setup.return_value = sample_data["face"]
        api.get_all_gym_climbs.return_value = sample_data["climbs"]

        sync = SyncManager(api, temp_db)

        # Avant sync
        assert temp_db.get_climb_count() == 0
        assert temp_db.get_hold_count() == 0

        # Sync
        result = sync.sync_full()

        # Après sync
        assert result.success
        assert temp_db.get_climb_count() == 3
        assert temp_db.get_hold_count() == 3
        assert temp_db.get_last_sync() is not None

    def test_filter_after_sync(self, populated_db, sample_data):
        """Teste le filtrage après synchronisation."""
        filter_service = ClimbFilterService(populated_db)

        # Tous les climbs
        all_climbs = filter_service.filter_climbs(ClimbFilter())
        assert len(all_climbs) == 3

        # Par grade
        grade_6a = filter_service.filter_climbs(ClimbFilter(grades=["6A"]))
        assert len(grade_6a) == 1
        assert grade_6a[0].name == "Easy"

        # Par setter
        alice_climbs = filter_service.filter_climbs(ClimbFilter(setter_name="Alice"))
        assert len(alice_climbs) == 2

        # Par prise
        hold_100 = filter_service.filter_climbs(ClimbFilter(hold_ids=[100]))
        assert len(hold_100) == 2  # Easy et Medium ont la prise 100

    def test_incremental_sync_adds_new_climbs(self, populated_db, sample_data):
        """Teste que la sync incrémentale ajoute les nouveaux climbs."""
        api = Mock(spec=StoktAPI)

        # Ajouter un nouveau climb
        new_climb = Climb(
            id="c4", name="Expert", holds_list="S100 T101",
            feet_rule="Tous pieds", face_id="face-1", wall_id="w1", wall_name="Wall",
            date_created="2025-12-13T10:00:00",
            setter=ClimbSetter(id="s2", full_name="Bob", avatar=None),
            grade=Grade(ircra=22, hueco="V7", font="7A+", dankyu="")
        )
        all_climbs = sample_data["climbs"] + [new_climb]
        api.get_all_gym_climbs.return_value = all_climbs

        sync = SyncManager(api, populated_db)

        # Avant
        assert populated_db.get_climb_count() == 3

        # Sync incrémentale
        result = sync.sync_incremental()

        # Après
        assert result.success
        assert result.climbs_added == 1
        assert populated_db.get_climb_count() == 4

    def test_search_climbs_by_hold(self, populated_db):
        """Teste la recherche de climbs par prise."""
        climb_repo = ClimbRepository(populated_db)

        # Prise 101 utilisée dans Medium et Hard
        climbs = climb_repo.get_climbs_by_hold(101)
        assert len(climbs) == 2
        names = [c.name for c in climbs]
        assert "Medium" in names
        assert "Hard" in names

        # Prise 102 utilisée dans tous
        climbs = climb_repo.get_climbs_by_hold(102)
        assert len(climbs) == 3

    def test_get_available_options(self, populated_db):
        """Teste la récupération des options disponibles."""
        filter_service = ClimbFilterService(populated_db)

        grades = filter_service.get_available_grades()
        assert "6A" in grades
        assert "7A" in grades

        setters = filter_service.get_available_setters()
        names = [s[1] for s in setters]
        assert "Alice" in names
        assert "Bob" in names

        feet_rules = filter_service.get_available_feet_rules()
        assert "Tous pieds" in feet_rules
        assert "Sans pieds" in feet_rules


class TestDataPersistence:
    """Tests de persistance des données."""

    def test_data_survives_db_reconnection(self, temp_db, sample_data):
        """Teste que les données survivent à une reconnexion."""
        db_path = temp_db.db_path

        # Peupler
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_data["face"])

        climb_repo = ClimbRepository(temp_db)
        for climb in sample_data["climbs"]:
            climb_repo.save_climb(climb)

        # Nouvelle connexion
        db2 = Database(db_path)

        assert db2.get_climb_count() == 3
        assert db2.get_hold_count() == 3

        climb_repo2 = ClimbRepository(db2)
        climb = climb_repo2.get_climb("c1")
        assert climb is not None
        assert climb.name == "Easy"

    def test_sync_metadata_persists(self, temp_db):
        """Teste la persistance des métadonnées."""
        db_path = temp_db.db_path

        temp_db.set_metadata("custom_key", "custom_value")
        temp_db.set_last_sync()

        # Nouvelle connexion
        db2 = Database(db_path)

        assert db2.get_metadata("custom_key") == "custom_value"
        assert db2.get_last_sync() is not None


class TestEdgeCases:
    """Tests des cas limites."""

    def test_empty_filter_returns_all(self, populated_db):
        """Teste qu'un filtre vide retourne tout."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter())
        assert len(results) == 3

    def test_no_match_returns_empty(self, populated_db):
        """Teste qu'un filtre sans correspondance retourne vide."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(grades=["8A"]))
        assert len(results) == 0

    def test_climb_without_grade(self, temp_db):
        """Teste un climb sans grade."""
        climb = Climb(
            id="no-grade", name="No Grade",
            holds_list="S100 T101", feet_rule="",
            face_id="f1", wall_id="w1", wall_name="W",
            date_created=""
        )

        repo = ClimbRepository(temp_db)
        repo.save_climb(climb)

        retrieved = repo.get_climb("no-grade")
        assert retrieved is not None
        assert retrieved.grade is None

    def test_climb_without_setter(self, temp_db):
        """Teste un climb sans setter."""
        climb = Climb(
            id="no-setter", name="No Setter",
            holds_list="S100 T101", feet_rule="",
            face_id="f1", wall_id="w1", wall_name="W",
            date_created=""
        )

        repo = ClimbRepository(temp_db)
        repo.save_climb(climb)

        retrieved = repo.get_climb("no-setter")
        assert retrieved is not None
        assert retrieved.setter is None
