# STATUS - TODO 08 : Modes de Coloration et Heatmaps

**Progression** : 100%

## Tâches

### Phase 1 : Backend (core) ✅
- [x] Ajouter `get_hold_max_grade()` dans `hold_index.py`
- [x] Ajouter `get_holds_usage_quantiles()` dans `hold_index.py`
- [x] Créer `core/colormaps.py` avec les 7 palettes
- [x] Tests unitaires pour les nouvelles fonctions (17 nouveaux tests)

### Phase 2 : Overlay (widgets) ✅
- [x] Ajouter `ColorMode` enum dans `hold_overlay.py`
- [x] Refactorer `update_colors()` pour supporter les 3 modes
- [x] Intégrer `colormaps.py` dans l'interpolation
- [x] Méthodes `set_color_mode()` et `set_colormap()`

### Phase 3 : UI (hold_selector) ✅
- [x] Ajouter radio buttons pour le mode (3 options)
- [x] Ajouter combobox pour la palette (7 palettes)
- [x] Ajouter aperçu visuel de la palette sélectionnée
- [x] Connecter les signaux

### Phase 4 : Validation ✅
- [x] 128 tests passent
- [x] Import de l'application vérifié

## Fichiers créés/modifiés

| Fichier | Action |
|---------|--------|
| `core/colormaps.py` | **NOUVEAU** - 7 palettes (viridis, plasma, inferno, magma, cividis, turbo, coolwarm) |
| `core/hold_index.py` | Ajout `get_hold_max_grade()`, `get_holds_usage_quantiles()` |
| `gui/widgets/hold_overlay.py` | Ajout `ColorMode`, refactoring `update_colors()` |
| `gui/hold_selector.py` | Ajout contrôles UI (radio buttons, combobox, aperçu) |
| `tests/test_hold_selector.py` | 17 nouveaux tests TODO 08 |

## Fonctionnalités

### Trois modes de coloration
- **Niveau min** : Grade du bloc le plus facile utilisant la prise
- **Niveau max** : Grade du bloc le plus difficile utilisant la prise
- **Fréquence** : Popularité de la prise (quantiles)

### Sept palettes
1. Viridis (recommandé, perceptuellement uniforme)
2. Plasma
3. Inferno
4. Magma
5. Cividis (daltoniens)
6. Turbo (arc-en-ciel)
7. Coolwarm (divergent bleu-rouge)
