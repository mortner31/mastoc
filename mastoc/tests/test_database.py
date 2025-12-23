"""Tests pour la base de données SQLite."""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from mastoc.db import Database, ClimbRepository, HoldRepository
from mastoc.api.models import Climb, Hold, Face, Grade, ClimbSetter, FacePicture


@pytest.fixture
def temp_db():
    """Crée une base de données temporaire pour les tests."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink(missing_ok=True)


@pytest.fixture
def sample_climb():
    """Crée un climb de test."""
    return Climb(
        id="test-climb-id",
        name="Test Climb",
        holds_list="S829279 O828906 F829104 T829009",
        feet_rule="Pieds des mains",
        face_id="test-face-id",
        wall_id="test-wall-id",
        wall_name="Test Wall",
        date_created="2025-12-17T10:00:00",
        climbed_by=5,
        total_likes=10,
        setter=ClimbSetter(id="setter-id", full_name="John Doe", avatar="avatar.jpg"),
        grade=Grade(ircra=20.5, hueco="V6", font="7A", dankyu="1Q")
    )


@pytest.fixture
def sample_face():
    """Crée une face de test avec des prises."""
    return Face(
        id="test-face-id",
        gym="Test Gym",
        wall="Test Wall",
        is_active=True,
        total_climbs=100,
        picture=FacePicture(name="test.jpg", width=2263, height=3000),
        feet_rules_options=["Tous pieds", "Pieds des mains"],
        has_symmetry=False,
        holds=[
            Hold(
                id=829279,
                area=1000.0,
                polygon_str="100,100 200,100 200,200 100,200",
                touch_polygon_str="",
                path_str="",
                centroid_str="150 150"
            ),
            Hold(
                id=828906,
                area=800.0,
                polygon_str="300,300 400,300 400,400 300,400",
                touch_polygon_str="",
                path_str="",
                centroid_str="350 350"
            ),
            Hold(
                id=829104,
                area=600.0,
                polygon_str="500,500 600,500 600,600 500,600",
                touch_polygon_str="",
                path_str="",
                centroid_str="550 550"
            ),
            Hold(
                id=829009,
                area=1200.0,
                polygon_str="700,700 800,700 800,800 700,800",
                touch_polygon_str="",
                path_str="",
                centroid_str="750 750"
            ),
        ]
    )


class TestDatabase:
    def test_init_creates_tables(self, temp_db):
        """Vérifie que les tables sont créées à l'initialisation."""
        with temp_db.connection() as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}

        assert "climbs" in tables
        assert "holds" in tables
        assert "faces" in tables
        assert "setters" in tables
        assert "climb_holds" in tables
        assert "sync_metadata" in tables

    def test_metadata_get_set(self, temp_db):
        """Teste get/set metadata."""
        temp_db.set_metadata("test_key", "test_value")
        value = temp_db.get_metadata("test_key")
        assert value == "test_value"

    def test_metadata_nonexistent(self, temp_db):
        """Teste get metadata pour clé inexistante."""
        value = temp_db.get_metadata("nonexistent")
        assert value is None

    def test_last_sync(self, temp_db):
        """Teste get/set last_sync."""
        assert temp_db.get_last_sync() is None

        temp_db.set_last_sync()
        last_sync = temp_db.get_last_sync()
        assert last_sync is not None
        assert isinstance(last_sync, datetime)

    def test_counts_empty(self, temp_db):
        """Teste les compteurs sur base vide."""
        assert temp_db.get_climb_count() == 0
        assert temp_db.get_hold_count() == 0


