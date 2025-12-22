"""Tests pour les composants du sélecteur de prises (TODO 06 + TODO 08)."""

import pytest
import tempfile
from pathlib import Path

from mastock.db import Database, ClimbRepository, HoldRepository
from mastock.api.models import Climb, Hold, Face, Grade, ClimbSetter, FacePicture
from mastock.core.hold_index import HoldClimbIndex
from mastock.core.colormaps import (
    Colormap, apply_colormap, get_colormap_lut, get_colormap_preview,
    get_all_colormaps, get_colormap_display_name
)
from mastock.gui.widgets.level_slider import (
    LevelRangeSlider, FONT_GRADES, grade_to_index, index_to_grade, ircra_to_index
)
from mastock.gui.widgets.hold_overlay import interpolate_color


@pytest.fixture
def temp_db():
    """Base de données temporaire."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    db = Database(db_path)
    yield db
    db_path.unlink(missing_ok=True)


@pytest.fixture
def sample_face():
    """Face de test avec prises."""
    return Face(
        id="face-1",
        gym="Test",
        wall="Wall",
        is_active=True,
        total_climbs=10,
        picture=FacePicture(name="test.jpg", width=2263, height=3000),
        holds=[
            Hold(id=100, area=1000, polygon_str="0,0 100,0 100,100 0,100",
                 touch_polygon_str="", path_str="", centroid_str="50 50"),
            Hold(id=101, area=800, polygon_str="200,0 300,0 300,100 200,100",
                 touch_polygon_str="", path_str="", centroid_str="250 50"),
            Hold(id=102, area=600, polygon_str="400,0 500,0 500,100 400,100",
                 touch_polygon_str="", path_str="", centroid_str="450 50"),
            Hold(id=103, area=500, polygon_str="600,0 700,0 700,100 600,100",
                 touch_polygon_str="", path_str="", centroid_str="650 50"),
        ]
    )


@pytest.fixture
def sample_climbs():
    """Liste de climbs avec grades variés."""
    return [
        Climb(
            id="c1", name="Easy", holds_list="S100 T102",
            feet_rule="Tous pieds", face_id="face-1", wall_id="w1", wall_name="W",
            date_created="2025-01-01",
            setter=ClimbSetter(id="s1", full_name="Alice", avatar=None),
            grade=Grade(ircra=14.0, hueco="V1", font="6A", dankyu="")
        ),
        Climb(
            id="c2", name="Medium", holds_list="S100 O101 T103",
            feet_rule="Tous pieds", face_id="face-1", wall_id="w1", wall_name="W",
            date_created="2025-01-02",
            setter=ClimbSetter(id="s1", full_name="Alice", avatar=None),
            grade=Grade(ircra=18.0, hueco="V4", font="6C", dankyu="")
        ),
        Climb(
            id="c3", name="Hard", holds_list="S101 O102 T103",
            feet_rule="Sans pieds", face_id="face-1", wall_id="w1", wall_name="W",
            date_created="2025-01-03",
            setter=ClimbSetter(id="s2", full_name="Bob", avatar=None),
            grade=Grade(ircra=22.0, hueco="V7", font="7B", dankyu="")
        ),
        Climb(
            id="c4", name="No Grade", holds_list="S102 T103",
            feet_rule="Tous pieds", face_id="face-1", wall_id="w1", wall_name="W",
            date_created="2025-01-04"
        ),
    ]


@pytest.fixture
def populated_db(temp_db, sample_face, sample_climbs):
    """BD peuplée pour les tests."""
    hold_repo = HoldRepository(temp_db)
    hold_repo.save_face(sample_face)

    climb_repo = ClimbRepository(temp_db)
    for climb in sample_climbs:
        climb_repo.save_climb(climb)

    return temp_db


class TestLevelSlider:
    """Tests pour le slider de niveau."""

    def test_font_grades_count(self):
        """Vérifie le nombre de grades."""
        assert len(FONT_GRADES) == 16  # 4 à 8A (sans 7C+)

    def test_grade_to_index(self):
        """Teste conversion grade → index."""
        assert grade_to_index("4") == 0
        assert grade_to_index("6A") == 4
        assert grade_to_index("8A") == 15

    def test_index_to_grade(self):
        """Teste conversion index → grade."""
        assert index_to_grade(0) == ("4", 12.0)      # Grade 4 = IRCRA 12.0
        assert index_to_grade(4) == ("6A", 15.5)     # Grade 6A = IRCRA 15.5
        assert index_to_grade(15) == ("8A", 26.5)    # Grade 8A = IRCRA 26.5

    def test_ircra_to_index(self):
        """Teste conversion IRCRA → index."""
        assert ircra_to_index(12.0) == 0   # Grade 4
        assert ircra_to_index(15.5) == 4   # Grade 6A
        assert ircra_to_index(26.5) == 15  # Grade 8A

    def test_ircra_values_match_real_data(self):
        """Vérifie que les valeurs IRCRA correspondent aux données réelles."""
        # Valeurs observées dans la base de données
        expected = {
            "4": 12.0,     # 4 commence à 12.0
            "4+": 13.25,   # 4+ commence à 13.25
            "5": 14.25,    # 5 commence à 14.25
            "5+": 15.0,    # 5+ commence à 15.0
            "6A": 15.5,    # 6A commence à 15.5
            "6B": 17.5,    # 6B commence à 17.5
            "7A": 20.5,    # 7A commence à 20.5
        }
        for grade_name, expected_ircra in expected.items():
            idx = grade_to_index(grade_name)
            _, actual_ircra = index_to_grade(idx)
            assert actual_ircra == expected_ircra, f"Grade {grade_name}: attendu {expected_ircra}, obtenu {actual_ircra}"


class TestColorInterpolation:
    """Tests pour l'interpolation de couleur."""

    def test_min_grade_is_green(self):
        """Le grade minimum doit être vert."""
        color = interpolate_color(12, 26, 12)  # IRCRA réel
        r, g, b, a = color
        assert g == 255
        assert r == 0

    def test_max_grade_is_red(self):
        """Le grade maximum doit être rouge."""
        color = interpolate_color(12, 26, 26)
        r, g, b, a = color
        assert r == 255
        assert g == 0

    def test_mid_grade_is_orange(self):
        """Le grade moyen doit être orange/jaune."""
        color = interpolate_color(12, 26, 19)  # Milieu entre 12 et 26
        r, g, b, a = color
        assert r == 255
        assert g > 0


