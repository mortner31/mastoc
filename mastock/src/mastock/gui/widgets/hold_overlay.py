"""
Overlay des prises avec coloration par niveau et sélection interactive.
"""

from typing import Optional, Callable
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QColor

from mastock.api.models import Hold
from mastock.core.hold_index import HoldClimbIndex


def parse_polygon_points(polygon_str: str) -> list[tuple[float, float]]:
    """Parse polygonStr en liste de tuples (x, y)."""
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


def interpolate_color(
    min_grade: float,
    max_grade: float,
    grade: float
) -> tuple[int, int, int, int]:
    """
    Interpole une couleur entre vert et rouge selon le grade.

    Vert (facile) → Orange → Rouge (difficile)
    """
    if max_grade <= min_grade:
        ratio = 0.5
    else:
        ratio = (grade - min_grade) / (max_grade - min_grade)
        ratio = max(0, min(1, ratio))

    # Dégradé vert → orange → rouge
    if ratio < 0.5:
        # Vert → Orange
        r = int(255 * (ratio * 2))
        g = 255
        b = 0
    else:
        # Orange → Rouge
        r = 255
        g = int(255 * (1 - (ratio - 0.5) * 2))
        b = 0

    return (r, g, b, 180)


class HoldOverlay(QObject):
    """Overlay des prises avec coloration et sélection."""

    selection_changed = pyqtSignal(list)  # Émet la liste des hold_ids sélectionnés
    hold_clicked = pyqtSignal(int)  # Émet l'ID de la prise cliquée

    def __init__(self, plot: pg.PlotItem, index: HoldClimbIndex):
        super().__init__()
        self.plot = plot
        self.index = index

        # État
        self.selected_holds: set[int] = set()
        self.min_ircra = 0.0
        self.max_ircra = 100.0

        # Items graphiques
        self.hold_items: dict[int, pg.PlotDataItem] = {}
        self.selection_items: dict[int, pg.PlotDataItem] = {}
        self.center_items: dict[int, pg.ScatterPlotItem] = {}
        self.tape_items: list[pg.PlotDataItem] = []  # Lignes de tape pour prises de départ

        # Créer les polygones pour toutes les prises
        self._create_hold_items()

    def _create_hold_items(self):
        """Crée les items graphiques pour toutes les prises."""
        for hold_id, hold in self.index.holds.items():
            points = parse_polygon_points(hold.polygon_str)
            if len(points) < 3:
                continue

            xs = [p[0] for p in points] + [points[0][0]]
            ys = [p[1] for p in points] + [points[0][1]]

            # Polygone principal
            item = pg.PlotDataItem(xs, ys)
            item.hold_id = hold_id  # Stocker l'ID pour le click
            self.hold_items[hold_id] = item
            self.plot.addItem(item)

            # Bordure de sélection (invisible par défaut)
            select_item = pg.PlotDataItem(xs, ys, pen=pg.mkPen(color='w', width=4))
            select_item.setVisible(False)
            self.selection_items[hold_id] = select_item
            self.plot.addItem(select_item)

            # Point central (invisible par défaut)
            cx, cy = hold.centroid
            center = pg.ScatterPlotItem([cx], [cy], size=8)
            center.setVisible(False)
            self.center_items[hold_id] = center
            self.plot.addItem(center)

        # Connecter les clicks
        self.plot.scene().sigMouseClicked.connect(self._on_mouse_clicked)

    def update_colors(self, min_ircra: float, max_ircra: float):
        """Met à jour les couleurs selon la plage de niveau."""
        self.min_ircra = min_ircra
        self.max_ircra = max_ircra

        for hold_id, item in self.hold_items.items():
            # Grade du bloc le plus facile pour cette prise
            min_grade = self.index.get_hold_min_grade(hold_id, min_ircra, max_ircra)

            if min_grade is None:
                # Prise hors filtre → grisée
                color = (128, 128, 128, 50)
            else:
                # Interpolation vert → rouge
                color = interpolate_color(min_ircra, max_ircra, min_grade)

            pen = pg.mkPen(color=color, width=2)
            brush = pg.mkBrush(color=(*color[:3], 80))

            item.setPen(pen)
            item.setFillLevel(0)
            item.setBrush(brush)

    def _on_mouse_clicked(self, event):
        """Gère les clicks sur les prises."""
        pos = event.scenePos()
        items = self.plot.scene().items(pos)

        for item in items:
            if hasattr(item, 'getData'):
                # C'est un PlotDataItem, chercher l'ID
                for hold_id, hold_item in self.hold_items.items():
                    if hold_item is item or hold_item.curve is item:
                        self.toggle_selection(hold_id)
                        self.hold_clicked.emit(hold_id)
                        return

    def toggle_selection(self, hold_id: int):
        """Toggle la sélection d'une prise."""
        if hold_id in self.selected_holds:
            self.selected_holds.remove(hold_id)
            self._update_hold_selection(hold_id, False)
        else:
            self.selected_holds.add(hold_id)
            self._update_hold_selection(hold_id, True)

        self.selection_changed.emit(list(self.selected_holds))

    def _update_hold_selection(self, hold_id: int, selected: bool):
        """Met à jour l'affichage de sélection pour une prise."""
        if hold_id in self.selection_items:
            self.selection_items[hold_id].setVisible(selected)
        if hold_id in self.center_items:
            self.center_items[hold_id].setVisible(selected)
            if selected:
                self.center_items[hold_id].setBrush(pg.mkBrush('w'))
                self.center_items[hold_id].setPen(pg.mkPen('w'))

    def clear_selection(self):
        """Efface toutes les sélections."""
        for hold_id in list(self.selected_holds):
            self._update_hold_selection(hold_id, False)
        self.selected_holds.clear()
        self.selection_changed.emit([])

    def get_selected_holds(self) -> list[int]:
        """Retourne les IDs des prises sélectionnées."""
        return list(self.selected_holds)

    def highlight_climb_holds(self, climb_id: str):
        """Met en évidence les prises d'un bloc spécifique."""
        climb = self.index.climbs.get(climb_id)
        if not climb:
            return

        # Réinitialiser toutes les sélections
        for hold_id in self.selection_items:
            self.selection_items[hold_id].setVisible(False)
            self.center_items[hold_id].setVisible(False)

        # Effacer les anciens tapes
        self._clear_tape_lines()

        # Identifier les prises de départ
        from mastock.api.models import HoldType
        climb_holds = climb.get_holds()
        start_holds = [ch for ch in climb_holds if ch.hold_type == HoldType.START]

        # Mettre en évidence les prises du bloc
        for ch in climb_holds:
            if ch.hold_id in self.selection_items:
                self.selection_items[ch.hold_id].setVisible(True)
                # Couleur selon le type (comme dans l'app Stokt)
                colors = {
                    HoldType.START: 'g',           # Vert
                    HoldType.OTHER: 'b',           # Bleu
                    HoldType.FEET: (49, 218, 255), # NEON_BLUE #31DAFF (cyan)
                    HoldType.TOP: 'r',             # Rouge
                }
                color = colors.get(ch.hold_type, 'w')
                self.selection_items[ch.hold_id].setPen(
                    pg.mkPen(color=color, width=5)
                )

        # Dessiner les tapes pour les prises de départ
        self._draw_start_tapes(start_holds)

    def _clear_tape_lines(self):
        """Efface toutes les lignes de tape."""
        for item in self.tape_items:
            self.plot.removeItem(item)
        self.tape_items.clear()

    def _draw_start_tapes(self, start_holds: list):
        """
        Dessine les lignes de tape pour les prises de départ.

        Logique (comme dans l'app Stokt) :
        - 1 prise de départ → 2 lignes (left + right) formant un "V"
        - 2+ prises de départ → 1 ligne centrale par prise
        """
        from mastock.api.models import ClimbHold

        for ch in start_holds:
            hold = self.index.holds.get(ch.hold_id)
            if not hold:
                continue

            if len(start_holds) == 1:
                # Une seule prise : deux lignes (V)
                self._add_tape_line(hold.left_tape_str)
                self._add_tape_line(hold.right_tape_str)
            else:
                # Plusieurs prises : ligne centrale
                self._add_tape_line(hold.center_tape_str)

    def _add_tape_line(self, tape_str: str):
        """Ajoute une ligne de tape au plot."""
        line = parse_tape_line(tape_str)
        if not line:
            return

        (x1, y1), (x2, y2) = line
        item = pg.PlotDataItem(
            [x1, x2], [y1, y2],
            pen=pg.mkPen(color='w', width=4)  # Blanc, épais
        )
        self.tape_items.append(item)
        self.plot.addItem(item)

    def set_visible(self, visible: bool):
        """Affiche ou masque tous les items."""
        for item in self.hold_items.values():
            item.setVisible(visible)
        if not visible:
            for item in self.selection_items.values():
                item.setVisible(False)
            for item in self.center_items.values():
                item.setVisible(False)
            self._clear_tape_lines()
