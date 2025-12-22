# STATUS - TODO 06 : Interface de Filtrage et Sélection de Blocs

**Progression** : 100%

## Architecture

L'application fonctionne en **deux modes distincts** :

### Mode Sélection
- Overlay pyqtgraph avec prises colorées par niveau (vert→rouge)
- Multi-sélection de prises avec logique ET
- Bouton Undo pour annuler la dernière sélection
- Slider de luminosité pour ajuster le fond

### Mode Parcours
- Rendu PIL identique à `app.py` (renderer commun)
- Prises du bloc en couleur originale
- Contours blancs (FEET cyan, TOP double contour)
- Lignes de tape pour les départs
- Navigation Préc/Suiv entre les blocs filtrés

## Tâches

### Prérequis (TODO 05) ✅
- [x] Structure package Python en place
- [x] Chargement des données (climbs + setup)
- [x] Affichage basique du mur avec polygones

### Double slider de niveau ✅
- [x] Widget LevelRangeSlider avec deux sliders (min/max)
- [x] Échelle Font (4 → 8A) - 17 grades
- [x] Affichage des valeurs sélectionnées
- [x] Signal range_changed avec valeurs IRCRA

### Coloration des prises ✅
- [x] Index `HoldClimbIndex` (prise → blocs, bloc → grade)
- [x] Méthode `get_hold_min_grade()` pour grade du bloc le plus facile
- [x] Algorithme de couleur (dégradé vert→orange→rouge)
- [x] Prises hors filtre grisées
- [x] Mise à jour en temps réel via `update_colors()`

### Sélection des prises ✅
- [x] Click toggle sur prise via `HoldOverlay`
- [x] Bordure blanche pour sélection
- [x] Multi-sélection supportée (liste ordonnée pour undo)
- [x] Filtrage ET logique via `get_climbs_for_holds()`
- [x] Signal selection_changed émis
- [x] Bouton Undo pour annuler la dernière sélection

### Liste des blocs filtrés ✅
- [x] Widget QListWidget avec `ClimbListItem`
- [x] Affichage : nom | grade | setter
- [x] Compteur de résultats
- [x] Click → passage en mode parcours

### Mode parcours ✅
- [x] Rendu PIL via `climb_renderer.py` (renderer commun)
- [x] Prises colorées par type (contours blancs, FEET cyan, TOP double)
- [x] Lignes de tape pour les départs
- [x] Navigation Previous/Next
- [x] Bouton "Retour sélection"

### Contrôles visuels ✅
- [x] Slider de luminosité (5-100%)
- [x] Image de fond avec chemin corrigé

### Tests ✅
- [x] 21 tests pour les composants TODO 06
- [x] Tests LevelSlider (grades, index, conversion)
- [x] Tests interpolation couleur
- [x] Tests HoldClimbIndex (filtrage, grades, usage)
- [x] **111 tests au total passent**

## Fichiers

| Fichier | Description |
|---------|-------------|
| `gui/widgets/level_slider.py` | Double slider de niveau (min/max) |
| `gui/widgets/hold_overlay.py` | Overlay prises colorées avec sélection |
| `gui/widgets/climb_renderer.py` | **Renderer commun** (rendu PIL partagé) |
| `gui/widgets/climb_detail.py` | Vue détaillée d'un bloc (non utilisé) |
| `gui/hold_selector.py` | Application principale HoldSelectorApp |
| `core/hold_index.py` | Index bidirectionnel prises ↔ blocs |
| `tests/test_hold_selector.py` | Tests unitaires (21 tests) |

## Usage

```bash
cd /media/veracrypt1/Repositories/mastock/mastock
python -m mastock.gui.hold_selector
```

## Fonctionnalités

1. **Mode sélection** : Filtrage par niveau + sélection multi-prises
2. **Mode parcours** : Visualisation des blocs avec rendu identique à app.py
3. **Undo** : Annuler la dernière prise sélectionnée
4. **Luminosité** : Slider pour ajuster le fond
