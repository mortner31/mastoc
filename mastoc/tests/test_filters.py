"""Tests pour le module de filtrage."""

import pytest
import tempfile
from pathlib import Path

from mastoc.db import Database, ClimbRepository, HoldRepository
from mastoc.api.models import Climb, Hold, Face, Grade, ClimbSetter, FacePicture
from mastoc.core.filters import ClimbFilter, ClimbFilterService, filter_climbs_simple


@pytest.fixture
def temp_db():
    """Crée une base de données temporaire."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink(missing_ok=True)


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
            Hold(id=100, area=1000, polygon_str="100,100 200,200",
                 touch_polygon_str="", path_str="", centroid_str="150 150"),
            Hold(id=101, area=800, polygon_str="300,300 400,400",
                 touch_polygon_str="", path_str="", centroid_str="350 350"),
            Hold(id=102, area=1200, polygon_str="500,500 600,600",
                 touch_polygon_str="", path_str="", centroid_str="550 550"),
        ]
    )


@pytest.fixture
def sample_climbs():
    """Liste de climbs de test variés."""
    setter1 = ClimbSetter(id="setter-1", full_name="Alice Martin", avatar=None)
    setter2 = ClimbSetter(id="setter-2", full_name="Bob Dupont", avatar=None)

    return [
        Climb(
            id="climb-1",
            name="Easy Route",
            holds_list="S100 O101 T102",
            feet_rule="Tous pieds",
            face_id="face-id",
            wall_id="wall-id",
            wall_name="Wall",
            date_created="2025-12-15T10:00:00",
            is_benchmark=False,
            has_symmetric=False,
            climbed_by=10,
            total_likes=5,
            setter=setter1,
            grade=Grade(ircra=16.0, hueco="V2", font="6A", dankyu="4Q")
        ),
        Climb(
            id="climb-2",
            name="Medium Challenge",
            holds_list="S100 O102 T101",
            feet_rule="Pieds des mains",
            face_id="face-id",
            wall_id="wall-id",
            wall_name="Wall",
            date_created="2025-12-16T10:00:00",
            is_benchmark=True,
            has_symmetric=False,
            climbed_by=5,
            total_likes=3,
            setter=setter1,
            grade=Grade(ircra=18.0, hueco="V4", font="6B+", dankyu="3Q")
        ),
        Climb(
            id="climb-3",
            name="Hard Problem",
            holds_list="S101 T102",
            feet_rule="Tous pieds",
            face_id="face-id",
            wall_id="wall-id",
            wall_name="Wall",
            date_created="2025-12-17T10:00:00",
            is_benchmark=False,
            has_symmetric=True,
            climbed_by=2,
            total_likes=10,
            setter=setter2,
            grade=Grade(ircra=20.5, hueco="V6", font="7A", dankyu="1Q")
        ),
        Climb(
            id="climb-4",
            name="Expert Block",
            holds_list="S100 T102",
            feet_rule="Sans pieds",
            face_id="face-id",
            wall_id="wall-id",
            wall_name="Wall",
            date_created="2025-12-18T10:00:00",
            is_benchmark=True,
            has_symmetric=False,
            climbed_by=1,
            total_likes=8,
            setter=setter2,
            grade=Grade(ircra=22.0, hueco="V7", font="7A+", dankyu="1D")
        ),
    ]


@pytest.fixture
def populated_db(temp_db, sample_face, sample_climbs):
    """Base de données peuplée avec les fixtures."""
    hold_repo = HoldRepository(temp_db)
    hold_repo.save_face(sample_face)

    climb_repo = ClimbRepository(temp_db)
    for climb in sample_climbs:
        climb_repo.save_climb(climb)

    return temp_db


class TestClimbFilter:
    def test_default_values(self):
        """Teste les valeurs par défaut."""
        f = ClimbFilter()
        assert f.grades == []
        assert f.setter_ids == []
        assert f.hold_ids == []
        assert f.sort_by == "date_created"
        assert f.sort_desc is True

    def test_with_values(self):
        """Teste l'initialisation avec valeurs."""
        f = ClimbFilter(
            grades=["6A", "6B"],
            setter_name="Alice",
            sort_by="grade"
        )
        assert f.grades == ["6A", "6B"]
        assert f.setter_name == "Alice"
        assert f.sort_by == "grade"


