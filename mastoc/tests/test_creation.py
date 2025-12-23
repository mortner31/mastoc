"""
Tests pour le module de création de blocs.
"""

import pytest
from unittest.mock import Mock, patch

from mastoc.api.models import HoldType
from mastoc.gui.creation import (
    ClimbCreationState,
    HoldSelection,
    GradeSystem,
    GRADE_VALUES,
    WizardController,
    WizardScreen,
)


class TestHoldSelection:
    """Tests pour HoldSelection."""

    def test_to_api_format_start(self):
        """Test format API pour prise START."""
        hs = HoldSelection(hold_id=123, hold_type=HoldType.START)
        assert hs.to_api_format() == "S123"

    def test_to_api_format_other(self):
        """Test format API pour prise OTHER."""
        hs = HoldSelection(hold_id=456, hold_type=HoldType.OTHER)
        assert hs.to_api_format() == "O456"

    def test_to_api_format_feet(self):
        """Test format API pour prise FEET."""
        hs = HoldSelection(hold_id=789, hold_type=HoldType.FEET)
        assert hs.to_api_format() == "F789"

    def test_to_api_format_top(self):
        """Test format API pour prise TOP."""
        hs = HoldSelection(hold_id=999, hold_type=HoldType.TOP)
        assert hs.to_api_format() == "T999"


class TestClimbCreationState:
    """Tests pour ClimbCreationState."""

    def test_default_state(self):
        """Test état par défaut."""
        state = ClimbCreationState()
        assert state.start_holds == []
        assert state.other_holds == []
        assert state.feet_holds == []
        assert state.top_holds == []
        assert state.selection_type == HoldType.OTHER
        assert state.name == ""
        assert state.grade_system == GradeSystem.FONT
        assert state.is_private == False

    def test_add_hold_default_type(self):
        """Test ajout de prise avec type par défaut."""
        state = ClimbCreationState()
        state.selection_type = HoldType.START
        state.add_hold(123)
        assert 123 in state.start_holds
        assert state.total_holds() == 1

    def test_add_hold_explicit_type(self):
        """Test ajout de prise avec type explicite."""
        state = ClimbCreationState()
        state.add_hold(123, HoldType.TOP)
        assert 123 in state.top_holds
        assert 123 not in state.start_holds

    def test_add_hold_moves_between_types(self):
        """Test que l'ajout déplace la prise d'un type à l'autre."""
        state = ClimbCreationState()
        state.add_hold(123, HoldType.START)
        assert 123 in state.start_holds

        state.add_hold(123, HoldType.TOP)
        assert 123 not in state.start_holds
        assert 123 in state.top_holds
        assert state.total_holds() == 1

    def test_remove_hold(self):
        """Test suppression de prise."""
        state = ClimbCreationState()
        state.add_hold(123, HoldType.START)
        state.add_hold(456, HoldType.OTHER)

        old_type = state.remove_hold(123)
        assert old_type == HoldType.START
        assert 123 not in state.start_holds
        assert state.total_holds() == 1

    def test_remove_nonexistent_hold(self):
        """Test suppression de prise inexistante."""
        state = ClimbCreationState()
        old_type = state.remove_hold(999)
        assert old_type is None

    def test_get_hold_type(self):
        """Test récupération du type d'une prise."""
        state = ClimbCreationState()
        state.add_hold(123, HoldType.FEET)
        assert state.get_hold_type(123) == HoldType.FEET
        assert state.get_hold_type(999) is None

    def test_get_all_holds(self):
        """Test récupération de toutes les prises."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.OTHER)
        state.add_hold(4, HoldType.TOP)

        all_holds = state.get_all_holds()
        assert len(all_holds) == 4
        assert HoldSelection(1, HoldType.START) in all_holds
        assert HoldSelection(4, HoldType.TOP) in all_holds

    def test_get_holds_list_str(self):
        """Test génération de la chaîne holdsList."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.OTHER)
        state.add_hold(4, HoldType.TOP)

        result = state.get_holds_list_str()
        assert "S1" in result
        assert "S2" in result
        assert "O3" in result
        assert "T4" in result

    def test_get_holds_dict(self):
        """Test génération du dictionnaire holdsList."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.OTHER)
        state.add_hold(4, HoldType.FEET)
        state.add_hold(5, HoldType.TOP)

        result = state.get_holds_dict()
        assert result["start"] == ["1", "2"]
        assert result["others"] == ["3"]
        assert result["feetOnly"] == ["4"]
        assert result["top"] == ["5"]

    def test_can_go_to_info_screen_invalid(self):
        """Test validation pour passer à l'écran info - invalide."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)  # 1 seul START

        can_proceed, errors = state.can_go_to_info_screen()
        assert can_proceed == False
        assert len(errors) == 2
        assert any("2 prises de départ" in e for e in errors)
        assert any("1 prise d'arrivée" in e for e in errors)

    def test_can_go_to_info_screen_valid(self):
        """Test validation pour passer à l'écran info - valide."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.TOP)

        can_proceed, errors = state.can_go_to_info_screen()
        assert can_proceed == True
        assert errors == []

    def test_is_valid_for_submit_invalid(self):
        """Test validation pour soumission - invalide."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.TOP)
        # Manque: name, grade

        is_valid, errors = state.is_valid_for_submit()
        assert is_valid == False
        assert any("nom" in e.lower() for e in errors)
        assert any("grade" in e.lower() for e in errors)

    def test_is_valid_for_submit_name_too_short(self):
        """Test validation nom trop court."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.TOP)
        state.name = "AB"  # 2 caractères
        state.grade_value = "6a"

        is_valid, errors = state.is_valid_for_submit()
        assert is_valid == False
        assert any("3 caractères" in e for e in errors)

    def test_is_valid_for_submit_valid(self):
        """Test validation pour soumission - valide."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.TOP)
        state.name = "Mon bloc"
        state.grade_value = "6a"

        is_valid, errors = state.is_valid_for_submit()
        assert is_valid == True
        assert errors == []

    def test_to_api_payload(self):
        """Test génération du payload API."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.add_hold(2, HoldType.START)
        state.add_hold(3, HoldType.TOP)
        state.name = "Test bloc"
        state.description = "Une description"
        state.grade_system = GradeSystem.FONT
        state.grade_value = "6A+"  # Majuscule pour l'API
        state.is_private = True
        state.feet_rule = "Free feet"

        payload = state.to_api_payload()

        assert payload["name"] == "Test bloc"
        assert payload["description"] == "Une description"
        assert payload["grade"]["gradingSystem"] == "font"  # Minuscule pour l'API
        assert payload["grade"]["value"] == "6A+"
        assert payload["attemptsNumber"] is None  # Requis par l'API
        assert payload["isPrivate"] == True
        assert payload["feetRule"] == "Free feet"
        assert payload["holdsList"]["start"] == ["1", "2"]
        assert payload["holdsList"]["top"] == ["3"]

    def test_reset(self):
        """Test réinitialisation de l'état."""
        state = ClimbCreationState()
        state.add_hold(1, HoldType.START)
        state.name = "Test"
        state.is_submitting = True

        state.reset()

        assert state.total_holds() == 0
        assert state.name == ""
        assert state.is_submitting == False


