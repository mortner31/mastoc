"""
Application de sélection de blocs par prises.

Interface interactive pour retrouver un bloc à partir des prises.
"""

import sys
import time
import logging
from pathlib import Path

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QListWidget, QListWidgetItem, QPushButton,
    QFrame, QStatusBar, QSlider, QRadioButton, QButtonGroup, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PIL import Image, ImageEnhance

from mastock.db import Database, HoldRepository
from mastock.core.hold_index import HoldClimbIndex
from mastock.core.colormaps import Colormap, get_colormap_preview, get_colormap_display_name, get_all_colormaps
from mastock.gui.widgets.level_slider import LevelRangeSlider
from mastock.gui.widgets.hold_overlay import HoldOverlay, ColorMode
from mastock.gui.widgets.climb_renderer import render_climb
from mastock.api.models import Climb

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


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
        t0 = time.perf_counter()
        logger.info("Démarrage HoldSelectorApp...")

        t1 = time.perf_counter()
        self.db = Database()
        logger.info(f"  Database: {(time.perf_counter() - t1)*1000:.0f}ms")

        t1 = time.perf_counter()
        self.index = HoldClimbIndex.from_database(self.db)
        logger.info(f"  HoldClimbIndex: {(time.perf_counter() - t1)*1000:.0f}ms ({len(self.index.climbs)} climbs, {len(self.index.holds)} holds)")

        # Charger l'image
        t1 = time.perf_counter()
        # Remonter jusqu'à la racine du projet (5 niveaux depuis gui/)
        self.image_path = Path(__file__).parent.parent.parent.parent.parent / "extracted" / "images" / "face_full_hires.jpg"
        self.img = None
        if self.image_path.exists():
            self.img = Image.open(self.image_path).convert('RGB')
        logger.info(f"  Image: {(time.perf_counter() - t1)*1000:.0f}ms")

        # État
        self.filtered_climbs: list[Climb] = []
        self.selected_holds: list[int] = []
        self.min_ircra = 12.0  # Grade 4 réel
        self.max_ircra = 26.5
        self.brightness = 25  # % luminosité fond (0-100)

        # Mode : "exploration" ou "parcours"
        self.mode = "exploration"
        self.current_climb_index = -1  # Index du bloc courant en mode parcours

        self.setWindowTitle("mastock - Sélection par prises")
        self.setMinimumSize(1400, 900)

        t1 = time.perf_counter()
        logger.info("  setup_ui: début...")
        self.setup_ui()
        logger.info(f"  setup_ui: {(time.perf_counter() - t1)*1000:.0f}ms")

        t1 = time.perf_counter()
        self.update_display()
        logger.info(f"  update_display: {(time.perf_counter() - t1)*1000:.0f}ms")

        logger.info(f"Total démarrage: {(time.perf_counter() - t0)*1000:.0f}ms")

    def setup_ui(self):
        """Configure l'interface."""
        t0 = time.perf_counter()
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

        # Slider de luminosité
        brightness_row = QWidget()
        brightness_layout = QHBoxLayout(brightness_row)
        brightness_layout.setContentsMargins(0, 5, 0, 5)
        brightness_layout.addWidget(QLabel("Luminosité:"))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(5, 100)
        self.brightness_slider.setValue(self.brightness)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)
        self.brightness_label = QLabel(f"{self.brightness}%")
        self.brightness_label.setMinimumWidth(40)
        brightness_layout.addWidget(self.brightness_label)
        left_layout.addWidget(brightness_row)

        # Séparateur
        left_layout.addWidget(self._separator())

        # === Mode de coloration (TODO 08) ===
        mode_label = QLabel("Mode de coloration")
        mode_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(mode_label)

        self.mode_group = QButtonGroup(self)
        mode_widget = QWidget()
        mode_layout = QVBoxLayout(mode_widget)
        mode_layout.setContentsMargins(0, 0, 0, 0)
        mode_layout.setSpacing(2)

        self.radio_min = QRadioButton("Niveau min (accessible dès)")
        self.radio_min.setChecked(True)
        self.mode_group.addButton(self.radio_min, 0)
        mode_layout.addWidget(self.radio_min)

        self.radio_max = QRadioButton("Niveau max (utilisée jusqu'à)")
        self.mode_group.addButton(self.radio_max, 1)
        mode_layout.addWidget(self.radio_max)

        self.radio_freq = QRadioButton("Fréquence (popularité)")
        self.mode_group.addButton(self.radio_freq, 2)
        mode_layout.addWidget(self.radio_freq)

        left_layout.addWidget(mode_widget)
        self.mode_group.idClicked.connect(self.on_color_mode_changed)

        # Palette de couleurs
        palette_row = QWidget()
        palette_layout = QHBoxLayout(palette_row)
        palette_layout.setContentsMargins(0, 5, 0, 0)
        palette_layout.addWidget(QLabel("Palette:"))

        self.palette_combo = QComboBox()
        for cmap in get_all_colormaps():
            self.palette_combo.addItem(get_colormap_display_name(cmap), cmap)
        self.palette_combo.currentIndexChanged.connect(self.on_colormap_changed)
        palette_layout.addWidget(self.palette_combo, stretch=1)
        left_layout.addWidget(palette_row)

        # Aperçu de la palette
        self.palette_preview = QLabel()
        self.palette_preview.setFixedHeight(20)
        self.palette_preview.setStyleSheet("border: 1px solid #666;")
        left_layout.addWidget(self.palette_preview)
        self._update_palette_preview()

        # Séparateur
        left_layout.addWidget(self._separator())

        # Sélection de prises
        selection_label = QLabel("Prises sélectionnées")
        selection_label.setStyleSheet("font-weight: bold;")
        left_layout.addWidget(selection_label)

        self.selection_info = QLabel("Cliquez sur les prises du mur")
        self.selection_info.setStyleSheet("color: gray;")
        left_layout.addWidget(self.selection_info)

        # Boutons de sélection (Undo + Effacer)
        selection_btns = QWidget()
        selection_btns_layout = QHBoxLayout(selection_btns)
        selection_btns_layout.setContentsMargins(0, 0, 0, 0)

        self.undo_btn = QPushButton("↩ Annuler")
        self.undo_btn.clicked.connect(self.undo_last_selection)
        self.undo_btn.setEnabled(False)
        selection_btns_layout.addWidget(self.undo_btn)

        self.clear_btn = QPushButton("Effacer tout")
        self.clear_btn.clicked.connect(self.clear_selection)
        selection_btns_layout.addWidget(self.clear_btn)

        left_layout.addWidget(selection_btns)

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
        self.climb_list.itemClicked.connect(self.on_climb_clicked)
        left_layout.addWidget(self.climb_list, stretch=1)

        # Contrôles mode parcours (masqués par défaut)
        self.parcours_widget = QWidget()
        parcours_layout = QHBoxLayout(self.parcours_widget)
        parcours_layout.setContentsMargins(0, 5, 0, 0)

        self.prev_btn = QPushButton("◀ Préc")
        self.prev_btn.clicked.connect(self.prev_climb)
        parcours_layout.addWidget(self.prev_btn)

        self.back_to_selection_btn = QPushButton("↩ Retour sélection")
        self.back_to_selection_btn.clicked.connect(self.back_to_exploration)
        parcours_layout.addWidget(self.back_to_selection_btn)

        self.next_btn = QPushButton("Suiv ▶")
        self.next_btn.clicked.connect(self.next_climb)
        parcours_layout.addWidget(self.next_btn)

        left_layout.addWidget(self.parcours_widget)
        self.parcours_widget.hide()

        splitter.addWidget(left_panel)
        logger.info(f"    left_panel: {(time.perf_counter() - t0)*1000:.0f}ms")

        # === Panneau central : vue du mur ===
        t1 = time.perf_counter()
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
        self.img_item = None
        if self.img:
            t2 = time.perf_counter()
            self.img_item = pg.ImageItem()
            self.plot.addItem(self.img_item)
            self.update_background_image()
            logger.info(f"    image fond: {(time.perf_counter() - t2)*1000:.0f}ms")

        # Overlay des prises
        t3 = time.perf_counter()
        self.hold_overlay = HoldOverlay(self.plot, self.index)
        self.hold_overlay.selection_changed.connect(self.on_selection_changed)
        logger.info(f"    HoldOverlay: {(time.perf_counter() - t3)*1000:.0f}ms")

        splitter.addWidget(center_panel)

        splitter.setSizes([300, 1100])
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

    def on_brightness_changed(self, value: int):
        """Appelé quand le slider de luminosité change."""
        self.brightness = value
        self.brightness_label.setText(f"{value}%")
        logger.info(f"Brightness changed to {value}%")
        self.update_background_image()

    def on_color_mode_changed(self, button_id: int):
        """Appelé quand le mode de coloration change."""
        modes = [ColorMode.MIN_GRADE, ColorMode.MAX_GRADE, ColorMode.FREQUENCY]
        mode = modes[button_id]
        logger.info(f"Color mode changed to {mode.value}")
        self.hold_overlay.set_color_mode(mode)
        self.update_display()

    def on_colormap_changed(self, index: int):
        """Appelé quand la palette change."""
        cmap = self.palette_combo.currentData()
        if cmap:
            logger.info(f"Colormap changed to {cmap.value}")
            self.hold_overlay.set_colormap(cmap)
            self._update_palette_preview()
            self.update_display()

    def _update_palette_preview(self):
        """Met à jour l'aperçu de la palette sélectionnée."""
        cmap = self.palette_combo.currentData()
        if not cmap:
            cmap = Colormap.VIRIDIS

        # Générer l'aperçu
        width = 300
        height = 16
        colors = get_colormap_preview(cmap, width)

        # Créer l'image
        img = QImage(width, height, QImage.Format.Format_RGB32)
        for x, (r, g, b) in enumerate(colors):
            for y in range(height):
                img.setPixelColor(x, y, Qt.GlobalColor.black)
                img.setPixel(x, y, (255 << 24) | (r << 16) | (g << 8) | b)

        self.palette_preview.setPixmap(QPixmap.fromImage(img))

    def update_background_image(self):
        """Met à jour l'image de fond avec la luminosité actuelle."""
        if not self.img or not self.img_item:
            logger.warning(f"Cannot update background: img={self.img is not None}, img_item={self.img_item is not None}")
            return
        # Mélange couleur/gris + luminosité ajustable
        img_gray = self.img.convert('L').convert('RGB')
        img_blend = Image.blend(self.img, img_gray, 0.85)  # 85% gris
        enhancer = ImageEnhance.Brightness(img_blend)
        img_dark = enhancer.enhance(self.brightness / 100.0)
        arr = np.array(img_dark)
        logger.info(f"Background image updated: brightness={self.brightness}%, mean={arr.mean():.1f}")
        arr = np.transpose(arr, (1, 0, 2))
        self.img_item.setImage(arr, autoLevels=False)
        self.img_item.update()
        self.view.viewport().update()

    def on_selection_changed(self, hold_ids: list[int]):
        """Appelé quand la sélection de prises change."""
        self.selected_holds = hold_ids
        if hold_ids:
            self.selection_info.setText(f"{len(hold_ids)} prise(s) sélectionnée(s)")
            self.undo_btn.setEnabled(True)
        else:
            self.selection_info.setText("Cliquez sur les prises du mur")
            self.undo_btn.setEnabled(False)
        self.update_results()

    def undo_last_selection(self):
        """Annule la dernière sélection de prise."""
        self.hold_overlay.undo_last_selection()

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

        # Collecter les prises et IDs des blocs filtrés
        valid_holds = None
        valid_climb_ids = None
        if self.selected_holds:
            valid_holds = set()
            valid_climb_ids = set()
            for climb in self.filtered_climbs:
                valid_climb_ids.add(climb.id)
                for ch in climb.get_holds():
                    valid_holds.add(ch.hold_id)

        # Mettre à jour les couleurs (double filtre : grade + prises sélectionnées)
        self.hold_overlay.update_colors(
            self.min_ircra, self.max_ircra, valid_holds, valid_climb_ids
        )

        # Mettre à jour la liste
        self.climb_list.clear()
        for climb in self.filtered_climbs:
            item = ClimbListItem(climb)
            self.climb_list.addItem(item)

        self.count_label.setText(f"{len(self.filtered_climbs)} bloc(s)")

    def on_climb_clicked(self, item: ClimbListItem):
        """Appelé quand un bloc est cliqué - passe en mode parcours."""
        if hasattr(item, 'climb'):
            # Trouver l'index du bloc
            for i, climb in enumerate(self.filtered_climbs):
                if climb.id == item.climb.id:
                    self.current_climb_index = i
                    break
            self.enter_parcours_mode()

    def enter_parcours_mode(self):
        """Passe en mode parcours de blocs."""
        self.mode = "parcours"
        self.parcours_widget.show()
        self.show_current_climb()

    def back_to_exploration(self):
        """Retourne au mode exploration."""
        self.mode = "exploration"
        self.current_climb_index = -1
        self.parcours_widget.hide()

        # Restaurer l'image de fond normale
        self.update_background_image()

        # Réafficher l'overlay des prises
        self.hold_overlay.set_visible(True)
        self.hold_overlay.clear_climb_highlight()
        self.hold_overlay.restore_selection_display()

        # Réafficher toutes les prises des blocs filtrés
        self.update_results()
        self.status.showMessage("Mode sélection")

    def show_current_climb(self):
        """Affiche le bloc courant en mode parcours (rendu PIL comme app.py)."""
        if self.current_climb_index < 0 or self.current_climb_index >= len(self.filtered_climbs):
            return

        climb = self.filtered_climbs[self.current_climb_index]

        # Masquer l'overlay des prises (on passe en rendu PIL)
        self.hold_overlay.set_visible(False)

        # Générer le rendu du bloc avec le renderer commun
        if self.img:
            arr = render_climb(
                self.img,
                climb,
                self.index.holds,
                gray_level=0.85,
                brightness=self.brightness / 100.0,
                contour_width=8
            )
            self.img_item.setImage(arr, autoLevels=False)

        # Sélectionner dans la liste
        self.climb_list.setCurrentRow(self.current_climb_index)

        # Mettre à jour le statut
        grade = climb.grade.font if climb.grade else "?"
        self.status.showMessage(
            f"[{self.current_climb_index + 1}/{len(self.filtered_climbs)}] "
            f"{climb.name} ({grade})"
        )

        # Activer/désactiver les boutons
        self.prev_btn.setEnabled(self.current_climb_index > 0)
        self.next_btn.setEnabled(self.current_climb_index < len(self.filtered_climbs) - 1)

    def prev_climb(self):
        """Passe au bloc précédent."""
        if self.current_climb_index > 0:
            self.current_climb_index -= 1
            self.show_current_climb()

    def next_climb(self):
        """Passe au bloc suivant."""
        if self.current_climb_index < len(self.filtered_climbs) - 1:
            self.current_climb_index += 1
            self.show_current_climb()


def main():
    """Point d'entrée de l'application."""
    app = QApplication(sys.argv)
    app.setApplicationName("mastock Hold Selector")

    window = HoldSelectorApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
