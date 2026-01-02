"""
Génération de pictos pour les blocs.

Représentation simplifiée d'un bloc : cercles colorés sur fond blanc.
"""

import math
from dataclasses import dataclass, field
from PIL import Image, ImageDraw
from collections import Counter

from mastoc.api.models import Climb, Hold, HoldType


@dataclass
class PictoStyle:
    """Paramètres de style pour le rendu des pictogrammes."""

    # Fond
    background_color: tuple[int, int, int] = (255, 255, 255)  # Blanc par défaut
    transparent_background: bool = False  # Fond transparent (RGBA)

    # Opacité des prises (0.0 = transparent, 1.0 = opaque)
    hold_opacity: float = 1.0  # Opacité des prises du bloc
    context_opacity: float = 1.0  # Opacité des prises de contexte

    # Prises de contexte (top holds)
    context_color: tuple[int, int, int] = (220, 220, 220)  # Gris clair
    context_count: int = 20  # Nombre de prises de contexte
    show_context: bool = True  # Afficher les prises de contexte
    context_use_polygon: bool = False  # Contexte en forme polygonale
    context_use_dilation: bool = True  # Appliquer la dilatation au contexte (sinon taille originale)

    # Taille des cercles
    hold_radius_factor: float = 1.0  # Multiplicateur du rayon
    min_radius_climb: float = 3.0  # Rayon minimum prises du bloc
    max_radius_climb: float = 20.0  # Rayon maximum prises du bloc
    min_radius_context: float = 2.0  # Rayon minimum prises de contexte
    max_radius_context: float = 15.0  # Rayon maximum prises de contexte
    proportional_scaling: bool = False  # Scaling proportionnel entre min et max

    # Forme des prises
    use_fitted_ellipse: bool = False  # Utiliser des ellipses fittées sur les polygones
    use_polygon_shape: bool = False  # Utiliser la forme polygonale des prises
    polygon_dilation: float = 1.0  # Facteur de dilatation du polygone (1.0 = taille originale)
    polygon_fill_opacity: float = 1.0  # Opacité du remplissage (0.0 = transparent)
    polygon_outline_opacity: float = 1.0  # Opacité du contour (même couleur que la prise)
    polygon_outline_width: int = 2  # Épaisseur du contour du polygone

    # Contours
    outline_light_holds: bool = True  # Liseré noir sur couleurs claires
    light_threshold: int = 180  # Seuil de luminance pour "clair"

    # Marqueurs spéciaux
    top_marker_offset: float = 3.0  # Offset du double cercle TOP
    top_marker_width: int = 2  # Épaisseur du marqueur TOP
    feet_color: tuple[int, int, int] = (49, 218, 255)  # Bleu néon FEET
    feet_width: int = 2  # Épaisseur contour FEET
    tape_width: int = 2  # Épaisseur des lignes de tape

    # Marge
    margin_ratio: float = 0.1  # Marge autour des prises

    def to_dict(self) -> dict:
        """Convertit le style en dictionnaire pour sérialisation JSON."""
        return {
            "background_color": list(self.background_color),
            "transparent_background": self.transparent_background,
            "hold_opacity": self.hold_opacity,
            "context_opacity": self.context_opacity,
            "context_color": list(self.context_color),
            "context_count": self.context_count,
            "show_context": self.show_context,
            "context_use_polygon": self.context_use_polygon,
            "context_use_dilation": self.context_use_dilation,
            "hold_radius_factor": self.hold_radius_factor,
            "min_radius_climb": self.min_radius_climb,
            "max_radius_climb": self.max_radius_climb,
            "min_radius_context": self.min_radius_context,
            "max_radius_context": self.max_radius_context,
            "proportional_scaling": self.proportional_scaling,
            "use_fitted_ellipse": self.use_fitted_ellipse,
            "use_polygon_shape": self.use_polygon_shape,
            "polygon_dilation": self.polygon_dilation,
            "polygon_fill_opacity": self.polygon_fill_opacity,
            "polygon_outline_opacity": self.polygon_outline_opacity,
            "polygon_outline_width": self.polygon_outline_width,
            "outline_light_holds": self.outline_light_holds,
            "light_threshold": self.light_threshold,
            "top_marker_offset": self.top_marker_offset,
            "top_marker_width": self.top_marker_width,
            "feet_color": list(self.feet_color),
            "feet_width": self.feet_width,
            "tape_width": self.tape_width,
            "margin_ratio": self.margin_ratio,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PictoStyle":
        """Crée un PictoStyle depuis un dictionnaire."""
        return cls(
            background_color=tuple(data.get("background_color", [255, 255, 255])),
            transparent_background=data.get("transparent_background", False),
            hold_opacity=data.get("hold_opacity", 1.0),
            context_opacity=data.get("context_opacity", 1.0),
            context_color=tuple(data.get("context_color", [220, 220, 220])),
            context_count=data.get("context_count", 20),
            show_context=data.get("show_context", True),
            context_use_polygon=data.get("context_use_polygon", False),
            context_use_dilation=data.get("context_use_dilation", True),
            hold_radius_factor=data.get("hold_radius_factor", 1.0),
            min_radius_climb=data.get("min_radius_climb", 3.0),
            max_radius_climb=data.get("max_radius_climb", 20.0),
            min_radius_context=data.get("min_radius_context", 2.0),
            max_radius_context=data.get("max_radius_context", 15.0),
            proportional_scaling=data.get("proportional_scaling", False),
            use_fitted_ellipse=data.get("use_fitted_ellipse", False),
            use_polygon_shape=data.get("use_polygon_shape", False),
            polygon_dilation=data.get("polygon_dilation", 1.0),
            polygon_fill_opacity=data.get("polygon_fill_opacity", 1.0),
            polygon_outline_opacity=data.get("polygon_outline_opacity", 1.0),
            polygon_outline_width=data.get("polygon_outline_width", 2),
            outline_light_holds=data.get("outline_light_holds", True),
            light_threshold=data.get("light_threshold", 180),
            top_marker_offset=data.get("top_marker_offset", 3.0),
            top_marker_width=data.get("top_marker_width", 2),
            feet_color=tuple(data.get("feet_color", [49, 218, 255])),
            feet_width=data.get("feet_width", 2),
            tape_width=data.get("tape_width", 2),
            margin_ratio=data.get("margin_ratio", 0.1),
        )


# Style par défaut (original)
DEFAULT_STYLE = PictoStyle()


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


def is_light_color(color: tuple[int, int, int], threshold: int = 180) -> bool:
    """Détermine si une couleur est claire (besoin de liseré noir)."""
    r, g, b = color
    # Luminance perçue
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance > threshold


def fit_ellipse_to_polygon(points: list[tuple[float, float]]) -> tuple[float, float, float, float, float] | None:
    """
    Calcule une ellipse englobante pour un polygone via PCA.

    Args:
        points: Liste de points (x, y) du polygone

    Returns:
        Tuple (cx, cy, a, b, angle) où:
        - cx, cy: centre de l'ellipse
        - a: demi-axe majeur
        - b: demi-axe mineur
        - angle: angle de rotation en degrés
    """
    if len(points) < 3:
        return None

    # Calculer le centroïde
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)

    # Centrer les points
    centered = [(p[0] - cx, p[1] - cy) for p in points]

    # Calculer la matrice de covariance
    cov_xx = sum(p[0] * p[0] for p in centered) / len(points)
    cov_yy = sum(p[1] * p[1] for p in centered) / len(points)
    cov_xy = sum(p[0] * p[1] for p in centered) / len(points)

    # Valeurs propres (formules analytiques pour 2x2)
    trace = cov_xx + cov_yy
    det = cov_xx * cov_yy - cov_xy * cov_xy

    # Discriminant
    disc = math.sqrt(max(0, trace * trace / 4 - det))
    lambda1 = trace / 2 + disc
    lambda2 = trace / 2 - disc

    # Demi-axes (2x écart-type pour couvrir ~95% des points)
    a = 2 * math.sqrt(max(lambda1, 0.01))
    b = 2 * math.sqrt(max(lambda2, 0.01))

    # Angle de rotation
    if abs(cov_xy) < 1e-10:
        angle = 0 if cov_xx >= cov_yy else 90
    else:
        angle = math.degrees(math.atan2(lambda1 - cov_xx, cov_xy))

    return (cx, cy, a, b, angle)


