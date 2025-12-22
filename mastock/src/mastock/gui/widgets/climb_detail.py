"""
Vue détaillée d'un bloc avec navigation Previous/Next.
"""

from pathlib import Path
from collections import Counter

import numpy as np
import pyqtgraph as pg
from typing import Optional
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PIL import Image, ImageDraw

from mastock.api.models import Climb, Hold, HoldType
from mastock.core.social_loader import SocialLoader, SocialData
from mastock.gui.widgets.social_panel import SocialPanel


# Couleurs pour les types de prises (comme dans l'app Stokt)
HOLD_TYPE_COLORS = {
    HoldType.START: (0, 255, 0),       # Vert
    HoldType.OTHER: (0, 150, 255),     # Bleu
    HoldType.FEET: (49, 218, 255),     # NEON_BLUE #31DAFF (cyan)
    HoldType.TOP: (255, 0, 0),         # Rouge
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


class ClimbDetailWidget(QWidget):
    """Widget affichant les détails d'un bloc."""

    previous_requested = pyqtSignal()
    next_requested = pyqtSignal()
    close_requested = pyqtSignal()
    like_toggled = pyqtSignal(str, bool)  # climb_id, is_liked
    bookmark_toggled = pyqtSignal(str, bool)  # climb_id, is_bookmarked

    def __init__(self, holds_map: dict[int, Hold], image_path: Path = None,
                 social_loader: Optional[SocialLoader] = None, parent=None):
        super().__init__(parent)
        self.holds_map = holds_map
        self.image_path = image_path
        self.climb = None
        self.climb_list: list[Climb] = []
        self.current_index = 0

        # Social loader (optionnel)
        self.social_loader = social_loader
        if self.social_loader:
            self.social_loader.on_data_loaded = self._on_social_data_loaded

        self.img_color = None
        if image_path and image_path.exists():
            self.img_color = Image.open(image_path).convert('RGB')

        self.img_item = None

        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface."""
        layout = QVBoxLayout(self)

        # Info du bloc
        info_frame = QFrame()
        info_frame.setFrameShape(QFrame.Shape.Box)
        info_layout = QVBoxLayout(info_frame)

        self.name_label = QLabel("Nom du bloc")
        self.name_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_layout.addWidget(self.name_label)

        details_layout = QHBoxLayout()

        self.grade_label = QLabel("Grade: ?")
        self.grade_label.setStyleSheet("font-size: 14px;")
        details_layout.addWidget(self.grade_label)

        self.setter_label = QLabel("Setter: ?")
        self.setter_label.setStyleSheet("font-size: 14px;")
        details_layout.addWidget(self.setter_label)

        self.feet_label = QLabel("Pieds: ?")
        self.feet_label.setStyleSheet("font-size: 14px;")
        details_layout.addWidget(self.feet_label)

        info_layout.addLayout(details_layout)

        stats_layout = QHBoxLayout()

        self.date_label = QLabel("Créé le: ?")
        self.date_label.setStyleSheet("font-size: 12px; color: gray;")
        stats_layout.addWidget(self.date_label)

        stats_layout.addStretch()

        # Compteurs sociaux (TODO 07)
        self.ascensions_label = QLabel("👤 0")
        self.ascensions_label.setStyleSheet("font-size: 12px;")
        self.ascensions_label.setToolTip("Ascensions")
        stats_layout.addWidget(self.ascensions_label)

        self.likes_label = QLabel("❤ 0")
        self.likes_label.setStyleSheet("font-size: 12px;")
        self.likes_label.setToolTip("Likes")
        stats_layout.addWidget(self.likes_label)

        self.comments_label = QLabel("💬 0")
        self.comments_label.setStyleSheet("font-size: 12px;")
        self.comments_label.setToolTip("Commentaires")
        stats_layout.addWidget(self.comments_label)

        info_layout.addLayout(stats_layout)

        layout.addWidget(info_frame)

        # Vue du mur
        self.view = pg.GraphicsLayoutWidget()
        layout.addWidget(self.view, stretch=1)

        self.plot = self.view.addPlot()
        self.plot.setAspectLocked(True)
        self.plot.invertY(True)
        self.plot.hideAxis('left')
        self.plot.hideAxis('bottom')

        # Légende
        legend_layout = QHBoxLayout()
        for hold_type, color in HOLD_TYPE_COLORS.items():
            lbl = QLabel(f"● {hold_type.name}")
            lbl.setStyleSheet(f"color: rgb{color}; font-weight: bold;")
            legend_layout.addWidget(lbl)
        layout.addLayout(legend_layout)

        # Navigation
        nav_layout = QHBoxLayout()

        self.prev_btn = QPushButton("◀ Previous")
        self.prev_btn.clicked.connect(self.previous_requested.emit)
        nav_layout.addWidget(self.prev_btn)

        self.position_label = QLabel("1 / 1")
        self.position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.position_label)

        self.next_btn = QPushButton("Next ▶")
        self.next_btn.clicked.connect(self.next_requested.emit)
        nav_layout.addWidget(self.next_btn)

        self.close_btn = QPushButton("Fermer")
        self.close_btn.clicked.connect(self.close_requested.emit)
        nav_layout.addWidget(self.close_btn)

        layout.addLayout(nav_layout)

        # Panel social (si loader disponible)
        self.social_panel: Optional[SocialPanel] = None
        if self.social_loader:
            self.social_panel = SocialPanel()
            self.social_panel.like_clicked.connect(self._on_like_clicked)
            self.social_panel.bookmark_clicked.connect(self._on_bookmark_clicked)
            self.social_panel.setMaximumHeight(200)
            layout.addWidget(self.social_panel)

    def set_climb_list(self, climbs: list[Climb]):
        """Définit la liste des blocs pour la navigation."""
        self.climb_list = climbs
        self.current_index = 0
        self.update_navigation()

    def show_climb(self, climb: Climb):
        """Affiche un bloc."""
        self.climb = climb

        # Mettre à jour l'index si dans la liste
        for i, c in enumerate(self.climb_list):
            if c.id == climb.id:
                self.current_index = i
                break

        # Infos
        self.name_label.setText(climb.name)
        self.grade_label.setText(f"Grade: {climb.grade.font if climb.grade else '?'}")
        self.setter_label.setText(f"Setter: {climb.setter.full_name if climb.setter else '?'}")
        self.feet_label.setText(f"Pieds: {climb.feet_rule}")
        self.date_label.setText(f"Créé le: {climb.date_created[:10] if climb.date_created else '?'}")

        # Compteurs sociaux
        self.ascensions_label.setText(f"👤 {climb.climbed_by}")
        self.likes_label.setText(f"❤ {climb.total_likes}")
        self.comments_label.setText(f"💬 {climb.total_comments}")

        # Navigation
        self.update_navigation()

        # Charger les données sociales (async)
        self._load_social_data()

        # Afficher le bloc
        if self.img_color:
            self._render_with_image()
        else:
            self._render_simple()

    def _render_with_image(self):
        """Affiche le bloc avec l'image du mur."""
        if not self.climb or not self.img_color:
            return

        # Créer l'image avec les prises colorées
        img_gray = self.img_color.convert('L').convert('RGB')
        img_blend = Image.blend(self.img_color, img_gray, 0.8)

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

            # Remplir le masque
            mask_draw.polygon(points, fill=255)

            # Couleur du contour selon le type
            color = HOLD_TYPE_COLORS.get(ch.hold_type, (200, 200, 200))
            contour_draw.polygon(points, outline=(*color, 255), width=5)

        # Dessiner les lignes de tape pour les prises de départ
        self._draw_tape_lines_pil(contour_draw, start_holds)

        # Fusionner
        result = Image.composite(self.img_color, img_blend, mask)
        result = result.convert('RGBA')
        result = Image.alpha_composite(result, contours)

        # Afficher
        arr = np.array(result)
        arr = np.transpose(arr, (1, 0, 2))

        if self.img_item:
            self.plot.removeItem(self.img_item)
        self.img_item = pg.ImageItem(arr)
        self.plot.addItem(self.img_item)

    def _draw_tape_lines_pil(self, draw: ImageDraw.Draw, start_holds: list):
        """Dessine les lignes de tape avec PIL."""
        for ch in start_holds:
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue

            if len(start_holds) == 1:
                # Une seule prise : deux lignes (V)
                self._draw_tape_line_pil(draw, hold.left_tape_str)
                self._draw_tape_line_pil(draw, hold.right_tape_str)
            else:
                # Plusieurs prises : ligne centrale
                self._draw_tape_line_pil(draw, hold.center_tape_str)

    def _draw_tape_line_pil(self, draw: ImageDraw.Draw, tape_str: str):
        """Dessine une ligne de tape avec PIL."""
        line = parse_tape_line(tape_str)
        if not line:
            return
        (x1, y1), (x2, y2) = line
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 255), width=4)

    def _render_simple(self):
        """Affiche le bloc sans image (polygones colorés)."""
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

            color = HOLD_TYPE_COLORS.get(ch.hold_type, (128, 128, 128))
            pen = pg.mkPen(color=(*color, 255), width=3)
            brush = pg.mkBrush(color=(*color, 80))

            polygon = pg.PlotDataItem(xs, ys, pen=pen, fillLevel=0, brush=brush)
            self.plot.addItem(polygon)

            # Centre
            cx, cy = hold.centroid
            scatter = pg.ScatterPlotItem(
                [cx], [cy], size=10,
                pen=pg.mkPen(color), brush=pg.mkBrush(color)
            )
            self.plot.addItem(scatter)

        # Dessiner les lignes de tape pour les prises de départ
        self._draw_tape_lines_pg(start_holds)

        self.plot.autoRange()

    def _draw_tape_lines_pg(self, start_holds: list):
        """Dessine les lignes de tape avec pyqtgraph."""
        for ch in start_holds:
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue

            if len(start_holds) == 1:
                # Une seule prise : deux lignes (V)
                self._draw_tape_line_pg(hold.left_tape_str)
                self._draw_tape_line_pg(hold.right_tape_str)
            else:
                # Plusieurs prises : ligne centrale
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

    def update_navigation(self):
        """Met à jour les boutons de navigation."""
        if not self.climb_list:
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)
            self.position_label.setText("0 / 0")
            return

        self.prev_btn.setEnabled(self.current_index > 0)
        self.next_btn.setEnabled(self.current_index < len(self.climb_list) - 1)
        self.position_label.setText(f"{self.current_index + 1} / {len(self.climb_list)}")

    def show_previous(self):
        """Affiche le bloc précédent."""
        if self.current_index > 0:
            self.current_index -= 1
            self.show_climb(self.climb_list[self.current_index])

    def show_next(self):
        """Affiche le bloc suivant."""
        if self.current_index < len(self.climb_list) - 1:
            self.current_index += 1
            self.show_climb(self.climb_list[self.current_index])

    # =========================================================================
    # Données sociales (TODO 07)
    # =========================================================================

    def _load_social_data(self):
        """Charge les données sociales pour le climb actuel."""
        if not self.social_loader or not self.climb:
            return

        if self.social_panel:
            self.social_panel.set_loading(True)

        self.social_loader.load(self.climb.id)

    def _on_social_data_loaded(self, data: SocialData):
        """Callback quand les données sociales sont chargées."""
        if not self.climb or data.climb_id != self.climb.id:
            return

        if self.social_panel:
            self.social_panel.set_data(data)

    def _on_like_clicked(self):
        """Toggle le like sur le climb actuel."""
        if not self.climb:
            return
        # TODO: implémenter l'appel API
        # Pour l'instant, émettre le signal
        self.like_toggled.emit(self.climb.id, True)

    def _on_bookmark_clicked(self):
        """Toggle le bookmark sur le climb actuel."""
        if not self.climb:
            return
        # TODO: implémenter l'appel API
        self.bookmark_toggled.emit(self.climb.id, True)

    def set_social_loader(self, loader: SocialLoader):
        """Configure le loader social après construction."""
        self.social_loader = loader
        self.social_loader.on_data_loaded = self._on_social_data_loaded

        # Ajouter le panel si pas déjà fait
        if not self.social_panel:
            self.social_panel = SocialPanel()
            self.social_panel.like_clicked.connect(self._on_like_clicked)
            self.social_panel.bookmark_clicked.connect(self._on_bookmark_clicked)
            self.social_panel.setMaximumHeight(200)
            self.layout().addWidget(self.social_panel)
