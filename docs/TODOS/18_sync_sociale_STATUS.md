# STATUS - TODO 18 : Synchronisation Données Sociales

**Progression** : 100%

## Phase 1 : Refresh Compteurs (100%)

- [x] Identifier endpoints Stokt (sends, comments, likes)
- [x] `StoktAPI.get_climb_social_stats(climb_id)` - appelle les 3 endpoints
- [x] `ClimbRepository.update_social_counts()` - mise à jour BD
- [x] `SyncManager.refresh_social_counts(climb_id)` - refresh unitaire
- [x] `SyncManager.refresh_all_social_counts()` - batch avec throttling
- [x] 4 tests unitaires

## Phase 2 : Intégration UI (100%)

- [x] Bouton "↻" Rafraîchir sur ClimbDetailPanel
- [x] Menu "Outils > Rafraîchir stats sociales (tous)..."
- [x] Indicateur stats "stale" (> 7 jours) - bouton orange + tooltip

## Phase 3 : Approche Complète (0%) - Reporté

- [ ] Tables `sends`/`comments` Railway
- [ ] Endpoints CRUD
- [ ] UI liste réalisations/commentaires

---

## Fichiers modifiés

### Phase 1 (Backend)
- `mastoc/src/mastoc/api/client.py` (+20 lignes)
  - `get_climb_social_stats()` : appelle sends, comments, likes
- `mastoc/src/mastoc/db/repository.py` (+25 lignes)
  - `update_social_counts()` : UPDATE climbed_by, total_likes, total_comments
- `mastoc/src/mastoc/core/sync.py` (+65 lignes)
  - `refresh_social_counts()` : refresh unitaire
  - `refresh_all_social_counts()` : batch avec throttling (1 req/sec)
- `mastoc/tests/test_sync.py` (+110 lignes)
  - 4 tests : refresh single, batch, error handling, repository

### Phase 2 (UI)
- `mastoc/src/mastoc/gui/widgets/climb_detail.py` (+80 lignes)
  - Signal `refresh_social_requested`
  - Bouton "↻" dans la barre des stats
  - Méthodes `on_social_refresh_done()`, `on_social_refresh_error()`
  - Indicateur stale avec `set_last_sync_date()`, `_update_stale_indicator()`
  - Constante `STALE_THRESHOLD_DAYS = 7`
- `mastoc/src/mastoc/gui/app.py` (+90 lignes)
  - Menu "Outils > Rafraîchir stats sociales (tous)..."
  - `refresh_all_social_stats()` avec progression et throttling

---

## Notes

- Phase 3 reportée : nécessite tables supplémentaires côté Railway
- Le refresh est disponible uniquement pour le backend Stokt (pas Railway)
- Throttling à 1 req/sec pour éviter le rate limiting Stokt
