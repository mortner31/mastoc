# TODO 15 - Synchronisation Incrémentale (Optimisation Téléchargement)

## Objectif

Réduire drastiquement le volume de données téléchargées lors des synchronisations en ne récupérant que les données récentes/modifiées au lieu de tout télécharger systématiquement.

## Contexte

**Situation actuelle :**
- `sync_full()` télécharge TOUS les climbs (~1000+) à chaque synchronisation
- `sync_incremental()` télécharge AUSSI tout, puis compare localement (inefficace)
- Même comportement pour Stokt et Railway

**Impact :**
- Sync quotidienne : ~1000 climbs téléchargés pour ~5 nouveaux
- Temps de sync : plusieurs secondes au lieu de millisecondes
- Consommation bande passante excessive

**Gain potentiel :**
| Scénario | Actuel | Avec filtrage | Gain |
|----------|--------|--------------|------|
| Sync quotidienne | ~1000 climbs | ~5-10 climbs | **~99%** |
| Sync hebdomadaire | ~1000 climbs | ~50-70 climbs | **~93%** |

## Analyse des Capacités de Filtrage

### Stokt API

| Paramètre | Disponible | Description |
|-----------|------------|-------------|
| `max_age` | **OUI** | Nombre de jours depuis création |
| `date_from` | Non | - |
| `face_id` | Non | - |

**Endpoint** : `GET /api/gyms/{gym_id}/climbs?max_age={jours}`

**Problème actuel** : Le code utilise `max_age=9999` systématiquement :
```python
# sync.py - get_all_gym_climbs() ligne ~160
climbs, total, next_url = self.get_gym_climbs(gym_id, max_age=9999)  # Hardcodé !
```

### Railway API

| Paramètre | Disponible | Champ DB | Description |
|-----------|------------|----------|-------------|
| `face_id` | OUI | - | Filtrer par face |
| `grade_min/max` | OUI | - | Filtrer par grade |
| `setter_id` | OUI | - | Filtrer par créateur |
| `since_created_at` | **NON** | `created_at` | À implémenter |
| `since_synced_at` | **NON** | `synced_at` | À implémenter |

**Note** : Les champs `created_at` et `synced_at` existent dans les modèles PostgreSQL mais ne sont pas exposés via les query parameters.

## Tâches

### Phase 1 : Stokt - Quick Win (Client seul)

- [ ] Modifier `SyncManager.sync_incremental()` pour calculer `max_age` dynamiquement
- [ ] Ajouter paramètre `max_age` à `get_all_gym_climbs()`
- [ ] Logique de calcul basée sur `last_sync` :
  ```python
  if last_sync:
      days_since = (datetime.now() - last_sync).days + 1
      max_age = max(days_since, 7)  # Minimum 7 jours de marge
  else:
      max_age = 9999  # Première sync : tout
  ```
- [ ] Tests unitaires pour la logique `max_age`
- [ ] Test d'intégration avec vraie API Stokt

### Phase 2 : Railway - Serveur

- [ ] Ajouter query param `since_created_at` à `GET /api/climbs`
- [ ] Ajouter query param `since_synced_at` à `GET /api/climbs`
- [ ] Exposer `created_at` dans `ClimbResponse` (schema)
- [ ] Tests endpoint avec filtrage date

**Fichier** : `/server/src/mastoc_api/routers/climbs.py`

```python
@router.get("/", response_model=ClimbsListResponse)
async def get_climbs(
    face_id: UUID | None = None,
    # ... autres params existants ...
    since_created_at: datetime | None = None,  # AJOUTER
    since_synced_at: datetime | None = None,   # AJOUTER
    ...
):
    query = select(Climb)
    if since_created_at:
        query = query.where(Climb.created_at >= since_created_at)
    if since_synced_at:
        query = query.where(Climb.synced_at >= since_synced_at)
```

### Phase 3 : Railway - Client

- [ ] Ajouter paramètre `since_created_at` à `MastocAPI.get_climbs()`
- [ ] Ajouter paramètre `since_created_at` à `MastocAPI.get_all_climbs()`
- [ ] Modifier `RailwaySyncManager.sync_incremental()` pour utiliser le filtre
- [ ] Tests unitaires client

**Fichier** : `/mastoc/src/mastoc/api/railway_client.py`

```python
def get_climbs(
    self,
    face_id: Optional[str] = None,
    since_created_at: Optional[datetime] = None,  # AJOUTER
    page: int = 1,
    page_size: int = 500,
) -> tuple[list[Climb], int]:
    params = {"page": page, "page_size": page_size}
    if face_id:
        params["face_id"] = face_id
    if since_created_at:
        params["since_created_at"] = since_created_at.isoformat()
    # ...
```

### Phase 4 : UI et Feedback

- [ ] Afficher le mode de sync dans l'UI (full vs incremental)
- [ ] Indicateur du nombre de climbs téléchargés vs total
- [ ] Option "Forcer sync complète" si incrémentale échoue

### Phase 5 : Documentation et Tests

- [ ] Documenter la stratégie dans ADR ou doc technique
- [ ] Tests de performance (mesurer gain réel)
- [ ] Mise à jour CHANGELOG

## Fichiers à Modifier

```
# Stokt (Phase 1)
/mastoc/src/mastoc/api/client.py           # get_all_gym_climbs() - ajouter param max_age
/mastoc/src/mastoc/core/sync.py            # SyncManager.sync_incremental()

# Railway Serveur (Phase 2)
/server/src/mastoc_api/routers/climbs.py   # Ajouter since_created_at
/server/src/mastoc_api/schemas/climb.py    # Exposer created_at

# Railway Client (Phase 3)
/mastoc/src/mastoc/api/railway_client.py   # MastocAPI.get_climbs()
/mastoc/src/mastoc/core/sync.py            # RailwaySyncManager.sync_incremental()

# Tests
/mastoc/tests/test_sync.py                 # Tests unitaires
```

## Risques et Mitigations

| Risque | Mitigation |
|--------|------------|
| Climbs modifiés non détectés | Utiliser `synced_at` en plus de `created_at` |
| Date serveur vs client décalée | Ajouter marge de sécurité (ex: -1 jour) |
| Première sync après longue période | Détecter et forcer full sync si > 30 jours |
| Bug incrémental rate des données | Option "Forcer sync complète" dans UI |

## Dépendances

- TODO 14 (Portage Client Railway) : pour modifier `RailwaySyncManager`
- Accès serveur Railway : pour modifier les endpoints API

## Références

- ADR-006 : Deux bases SQLite séparées (stokt.db / railway.db)
- `/mastoc/src/mastoc/core/sync.py` : Code de synchronisation actuel
- `/server/src/mastoc_api/routers/climbs.py` : Endpoint climbs Railway
- Plan d'analyse : `/home/mortner/.claude/plans/compressed-launching-thacker.md`
