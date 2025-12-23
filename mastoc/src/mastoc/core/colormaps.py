"""
Gestion des palettes de couleurs (heatmaps) pour la visualisation des prises.

Palettes générées sans dépendance externe (pas de matplotlib requis).
Les LUT sont pré-calculées pour 256 niveaux.
"""

from enum import Enum
import math


class Colormap(Enum):
    """Palettes de couleurs disponibles."""
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"
    TURBO = "turbo"
    COOLWARM = "coolwarm"


# LUT pré-calculées (256 couleurs RGB pour chaque palette)
# Format: liste de tuples (r, g, b) avec valeurs 0-255

def _generate_viridis() -> list[tuple[int, int, int]]:
    """Génère la palette viridis (perceptuellement uniforme)."""
    # Coefficients polynomiaux approximatifs pour viridis
    colors = []
    for i in range(256):
        t = i / 255.0
        # Approximation polynomiale de viridis
        r = int(255 * max(0, min(1, 0.267004 + t * (0.003310 + t * (0.394756 + t * (-0.117387))))))
        g = int(255 * max(0, min(1, 0.004874 + t * (1.306966 + t * (-0.425592 + t * 0.092948)))))
        b = int(255 * max(0, min(1, 0.329415 + t * (0.565491 + t * (-1.169775 + t * 0.526421)))))
        colors.append((r, g, b))
    return colors


def _generate_plasma() -> list[tuple[int, int, int]]:
    """Génère la palette plasma."""
    colors = []
    for i in range(256):
        t = i / 255.0
        # Approximation de plasma
        r = int(255 * max(0, min(1, 0.050383 + t * (2.014523 + t * (-1.290058 + t * 0.189539)))))
        g = int(255 * max(0, min(1, 0.029803 + t * (-0.264776 + t * (1.556932 + t * (-0.342479))))))
        b = int(255 * max(0, min(1, 0.527975 + t * (0.814788 + t * (-2.082147 + t * 0.737692)))))
        colors.append((r, g, b))
    return colors


def _generate_inferno() -> list[tuple[int, int, int]]:
    """Génère la palette inferno (noir → jaune)."""
    colors = []
    for i in range(256):
        t = i / 255.0
        # Approximation de inferno
        r = int(255 * max(0, min(1, 0.001462 + t * (1.229858 + t * (0.653728 + t * (-0.898854))))))
        g = int(255 * max(0, min(1, 0.000466 + t * (-0.094633 + t * (1.288177 + t * (-0.213015))))))
        b = int(255 * max(0, min(1, 0.013866 + t * (1.100166 + t * (-2.268887 + t * 1.170173)))))
        colors.append((r, g, b))
    return colors


def _generate_magma() -> list[tuple[int, int, int]]:
    """Génère la palette magma (noir → rose)."""
    colors = []
    for i in range(256):
        t = i / 255.0
        # Approximation de magma
        r = int(255 * max(0, min(1, 0.001462 + t * (1.015283 + t * (0.557693 + t * (-0.575866))))))
        g = int(255 * max(0, min(1, 0.000466 + t * (-0.113169 + t * (0.965386 + t * 0.141701)))))
        b = int(255 * max(0, min(1, 0.013866 + t * (1.264213 + t * (-1.869202 + t * 0.605845)))))
        colors.append((r, g, b))
    return colors


def _generate_cividis() -> list[tuple[int, int, int]]:
    """Génère la palette cividis (daltonien-optimisé)."""
    colors = []
    for i in range(256):
        t = i / 255.0
        # Approximation de cividis (bleu-gris → jaune)
        r = int(255 * max(0, min(1, -0.046987 + t * (1.286494 + t * (-0.255453 + t * 0.018936)))))
        g = int(255 * max(0, min(1, 0.135112 + t * (0.594445 + t * (0.260096 + t * 0.010278)))))
        b = int(255 * max(0, min(1, 0.333333 + t * (-0.016122 + t * (-0.381716 + t * 0.063898)))))
        colors.append((r, g, b))
    return colors