def scale_radius_proportional(
    raw_radius: float,
    min_raw: float,
    max_raw: float,
    min_display: float,
    max_display: float
) -> float:
    """
    Calcule un rayon proportionnel entre min et max.

    Args:
        raw_radius: Rayon brut (avant scaling)
        min_raw, max_raw: Plage des rayons bruts observés
        min_display, max_display: Plage des rayons à afficher

    Returns:
        Rayon normalisé entre min_display et max_display
    """
    if max_raw <= min_raw:
        return (min_display + max_display) / 2

    # Normaliser entre 0 et 1
    t = (raw_radius - min_raw) / (max_raw - min_raw)
    t = max(0, min(1, t))  # Clamp

    # Interpoler vers la plage d'affichage
    return min_display + t * (max_display - min_display)


def get_hold_ellipse_info(hold: Hold) -> tuple[float, float, float, float, float] | None:
    """Extrait les paramètres d'ellipse fittée d'une prise."""
    points = parse_polygon_points(hold.polygon_str)
    if len(points) < 3:
        return None
    return fit_ellipse_to_polygon(points)


def dilate_polygon(
    points: list[tuple[float, float]],
    factor: float,
    center: tuple[float, float] = None
) -> list[tuple[float, float]]:
    """
    Dilate un polygone par rapport à son centre.

    Args:
        points: Liste de points (x, y) du polygone
        factor: Facteur de dilatation (1.0 = taille originale, 2.0 = double)
        center: Centre de dilatation (par défaut : centroïde du polygone)

    Returns:
        Liste de points dilatés
    """
    if len(points) < 3:
        return points

    # Calculer le centre si non fourni
    if center is None:
        cx = sum(p[0] for p in points) / len(points)
        cy = sum(p[1] for p in points) / len(points)
    else:
        cx, cy = center

    # Dilater chaque point par rapport au centre
    dilated = []
    for px, py in points:
        # Vecteur du centre vers le point
        dx = px - cx
        dy = py - cy
        # Appliquer le facteur de dilatation
        new_x = cx + dx * factor
        new_y = cy + dy * factor
        dilated.append((new_x, new_y))

    return dilated