class TestClimbFilterService:
    def test_filter_no_criteria(self, populated_db, sample_climbs):
        """Teste filtrage sans critères (tous les climbs)."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter())
        assert len(results) == 4

    def test_filter_by_single_grade(self, populated_db):
        """Teste filtrage par un seul grade."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(grades=["6A"]))
        assert len(results) == 1
        assert results[0].name == "Easy Route"

    def test_filter_by_multiple_grades(self, populated_db):
        """Teste filtrage par plusieurs grades."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(grades=["6A", "7A"]))
        assert len(results) == 2

    def test_filter_by_grade_range(self, populated_db):
        """Teste filtrage par plage IRCRA."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(
            grade_min=17.0,
            grade_max=21.0
        ))
        assert len(results) == 2
        # 6B+ (18.0) et 7A (20.5)
        grades = [c.grade.font for c in results]
        assert "6B+" in grades
        assert "7A" in grades

    def test_filter_by_setter_id(self, populated_db):
        """Teste filtrage par ID setter."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(setter_ids=["setter-1"]))
        assert len(results) == 2
        for c in results:
            assert c.setter.id == "setter-1"

    def test_filter_by_setter_name(self, populated_db):
        """Teste filtrage par nom de setter (partiel)."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(setter_name="Alice"))
        assert len(results) == 2

        results = service.filter_climbs(ClimbFilter(setter_name="bob"))
        assert len(results) == 2

        results = service.filter_climbs(ClimbFilter(setter_name="martin"))
        assert len(results) == 2

    def test_filter_by_holds_all(self, populated_db):
        """Teste filtrage par prises (mode ALL)."""
        service = ClimbFilterService(populated_db)
        # Climbs avec prises 100 ET 101
        results = service.filter_climbs(ClimbFilter(
            hold_ids=[100, 101],
            hold_match_mode="all"
        ))
        # climb-1 (S100 O101 T102) et climb-2 (S100 O102 T101) ont les deux
        assert len(results) == 2
        ids = [c.id for c in results]
        assert "climb-1" in ids
        assert "climb-2" in ids

    def test_filter_by_holds_any(self, populated_db):
        """Teste filtrage par prises (mode ANY)."""
        service = ClimbFilterService(populated_db)
        # Climbs avec prise 100 OU 101
        results = service.filter_climbs(ClimbFilter(
            hold_ids=[100, 101],
            hold_match_mode="any"
        ))
        # Tous sauf climb-3 qui n'a que 101 et 102
        # climb-1: 100, 101, 102
        # climb-2: 100, 102, 101
        # climb-3: 101, 102
        # climb-4: 100, 102
        assert len(results) == 4  # Tous ont au moins une des prises

    def test_filter_by_feet_rule(self, populated_db):
        """Teste filtrage par règle de pieds."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(feet_rules=["Tous pieds"]))
        assert len(results) == 2

    def test_filter_by_benchmark(self, populated_db):
        """Teste filtrage par benchmark."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(is_benchmark=True))
        assert len(results) == 2

        results = service.filter_climbs(ClimbFilter(is_benchmark=False))
        assert len(results) == 2

    def test_filter_by_symmetric(self, populated_db):
        """Teste filtrage par symétrie."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(has_symmetric=True))
        assert len(results) == 1
        assert results[0].name == "Hard Problem"

    def test_filter_by_search_text(self, populated_db):
        """Teste recherche textuelle."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(search_text="challenge"))
        assert len(results) == 1
        assert results[0].name == "Medium Challenge"

        results = service.filter_climbs(ClimbFilter(search_text="ROUTE"))
        assert len(results) == 1

    def test_sort_by_date(self, populated_db):
        """Teste tri par date."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(sort_by="date_created", sort_desc=True))
        assert results[0].name == "Expert Block"
        assert results[-1].name == "Easy Route"

    def test_sort_by_grade(self, populated_db):
        """Teste tri par grade."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(sort_by="grade", sort_desc=True))
        assert results[0].grade.font == "7A+"
        assert results[-1].grade.font == "6A"

    def test_sort_by_name(self, populated_db):
        """Teste tri par nom."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(sort_by="name", sort_desc=False))
        assert results[0].name == "Easy Route"

    def test_sort_by_climbed_by(self, populated_db):
        """Teste tri par popularité."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(sort_by="climbed_by", sort_desc=True))
        assert results[0].climbed_by == 10

    def test_combined_filters(self, populated_db):
        """Teste combinaison de filtres."""
        service = ClimbFilterService(populated_db)
        results = service.filter_climbs(ClimbFilter(
            grades=["6A", "6B+", "7A", "7A+"],
            setter_name="bob",
            feet_rules=["Tous pieds"]
        ))
        assert len(results) == 1
        assert results[0].name == "Hard Problem"

    def test_get_available_grades(self, populated_db):
        """Teste récupération des grades disponibles."""
        service = ClimbFilterService(populated_db)
        grades = service.get_available_grades()
        assert len(grades) == 4
        assert "6A" in grades
        assert "7A+" in grades

    def test_get_available_setters(self, populated_db):
        """Teste récupération des setters disponibles."""
        service = ClimbFilterService(populated_db)
        setters = service.get_available_setters()
        assert len(setters) == 2
        names = [s[1] for s in setters]
        assert "Alice Martin" in names
        assert "Bob Dupont" in names

    def test_get_available_feet_rules(self, populated_db):
        """Teste récupération des règles de pieds."""
        service = ClimbFilterService(populated_db)
        rules = service.get_available_feet_rules()
        assert len(rules) == 3
        assert "Tous pieds" in rules
        assert "Pieds des mains" in rules
        assert "Sans pieds" in rules


class TestFilterClimbsSimple:
    def test_filter_by_grades(self, sample_climbs):
        """Teste filtrage simple par grades."""
        results = filter_climbs_simple(sample_climbs, grades=["6A"])
        assert len(results) == 1

    def test_filter_by_setter_name(self, sample_climbs):
        """Teste filtrage simple par setter."""
        results = filter_climbs_simple(sample_climbs, setter_name="Alice")
        assert len(results) == 2

    def test_filter_by_search(self, sample_climbs):
        """Teste filtrage simple par texte."""
        results = filter_climbs_simple(sample_climbs, search_text="block")
        assert len(results) == 1

    def test_filter_combined(self, sample_climbs):
        """Teste filtrage simple combiné."""
        results = filter_climbs_simple(
            sample_climbs,
            grades=["7A", "7A+"],
            setter_name="bob"
        )
        assert len(results) == 2

    def test_filter_no_match(self, sample_climbs):
        """Teste filtrage sans résultat."""
        results = filter_climbs_simple(sample_climbs, grades=["8A"])
        assert len(results) == 0
