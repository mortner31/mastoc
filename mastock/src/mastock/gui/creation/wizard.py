"""
Widget wizard de création de bloc.

Contient un QStackedWidget pour naviguer entre les écrans de création.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QMessageBox, QProgressBar
)
from PyQt6.QtCore import pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QMovie, QFont

from mastock.core.hold_index import HoldClimbIndex
from mastock.api.client import StoktAPI
from .controller import WizardController, WizardScreen
from .state import ClimbCreationState

logger = logging.getLogger(__name__)


class CreationWizard(QWidget):
    """
    Widget wizard multi-écrans pour la création de blocs.

    Utilise un QStackedWidget pour naviguer entre:
    - SelectHoldsScreen: Sélection des prises
    - ClimbInfoScreen: Informations du bloc
    - Écrans de feedback (loading, succès, erreur)

    Signals:
        climb_created(str): Émis avec l'ID du climb créé
        cancelled(): Émis quand l'utilisateur annule
    """

    climb_created = pyqtSignal(str)
    cancelled = pyqtSignal()

    def __init__(
        self,
        index: HoldClimbIndex,
        api: Optional[StoktAPI] = None,
        face_id: str = "",
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.index = index
        self.api = api

        # Contrôleur
        self.controller = WizardController(face_id=face_id)
        self.controller.screen_changed.connect(self._on_screen_changed)
        self.controller.state_changed.connect(self._update_navigation)
        self.controller.validation_failed.connect(self._on_validation_failed)
        self.controller.creation_success.connect(self._on_creation_success)
        self.controller.creation_failed.connect(self._on_creation_failed)

        # Callback de soumission
        self.controller.set_submit_callback(self._do_submit)

        # Écrans (créés à la demande)
        self._screens: dict[WizardScreen, QWidget] = {}

        self._setup_ui()

    def _setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header avec progression
        self.header = self._create_header()
        layout.addWidget(self.header)

        # Séparateur
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(sep)

        # Stack des écrans
        self.stack = QStackedWidget()
        layout.addWidget(self.stack, stretch=1)

        # Footer avec boutons de navigation
        self.footer = self._create_footer()
        layout.addWidget(self.footer)

        # Créer et afficher le premier écran
        self._ensure_screen(WizardScreen.SELECT_HOLDS)
        self._update_navigation()

    def _create_header(self) -> QWidget:
        """Crée le header avec indicateur de progression."""
        header = QWidget()
        layout = QHBoxLayout(header)
        layout.setContentsMargins(10, 5, 10, 5)

        # Titre
        self.title_label = QLabel("Nouveau bloc")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Indicateur d'étape
        self.step_label = QLabel("Étape 1/2")
        self.step_label.setStyleSheet("color: gray;")
        layout.addWidget(self.step_label)

        return header

    def _create_footer(self) -> QWidget:
        """Crée le footer avec boutons de navigation."""
        footer = QWidget()
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(10, 5, 10, 5)

        # Bouton Annuler
        self.cancel_btn = QPushButton("Annuler")
        self.cancel_btn.clicked.connect(self._on_cancel)
        layout.addWidget(self.cancel_btn)

        layout.addStretch()

        # Bouton Précédent
        self.back_btn = QPushButton("Précédent")
        self.back_btn.clicked.connect(self._on_back)
        layout.addWidget(self.back_btn)

        # Bouton Suivant/Publier
        self.next_btn = QPushButton("Suivant")
        self.next_btn.clicked.connect(self._on_next)
        self.next_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:disabled {
                background-color: #9E9E9E;
                color: #BDBDBD;
            }
            QPushButton:hover:!disabled {
                background-color: #45a049;
            }
        """)
        layout.addWidget(self.next_btn)

        return footer

    def _ensure_screen(self, screen: WizardScreen):
        """Crée un écran s'il n'existe pas encore."""
        if screen in self._screens:
            return

        widget = self._create_screen(screen)
        if widget:
            self._screens[screen] = widget
            self.stack.addWidget(widget)

    def _create_screen(self, screen: WizardScreen) -> Optional[QWidget]:
        """Crée un widget pour un écran donné."""
        if screen == WizardScreen.SELECT_HOLDS:
            return self._create_select_holds_screen()
        elif screen == WizardScreen.CLIMB_INFO:
            return self._create_climb_info_screen()
        elif screen == WizardScreen.SUBMITTING:
            return self._create_submitting_screen()
        elif screen == WizardScreen.SUCCESS:
            return self._create_success_screen()
        elif screen == WizardScreen.ERROR:
            return self._create_error_screen()
        return None

    def _create_select_holds_screen(self) -> QWidget:
        """Crée l'écran de sélection des prises."""
        # Import local pour éviter les dépendances circulaires
        from .screens.select_holds import SelectHoldsScreen
        screen = SelectHoldsScreen(self.controller, self.index)
        return screen

    def _create_climb_info_screen(self) -> QWidget:
        """Crée l'écran d'informations du bloc."""
        from .screens.climb_info import ClimbInfoScreen
        screen = ClimbInfoScreen(self.controller)
        return screen

    def _create_submitting_screen(self) -> QWidget:
        """Crée l'écran de chargement avec spinner animé."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icône de chargement (texte animé)
        self.loading_label = QLabel("Publication en cours")
        self.loading_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

        # Barre de progression indéterminée
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Mode indéterminé
        self.progress_bar.setMaximumWidth(300)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #4CAF50;
                border-radius: 5px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        layout.addWidget(self.progress_bar, alignment=Qt.AlignmentFlag.AlignCenter)

        # Timer pour animer les points
        self._loading_dots = 0
        self._loading_timer = QTimer()
        self._loading_timer.timeout.connect(self._animate_loading)
        self._loading_timer.start(500)

        # Message secondaire
        hint = QLabel("Envoi vers le serveur...")
        hint.setStyleSheet("color: gray; font-size: 12px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        return widget

    def _animate_loading(self):
        """Anime les points de chargement."""
        self._loading_dots = (self._loading_dots + 1) % 4
        dots = "." * self._loading_dots
        self.loading_label.setText(f"Publication en cours{dots}")

    def _create_success_screen(self) -> QWidget:
        """Crée l'écran de succès."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icône de succès (emoji)
        icon = QLabel("✓")
        icon.setStyleSheet("font-size: 64px; color: #4CAF50;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        label = QLabel("Bloc créé avec succès !")
        label.setStyleSheet("font-size: 20px; color: #4CAF50; font-weight: bold;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # ID du climb créé
        self.success_id_label = QLabel("")
        self.success_id_label.setStyleSheet("color: gray; font-size: 12px;")
        self.success_id_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.success_id_label)

        return widget

    def _create_error_screen(self) -> QWidget:
        """Crée l'écran d'erreur."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Icône d'erreur
        icon = QLabel("✗")
        icon.setStyleSheet("font-size: 64px; color: #f44336;")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("Erreur lors de la création")
        title.setStyleSheet("font-size: 20px; color: #f44336; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Message d'erreur détaillé
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            background-color: #ffebee;
            padding: 10px;
            border-radius: 5px;
        """)
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setMaximumWidth(400)
        layout.addWidget(self.error_label)

        # Suggestion
        hint = QLabel("Vérifiez votre connexion et réessayez")
        hint.setStyleSheet("color: gray; font-size: 12px; margin-top: 10px;")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint)

        return widget

    def _on_screen_changed(self, screen: WizardScreen):
        """Appelé quand l'écran change."""
        self._ensure_screen(screen)
        if screen in self._screens:
            self.stack.setCurrentWidget(self._screens[screen])
        self._update_navigation()

    def _update_navigation(self):
        """Met à jour les boutons et indicateurs de navigation."""
        screen = self.controller.current_screen

        # Titre et étape
        if screen == WizardScreen.SELECT_HOLDS:
            self.title_label.setText("Sélection des prises")
            self.step_label.setText("Étape 1/2")
        elif screen == WizardScreen.CLIMB_INFO:
            self.title_label.setText("Informations")
            self.step_label.setText("Étape 2/2")
        elif screen == WizardScreen.SUBMITTING:
            self.title_label.setText("Publication")
            self.step_label.setText("")
        elif screen == WizardScreen.SUCCESS:
            self.title_label.setText("Terminé")
            self.step_label.setText("")
        elif screen == WizardScreen.ERROR:
            self.title_label.setText("Erreur")
            self.step_label.setText("")

        # Boutons
        self.back_btn.setVisible(screen in (
            WizardScreen.SELECT_HOLDS,
            WizardScreen.CLIMB_INFO,
            WizardScreen.ERROR,
        ))
        self.back_btn.setEnabled(self.controller.can_go_back())

        if screen == WizardScreen.CLIMB_INFO:
            self.next_btn.setText("Publier")
        elif screen == WizardScreen.SUCCESS:
            self.next_btn.setText("Fermer")
        elif screen == WizardScreen.ERROR:
            self.next_btn.setText("Réessayer")
        else:
            self.next_btn.setText("Suivant")

        self.next_btn.setVisible(screen not in (WizardScreen.SUBMITTING,))

        # Activer/désactiver selon la validation
        if screen in (WizardScreen.SELECT_HOLDS, WizardScreen.CLIMB_INFO):
            self.next_btn.setEnabled(self.controller.can_go_next())
        else:
            self.next_btn.setEnabled(True)

    def _on_back(self):
        """Retour à l'écran précédent."""
        self.controller.back()

    def _on_next(self):
        """Passe à l'écran suivant ou action spéciale."""
        screen = self.controller.current_screen

        if screen == WizardScreen.SUCCESS:
            self.climb_created.emit(self.controller.state.created_climb_id or "")
            return

        if screen == WizardScreen.ERROR:
            self.controller.retry()
            return

        self.controller.next()

    def _on_cancel(self):
        """Annule la création."""
        if self.controller.state.total_holds() > 0:
            reply = QMessageBox.question(
                self,
                "Annuler",
                "Voulez-vous vraiment annuler ? Les prises sélectionnées seront perdues.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.controller.reset()
        self.cancelled.emit()

    def _on_validation_failed(self, errors: list[str]):
        """Appelé quand la validation échoue."""
        QMessageBox.warning(
            self,
            "Validation",
            "Veuillez corriger les erreurs:\n\n" + "\n".join(f"- {e}" for e in errors)
        )

    def _on_creation_success(self, climb_id: str):
        """Appelé quand la création a réussi."""
        logger.info(f"Climb created successfully: {climb_id}")
        # Arrêter le timer de loading
        self._stop_loading_timer()
        # Afficher l'ID du climb
        if hasattr(self, 'success_id_label'):
            self.success_id_label.setText(f"ID: {climb_id}")

    def _on_creation_failed(self, error: str):
        """Appelé quand la création a échoué."""
        # Arrêter le timer de loading
        self._stop_loading_timer()
        # Afficher le message d'erreur
        if hasattr(self, 'error_label'):
            self.error_label.setText(error)

    def _stop_loading_timer(self):
        """Arrête le timer de loading s'il existe."""
        if hasattr(self, '_loading_timer') and self._loading_timer.isActive():
            self._loading_timer.stop()

    def _do_submit(self, payload: dict):
        """Soumet la création à l'API."""
        if not self.api:
            self.controller.on_creation_failed("API non configurée")
            return

        face_id = self.controller.state.face_id
        if not face_id:
            self.controller.on_creation_failed("Face ID manquant")
            return

        try:
            # Créer le climb via l'API
            result = self.api.create_climb(face_id, payload)
            self.controller.on_creation_success(result.id)
        except Exception as e:
            error_msg = str(e)
            # Extraire le message d'erreur de la réponse si disponible
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'nonFieldErrors' in error_data:
                        error_msg = error_data['nonFieldErrors'][0]
                    elif isinstance(error_data, dict):
                        # Première erreur trouvée
                        for key, value in error_data.items():
                            if isinstance(value, list) and value:
                                error_msg = f"{key}: {value[0]}"
                                break
                except Exception:
                    pass
            self.controller.on_creation_failed(error_msg)

    def reset(self):
        """Réinitialise le wizard."""
        self.controller.reset()
