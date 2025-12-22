"""
Application de sélection de blocs par prises.

Interface interactive pour retrouver un bloc à partir des prises.
"""

import sys
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QFrame, QStatusBar
)
from PyQt6.QtCore import Qt
from PIL import Image

from mastock.db import Database, HoldRepository
from mastock.core.hold_index import HoldClimbIndex
from mastock.gui.widgets.level_slider import LevelRangeSlider
from mastock.gui.widgets.hold_overlay import HoldOverlay
from mastock.gui.widgets.climb_detail import ClimbDetailWidget
from mastock.api.models import Climb


class ClimbListItem(QListWidgetItem):
    """Item représentant un bloc dans la liste."""

    def __init__(self, climb: Climb):
        self.climb = climb
        grade = climb.grade.font if climb.grade else "?"
        setter = climb.setter.full_name if climb.setter else "?"

        text = f"{climb.name} | {grade} | {setter}"
        super().__init__(text)
        self.setData(Qt.ItemDataRole.UserRole, climb.id)


class HoldSelectorApp(QMainWindow):
    """Application de sélection de blocs par prises."""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.index = HoldClimbIndex.from_database(self.db)

        # Charger l'image
        self.image_path = Path(__file__).parent.parent.parent.parent / "extracted" / "images" / "face_full_hires.jpg"
        self.img = None
        if self.image_path.exists():
            self.img = Image.open(self.image_path).convert('RGB')

        # État
        self.filtered_climbs: list[Climb] = []
        self.selected_holds: list[int] = []
        self.min_ircra = 10.0
        self.max_ircra = 26.0

        self.setWindowTitle("mastock - Sélection par prises")
        self.setMinimumSize(1400, 900)

        self.setup_ui()
        self.update_display()

    def setup_ui(self):
        """Configure l'interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === Panneau gauche : contrôles ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_panel.setMaximumWidth(350)

        # Titre
        title = QLabel("Filtrage par prises")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        left_layout.addWidget(title)

        # Slider de niveau
        self.level_slider = LevelRangeSlider()
        self.level_slider.range_changed.connect(self.on_level_changed)
        left_layout.addWidget(self.level_slider)

        # Séparateur
        left_layout.addWidget(self._separator())

        # Sélection de prises
        selection_label = QLabel("Prises sélectionnées")
        selection_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(selection_label)

        self.selection_info = QLabel("Cliquez sur les prises du mur")
        self.selection_info.setStyleSheet("color: gray;")
        left_layout.addWidget(self.selection_info)

        self.clear_btn = QPushButton("Effacer la sélection")
        self.clear_btn.clicked.connect(self.clear_selection)
        left_layout.addWidget(self.clear_btn)

        # Séparateur
        left_layout.addWidget(self._separator())

        # Résultats
        results_label = QLabel("Blocs correspondants")
        results_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(results_label)

        self.count_label = QLabel("0 blocs")
        self.count_label.setStyleSheet("color: gray;")
        left_layout.addWidget(self.count_label)

        # Liste des blocs
        self.climb_list = QListWidget()
        self.climb_list.itemClicked.connect(self.on_climb_selected)
        self.climb_list.itemDoubleClicked.connect(self.on_climb_double_clicked)
        left_layout.addWidget(self.climb_list, stretch=1)

        splitter.addWidget(left_panel)

        # === Panneau central : vue du mur ===
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)

        self.view = pg.GraphicsLayoutWidget()
        center_layout.addWidget(self.view)

        self.plot = self.view.addPlot()
        self.plot.setAspectLocked(True)
        self.plot.invertY(True)
        self.plot.hideAxis('left')
        self.plot.hideAxis('bottom')

        # Afficher l'image de fond
        if self.img:
            arr = np.array(self.img)
            arr = np.transpose(arr, (1, 0, 2))
            self.img_item = pg.ImageItem(arr)
            self.plot.addItem(self.img_item)

        # Overlay des prises
        self.hold_overlay = HoldOverlay(self.plot, self.index)
        self.hold_overlay.selection_changed.connect(self.on_selection_changed)

        splitter.addWidget(center_panel)

        # === Panneau droit : détail bloc ===
        self.detail_widget = ClimbDetailWidget(
            self.index.holds,
            self.image_path if self.image_path.exists() else None
        )
        self.detail_widget.previous_requested.connect(self.show_previous_climb)
        self.detail_widget.next_requested.connect(self.show_next_climb)
        self.detail_widget.close_requested.connect(self.hide_detail)
        self.detail_widget.setMaximumWidth(500)
        self.detail_widget.hide()

        splitter.addWidget(self.detail_widget)

        splitter.setSizes([300, 800, 0])
        layout.addWidget(splitter)

        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage(
            f"{len(self.index.climbs)} blocs | {len(self.index.holds)} prises"
        )

    def _separator(self) -> QFrame:
        """Crée un séparateur horizontal."""
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #ccc;")
        return sep

    def on_level_changed(self, min_ircra: float, max_ircra: float):
        """Appelé quand la plage de niveau change."""
        self.min_ircra = min_ircra
        self.max_ircra = max_ircra
        self.update_display()

    def on_selection_changed(self, hold_ids: list[int]):
        """Appelé quand la sélection de prises change."""
        self.selected_holds = hold_ids
        if hold_ids:
            self.selection_info.setText(f"{len(hold_ids)} prise(s) sélectionnée(s)")
        else:
            self.selection_info.setText("Cliquez sur les prises du mur")
        self.update_results()

    def clear_selection(self):
        """Efface la sélection de prises."""
        self.hold_overlay.clear_selection()
        self.selection_info.setText("Cliquez sur les prises du mur")

    def update_display(self):
        """Met à jour l'affichage des prises et des résultats."""
        # Mettre à jour les couleurs des prises
        self.hold_overlay.update_colors(self.min_ircra, self.max_ircra)
        self.update_results()

    def update_results(self):
        """Met à jour la liste des blocs filtrés."""
        # Filtrer les blocs
        self.filtered_climbs = self.index.get_filtered_climbs(
            hold_ids=self.selected_holds if self.selected_holds else None,
            min_ircra=self.min_ircra,
            max_ircra=self.max_ircra
        )

        # Trier par grade
        self.filtered_climbs.sort(
            key=lambda c: self.index.climb_grades.get(c.id, 0)
        )

        # Mettre à jour la liste
        self.climb_list.clear()
        for climb in self.filtered_climbs:
            item = ClimbListItem(climb)
            self.climb_list.addItem(item)

        self.count_label.setText(f"{len(self.filtered_climbs)} bloc(s)")

        # Mettre à jour le détail si visible
        if self.detail_widget.isVisible():
            self.detail_widget.set_climb_list(self.filtered_climbs)

    def on_climb_selected(self, item: ClimbListItem):
        """Appelé quand un bloc est sélectionné."""
        if hasattr(item, 'climb'):
            # Mettre en évidence les prises du bloc
            self.hold_overlay.highlight_climb_holds(item.climb.id)
            self.status.showMessage(f"Bloc: {item.climb.name}")

    def on_climb_double_clicked(self, item: ClimbListItem):
        """Appelé quand un bloc est double-cliqué."""
        if hasattr(item, 'climb'):
            self.show_climb_detail(item.climb)

    def show_climb_detail(self, climb: Climb):
        """Affiche le panneau de détail pour un bloc."""
        self.detail_widget.set_climb_list(self.filtered_climbs)
        self.detail_widget.show_climb(climb)
        self.detail_widget.show()

        # Redimensionner le splitter
        sizes = self.centralWidget().findChild(QSplitter).sizes()
        if sizes[2] == 0:
            sizes[1] -= 400
            sizes[2] = 400
            self.centralWidget().findChild(QSplitter).setSizes(sizes)

    def hide_detail(self):
        """Masque le panneau de détail."""
        self.detail_widget.hide()
        # Restaurer la taille du panneau central
        sizes = self.centralWidget().findChild(QSplitter).sizes()
        sizes[1] += sizes[2]
        sizes[2] = 0
        self.centralWidget().findChild(QSplitter).setSizes(sizes)

    def show_previous_climb(self):
        """Affiche le bloc précédent."""
        self.detail_widget.show_previous()

    def show_next_climb(self):
        """Affiche le bloc suivant."""
        self.detail_widget.show_next()


def main():
    """Point d'entrée de l'application."""
    app = QApplication(sys.argv)
    app.setApplicationName("mastock Hold Selector")

    window = HoldSelectorApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
