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
    QFrame, QStatusBar, QSlider, QRadioButton, QButtonGroup, QComboBox,
    QCheckBox, QScrollArea, QGroupBox, QDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PIL import Image, ImageEnhance

from mastock.db import Database, HoldRepository
from mastock.core.hold_index import HoldClimbIndex
from mastock.core.colormaps import Colormap, get_colormap_preview, get_colormap_display_name, get_all_colormaps
from mastock.core.social_loader import SocialLoader, SocialData
from mastock.gui.widgets.level_slider import LevelRangeSlider
from mastock.gui.widgets.hold_overlay import HoldOverlay, ColorMode
from mastock.gui.widgets.climb_renderer import render_climb
from mastock.gui.widgets.social_panel import SocialPanel
from mastock.api.client import StoktAPI, MONTOBOARD_GYM_ID
from mastock.api.models import Climb
from mastock.gui.creation import CreationWizard

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

        # Filtre setters (TODO 08)
        self.setter_filter_mode = "none"  # "none", "include", "exclude"
        self.filtered_setters: set[str] = set()

        # Mode : "exploration" ou "parcours"
        self.mode = "exploration"
        self.current_climb_index = -1  # Index du bloc courant en mode parcours

        # API et social loader (TODO 07)
        self.api: StoktAPI | None = None
        self.social_loader: SocialLoader | None = None
        self._init_api()

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

    def _init_api(self):
        """Initialise l'API avec le token stocké."""
        # Token stocké dans la documentation (TODO: dialog de login)
        TOKEN = "dba723cbee34ff3cf049b12150a21dc8919c3cf8"
        try:
            self.api = StoktAPI()
            self.api.set_token(TOKEN)
            # Vérifier que le token est valide
            self.api.get_user_profile()
            self.social_loader = SocialLoader(self.api)
            self.social_loader.on_data_loaded = self._on_social_data_loaded
            logger.info("API initialisée avec succès")
        except Exception as e:
            logger.warning(f"API non disponible: {e}")
            self.api = None
            self.social_loader = None

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
        mode_row = QWidget()
        mode_layout = QHBoxLayout(mode_row)
        mode_layout.setContentsMargins(0, 5, 0, 0)
        mode_layout.addWidget(QLabel("Coloration:"))

        self.color_mode_combo = QComboBox()
        self.color_mode_combo.addItem("Niveau min", ColorMode.MIN_GRADE)
        self.color_mode_combo.addItem("Niveau max", ColorMode.MAX_GRADE)
        self.color_mode_combo.addItem("Fréquence", ColorMode.FREQUENCY)
        self.color_mode_combo.addItem("Rareté", ColorMode.RARE)
        self.color_mode_combo.currentIndexChanged.connect(self.on_color_mode_changed)
        mode_layout.addWidget(self.color_mode_combo, stretch=1)
        left_layout.addWidget(mode_row)

        # Palette de couleurs
        palette_row = QWidget()
        palette_layout = QHBoxLayout(palette_row)
        palette_layout.setContentsMargins(0, 2, 0, 0)
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

        # === Filtre par ouvreur (TODO 08) - Compact/dépliable ===
        setter_header = QWidget()
        setter_header_layout = QHBoxLayout(setter_header)
        setter_header_layout.setContentsMargins(0, 0, 0, 0)

        self.setter_toggle_btn = QPushButton("▶ Ouvreurs")
        self.setter_toggle_btn.setStyleSheet("font-weight: bold; text-align: left; border: none;")
        self.setter_toggle_btn.clicked.connect(self.toggle_setter_panel)
        setter_header_layout.addWidget(self.setter_toggle_btn)

        # Mode du filtre (compact)
        self.setter_mode_combo = QComboBox()
        self.setter_mode_combo.addItem("Tous", "none")
        self.setter_mode_combo.addItem("Inclure", "include")
        self.setter_mode_combo.addItem("Exclure", "exclude")
        self.setter_mode_combo.currentIndexChanged.connect(self.on_setter_mode_changed)
        self.setter_mode_combo.setMaximumWidth(90)
        setter_header_layout.addWidget(self.setter_mode_combo)

        left_layout.addWidget(setter_header)

        # Panel dépliable (masqué par défaut)
        self.setter_panel = QWidget()
        setter_panel_layout = QVBoxLayout(self.setter_panel)
        setter_panel_layout.setContentsMargins(0, 0, 0, 0)
        setter_panel_layout.setSpacing(2)

        # Liste des ouvreurs avec checkboxes
        self.setter_scroll = QScrollArea()
        self.setter_scroll.setWidgetResizable(True)
        self.setter_scroll.setMaximumHeight(120)
        self.setter_scroll.setStyleSheet("QScrollArea { border: 1px solid #444; }")

        setter_container = QWidget()
        self.setter_layout = QVBoxLayout(setter_container)
        self.setter_layout.setContentsMargins(4, 4, 4, 4)
        self.setter_layout.setSpacing(2)

        self.setter_checkboxes: dict[str, QCheckBox] = {}
        for name, count in self.index.setters[:20]:  # Top 20 setters
            cb = QCheckBox(f"{name} ({count})")
            cb.stateChanged.connect(self.on_setter_checkbox_changed)
            self.setter_layout.addWidget(cb)
            self.setter_checkboxes[name] = cb

        self.setter_layout.addStretch()
        self.setter_scroll.setWidget(setter_container)
        setter_panel_layout.addWidget(self.setter_scroll)

        # Boutons Tout/Rien
        setter_btns = QWidget()
        setter_btns_layout = QHBoxLayout(setter_btns)
        setter_btns_layout.setContentsMargins(0, 2, 0, 0)

        self.setter_all_btn = QPushButton("Tout")
        self.setter_all_btn.clicked.connect(self.select_all_setters)
        setter_btns_layout.addWidget(self.setter_all_btn)

        self.setter_none_btn = QPushButton("Rien")
        self.setter_none_btn.clicked.connect(self.select_no_setters)
        setter_btns_layout.addWidget(self.setter_none_btn)

        setter_panel_layout.addWidget(setter_btns)

        left_layout.addWidget(self.setter_panel)
        self.setter_panel.hide()  # Masqué par défaut

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

        # Bouton créer un bloc (TODO 10)
        self.create_btn = QPushButton("+ Créer un bloc")
        self.create_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        self.create_btn.clicked.connect(self.open_creation_wizard)
        self.create_btn.setEnabled(self.api is not None)
        left_layout.addWidget(self.create_btn)

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

        # Panel social (TODO 07) - visible en mode parcours
        self.social_panel = SocialPanel()
        self.social_panel.setMaximumHeight(180)
        self.social_panel.hide()
        left_layout.addWidget(self.social_panel)

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

    def on_color_mode_changed(self, index: int):
        """Appelé quand le mode de coloration change."""
        mode = self.color_mode_combo.currentData()
        if mode:
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

    def toggle_setter_panel(self):
        """Affiche/masque le panel des setters."""
        if self.setter_panel.isVisible():
            self.setter_panel.hide()
            self.setter_toggle_btn.setText("▶ Ouvreurs")
        else:
            self.setter_panel.show()
            self.setter_toggle_btn.setText("▼ Ouvreurs")

    def on_setter_mode_changed(self, index: int):
        """Appelé quand le mode de filtre setter change."""
        self.setter_filter_mode = self.setter_mode_combo.currentData()
        logger.info(f"Setter filter mode: {self.setter_filter_mode}")
        self.update_display()

    def on_setter_checkbox_changed(self, state: int):
        """Appelé quand une checkbox setter change."""
        self._update_filtered_setters()
        if self.setter_filter_mode != "none":
            self.update_display()

    def _update_filtered_setters(self):
        """Met à jour le set des setters cochés."""
        self.filtered_setters = set()
        for name, cb in self.setter_checkboxes.items():
            if cb.isChecked():
                self.filtered_setters.add(name)

    def select_all_setters(self):
        """Coche tous les setters."""
        for cb in self.setter_checkboxes.values():
            cb.setChecked(True)

    def select_no_setters(self):
        """Décoche tous les setters."""
        for cb in self.setter_checkboxes.values():
            cb.setChecked(False)

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
        # Préparer les filtres setters
        include_setters = None
        exclude_setters = None
        if self.setter_filter_mode == "include" and self.filtered_setters:
            include_setters = self.filtered_setters
        elif self.setter_filter_mode == "exclude" and self.filtered_setters:
            exclude_setters = self.filtered_setters

        # Filtrer les blocs
        self.filtered_climbs = self.index.get_filtered_climbs(
            hold_ids=self.selected_holds if self.selected_holds else None,
            min_ircra=self.min_ircra,
            max_ircra=self.max_ircra,
            include_setters=include_setters,
            exclude_setters=exclude_setters
        )

        # Trier par grade
        self.filtered_climbs.sort(
            key=lambda c: self.index.climb_grades.get(c.id, 0)
        )

        # Collecter les prises et IDs des blocs filtrés
        # Toujours calculer valid_climb_ids pour les quantiles (mode fréquence)
        valid_holds = None
        valid_climb_ids = set(c.id for c in self.filtered_climbs)

        if self.selected_holds:
            valid_holds = set()
            for climb in self.filtered_climbs:
                for ch in climb.get_holds():
                    valid_holds.add(ch.hold_id)

        # Mettre à jour les couleurs (triple filtre : grade + prises + setters)
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
        # Afficher le panel social si l'API est disponible
        if self.social_loader:
            self.social_panel.show()
        self.show_current_climb()

    def back_to_exploration(self):
        """Retourne au mode exploration."""
        self.mode = "exploration"
        self.current_climb_index = -1
        self.parcours_widget.hide()
        self.social_panel.hide()

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

        # Charger les données sociales (async)
        if self.social_loader:
            self.social_panel.set_loading(True)
            self.social_loader.load(climb.id)

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

    def _on_social_data_loaded(self, data: SocialData):
        """Callback appelé quand les données sociales sont chargées."""
        # Vérifier qu'on est toujours en mode parcours sur le bon climb
        if self.mode != "parcours" or self.current_climb_index < 0:
            return
        current_climb = self.filtered_climbs[self.current_climb_index]
        if data.climb_id == current_climb.id:
            self.social_panel.set_data(data)

    def open_creation_wizard(self):
        """Ouvre le wizard de création de bloc (TODO 10)."""
        if not self.api:
            QMessageBox.warning(
                self,
                "API non disponible",
                "Vous devez être connecté pour créer un bloc."
            )
            return

        # Récupérer le face_id depuis la base de données
        face_id = self._get_face_id()
        if not face_id:
            QMessageBox.warning(
                self,
                "Erreur",
                "Impossible de trouver la face ID."
            )
            return

        # Créer un dialog modal avec le wizard
        dialog = QDialog(self)
        dialog.setWindowTitle("Créer un bloc")
        dialog.setMinimumSize(1200, 800)
        dialog.setModal(True)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)

        # Créer le wizard
        wizard = CreationWizard(
            index=self.index,
            api=self.api,
            face_id=face_id
        )
        wizard.climb_created.connect(lambda id: self._on_climb_created(id, dialog))
        wizard.cancelled.connect(dialog.close)
        layout.addWidget(wizard)

        dialog.exec()

    def _get_face_id(self) -> str:
        """Récupère le face_id depuis la base de données."""
        # Utiliser le premier climb pour trouver la face_id
        if self.index.climbs:
            first_climb = next(iter(self.index.climbs.values()))
            return first_climb.face_id
        return ""

    def _on_climb_created(self, climb_id: str, dialog: QDialog):
        """Appelé quand un bloc a été créé avec succès."""
        logger.info(f"Bloc créé: {climb_id}")
        dialog.close()

        # Rafraîchir la liste des blocs
        QMessageBox.information(
            self,
            "Succès",
            f"Bloc créé avec succès!\n\nID: {climb_id}\n\n"
            "Rafraîchissez l'application pour voir le nouveau bloc."
        )


def main():
    """Point d'entrée de l'application."""
    app = QApplication(sys.argv)
    app.setApplicationName("mastock Hold Selector")

    window = HoldSelectorApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
