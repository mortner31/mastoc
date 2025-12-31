# STATUS - TODO 15 : Synchronisation Incrémentale

**Progression** : 60%

## Phase 1 : Stokt - Quick Win (100%)

- [x] Modifier `SyncManager.sync_incremental()` pour `max_age` dynamique
- [x] Ajouter param `max_age` à `get_all_gym_climbs()`
- [x] Logique calcul basée sur `last_sync` (`_calculate_max_age()`)
- [x] Tests unitaires (4 nouveaux tests)
- [ ] Test d'intégration API Stokt (optionnel - nécessite connexion réelle)

## Phase 2 : Railway - Serveur (100%)

- [x] Query param `since_created_at` sur `GET /api/climbs`
- [x] Query param `since_synced_at` sur `GET /api/climbs`
- [x] Exposer `created_at` dans `ClimbResponse`
- [x] Tests endpoint (2 nouveaux tests)

## Phase 3 : Railway - Client (100%)

- [x] Param `since_created_at` dans `MastocAPI.get_climbs()`
- [x] Param `since_created_at` dans `MastocAPI.get_all_climbs()`
- [x] `RailwaySyncManager.sync_incremental()` créé avec since_created_at
- [x] `RailwaySyncManager.needs_sync()` ajouté
- [x] Tests existants passent (300 tests)

## Phase 4 : UI et Feedback (0%)

- [ ] Afficher mode sync (full vs incremental)
- [ ] Indicateur climbs téléchargés vs total
- [ ] Option "Forcer sync complète"

## Phase 5 : Documentation et Tests (0%)

- [ ] Documenter stratégie (ADR ou doc)
- [ ] Tests de performance
- [ ] Mise à jour CHANGELOG
