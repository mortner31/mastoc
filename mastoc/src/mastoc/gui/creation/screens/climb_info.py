"""
Écran d'informations du bloc pour la création.

Permet de saisir le nom, grade, description et options du bloc.
"""

import logging
from typing import Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox,
    QFrame, QGroupBox
)
from PyQt6.QtCore import Qt

from ..controller import WizardController
from ..state import GradeSystem, GRADE_VALUES

logger = logging.getLogger(__name__)


class ClimbInfoScreen(QWidget):
    """
    Écran de saisie des informations du bloc.

    Champs:
    - Nom (obligatoire, min 3 caractères)
    - Grade (obligatoire)
    - Description (optionnel)
    - Règle des pieds (optionnel)
    - Privé/Public
    """

    def __init__(
        self,
        controller: WizardController,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.controller = controller

        self._setup_ui()
        self._connect_signals()
        self._load_state()

    def _setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Résumé des prises
        summary = self._create_summary_section()
        layout.addWidget(summary)

        # Séparateur
        layout.addWidget(self._separator())

        # Formulaire principal
        form_group = QGroupBox("Informations du bloc")
        form_layout = QFormLayout(form_group)
        form_layout.setSpacing(10)

        # Nom
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Nom du bloc (min 3 caractères)")
        self.name_edit.setMaxLength(50)
        self.name_edit.textChanged.connect(self._on_name_changed)
        form_layout.addRow("Nom *", self.name_edit)

        self.name_error = QLabel()
        self.name_error.setStyleSheet("color: red; font-size: 11px;")
        form_layout.addRow("", self.name_error)

        # Grade
        grade_widget = QWidget()
        grade_layout = QHBoxLayout(grade_widget)
        grade_layout.setContentsMargins(0, 0, 0, 0)

        self.grade_system_combo = QComboBox()
        self.grade_system_combo.addItem("Fontainebleau", GradeSystem.FONT)
        self.grade_system_combo.addItem("V-Scale", GradeSystem.V_SCALE)
        self.grade_system_combo.addItem("Dankyu", GradeSystem.DANKYU)
        self.grade_system_combo.currentIndexChanged.connect(self._on_grade_system_changed)
        grade_layout.addWidget(self.grade_system_combo)

        self.grade_value_combo = QComboBox()
        self.grade_value_combo.currentIndexChanged.connect(self._on_grade_value_changed)
        grade_layout.addWidget(self.grade_value_combo, stretch=1)

        form_layout.addRow("Grade *", grade_widget)

        # Peupler les valeurs de grade
        self._populate_grade_values()

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Description (optionnel)")
        self.description_edit.setMaximumHeight(80)
        self.description_edit.textChanged.connect(self._on_description_changed)
        form_layout.addRow("Description", self.description_edit)

        # Règle des pieds
        self.feet_rule_combo = QComboBox()
        self.feet_rule_combo.addItem("Pas de restriction", "")
        self.feet_rule_combo.addItem("Pieds libres", "Free feet")
        self.feet_rule_combo.addItem("Pieds suivent", "Feet follow hands")
        self.feet_rule_combo.addItem("Pas de pieds", "No feet")
        self.feet_rule_combo.currentIndexChanged.connect(self._on_feet_rule_changed)
        form_layout.addRow("Règle pieds", self.feet_rule_combo)

        layout.addWidget(form_group)

        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        self.private_check = QCheckBox("Bloc privé (visible uniquement par moi)")
        self.private_check.stateChanged.connect(self._on_private_changed)
        options_layout.addWidget(self.private_check)

        layout.addWidget(options_group)

        # Validation
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("color: red;")
        layout.addWidget(self.validation_label)

        layout.addStretch()

    def _create_summary_section(self) -> QWidget:
        """Crée la section résumé des prises."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        self.summary_label = QLabel()
        self.summary_label.setStyleSheet("color: gray;")
        layout.addWidget(self.summary_label)

        layout.addStretch()

        return widget

    def _separator(self) -> QFrame:
        """Crée un séparateur horizontal."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #ccc;")
        return sep

    def _connect_signals(self):
        """Connecte les signaux."""
        self.controller.state_changed.connect(self._load_state)

    def _populate_grade_values(self):
        """Remplit le combo des valeurs de grade."""
        # Bloquer les signaux pour éviter les boucles
        was_blocked = self.grade_value_combo.signalsBlocked()
        self.grade_value_combo.blockSignals(True)

        self.grade_value_combo.clear()
        system = self.grade_system_combo.currentData()
        if system and system in GRADE_VALUES:
            for value in GRADE_VALUES[system]:
                self.grade_value_combo.addItem(value, value)

        # Restaurer l'état précédent des signaux
        self.grade_value_combo.blockSignals(was_blocked)

    def _load_state(self):
        """Charge l'état dans le formulaire."""
        state = self.controller.state

        # Résumé des prises
        self.summary_label.setText(
            f"Prises: {len(state.start_holds)} départ, "
            f"{len(state.other_holds)} intermédiaires, "
            f"{len(state.feet_holds)} pieds, "
            f"{len(state.top_holds)} arrivée"
        )

        # Ne pas mettre à jour si l'utilisateur est en train de taper
        if not self.name_edit.hasFocus():
            if self.name_edit.text() != state.name:
                self.name_edit.blockSignals(True)
                self.name_edit.setText(state.name)
                self.name_edit.blockSignals(False)

        if not self.description_edit.hasFocus():
            if self.description_edit.toPlainText() != state.description:
                self.description_edit.blockSignals(True)
                self.description_edit.setPlainText(state.description)
                self.description_edit.blockSignals(False)

        # Bloquer les signaux pour éviter les boucles infinies
        self.grade_system_combo.blockSignals(True)
        self.grade_value_combo.blockSignals(True)
        self.feet_rule_combo.blockSignals(True)
        self.private_check.blockSignals(True)

        # Grade system
        for i in range(self.grade_system_combo.count()):
            if self.grade_system_combo.itemData(i) == state.grade_system:
                if self.grade_system_combo.currentIndex() != i:
                    self.grade_system_combo.setCurrentIndex(i)
                    self._populate_grade_values()
                break

        # Grade value
        for i in range(self.grade_value_combo.count()):
            if self.grade_value_combo.itemData(i) == state.grade_value:
                if self.grade_value_combo.currentIndex() != i:
                    self.grade_value_combo.setCurrentIndex(i)
                break

        # Feet rule
        for i in range(self.feet_rule_combo.count()):
            if self.feet_rule_combo.itemData(i) == state.feet_rule:
                if self.feet_rule_combo.currentIndex() != i:
                    self.feet_rule_combo.setCurrentIndex(i)
                break

        # Private
        if self.private_check.isChecked() != state.is_private:
            self.private_check.setChecked(state.is_private)

        # Réactiver les signaux
        self.grade_system_combo.blockSignals(False)
        self.grade_value_combo.blockSignals(False)
        self.feet_rule_combo.blockSignals(False)
        self.private_check.blockSignals(False)

        # Validation
        self._update_validation()

    def _on_name_changed(self, text: str):
        """Appelé quand le nom change."""
        self.controller.set_name(text)
        self._validate_name(text)

    def _validate_name(self, text: str):
        """Valide le nom et affiche les erreurs."""
        if not text:
            self.name_error.setText("Le nom est requis")
        elif len(text) < 3:
            self.name_error.setText(f"Minimum 3 caractères ({len(text)}/3)")
        else:
            self.name_error.setText("")

    def _on_grade_system_changed(self, index: int):
        """Appelé quand le système de grade change."""
        system = self.grade_system_combo.currentData()
        if system:
            self._populate_grade_values()
            value = self.grade_value_combo.currentData() or ""
            self.controller.set_grade(system, value)

    def _on_grade_value_changed(self, index: int):
        """Appelé quand la valeur de grade change."""
        system = self.grade_system_combo.currentData()
        value = self.grade_value_combo.currentData() or ""
        if system:
            self.controller.set_grade(system, value)

    def _on_description_changed(self):
        """Appelé quand la description change."""
        self.controller.set_description(self.description_edit.toPlainText())

    def _on_feet_rule_changed(self, index: int):
        """Appelé quand la règle des pieds change."""
        rule = self.feet_rule_combo.currentData() or ""
        self.controller.set_feet_rule(rule)

    def _on_private_changed(self, state: int):
        """Appelé quand l'option privé change."""
        self.controller.set_private(state == Qt.CheckState.Checked.value)

    def _update_validation(self):
        """Met à jour le message de validation global."""
        is_valid, errors = self.controller.state.is_valid_for_submit()
        if is_valid:
            self.validation_label.setText("")
        else:
            # Filtrer les erreurs déjà affichées ailleurs
            filtered = [e for e in errors if "prises" not in e.lower()]
            self.validation_label.setText("\n".join(filtered))