def get_hold_polygon_scaled(
    hold: Hold,
    scale: float,
    offset_x: float,
    offset_y: float,
    dilation: float = 1.0
) -> list[tuple[float, float]] | None:
    """
    Extrait et transforme le polygone d'une prise pour le rendu.

    Args:
        hold: La prise
        scale: Facteur d'échelle de l'image
        offset_x, offset_y: Offsets de translation
        dilation: Facteur de dilatation du polygone

    Returns:
        Liste de points transformés [(x, y), ...] ou None
    """
    points = parse_polygon_points(hold.polygon_str)
    if len(points) < 3:
        return None

    # Dilater si nécessaire
    if dilation != 1.0:
        points = dilate_polygon(points, dilation)

    # Transformer les coordonnées
    transformed = [
        (px * scale + offset_x, py * scale + offset_y)
        for px, py in points
    ]

    return transformed


def draw_rotated_ellipse(
    img: Image.Image,
    cx: float, cy: float,
    a: float, b: float,
    angle: float,
    fill: tuple,
    outline: tuple = None,
    outline_width: int = 1
) -> Image.Image:
    """
    Dessine une ellipse rotée en utilisant alpha compositing.

    Args:
        img: Image de destination (RGBA)
        cx, cy: Centre de l'ellipse
        a, b: Demi-axes (a = majeur, b = mineur)
        angle: Angle de rotation en degrés
        fill: Couleur de remplissage (RGBA)
        outline: Couleur de contour optionnelle (RGBA)
        outline_width: Épaisseur du contour

    Returns:
        Image avec l'ellipse dessinée
    """
    # Créer un calque assez grand pour l'ellipse + rotation
    padding = int(max(a, b) * 1.5)
    layer_size = int(max(a, b) * 2) + padding * 2
    layer = Image.new('RGBA', (layer_size, layer_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    # Dessiner l'ellipse au centre du calque (non rotée)
    center = layer_size // 2
    bbox = (center - a, center - b, center + a, center + b)
    draw.ellipse(bbox, fill=fill)
    if outline:
        draw.ellipse(bbox, outline=outline, width=outline_width)

    # Faire pivoter le calque
    rotated = layer.rotate(-angle, expand=False, center=(center, center), resample=Image.Resampling.BILINEAR)

    # Calculer la position pour coller sur l'image principale
    paste_x = int(cx - center)
    paste_y = int(cy - center)

    # Coller avec alpha compositing
    # On doit d'abord extraire la région, puis composer, puis recoller
    # Pour simplifier, on utilise paste avec masque
    img.paste(rotated, (paste_x, paste_y), rotated)

    return img


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
    top_holds: list[int] = None,
    style: PictoStyle = None,
    fixed_bounds: tuple[float, float, float, float] = None
) -> Image.Image:
    """
    Génère un picto carré pour un bloc.

    Args:
        climb: Le bloc à représenter
        holds_map: Mapping hold_id -> Hold
        wall_image: Image du mur (pour extraire les couleurs)
        size: Taille du picto en pixels (carré)
        top_holds: Liste des IDs des prises les plus utilisées (affichées en gris)
        style: Paramètres de style (PictoStyle)
        fixed_bounds: Bounding box fixe (min_x, min_y, max_x, max_y) pour cadre constant

    Returns:
        Image PIL du picto
    """
    if style is None:
        style = DEFAULT_STYLE

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
        if style.transparent_background:
            return Image.new('RGBA', (size, size), (0, 0, 0, 0))
        return Image.new('RGB', (size, size), style.background_color)

    # Collecter les infos des top prises (pour le fond gris)
    bg_hold_infos = []  # [(cx, cy, radius, hold), ...]
    if top_holds and style.show_context:
        for hold_id in top_holds:
            if hold_id in climb_hold_ids:
                continue  # Ne pas redessiner les prises du bloc
            hold = holds_map.get(hold_id)
            if not hold:
                continue
            info = get_hold_info(hold)
            if info:
                cx, cy, radius = info
                bg_hold_infos.append((cx, cy, radius, hold))

    # Calculer la bounding box
    if fixed_bounds:
        # Utiliser les bounds fixes (cadre constant)
        min_x, min_y, max_x, max_y = fixed_bounds
    else:
        # Calculer dynamiquement (incluant les top holds pour le contexte)
        all_infos = [(cx, cy, r) for cx, cy, r, _, _, _ in hold_infos] + [(cx, cy, r) for cx, cy, r, _ in bg_hold_infos]

        min_x = min(h[0] - h[2] for h in all_infos)
        max_x = max(h[0] + h[2] for h in all_infos)
        min_y = min(h[1] - h[2] for h in all_infos)
        max_y = max(h[1] + h[2] for h in all_infos)

        # Ajouter une marge
        margin = style.margin_ratio
        width = max_x - min_x
        height = max_y - min_y
        min_x -= width * margin
        max_x += width * margin
        min_y -= height * margin
        max_y += height * margin

    # Calculer dimensions
    width = max_x - min_x
    height = max_y - min_y

    # Facteur d'échelle pour tenir dans le carré
    scale = size / max(width, height)

    # Offset pour centrer
    offset_x = (size - width * scale) / 2 - min_x * scale
    offset_y = (size - height * scale) / 2 - min_y * scale

    # Pré-calculer min/max rayons pour le scaling proportionnel
    if style.proportional_scaling:
        all_radii_climb = [r for _, _, r, _, _, _ in hold_infos]
        all_radii_ctx = [r for _, _, r, _ in bg_hold_infos]

        min_raw_climb = min(all_radii_climb) if all_radii_climb else 1
        max_raw_climb = max(all_radii_climb) if all_radii_climb else 1
        min_raw_ctx = min(all_radii_ctx) if all_radii_ctx else 1
        max_raw_ctx = max(all_radii_ctx) if all_radii_ctx else 1
    else:
        min_raw_climb = max_raw_climb = min_raw_ctx = max_raw_ctx = 1

    # Déterminer si on utilise l'alpha compositing (transparence entre prises)
    needs_alpha = (
        style.transparent_background or
        style.hold_opacity < 1.0 or
        style.context_opacity < 1.0
    )

    # Calculer les alphas
    context_alpha = int(style.context_opacity * 255)
    hold_alpha = int(style.hold_opacity * 255)

    # Créer l'image de base (toujours RGBA si transparence nécessaire)
    if needs_alpha:
        if style.transparent_background:
            img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        else:
            img = Image.new('RGBA', (size, size), (*style.background_color, 255))
    else:
        img = Image.new('RGB', (size, size), style.background_color)
        draw = ImageDraw.Draw(img)

    if needs_alpha:
        # Mode alpha compositing : chaque prise sur un calque séparé
        # D'abord dessiner les top holds en gris clair (fond)
        for cx, cy, radius, ctx_hold in bg_hold_infos:
            px = cx * scale + offset_x
            py = cy * scale + offset_y

            # Calculer le rayon (proportionnel ou simple)
            if style.proportional_scaling:
                pr = scale_radius_proportional(
                    radius * scale,
                    min_raw_ctx * scale,
                    max_raw_ctx * scale,
                    style.min_radius_context,
                    style.max_radius_context
                )
            else:
                pr = max(radius * scale * style.hold_radius_factor, style.min_radius_context)

            # Créer un calque pour cette prise
            layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer)

            # Mode polygone ou cercle pour le contexte
            if style.context_use_polygon:
                dilation = style.polygon_dilation if style.context_use_dilation else 1.0
                polygon_pts = get_hold_polygon_scaled(
                    ctx_hold, scale, offset_x, offset_y, dilation
                )
                if polygon_pts and len(polygon_pts) >= 3:
                    layer_draw.polygon(polygon_pts, fill=(*style.context_color, context_alpha))
                else:
                    # Fallback : cercle
                    bbox = (px - pr, py - pr, px + pr, py + pr)
                    layer_draw.ellipse(bbox, fill=(*style.context_color, context_alpha))
            else:
                # Mode cercle standard
                bbox = (px - pr, py - pr, px + pr, py + pr)
                layer_draw.ellipse(bbox, fill=(*style.context_color, context_alpha))

            # Fusionner avec alpha compositing
            img = Image.alpha_composite(img, layer)

        # Ensuite dessiner les prises du bloc (premier plan)
        for cx, cy, radius, color, hold_type, hold in hold_infos:
            px = cx * scale + offset_x
            py = cy * scale + offset_y

            # Calculer le rayon (proportionnel ou simple)
            if style.proportional_scaling:
                pr = scale_radius_proportional(
                    radius * scale,
                    min_raw_climb * scale,
                    max_raw_climb * scale,
                    style.min_radius_climb,
                    style.max_radius_climb
                )
            else:
                pr = max(radius * scale * style.hold_radius_factor, style.min_radius_climb)

            # Créer un calque pour cette prise
            layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            layer_draw = ImageDraw.Draw(layer)

            # Couleur avec outline si nécessaire
            outline_color_hold = (0, 0, 0, hold_alpha) if style.outline_light_holds and is_light_color(color, style.light_threshold) else None

            # Mode polygone, ellipse fittée ou cercle
            if style.use_polygon_shape:
                # Mode polygone dilaté
                polygon_pts = get_hold_polygon_scaled(
                    hold, scale, offset_x, offset_y, style.polygon_dilation
                )
                if polygon_pts and len(polygon_pts) >= 3:
                    # Calculer les alphas pour remplissage et contour
                    fill_alpha = int(style.polygon_fill_opacity * hold_alpha)
                    outline_alpha = int(style.polygon_outline_opacity * 255)

                    # Dessiner le remplissage
                    if fill_alpha > 0:
                        layer_draw.polygon(polygon_pts, fill=(*color, fill_alpha))

                    # Dessiner le contour (même couleur que la prise)
                    if outline_alpha > 0 and style.polygon_outline_width > 0:
                        layer_draw.polygon(
                            polygon_pts,
                            outline=(*color, outline_alpha),
                            width=style.polygon_outline_width
                        )
                else:
                    # Fallback : cercle
                    bbox = (px - pr, py - pr, px + pr, py + pr)
                    layer_draw.ellipse(bbox, fill=(*color, hold_alpha))
                    if outline_color_hold:
                        layer_draw.ellipse(bbox, outline=outline_color_hold, width=1)
            elif style.use_fitted_ellipse:
                ellipse_info = get_hold_ellipse_info(hold)
                if ellipse_info:
                    ecx, ecy, ea, eb, angle = ellipse_info
                    # Transformer les coordonnées de l'ellipse
                    epx = ecx * scale + offset_x
                    epy = ecy * scale + offset_y
                    # Appliquer le scaling aux axes
                    if style.proportional_scaling:
                        # Utiliser le même facteur de scaling que pour les cercles
                        avg_raw = (ea + eb) / 2
                        scaled_factor = scale_radius_proportional(
                            avg_raw * scale,
                            min_raw_climb * scale,
                            max_raw_climb * scale,
                            style.min_radius_climb,
                            style.max_radius_climb
                        ) / (avg_raw * scale) if avg_raw * scale > 0 else 1
                        epa = ea * scale * scaled_factor
                        epb = eb * scale * scaled_factor
                    else:
                        epa = ea * scale * style.hold_radius_factor
                        epb = eb * scale * style.hold_radius_factor
                    # Dessiner l'ellipse rotée
                    layer = draw_rotated_ellipse(
                        layer, epx, epy, epa, epb, angle,
                        fill=(*color, hold_alpha),
                        outline=outline_color_hold,
                        outline_width=1
                    )
                else:
                    # Fallback : cercle
                    bbox = (px - pr, py - pr, px + pr, py + pr)
                    layer_draw.ellipse(bbox, fill=(*color, hold_alpha))
                    if outline_color_hold:
                        layer_draw.ellipse(bbox, outline=outline_color_hold, width=1)
            else:
                # Mode cercle standard
                bbox = (px - pr, py - pr, px + pr, py + pr)
                layer_draw.ellipse(bbox, fill=(*color, hold_alpha))
                if outline_color_hold:
                    layer_draw.ellipse(bbox, outline=outline_color_hold, width=1)

            # Prise TOP : double cercle/ellipse
            if hold_type == HoldType.TOP and style.top_marker_width > 0:
                outer_pr = pr + style.top_marker_offset
                outer_bbox = (px - outer_pr, py - outer_pr, px + outer_pr, py + outer_pr)
                if is_light_color(color, style.light_threshold):
                    outline_color = (0, 0, 0, hold_alpha)
                else:
                    outline_color = (*color, hold_alpha)
                layer_draw.ellipse(outer_bbox, outline=outline_color, width=style.top_marker_width)

            # Prise FEET : contour NEON_BLUE
            if hold_type == HoldType.FEET and style.feet_width > 0:
                feet_bbox = (px - pr, py - pr, px + pr, py + pr)
                layer_draw.ellipse(feet_bbox, outline=(*style.feet_color, hold_alpha), width=style.feet_width)

            # Fusionner avec alpha compositing
            img = Image.alpha_composite(img, layer)

        # Dessiner les lignes de tape sur un calque
        hold_colors = {}
        for cx, cy, radius, color, hold_type, hold in hold_infos:
            if hold_type == HoldType.START:
                hold_colors[hold.id] = color

        tape_layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        tape_draw = ImageDraw.Draw(tape_layer)
        _draw_start_tapes(tape_draw, start_holds, holds_map, hold_colors, scale, offset_x, offset_y, style, True, hold_alpha)
        img = Image.alpha_composite(img, tape_layer)

    else:
        # Mode simple (pas de transparence) : dessin direct
        # D'abord dessiner les top holds en gris clair (fond)
        for cx, cy, radius, ctx_hold in bg_hold_infos:
            px = cx * scale + offset_x
            py = cy * scale + offset_y

            # Calculer le rayon (proportionnel ou simple)
            if style.proportional_scaling:
                pr = scale_radius_proportional(
                    radius * scale,
                    min_raw_ctx * scale,
                    max_raw_ctx * scale,
                    style.min_radius_context,
                    style.max_radius_context
                )
            else:
                pr = max(radius * scale * style.hold_radius_factor, style.min_radius_context)

            # Mode polygone ou cercle pour le contexte
            if style.context_use_polygon:
                dilation = style.polygon_dilation if style.context_use_dilation else 1.0
                polygon_pts = get_hold_polygon_scaled(
                    ctx_hold, scale, offset_x, offset_y, dilation
                )
                if polygon_pts and len(polygon_pts) >= 3:
                    draw.polygon(polygon_pts, fill=style.context_color)
                else:
                    bbox = (px - pr, py - pr, px + pr, py + pr)
                    draw.ellipse(bbox, fill=style.context_color)
            else:
                bbox = (px - pr, py - pr, px + pr, py + pr)
                draw.ellipse(bbox, fill=style.context_color)

        # Ensuite dessiner les prises du bloc (premier plan)
        for cx, cy, radius, color, hold_type, hold in hold_infos:
            px = cx * scale + offset_x
            py = cy * scale + offset_y

            # Calculer le rayon (proportionnel ou simple)
            if style.proportional_scaling:
                pr = scale_radius_proportional(
                    radius * scale,
                    min_raw_climb * scale,
                    max_raw_climb * scale,
                    style.min_radius_climb,
                    style.max_radius_climb
                )
            else:
                pr = max(radius * scale * style.hold_radius_factor, style.min_radius_climb)

            # Couleur avec outline si nécessaire
            outline_color_hold = (0, 0, 0) if style.outline_light_holds and is_light_color(color, style.light_threshold) else None

            # Mode polygone, ellipse fittée ou cercle
            if style.use_polygon_shape:
                # Mode polygone dilaté
                polygon_pts = get_hold_polygon_scaled(
                    hold, scale, offset_x, offset_y, style.polygon_dilation
                )
                if polygon_pts and len(polygon_pts) >= 3:
                    # Calculer les alphas pour remplissage et contour
                    fill_alpha = int(style.polygon_fill_opacity * 255)
                    outline_alpha = int(style.polygon_outline_opacity * 255)

                    # Si opacités < 1, utiliser un calque RGBA
                    if fill_alpha < 255 or outline_alpha < 255:
                        img_rgba = img.convert('RGBA') if img.mode != 'RGBA' else img
                        layer = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                        layer_draw = ImageDraw.Draw(layer)

                        if fill_alpha > 0:
                            layer_draw.polygon(polygon_pts, fill=(*color, fill_alpha))
                        if outline_alpha > 0 and style.polygon_outline_width > 0:
                            layer_draw.polygon(
                                polygon_pts,
                                outline=(*color, outline_alpha),
                                width=style.polygon_outline_width
                            )

                        img_rgba = Image.alpha_composite(img_rgba, layer)
                        img = img_rgba.convert('RGB')
                        draw = ImageDraw.Draw(img)
                    else:
                        # Mode opaque simple
                        draw.polygon(polygon_pts, fill=color)
                        if style.polygon_outline_width > 0:
                            draw.polygon(
                                polygon_pts,
                                outline=color,
                                width=style.polygon_outline_width
                            )
                else:
                    # Fallback : cercle
                    bbox = (px - pr, py - pr, px + pr, py + pr)
                    draw.ellipse(bbox, fill=color)
                    if outline_color_hold:
                        draw.ellipse(bbox, outline=outline_color_hold, width=1)
            elif style.use_fitted_ellipse:
                ellipse_info = get_hold_ellipse_info(hold)
                if ellipse_info:
                    ecx, ecy, ea, eb, angle = ellipse_info
                    # Transformer les coordonnées de l'ellipse
                    epx = ecx * scale + offset_x
                    epy = ecy * scale + offset_y
                    # Appliquer le scaling aux axes
                    if style.proportional_scaling:
                        avg_raw = (ea + eb) / 2
                        scaled_factor = scale_radius_proportional(
                            avg_raw * scale,
                            min_raw_climb * scale,
                            max_raw_climb * scale,
                            style.min_radius_climb,
                            style.max_radius_climb
                        ) / (avg_raw * scale) if avg_raw * scale > 0 else 1
                        epa = ea * scale * scaled_factor
                        epb = eb * scale * scaled_factor
                    else:
                        epa = ea * scale * style.hold_radius_factor
                        epb = eb * scale * style.hold_radius_factor
                    # Dessiner l'ellipse rotée (convertir img en RGBA temporairement)
                    img_rgba = img.convert('RGBA') if img.mode != 'RGBA' else img
                    img_rgba = draw_rotated_ellipse(
                        img_rgba, epx, epy, epa, epb, angle,
                        fill=(*color, 255),
                        outline=(*outline_color_hold, 255) if outline_color_hold else None,
                        outline_width=1
                    )
                    img = img_rgba.convert('RGB')
                    draw = ImageDraw.Draw(img)
                else:
                    # Fallback : cercle
                    bbox = (px - pr, py - pr, px + pr, py + pr)
                    draw.ellipse(bbox, fill=color)
                    if outline_color_hold:
                        draw.ellipse(bbox, outline=outline_color_hold, width=1)
            else:
                # Mode cercle standard
                bbox = (px - pr, py - pr, px + pr, py + pr)
                draw.ellipse(bbox, fill=color)
                if outline_color_hold:
                    draw.ellipse(bbox, outline=outline_color_hold, width=1)

            # Prise TOP : double cercle
            if hold_type == HoldType.TOP and style.top_marker_width > 0:
                outer_pr = pr + style.top_marker_offset
                outer_bbox = (px - outer_pr, py - outer_pr, px + outer_pr, py + outer_pr)
                outline_color = (0, 0, 0) if is_light_color(color, style.light_threshold) else color
                draw.ellipse(outer_bbox, outline=outline_color, width=style.top_marker_width)

            # Prise FEET : contour NEON_BLUE
            if hold_type == HoldType.FEET and style.feet_width > 0:
                feet_bbox = (px - pr, py - pr, px + pr, py + pr)
                draw.ellipse(feet_bbox, outline=style.feet_color, width=style.feet_width)

        # Dessiner les lignes de tape
        hold_colors = {}
        for cx, cy, radius, color, hold_type, hold in hold_infos:
            if hold_type == HoldType.START:
                hold_colors[hold.id] = color

        _draw_start_tapes(draw, start_holds, holds_map, hold_colors, scale, offset_x, offset_y, style, False, 255)

    return img


