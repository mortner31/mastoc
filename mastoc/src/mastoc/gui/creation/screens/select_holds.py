"""
Écran de sélection des prises pour la création de bloc.

Permet de sélectionner des prises et leur assigner un type
(START, OTHER, FEET, TOP).
"""

import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pyqtgraph as pg
from PIL import Image, ImageEnhance
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QLabel, QPushButton, QFrame, QButtonGroup, QRadioButton,
    QSlider, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from mastoc.api.models import HoldType
from mastoc.core.hold_index import HoldClimbIndex
from mastoc.gui.widgets.hold_overlay import HoldOverlay
from ..controller import WizardController

logger = logging.getLogger(__name__)


# Couleurs par type de prise
HOLD_TYPE_COLORS = {
    HoldType.START: (255, 200, 0, 200),    # Jaune/Or
    HoldType.OTHER: (100, 200, 255, 200),  # Bleu clair
    HoldType.FEET: (49, 218, 255, 200),    # Cyan (NEON_BLUE)
    HoldType.TOP: (255, 100, 100, 200),    # Rouge
}

HOLD_TYPE_LABELS = {
    HoldType.START: "Départ (S)",
    HoldType.OTHER: "Intermédiaire (O)",
    HoldType.FEET: "Pieds (F)",
    HoldType.TOP: "Arrivée (T)",
}


class SelectHoldsScreen(QWidget):
    """
    Écran de sélection des prises.

    Permet de cliquer sur les prises du mur et leur assigner
    un type (START, OTHER, FEET, TOP).
    """

    def __init__(
        self,
        controller: WizardController,
        index: HoldClimbIndex,
        parent: Optional[QWidget] = None
    ):
        super().__init__(parent)
        self.controller = controller
        self.index = index

        # Image du mur
        self.image_path = (
            Path(__file__).parent.parent.parent.parent.parent.parent.parent
            / "extracted" / "images" / "face_full_hires.jpg"
        )
        self.img: Optional[Image.Image] = None
        if self.image_path.exists():
            self.img = Image.open(self.image_path).convert('RGB')

        # État local
        self.brightness = 25

        self._setup_ui()
        self._connect_signals()
        self._update_display()

    def _setup_ui(self):
        """Configure l'interface."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Splitter horizontal
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === Panneau gauche : contrôles ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(280)

        # Type de prise actif
        type_label = QLabel("Type de prise")
        type_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(type_label)

        # Radio buttons pour les types
        self.type_group = QButtonGroup(self)
        types_widget = QWidget()
        types_layout = QVBoxLayout(types_widget)
        types_layout.setContentsMargins(0, 0, 0, 0)
        types_layout.setSpacing(2)

        for hold_type in [HoldType.START, HoldType.OTHER, HoldType.FEET, HoldType.TOP]:
            rb = QRadioButton(HOLD_TYPE_LABELS[hold_type])
            rb.setProperty("hold_type", hold_type)
            color = HOLD_TYPE_COLORS[hold_type]
            rb.setStyleSheet(f"color: rgb({color[0]}, {color[1]}, {color[2]});")
            self.type_group.addButton(rb)
            types_layout.addWidget(rb)

            if hold_type == HoldType.OTHER:
                rb.setChecked(True)

        self.type_group.buttonClicked.connect(self._on_type_changed)
        left_layout.addWidget(types_widget)

        # Séparateur
        left_layout.addWidget(self._separator())

        # Luminosité
        brightness_row = QWidget()
        brightness_layout = QHBoxLayout(brightness_row)
        brightness_layout.setContentsMargins(0, 5, 0, 5)
        brightness_layout.addWidget(QLabel("Luminosité:"))

        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(5, 100)
        self.brightness_slider.setValue(self.brightness)
        self.brightness_slider.valueChanged.connect(self._on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)

        self.brightness_label = QLabel(f"{self.brightness}%")
        self.brightness_label.setMinimumWidth(40)
        brightness_layout.addWidget(self.brightness_label)
        left_layout.addWidget(brightness_row)

        # Séparateur
        left_layout.addWidget(self._separator())

        # Liste des prises sélectionnées
        selected_label = QLabel("Prises sélectionnées")
        selected_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(selected_label)

        self.selected_list = QListWidget()
        self.selected_list.setMaximumHeight(200)
        left_layout.addWidget(self.selected_list)

        # Compteurs
        self.counts_label = QLabel()
        self.counts_label.setStyleSheet("color: gray; font-size: 11px;")
        left_layout.addWidget(self.counts_label)

        # Boutons d'action
        btns_widget = QWidget()
        btns_layout = QHBoxLayout(btns_widget)
        btns_layout.setContentsMargins(0, 5, 0, 0)

        self.undo_btn = QPushButton("Annuler")
        self.undo_btn.clicked.connect(self._on_undo)
        self.undo_btn.setEnabled(False)
        btns_layout.addWidget(self.undo_btn)

        self.clear_btn = QPushButton("Effacer tout")
        self.clear_btn.clicked.connect(self._on_clear)
        btns_layout.addWidget(self.clear_btn)

        left_layout.addWidget(btns_widget)

        # Validation
        self.validation_label = QLabel()
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("color: red;")
        left_layout.addWidget(self.validation_label)

        left_layout.addStretch()

        splitter.addWidget(left_panel)

        # === Panneau central : vue du mur ===
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)
        center_layout.setContentsMargins(0, 0, 0, 0)

        # Vue pyqtgraph
        self.view = pg.GraphicsLayoutWidget()
        center_layout.addWidget(self.view)

        self.plot = self.view.addPlot()
        self.plot.setAspectLocked(True)
        self.plot.invertY(True)
        self.plot.hideAxis('left')
        self.plot.hideAxis('bottom')

        # Image de fond
        self.img_item = None
        if self.img:
            self.img_item = pg.ImageItem()
            self.plot.addItem(self.img_item)
            self._update_background()

        # Overlay des prises (mode création)
        self.hold_overlay = CreationHoldOverlay(self.plot, self.index, self.controller)

        splitter.addWidget(center_panel)
        splitter.setSizes([280, 800])

        layout.addWidget(splitter)

    def _separator(self) -> QFrame:
        """Crée un séparateur horizontal."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #ccc;")
        return sep

    def _connect_signals(self):
        """Connecte les signaux."""
        self.controller.state_changed.connect(self._update_display)
        self.hold_overlay.hold_clicked.connect(self._on_hold_clicked)

    def _on_type_changed(self, button):
        """Appelé quand le type de prise change."""
        hold_type = button.property("hold_type")
        if hold_type:
            self.controller.set_selection_type(hold_type)

    def _on_brightness_changed(self, value: int):
        """Appelé quand la luminosité change."""
        self.brightness = value
        self.brightness_label.setText(f"{value}%")
        self._update_background()

    def _on_hold_clicked(self, hold_id: int):
        """Appelé quand une prise est cliquée."""
        state = self.controller.state
        current_type = state.get_hold_type(hold_id)

        if current_type is not None:
            # Prise déjà sélectionnée → désélectionner
            self.controller.remove_hold(hold_id)
        else:
            # Nouvelle prise → ajouter avec le type actif
            self.controller.add_hold(hold_id)

    def _on_undo(self):
        """Annule la dernière sélection."""
        # Trouver la dernière prise ajoutée
        state = self.controller.state
        all_holds = state.get_all_holds()
        if all_holds:
            last_hold = all_holds[-1]
            self.controller.remove_hold(last_hold.hold_id)

    def _on_clear(self):
        """Efface toutes les sélections."""
        state = self.controller.state
        for hold in list(state.get_all_holds()):
            self.controller.remove_hold(hold.hold_id)

    def _update_background(self):
        """Met à jour l'image de fond."""
        if not self.img or not self.img_item:
            return

        # Mélange gris + luminosité
        img_gray = self.img.convert('L').convert('RGB')
        img_blend = Image.blend(self.img, img_gray, 0.85)
        enhancer = ImageEnhance.Brightness(img_blend)
        img_dark = enhancer.enhance(self.brightness / 100.0)
        arr = np.array(img_dark)
        arr = np.transpose(arr, (1, 0, 2))
        self.img_item.setImage(arr, autoLevels=False)

    def _update_display(self):
        """Met à jour l'affichage des prises sélectionnées."""
        state = self.controller.state

        # Mettre à jour l'overlay
        self.hold_overlay.update_selection(state)

        # Mettre à jour la liste
        self.selected_list.clear()
        for hold_sel in state.get_all_holds():
            hold = self.index.holds.get(hold_sel.hold_id)
            if hold:
                label = HOLD_TYPE_LABELS[hold_sel.hold_type]
                item = QListWidgetItem(f"{label[:1]} - Hold #{hold_sel.hold_id}")
                color = HOLD_TYPE_COLORS[hold_sel.hold_type]
                item.setForeground(QColor(*color[:3]))
                self.selected_list.addItem(item)

        # Compteurs
        self.counts_label.setText(
            f"START: {len(state.start_holds)} | "
            f"OTHER: {len(state.other_holds)} | "
            f"FEET: {len(state.feet_holds)} | "
            f"TOP: {len(state.top_holds)}"
        )

        # Validation
        can_proceed, errors = state.can_go_to_info_screen()
        if can_proceed:
            self.validation_label.setText("")
        else:
            self.validation_label.setText("\n".join(errors))

        # Boutons
        self.undo_btn.setEnabled(state.total_holds() > 0)


