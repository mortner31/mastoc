# TODO 08 - Modes de Coloration et Heatmaps

## Objectif

Enrichir la visualisation des prises avec trois modes de coloration et une sélection de palettes heatmap professionnelles.

## Contexte

Le mode actuel (`hold_overlay.py`) colore les prises selon le **niveau minimum** des blocs qui les utilisent. Cette logique répond à la question "quelle est la prise la plus accessible ?".

Deux nouvelles perspectives sont pertinentes :
- **Mode Max** : "À quel niveau cette prise devient-elle difficile ?"
- **Mode Fréquence** : "Cette prise est-elle populaire parmi les ouvreurs ?"

## Analyse des Données

### Distribution des usages (hypothèse à valider)

D'après `get_holds_usage()` dans `hold_index.py`, certaines prises sont très utilisées (prises centrales, bacs) tandis que la majorité sont peu sollicitées. Une échelle linéaire écraserait les variations.

**Solution** : Quantiles (ex: percentiles 0, 25, 50, 75, 100) pour étaler la distribution sur toute la palette.

### Palette actuelle

```python
# Dégradé simple vert → orange → rouge (hold_overlay.py:44-72)
if ratio < 0.5:
    r = int(255 * (ratio * 2))
    g = 255
else:
    r = 255
    g = int(255 * (1 - (ratio - 0.5) * 2))
```

**Limite** : 3 couleurs seulement, peu de nuances pour distinguer les niveaux intermédiaires.

## Fonctionnalités

### a) Trois modes de coloration

| Mode | Logique | Question utilisateur |
|------|---------|---------------------|
| **Min** (actuel) | Grade du bloc le plus facile | "Accessible dès quel niveau ?" |
| **Max** | Grade du bloc le plus difficile | "Utilisée jusqu'à quel niveau ?" |
| **Fréquence** | Nombre de blocs utilisant la prise | "Cette prise est-elle populaire ?" |

### b) Sélection de heatmaps

Palettes matplotlib à proposer (256 couleurs chacune) :

| Palette | Caractéristique | Usage recommandé |
|---------|----------------|------------------|
| `viridis` | Perceptuellement uniforme, daltonien-friendly | Défaut recommandé |
| `plasma` | Chaud, haute lisibilité | Niveaux |
| `inferno` | Noir→jaune, contraste fort | Fréquence |
| `magma` | Noir→rose, doux | Niveaux |
| `cividis` | Daltonien-optimisé | Accessibilité |
| `turbo` | Arc-en-ciel amélioré | Maximum de distinction |
| `coolwarm` | Bleu→rouge, divergent | Min/Max contrasté |

### c) Mode fréquence avec quantiles

**Algorithme** :
1. Calculer `usage[hold_id]` via `get_holds_usage()`
2. Calculer les percentiles (0, 10, 25, 50, 75, 90, 100)
3. Mapper chaque prise sur la palette selon son percentile

**Exemple** :
- Prise utilisée par 1 bloc → percentile ~10% → couleur froide
- Prise utilisée par 50 blocs → percentile ~95% → couleur chaude

## Architecture

### Modifications

```
mastock/src/mastock/
├── core/
│   ├── hold_index.py          # Ajouter get_hold_max_grade()
│   └── colormaps.py           # [NOUVEAU] Gestion des palettes
├── gui/
│   └── widgets/
│       ├── hold_overlay.py    # Refactor interpolate_color()
│       └── colormap_picker.py # [NOUVEAU] Sélecteur de palette
└── tests/
    ├── test_colormaps.py      # [NOUVEAU]
    └── test_hold_selector.py  # Étendre les tests
```

### Nouveaux composants

#### `core/colormaps.py`

```python
"""Gestion des palettes de couleurs (heatmaps)."""

from enum import Enum
import numpy as np

class Colormap(Enum):
    VIRIDIS = "viridis"
    PLASMA = "plasma"
    INFERNO = "inferno"
    MAGMA = "magma"
    CIVIDIS = "cividis"
    TURBO = "turbo"
    COOLWARM = "coolwarm"

def get_colormap_colors(cmap: Colormap, n: int = 256) -> np.ndarray:
    """Retourne n couleurs RGBA de la palette."""
    # Utiliser matplotlib.cm ou générer manuellement
    ...

def apply_colormap(value: float, cmap: Colormap) -> tuple[int, int, int, int]:
    """Applique la palette à une valeur [0, 1]."""
    ...
```