class TestHoldClimbIndex:
    """Tests pour l'index prises ↔ blocs."""

    def test_from_database(self, populated_db):
        """Teste la création de l'index depuis la BD."""
        index = HoldClimbIndex.from_database(populated_db)

        assert len(index.climbs) == 4
        assert len(index.holds) == 4
        assert 100 in index.hold_to_climbs

    def test_get_climbs_for_hold(self, populated_db):
        """Teste la recherche de blocs par prise."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prise 100 est dans c1 et c2
        climbs = index.get_climbs_for_hold(100)
        ids = [c.id for c in climbs]
        assert "c1" in ids
        assert "c2" in ids
        assert len(climbs) == 2

    def test_get_climbs_for_multiple_holds(self, populated_db):
        """Teste la recherche de blocs par plusieurs prises (logique ET)."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prises 100 ET 101 = seulement c2
        climbs = index.get_climbs_for_holds([100, 101])
        assert len(climbs) == 1
        assert climbs[0].id == "c2"

    def test_get_climbs_in_grade_range(self, populated_db):
        """Teste le filtrage par plage de grade."""
        index = HoldClimbIndex.from_database(populated_db)

        # 6A-6C (14-18)
        climbs = index.get_climbs_in_grade_range(14, 18)
        ids = [c.id for c in climbs]
        assert "c1" in ids
        assert "c2" in ids
        assert "c3" not in ids

    def test_get_filtered_climbs_combined(self, populated_db):
        """Teste le filtrage combiné (prises + grade)."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prise 100 + grade 14-18 = c1 et c2
        climbs = index.get_filtered_climbs(
            hold_ids=[100],
            min_ircra=14,
            max_ircra=18
        )
        ids = [c.id for c in climbs]
        assert len(climbs) == 2

        # Prise 103 + grade 20-24 = c3 seulement
        climbs = index.get_filtered_climbs(
            hold_ids=[103],
            min_ircra=20,
            max_ircra=24
        )
        assert len(climbs) == 1
        assert climbs[0].id == "c3"

    def test_get_hold_min_grade(self, populated_db):
        """Teste le grade minimum d'une prise."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prise 100 : min grade = 14 (c1 = 6A)
        min_grade = index.get_hold_min_grade(100)
        assert min_grade == 14.0

        # Prise 103 : min grade = 0 (c4 n'a pas de grade → ircra=0)
        min_grade = index.get_hold_min_grade(103)
        assert min_grade == 0  # c4 sans grade

    def test_get_hold_min_grade_with_filter(self, populated_db):
        """Teste le grade minimum d'une prise avec filtre."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prise 103 dans plage 20-26 : min = 22 (c3 = 7B)
        min_grade = index.get_hold_min_grade(103, min_ircra=20, max_ircra=26)
        assert min_grade == 22.0

        # Prise 100 dans plage 20-26 : None (c1 et c2 sont < 20)
        min_grade = index.get_hold_min_grade(100, min_ircra=20, max_ircra=26)
        assert min_grade is None

    def test_get_holds_usage(self, populated_db):
        """Teste le comptage d'utilisation des prises."""
        index = HoldClimbIndex.from_database(populated_db)

        usage = index.get_holds_usage()
        assert usage[100] == 2  # c1, c2
        assert usage[103] == 3  # c2, c3, c4

        # Avec filtre grade
        usage = index.get_holds_usage(min_ircra=20, max_ircra=26)
        assert usage.get(100) is None  # Pas de bloc avec prise 100 dans cette plage
        assert usage[103] == 1  # Seulement c3


