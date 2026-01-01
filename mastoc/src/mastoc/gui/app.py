"""
Application principale mastoc.

Fenêtre principale combinant liste de climbs, visualisation et synchronisation.
"""

import sys
import logging
from pathlib import Path
from collections import Counter

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QLabel, QSlider, QPushButton, QStatusBar, QMenuBar,
    QMenu, QMessageBox, QProgressDialog, QToolBar, QTabWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PIL import Image, ImageDraw, ImageEnhance
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

from mastoc.api.client import StoktAPI, AuthenticationError
from mastoc.core.backend import (
    BackendSwitch,
    BackendConfig,
    BackendSource,
    MONTOBOARD_GYM_ID,
)
from mastoc.core.config import AppConfig
from mastoc.core.assets import get_asset_manager
from mastoc.db import Database, ClimbRepository, HoldRepository


from mastoc.api.models import Climb, Hold, HoldType
from mastoc.core.sync import SyncManager, RailwaySyncManager
from mastoc.gui.widgets.climb_list import ClimbListWidget
from mastoc.gui.widgets.my_lists_panel import MyListsPanel
from mastoc.gui.dialogs.login import LoginDialog, TokenExpiredDialog
from mastoc.gui.dialogs.sync import SyncDialog
from mastoc.gui.dialogs.sync_status import SyncStatusDialog
from mastoc.gui.dialogs.mastoc_auth import MastocLoginDialog, ProfileDialog
from mastoc.core.auth import AuthManager


# Couleurs pour les types de prises (comme dans l'app Stokt)
HOLD_COLORS = {
    HoldType.START: (0, 255, 0, 200),      # Vert
    HoldType.OTHER: (0, 150, 255, 200),    # Bleu
    HoldType.FEET: (49, 218, 255, 200),    # NEON_BLUE #31DAFF (cyan)
    HoldType.TOP: (255, 0, 0, 200),        # Rouge
}


def get_db_path(source: BackendSource) -> Path:
    """Retourne le chemin de la base SQLite selon la source (ADR-006)."""
    base_dir = Path.home() / ".mastoc"
    if source == BackendSource.RAILWAY:
        return base_dir / "railway.db"
    return base_dir / "stokt.db"


def parse_polygon_points(polygon_str: str) -> list[tuple[float, float]]:
    """Parse polygonStr en liste de tuples."""
    points = []
    for point in polygon_str.split():
        if "," in point:
            x, y = point.split(",")
            points.append((float(x), float(y)))
    return points