class TestGradeSystem:
    """Tests pour les grades."""

    def test_font_grades_exist(self):
        """Test que les grades Fontainebleau existent (majuscules)."""
        assert GradeSystem.FONT in GRADE_VALUES
        assert "6A" in GRADE_VALUES[GradeSystem.FONT]
        assert "7B+" in GRADE_VALUES[GradeSystem.FONT]

    def test_v_scale_grades_exist(self):
        """Test que les grades V-Scale existent."""
        assert GradeSystem.V_SCALE in GRADE_VALUES
        assert "V0" in GRADE_VALUES[GradeSystem.V_SCALE]
        assert "V10" in GRADE_VALUES[GradeSystem.V_SCALE]

    def test_dankyu_grades_exist(self):
        """Test que les grades Dankyu existent."""
        assert GradeSystem.DANKYU in GRADE_VALUES
        assert "6Q" in GRADE_VALUES[GradeSystem.DANKYU]
        assert "1D" in GRADE_VALUES[GradeSystem.DANKYU]


class TestWizardController:
    """Tests pour WizardController."""

    def test_initial_screen(self):
        """Test écran initial."""
        controller = WizardController()
        assert controller.current_screen == WizardScreen.SELECT_HOLDS

    def test_initial_state(self):
        """Test état initial."""
        controller = WizardController(face_id="test-face-id")
        assert controller.state.face_id == "test-face-id"
        assert controller.state.total_holds() == 0

    def test_goto_screen(self):
        """Test navigation directe."""
        controller = WizardController()
        controller.goto(WizardScreen.CLIMB_INFO)
        assert controller.current_screen == WizardScreen.CLIMB_INFO

    def test_back_no_history(self):
        """Test retour sans historique."""
        controller = WizardController()
        result = controller.back()
        assert result == False
        assert controller.current_screen == WizardScreen.SELECT_HOLDS

    def test_back_with_history(self):
        """Test retour avec historique."""
        controller = WizardController()
        controller.goto(WizardScreen.CLIMB_INFO)
        result = controller.back()
        assert result == True
        assert controller.current_screen == WizardScreen.SELECT_HOLDS

    def test_next_fails_without_holds(self):
        """Test que next échoue sans prises valides."""
        controller = WizardController()
        # Connecter un slot pour capturer validation_failed
        errors_received = []
        controller.validation_failed.connect(lambda e: errors_received.extend(e))

        result = controller.next()
        assert result == False
        assert len(errors_received) > 0

    def test_next_succeeds_with_valid_holds(self):
        """Test que next réussit avec prises valides."""
        controller = WizardController()
        controller.state.add_hold(1, HoldType.START)
        controller.state.add_hold(2, HoldType.START)
        controller.state.add_hold(3, HoldType.TOP)

        result = controller.next()
        assert result == True
        assert controller.current_screen == WizardScreen.CLIMB_INFO

    def test_add_hold_via_controller(self):
        """Test ajout de prise via contrôleur."""
        controller = WizardController()
        controller.state.selection_type = HoldType.START
        controller.add_hold(123)

        assert 123 in controller.state.start_holds
        assert controller.state.total_holds() == 1

    def test_set_name(self):
        """Test définition du nom."""
        controller = WizardController()
        controller.set_name("Mon bloc")
        assert controller.state.name == "Mon bloc"

    def test_set_grade(self):
        """Test définition du grade."""
        controller = WizardController()
        controller.set_grade(GradeSystem.V_SCALE, "V5")
        assert controller.state.grade_system == GradeSystem.V_SCALE
        assert controller.state.grade_value == "V5"

    def test_can_go_back(self):
        """Test can_go_back."""
        controller = WizardController()
        assert controller.can_go_back() == False

        controller.goto(WizardScreen.CLIMB_INFO)
        assert controller.can_go_back() == True

    def test_can_go_next(self):
        """Test can_go_next."""
        controller = WizardController()
        assert controller.can_go_next() == False  # Pas assez de prises

        controller.state.add_hold(1, HoldType.START)
        controller.state.add_hold(2, HoldType.START)
        controller.state.add_hold(3, HoldType.TOP)
        assert controller.can_go_next() == True

    def test_reset(self):
        """Test réinitialisation."""
        controller = WizardController()
        controller.state.add_hold(1, HoldType.START)
        controller.goto(WizardScreen.CLIMB_INFO)

        controller.reset()

        assert controller.current_screen == WizardScreen.SELECT_HOLDS
        assert controller.state.total_holds() == 0
        assert controller.can_go_back() == False

    def test_submit_callback(self):
        """Test callback de soumission."""
        controller = WizardController()
        callback_called = []

        def mock_callback(payload):
            callback_called.append(payload)

        controller.set_submit_callback(mock_callback)

        # Préparer un état valide
        controller.state.add_hold(1, HoldType.START)
        controller.state.add_hold(2, HoldType.START)
        controller.state.add_hold(3, HoldType.TOP)
        controller.state.name = "Test"
        controller.state.grade_value = "6a"

        # Aller à l'écran info puis soumettre
        controller.next()  # SELECT_HOLDS -> CLIMB_INFO
        controller.next()  # CLIMB_INFO -> SUBMITTING

        assert len(callback_called) == 1
        assert callback_called[0]["name"] == "Test"

    def test_creation_success(self):
        """Test succès de création."""
        controller = WizardController()
        controller.goto(WizardScreen.SUBMITTING)

        success_ids = []
        controller.creation_success.connect(lambda id: success_ids.append(id))

        controller.on_creation_success("climb-123")

        assert controller.current_screen == WizardScreen.SUCCESS
        assert controller.state.created_climb_id == "climb-123"
        assert "climb-123" in success_ids

    def test_creation_failed(self):
        """Test échec de création."""
        controller = WizardController()
        controller.goto(WizardScreen.SUBMITTING)

        errors = []
        controller.creation_failed.connect(lambda e: errors.append(e))

        controller.on_creation_failed("Erreur réseau")

        assert controller.current_screen == WizardScreen.ERROR
        assert controller.state.submit_error == "Erreur réseau"
        assert "Erreur réseau" in errors

    def test_retry_after_error(self):
        """Test retry après erreur."""
        controller = WizardController()
        controller.goto(WizardScreen.ERROR)
        controller.state.submit_error = "Une erreur"

        controller.retry()

        assert controller.current_screen == WizardScreen.CLIMB_INFO
        assert controller.state.submit_error is None


class TestWizardScreenSignals:
    """Tests pour les signaux du contrôleur."""

    def test_screen_changed_signal(self):
        """Test signal screen_changed."""
        controller = WizardController()
        screens_received = []
        controller.screen_changed.connect(lambda s: screens_received.append(s))

        controller.goto(WizardScreen.CLIMB_INFO)

        assert WizardScreen.CLIMB_INFO in screens_received

    def test_state_changed_signal(self):
        """Test signal state_changed."""
        controller = WizardController()
        changes = []
        controller.state_changed.connect(lambda: changes.append(1))

        controller.add_hold(123)
        controller.set_name("Test")

        assert len(changes) == 2