class TestClimbRepository:
    def test_save_and_get_climb(self, temp_db, sample_climb):
        """Teste sauvegarde et récupération d'un climb."""
        repo = ClimbRepository(temp_db)
        repo.save_climb(sample_climb)

        retrieved = repo.get_climb(sample_climb.id)
        assert retrieved is not None
        assert retrieved.id == sample_climb.id
        assert retrieved.name == sample_climb.name
        assert retrieved.holds_list == sample_climb.holds_list

    def test_climb_with_grade(self, temp_db, sample_climb):
        """Teste que le grade est bien sauvegardé."""
        repo = ClimbRepository(temp_db)
        repo.save_climb(sample_climb)

        retrieved = repo.get_climb(sample_climb.id)
        assert retrieved.grade is not None
        assert retrieved.grade.font == "7A"
        assert retrieved.grade.ircra == pytest.approx(20.5)

    def test_climb_with_setter(self, temp_db, sample_climb):
        """Teste que le setter est bien sauvegardé."""
        repo = ClimbRepository(temp_db)
        repo.save_climb(sample_climb)

        retrieved = repo.get_climb(sample_climb.id)
        assert retrieved.setter is not None
        assert retrieved.setter.full_name == "John Doe"

    def test_get_nonexistent_climb(self, temp_db):
        """Teste récupération d'un climb inexistant."""
        repo = ClimbRepository(temp_db)
        retrieved = repo.get_climb("nonexistent-id")
        assert retrieved is None

    def test_save_climbs_batch(self, temp_db):
        """Teste sauvegarde de plusieurs climbs."""
        repo = ClimbRepository(temp_db)
        climbs = [
            Climb(
                id=f"climb-{i}",
                name=f"Climb {i}",
                holds_list="S829279 T829009",
                feet_rule="",
                face_id="face-id",
                wall_id="wall-id",
                wall_name="Wall",
                date_created=""
            )
            for i in range(10)
        ]

        progress_calls = []
        repo.save_climbs(climbs, callback=lambda c, t: progress_calls.append((c, t)))

        assert temp_db.get_climb_count() == 10
        assert len(progress_calls) > 0

    def test_get_all_climbs(self, temp_db):
        """Teste récupération de tous les climbs."""
        repo = ClimbRepository(temp_db)
        for i in range(5):
            climb = Climb(
                id=f"climb-{i}",
                name=f"Climb {i}",
                holds_list="S829279 T829009",
                feet_rule="",
                face_id="face-id",
                wall_id="wall-id",
                wall_name="Wall",
                date_created=f"2025-12-{10+i}T10:00:00"
            )
            repo.save_climb(climb)

        all_climbs = repo.get_all_climbs()
        assert len(all_climbs) == 5

    def test_get_climbs_by_grade(self, temp_db):
        """Teste filtrage par grade."""
        repo = ClimbRepository(temp_db)

        # Climb 7A
        climb_7a = Climb(
            id="climb-7a",
            name="Hard Climb",
            holds_list="S829279 T829009",
            feet_rule="",
            face_id="face-id",
            wall_id="wall-id",
            wall_name="Wall",
            date_created="",
            grade=Grade(ircra=20.5, hueco="V6", font="7A", dankyu="1Q")
        )

        # Climb 6A
        climb_6a = Climb(
            id="climb-6a",
            name="Easy Climb",
            holds_list="S829279 T829009",
            feet_rule="",
            face_id="face-id",
            wall_id="wall-id",
            wall_name="Wall",
            date_created="",
            grade=Grade(ircra=16.0, hueco="V2", font="6A", dankyu="4Q")
        )

        repo.save_climb(climb_7a)
        repo.save_climb(climb_6a)

        climbs_7a = repo.get_climbs_by_grade("7A")
        assert len(climbs_7a) == 1
        assert climbs_7a[0].name == "Hard Climb"

    def test_get_unique_grades(self, temp_db):
        """Teste récupération des grades uniques."""
        repo = ClimbRepository(temp_db)

        grades = [("6A", 16.0), ("6B", 17.0), ("7A", 20.5)]
        for i, (font, ircra) in enumerate(grades):
            climb = Climb(
                id=f"climb-{i}",
                name=f"Climb {font}",
                holds_list="S829279 T829009",
                feet_rule="",
                face_id="face-id",
                wall_id="wall-id",
                wall_name="Wall",
                date_created="",
                grade=Grade(ircra=ircra, hueco="", font=font, dankyu="")
            )
            repo.save_climb(climb)

        unique_grades = repo.get_unique_grades()
        assert len(unique_grades) == 3
        assert "6A" in unique_grades
        assert "7A" in unique_grades