class CreationHoldOverlay(HoldOverlay):
    """
    Overlay spécialisé pour la création de blocs.

    Affiche les prises avec couleurs par type de sélection
    au lieu de la coloration par niveau.
    """

    def __init__(
        self,
        plot: pg.PlotItem,
        index: HoldClimbIndex,
        controller: WizardController
    ):
        super().__init__(plot, index)
        self.controller = controller

    def update_selection(self, state):
        """Met à jour l'affichage selon l'état de création."""
        # Couleur de base pour toutes les prises (grisé)
        base_color = (100, 100, 100, 60)
        base_pen = pg.mkPen(color=base_color, width=1)
        base_brush = pg.mkBrush(color=(*base_color[:3], 30))

        # Réinitialiser toutes les prises
        for hold_id, item in self.hold_items.items():
            item.setPen(base_pen)
            item.setFillLevel(0)
            item.setBrush(base_brush)

        # Masquer tous les items de sélection
        for hold_id in self.selection_items:
            self.selection_items[hold_id].setVisible(False)
        for hold_id in self.center_items:
            self.center_items[hold_id].setVisible(False)

        # Colorer les prises sélectionnées
        for hold_sel in state.get_all_holds():
            hold_id = hold_sel.hold_id
            hold_type = hold_sel.hold_type

            if hold_id not in self.hold_items:
                continue

            # Couleur selon le type
            color = HOLD_TYPE_COLORS.get(hold_type, (255, 255, 255, 200))
            pen = pg.mkPen(color=color, width=3)
            brush = pg.mkBrush(color=(*color[:3], 100))

            item = self.hold_items[hold_id]
            item.setPen(pen)
            item.setFillLevel(0)
            item.setBrush(brush)

            # Afficher le point central
            self._ensure_selection_items(hold_id)
            if hold_id in self.center_items:
                self.center_items[hold_id].setVisible(True)
                self.center_items[hold_id].setBrush(pg.mkBrush(color[:3]))
                self.center_items[hold_id].setPen(pg.mkPen(color[:3]))
