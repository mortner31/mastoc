"""
Génération de pictos pour les blocs.

Représentation simplifiée d'un bloc : cercles colorés sur fond blanc.
"""

import math
from PIL import Image, ImageDraw
from collections import Counter

from mastoc.api.models import Climb, Hold, HoldType


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


def polygon_area(points: list[tuple[float, float]]) -> float:
    """Calcule l'aire d'un polygone (formule du lacet)."""
    n = len(points)
    if n < 3:
        return 0
    area = 0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    return abs(area) / 2


def get_dominant_color(
    img: Image.Image,
    centroid: tuple[float, float],
    radius: int = 15
) -> tuple[int, int, int]:
    """Trouve la couleur dominante autour du centroïde."""
    cx, cy = int(centroid[0]), int(centroid[1])
    colors = []

    for dx in range(-radius, radius + 1, 3):
        for dy in range(-radius, radius + 1, 3):
            x, y = cx + dx, cy + dy
            if 0 <= x < img.width and 0 <= y < img.height:
                pixel = img.getpixel((x, y))
                if len(pixel) >= 3:
                    r, g, b = pixel[:3]
                else:
                    continue
                # Ignorer les pixels gris (pas de couleur)
                max_diff = max(abs(r - g), abs(g - b), abs(r - b))
                if max_diff > 30:
                    colors.append((r // 32 * 32, g // 32 * 32, b // 32 * 32))

    if colors:
        return Counter(colors).most_common(1)[0][0]
    return (200, 200, 200)


def is_light_color(color: tuple[int, int, int]) -> bool:
    """Détermine si une couleur est claire (besoin de liseré noir)."""
    r, g, b = color
    # Luminance perçue
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance > 180


def get_hold_info(hold: Hold) -> tuple[float, float, float]:
    """Extrait centroïde et rayon d'une prise."""
    points = parse_polygon_points(hold.polygon_str)
    if len(points) < 3:
        return None
    cx, cy = hold.centroid
    area = polygon_area(points)
    radius = math.sqrt(area / math.pi)
    return (cx, cy, radius)


def generate_climb_picto(
    climb: Climb,
    holds_map: dict[int, Hold],
    wall_image: Image.Image = None,
    size: int = 128,
    top_holds: list[int] = None
) -> Image.Image:
    """
    Génère un picto carré pour un bloc.

    Args:
        climb: Le bloc à représenter
        holds_map: Mapping hold_id -> Hold
        wall_image: Image du mur (pour extraire les couleurs)
        size: Taille du picto en pixels (carré)
        top_holds: Liste des IDs des prises les plus utilisées (affichées en gris)

    Returns:
        Image PIL du picto
    """
    # Collecter les infos des prises du bloc
    hold_infos = []  # [(cx, cy, radius, color, hold_type, hold), ...]
    climb_hold_ids = set()
    climb_holds = climb.get_holds()
    start_holds = [ch for ch in climb_holds if ch.hold_type == HoldType.START]

    for ch in climb_holds:
        hold = holds_map.get(ch.hold_id)
        if not hold:
            continue

        info = get_hold_info(hold)
        if not info:
            continue

        cx, cy, radius = info
        climb_hold_ids.add(ch.hold_id)

        # Couleur
        if wall_image:
            color = get_dominant_color(wall_image, (cx, cy))
        else:
            color = (200, 200, 200)

        hold_infos.append((cx, cy, radius, color, ch.hold_type, hold))

    if not hold_infos:
        # Aucune prise, retourner image vide
        return Image.new('RGB', (size, size), (255, 255, 255))

    # Collecter les infos des top prises (pour le fond gris)
    bg_hold_infos = []  # [(cx, cy, radius), ...]
    if top_holds:
        for hold_id in top_holds:
            if hold_id in climb_hold_ids:
                continue  # Ne pas redessiner les prises du bloc
            hold = holds_map.get(hold_id)
            if not hold:
                continue
            info = get_hold_info(hold)
            if info:
                bg_hold_infos.append(info)

    # Calculer la bounding box (incluant les top holds pour le contexte)
    all_infos = [(cx, cy, r) for cx, cy, r, _, _, _ in hold_infos] + [(cx, cy, r) for cx, cy, r in bg_hold_infos]

    min_x = min(h[0] - h[2] for h in all_infos)
    max_x = max(h[0] + h[2] for h in all_infos)
    min_y = min(h[1] - h[2] for h in all_infos)
    max_y = max(h[1] + h[2] for h in all_infos)

    # Ajouter une marge
    margin = 0.1
    width = max_x - min_x
    height = max_y - min_y
    min_x -= width * margin
    max_x += width * margin
    min_y -= height * margin
    max_y += height * margin

    # Recalculer après marge
    width = max_x - min_x
    height = max_y - min_y

    # Facteur d'échelle pour tenir dans le carré
    scale = size / max(width, height)

    # Offset pour centrer
    offset_x = (size - width * scale) / 2 - min_x * scale
    offset_y = (size - height * scale) / 2 - min_y * scale

    # Créer l'image
    img = Image.new('RGB', (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # D'abord dessiner les top holds en gris clair (fond)
    GRAY_COLOR = (220, 220, 220)
    for cx, cy, radius in bg_hold_infos:
        px = cx * scale + offset_x
        py = cy * scale + offset_y
        pr = max(radius * scale, 2)
        bbox = (px - pr, py - pr, px + pr, py + pr)
        draw.ellipse(bbox, fill=GRAY_COLOR)

    # Ensuite dessiner les prises du bloc (premier plan)
    for cx, cy, radius, color, hold_type, hold in hold_infos:
        px = cx * scale + offset_x
        py = cy * scale + offset_y
        pr = max(radius * scale, 3)

        bbox = (px - pr, py - pr, px + pr, py + pr)
        draw.ellipse(bbox, fill=color)

        # Liseré noir si couleur claire
        if is_light_color(color):
            draw.ellipse(bbox, outline=(0, 0, 0), width=1)

        # Prise TOP : double cercle
        if hold_type == HoldType.TOP:
            outer_pr = pr + 3
            outer_bbox = (px - outer_pr, py - outer_pr, px + outer_pr, py + outer_pr)
            outline_color = (0, 0, 0) if is_light_color(color) else color
            draw.ellipse(outer_bbox, outline=outline_color, width=2)

        # Prise FEET : contour NEON_BLUE
        if hold_type == HoldType.FEET:
            NEON_BLUE = (49, 218, 255)
            draw.ellipse(bbox, outline=NEON_BLUE, width=2)

    # Dessiner les lignes de tape pour les prises de départ
    # Construire le mapping hold_id -> couleur pour les prises START
    hold_colors = {}
    for cx, cy, radius, color, hold_type, hold in hold_infos:
        if hold_type == HoldType.START:
            hold_colors[hold.id] = color

    _draw_start_tapes(draw, start_holds, holds_map, hold_colors, scale, offset_x, offset_y)

    return img


def _draw_start_tapes(
    draw: ImageDraw.Draw,
    start_holds: list,
    holds_map: dict[int, Hold],
    hold_colors: dict[int, tuple[int, int, int]],
    scale: float,
    offset_x: float,
    offset_y: float
):
    """
    Dessine les lignes de tape pour les prises de départ.

    Logique (comme dans l'app Stokt) :
    - 1 prise de départ → 2 lignes (left + right) formant un "V"
    - 2+ prises de départ → 1 ligne centrale par prise
    """
    for ch in start_holds:
        hold = holds_map.get(ch.hold_id)
        if not hold:
            continue

        # Couleur de la prise (ou noir par défaut)
        color = hold_colors.get(ch.hold_id, (0, 0, 0))

        if len(start_holds) == 1:
            # Une seule prise : deux lignes (V)
            _draw_tape_line(draw, hold.left_tape_str, color, scale, offset_x, offset_y)
            _draw_tape_line(draw, hold.right_tape_str, color, scale, offset_x, offset_y)
        else:
            # Plusieurs prises : ligne centrale
            _draw_tape_line(draw, hold.center_tape_str, color, scale, offset_x, offset_y)


def _draw_tape_line(
    draw: ImageDraw.Draw,
    tape_str: str,
    color: tuple[int, int, int],
    scale: float,
    offset_x: float,
    offset_y: float
):
    """Dessine une ligne de tape avec les coordonnées transformées."""
    line = parse_tape_line(tape_str)
    if not line:
        return
    (x1, y1), (x2, y2) = line

    # Transformer les coordonnées
    px1 = x1 * scale + offset_x
    py1 = y1 * scale + offset_y
    px2 = x2 * scale + offset_x
    py2 = y2 * scale + offset_y

    draw.line([(px1, py1), (px2, py2)], fill=color, width=2)


def compute_top_holds(climbs: list[Climb], n: int = 20) -> list[int]:
    """
    Calcule les N prises les plus utilisées.

    Args:
        climbs: Liste des blocs
        n: Nombre de prises à retourner

    Returns:
        Liste des hold_ids triés par fréquence décroissante
    """
    hold_counts = Counter()
    for climb in climbs:
        for ch in climb.get_holds():
            hold_counts[ch.hold_id] += 1

    return [hold_id for hold_id, _ in hold_counts.most_common(n)]


def generate_climb_pictos_batch(
    climbs: list[Climb],
    holds_map: dict[int, Hold],
    wall_image: Image.Image = None,
    size: int = 128,
    show_top_holds: bool = True,
    top_n: int = 20
) -> dict[str, Image.Image]:
    """
    Génère les pictos pour plusieurs blocs.

    Args:
        climbs: Liste des blocs
        holds_map: Mapping hold_id -> Hold
        wall_image: Image du mur
        size: Taille des pictos
        show_top_holds: Afficher les prises populaires en gris
        top_n: Nombre de prises populaires à afficher

    Returns:
        Dictionnaire climb_id -> Image PIL
    """
    # Calculer les top holds une seule fois
    top_holds = compute_top_holds(climbs, top_n) if show_top_holds else None

    return {
        climb.id: generate_climb_picto(climb, holds_map, wall_image, size, top_holds)
        for climb in climbs
    }
