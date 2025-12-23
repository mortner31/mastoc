"""
Contrôleur du wizard de création de bloc.

Gère la navigation entre les écrans et l'état partagé.
"""

from enum import Enum, auto
from typing import Optional, Callable
import logging

from PyQt6.QtCore import QObject, pyqtSignal

from .state import ClimbCreationState

logger = logging.getLogger(__name__)


class WizardScreen(Enum):
    """Écrans du wizard de création."""
    SELECT_HOLDS = auto()  # Sélection des prises
    CLIMB_INFO = auto()    # Informations du bloc
    SUBMITTING = auto()    # En cours de soumission
    SUCCESS = auto()       # Création réussie
    ERROR = auto()         # Erreur de création


class WizardController(QObject):
    """
    Contrôleur de navigation pour le wizard de création.

    Gère les transitions entre écrans et maintient l'état partagé.

    Signals:
        screen_changed(WizardScreen): Émis quand l'écran change
        state_changed(): Émis quand l'état change
        validation_failed(list[str]): Émis quand la validation échoue
        creation_started(): Émis au début de la création
        creation_success(str): Émis avec l'ID du climb créé
        creation_failed(str): Émis avec le message d'erreur
    """

    screen_changed = pyqtSignal(object)  # WizardScreen
    state_changed = pyqtSignal()
    validation_failed = pyqtSignal(list)  # list[str]
    creation_started = pyqtSignal()
    creation_success = pyqtSignal(str)
    creation_failed = pyqtSignal(str)

    def __init__(self, face_id: str = ""):
        super().__init__()
        self._state = ClimbCreationState(face_id=face_id)
        self._current_screen = WizardScreen.SELECT_HOLDS
        self._screen_history: list[WizardScreen] = []

        # Callback optionnel pour la soumission (injecté par l'UI)
        self._submit_callback: Optional[Callable[[dict], None]] = None

    @property
    def state(self) -> ClimbCreationState:
        """État actuel de création."""
        return self._state

    @property
    def current_screen(self) -> WizardScreen:
        """Écran actuel."""
        return self._current_screen

    def set_submit_callback(self, callback: Callable[[dict], None]):
        """
        Définit le callback de soumission.

        Le callback reçoit le payload API et doit gérer la requête.
        """
        self._submit_callback = callback

    def goto(self, screen: WizardScreen):
        """
        Change d'écran directement.

        Args:
            screen: Écran cible
        """
        if screen == self._current_screen:
            return

        self._screen_history.append(self._current_screen)
        self._current_screen = screen
        logger.info(f"Wizard: {self._current_screen.name}")
        self.screen_changed.emit(screen)

    def back(self) -> bool:
        """
        Retourne à l'écran précédent.

        Returns:
            True si navigation effectuée, False si impossible
        """
        if not self._screen_history:
            return False

        self._current_screen = self._screen_history.pop()
        logger.info(f"Wizard back: {self._current_screen.name}")
        self.screen_changed.emit(self._current_screen)
        return True

    def next(self) -> bool:
        """
        Passe à l'écran suivant avec validation.

        Returns:
            True si navigation effectuée, False si validation échouée
        """
        if self._current_screen == WizardScreen.SELECT_HOLDS:
            return self._goto_info_screen()
        elif self._current_screen == WizardScreen.CLIMB_INFO:
            return self._submit()
        return False

    def _goto_info_screen(self) -> bool:
        """Valide et passe à l'écran d'informations."""
        can_proceed, errors = self._state.can_go_to_info_screen()
        if not can_proceed:
            logger.warning(f"Cannot proceed to info screen: {errors}")
            self.validation_failed.emit(errors)
            return False

        self.goto(WizardScreen.CLIMB_INFO)
        return True

    def _submit(self) -> bool:
        """Valide et soumet la création."""
        is_valid, errors = self._state.is_valid_for_submit()
        if not is_valid:
            logger.warning(f"Cannot submit: {errors}")
            self.validation_failed.emit(errors)
            return False

        # Passer en mode soumission
        self._state.is_submitting = True
        self._state.submit_error = None
        self.goto(WizardScreen.SUBMITTING)
        self.creation_started.emit()

        # Appeler le callback de soumission si défini
        if self._submit_callback:
            payload = self._state.to_api_payload()
            logger.info(f"Submitting climb: {payload}")
            self._submit_callback(payload)
        else:
            logger.warning("No submit callback defined")
            self.on_creation_failed("Pas de callback de soumission défini")

        return True

    def on_creation_success(self, climb_id: str):
        """
        Appelé quand la création a réussi.

        Args:
            climb_id: ID du climb créé
        """
        self._state.is_submitting = False
        self._state.created_climb_id = climb_id
        self.goto(WizardScreen.SUCCESS)
        self.creation_success.emit(climb_id)
        logger.info(f"Climb created: {climb_id}")

    def on_creation_failed(self, error: str):
        """
        Appelé quand la création a échoué.

        Args:
            error: Message d'erreur
        """
        self._state.is_submitting = False
        self._state.submit_error = error
        self.goto(WizardScreen.ERROR)
        self.creation_failed.emit(error)
        logger.error(f"Climb creation failed: {error}")

    def retry(self):
        """Retente la création après une erreur."""
        self._state.submit_error = None
        self.goto(WizardScreen.CLIMB_INFO)

    def reset(self):
        """Réinitialise le wizard pour une nouvelle création."""
        self._state.reset()
        self._screen_history.clear()
        self._current_screen = WizardScreen.SELECT_HOLDS
        self.screen_changed.emit(self._current_screen)
        self.state_changed.emit()
        logger.info("Wizard reset")

    def can_go_back(self) -> bool:
        """Indique si on peut revenir en arrière."""
        return len(self._screen_history) > 0

    def can_go_next(self) -> bool:
        """Indique si on peut avancer (validation soft)."""
        if self._current_screen == WizardScreen.SELECT_HOLDS:
            can_proceed, _ = self._state.can_go_to_info_screen()
            return can_proceed
        elif self._current_screen == WizardScreen.CLIMB_INFO:
            is_valid, _ = self._state.is_valid_for_submit()
            return is_valid
        return False

    # === Raccourcis pour modifier l'état ===

    def add_hold(self, hold_id: int):
        """Ajoute une prise avec le type actif."""
        self._state.add_hold(hold_id)
        self.state_changed.emit()

    def remove_hold(self, hold_id: int):
        """Retire une prise."""
        self._state.remove_hold(hold_id)
        self.state_changed.emit()

    def set_selection_type(self, hold_type):
        """Change le type de sélection actif."""
        from mastock.api.models import HoldType
        if isinstance(hold_type, HoldType):
            self._state.selection_type = hold_type
            self.state_changed.emit()

    def set_name(self, name: str):
        """Définit le nom du bloc."""
        self._state.name = name
        self.state_changed.emit()

    def set_description(self, description: str):
        """Définit la description."""
        self._state.description = description
        self.state_changed.emit()

    def set_grade(self, system, value: str):
        """Définit le grade."""
        from .state import GradeSystem
        if isinstance(system, GradeSystem):
            self._state.grade_system = system
        self._state.grade_value = value
        self.state_changed.emit()

    def set_private(self, is_private: bool):
        """Définit la visibilité."""
        self._state.is_private = is_private
        self.state_changed.emit()

    def set_feet_rule(self, rule: str):
        """Définit la règle des pieds."""
        self._state.feet_rule = rule
        self.state_changed.emit()
