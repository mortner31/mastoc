# TODO 06 - Interface de Filtrage et Sélection de Blocs

## Objectif

Créer une interface interactive permettant de retrouver un bloc (parcours) à partir des prises, avec filtrage par niveau de difficulté et sélection visuelle des prises sur le mur.

## Contexte

Ce TODO complète le TODO 05 (Structure Package Python). Il s'appuie sur :
- L'architecture PyQtGraph + PyQt6 du TODO 05
- Les données extraites : 1017 climbs, 776 prises avec polygones
- L'image du mur (2263×3000 pixels)

## Fonctionnalités

### a) Double slider de niveau

- Slider horizontal avec deux curseurs (min/max)
- Échelle Font : 4+ → 8A
- Grades disponibles : 4, 4+, 5, 5+, 6A, 6A+, 6B, 6B+, 6C, 6C+, 7A, 7A+, 7B, 7B+, 7C, 8A
- Affichage des valeurs sélectionnées (ex: "6A - 7A")
- Filtre les blocs affichés dans la plage sélectionnée

### b) Coloration des prises selon le niveau

**Logique** : Chaque prise est colorée selon le grade du bloc **le plus facile** qui la contient (parmi les blocs dans la plage du slider).

**Palette** : Dégradé continu vert → orange → rouge
- Vert = grade le plus bas de la plage sélectionnée
- Rouge = grade le plus haut de la plage sélectionnée
- Interpolation linéaire entre les deux

**Prises hors filtre** : Grisées (semi-transparentes) si la prise n'appartient à aucun bloc dans la plage de niveau.

### c) Sélection interactive des prises

- Click sur une prise → toggle sélection
- Prises sélectionnées : bordure blanche (highlight)
- Multi-sélection possible
- Logique **ET** : seuls les blocs contenant **TOUTES** les prises sélectionnées sont affichés
- Compteur de résultats en temps réel

### d) Liste des blocs filtrés

Affichée sous l'image du mur :
- Une ligne par bloc : **Nom** | **Auteur** | **Grade**
- Liste scrollable si nombreux résultats
- Click sur un bloc → ouvre la vue détaillée

### e) Vue détaillée d'un bloc

Fenêtre/panneau séparé affichant :

**Image du mur avec prises du bloc** :
- Prises colorées par type :
  - S (Start) : Vert
  - O (Other) : Bleu
  - F (Feet) : Jaune
  - T (Top) : Rouge
- Autres prises grisées

**Informations** :
- Nom du bloc
- Auteur (setter)
- Grade (Font)
- Règle de pieds (feetRule)
- Date de création
- Nombre d'ascensions (climbedBy)

**Navigation** :
- Bouton "Previous" → bloc précédent dans la liste filtrée
- Bouton "Next" → bloc suivant dans la liste filtrée
- Bouton "Fermer" ou "Retour" → retour à la vue principale

## Architecture

```
mastock/src/mastock/gui/
├── widgets/
│   ├── board_view.py        # Vue du mur (existant TODO 05)
│   ├── hold_overlay.py      # [NOUVEAU] Overlay des prises colorées
│   ├── level_slider.py      # [NOUVEAU] Double slider de niveau
│   ├── climb_list.py        # [NOUVEAU] Liste des blocs filtrés
│   └── climb_detail.py      # [NOUVEAU] Vue détaillée d'un bloc
└── app.py                   # Application principale
```

## Données requises

### Structures en mémoire

```python
# Index prise → blocs (pour filtrage rapide)
hold_to_climbs: dict[int, list[str]]  # hold_id → [climb_id, ...]

# Index bloc → grade numérique (pour comparaisons)
climb_grades: dict[str, float]  # climb_id → ircra (numérique)

# Ordre des grades Font
FONT_GRADES = ['4', '4+', '5', '5+', '6A', '6A+', '6B', '6B+',
               '6C', '6C+', '7A', '7A+', '7B', '7B+', '7C', '8A']
```

### Algorithme de coloration

```python
def get_hold_color(hold_id, selected_min, selected_max, hold_to_climbs, climb_grades):
    """
    Retourne la couleur d'une prise selon le bloc le plus facile
    qui la contient dans la plage sélectionnée.

    Returns: QColor (vert→rouge) ou gris si hors filtre
    """
    climbs = hold_to_climbs.get(hold_id, [])

    # Filtrer les blocs dans la plage
    valid_climbs = [c for c in climbs
                    if selected_min <= climb_grades[c] <= selected_max]

    if not valid_climbs:
        return QColor(128, 128, 128, 100)  # Grisé

    # Grade du bloc le plus facile
    min_grade = min(climb_grades[c] for c in valid_climbs)

    # Interpolation vert → rouge
    ratio = (min_grade - selected_min) / (selected_max - selected_min)
    return interpolate_color(GREEN, RED, ratio)
```

## Stack technique

| Composant | Technologie |
|-----------|-------------|
| GUI | PyQtGraph + PyQt6 |
| Slider | QRangeSlider (qtrangeslider) ou custom |
| Liste | QListWidget ou QTableWidget |
| Overlay prises | pyqtgraph.PlotItem avec polygones |

## Références

- TODO 05 : `/docs/TODOS/05_python_package_structure.md`
- Structure données : `/docs/reverse_engineering/04_STRUCTURES.md`
- Données climbs : `/extracted/data/montoboard_ALL_climbs.json`
- Setup prises : `/extracted/data/montoboard_setup.json`
- Image mur : `/extracted/data/montoboard_wall.jpg`

## Notes

- Les 31 blocs sans grade ("?") seront exclus du filtrage
- Performance : pré-calculer l'index `hold_to_climbs` au chargement
- Le slider doit être réactif (mise à jour des couleurs en temps réel)
