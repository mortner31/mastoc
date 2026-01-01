"""
Tests pour AnnotationPanel (TODO 12).

Tests couverts :
- Labels français des enums
- Logique du widget (sans Qt)
"""

import pytest

from mastoc.api.models import (
    HoldAnnotation, HoldConsensus, AnnotationData,
    HoldGripType, HoldCondition, HoldRelativeDifficulty
)
from mastoc.gui.widgets.annotation_panel import (
    _GRIP_TYPE_LABELS, _CONDITION_LABELS, _DIFFICULTY_LABELS
)


class TestEnumLabels:
    """Tests pour les labels français des enums."""

    def test_grip_type_labels_complete(self):
        """Tous les types de grip ont un label."""
        # Vérifier None
        assert None in _GRIP_TYPE_LABELS
        assert _GRIP_TYPE_LABELS[None] == "— Non spécifié —"

        # Vérifier toutes les valeurs de l'enum
        for grip in HoldGripType:
            assert grip in _GRIP_TYPE_LABELS, f"HoldGripType.{grip.name} manquant"
            assert len(_GRIP_TYPE_LABELS[grip]) > 0

    def test_condition_labels_complete(self):
        """Tous les états ont un label."""
        assert None in _CONDITION_LABELS

        for cond in HoldCondition:
            assert cond in _CONDITION_LABELS, f"HoldCondition.{cond.name} manquant"

    def test_difficulty_labels_complete(self):
        """Toutes les difficultés ont un label."""
        assert None in _DIFFICULTY_LABELS

        for diff in HoldRelativeDifficulty:
            assert diff in _DIFFICULTY_LABELS, f"HoldRelativeDifficulty.{diff.name} manquant"

    def test_grip_type_labels_french(self):
        """Les labels sont en français."""
        assert _GRIP_TYPE_LABELS[HoldGripType.PLAT] == "Plat"
        assert _GRIP_TYPE_LABELS[HoldGripType.REGLETTE] == "Réglette"
        assert _GRIP_TYPE_LABELS[HoldGripType.BI_DOIGT] == "Bi-doigt"
        assert _GRIP_TYPE_LABELS[HoldGripType.TRI_DOIGT] == "Tri-doigt"
        assert _GRIP_TYPE_LABELS[HoldGripType.MONO_DOIGT] == "Mono-doigt"
        assert _GRIP_TYPE_LABELS[HoldGripType.PINCE] == "Pince"
        assert _GRIP_TYPE_LABELS[HoldGripType.COLONNETTE] == "Colonnette"
        assert _GRIP_TYPE_LABELS[HoldGripType.INVERSE] == "Inversé"
        assert _GRIP_TYPE_LABELS[HoldGripType.BAC] == "Bac"
        assert _GRIP_TYPE_LABELS[HoldGripType.PRISE_VOLUME] == "Prise volume"
        assert _GRIP_TYPE_LABELS[HoldGripType.MICRO] == "Micro"
        assert _GRIP_TYPE_LABELS[HoldGripType.AUTRE] == "Autre"

    def test_condition_labels_french(self):
        """Les labels condition sont en français."""
        assert _CONDITION_LABELS[HoldCondition.OK] == "OK"
        assert _CONDITION_LABELS[HoldCondition.A_BROSSER] == "À brosser"
        assert _CONDITION_LABELS[HoldCondition.SALE] == "Sale"
        assert _CONDITION_LABELS[HoldCondition.TOURNEE] == "Tournée"
        assert _CONDITION_LABELS[HoldCondition.USEE] == "Usée"
        assert _CONDITION_LABELS[HoldCondition.CASSEE] == "Cassée"

    def test_difficulty_labels_french(self):
        """Les labels difficulté sont en français."""
        assert _DIFFICULTY_LABELS[HoldRelativeDifficulty.FACILE] == "Facile"
        assert _DIFFICULTY_LABELS[HoldRelativeDifficulty.NORMALE] == "Normale"
        assert _DIFFICULTY_LABELS[HoldRelativeDifficulty.DURE] == "Difficile"


class TestHoldAnnotationCreation:
    """Tests pour la création d'annotations."""

    def test_create_annotation_minimal(self):
        """Crée une annotation avec seulement le hold_id."""
        ann = HoldAnnotation(hold_id=123)
        assert ann.hold_id == 123
        assert ann.grip_type is None
        assert ann.condition is None
        assert ann.difficulty is None
        assert ann.notes == ""

    def test_create_annotation_full(self):
        """Crée une annotation complète."""
        ann = HoldAnnotation(
            hold_id=456,
            grip_type=HoldGripType.PINCE,
            condition=HoldCondition.A_BROSSER,
            difficulty=HoldRelativeDifficulty.DURE,
            notes="Prise technique"
        )
        assert ann.grip_type == HoldGripType.PINCE
        assert ann.condition == HoldCondition.A_BROSSER
        assert ann.difficulty == HoldRelativeDifficulty.DURE
        assert ann.notes == "Prise technique"


