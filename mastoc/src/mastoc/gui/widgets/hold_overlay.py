"""
Overlay des prises avec coloration par niveau et sélection interactive.

Supporte trois modes de coloration (TODO 08):
- MIN_GRADE: Niveau du bloc le plus facile (défaut)
- MAX_GRADE: Niveau du bloc le plus difficile
- FREQUENCY: Fréquence d'utilisation (quantiles)
"""

from enum import Enum
from typing import Optional, Callable
import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtGui import QColor

from mastoc.api.models import Hold, HoldGripType, HoldCondition, HoldRelativeDifficulty, AnnotationData
from mastoc.core.hold_index import HoldClimbIndex
from mastoc.core.colormaps import Colormap, apply_colormap


# Mapping des enums vers des valeurs normalisées [0, 1] pour les colormaps
GRIP_TYPE_VALUES = {
    HoldGripType.BAC: 0.0,         # Facile (vert)
    HoldGripType.PRISE_VOLUME: 0.08,
    HoldGripType.PLAT: 0.17,
    HoldGripType.PINCE: 0.25,
    HoldGripType.COLONNETTE: 0.33,
    HoldGripType.INVERSE: 0.42,
    HoldGripType.REGLETTE: 0.50,   # Moyen (jaune)
    HoldGripType.TRI_DOIGT: 0.58,
    HoldGripType.BI_DOIGT: 0.67,
    HoldGripType.MONO_DOIGT: 0.75,
    HoldGripType.MICRO: 0.92,
    HoldGripType.AUTRE: 1.0,       # Difficile (rouge)
}

CONDITION_VALUES = {
    HoldCondition.OK: 0.0,         # Bon (vert)
    HoldCondition.A_BROSSER: 0.2,
    HoldCondition.SALE: 0.4,
    HoldCondition.TOURNEE: 0.6,
    HoldCondition.USEE: 0.8,
    HoldCondition.CASSEE: 1.0,     # Mauvais (rouge)
}

DIFFICULTY_VALUES = {
    HoldRelativeDifficulty.FACILE: 0.0,   # Vert
    HoldRelativeDifficulty.NORMALE: 0.5,  # Jaune
    HoldRelativeDifficulty.DURE: 1.0,     # Rouge
}


