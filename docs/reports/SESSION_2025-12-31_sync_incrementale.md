# Rapport de Session - Sync Incrémentale TODO 15

**Date** : 2025-12-31

## Objectifs Atteints

- TODO 14 archivé (100% complété)
- TODO 15 avancé à 60% (Phases 1-3 complétées)
- TODO 16 enrichi avec stratégie sync sociale

## Travail Réalisé

### TODO 14 - Archivage

- Déplacé vers `/archive/TODOS/`
- TIMELINE mis à jour

### TODO 15 - Sync Incrémentale (60%)

#### Phase 1 : Stokt - Quick Win (100%)

| Fichier | Modification |
|---------|--------------|
| `mastoc/api/client.py` | `get_all_gym_climbs(max_age=9999)` - param dynamique |
| `mastoc/core/sync.py` | `_calculate_max_age()` basé sur `last_sync` |
| `mastoc/tests/test_sync.py` | +4 tests |

**Comportement** :
- Sync récente (< 7 jours) → `max_age=7` (marge sécurité)
- Sync ancienne (ex: 15j) → `max_age=16`

#### Phase 2 : Railway Serveur (100%)

| Fichier | Modification |
|---------|--------------|
| `server/routers/climbs.py` | `since_created_at`, `since_synced_at` query params |
| `server/routers/climbs.py` | `created_at` exposé dans `ClimbResponse` |
| `server/tests/test_climbs.py` | +2 tests |

#### Phase 3 : Railway Client (100%)

| Fichier | Modification |
|---------|--------------|
| `mastoc/api/railway_client.py` | `since_created_at` dans `get_climbs()` et `get_all_climbs()` |
| `mastoc/core/sync.py` | `RailwaySyncManager.sync_incremental()` créé |
| `mastoc/core/sync.py` | `RailwaySyncManager.needs_sync()` ajouté |

#### Phases 4-5 : Non commencées (optionnelles)

- Phase 4 : UI feedback (mode sync, compteur)
- Phase 5 : Documentation + tests perf

### TODO 16 - Mise à jour

Ajout d'une note importante sur la **limitation de la sync incrémentale** :

> La sync incrémentale (TODO 15) filtre par `created_at` du climb.
> Elle ne détecte PAS les changements sociaux :
> - Réalisation d'un climb (send)
> - Ajout de commentaire
> - Ajout de like

**Solution documentée dans Phase 2c** :
- Sync sociale dédiée interrogeant les endpoints `/latest-sends`, `/comments`, `/likes`
- 3 modes : à la demande, batch, intelligent
- Détection par comparaison des compteurs (`climbed_by`, `total_likes`)

## Commits Créés

```
189b37e feat: TODO 15 Phase 1 - Sync incrémentale Stokt (max_age dynamique)
997d9c6 feat: TODO 15 Phases 2-3 - Sync incrémentale Railway
def5b66 docs: TODO 16 - Ajouter stratégie sync sociale
```

## Tests

- **300 tests passent** (inchangé, pas de régression)
- +4 tests sync Stokt
- +2 tests serveur Railway (non exécutés localement, env manquant)

## Gain Attendu

| Scénario | Avant | Après | Gain |
|----------|-------|-------|------|
| Sync quotidienne | ~1000 climbs | ~10-20 climbs | ~99% |
| Sync hebdomadaire | ~1000 climbs | ~50-100 climbs | ~95% |

## Prochaines Étapes

### TODO 15 (optionnel)
- [ ] Phase 4 : UI feedback
- [ ] Phase 5 : Documentation

### TODO 16 (sync bidirectionnelle)
- [ ] Phase 1 : Diff Engine
- [ ] Phase 2c : Sync sociale (prioritaire pour détecter sends/comments/likes)

### Autres
- TODO 17 : Authentification utilisateurs (créé, 0%)
