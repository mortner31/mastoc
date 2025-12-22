# STATUS - TODO 08 : Modes de Coloration et Heatmaps

**Progression** : 100%

## Tâches

### Phase 1 : Backend (core) ✅
- [x] Ajouter `get_hold_max_grade()` dans `hold_index.py`
- [x] Ajouter `get_holds_usage_quantiles()` dans `hold_index.py`
- [x] Créer `core/colormaps.py` avec les 7 palettes
- [x] Index setter → climbs pour filtrage par ouvreur
- [x] Tests unitaires (23 nouveaux tests)

### Phase 2 : Overlay (widgets) ✅
- [x] Ajouter `ColorMode` enum dans `hold_overlay.py`
- [x] Refactorer `update_colors()` pour supporter les 4 modes
- [x] Intégrer `colormaps.py` dans l'interpolation
- [x] Méthodes `set_color_mode()` et `set_colormap()`

### Phase 3 : UI (hold_selector) ✅
- [x] Combobox mode de coloration (Niveau min/max/Fréquence/Rareté)
- [x] Combobox palette (7 palettes)
- [x] Aperçu visuel de la palette
- [x] Filtre par ouvreur (Tous/Inclure/Exclure)
- [x] Checkboxes pour top 20 setters
- [x] Boutons Tout/Rien
- [x] Panel ouvreurs rétractable (caché par défaut)

### Phase 4 : Validation ✅
- [x] 137 tests passent
- [x] Quantiles recalculés à chaque filtrage

## Fichiers créés/modifiés

| Fichier | Action |
|---------|--------|
| `core/colormaps.py` | **NOUVEAU** - 7 palettes LUT 256 couleurs |
| `core/hold_index.py` | `get_hold_max_grade()`, `get_holds_usage_quantiles()`, index setters, filtre include/exclude |
| `gui/widgets/hold_overlay.py` | `ColorMode` enum, refactoring `update_colors()` |
| `gui/hold_selector.py` | Comboboxes mode/palette, filtre setters (checkboxes) |
| `tests/test_hold_selector.py` | 23 nouveaux tests TODO 08 |

## Fonctionnalités

### Quatre modes de coloration
- **Niveau min** : Grade du bloc le plus facile utilisant la prise
- **Niveau max** : Grade du bloc le plus difficile utilisant la prise
- **Fréquence** : Popularité de la prise (quantiles recalculés selon filtres)
- **Rareté** : 5 niveaux (0, 1, 2, 3, 4+ utilisations) - prises rares très visibles

### Sept palettes
1. Viridis (recommandé, perceptuellement uniforme)
2. Plasma
3. Inferno
4. Magma
5. Cividis (daltoniens)
6. Turbo (arc-en-ciel)
7. Coolwarm (divergent bleu-rouge)

### Filtre par ouvreur
- **Tous** : Pas de filtre
- **Inclure** : Uniquement les ouvreurs cochés
- **Exclure** : Tous sauf les ouvreurs cochés
- Top 20 setters affichés (79 au total)
