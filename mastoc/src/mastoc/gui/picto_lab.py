"""
Picto Lab - Interface de test pour le rendu des pictogrammes.

Permet d'ajuster en temps réel les paramètres de style des pictos.
"""

import sys
import json
import logging
from pathlib import Path
from dataclasses import replace

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QSlider, QPushButton, QComboBox, QGroupBox, QScrollArea,
    QCheckBox, QSpinBox, QDoubleSpinBox, QSplitter, QListWidget,
    QListWidgetItem, QFrame, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PIL import Image as PILImage

from mastoc.core.picto import (
    PictoStyle, DEFAULT_STYLE, generate_climb_picto, compute_top_holds,
    compute_all_holds_bounds
)
from mastoc.core.backend import BackendSource
from mastoc.db import Database, ClimbRepository, HoldRepository
from mastoc.core.assets import get_asset_manager


def get_db_path(source: BackendSource) -> Path:
    """Retourne le chemin de la base SQLite selon la source."""
    base_dir = Path.home() / ".mastoc"
    if source == BackendSource.RAILWAY:
        return base_dir / "railway.db"
    return base_dir / "stokt.db"

logger = logging.getLogger(__name__)


def pil_to_qpixmap(pil_image: PILImage.Image, size: int = None) -> QPixmap:
    """Convertit une image PIL en QPixmap (supporte RGB et RGBA)."""
    if size:
        pil_image = pil_image.resize((size, size), PILImage.Resampling.LANCZOS)

    if pil_image.mode == 'RGBA':
        data = pil_image.tobytes('raw', 'RGBA')
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_RGBA8888)
    else:
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        data = pil_image.tobytes('raw', 'RGB')
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format.Format_RGB888)

    return QPixmap.fromImage(qimage)


