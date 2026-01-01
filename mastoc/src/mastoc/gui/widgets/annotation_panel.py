"""
Panel d'affichage et d'édition des annotations de prises.

ADR-008 : Hold Annotations (Annotations Crowd-Sourcées).
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTextEdit, QPushButton, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, pyqtSignal

from mastoc.api.models import (
    AnnotationData, HoldAnnotation, HoldConsensus,
    HoldGripType, HoldCondition, HoldRelativeDifficulty
)


# Labels français pour les enums
_GRIP_TYPE_LABELS = {
    None: "— Non spécifié —",
    HoldGripType.PLAT: "Plat",
    HoldGripType.REGLETTE: "Réglette",
    HoldGripType.BI_DOIGT: "Bi-doigt",
    HoldGripType.TRI_DOIGT: "Tri-doigt",
    HoldGripType.MONO_DOIGT: "Mono-doigt",
    HoldGripType.PINCE: "Pince",
    HoldGripType.COLONNETTE: "Colonnette",
    HoldGripType.INVERSE: "Inversé",
    HoldGripType.BAC: "Bac",
    HoldGripType.PRISE_VOLUME: "Prise volume",
    HoldGripType.MICRO: "Micro",
    HoldGripType.AUTRE: "Autre",
}

_CONDITION_LABELS = {
    None: "— Non spécifié —",
    HoldCondition.OK: "OK",
    HoldCondition.A_BROSSER: "À brosser",
    HoldCondition.SALE: "Sale",
    HoldCondition.TOURNEE: "Tournée",
    HoldCondition.USEE: "Usée",
    HoldCondition.CASSEE: "Cassée",
}

_DIFFICULTY_LABELS = {
    None: "— Non spécifié —",
    HoldRelativeDifficulty.FACILE: "Facile",
    HoldRelativeDifficulty.NORMALE: "Normale",
    HoldRelativeDifficulty.DURE: "Difficile",
}


class AnnotationPanel(QWidget):
    """
    Panel affichant et éditant les annotations d'une prise.

    Contient :
    - Section "Consensus" (lecture seule)
    - Section "Mon annotation" (éditable)
    - Boutons Save/Delete
    """

    annotation_changed = pyqtSignal(int, object)  # hold_id, HoldAnnotation ou None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_hold_id = None
        self._current_annotation = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Titre
        self.title_label = QLabel("Sélectionnez une prise")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Section Consensus (lecture seule)
        consensus_group = QGroupBox("Consensus communautaire")
        consensus_layout = QFormLayout(consensus_group)

        self.consensus_grip = QLabel("—")
        self.consensus_condition = QLabel("—")
        self.consensus_difficulty = QLabel("—")
        self.consensus_votes = QLabel("0 votes")

        consensus_layout.addRow("Type:", self.consensus_grip)
        consensus_layout.addRow("État:", self.consensus_condition)
        consensus_layout.addRow("Difficulté:", self.consensus_difficulty)
        consensus_layout.addRow("Votes:", self.consensus_votes)

        layout.addWidget(consensus_group)

        # Section Mon annotation (éditable)
        my_group = QGroupBox("Mon annotation")
        my_layout = QFormLayout(my_group)

        self.grip_combo = QComboBox()
        self._populate_combo(self.grip_combo, _GRIP_TYPE_LABELS)
        my_layout.addRow("Type:", self.grip_combo)

        self.condition_combo = QComboBox()
        self._populate_combo(self.condition_combo, _CONDITION_LABELS)
        my_layout.addRow("État:", self.condition_combo)

        self.difficulty_combo = QComboBox()
        self._populate_combo(self.difficulty_combo, _DIFFICULTY_LABELS)
        my_layout.addRow("Difficulté:", self.difficulty_combo)

        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(60)
        self.notes_edit.setPlaceholderText("Notes optionnelles...")
        my_layout.addRow("Notes:", self.notes_edit)

        layout.addWidget(my_group)

        # Boutons
        buttons_layout = QHBoxLayout()

        self.save_btn = QPushButton("Enregistrer")
        self.save_btn.clicked.connect(self._on_save)
        buttons_layout.addWidget(self.save_btn)

        self.delete_btn = QPushButton("Supprimer")
        self.delete_btn.clicked.connect(self._on_delete)
        buttons_layout.addWidget(self.delete_btn)

        layout.addLayout(buttons_layout)
        layout.addStretch()

        # État initial
        self.set_loading(False)

    def _populate_combo(self, combo: QComboBox, labels: dict):
        """Remplit un combo avec les valeurs de l'enum."""
        for value, label in labels.items():
            combo.addItem(label, value)

    def set_loading(self, loading: bool):
        """Affiche/masque l'état de chargement."""
        self.save_btn.setEnabled(not loading and self._current_hold_id is not None)
        self.delete_btn.setEnabled(not loading and self._current_annotation is not None)

    def set_data(self, hold_id: int, data: AnnotationData):
        """
        Affiche les données d'annotation pour une prise.

        Args:
            hold_id: ID de la prise
            data: Données d'annotation (consensus + user_annotation)
        """
        self._current_hold_id = hold_id
        self._current_annotation = data.user_annotation

        self.title_label.setText(f"Prise #{hold_id}")

        # Consensus
        consensus = data.consensus
        self.consensus_grip.setText(
            _GRIP_TYPE_LABELS.get(consensus.grip_type, "—")
            + f" ({consensus.grip_type_votes})"
            if consensus.grip_type else "—"
        )
        self.consensus_condition.setText(
            _CONDITION_LABELS.get(consensus.condition, "—")
            + f" ({consensus.condition_votes})"
            if consensus.condition else "—"
        )
        self.consensus_difficulty.setText(
            _DIFFICULTY_LABELS.get(consensus.difficulty, "—")
            + f" ({consensus.difficulty_votes})"
            if consensus.difficulty else "—"
        )
        self.consensus_votes.setText(f"{consensus.total_annotators} annotateurs")

        # Mon annotation
        if data.user_annotation:
            ann = data.user_annotation
            self._set_combo_value(self.grip_combo, ann.grip_type)
            self._set_combo_value(self.condition_combo, ann.condition)
            self._set_combo_value(self.difficulty_combo, ann.difficulty)
            self.notes_edit.setText(ann.notes or "")
        else:
            self.grip_combo.setCurrentIndex(0)
            self.condition_combo.setCurrentIndex(0)
            self.difficulty_combo.setCurrentIndex(0)
            self.notes_edit.clear()

        self.set_loading(False)

    def _set_combo_value(self, combo: QComboBox, value):
        """Sélectionne une valeur dans un combo."""
        for i in range(combo.count()):
            if combo.itemData(i) == value:
                combo.setCurrentIndex(i)
                return
        combo.setCurrentIndex(0)

    def clear(self):
        """Efface les données affichées."""
        self._current_hold_id = None
        self._current_annotation = None
        self.title_label.setText("Sélectionnez une prise")
        self.consensus_grip.setText("—")
        self.consensus_condition.setText("—")
        self.consensus_difficulty.setText("—")
        self.consensus_votes.setText("0 votes")
        self.grip_combo.setCurrentIndex(0)
        self.condition_combo.setCurrentIndex(0)
        self.difficulty_combo.setCurrentIndex(0)
        self.notes_edit.clear()
        self.set_loading(False)

    def _on_save(self):
        """Enregistre l'annotation."""
        if self._current_hold_id is None:
            return

        grip_type = self.grip_combo.currentData()
        condition = self.condition_combo.currentData()
        difficulty = self.difficulty_combo.currentData()
        notes = self.notes_edit.toPlainText().strip()

        annotation = HoldAnnotation(
            hold_id=self._current_hold_id,
            grip_type=grip_type,
            condition=condition,
            difficulty=difficulty,
            notes=notes,
        )

        self._current_annotation = annotation
        self.delete_btn.setEnabled(True)
        self.annotation_changed.emit(self._current_hold_id, annotation)

    def _on_delete(self):
        """Supprime l'annotation."""
        if self._current_hold_id is None:
            return

        self._current_annotation = None
        self.grip_combo.setCurrentIndex(0)
        self.condition_combo.setCurrentIndex(0)
        self.difficulty_combo.setCurrentIndex(0)
        self.notes_edit.clear()
        self.delete_btn.setEnabled(False)
        self.annotation_changed.emit(self._current_hold_id, None)