def _draw_start_tapes(
    draw: ImageDraw.Draw,
    start_holds: list,
    holds_map: dict[int, Hold],
    hold_colors: dict[int, tuple[int, int, int]],
    scale: float,
    offset_x: float,
    offset_y: float,
    style: PictoStyle = None,
    needs_alpha: bool = False,
    hold_alpha: int = 255
):
    """
    Dessine les lignes de tape pour les prises de départ.

    Logique (comme dans l'app Stokt) :
    - 1 prise de départ → 2 lignes (left + right) formant un "V"
    - 2+ prises de départ → 1 ligne centrale par prise
    """
    if style is None:
        style = DEFAULT_STYLE

    for ch in start_holds:
        hold = holds_map.get(ch.hold_id)
        if not hold:
            continue

        # Couleur de la prise (ou noir par défaut)
        color = hold_colors.get(ch.hold_id, (0, 0, 0))
        line_color = (*color, hold_alpha) if needs_alpha else color

        if len(start_holds) == 1:
            # Une seule prise : deux lignes (V)
            _draw_tape_line(draw, hold.left_tape_str, line_color, scale, offset_x, offset_y, style.tape_width)
            _draw_tape_line(draw, hold.right_tape_str, line_color, scale, offset_x, offset_y, style.tape_width)
        else:
            # Plusieurs prises : ligne centrale
            _draw_tape_line(draw, hold.center_tape_str, line_color, scale, offset_x, offset_y, style.tape_width)