class ColorButton(QPushButton):
    """Bouton affichant une couleur."""

    def __init__(self, color: tuple[int, int, int], parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(30, 30)
        self.update_color(color)

    def update_color(self, color: tuple[int, int, int]):
        self.color = color
        r, g, b = color
        self.setStyleSheet(f"background-color: rgb({r}, {g}, {b}); border: 1px solid #888;")


class PictoLabWindow(QMainWindow):
    """Fenêtre principale du Picto Lab."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Picto Lab - Test de rendu")
        self.setMinimumSize(1000, 700)

        # État
        self.style = PictoStyle()
        self.climbs = []
        self.holds_map = {}
        self.wall_image = None
        self.current_climb = None
        self.top_holds = []
        self.fixed_bounds = None  # Bounding box de toutes les prises
        self.use_fixed_bounds = False  # Activer le cadre fixe

        self.setup_ui()
        self.load_data()
        self.apply_preset("original")

    def setup_ui(self):
        """Configure l'interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Splitter principal
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # === PANNEAU GAUCHE : Liste des climbs ===
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.addWidget(QLabel("Blocs :"))

        self.climb_list = QListWidget()
        self.climb_list.currentRowChanged.connect(self.on_climb_selected)
        left_layout.addWidget(self.climb_list)

        left_panel.setMaximumWidth(250)
        splitter.addWidget(left_panel)

        # === PANNEAU CENTRAL : Aperçu du picto ===
        center_panel = QWidget()
        center_layout = QVBoxLayout(center_panel)

        # Présets
        presets_layout = QHBoxLayout()
        presets_layout.addWidget(QLabel("Présets :"))

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Original (blanc)",
            "Dark mode",
            "Minimaliste",
            "High contrast"
        ])
        self.preset_combo.currentTextChanged.connect(self.on_preset_changed)
        presets_layout.addWidget(self.preset_combo)
        presets_layout.addStretch()
        center_layout.addLayout(presets_layout)

        # Aperçu grand format
        self.picto_label = QLabel()
        self.picto_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picto_label.setMinimumSize(256, 256)
        self.picto_label.setStyleSheet("border: 1px solid #ccc; background: #f0f0f0;")
        center_layout.addWidget(self.picto_label, 1)

        # Ligne de pictos comparatifs
        compare_layout = QHBoxLayout()
        compare_layout.addWidget(QLabel("Tailles :"))
        self.picto_128 = QLabel("128")
        self.picto_128.setFixedSize(128, 128)
        self.picto_128.setStyleSheet("border: 1px solid #888;")
        compare_layout.addWidget(self.picto_128)

        self.picto_64 = QLabel("64")
        self.picto_64.setFixedSize(64, 64)
        self.picto_64.setStyleSheet("border: 1px solid #888;")
        compare_layout.addWidget(self.picto_64)

        self.picto_48 = QLabel("48")
        self.picto_48.setFixedSize(48, 48)
        self.picto_48.setStyleSheet("border: 1px solid #888;")
        compare_layout.addWidget(self.picto_48)

        self.picto_32 = QLabel("32")
        self.picto_32.setFixedSize(32, 32)
        self.picto_32.setStyleSheet("border: 1px solid #888;")
        compare_layout.addWidget(self.picto_32)

        compare_layout.addStretch()
        center_layout.addLayout(compare_layout)

        splitter.addWidget(center_panel)

        # === PANNEAU DROIT : Contrôles ===
        right_panel = QScrollArea()
        right_panel.setWidgetResizable(True)
        right_panel.setMaximumWidth(350)

        controls = QWidget()
        controls_layout = QVBoxLayout(controls)

        # Groupe : Fond
        bg_group = QGroupBox("Fond")
        bg_layout = QVBoxLayout(bg_group)

        # Couleur de fond (slider gris simple pour l'instant)
        bg_color_layout = QHBoxLayout()
        bg_color_layout.addWidget(QLabel("Luminosité :"))
        self.bg_slider = QSlider(Qt.Orientation.Horizontal)
        self.bg_slider.setRange(0, 255)
        self.bg_slider.setValue(255)
        self.bg_slider.valueChanged.connect(self.on_bg_changed)
        bg_color_layout.addWidget(self.bg_slider)
        self.bg_value = QLabel("255")
        self.bg_value.setMinimumWidth(30)
        bg_color_layout.addWidget(self.bg_value)
        bg_layout.addLayout(bg_color_layout)

        # Transparence fond
        self.transparent_cb = QCheckBox("Fond transparent")
        self.transparent_cb.setChecked(False)
        self.transparent_cb.stateChanged.connect(self.on_style_changed)
        bg_layout.addWidget(self.transparent_cb)

        # Opacité des prises
        hold_opacity_layout = QHBoxLayout()
        hold_opacity_layout.addWidget(QLabel("Opacité prises :"))
        self.hold_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.hold_opacity_slider.setRange(0, 100)
        self.hold_opacity_slider.setValue(100)
        self.hold_opacity_slider.valueChanged.connect(self.on_style_changed)
        hold_opacity_layout.addWidget(self.hold_opacity_slider)
        self.hold_opacity_value = QLabel("100%")
        self.hold_opacity_value.setMinimumWidth(40)
        hold_opacity_layout.addWidget(self.hold_opacity_value)
        bg_layout.addLayout(hold_opacity_layout)

        # Opacité du contexte
        ctx_opacity_layout = QHBoxLayout()
        ctx_opacity_layout.addWidget(QLabel("Opacité contexte :"))
        self.ctx_opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.ctx_opacity_slider.setRange(0, 100)
        self.ctx_opacity_slider.setValue(100)
        self.ctx_opacity_slider.valueChanged.connect(self.on_style_changed)
        ctx_opacity_layout.addWidget(self.ctx_opacity_slider)
        self.ctx_opacity_value = QLabel("100%")
        self.ctx_opacity_value.setMinimumWidth(40)
        ctx_opacity_layout.addWidget(self.ctx_opacity_value)
        bg_layout.addLayout(ctx_opacity_layout)

        controls_layout.addWidget(bg_group)

        # Groupe : Cadrage
        frame_group = QGroupBox("Cadrage")
        frame_layout = QVBoxLayout(frame_group)

        self.fixed_bounds_cb = QCheckBox("Cadre fixe (toutes les prises)")
        self.fixed_bounds_cb.setChecked(False)
        self.fixed_bounds_cb.stateChanged.connect(self.on_fixed_bounds_changed)
        frame_layout.addWidget(self.fixed_bounds_cb)

        controls_layout.addWidget(frame_group)

        # Groupe : Prises de contexte
        ctx_group = QGroupBox("Prises de contexte (top holds)")
        ctx_layout = QVBoxLayout(ctx_group)

        # Afficher contexte
        self.show_context_cb = QCheckBox("Afficher")
        self.show_context_cb.setChecked(True)
        self.show_context_cb.stateChanged.connect(self.on_style_changed)
        ctx_layout.addWidget(self.show_context_cb)

        # Nombre de prises
        ctx_count_layout = QHBoxLayout()
        ctx_count_layout.addWidget(QLabel("Nombre :"))
        self.ctx_count_spin = QSpinBox()
        self.ctx_count_spin.setRange(0, 100)
        self.ctx_count_spin.setValue(20)
        self.ctx_count_spin.valueChanged.connect(self.on_context_count_changed)
        ctx_count_layout.addWidget(self.ctx_count_spin)
        ctx_layout.addLayout(ctx_count_layout)

        # Couleur contexte (gris)
        ctx_color_layout = QHBoxLayout()
        ctx_color_layout.addWidget(QLabel("Gris :"))
        self.ctx_gray_slider = QSlider(Qt.Orientation.Horizontal)
        self.ctx_gray_slider.setRange(0, 255)
        self.ctx_gray_slider.setValue(220)
        self.ctx_gray_slider.valueChanged.connect(self.on_style_changed)
        ctx_color_layout.addWidget(self.ctx_gray_slider)
        self.ctx_gray_value = QLabel("220")
        self.ctx_gray_value.setMinimumWidth(30)
        ctx_color_layout.addWidget(self.ctx_gray_value)
        ctx_layout.addLayout(ctx_color_layout)

        # Contexte en polygone
        self.ctx_polygon_cb = QCheckBox("Forme polygonale")
        self.ctx_polygon_cb.setChecked(False)
        self.ctx_polygon_cb.stateChanged.connect(self.on_style_changed)
        ctx_layout.addWidget(self.ctx_polygon_cb)

        # Appliquer la dilatation au contexte
        self.ctx_dilation_cb = QCheckBox("Appliquer dilatation")
        self.ctx_dilation_cb.setChecked(True)
        self.ctx_dilation_cb.stateChanged.connect(self.on_style_changed)
        ctx_layout.addWidget(self.ctx_dilation_cb)

        controls_layout.addWidget(ctx_group)

        # Groupe : Taille des cercles
        size_group = QGroupBox("Taille des cercles")
        size_layout = QVBoxLayout(size_group)

        # Facteur de rayon
        radius_layout = QHBoxLayout()
        radius_layout.addWidget(QLabel("Facteur :"))
        self.radius_slider = QSlider(Qt.Orientation.Horizontal)
        self.radius_slider.setRange(50, 300)  # 0.5x à 3.0x
        self.radius_slider.setValue(100)
        self.radius_slider.valueChanged.connect(self.on_style_changed)
        radius_layout.addWidget(self.radius_slider)
        self.radius_value = QLabel("1.0x")
        self.radius_value.setMinimumWidth(40)
        radius_layout.addWidget(self.radius_value)
        size_layout.addLayout(radius_layout)

        # Rayon minimum (climb)
        min_climb_layout = QHBoxLayout()
        min_climb_layout.addWidget(QLabel("Min (bloc) :"))
        self.min_climb_spin = QDoubleSpinBox()
        self.min_climb_spin.setRange(1, 50)
        self.min_climb_spin.setValue(3.0)
        self.min_climb_spin.setSingleStep(0.5)
        self.min_climb_spin.valueChanged.connect(self.on_style_changed)
        min_climb_layout.addWidget(self.min_climb_spin)
        size_layout.addLayout(min_climb_layout)

        # Rayon maximum (climb)
        max_climb_layout = QHBoxLayout()
        max_climb_layout.addWidget(QLabel("Max (bloc) :"))
        self.max_climb_spin = QDoubleSpinBox()
        self.max_climb_spin.setRange(5, 100)
        self.max_climb_spin.setValue(20.0)
        self.max_climb_spin.setSingleStep(1.0)
        self.max_climb_spin.valueChanged.connect(self.on_style_changed)
        max_climb_layout.addWidget(self.max_climb_spin)
        size_layout.addLayout(max_climb_layout)

        # Rayon minimum (contexte)
        min_ctx_layout = QHBoxLayout()
        min_ctx_layout.addWidget(QLabel("Min (ctx) :"))
        self.min_ctx_spin = QDoubleSpinBox()
        self.min_ctx_spin.setRange(1, 50)
        self.min_ctx_spin.setValue(2.0)
        self.min_ctx_spin.setSingleStep(0.5)
        self.min_ctx_spin.valueChanged.connect(self.on_style_changed)
        min_ctx_layout.addWidget(self.min_ctx_spin)
        size_layout.addLayout(min_ctx_layout)

        # Rayon maximum (contexte)
        max_ctx_layout = QHBoxLayout()
        max_ctx_layout.addWidget(QLabel("Max (ctx) :"))
        self.max_ctx_spin = QDoubleSpinBox()
        self.max_ctx_spin.setRange(5, 100)
        self.max_ctx_spin.setValue(15.0)
        self.max_ctx_spin.setSingleStep(1.0)
        self.max_ctx_spin.valueChanged.connect(self.on_style_changed)
        max_ctx_layout.addWidget(self.max_ctx_spin)
        size_layout.addLayout(max_ctx_layout)

        # Scaling proportionnel
        self.proportional_cb = QCheckBox("Scaling proportionnel (min→max)")
        self.proportional_cb.setChecked(False)
        self.proportional_cb.stateChanged.connect(self.on_style_changed)
        size_layout.addWidget(self.proportional_cb)

        # Ellipses fittées
        self.ellipse_cb = QCheckBox("Ellipses fittées sur polygones")
        self.ellipse_cb.setChecked(False)
        self.ellipse_cb.stateChanged.connect(self.on_style_changed)
        size_layout.addWidget(self.ellipse_cb)

        # Polygones dilatés
        self.polygon_cb = QCheckBox("Forme polygonale")
        self.polygon_cb.setChecked(False)
        self.polygon_cb.stateChanged.connect(self.on_style_changed)
        size_layout.addWidget(self.polygon_cb)

        # Facteur de dilatation
        dilation_layout = QHBoxLayout()
        dilation_layout.addWidget(QLabel("Dilatation :"))
        self.dilation_slider = QSlider(Qt.Orientation.Horizontal)
        self.dilation_slider.setRange(50, 1000)  # 0.5x à 10.0x
        self.dilation_slider.setValue(100)
        self.dilation_slider.valueChanged.connect(self.on_style_changed)
        dilation_layout.addWidget(self.dilation_slider)
        self.dilation_value = QLabel("1.0x")
        self.dilation_value.setMinimumWidth(50)
        dilation_layout.addWidget(self.dilation_value)
        size_layout.addLayout(dilation_layout)

        # Opacité remplissage polygone
        poly_fill_layout = QHBoxLayout()
        poly_fill_layout.addWidget(QLabel("Opacité centre :"))
        self.poly_fill_slider = QSlider(Qt.Orientation.Horizontal)
        self.poly_fill_slider.setRange(0, 100)
        self.poly_fill_slider.setValue(100)
        self.poly_fill_slider.valueChanged.connect(self.on_style_changed)
        poly_fill_layout.addWidget(self.poly_fill_slider)
        self.poly_fill_value = QLabel("100%")
        self.poly_fill_value.setMinimumWidth(40)
        poly_fill_layout.addWidget(self.poly_fill_value)
        size_layout.addLayout(poly_fill_layout)

        # Opacité contour polygone
        poly_outline_layout = QHBoxLayout()
        poly_outline_layout.addWidget(QLabel("Opacité contour :"))
        self.poly_outline_slider = QSlider(Qt.Orientation.Horizontal)
        self.poly_outline_slider.setRange(0, 100)
        self.poly_outline_slider.setValue(100)
        self.poly_outline_slider.valueChanged.connect(self.on_style_changed)
        poly_outline_layout.addWidget(self.poly_outline_slider)
        self.poly_outline_value = QLabel("100%")
        self.poly_outline_value.setMinimumWidth(40)
        poly_outline_layout.addWidget(self.poly_outline_value)
        size_layout.addLayout(poly_outline_layout)

        # Épaisseur contour polygone
        poly_width_layout = QHBoxLayout()
        poly_width_layout.addWidget(QLabel("Épaisseur contour :"))
        self.poly_width_spin = QSpinBox()
        self.poly_width_spin.setRange(0, 20)
        self.poly_width_spin.setValue(2)
        self.poly_width_spin.valueChanged.connect(self.on_style_changed)
        poly_width_layout.addWidget(self.poly_width_spin)
        size_layout.addLayout(poly_width_layout)

        controls_layout.addWidget(size_group)

        # Groupe : Contours
        outline_group = QGroupBox("Contours")
        outline_layout = QVBoxLayout(outline_group)

        # Liseré sur couleurs claires
        self.outline_cb = QCheckBox("Liseré noir sur couleurs claires")
        self.outline_cb.setChecked(True)
        self.outline_cb.stateChanged.connect(self.on_style_changed)
        outline_layout.addWidget(self.outline_cb)

        # Seuil de luminance
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Seuil luminance :"))
        self.threshold_slider = QSlider(Qt.Orientation.Horizontal)
        self.threshold_slider.setRange(0, 255)
        self.threshold_slider.setValue(180)
        self.threshold_slider.valueChanged.connect(self.on_style_changed)
        threshold_layout.addWidget(self.threshold_slider)
        self.threshold_value = QLabel("180")
        self.threshold_value.setMinimumWidth(30)
        threshold_layout.addWidget(self.threshold_value)
        outline_layout.addLayout(threshold_layout)

        controls_layout.addWidget(outline_group)

        # Groupe : Marqueurs spéciaux
        markers_group = QGroupBox("Marqueurs spéciaux")
        markers_layout = QVBoxLayout(markers_group)

        # TOP marker offset
        top_offset_layout = QHBoxLayout()
        top_offset_layout.addWidget(QLabel("TOP offset :"))
        self.top_offset_spin = QDoubleSpinBox()
        self.top_offset_spin.setRange(0, 20)
        self.top_offset_spin.setValue(3.0)
        self.top_offset_spin.setSingleStep(0.5)
        self.top_offset_spin.valueChanged.connect(self.on_style_changed)
        top_offset_layout.addWidget(self.top_offset_spin)
        markers_layout.addLayout(top_offset_layout)

        # TOP marker width
        top_width_layout = QHBoxLayout()
        top_width_layout.addWidget(QLabel("TOP épaisseur :"))
        self.top_width_spin = QSpinBox()
        self.top_width_spin.setRange(0, 10)
        self.top_width_spin.setValue(2)
        self.top_width_spin.valueChanged.connect(self.on_style_changed)
        top_width_layout.addWidget(self.top_width_spin)
        markers_layout.addLayout(top_width_layout)

        # FEET width
        feet_width_layout = QHBoxLayout()
        feet_width_layout.addWidget(QLabel("FEET épaisseur :"))
        self.feet_width_spin = QSpinBox()
        self.feet_width_spin.setRange(0, 10)
        self.feet_width_spin.setValue(2)
        self.feet_width_spin.valueChanged.connect(self.on_style_changed)
        feet_width_layout.addWidget(self.feet_width_spin)
        markers_layout.addLayout(feet_width_layout)

        # Tape width
        tape_width_layout = QHBoxLayout()
        tape_width_layout.addWidget(QLabel("Tape épaisseur :"))
        self.tape_width_spin = QSpinBox()
        self.tape_width_spin.setRange(1, 10)
        self.tape_width_spin.setValue(2)
        self.tape_width_spin.valueChanged.connect(self.on_style_changed)
        tape_width_layout.addWidget(self.tape_width_spin)
        markers_layout.addLayout(tape_width_layout)

        controls_layout.addWidget(markers_group)

        # Groupe : Marge
        margin_group = QGroupBox("Marge")
        margin_layout = QVBoxLayout(margin_group)

        margin_slider_layout = QHBoxLayout()
        margin_slider_layout.addWidget(QLabel("Ratio :"))
        self.margin_slider = QSlider(Qt.Orientation.Horizontal)
        self.margin_slider.setRange(0, 50)  # 0% à 50%
        self.margin_slider.setValue(10)
        self.margin_slider.valueChanged.connect(self.on_style_changed)
        margin_slider_layout.addWidget(self.margin_slider)
        self.margin_value = QLabel("10%")
        self.margin_value.setMinimumWidth(40)
        margin_slider_layout.addWidget(self.margin_value)
        margin_layout.addLayout(margin_slider_layout)

        controls_layout.addWidget(margin_group)

        # Groupe : Configuration
        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout(config_group)

        # Bouton Reset
        reset_btn = QPushButton("Reset (Original)")
        reset_btn.clicked.connect(lambda: self.apply_preset("original"))
        config_layout.addWidget(reset_btn)

        # Boutons Save/Load
        save_load_layout = QHBoxLayout()
        save_btn = QPushButton("Sauvegarder...")
        save_btn.clicked.connect(self.save_config)
        save_load_layout.addWidget(save_btn)

        load_btn = QPushButton("Charger...")
        load_btn.clicked.connect(self.load_config)
        save_load_layout.addWidget(load_btn)
        config_layout.addLayout(save_load_layout)

        controls_layout.addWidget(config_group)

        controls_layout.addStretch()

        right_panel.setWidget(controls)
        splitter.addWidget(right_panel)

        # Proportions du splitter
        splitter.setSizes([200, 500, 300])
        layout.addWidget(splitter)

    def _load_face_image(self, hold_repo: HoldRepository) -> PILImage.Image | None:
        """Charge l'image du mur avec fallback legacy."""
        # Chemin legacy (dossier extracted à la racine du projet)
        legacy_path = Path(__file__).parent.parent.parent.parent.parent / "extracted" / "images" / "face_full_hires.jpg"

        try:
            picture_path = hold_repo.get_any_face_picture_path()

            if not picture_path:
                logger.warning("Pas de picture_path en DB, utilisation du fallback")
                if legacy_path.exists():
                    logger.info(f"Image legacy: {legacy_path}")
                    return PILImage.open(legacy_path).convert('RGB')
                return None

            asset_manager = get_asset_manager()
            cached_path = asset_manager.get_face_image(picture_path)

            if cached_path and cached_path.exists():
                logger.info(f"Image chargée depuis cache: {cached_path}")
                return PILImage.open(cached_path).convert('RGB')

            logger.warning("Échec téléchargement image, utilisation du fallback")
            if legacy_path.exists():
                return PILImage.open(legacy_path).convert('RGB')
            return None

        except Exception as e:
            logger.error(f"Erreur chargement image: {e}")
            if legacy_path.exists():
                return PILImage.open(legacy_path).convert('RGB')
            return None

    def load_data(self):
        """Charge les données depuis la base."""
        # Utiliser la base Railway par défaut
        db_path = get_db_path(BackendSource.RAILWAY)
        if not db_path.exists():
            db_path = get_db_path(BackendSource.STOKT)

        if not db_path.exists():
            logger.warning("Aucune base de données trouvée")
            return

        db = Database(db_path)

        # Charger les prises
        hold_repo = HoldRepository(db)
        holds = hold_repo.get_all_holds()
        self.holds_map = {h.id: h for h in holds}
        logger.info(f"Chargé {len(holds)} prises")

        # Calculer les bounds fixes (toutes les prises)
        self.fixed_bounds = compute_all_holds_bounds(self.holds_map)
        logger.info(f"Fixed bounds: {self.fixed_bounds}")

        # Charger les climbs
        climb_repo = ClimbRepository(db)
        self.climbs = climb_repo.get_all_climbs()
        logger.info(f"Chargé {len(self.climbs)} blocs")

        # Calculer les top holds
        self.top_holds = compute_top_holds(self.climbs, 100)

        # Charger l'image du mur (avec fallback legacy)
        self.wall_image = self._load_face_image(hold_repo)
        if self.wall_image:
            logger.info(f"Image du mur chargée: {self.wall_image.size}")

        # Remplir la liste des climbs
        for climb in self.climbs[:100]:  # Limiter à 100 pour performance
            grade = climb.grade.font if climb.grade else "?"
            item = QListWidgetItem(f"{climb.name} ({grade})")
            item.setData(Qt.ItemDataRole.UserRole, climb)
            self.climb_list.addItem(item)

        # Sélectionner le premier
        if self.climbs:
            self.climb_list.setCurrentRow(0)

    def on_climb_selected(self, row: int):
        """Appelé quand un climb est sélectionné."""
        if row < 0:
            return

        item = self.climb_list.item(row)
        self.current_climb = item.data(Qt.ItemDataRole.UserRole)
        self.update_picto()

    def on_preset_changed(self, text: str):
        """Appelé quand un préset est sélectionné."""
        preset_map = {
            "Original (blanc)": "original",
            "Dark mode": "dark",
            "Minimaliste": "minimal",
            "High contrast": "contrast"
        }
        preset = preset_map.get(text, "original")
        self.apply_preset(preset)

    def apply_preset(self, preset: str):
        """Applique un préset de style."""
        if preset == "original":
            self.style = PictoStyle()
        elif preset == "dark":
            self.style = PictoStyle(
                background_color=(0, 0, 0),
                context_color=(60, 60, 60),
                context_count=40,
                hold_radius_factor=1.2,
                outline_light_holds=False
            )
        elif preset == "minimal":
            self.style = PictoStyle(
                background_color=(245, 245, 245),
                show_context=False,
                hold_radius_factor=0.8,
                outline_light_holds=False
            )
        elif preset == "contrast":
            self.style = PictoStyle(
                background_color=(30, 30, 30),
                context_color=(80, 80, 80),
                context_count=30,
                hold_radius_factor=1.5,
                min_radius_climb=5.0,
                min_radius_context=3.0,
                light_threshold=150
            )

        self.update_controls_from_style()
        self.update_picto()

    def update_controls_from_style(self):
        """Met à jour les contrôles depuis le style actuel."""
        # Bloquer les signaux pendant la mise à jour
        widgets = [
            self.bg_slider, self.transparent_cb, self.hold_opacity_slider,
            self.ctx_opacity_slider, self.fixed_bounds_cb, self.show_context_cb,
            self.ctx_count_spin, self.ctx_gray_slider,
            self.ctx_polygon_cb, self.ctx_dilation_cb,
            self.radius_slider,
            self.min_climb_spin, self.max_climb_spin, self.min_ctx_spin,
            self.max_ctx_spin, self.proportional_cb, self.ellipse_cb,
            self.polygon_cb, self.dilation_slider,
            self.poly_fill_slider, self.poly_outline_slider, self.poly_width_spin,
            self.outline_cb, self.threshold_slider, self.top_offset_spin,
            self.top_width_spin, self.feet_width_spin, self.tape_width_spin,
            self.margin_slider
        ]
        for w in widgets:
            w.blockSignals(True)

        # Mettre à jour les valeurs
        bg = self.style.background_color[0]  # Supposer niveau de gris
        self.bg_slider.setValue(bg)
        self.bg_value.setText(str(bg))

        self.transparent_cb.setChecked(self.style.transparent_background)

        hold_opacity_pct = int(self.style.hold_opacity * 100)
        self.hold_opacity_slider.setValue(hold_opacity_pct)
        self.hold_opacity_value.setText(f"{hold_opacity_pct}%")

        ctx_opacity_pct = int(self.style.context_opacity * 100)
        self.ctx_opacity_slider.setValue(ctx_opacity_pct)
        self.ctx_opacity_value.setText(f"{ctx_opacity_pct}%")

        self.fixed_bounds_cb.setChecked(self.use_fixed_bounds)

        self.show_context_cb.setChecked(self.style.show_context)
        self.ctx_count_spin.setValue(self.style.context_count)
        self.ctx_polygon_cb.setChecked(self.style.context_use_polygon)
        self.ctx_dilation_cb.setChecked(self.style.context_use_dilation)

        ctx_gray = self.style.context_color[0]
        self.ctx_gray_slider.setValue(ctx_gray)
        self.ctx_gray_value.setText(str(ctx_gray))

        self.radius_slider.setValue(int(self.style.hold_radius_factor * 100))
        self.radius_value.setText(f"{self.style.hold_radius_factor:.1f}x")

        self.min_climb_spin.setValue(self.style.min_radius_climb)
        self.max_climb_spin.setValue(self.style.max_radius_climb)
        self.min_ctx_spin.setValue(self.style.min_radius_context)
        self.max_ctx_spin.setValue(self.style.max_radius_context)
        self.proportional_cb.setChecked(self.style.proportional_scaling)
        self.ellipse_cb.setChecked(self.style.use_fitted_ellipse)
        self.polygon_cb.setChecked(self.style.use_polygon_shape)
        self.dilation_slider.setValue(int(self.style.polygon_dilation * 100))
        self.dilation_value.setText(f"{self.style.polygon_dilation:.1f}x")

        poly_fill_pct = int(self.style.polygon_fill_opacity * 100)
        self.poly_fill_slider.setValue(poly_fill_pct)
        self.poly_fill_value.setText(f"{poly_fill_pct}%")

        poly_outline_pct = int(self.style.polygon_outline_opacity * 100)
        self.poly_outline_slider.setValue(poly_outline_pct)
        self.poly_outline_value.setText(f"{poly_outline_pct}%")

        self.poly_width_spin.setValue(self.style.polygon_outline_width)

        self.outline_cb.setChecked(self.style.outline_light_holds)
        self.threshold_slider.setValue(self.style.light_threshold)
        self.threshold_value.setText(str(self.style.light_threshold))

        self.top_offset_spin.setValue(self.style.top_marker_offset)
        self.top_width_spin.setValue(self.style.top_marker_width)
        self.feet_width_spin.setValue(self.style.feet_width)
        self.tape_width_spin.setValue(self.style.tape_width)

        self.margin_slider.setValue(int(self.style.margin_ratio * 100))
        self.margin_value.setText(f"{int(self.style.margin_ratio * 100)}%")

        # Débloquer les signaux
        for w in widgets:
            w.blockSignals(False)

    def on_bg_changed(self, value: int):
        """Appelé quand le fond change."""
        self.bg_value.setText(str(value))
        self.on_style_changed()

    def on_context_count_changed(self, value: int):
        """Appelé quand le nombre de prises de contexte change."""
        # Recalculer les top holds
        self.top_holds = compute_top_holds(self.climbs, value)
        self.on_style_changed()

    def on_style_changed(self):
        """Appelé quand un paramètre de style change."""
        # Mettre à jour les labels
        self.ctx_gray_value.setText(str(self.ctx_gray_slider.value()))
        self.radius_value.setText(f"{self.radius_slider.value() / 100:.1f}x")
        self.threshold_value.setText(str(self.threshold_slider.value()))
        self.margin_value.setText(f"{self.margin_slider.value()}%")
        self.hold_opacity_value.setText(f"{self.hold_opacity_slider.value()}%")
        self.ctx_opacity_value.setText(f"{self.ctx_opacity_slider.value()}%")
        self.dilation_value.setText(f"{self.dilation_slider.value() / 100:.1f}x")
        self.poly_fill_value.setText(f"{self.poly_fill_slider.value()}%")
        self.poly_outline_value.setText(f"{self.poly_outline_slider.value()}%")

        # Reconstruire le style
        bg = self.bg_slider.value()
        ctx_gray = self.ctx_gray_slider.value()

        self.style = PictoStyle(
            background_color=(bg, bg, bg),
            transparent_background=self.transparent_cb.isChecked(),
            hold_opacity=self.hold_opacity_slider.value() / 100.0,
            context_opacity=self.ctx_opacity_slider.value() / 100.0,
            context_color=(ctx_gray, ctx_gray, ctx_gray),
            context_count=self.ctx_count_spin.value(),
            show_context=self.show_context_cb.isChecked(),
            context_use_polygon=self.ctx_polygon_cb.isChecked(),
            context_use_dilation=self.ctx_dilation_cb.isChecked(),
            hold_radius_factor=self.radius_slider.value() / 100.0,
            min_radius_climb=self.min_climb_spin.value(),
            max_radius_climb=self.max_climb_spin.value(),
            min_radius_context=self.min_ctx_spin.value(),
            max_radius_context=self.max_ctx_spin.value(),
            proportional_scaling=self.proportional_cb.isChecked(),
            use_fitted_ellipse=self.ellipse_cb.isChecked(),
            use_polygon_shape=self.polygon_cb.isChecked(),
            polygon_dilation=self.dilation_slider.value() / 100.0,
            polygon_fill_opacity=self.poly_fill_slider.value() / 100.0,
            polygon_outline_opacity=self.poly_outline_slider.value() / 100.0,
            polygon_outline_width=self.poly_width_spin.value(),
            outline_light_holds=self.outline_cb.isChecked(),
            light_threshold=self.threshold_slider.value(),
            top_marker_offset=self.top_offset_spin.value(),
            top_marker_width=self.top_width_spin.value(),
            feet_color=(49, 218, 255),  # NEON_BLUE fixe
            feet_width=self.feet_width_spin.value(),
            tape_width=self.tape_width_spin.value(),
            margin_ratio=self.margin_slider.value() / 100.0
        )

        self.update_picto()

    def on_fixed_bounds_changed(self, state: int):
        """Appelé quand la checkbox cadre fixe change."""
        self.use_fixed_bounds = state == Qt.CheckState.Checked.value
        self.update_picto()

    def update_picto(self):
        """Régénère et affiche le picto."""
        if not self.current_climb or not self.holds_map:
            return

        # Générer le picto en 256px pour l'aperçu principal
        top_holds = self.top_holds[:self.style.context_count] if self.style.show_context else None
        bounds = self.fixed_bounds if self.use_fixed_bounds else None

        picto = generate_climb_picto(
            self.current_climb,
            self.holds_map,
            self.wall_image,
            size=256,
            top_holds=top_holds,
            style=self.style,
            fixed_bounds=bounds
        )

        # Affichage principal
        self.picto_label.setPixmap(pil_to_qpixmap(picto))

        # Générer les différentes tailles
        picto_128 = generate_climb_picto(
            self.current_climb, self.holds_map, self.wall_image,
            size=128, top_holds=top_holds, style=self.style, fixed_bounds=bounds
        )
        self.picto_128.setPixmap(pil_to_qpixmap(picto_128))

        picto_64 = generate_climb_picto(
            self.current_climb, self.holds_map, self.wall_image,
            size=64, top_holds=top_holds, style=self.style, fixed_bounds=bounds
        )
        self.picto_64.setPixmap(pil_to_qpixmap(picto_64))

        # Redimensionner pour 48 et 32 depuis 128
        self.picto_48.setPixmap(pil_to_qpixmap(picto_128, 48))
        self.picto_32.setPixmap(pil_to_qpixmap(picto_128, 32))

    def save_config(self):
        """Sauvegarde la configuration actuelle dans un fichier JSON."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder la configuration",
            str(Path.home() / "picto_style.json"),
            "JSON files (*.json)"
        )
        if not file_path:
            return

        config = {
            "style": self.style.to_dict(),
            "use_fixed_bounds": self.use_fixed_bounds
        }
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info(f"Configuration sauvegardée: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de sauvegarder: {e}")

    def load_config(self):
        """Charge une configuration depuis un fichier JSON."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Charger une configuration",
            str(Path.home()),
            "JSON files (*.json)"
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.style = PictoStyle.from_dict(config.get("style", {}))
            self.use_fixed_bounds = config.get("use_fixed_bounds", False)

            self.update_controls_from_style()
            self.update_picto()
            logger.info(f"Configuration chargée: {file_path}")
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Impossible de charger: {e}")


def main():
    """Point d'entrée."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    app = QApplication(sys.argv)
    window = PictoLabWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