class TestConsensusDisplay:
    """Tests pour l'affichage du consensus."""

    def test_empty_consensus(self):
        """Consensus vide affiche correctement."""
        consensus = HoldConsensus(hold_id=123)
        assert consensus.grip_type is None
        assert consensus.grip_type_votes == 0
        assert consensus.grip_type_confidence == 0.0
        assert consensus.total_annotators == 0

    def test_consensus_with_votes(self):
        """Consensus avec votes."""
        consensus = HoldConsensus(
            hold_id=123,
            grip_type=HoldGripType.BAC,
            grip_type_votes=8,
            grip_type_confidence=0.8,
            condition=HoldCondition.OK,
            condition_votes=10,
            condition_confidence=1.0,
            total_annotators=10
        )
        # Le label devrait être "Bac (8)"
        label = _GRIP_TYPE_LABELS.get(consensus.grip_type, "—")
        assert label == "Bac"
        assert consensus.grip_type_votes == 8


class TestAnnotationDataStructure:
    """Tests pour AnnotationData."""

    def test_annotation_data_without_user(self):
        """AnnotationData sans annotation utilisateur."""
        consensus = HoldConsensus(hold_id=123)
        data = AnnotationData(
            hold_id=123,
            consensus=consensus,
            loaded=True
        )
        assert data.user_annotation is None
        assert data.loaded is True

    def test_annotation_data_with_user(self):
        """AnnotationData avec annotation utilisateur."""
        consensus = HoldConsensus(hold_id=123)
        user_ann = HoldAnnotation(
            hold_id=123,
            grip_type=HoldGripType.REGLETTE
        )
        data = AnnotationData(
            hold_id=123,
            consensus=consensus,
            user_annotation=user_ann,
            loaded=True
        )
        assert data.user_annotation is not None
        assert data.user_annotation.grip_type == HoldGripType.REGLETTE

    def test_annotation_data_with_error(self):
        """AnnotationData avec erreur."""
        consensus = HoldConsensus(hold_id=123)
        data = AnnotationData(
            hold_id=123,
            consensus=consensus,
            loaded=False,
            error="Connection refused"
        )
        assert data.loaded is False
        assert data.error == "Connection refused"


class TestColorModeAnnotations:
    """Tests pour les ColorModes d'annotation."""

    def test_grip_type_mode_exists(self):
        """Vérifie que le mode GRIP_TYPE existe."""
        from mastoc.gui.widgets.hold_overlay import ColorMode
        assert hasattr(ColorMode, 'GRIP_TYPE')
        assert ColorMode.GRIP_TYPE.value == "grip"

    def test_condition_mode_exists(self):
        """Vérifie que le mode CONDITION existe."""
        from mastoc.gui.widgets.hold_overlay import ColorMode
        assert hasattr(ColorMode, 'CONDITION')
        assert ColorMode.CONDITION.value == "condition"

    def test_difficulty_mode_exists(self):
        """Vérifie que le mode DIFFICULTY existe."""
        from mastoc.gui.widgets.hold_overlay import ColorMode
        assert hasattr(ColorMode, 'DIFFICULTY')
        assert ColorMode.DIFFICULTY.value == "difficulty"


class TestGripTypeValueMapping:
    """Tests pour le mapping grip_type → valeur normalisée."""

    def test_grip_type_values(self):
        """Vérifie le mapping des types de prise."""
        from mastoc.gui.widgets.hold_overlay import (
            GRIP_TYPE_VALUES, CONDITION_VALUES, DIFFICULTY_VALUES
        )

        # Vérifier que tous les types sont mappés
        for grip in HoldGripType:
            assert grip in GRIP_TYPE_VALUES, f"HoldGripType.{grip.name} non mappé"
            value = GRIP_TYPE_VALUES[grip]
            assert 0 <= value <= 1, f"Valeur hors bornes: {value}"

        # Valeurs spécifiques
        assert GRIP_TYPE_VALUES[HoldGripType.BAC] == 0.0  # Facile
        assert GRIP_TYPE_VALUES[HoldGripType.MICRO] == 0.92  # Difficile

    def test_condition_values(self):
        """Vérifie le mapping des conditions."""
        from mastoc.gui.widgets.hold_overlay import CONDITION_VALUES

        for cond in HoldCondition:
            assert cond in CONDITION_VALUES, f"HoldCondition.{cond.name} non mappé"

        assert CONDITION_VALUES[HoldCondition.OK] == 0.0  # Bon état
        assert CONDITION_VALUES[HoldCondition.CASSEE] == 1.0  # Mauvais état

    def test_difficulty_values(self):
        """Vérifie le mapping des difficultés."""
        from mastoc.gui.widgets.hold_overlay import DIFFICULTY_VALUES

        for diff in HoldRelativeDifficulty:
            assert diff in DIFFICULTY_VALUES, f"HoldRelativeDifficulty.{diff.name} non mappé"

        assert DIFFICULTY_VALUES[HoldRelativeDifficulty.FACILE] == 0.0
        assert DIFFICULTY_VALUES[HoldRelativeDifficulty.NORMALE] == 0.5
        assert DIFFICULTY_VALUES[HoldRelativeDifficulty.DURE] == 1.0
