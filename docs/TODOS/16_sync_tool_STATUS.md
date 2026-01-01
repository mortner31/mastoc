# STATUS - TODO 16 : Tableau de Bord Sync

**Progression** : 100%

## Phase 1 : Dashboard Stats (100%)

- [x] Créer `mastoc/core/sync_stats.py`
  - [x] `get_sync_stats()`
  - [x] `get_local_climbs()`
- [x] Créer CLI `python -m mastoc.tools.sync_status`
- [x] Intégrer dans GUI (menu Outils > État synchronisation)
- [x] Enrichir endpoint serveur `/api/sync/stats` (climbs_synced, climbs_local)
- [x] Ajouter paramètre `local_only` à `/api/climbs`
- [x] Dialog `SyncStatusDialog` avec stats et liste climbs locaux

## Phase 2 : Refresh Compteurs Sociaux - Reporté

Reporté au TODO 18 (Sync Sociale)