class TestEdgeCases:
    """Tests des cas limites."""

    def test_empty_selection_returns_all(self, populated_db):
        """Une sélection vide retourne tous les blocs (avec grade)."""
        index = HoldClimbIndex.from_database(populated_db)

        climbs = index.get_filtered_climbs(
            hold_ids=[],
            min_ircra=12,   # IRCRA réel pour grade 4
            max_ircra=30
        )
        # 3 blocs avec grade (c4 a grade=0 donc exclu sauf si on met min=0)
        assert len(climbs) >= 3

    def test_no_match_returns_empty(self, populated_db):
        """Pas de correspondance retourne liste vide."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prise inexistante
        climbs = index.get_climbs_for_hold(999)
        assert len(climbs) == 0

        # Combinaison impossible (100 + 101 + 103 n'existe pas)
        climbs = index.get_climbs_for_holds([100, 103])
        # c1 a 100+102, c2 a 100+101+103 → c2 a 100 et 103
        assert len(climbs) == 1  # c2 seulement

    def test_climb_without_grade(self, populated_db):
        """Un bloc sans grade a IRCRA=0."""
        index = HoldClimbIndex.from_database(populated_db)

        assert index.climb_grades["c4"] == 0


class TestIrcraFilteringIntegration:
    """Tests d'intégration pour le filtrage IRCRA avec données réelles."""

    def test_grade_4_to_5plus_range(self):
        """Test du filtrage 4-5+ avec les vraies données de la base."""
        from mastock.db import Database
        from mastock.core.filters import ClimbFilterService, ClimbFilter

        db = Database()
        svc = ClimbFilterService(db)

        # Plage 4-5+ avec les nouvelles valeurs IRCRA corrigées
        # 4 commence à 12.0, 5+ va jusqu'à ~15.25, 6A commence à 15.5
        f = ClimbFilter(grade_min=12.0, grade_max=15.49)
        climbs = svc.filter_climbs(f)

        # Collecter les grades trouvés
        grades = set()
        for c in climbs:
            if c.grade:
                grades.add(c.grade.font)

        # Vérifier qu'on a bien les grades 4, 4+, 5, 5+
        expected_grades = {"4", "4+", "5", "5+"}
        assert grades == expected_grades, f"Attendu {expected_grades}, obtenu {grades}"

        # Vérifier qu'on a au moins 100 blocs (il y en a 133 dans la vraie base)
        assert len(climbs) >= 100, f"Attendu >= 100 blocs, obtenu {len(climbs)}"

    def test_slider_range_calculation(self):
        """Test que le slider calcule correctement les bornes IRCRA."""
        from mastock.gui.widgets.level_slider import FONT_GRADES

        # Pour 4-5+ (indices 0-3), le max devrait être juste avant 6A
        min_idx = 0  # Grade 4
        max_idx = 3  # Grade 5+

        _, min_ircra = FONT_GRADES[min_idx]
        _, next_ircra = FONT_GRADES[max_idx + 1]  # Grade 6A
        max_ircra = next_ircra - 0.01

        assert min_ircra == 12.0, f"Min IRCRA attendu 12.0, obtenu {min_ircra}"
        assert max_ircra == 15.49, f"Max IRCRA attendu 15.49, obtenu {max_ircra}"


