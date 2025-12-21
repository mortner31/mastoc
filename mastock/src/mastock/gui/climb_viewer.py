"""
Visualisation d'un climb sur le mur.

Script standalone pour afficher un climb avec ses prises colorées.
"""

import sys
from pathlib import Path
from collections import Counter

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QSlider
)
from PyQt6.QtCore import Qt
from PIL import Image, ImageDraw

from mastock.db import Database, ClimbRepository, HoldRepository
from mastock.api.models import Climb, Hold, HoldType


# Couleurs pour les types de prises (mode sans image)
HOLD_COLORS = {
    HoldType.START: (0, 255, 0, 200),    # Vert
    HoldType.OTHER: (0, 150, 255, 200),  # Bleu
    HoldType.FEET: (255, 255, 0, 200),   # Jaune
    HoldType.TOP: (255, 0, 0, 200),      # Rouge
}


def parse_polygon(polygon_str: str) -> tuple[list[float], list[float]]:
    """Parse un polygonStr en listes de coordonnées x, y pour pyqtgraph."""
    xs, ys = [], []
    for point in polygon_str.split():
        if "," in point:
            x, y = point.split(",")
            xs.append(float(x))
            ys.append(float(y))
    # Fermer le polygone
    if xs and ys:
        xs.append(xs[0])
        ys.append(ys[0])
    return xs, ys


def parse_polygon_points(polygon_str: str) -> list[tuple[float, float]]:
    """Parse un polygonStr en liste de tuples (x, y) pour PIL."""
    points = []
    for point in polygon_str.split():
        if "," in point:
            x, y = point.split(",")
            points.append((float(x), float(y)))
    return points