#### `core/hold_index.py` - Ajout

```python
def get_hold_max_grade(
    self,
    hold_id: int,
    min_ircra: float = None,
    max_ircra: float = None,
    valid_climb_ids: set[str] = None
) -> Optional[float]:
    """
    Retourne le grade IRCRA du bloc le plus DIFFICILE contenant cette prise.
    """
    # Similaire à get_hold_min_grade() mais avec max() au lieu de min()
    ...

def get_holds_usage_quantiles(
    self,
    min_ircra: float = None,
    max_ircra: float = None,
    quantiles: list[float] = [0, 0.25, 0.5, 0.75, 1.0]
) -> tuple[dict[int, float], list[int]]:
    """
    Retourne les percentiles d'usage pour chaque prise.

    Returns:
        - dict[hold_id, percentile] : 0.0 à 1.0
        - list[int] : seuils de quantiles (pour affichage)
    """
    ...
```

#### `gui/widgets/hold_overlay.py` - Refactoring

```python
class ColorMode(Enum):
    MIN_GRADE = "min"    # Grade du bloc le plus facile
    MAX_GRADE = "max"    # Grade du bloc le plus difficile
    FREQUENCY = "freq"   # Nombre de blocs (quantiles)

class HoldOverlay:
    def __init__(self, ...):
        self.color_mode = ColorMode.MIN_GRADE
        self.colormap = Colormap.VIRIDIS
        ...

    def set_color_mode(self, mode: ColorMode):
        """Change le mode de coloration."""
        ...

    def set_colormap(self, cmap: Colormap):
        """Change la palette de couleurs."""
        ...
```

## UI

### Contrôles à ajouter

Dans le panneau gauche de `hold_selector.py` :

```
┌─────────────────────────────┐
│ Mode de coloration          │
│ ○ Niveau min (par défaut)   │
│ ○ Niveau max                │
│ ○ Fréquence (quantiles)     │
├─────────────────────────────┤
│ Palette                     │
│ [▼ Viridis           ]      │
│ ████████████████████        │  ← Aperçu de la palette
└─────────────────────────────┘
```

## Tâches

### Phase 1 : Backend (core)
- [ ] Ajouter `get_hold_max_grade()` dans `hold_index.py`
- [ ] Ajouter `get_holds_usage_quantiles()` dans `hold_index.py`
- [ ] Créer `core/colormaps.py` avec les 7 palettes
- [ ] Tests unitaires pour les nouvelles fonctions

### Phase 2 : Overlay (widgets)
- [ ] Ajouter `ColorMode` enum dans `hold_overlay.py`
- [ ] Refactorer `update_colors()` pour supporter les 3 modes
- [ ] Intégrer `colormaps.py` dans l'interpolation
- [ ] Tests pour les modes de coloration

### Phase 3 : UI (hold_selector)
- [ ] Ajouter radio buttons pour le mode
- [ ] Ajouter combobox pour la palette
- [ ] Ajouter aperçu visuel de la palette sélectionnée
- [ ] Connecter les signaux

### Phase 4 : Validation
- [ ] Test avec les 1017 blocs et 776 prises
- [ ] Vérifier la distribution des quantiles en mode fréquence
- [ ] Ajuster les paramètres si nécessaire

## Dépendances

| Package | Usage | Installation |
|---------|-------|--------------|
| `matplotlib` | Colormaps | `pip install matplotlib` (optionnel, peut être généré manuellement) |

**Alternative sans matplotlib** : Générer les LUT (lookup tables) des palettes en dur dans `colormaps.py`.

## Références

- Matplotlib colormaps : https://matplotlib.org/stable/users/explain/colors/colormaps.html
- `hold_overlay.py` : `/mastock/src/mastock/gui/widgets/hold_overlay.py`
- `hold_index.py` : `/mastock/src/mastock/core/hold_index.py`
- TODO 06 : `/docs/TODOS/06_interface_filtrage_blocs.md`

## Notes

- La palette `viridis` est recommandée comme défaut car perceptuellement uniforme
- Le mode fréquence avec quantiles est crucial car la distribution d'usage est très asymétrique
- L'aperçu de la palette aide l'utilisateur à choisir sans tâtonnement