def _generate_turbo() -> list[tuple[int, int, int]]:
    """Génère la palette turbo (arc-en-ciel amélioré, maximum de distinction)."""
    colors = []
    for i in range(256):
        t = i / 255.0
        # Turbo utilise des polynômes plus complexes
        r = 0.13572138 + t * (4.61539260 + t * (-42.66032258 + t * (
            132.13108234 + t * (-152.94239396 + t * 59.28637943))))
        g = 0.09140261 + t * (2.19418839 + t * (4.84296658 + t * (
            -14.18503333 + t * (4.27729857 + t * 2.82956604))))
        b = 0.10667330 + t * (12.64194608 + t * (-60.58204836 + t * (
            110.36276771 + t * (-89.90310912 + t * 27.34824973))))
        colors.append((
            int(255 * max(0, min(1, r))),
            int(255 * max(0, min(1, g))),
            int(255 * max(0, min(1, b)))
        ))
    return colors


def _generate_coolwarm() -> list[tuple[int, int, int]]:
    """Génère la palette coolwarm (bleu → blanc → rouge, divergent)."""
    colors = []
    for i in range(256):
        t = i / 255.0
        # Divergent colormap: bleu froid → blanc → rouge chaud
        if t < 0.5:
            # Bleu → Blanc
            s = t * 2  # 0 à 1
            r = int(255 * (0.230 + s * 0.770))
            g = int(255 * (0.299 + s * 0.701))
            b = int(255 * (0.754 + s * 0.246))
        else:
            # Blanc → Rouge
            s = (t - 0.5) * 2  # 0 à 1
            r = int(255 * (1.0 - s * 0.294))
            g = int(255 * (1.0 - s * 0.713))
            b = int(255 * (1.0 - s * 0.715))
        colors.append((r, g, b))
    return colors


# Cache des LUT générées
_LUT_CACHE: dict[Colormap, list[tuple[int, int, int]]] = {}


def get_colormap_lut(cmap: Colormap) -> list[tuple[int, int, int]]:
    """
    Retourne la LUT (256 couleurs RGB) pour une palette.

    Args:
        cmap: La palette à utiliser

    Returns:
        Liste de 256 tuples (r, g, b) avec valeurs 0-255
    """
    if cmap not in _LUT_CACHE:
        generators = {
            Colormap.VIRIDIS: _generate_viridis,
            Colormap.PLASMA: _generate_plasma,
            Colormap.INFERNO: _generate_inferno,
            Colormap.MAGMA: _generate_magma,
            Colormap.CIVIDIS: _generate_cividis,
            Colormap.TURBO: _generate_turbo,
            Colormap.COOLWARM: _generate_coolwarm,
        }
        _LUT_CACHE[cmap] = generators[cmap]()
    return _LUT_CACHE[cmap]


def apply_colormap(
    value: float,
    cmap: Colormap,
    alpha: int = 180
) -> tuple[int, int, int, int]:
    """
    Applique une palette à une valeur normalisée.

    Args:
        value: Valeur entre 0.0 et 1.0
        cmap: Palette à utiliser
        alpha: Transparence (0-255)

    Returns:
        Tuple (r, g, b, a) avec valeurs 0-255
    """
    lut = get_colormap_lut(cmap)
    # Clamp et index
    idx = max(0, min(255, int(value * 255)))
    r, g, b = lut[idx]
    return (r, g, b, alpha)


def get_colormap_preview(cmap: Colormap, width: int = 256) -> list[tuple[int, int, int]]:
    """
    Génère un aperçu de la palette (pour affichage UI).

    Args:
        cmap: Palette à prévisualiser
        width: Largeur en pixels

    Returns:
        Liste de width tuples (r, g, b)
    """
    lut = get_colormap_lut(cmap)
    if width == 256:
        return lut
    # Rééchantillonner
    preview = []
    for i in range(width):
        idx = int(i * 255 / (width - 1)) if width > 1 else 0
        preview.append(lut[idx])
    return preview


def get_all_colormaps() -> list[Colormap]:
    """Retourne la liste de toutes les palettes disponibles."""
    return list(Colormap)


def get_colormap_display_name(cmap: Colormap) -> str:
    """Retourne le nom d'affichage d'une palette."""
    names = {
        Colormap.VIRIDIS: "Viridis (recommandé)",
        Colormap.PLASMA: "Plasma",
        Colormap.INFERNO: "Inferno",
        Colormap.MAGMA: "Magma",
        Colormap.CIVIDIS: "Cividis (daltoniens)",
        Colormap.TURBO: "Turbo (arc-en-ciel)",
        Colormap.COOLWARM: "Froid-Chaud",
    }
    return names.get(cmap, cmap.value)