# ============================================================
# Tests TODO 08 - Modes de coloration et heatmaps
# ============================================================

class TestHoldMaxGrade:
    """Tests pour get_hold_max_grade() (TODO 08)."""

    def test_get_hold_max_grade(self, populated_db):
        """Teste le grade maximum d'une prise."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prise 100 : max grade = 18 (c2 = 6C)
        max_grade = index.get_hold_max_grade(100)
        assert max_grade == 18.0

        # Prise 103 : max grade = 22 (c3 = 7B, c4=0, c2=18)
        max_grade = index.get_hold_max_grade(103)
        assert max_grade == 22.0

    def test_get_hold_max_grade_with_filter(self, populated_db):
        """Teste le grade maximum avec filtre de plage."""
        index = HoldClimbIndex.from_database(populated_db)

        # Prise 103 dans plage 14-20 : max = 18 (c2 = 6C)
        max_grade = index.get_hold_max_grade(103, min_ircra=14, max_ircra=20)
        assert max_grade == 18.0

        # Prise 100 dans plage 20-26 : None (aucun bloc)
        max_grade = index.get_hold_max_grade(100, min_ircra=20, max_ircra=26)
        assert max_grade is None

    def test_get_hold_max_grade_nonexistent(self, populated_db):
        """Prise inexistante retourne None."""
        index = HoldClimbIndex.from_database(populated_db)
        assert index.get_hold_max_grade(999) is None


class TestHoldsUsageQuantiles:
    """Tests pour get_holds_usage_quantiles() (TODO 08)."""

    def test_basic_quantiles(self, populated_db):
        """Teste le calcul des quantiles d'usage."""
        index = HoldClimbIndex.from_database(populated_db)

        quantiles = index.get_holds_usage_quantiles()

        # Vérifier que toutes les prises ont un percentile
        assert 100 in quantiles
        assert 101 in quantiles
        assert 102 in quantiles
        assert 103 in quantiles

        # Les percentiles sont entre 0 et 1
        for hold_id, percentile in quantiles.items():
            assert 0 <= percentile <= 1, f"Prise {hold_id}: percentile {percentile} hors bornes"

    def test_quantiles_ordering(self, populated_db):
        """Les prises plus utilisées ont des percentiles plus élevés."""
        index = HoldClimbIndex.from_database(populated_db)

        # Usage: 100=2, 101=2, 102=3, 103=3
        quantiles = index.get_holds_usage_quantiles()

        # Prises avec usage=3 doivent avoir percentile >= prises avec usage=2
        assert quantiles[102] >= quantiles[100]
        assert quantiles[103] >= quantiles[101]

    def test_quantiles_with_filter(self, populated_db):
        """Teste les quantiles avec filtre de grade."""
        index = HoldClimbIndex.from_database(populated_db)

        # Filtre 14-18 : c1 (14) et c2 (18)
        # Usage filtré: 100=2, 101=1, 102=1, 103=1
        quantiles = index.get_holds_usage_quantiles(min_ircra=14, max_ircra=18)

        # Prise 100 (usage=2) doit avoir le percentile le plus élevé
        assert quantiles[100] > quantiles[101]

    def test_quantiles_empty(self, populated_db):
        """Filtre qui exclut tout retourne dict vide."""
        index = HoldClimbIndex.from_database(populated_db)

        quantiles = index.get_holds_usage_quantiles(min_ircra=50, max_ircra=60)
        assert quantiles == {}


