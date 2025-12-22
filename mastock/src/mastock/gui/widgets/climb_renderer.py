"""
Renderer commun pour l'affichage des blocs.

Génère une image PIL avec :
- Fond grisé/foncé
- Prises du bloc en couleur originale
- Contours blancs (FEET en cyan, TOP avec double contour)
- Lignes de tape pour les départs
"""

from PIL import Image, ImageDraw, ImageEnhance
import numpy as np

from mastock.api.models import Climb, Hold, HoldType


def parse_polygon_points(polygon_str: str) -> list[tuple[float, float]]:
    """Parse polygonStr en liste de tuples (x, y)."""
    points = []
    for point in polygon_str.split():
        if "," in point:
            x, y = point.split(",")
            points.append((float(x), float(y)))
    return points


def parse_tape_line(tape_str: str) -> tuple[tuple[float, float], tuple[float, float]] | None:
    """Parse un tapeStr en deux points."""
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


# Couleurs
NEON_BLUE = (49, 218, 255, 255)  # Cyan pour FEET


def render_climb(
    img: Image.Image,
    climb: Climb,
    holds_map: dict[int, Hold],
    gray_level: float = 0.85,
    brightness: float = 0.25,
    contour_width: int = 8,
) -> np.ndarray:
    """
    Génère le rendu d'un bloc sur l'image.

    Args:
        img: Image de fond (RGB)
        climb: Bloc à afficher
        holds_map: Dictionnaire hold_id -> Hold
        gray_level: Niveau de gris du fond (0=couleur, 1=gris)
        brightness: Luminosité du fond (0=noir, 1=original)
        contour_width: Épaisseur des contours

    Returns:
        Array numpy (H, W, 4) RGBA transposé pour pyqtgraph
    """
    # Créer le fond grisé et foncé
    img_gray = img.convert('L').convert('RGB')
    img_blend = Image.blend(img, img_gray, gray_level)

    if brightness < 1.0:
        enhancer = ImageEnhance.Brightness(img_blend)
        img_blend = enhancer.enhance(brightness)

    # Masque pour les prises du bloc (zones en couleur)
    mask = Image.new('L', img.size, 0)
    mask_draw = ImageDraw.Draw(mask)

    # Contours sur couche transparente
    contours = Image.new('RGBA', img.size, (0, 0, 0, 0))
    contour_draw = ImageDraw.Draw(contours)

    # Prises du bloc
    climb_holds = climb.get_holds()
    start_holds = [ch for ch in climb_holds if ch.hold_type == HoldType.START]

    for ch in climb_holds:
        hold = holds_map.get(ch.hold_id)
        if not hold:
            continue
        points = parse_polygon_points(hold.polygon_str)
        if len(points) < 3:
            continue

        # Masque : zone en couleur originale
        mask_draw.polygon(points, fill=255)

        # Contour selon le type
        if ch.hold_type == HoldType.TOP:
            # Double contour blanc
            contour_draw.polygon(points, outline=(255, 255, 255, 255), width=contour_width)
            # Contour écarté
            cx, cy = hold.centroid
            scale_factor = 1.35
            expanded_points = [
                (cx + (px - cx) * scale_factor, cy + (py - cy) * scale_factor)
                for px, py in points
            ]
            contour_draw.polygon(expanded_points, outline=(255, 255, 255, 255), width=contour_width)
        elif ch.hold_type == HoldType.FEET:
            # Contour cyan
            contour_draw.polygon(points, outline=NEON_BLUE, width=contour_width)
        else:
            # Contour blanc (START, OTHER)
            contour_draw.polygon(points, outline=(255, 255, 255, 255), width=contour_width)

    # Lignes de tape pour les départs
    _draw_start_tapes(contour_draw, start_holds, holds_map, contour_width)

    # Composite : prises en couleur, reste en gris foncé
    result = Image.composite(img, img_blend, mask)
    result = result.convert('RGBA')
    result = Image.alpha_composite(result, contours)

    # Convertir pour pyqtgraph
    arr = np.array(result)
    arr = np.transpose(arr, (1, 0, 2))

    return arr


def _draw_start_tapes(
    draw: ImageDraw.Draw,
    start_holds: list,
    holds_map: dict[int, Hold],
    width: int
):
    """Dessine les lignes de tape pour les prises de départ."""
    for ch in start_holds:
        hold = holds_map.get(ch.hold_id)
        if not hold:
            continue

        if len(start_holds) == 1:
            # Une seule prise : deux lignes (V)
            _draw_tape_line(draw, hold.left_tape_str, width)
            _draw_tape_line(draw, hold.right_tape_str, width)
        else:
            # Plusieurs prises : ligne centrale
            _draw_tape_line(draw, hold.center_tape_str, width)


def _draw_tape_line(draw: ImageDraw.Draw, tape_str: str, width: int):
    """Dessine une ligne de tape."""
    line = parse_tape_line(tape_str)
    if not line:
        return
    (x1, y1), (x2, y2) = line
    draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 255, 255), width=width)