def _draw_tape_line(
    draw: ImageDraw.Draw,
    tape_str: str,
    color: tuple,
    scale: float,
    offset_x: float,
    offset_y: float,
    width: int = 2
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

    draw.line([(px1, py1), (px2, py2)], fill=color, width=width)


def compute_all_holds_bounds(
    holds_map: dict[int, Hold],
    margin_ratio: float = 0.1
) -> tuple[float, float, float, float]:
    """
    Calcule la bounding box de toutes les prises.

    Args:
        holds_map: Mapping hold_id -> Hold
        margin_ratio: Marge à ajouter (ratio)

    Returns:
        Tuple (min_x, min_y, max_x, max_y)
    """
    if not holds_map:
        return (0, 0, 100, 100)

    infos = []
    for hold in holds_map.values():
        info = get_hold_info(hold)
        if info:
            infos.append(info)

    if not infos:
        return (0, 0, 100, 100)

    min_x = min(h[0] - h[2] for h in infos)
    max_x = max(h[0] + h[2] for h in infos)
    min_y = min(h[1] - h[2] for h in infos)
    max_y = max(h[1] + h[2] for h in infos)

    # Ajouter une marge
    width = max_x - min_x
    height = max_y - min_y
    min_x -= width * margin_ratio
    max_x += width * margin_ratio
    min_y -= height * margin_ratio
    max_y += height * margin_ratio

    return (min_x, min_y, max_x, max_y)


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
    top_n: int = 20,
    style: PictoStyle = None
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
        style: Paramètres de style (PictoStyle)

    Returns:
        Dictionnaire climb_id -> Image PIL
    """
    if style is None:
        style = DEFAULT_STYLE

    # Calculer les top holds une seule fois (utilise context_count du style si show_top_holds est True)
    effective_top_n = style.context_count if style.show_context else top_n
    top_holds = compute_top_holds(climbs, effective_top_n) if show_top_holds and style.show_context else None

    return {
        climb.id: generate_climb_picto(climb, holds_map, wall_image, size, top_holds, style)
        for climb in climbs
    }