class ColorMode(Enum):
    """Mode de coloration des prises."""
    MIN_GRADE = "min"    # Grade du bloc le plus facile
    MAX_GRADE = "max"    # Grade du bloc le plus difficile
    FREQUENCY = "freq"   # Fréquence d'utilisation (quantiles)
    RARE = "rare"        # Prises rares (0, 1, 2, 3+ utilisations)
    # Modes annotations (ADR-008)
    GRIP_TYPE = "grip"   # Couleur par type de préhension
    CONDITION = "condition"  # Couleur par état de maintenance
    DIFFICULTY = "difficulty"  # Couleur par difficulté relative


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

        # État - liste pour garder l'ordre de sélection (undo)
        self.selected_holds: list[int] = []
        self.min_ircra = 0.0
        self.max_ircra = 100.0

        # Mode de coloration et palette (TODO 08)
        self.color_mode = ColorMode.MIN_GRADE
        self.colormap = Colormap.VIRIDIS

        # Cache des quantiles pour le mode fréquence
        self._frequency_cache: dict[int, float] = {}

        # Cache du comptage pour le mode rare
        self._usage_count_cache: dict[int, int] = {}

        # Cache des annotations (ADR-008)
        self._annotation_cache: dict[int, AnnotationData] = {}

        # Items graphiques
        self.hold_items: dict[int, pg.PlotDataItem] = {}
        self.selection_items: dict[int, pg.PlotDataItem] = {}
        self.center_items: dict[int, pg.ScatterPlotItem] = {}
        self.tape_items: list[pg.PlotDataItem] = []  # Lignes de tape pour prises de départ
        self.extra_contours: list[pg.PlotDataItem] = []  # Contours supplémentaires (TOP)

        # Créer les polygones pour toutes les prises
        self._create_hold_items()

    def _create_hold_items(self):
        """Crée les items graphiques pour toutes les prises."""
        # Pré-parser tous les polygones
        self._polygon_cache: dict[int, list[tuple[float, float]]] = {}

        for hold_id, hold in self.index.holds.items():
            points = parse_polygon_points(hold.polygon_str)
            if len(points) < 3:
                continue

            self._polygon_cache[hold_id] = points
            xs = [p[0] for p in points] + [points[0][0]]
            ys = [p[1] for p in points] + [points[0][1]]

            # Polygone principal seulement
            item = pg.PlotDataItem(xs, ys)
            item.hold_id = hold_id
            self.hold_items[hold_id] = item
            self.plot.addItem(item)

        # Les items de sélection et centres sont créés à la demande
        # Connecter les clicks
        self.plot.scene().sigMouseClicked.connect(self._on_mouse_clicked)

    def _ensure_selection_items(self, hold_id: int):
        """Crée les items de sélection pour une prise si nécessaire."""
        if hold_id in self.selection_items:
            return

        points = self._polygon_cache.get(hold_id)
        if not points:
            return

        xs = [p[0] for p in points] + [points[0][0]]
        ys = [p[1] for p in points] + [points[0][1]]

        # Bordure de sélection
        select_item = pg.PlotDataItem(xs, ys, pen=pg.mkPen(color='w', width=4))
        select_item.setVisible(False)
        self.selection_items[hold_id] = select_item
        self.plot.addItem(select_item)

        # Point central
        hold = self.index.holds.get(hold_id)
        if hold:
            cx, cy = hold.centroid
            center = pg.ScatterPlotItem([cx], [cy], size=8)
            center.setVisible(False)
            self.center_items[hold_id] = center
            self.plot.addItem(center)

    def set_color_mode(self, mode: ColorMode):
        """Change le mode de coloration."""
        self.color_mode = mode
        # Invalider le cache fréquence si on change de mode
        self._frequency_cache.clear()

    def set_colormap(self, cmap: Colormap):
        """Change la palette de couleurs."""
        self.colormap = cmap

    def set_annotation_data(self, annotations: dict[int, AnnotationData]):
        """
        Définit les données d'annotations pour les modes GRIP_TYPE/CONDITION/DIFFICULTY.

        Args:
            annotations: Dict hold_id -> AnnotationData
        """
        self._annotation_cache = annotations

    def update_colors(
        self,
        min_ircra: float,
        max_ircra: float,
        valid_holds: set[int] = None,
        valid_climb_ids: set[str] = None
    ):
        """
        Met à jour les couleurs selon la plage de niveau et le mode actif.

        Args:
            min_ircra: Grade minimum
            max_ircra: Grade maximum
            valid_holds: Si fourni, seules ces prises sont colorées (les autres grisées)
            valid_climb_ids: Si fourni, ne considère que ces blocs pour calculer les couleurs
        """
        self.min_ircra = min_ircra
        self.max_ircra = max_ircra

        # Pré-calculer les quantiles si mode fréquence
        if self.color_mode == ColorMode.FREQUENCY:
            self._frequency_cache = self.index.get_holds_usage_quantiles(
                min_ircra, max_ircra, valid_climb_ids
            )

        # Pré-calculer le comptage si mode rare
        if self.color_mode == ColorMode.RARE:
            if valid_climb_ids is not None:
                # Compter manuellement avec le filtre
                self._usage_count_cache = {}
                for hold_id, climb_ids in self.index.hold_to_climbs.items():
                    count = sum(1 for cid in climb_ids if cid in valid_climb_ids)
                    self._usage_count_cache[hold_id] = count
            else:
                # Utiliser get_holds_usage()
                self._usage_count_cache = self.index.get_holds_usage(min_ircra, max_ircra)

        for hold_id, item in self.hold_items.items():
            # Si valid_holds est fourni et cette prise n'en fait pas partie → grisée
            if valid_holds is not None and hold_id not in valid_holds:
                color = (80, 80, 80, 40)  # Très gris, très transparent
                pen = pg.mkPen(color=color, width=1)
                brush = pg.mkBrush(color=(*color[:3], 30))
                item.setPen(pen)
                item.setFillLevel(0)
                item.setBrush(brush)
                continue

            # Calculer la valeur selon le mode
            value = self._get_hold_value(hold_id, min_ircra, max_ircra, valid_climb_ids)

            if value is None:
                # Prise hors filtre → grisée
                color = (128, 128, 128, 50)
            else:
                # Appliquer la colormap
                color = apply_colormap(value, self.colormap, alpha=180)

            pen = pg.mkPen(color=color, width=2)
            brush = pg.mkBrush(color=(*color[:3], 80))

            item.setPen(pen)
            item.setFillLevel(0)
            item.setBrush(brush)

    def _get_hold_value(
        self,
        hold_id: int,
        min_ircra: float,
        max_ircra: float,
        valid_climb_ids: set[str] = None
    ) -> Optional[float]:
        """
        Calcule la valeur normalisée [0, 1] d'une prise selon le mode actif.

        Returns:
            Valeur entre 0 et 1, ou None si prise hors filtre
        """
        if self.color_mode == ColorMode.MIN_GRADE:
            grade = self.index.get_hold_min_grade(
                hold_id, min_ircra, max_ircra, valid_climb_ids
            )
            if grade is None:
                return None
            # Normaliser dans la plage
            if max_ircra <= min_ircra:
                return 0.5
            return (grade - min_ircra) / (max_ircra - min_ircra)

        elif self.color_mode == ColorMode.MAX_GRADE:
            grade = self.index.get_hold_max_grade(
                hold_id, min_ircra, max_ircra, valid_climb_ids
            )
            if grade is None:
                return None
            # Normaliser dans la plage
            if max_ircra <= min_ircra:
                return 0.5
            return (grade - min_ircra) / (max_ircra - min_ircra)

        elif self.color_mode == ColorMode.FREQUENCY:
            # Utiliser le cache des quantiles
            return self._frequency_cache.get(hold_id)

        elif self.color_mode == ColorMode.RARE:
            # Mode rare: prises rares en valeur (couleur chaude), communes neutres
            # 0=1.0 (max), 1=0.75, 2=0.5, 3=0.25, 4+=0.0 (min)
            count = self._usage_count_cache.get(hold_id, 0)
            if count == 0:
                return 1.0   # Jamais utilisée → très visible
            elif count == 1:
                return 0.75  # 1 fois → visible
            elif count == 2:
                return 0.50  # 2 fois → modéré
            elif count == 3:
                return 0.25  # 3 fois → peu visible
            else:
                return 0.0   # 4+ fois → neutre

        # Modes annotations (ADR-008)
        elif self.color_mode == ColorMode.GRIP_TYPE:
            annotation = self._annotation_cache.get(hold_id)
            if not annotation or not annotation.consensus.grip_type:
                return None
            return GRIP_TYPE_VALUES.get(annotation.consensus.grip_type, 0.5)

        elif self.color_mode == ColorMode.CONDITION:
            annotation = self._annotation_cache.get(hold_id)
            if not annotation or not annotation.consensus.condition:
                return None
            return CONDITION_VALUES.get(annotation.consensus.condition, 0.5)

        elif self.color_mode == ColorMode.DIFFICULTY:
            annotation = self._annotation_cache.get(hold_id)
            if not annotation or not annotation.consensus.difficulty:
                return None
            return DIFFICULTY_VALUES.get(annotation.consensus.difficulty, 0.5)

        return None

    def _on_mouse_clicked(self, event):
        """Gère les clicks sur les prises."""
        # Convertir les coordonnées de scène en coordonnées du plot
        pos = event.scenePos()
        vb = self.plot.getViewBox()
        mouse_point = vb.mapSceneToView(pos)
        x, y = mouse_point.x(), mouse_point.y()

        # Trouver la prise cliquée (test point-dans-polygone)
        clicked_hold = self._find_hold_at(x, y)
        if clicked_hold is not None:
            self.toggle_selection(clicked_hold)
            self.hold_clicked.emit(clicked_hold)

    def _find_hold_at(self, x: float, y: float) -> int | None:
        """Trouve la prise à la position (x, y) en coordonnées du plot."""
        for hold_id, points in self._polygon_cache.items():
            if self._point_in_polygon(x, y, points):
                return hold_id
        return None

    def _point_in_polygon(self, x: float, y: float, polygon: list[tuple[float, float]]) -> bool:
        """Test point-dans-polygone (ray casting algorithm)."""
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    def toggle_selection(self, hold_id: int):
        """Toggle la sélection d'une prise."""
        if hold_id in self.selected_holds:
            self.selected_holds.remove(hold_id)
            self._update_hold_selection(hold_id, False)
        else:
            self.selected_holds.append(hold_id)
            self._update_hold_selection(hold_id, True)

        self.selection_changed.emit(list(self.selected_holds))

    def undo_last_selection(self) -> bool:
        """Annule la dernière sélection. Retourne True si une prise a été désélectionnée."""
        if not self.selected_holds:
            return False
        hold_id = self.selected_holds.pop()
        self._update_hold_selection(hold_id, False)
        self.selection_changed.emit(list(self.selected_holds))
        return True

    def _update_hold_selection(self, hold_id: int, selected: bool):
        """Met à jour l'affichage de sélection pour une prise."""
        # Créer les items de sélection si nécessaire
        self._ensure_selection_items(hold_id)

        if hold_id in self.selection_items:
            self.selection_items[hold_id].setVisible(selected)
        if hold_id in self.center_items:
            self.center_items[hold_id].setVisible(selected)
            if selected:
                self.center_items[hold_id].setBrush(pg.mkBrush('w'))
                self.center_items[hold_id].setPen(pg.mkPen('w'))

    def clear_selection(self):
        """Efface toutes les sélections et highlights."""
        # Effacer les sélections de prises
        for hold_id in self.selected_holds:
            self._update_hold_selection(hold_id, False)
        self.selected_holds.clear()

        # Effacer les highlights de blocs
        self.clear_climb_highlight()
        self.selection_changed.emit([])

    def clear_climb_highlight(self):
        """Efface le highlight d'un bloc (prises colorées + tapes)."""
        # Masquer tous les items de sélection existants
        for hold_id in self.selection_items:
            self.selection_items[hold_id].setVisible(False)
        for hold_id in self.center_items:
            self.center_items[hold_id].setVisible(False)

        # Effacer les lignes de tape et contours supplémentaires
        self._clear_tape_lines()
        self._clear_extra_contours()

    def restore_selection_display(self):
        """Réaffiche les bordures des prises sélectionnées."""
        for hold_id in self.selected_holds:
            self._update_hold_selection(hold_id, True)

    def get_selected_holds(self) -> list[int]:
        """Retourne les IDs des prises sélectionnées."""
        return list(self.selected_holds)

    def highlight_climb_holds(self, climb_id: str):
        """Met en évidence les prises d'un bloc spécifique (style app.py)."""
        climb = self.index.climbs.get(climb_id)
        if not climb:
            return

        # Réinitialiser toutes les sélections
        for hold_id in self.selection_items:
            self.selection_items[hold_id].setVisible(False)
            self.center_items[hold_id].setVisible(False)

        # Effacer les anciens tapes et contours supplémentaires
        self._clear_tape_lines()
        self._clear_extra_contours()

        # Identifier les prises de départ
        from mastoc.api.models import HoldType
        climb_holds = climb.get_holds()
        start_holds = [ch for ch in climb_holds if ch.hold_type == HoldType.START]

        # Mettre en évidence les prises du bloc (contour blanc épais comme app.py)
        CONTOUR_WIDTH = 8
        for ch in climb_holds:
            # Créer les items de sélection si nécessaire
            self._ensure_selection_items(ch.hold_id)

            if ch.hold_id in self.selection_items:
                self.selection_items[ch.hold_id].setVisible(True)

                # Contour blanc pour toutes les prises (comme app.py)
                # Sauf FEET qui a un contour NEON_BLUE
                if ch.hold_type == HoldType.FEET:
                    color = (49, 218, 255)  # NEON_BLUE
                else:
                    color = 'w'  # Blanc

                self.selection_items[ch.hold_id].setPen(
                    pg.mkPen(color=color, width=CONTOUR_WIDTH)
                )

                # Prise TOP : double contour écarté
                if ch.hold_type == HoldType.TOP:
                    self._add_expanded_contour(ch.hold_id, CONTOUR_WIDTH)

        # Dessiner les tapes pour les prises de départ
        self._draw_start_tapes(start_holds)

    def _clear_tape_lines(self):
        """Efface toutes les lignes de tape."""
        for item in self.tape_items:
            self.plot.removeItem(item)
        self.tape_items.clear()

    def _clear_extra_contours(self):
        """Efface les contours supplémentaires (TOP)."""
        for item in self.extra_contours:
            self.plot.removeItem(item)
        self.extra_contours.clear()

    def _add_expanded_contour(self, hold_id: int, width: int):
        """Ajoute un contour écarté pour les prises TOP (double contour)."""
        points = self._polygon_cache.get(hold_id)
        if not points or len(points) < 3:
            return

        hold = self.index.holds.get(hold_id)
        if not hold:
            return

        # Dilater les points depuis le centroïde
        cx, cy = hold.centroid
        expansion = 15  # Pixels d'expansion
        expanded_points = []
        for px, py in points:
            dx, dy = px - cx, py - cy
            dist = (dx**2 + dy**2) ** 0.5
            if dist > 0:
                scale = (dist + expansion) / dist
                expanded_points.append((cx + dx * scale, cy + dy * scale))
            else:
                expanded_points.append((px, py))

        # Créer le contour écarté
        xs = [p[0] for p in expanded_points] + [expanded_points[0][0]]
        ys = [p[1] for p in expanded_points] + [expanded_points[0][1]]
        item = pg.PlotDataItem(xs, ys, pen=pg.mkPen(color='w', width=width))
        self.extra_contours.append(item)
        self.plot.addItem(item)

    def _draw_start_tapes(self, start_holds: list):
        """
        Dessine les lignes de tape pour les prises de départ.

        Logique (comme dans l'app Stokt) :
        - 1 prise de départ → 2 lignes (left + right) formant un "V"
        - 2+ prises de départ → 1 ligne centrale par prise
        """
        from mastoc.api.models import ClimbHold

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
