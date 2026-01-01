# STATUS - TODO 18 : Synchronisation Données Sociales

**Progression** : 40%

## Phase 1 : Refresh Compteurs (100%)

- [x] Identifier endpoints Stokt (sends, comments, likes)
- [x] `StoktAPI.get_climb_social_stats(climb_id)` - appelle les 3 endpoints
- [x] `ClimbRepository.update_social_counts()` - mise à jour BD
- [x] `SyncManager.refresh_social_counts(climb_id)` - refresh unitaire
- [x] `SyncManager.refresh_all_social_counts()` - batch avec throttling
- [x] 4 tests unitaires

## Phase 2 : Intégration UI (0%)

- [ ] Bouton "Rafraîchir" sur ClimbDetailPanel
- [ ] Menu "Outils > Rafraîchir stats sociales (tous)"
- [ ] Indicateur stats "stale" (> 7 jours)

## Phase 3 : Approche Complète (0%) - Optionnel

- [ ] Tables `sends`/`comments` Railway
- [ ] Endpoints CRUD
- [ ] UI liste réalisations/commentaires

---

## Fichiers modifiés

- `mastoc/src/mastoc/api/client.py` (+20 lignes)
  - `get_climb_social_stats()` : appelle sends, comments, likes
- `mastoc/src/mastoc/db/repository.py` (+25 lignes)
  - `update_social_counts()` : UPDATE climbed_by, total_likes, total_comments
- `mastoc/src/mastoc/core/sync.py` (+65 lignes)
  - `refresh_social_counts()` : refresh unitaire
  - `refresh_all_social_counts()` : batch avec throttling (1 req/sec)
- `mastoc/tests/test_sync.py` (+110 lignes)
  - 4 tests : refresh single, batch, error handling, repository