class TestHoldRepository:
    def test_save_face_with_holds(self, temp_db, sample_face):
        """Teste sauvegarde d'une face avec ses prises."""
        repo = HoldRepository(temp_db)
        repo.save_face(sample_face)

        assert temp_db.get_hold_count() == 4

    def test_get_hold(self, temp_db, sample_face):
        """Teste récupération d'une prise."""
        repo = HoldRepository(temp_db)
        repo.save_face(sample_face)

        hold = repo.get_hold(829279)
        assert hold is not None
        assert hold.id == 829279
        x, y = hold.centroid
        assert x == pytest.approx(150.0)

    def test_get_nonexistent_hold(self, temp_db):
        """Teste récupération d'une prise inexistante."""
        repo = HoldRepository(temp_db)
        hold = repo.get_hold(999999)
        assert hold is None

    def test_get_all_holds(self, temp_db, sample_face):
        """Teste récupération de toutes les prises."""
        repo = HoldRepository(temp_db)
        repo.save_face(sample_face)

        holds = repo.get_all_holds()
        assert len(holds) == 4

    def test_get_holds_by_face(self, temp_db, sample_face):
        """Teste récupération des prises par face."""
        repo = HoldRepository(temp_db)
        repo.save_face(sample_face)

        holds = repo.get_all_holds(face_id="test-face-id")
        assert len(holds) == 4

        holds_other = repo.get_all_holds(face_id="other-face")
        assert len(holds_other) == 0

    def test_get_face(self, temp_db, sample_face):
        """Teste récupération d'une face."""
        repo = HoldRepository(temp_db)
        repo.save_face(sample_face)

        face = repo.get_face("test-face-id")
        assert face is not None
        assert face.gym == "Test Gym"
        assert face.picture.width == 2263
        assert len(face.holds) == 4


class TestClimbHoldsRelation:
    def test_climb_holds_saved(self, temp_db, sample_climb, sample_face):
        """Teste que les relations climb-holds sont sauvegardées."""
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        climb_repo.save_climb(sample_climb)

        # Vérifier que les relations existent
        with temp_db.connection() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM climb_holds WHERE climb_id = ?",
                (sample_climb.id,)
            )
            count = cursor.fetchone()[0]

        assert count == 4  # S, O, F, T

    def test_get_climbs_by_hold(self, temp_db, sample_climb, sample_face):
        """Teste recherche de climbs par prise."""
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)
        climb_repo.save_climb(sample_climb)

        # Recherche par prise Start
        climbs = climb_repo.get_climbs_by_hold(829279)
        assert len(climbs) == 1
        assert climbs[0].id == sample_climb.id

    def test_get_climbs_by_multiple_holds(self, temp_db, sample_face):
        """Teste recherche de climbs par plusieurs prises."""
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)

        # Climb avec prises 829279 et 828906
        climb1 = Climb(
            id="climb-1",
            name="Climb 1",
            holds_list="S829279 O828906 T829009",
            feet_rule="",
            face_id="test-face-id",
            wall_id="",
            wall_name="",
            date_created=""
        )

        # Climb avec seulement 829279
        climb2 = Climb(
            id="climb-2",
            name="Climb 2",
            holds_list="S829279 T829104",
            feet_rule="",
            face_id="test-face-id",
            wall_id="",
            wall_name="",
            date_created=""
        )

        climb_repo.save_climb(climb1)
        climb_repo.save_climb(climb2)

        # Recherche avec les deux prises
        climbs = climb_repo.get_climbs_by_holds([829279, 828906])
        assert len(climbs) == 1
        assert climbs[0].id == "climb-1"

    def test_same_hold_different_types(self, temp_db, sample_face):
        """Teste qu'une même prise peut avoir différents types (S et T par ex)."""
        hold_repo = HoldRepository(temp_db)
        hold_repo.save_face(sample_face)

        climb_repo = ClimbRepository(temp_db)

        # Climb où la même prise est Start et Top
        climb = Climb(
            id="climb-same-hold",
            name="Same Hold Climb",
            holds_list="S829279 T829279",  # Même prise, types différents
            feet_rule="",
            face_id="test-face-id",
            wall_id="",
            wall_name="",
            date_created=""
        )

        # Ne doit pas lever d'exception
        climb_repo.save_climb(climb)

        # Vérifier les relations
        with temp_db.connection() as conn:
            cursor = conn.execute(
                "SELECT hold_type FROM climb_holds WHERE climb_id = ? AND hold_id = ?",
                (climb.id, 829279)
            )
            types = [row[0] for row in cursor.fetchall()]

        assert "S" in types
        assert "T" in types
