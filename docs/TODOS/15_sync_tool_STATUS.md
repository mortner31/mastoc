# STATUS - TODO 15 : Outil de Synchronisation Bidirectionnelle

**Progression** : 0%

## Prérequis

- [ ] TODO 14 complété (MastocAPI client Railway)

## Phase 1 : Diff Engine - Climbs (0%)

- [ ] Créer `mastoc/core/diff_engine.py`
- [ ] Récupérer climbs Railway avec stokt_id
- [ ] Récupérer climbs Stokt
- [ ] Calculer catégories (local_only, stokt_only, synced, conflicts)
- [ ] Retourner ClimbDiffReport avec statistiques

## Phase 1b : Diff Engine - Users (0%)

- [ ] Récupérer users Railway avec stokt_id
- [ ] Extraire setters uniques depuis climbs Stokt
- [ ] Calculer catégories (new_users, updated_users, synced_users)
- [ ] Retourner UserDiffReport

## Phase 2 : API Push/Import Climbs (0%)

- [ ] `push_climb_to_stokt(climb_id)`
- [ ] `import_climb_from_stokt(stokt_climb_id)`
- [ ] Endpoint `PATCH /api/climbs/{id}/stokt-id` sur Railway

## Phase 2b : Sync Users (0%)

- [ ] `import_users_from_stokt()` batch
- [ ] Mettre à jour users existants si nom/avatar changé
- [ ] Créer nouveaux setters découverts

## Phase 2c : Sync Données Sociales (0%)

- [ ] `sync_climb_social(climb_id)`
- [ ] GET efforts → importer sends
- [ ] GET comments → importer commentaires
- [ ] Mettre à jour climbed_by et total_likes
- [ ] Tables Railway : sends, comments

## Phase 3 : Interface Graphique (0%)

- [ ] Créer `mastoc/gui/sync_app.py`
- [ ] Onglet Climbs : dashboard + liste différences
- [ ] Onglet Users : nouveaux / modifiés / à jour
- [ ] Onglet Social : sends, comments par bloc
- [ ] Actions en masse
- [ ] Barre de progression

## Phase 4 : Gestion des Conflits (0%)

- [ ] Détection blocs modifiés des deux côtés
- [ ] UI résolution côte-à-côte
- [ ] Choix : Garder mastoc / Garder Stokt
- [ ] Historique des actions

## Phase 5 : Polish et Tests (0%)

- [ ] Chargement asynchrone
- [ ] Cache données Stokt
- [ ] Tests unitaires DiffEngine
- [ ] Tests d'intégration
- [ ] Documentation utilisateur
