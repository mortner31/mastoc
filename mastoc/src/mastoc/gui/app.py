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
    QMenu, QMessageBox, QProgressDialog, QToolBar
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
from PIL import Image, ImageDraw, ImageEnhance
from PIL import Image as PILImage

logger = logging.getLogger(__name__)

from mastoc.api.client import StoktAPI, AuthenticationError, MONTOBOARD_GYM_ID
from mastoc.db import Database, ClimbRepository, HoldRepository
from mastoc.api.models import Climb, Hold, HoldType
from mastoc.core.sync import SyncManager
from mastoc.gui.widgets.climb_list import ClimbListWidget
from mastoc.gui.dialogs.login import LoginDialog, TokenExpiredDialog


# Couleurs pour les types de prises (comme dans l'app Stokt)
HOLD_COLORS = {
    HoldType.START: (0, 255, 0, 200),      # Vert
    HoldType.OTHER: (0, 150, 255, 200),    # Bleu
    HoldType.FEET: (49, 218, 255, 200),    # NEON_BLUE #31DAFF (cyan)
    HoldType.TOP: (255, 0, 0, 200),        # Rouge
}


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
        self.db = Database()
        self.api = StoktAPI()
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

        # Liste des climbs (gauche)
        self.climb_list = ClimbListWidget(self.db)
        self.climb_list.climb_selected.connect(self.on_climb_selected)
        self.climb_list.setMinimumWidth(350)
        splitter.addWidget(self.climb_list)

        # Viewer (droite)
        self.climb_viewer = ClimbViewerWidget()
        splitter.addWidget(self.climb_viewer)

        splitter.setSizes([400, 800])
        layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Prêt")

    def setup_menu(self):
        """Configure la barre de menu."""
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")

        sync_action = QAction("Synchroniser...", self)
        sync_action.triggered.connect(self.sync_data)
        file_menu.addAction(sync_action)

        login_action = QAction("Connexion...", self)
        login_action.triggered.connect(self.show_login)
        file_menu.addAction(login_action)

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

    def load_data(self):
        """Charge les données depuis la base de données."""
        # Charger les prises
        hold_repo = HoldRepository(self.db)
        holds = hold_repo.get_all_holds()
        self.holds_map = {h.id: h for h in holds}
        self.climb_viewer.set_holds_map(self.holds_map)

        # Chercher l'image du mur
        self.image_path = Path(__file__).parent.parent.parent.parent.parent / "extracted" / "images" / "face_full_hires.jpg"
        self.wall_image = None
        if self.image_path.exists():
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
        """Appelé quand un climb est sélectionné."""
        logger.info(f"Climb sélectionné: {climb.name} ({climb.grade.font if climb.grade else '?'})")
        self.climb_viewer.show_climb(climb)
        self.statusBar().showMessage(f"Climb: {climb.name}")

    def show_login(self):
        """Affiche le dialog de connexion."""
        dialog = LoginDialog(self.api, self)
        if dialog.exec():
            self.statusBar().showMessage("Connecté")

    def sync_data(self):
        """Synchronise les données depuis l'API."""
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

        # Dialog de progression
        progress = QProgressDialog("Synchronisation...", "Annuler", 0, 100, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)

        def on_progress(current, total, message):
            if total > 0:
                progress.setValue(int(current / total * 100))
            progress.setLabelText(message)
            QApplication.processEvents()

        try:
            result = self.sync_manager.sync_full(callback=on_progress)

            progress.close()

            if result.success:
                self.load_data()
                self.refresh_list()

                # Proposer de générer les pictos si nouveaux climbs
                if result.climbs_added > 0:
                    reply = QMessageBox.question(
                        self, "Synchronisation terminée",
                        f"Climbs ajoutés: {result.climbs_added}\n"
                        f"Prises: {result.holds_added}\n\n"
                        "Voulez-vous générer les pictos pour les nouveaux blocs ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply == QMessageBox.StandardButton.Yes:
                        self.regenerate_pictos(force=False)
                else:
                    QMessageBox.information(
                        self, "Synchronisation terminée",
                        f"Climbs ajoutés: {result.climbs_added}\n"
                        f"Prises: {result.holds_added}"
                    )
            else:
                QMessageBox.warning(
                    self, "Erreur de synchronisation",
                    "\n".join(result.errors)
                )

        except AuthenticationError:
            progress.close()
            dialog = TokenExpiredDialog(self)
            if dialog.show_login_dialog(self.api):
                self.sync_data()

    def refresh_list(self):
        """Rafraîchit la liste des climbs."""
        self.climb_list.refresh()

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
