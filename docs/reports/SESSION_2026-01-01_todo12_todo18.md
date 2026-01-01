# Rapport de Session - TODO 12 + TODO 18

**Date** : 2026-01-01

## Objectifs Atteints

### TODO 12 - Hold Annotations (Archivé à 95%)

- **Backend** : Modèle HoldAnnotation + 4 endpoints REST + 16 tests
- **Client** : Enums, dataclasses, API methods, AnnotationLoader
- **GUI** : 3 ColorModes (GRIP_TYPE, CONDITION, DIFFICULTY) + AnnotationPanel
- **Tests** : 43 tests client
- **Documentation** : ADR-008 créé

### TODO 18 - Sync Données Sociales (Phase 1 : 40%)

- **API** : `get_climb_social_stats()` - appelle sends, comments, likes
- **Repository** : `update_social_counts()` - mise à jour BD
- **SyncManager** :
  - `refresh_social_counts(climb_id)` - refresh unitaire
  - `refresh_all_social_counts()` - batch avec throttling (1 req/sec)
- **Tests** : 4 nouveaux tests

## Commits

| Hash | Message |
|------|---------|
| `997ce80` | feat: TODO 12 - Hold Annotations (85%) |
| `27e43ad` | test: TODO 12 - Tests client annotations (+43 tests) |
| `c83fff6` | docs: Archivage TODO 12 |
| `e7f93b2` | feat: TODO 18 - Phase 1 Refresh compteurs sociaux (40%) |

## Statistiques

- **Tests mastoc** : 375 passent (+47 depuis début de session)
- **Tests serveur** : 16 tests hold_annotations

## Fichiers Créés/Modifiés

### TODO 12

**Serveur :**
- `server/src/mastoc_api/models/hold_annotation.py` (nouveau)
- `server/src/mastoc_api/routers/hold_annotations.py` (nouveau)
- `server/tests/test_hold_annotations.py` (nouveau)

**Client :**
- `mastoc/src/mastoc/api/models.py` (+3 enums, +3 dataclasses)
- `mastoc/src/mastoc/api/railway_client.py` (+4 méthodes)
- `mastoc/src/mastoc/core/annotation_loader.py` (nouveau)
- `mastoc/src/mastoc/gui/widgets/hold_overlay.py` (+3 ColorModes)
- `mastoc/src/mastoc/gui/widgets/annotation_panel.py` (nouveau)
- `mastoc/tests/test_annotation_loader.py` (nouveau, 24 tests)
- `mastoc/tests/test_annotation_panel.py` (nouveau, 19 tests)

**Documentation :**
- `docs/adr/008_hold_annotations.md` (nouveau)

### TODO 18

- `mastoc/src/mastoc/api/client.py` (+20 lignes)
- `mastoc/src/mastoc/db/repository.py` (+25 lignes)
- `mastoc/src/mastoc/core/sync.py` (+65 lignes)
- `mastoc/tests/test_sync.py` (+110 lignes)

## Prochaines Étapes

1. **TODO 18 Phase 2** : Intégration UI
   - Bouton "Rafraîchir" sur ClimbDetailPanel
   - Menu "Outils > Rafraîchir stats sociales (tous)"
   - Indicateur stats "stale" (> 7 jours)

2. **TODO 12 optionnel** : Intégration hold_selector.py