class TestColormaps:
    """Tests pour le module colormaps (TODO 08)."""

    def test_all_colormaps_generate_256_colors(self):
        """Chaque palette génère 256 couleurs."""
        for cmap in Colormap:
            lut = get_colormap_lut(cmap)
            assert len(lut) == 256, f"{cmap.value} n'a pas 256 couleurs"

    def test_colormap_colors_in_range(self):
        """Les couleurs sont dans la plage 0-255."""
        for cmap in Colormap:
            lut = get_colormap_lut(cmap)
            for r, g, b in lut:
                assert 0 <= r <= 255, f"{cmap.value}: r={r} hors plage"
                assert 0 <= g <= 255, f"{cmap.value}: g={g} hors plage"
                assert 0 <= b <= 255, f"{cmap.value}: b={b} hors plage"

    def test_apply_colormap_extremes(self):
        """Test des valeurs extrêmes."""
        for cmap in Colormap:
            # Valeur 0
            color = apply_colormap(0.0, cmap)
            assert len(color) == 4
            assert color[3] == 180  # Alpha par défaut

            # Valeur 1
            color = apply_colormap(1.0, cmap)
            assert len(color) == 4

    def test_apply_colormap_clamping(self):
        """Les valeurs hors bornes sont clampées."""
        color_neg = apply_colormap(-0.5, Colormap.VIRIDIS)
        color_zero = apply_colormap(0.0, Colormap.VIRIDIS)
        assert color_neg[:3] == color_zero[:3]

        color_over = apply_colormap(1.5, Colormap.VIRIDIS)
        color_one = apply_colormap(1.0, Colormap.VIRIDIS)
        assert color_over[:3] == color_one[:3]

    def test_apply_colormap_custom_alpha(self):
        """Test du paramètre alpha."""
        color = apply_colormap(0.5, Colormap.PLASMA, alpha=255)
        assert color[3] == 255

    def test_get_colormap_preview(self):
        """Test de la génération d'aperçu."""
        preview = get_colormap_preview(Colormap.INFERNO, width=100)
        assert len(preview) == 100

        # Aperçu pleine taille
        full = get_colormap_preview(Colormap.INFERNO, width=256)
        assert len(full) == 256

    def test_get_all_colormaps(self):
        """Liste toutes les palettes."""
        cmaps = get_all_colormaps()
        assert len(cmaps) == 7
        assert Colormap.VIRIDIS in cmaps
        assert Colormap.COOLWARM in cmaps

    def test_get_colormap_display_name(self):
        """Test des noms d'affichage."""
        assert "recommandé" in get_colormap_display_name(Colormap.VIRIDIS)
        assert "daltoniens" in get_colormap_display_name(Colormap.CIVIDIS)

    def test_viridis_gradient(self):
        """Viridis va du violet sombre au jaune-vert."""
        lut = get_colormap_lut(Colormap.VIRIDIS)

        # Début: teinte sombre (violet/bleu)
        r0, g0, b0 = lut[0]
        assert r0 < 100  # Pas trop rouge
        assert b0 > r0   # Plus bleu que rouge

        # Fin: jaune-vert (viridis finit en jaune-vert, pas jaune pur)
        r255, g255, b255 = lut[255]
        assert g255 > 200  # Beaucoup de vert
        assert b255 < 100  # Peu de bleu
        # Le rouge peut être modéré dans viridis (approximation polynomiale)

    def test_coolwarm_is_divergent(self):
        """Coolwarm est bleu → blanc → rouge."""
        lut = get_colormap_lut(Colormap.COOLWARM)

        # Début: bleu
        r0, g0, b0 = lut[0]
        assert b0 > r0  # Plus bleu que rouge

        # Milieu: blanc/gris clair
        r128, g128, b128 = lut[128]
        assert r128 > 200
        assert g128 > 200
        assert b128 > 200

        # Fin: rouge
        r255, g255, b255 = lut[255]
        assert r255 > b255  # Plus rouge que bleu