def get_dominant_color(img: Image.Image, centroid: tuple[float, float]) -> tuple[int, int, int]:
    """Trouve la couleur dominante non-grise autour du centroïde."""
    cx, cy = int(centroid[0]), int(centroid[1])
    colors = []
    radius = 15

    for dx in range(-radius, radius + 1, 3):
        for dy in range(-radius, radius + 1, 3):
            x, y = cx + dx, cy + dy
            if 0 <= x < img.width and 0 <= y < img.height:
                r, g, b = img.getpixel((x, y))
                # Filtrer les pixels gris (R ≈ G ≈ B)
                max_diff = max(abs(r - g), abs(g - b), abs(r - b))
                if max_diff > 30:  # Pixel coloré
                    # Quantifier pour regrouper les couleurs similaires
                    colors.append((r // 32 * 32, g // 32 * 32, b // 32 * 32))

    if colors:
        return Counter(colors).most_common(1)[0][0]
    return (200, 200, 200)  # Gris par défaut


def blend_color(color: tuple[int, int, int], white_ratio: float) -> tuple[int, int, int]:
    """Blend entre une couleur et blanc."""
    r, g, b = color
    return (
        int(r + (255 - r) * white_ratio),
        int(g + (255 - g) * white_ratio),
        int(b + (255 - b) * white_ratio)
    )


class ClimbViewerWindow(QMainWindow):
    """Fenêtre de visualisation d'un climb avec contrôles de rendu."""

    def __init__(
        self,
        climb: Climb,
        holds_map: dict[int, Hold],
        image_path: Path = None,
        show_image: bool = False
    ):
        super().__init__()
        self.climb = climb
        self.holds_map = holds_map
        self.image_path = image_path
        self.show_image = show_image

        # Paramètres de rendu
        self.gray_level = 1.0
        self.contour_white = 0.0
        self.contour_width = 5

        # Cache
        self.img_color = None
        self.hold_colors = {}
        self.img_item = None

        self.setWindowTitle(f"Climb: {climb.name}")
        self._load_image_and_colors()
        self.setup_ui()

    def _load_image_and_colors(self):
        """Charge l'image et détecte les couleurs des prises."""
        if not self.show_image or not self.image_path or not self.image_path.exists():
            return

        self.img_color = Image.open(self.image_path).convert('RGB')

        # Détecter les couleurs de chaque prise
        for ch in self.climb.get_holds():
            hold = self.holds_map.get(ch.hold_id)
            if hold:
                self.hold_colors[ch.hold_id] = get_dominant_color(
                    self.img_color, hold.centroid
                )

    def setup_ui(self):
        """Configure l'interface."""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Info du climb
        grade = self.climb.grade.font if self.climb.grade else "?"
        setter = self.climb.setter.full_name if self.climb.setter else "?"
        info = f"{self.climb.name} | {grade} | by {setter} | {self.climb.feet_rule}"
        label = QLabel(info)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Sliders (seulement en mode image)
        if self.show_image and self.img_color:
            self._setup_sliders(layout)

        # GraphicsView pour le mur
        self.view = pg.GraphicsLayoutWidget()
        layout.addWidget(self.view)

        self.plot = self.view.addPlot()
        self.plot.setAspectLocked(True)
        self.plot.invertY(True)

        if self.show_image and self.img_color:
            self.plot.hideAxis('left')
            self.plot.hideAxis('bottom')
            self.update_image()
        else:
            self.draw_climb_holds_simple()
            self.plot.autoRange()

    def _setup_sliders(self, layout):
        """Configure les sliders de contrôle."""
        # Slider fond gris
        h1 = QHBoxLayout()
        h1.addWidget(QLabel('Fond (couleur ↔ gris):'))
        self.gray_slider = QSlider(Qt.Orientation.Horizontal)
        self.gray_slider.setRange(0, 100)
        self.gray_slider.setValue(100)
        self.gray_slider.valueChanged.connect(self.on_gray_changed)
        h1.addWidget(self.gray_slider)
        self.gray_label = QLabel('100%')
        self.gray_label.setMinimumWidth(40)
        h1.addWidget(self.gray_label)
        layout.addLayout(h1)

        # Slider contour couleur/blanc
        h2 = QHBoxLayout()
        h2.addWidget(QLabel('Contour (couleur ↔ blanc):'))
        self.contour_slider = QSlider(Qt.Orientation.Horizontal)
        self.contour_slider.setRange(0, 100)
        self.contour_slider.setValue(0)
        self.contour_slider.valueChanged.connect(self.on_contour_changed)
        h2.addWidget(self.contour_slider)
        self.contour_label = QLabel('0%')
        self.contour_label.setMinimumWidth(40)
        h2.addWidget(self.contour_label)
        layout.addLayout(h2)

        # Slider épaisseur contour
        h3 = QHBoxLayout()
        h3.addWidget(QLabel('Épaisseur contour:'))
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, 20)
        self.width_slider.setValue(5)
        self.width_slider.valueChanged.connect(self.on_width_changed)
        h3.addWidget(self.width_slider)
        self.width_label = QLabel('5px')
        self.width_label.setMinimumWidth(40)
        h3.addWidget(self.width_label)
        layout.addLayout(h3)

    def on_gray_changed(self, value):
        self.gray_level = value / 100.0
        self.gray_label.setText(f'{value}%')
        self.update_image()

    def on_contour_changed(self, value):
        self.contour_white = value / 100.0
        self.contour_label.setText(f'{value}%')
        self.update_image()

    def on_width_changed(self, value):
        self.contour_width = value
        self.width_label.setText(f'{value}px')
        self.update_image()

    def update_image(self):
        """Met à jour l'image avec les paramètres actuels."""
        if not self.img_color:
            return

        # Créer image grise avec niveau ajustable
        img_gray = self.img_color.convert('L').convert('RGB')
        img_blend = Image.blend(self.img_color, img_gray, self.gray_level)

        # Masque des prises (blanc = garder couleur originale)
        mask = Image.new('L', self.img_color.size, 0)
        mask_draw = ImageDraw.Draw(mask)

        # Contours colorés
        contours = Image.new('RGBA', self.img_color.size, (0, 0, 0, 0))
        contour_draw = ImageDraw.Draw(contours)

        for ch in self.climb.get_holds():
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue
            points = parse_polygon_points(hold.polygon_str)
            if len(points) < 3:
                continue

            # Remplir le masque
            mask_draw.polygon(points, fill=255)

            # Couleur du contour (blend entre couleur détectée et blanc)
            base_color = self.hold_colors.get(ch.hold_id, (200, 200, 200))
            contour_color = blend_color(base_color, self.contour_white)
            contour_draw.polygon(points, outline=(*contour_color, 255), width=self.contour_width)

        # Fusionner : couleur sur les prises, gris/blend ailleurs
        result = Image.composite(self.img_color, img_blend, mask)
        result = result.convert('RGBA')
        result = Image.alpha_composite(result, contours)

        # Convertir pour pyqtgraph
        arr = np.array(result)
        arr = np.transpose(arr, (1, 0, 2))

        # Afficher
        if self.img_item:
            self.plot.removeItem(self.img_item)
        self.img_item = pg.ImageItem(arr)
        self.plot.addItem(self.img_item)

    def draw_climb_holds_simple(self):
        """Dessine les prises du climb (mode sans image)."""
        for ch in self.climb.get_holds():
            hold = self.holds_map.get(ch.hold_id)
            if not hold:
                continue

            xs, ys = parse_polygon(hold.polygon_str)
            if not xs:
                continue

            color = HOLD_COLORS.get(ch.hold_type, (128, 128, 128, 200))
            pen = pg.mkPen(color=color, width=3)
            brush = pg.mkBrush(color=(*color[:3], 80))

            polygon = pg.PlotDataItem(xs, ys, pen=pen, fillLevel=0, brush=brush)
            self.plot.addItem(polygon)

            cx, cy = hold.centroid
            scatter = pg.ScatterPlotItem(
                [cx], [cy], size=10, pen=pg.mkPen(color), brush=pg.mkBrush(color)
            )
            self.plot.addItem(scatter)


def show_climb(
    climb_id: str = None,
    climb_name: str = None,
    setter_name: str = None,
    show_image: bool = False
):
    """
    Affiche un climb.

    Args:
        climb_id: ID du climb
        climb_name: Nom du climb (recherche partielle)
        setter_name: Nom du setter (pour filtrer)
        show_image: Afficher l'image du mur avec effet gris
    """
    db = Database()
    climb_repo = ClimbRepository(db)
    hold_repo = HoldRepository(db)

    # Trouver le climb
    climb = None
    if climb_id:
        climb = climb_repo.get_climb(climb_id)
    elif climb_name or setter_name:
        all_climbs = climb_repo.get_all_climbs()
        for c in all_climbs:
            if climb_name and climb_name.lower() in c.name.lower():
                if setter_name:
                    if c.setter and setter_name.lower() in c.setter.full_name.lower():
                        climb = c
                        break
                else:
                    climb = c
                    break
            elif setter_name and c.setter:
                if setter_name.lower() in c.setter.full_name.lower():
                    climb = c
                    break

    if not climb:
        print("Climb non trouvé!")
        return

    print(f"Climb: {climb.name} ({climb.grade.font if climb.grade else '?'})")
    print(f"By: {climb.setter.full_name if climb.setter else '?'}")
    print(f"Holds: {climb.holds_list}")

    # Charger toutes les prises
    holds = hold_repo.get_all_holds()
    holds_map = {h.id: h for h in holds}

    # Chercher l'image du mur
    image_path = Path(__file__).parent.parent.parent.parent.parent / "extracted" / "images" / "face_full_hires.jpg"

    # Afficher
    app = QApplication.instance() or QApplication(sys.argv)
    window = ClimbViewerWindow(climb, holds_map, image_path, show_image=show_image)
    window.resize(900, 1100)
    window.show()

    if not QApplication.instance():
        sys.exit(app.exec())
    else:
        app.exec()


def list_climbs_by_setter(setter_name: str, limit: int = 10):
    """Liste les climbs d'un setter."""
    db = Database()
    repo = ClimbRepository(db)

    all_climbs = repo.get_all_climbs()
    climbs = [c for c in all_climbs if c.setter and setter_name.lower() in c.setter.full_name.lower()]

    print(f"\nClimbs de '{setter_name}' ({len(climbs)} trouvés):\n")
    for c in climbs[:limit]:
        grade = c.grade.font if c.grade else "?"
        print(f"  - {c.name} ({grade}) - {c.feet_rule}")

    if len(climbs) > limit:
        print(f"  ... et {len(climbs) - limit} autres")

    return climbs


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Visualiser un climb")
    parser.add_argument("--id", help="ID du climb")
    parser.add_argument("--name", help="Nom du climb (recherche partielle)")
    parser.add_argument("--setter", help="Nom du setter")
    parser.add_argument("--list", action="store_true", help="Lister les climbs du setter")
    parser.add_argument("--image", action="store_true", help="Afficher l'image du mur avec effet gris")
    args = parser.parse_args()

    if args.list and args.setter:
        list_climbs_by_setter(args.setter)
    elif args.id or args.name or args.setter:
        show_climb(climb_id=args.id, climb_name=args.name, setter_name=args.setter, show_image=args.image)
    else:
        parser.print_help()