def parse_tape_line(tape_str: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """
    Parse un tapeStr en deux points (p1, p2).

    Format: "x1 y1 x2 y2"
    Retourne ((x1, y1), (x2, y2)) ou None si invalide.
    """
    if not tape_str:
        return None
    parts = tape_str.split()
    if len(parts) != 4:
        return None
    try:
        x1, y1, x2, y2 = map(float, parts)
        return ((x1, y1), (x2, y2))
    except ValueError:
        return None


def get_dominant_color(img: Image.Image, centroid: tuple[float, float]) -> tuple[int, int, int]:
    """Trouve la couleur dominante autour du centroïde."""
    cx, cy = int(centroid[0]), int(centroid[1])
    colors = []
    radius = 15

    for dx in range(-radius, radius + 1, 3):
        for dy in range(-radius, radius + 1, 3):
            x, y = cx + dx, cy + dy
            if 0 <= x < img.width and 0 <= y < img.height:
                r, g, b = img.getpixel((x, y))
                max_diff = max(abs(r - g), abs(g - b), abs(r - b))
                if max_diff > 30:
                    colors.append((r // 32 * 32, g // 32 * 32, b // 32 * 32))

    if colors:
        return Counter(colors).most_common(1)[0][0]
    return (200, 200, 200)


def blend_color(color: tuple[int, int, int], white_ratio: float) -> tuple[int, int, int]:
    """Blend entre une couleur et blanc."""
    r, g, b = color
    return (
        int(r + (255 - r) * white_ratio),
        int(g + (255 - g) * white_ratio),
        int(b + (255 - b) * white_ratio)
    )


class ClimbViewerWidget(QWidget):
    """Widget de visualisation d'un climb."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.climb = None
        self.holds_map = {}
        self.img_color = None
        self.hold_colors = {}
        self.img_item = None

        # Paramètres de rendu (valeurs par défaut)
        self.gray_level = 0.70  # 70% gris
        self.brightness_max = 0.66  # 66% luminosité
        self.contour_white = 1.0  # 100% blanc
        self.contour_width = 12  # 12px

        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Info climb
        self.info_label = QLabel("Sélectionnez un climb")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.info_label)

        # GraphicsView
        self.view = pg.GraphicsLayoutWidget()
        layout.addWidget(self.view)

        self.plot = self.view.addPlot()
        self.plot.setAspectLocked(True)
        self.plot.invertY(True)
        self.plot.hideAxis('left')
        self.plot.hideAxis('bottom')

        # Sliders
        self.sliders_widget = QWidget()
        sliders_layout = QVBoxLayout(self.sliders_widget)

        # Slider fond gris
        h1 = QHBoxLayout()
        h1.addWidget(QLabel('Fond (couleur ↔ gris):'))
        self.gray_slider = QSlider(Qt.Orientation.Horizontal)
        self.gray_slider.setRange(0, 100)
        self.gray_slider.setValue(70)
        self.gray_slider.valueChanged.connect(self.on_gray_changed)
        h1.addWidget(self.gray_slider)
        self.gray_label = QLabel('70%')
        self.gray_label.setMinimumWidth(40)
        h1.addWidget(self.gray_label)
        sliders_layout.addLayout(h1)

        # Slider luminosité max (fond foncé)
        h_bright = QHBoxLayout()
        h_bright.addWidget(QLabel('Luminosité max fond:'))
        self.brightness_slider = QSlider(Qt.Orientation.Horizontal)
        self.brightness_slider.setRange(10, 100)  # 10% à 100%
        self.brightness_slider.setValue(66)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        h_bright.addWidget(self.brightness_slider)
        self.brightness_label = QLabel('66%')
        self.brightness_label.setMinimumWidth(40)
        h_bright.addWidget(self.brightness_label)
        sliders_layout.addLayout(h_bright)

        # Slider contour
        h2 = QHBoxLayout()
        h2.addWidget(QLabel('Contour (couleur ↔ blanc):'))
        self.contour_slider = QSlider(Qt.Orientation.Horizontal)
        self.contour_slider.setRange(0, 100)
        self.contour_slider.setValue(100)
        self.contour_slider.valueChanged.connect(self.on_contour_changed)
        h2.addWidget(self.contour_slider)
        self.contour_label = QLabel('100%')
        self.contour_label.setMinimumWidth(40)
        h2.addWidget(self.contour_label)
        sliders_layout.addLayout(h2)

        # Slider épaisseur
        h3 = QHBoxLayout()
        h3.addWidget(QLabel('Épaisseur contour:'))
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, 20)
        self.width_slider.setValue(12)
        self.width_slider.valueChanged.connect(self.on_width_changed)
        h3.addWidget(self.width_slider)
        self.width_label = QLabel('12px')
        self.width_label.setMinimumWidth(40)
        h3.addWidget(self.width_label)
        sliders_layout.addLayout(h3)

        layout.addWidget(self.sliders_widget)
        self.sliders_widget.hide()

    def set_holds_map(self, holds_map: dict[int, Hold]):
        """Définit le mapping des prises."""
        self.holds_map = holds_map

    def set_image(self, image_path: Path):
        """Charge l'image du mur."""
        if image_path and image_path.exists():
            self.img_color = Image.open(image_path).convert('RGB')
            self.sliders_widget.show()
        else:
            self.img_color = None
            self.sliders_widget.hide()

    def show_climb(self, climb: Climb):
        """Affiche un climb."""
        self.climb = climb

        # Mise à jour info
        grade = climb.grade.font if climb.grade else "?"
        setter = climb.setter.full_name if climb.setter else "?"
        self.info_label.setText(f"{climb.name} | {grade} | {setter} | {climb.feet_rule}")

        holds = climb.get_holds()
        logger.debug(f"Affichage climb {climb.name}: {len(holds)} prises")

        # Détecter les couleurs si image disponible
        if self.img_color:
            self.hold_colors.clear()
            for ch in holds:
                hold = self.holds_map.get(ch.hold_id)
                if hold:
                    self.hold_colors[ch.hold_id] = get_dominant_color(self.img_color, hold.centroid)
            self.update_image()
        else:
            self.draw_climb_simple()

    def on_gray_changed(self, value):
        self.gray_level = value / 100.0
        self.gray_label.setText(f'{value}%')
        logger.debug(f"Niveau de gris: {value}%")
        if self.climb:
            self.update_image()

    def on_brightness_changed(self, value):
        self.brightness_max = value / 100.0
        self.brightness_label.setText(f'{value}%')
        logger.debug(f"Luminosité max: {value}%")
        if self.climb:
            self.update_image()

    def on_contour_changed(self, value):
        self.contour_white = value / 100.0
        self.contour_label.setText(f'{value}%')
        if self.climb:
            self.update_image()

    def on_width_changed(self, value):
        self.contour_width = value
        self.width_label.setText(f'{value}px')
        if self.climb:
            self.update_image()

    def update_image(self):
        """Met à jour l'image avec les paramètres actuels."""
        if not self.img_color or not self.climb:
            return

        logger.debug(f"Mise à jour image: gris={self.gray_level}, luminosité={self.brightness_max}")

        img_gray = self.img_color.convert('L').convert('RGB')
        img_blend = Image.blend(self.img_color, img_gray, self.gray_level)

        # Appliquer la luminosité max au fond (foncer l'image)
        if self.brightness_max < 1.0:
            enhancer = ImageEnhance.Brightness(img_blend)
            img_blend = enhancer.enhance(self.brightness_max)

        mask = Image.new('L', self.img_color.size, 0)
        mask_draw = ImageDraw.Draw(mask)

        contours = Image.new('RGBA', self.img_color.size, (0, 0, 0, 0))
        contour_draw = ImageDraw.Draw(contours)

        # Identifier les prises de départ
        climb_holds = self.climb.get_holds()
        start_holds = [ch for ch in climb_holds if ch.hold_type == HoldType.START]

        for ch in climb_holds:
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue
            points = parse_polygon_points(hold.polygon_str)
            if len(points) < 3:
                continue

            mask_draw.polygon(points, fill=255)

            base_color = self.hold_colors.get(ch.hold_id, (200, 200, 200))
            contour_color = blend_color(base_color, self.contour_white)

            # Prise TOP : double contour écarté
            if ch.hold_type == HoldType.TOP:
                contour_draw.polygon(points, outline=(*contour_color, 255), width=self.contour_width)
                # Deuxième contour écarté (dilater les points depuis le centroïde)
                cx, cy = hold.centroid
                scale_factor = 1.35  # 35% plus grand
                expanded_points = [
                    (cx + (px - cx) * scale_factor, cy + (py - cy) * scale_factor)
                    for px, py in points
                ]
                contour_draw.polygon(expanded_points, outline=(*contour_color, 255), width=self.contour_width)
            # Prise FEET : contour NEON_BLUE (#31DAFF)
            elif ch.hold_type == HoldType.FEET:
                # Contour cyan néon pour marquer les pieds obligatoires
                NEON_BLUE = (49, 218, 255, 255)
                contour_draw.polygon(points, outline=NEON_BLUE, width=self.contour_width)
            else:
                contour_draw.polygon(points, outline=(*contour_color, 255), width=self.contour_width)

        # Dessiner les lignes de tape pour les prises de départ
        self._draw_start_tapes(contour_draw, start_holds)

        # Image couleur originale pour les prises (non affectée par luminosité)
        result = Image.composite(self.img_color, img_blend, mask)
        result = result.convert('RGBA')
        result = Image.alpha_composite(result, contours)

        arr = np.array(result)
        arr = np.transpose(arr, (1, 0, 2))

        if self.img_item:
            self.plot.removeItem(self.img_item)
        self.img_item = pg.ImageItem(arr)
        self.plot.addItem(self.img_item)

    def _draw_start_tapes(self, draw: ImageDraw.Draw, start_holds: list):
        """Dessine les lignes de tape pour les prises de départ."""
        for ch in start_holds:
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue

            if len(start_holds) == 1:
                # Une seule prise : deux lignes (V)
                self._draw_tape_line(draw, hold.left_tape_str)
                self._draw_tape_line(draw, hold.right_tape_str)
            else:
                # Plusieurs prises : ligne centrale
                self._draw_tape_line(draw, hold.center_tape_str)

    def _draw_tape_line(self, draw: ImageDraw.Draw, tape_str: str):
        """Dessine une ligne de tape."""
        line = parse_tape_line(tape_str)
        if not line:
            return
        (x1, y1), (x2, y2) = line
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 255), width=self.contour_width)

    def draw_climb_simple(self):
        """Dessine le climb sans image."""
        self.plot.clear()
        if not self.climb:
            return

        climb_holds = self.climb.get_holds()
        start_holds = [ch for ch in climb_holds if ch.hold_type == HoldType.START]

        for ch in climb_holds:
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue

            points = parse_polygon_points(hold.polygon_str)
            if not points:
                continue

            xs = [p[0] for p in points] + [points[0][0]]
            ys = [p[1] for p in points] + [points[0][1]]

            color = HOLD_COLORS.get(ch.hold_type, (128, 128, 128, 200))
            pen = pg.mkPen(color=color, width=3)
            brush = pg.mkBrush(color=(*color[:3], 80))

            polygon = pg.PlotDataItem(xs, ys, pen=pen, fillLevel=0, brush=brush)
            self.plot.addItem(polygon)

            cx, cy = hold.centroid
            scatter = pg.ScatterPlotItem([cx], [cy], size=10, pen=pg.mkPen(color), brush=pg.mkBrush(color))
            self.plot.addItem(scatter)

        # Dessiner les lignes de tape pour les prises de départ
        self._draw_start_tapes_pg(start_holds)

        self.plot.autoRange()

    def _draw_start_tapes_pg(self, start_holds: list):
        """Dessine les lignes de tape avec pyqtgraph."""
        for ch in start_holds:
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue

            if len(start_holds) == 1:
                self._draw_tape_line_pg(hold.left_tape_str)
                self._draw_tape_line_pg(hold.right_tape_str)
            else:
                self._draw_tape_line_pg(hold.center_tape_str)

    def _draw_tape_line_pg(self, tape_str: str):
        """Dessine une ligne de tape avec pyqtgraph."""
        line = parse_tape_line(tape_str)
        if not line:
            return
        (x1, y1), (x2, y2) = line
        item = pg.PlotDataItem(
            [x1, x2], [y1, y2],
            pen=pg.mkPen(color='w', width=4)
        )
        self.plot.addItem(item)


class MastockApp(QMainWindow):
    """Application principale mastoc."""

    def __init__(self):
        super().__init__()

        # Charger la configuration persistante
        self._app_config = AppConfig.load()

        # AuthManager pour l'authentification mastoc (JWT)
        self.auth_manager = AuthManager(
            base_url=self._app_config.railway_url or "https://mastoc-production.up.railway.app"
        )
        self.auth_manager.set_on_auth_change(self._on_auth_changed)

        # Backend avec fallback Stokt → Railway
        self._current_source = BackendSource(self._app_config.source)
        self.backend = BackendSwitch(BackendConfig(
            source=self._current_source,
            railway_api_key=self._app_config.railway_api_key,
            railway_url=self._app_config.railway_url,
            fallback_to_stokt=True,
        ))
        # Alias pour compatibilité (widgets existants)
        if self._current_source == BackendSource.RAILWAY and self.backend.railway:
            self.api = self.backend.railway.api
        else:
            self.api = self.backend.stokt.api if self.backend.stokt else StoktAPI()

        # Base SQLite selon la source (ADR-006)
        self.db = Database(get_db_path(self._current_source))
        # SyncManager selon la source
        if self._current_source == BackendSource.RAILWAY:
            self.sync_manager = RailwaySyncManager(self.api, self.db)
        else:
            self.sync_manager = SyncManager(self.api, self.db)
        self.holds_map = {}

        self.setWindowTitle("mastoc - Climb Viewer")
        self.setMinimumSize(1200, 800)

        self.setup_ui()
        self.setup_menu()
        self.load_data()

    def setup_ui(self):
        """Configure l'interface principale."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)

        # Splitter pour liste / viewer
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Panneau gauche avec onglets
        self.left_tabs = QTabWidget()
        self.left_tabs.setMinimumWidth(350)

        # Onglet Climbs (base de donnees locale)
        self.climb_list = ClimbListWidget(self.db)
        self.climb_list.climb_selected.connect(self.on_climb_selected)
        self.left_tabs.addTab(self.climb_list, "Climbs")

        # Onglet Listes (API, necessite connexion)
        self.lists_panel = MyListsPanel(self.api, MONTOBOARD_GYM_ID, "")
        self.lists_panel.climb_selected.connect(self.on_climb_selected)
        self.left_tabs.addTab(self.lists_panel, "Listes")

        # Rafraichir les listes quand on change d'onglet
        self.left_tabs.currentChanged.connect(self._on_tab_changed)

        splitter.addWidget(self.left_tabs)

        # Viewer (droite)
        self.climb_viewer = ClimbViewerWidget()
        splitter.addWidget(self.climb_viewer)

        splitter.setSizes([400, 800])
        layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Pret")

    def setup_menu(self):
        """Configure la barre de menu."""
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")

        sync_action = QAction("Synchroniser...", self)
        sync_action.triggered.connect(self.sync_data)
        file_menu.addAction(sync_action)

        login_action = QAction("Connexion Stokt...", self)
        login_action.triggered.connect(self.show_login)
        file_menu.addAction(login_action)

        file_menu.addSeparator()

        # Sous-menu Backend
        backend_menu = file_menu.addMenu("Source de données")

        self.stokt_action = QAction("Stokt (sostokt.com)", self)
        self.stokt_action.setCheckable(True)
        self.stokt_action.setChecked(self.backend.source == BackendSource.STOKT)
        self.stokt_action.triggered.connect(lambda: self._set_backend_source(BackendSource.STOKT))
        backend_menu.addAction(self.stokt_action)

        self.railway_action = QAction("Railway (mastoc-api)", self)
        self.railway_action.setCheckable(True)
        self.railway_action.setChecked(self.backend.source == BackendSource.RAILWAY)
        self.railway_action.triggered.connect(lambda: self._set_backend_source(BackendSource.RAILWAY))
        backend_menu.addAction(self.railway_action)

        backend_menu.addSeparator()

        railway_key_action = QAction("Configurer API Key Railway...", self)
        railway_key_action.triggered.connect(self._configure_railway_key)
        backend_menu.addAction(railway_key_action)

        file_menu.addSeparator()

        quit_action = QAction("Quitter", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu Affichage
        view_menu = menubar.addMenu("Affichage")

        refresh_action = QAction("Rafraîchir", self)
        refresh_action.triggered.connect(self.refresh_list)
        view_menu.addAction(refresh_action)

        # Menu Outils
        tools_menu = menubar.addMenu("Outils")

        regen_pictos_action = QAction("Régénérer pictos...", self)
        regen_pictos_action.triggered.connect(self.regenerate_pictos)
        tools_menu.addAction(regen_pictos_action)

        sync_status_action = QAction("État synchronisation...", self)
        sync_status_action.triggered.connect(self.show_sync_status)
        tools_menu.addAction(sync_status_action)

        # Menu Compte
        self.account_menu = menubar.addMenu("Compte")

        self.login_mastoc_action = QAction("Connexion mastoc...", self)
        self.login_mastoc_action.triggered.connect(self.show_mastoc_login)
        self.account_menu.addAction(self.login_mastoc_action)

        self.profile_action = QAction("Mon profil...", self)
        self.profile_action.triggered.connect(self.show_profile)
        self.account_menu.addAction(self.profile_action)

        self.account_menu.addSeparator()

        self.logout_mastoc_action = QAction("Déconnexion", self)
        self.logout_mastoc_action.triggered.connect(self.do_mastoc_logout)
        self.account_menu.addAction(self.logout_mastoc_action)

        # Mettre à jour l'état initial du menu Compte
        self._update_account_menu()

    def _load_face_image(self) -> Path | None:
        """
        Charge l'image du mur depuis le cache d'assets.

        Returns:
            Chemin local de l'image, ou fallback vers le chemin legacy
        """
        legacy_path = Path(__file__).parent.parent.parent.parent.parent / "extracted" / "images" / "face_full_hires.jpg"

        try:
            hold_repo = HoldRepository(self.db)
            picture_path = hold_repo.get_any_face_picture_path()

            if not picture_path:
                logger.warning("Pas de picture_path en DB, utilisation du fallback")
                return legacy_path if legacy_path.exists() else None

            asset_manager = get_asset_manager()
            cached_path = asset_manager.get_face_image(picture_path)

            if cached_path and cached_path.exists():
                logger.info(f"Image chargée depuis cache: {cached_path}")
                return cached_path

            logger.warning("Échec téléchargement image, utilisation du fallback")
            return legacy_path if legacy_path.exists() else None

        except Exception as e:
            logger.error(f"Erreur chargement image: {e}")
            return legacy_path if legacy_path.exists() else None

    def load_data(self):
        """Charge les données depuis la base de données."""
        # Charger les prises
        hold_repo = HoldRepository(self.db)
        holds = hold_repo.get_all_holds()
        self.holds_map = {h.id: h for h in holds}
        self.climb_viewer.set_holds_map(self.holds_map)

        # Charger l'image du mur depuis le cache
        self.image_path = self._load_face_image()
        self.wall_image = None
        if self.image_path and self.image_path.exists():
            self.climb_viewer.set_image(self.image_path)
            self.wall_image = PILImage.open(self.image_path).convert('RGB')

        # Stats pictos
        picto_cache = self.climb_list.get_picto_cache()
        cached_count = picto_cache.get_cached_count()
        logger.info(f"Pictos en cache: {cached_count}")

        # Stats
        status = self.sync_manager.get_sync_status()
        self.statusBar().showMessage(
            f"{status['climb_count']} climbs | {status['hold_count']} prises | {cached_count} pictos"
        )

    def on_climb_selected(self, climb: Climb):
        """Appele quand un climb est selectionne."""
        logger.info(f"Climb selectionne: {climb.name} ({climb.grade.font if climb.grade else '?'})")
        self.climb_viewer.show_climb(climb)
        self.statusBar().showMessage(f"Climb: {climb.name}")

    def _on_tab_changed(self, index: int):
        """Appele quand l'onglet change."""
        # Onglet Listes (index 1)
        if index == 1:
            if not self.api.is_authenticated():
                self.statusBar().showMessage("Connexion requise pour voir les listes")
                QMessageBox.information(
                    self, "Connexion requise",
                    "Connectez-vous pour acceder a vos listes personnalisees."
                )
            elif not self.lists_panel.my_lists and not self.lists_panel.gym_lists:
                # Premier chargement
                self._update_lists_panel_user()
                self.lists_panel.refresh()

    def _update_lists_panel_user(self):
        """Met a jour le user_id du panel listes."""
        # get_user_profile n'existe que sur StoktAPI (pas sur MastocAPI/Railway)
        if not hasattr(self.api, 'get_user_profile'):
            logger.debug("API sans get_user_profile (Railway), skip profil")
            return

        if self.api.is_authenticated():
            try:
                profile = self.api.get_user_profile()
                user_id = profile.get("id", "")
                self.lists_panel.user_id = user_id
                logger.info(f"User ID pour listes: {user_id}")
            except Exception as e:
                logger.error(f"Erreur recuperation profil: {e}")

    def show_login(self):
        """Affiche le dialog de connexion."""
        dialog = LoginDialog(self.api, self)
        if dialog.exec():
            self.statusBar().showMessage("Connecte")
            # Mettre a jour le user_id du panel listes
            self._update_lists_panel_user()

    def sync_data(self):
        """Synchronise les données depuis l'API via le dialog de sync."""
        # Gestion de l'authentification selon la source
        if self._current_source == BackendSource.RAILWAY:
            # Railway utilise une API Key
            if not self.api.is_authenticated():
                reply = QMessageBox.question(
                    self, "API Key requise",
                    "Une API Key Railway est requise pour synchroniser.\n"
                    "Voulez-vous la configurer ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self._configure_railway_key()
                    if not self.api.is_authenticated():
                        return
                else:
                    return
        else:
            # Stokt utilise login/password
            if not self.api.is_authenticated():
                reply = QMessageBox.question(
                    self, "Connexion requise",
                    "Vous devez être connecté pour synchroniser.\nVoulez-vous vous connecter ?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.show_login()
                    if not self.api.is_authenticated():
                        return
                else:
                    return

        # Ouvrir le dialog de synchronisation
        dialog = SyncDialog(self.sync_manager, self.db, self)
        if dialog.exec():
            result = dialog.get_result()
            if result and result.success:
                self.load_data()
                self.refresh_list()

                # Proposer de générer les pictos si nouveaux climbs
                if result.climbs_added > 0:
                    reply = QMessageBox.question(
                        self, "Nouveaux climbs",
                        f"{result.climbs_added} nouveaux climbs ajoutés.\n\n"
                        "Voulez-vous générer les pictos pour les nouveaux blocs ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        self.regenerate_pictos(force=False)

    def refresh_list(self):
        """Rafraîchit la liste des climbs."""
        self.climb_list.refresh()

    def show_sync_status(self):
        """Affiche le dialog d'état de synchronisation."""
        dialog = SyncStatusDialog(self)
        dialog.exec()

    def regenerate_pictos(self, force: bool = True):
        """Régénère tous les pictos."""
        climb_repo = ClimbRepository(self.db)
        all_climbs = climb_repo.get_all_climbs()

        if not all_climbs:
            QMessageBox.information(self, "Info", "Aucun climb dans la base de données.")
            return

        if not self.holds_map:
            QMessageBox.warning(self, "Erreur", "Prises non chargées.")
            return

        # Dialog de progression
        progress = QProgressDialog("Génération des pictos...", "Annuler", 0, len(all_climbs), self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)

        def on_progress(current, total, message):
            progress.setValue(current)
            progress.setLabelText(message)
            QApplication.processEvents()
            if progress.wasCanceled():
                raise InterruptedError("Annulé par l'utilisateur")

        try:
            picto_cache = self.climb_list.get_picto_cache()

            if force:
                picto_cache.clear()

            picto_cache.generate_all(
                all_climbs,
                self.holds_map,
                self.wall_image,
                progress_callback=on_progress,
                force=force
            )

            progress.close()

            # Recharger les icônes
            self.climb_list.clear_icon_cache()
            self.climb_list.refresh()

            # Mettre à jour le status
            cached_count = picto_cache.get_cached_count()
            self.statusBar().showMessage(f"Pictos régénérés: {cached_count}")

            QMessageBox.information(
                self, "Terminé",
                f"{cached_count} pictos générés."
            )

        except InterruptedError:
            progress.close()
            self.statusBar().showMessage("Génération annulée")

        except Exception as e:
            progress.close()
            logger.error(f"Erreur génération pictos: {e}")
            QMessageBox.warning(self, "Erreur", str(e))

    def _set_backend_source(self, source: BackendSource):
        """Change la source de données (ADR-006 : deux bases séparées)."""
        if source == self._current_source:
            return

        self._current_source = source
        self.backend.switch_source(source)

        # Sauvegarder la préférence
        self._app_config.source = source.value
        self._app_config.save()

        # Mettre à jour les checkboxes du menu
        self.stokt_action.setChecked(source == BackendSource.STOKT)
        self.railway_action.setChecked(source == BackendSource.RAILWAY)

        # Mettre à jour l'alias API
        if source == BackendSource.STOKT and self.backend.stokt:
            self.api = self.backend.stokt.api
        elif source == BackendSource.RAILWAY and self.backend.railway:
            self.api = self.backend.railway.api

        # Basculer vers la base SQLite correspondante (ADR-006)
        self.db = Database(get_db_path(source))
        # Utiliser le bon SyncManager selon la source
        if source == BackendSource.RAILWAY:
            self.sync_manager = RailwaySyncManager(self.api, self.db)
        else:
            self.sync_manager = SyncManager(self.api, self.db)
        self.climb_list.set_database(self.db)

        # Mettre à jour le panel listes avec la nouvelle API
        self.lists_panel.api = self.api

        source_name = "Stokt" if source == BackendSource.STOKT else "Railway"
        self.statusBar().showMessage(f"Source: {source_name}")
        logger.info(f"Backend changé vers: {source_name}")

    # =========================================================================
    # Menu Compte (authentification mastoc)
    # =========================================================================

    def _update_account_menu(self):
        """Met à jour le menu Compte selon l'état d'authentification."""
        is_auth = self.auth_manager.is_authenticated
        user = self.auth_manager.current_user

        # Visible si non connecté
        self.login_mastoc_action.setVisible(not is_auth)

        # Visible si connecté
        self.profile_action.setVisible(is_auth)
        self.logout_mastoc_action.setVisible(is_auth)

        # Mettre à jour le titre du menu si connecté
        if is_auth and user:
            self.account_menu.setTitle(f"Compte ({user.full_name})")
        else:
            self.account_menu.setTitle("Compte")

    def _on_auth_changed(self, is_authenticated: bool):
        """Callback appelé quand l'état d'authentification change."""
        self._update_account_menu()

        if is_authenticated:
            user = self.auth_manager.current_user
            if user:
                self.statusBar().showMessage(f"Connecté : {user.full_name}")
                logger.info(f"Utilisateur connecté : {user.email}")
        else:
            self.statusBar().showMessage("Déconnecté")
            logger.info("Utilisateur déconnecté")

    def show_mastoc_login(self):
        """Affiche le dialog de connexion mastoc."""
        dialog = MastocLoginDialog(self.auth_manager, self)
        if dialog.exec():
            self.statusBar().showMessage(f"Connecté : {self.auth_manager.current_user.full_name}")

    def show_profile(self):
        """Affiche le dialog de profil utilisateur."""
        if not self.auth_manager.is_authenticated:
            QMessageBox.warning(self, "Non connecté", "Vous devez être connecté pour accéder à votre profil.")
            return

        dialog = ProfileDialog(self.auth_manager, self)
        dialog.exec()
        # Mettre à jour le menu après fermeture (au cas où déconnexion)
        self._update_account_menu()

    def do_mastoc_logout(self):
        """Déconnexion mastoc."""
        reply = QMessageBox.question(
            self,
            "Déconnexion",
            "Voulez-vous vraiment vous déconnecter ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.auth_manager.logout()

    def _configure_railway_key(self):
        """Configure l'API Key Railway."""
        from PyQt6.QtWidgets import QInputDialog

        current_key = self._app_config.railway_api_key or ""

        key, ok = QInputDialog.getText(
            self,
            "API Key Railway",
            "Entrez votre API Key Railway:",
            text=current_key
        )

        if ok and key:
            self.backend.set_railway_api_key(key)

            # Sauvegarder la clé
            self._app_config.railway_api_key = key
            self._app_config.save()

            self.statusBar().showMessage("API Key Railway configurée et sauvegardée")
            logger.info("API Key Railway configurée et sauvegardée")

            # Proposer de basculer vers Railway
            reply = QMessageBox.question(
                self,
                "Basculer vers Railway?",
                "L'API Key est configurée.\nVoulez-vous basculer vers Railway comme source?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._set_backend_source(BackendSource.RAILWAY)


def main():
    """Point d'entrée de l'application."""
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    logger.info("Démarrage de mastoc")

    app = QApplication(sys.argv)
    app.setApplicationName("mastoc")

    window = MastockApp()
    window.show()
    logger.info("Fenêtre principale affichée")

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
