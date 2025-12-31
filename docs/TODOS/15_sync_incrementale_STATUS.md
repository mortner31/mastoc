# STATUS - TODO 15 : Synchronisation Incrémentale

**Progression** : 0%

## Phase 1 : Stokt - Quick Win (0%)

- [ ] Modifier `SyncManager.sync_incremental()` pour `max_age` dynamique
- [ ] Ajouter param `max_age` à `get_all_gym_climbs()`
- [ ] Logique calcul basée sur `last_sync`
- [ ] Tests unitaires
- [ ] Test d'intégration API Stokt

## Phase 2 : Railway - Serveur (0%)

- [ ] Query param `since_created_at` sur `GET /api/climbs`
- [ ] Query param `since_synced_at` sur `GET /api/climbs`
- [ ] Exposer `created_at` dans `ClimbResponse`
- [ ] Tests endpoint

## Phase 3 : Railway - Client (0%)

- [ ] Param `since_created_at` dans `MastocAPI.get_climbs()`
- [ ] Param `since_created_at` dans `MastocAPI.get_all_climbs()`
- [ ] `RailwaySyncManager.sync_incremental()` utilise le filtre
- [ ] Tests unitaires client

## Phase 4 : UI et Feedback (0%)

- [ ] Afficher mode sync (full vs incremental)
- [ ] Indicateur climbs téléchargés vs total
- [ ] Option "Forcer sync complète"

## Phase 5 : Documentation et Tests (0%)

- [ ] Documenter stratégie (ADR ou doc)
- [ ] Tests de performance
- [ ] Mise à jour CHANGELOG
