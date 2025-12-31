# ADR 007 - Synchronisation Incrémentale

**Date** : 2025-12-31
**Statut** : Accepté

## Contexte

La synchronisation entre le client mastoc et les APIs (Stokt et Railway) téléchargeait systématiquement TOUS les climbs à chaque synchronisation, même pour les mises à jour quotidiennes.

**Problème identifié** :
- ~1000+ climbs téléchargés à chaque sync
- Temps de sync : plusieurs secondes au lieu de millisecondes
- Consommation bande passante excessive
- Pour une sync quotidienne : ~1000 climbs téléchargés pour ~5 nouveaux

## Décision

Implémenter une synchronisation incrémentale qui ne télécharge que les données récentes/modifiées.

### Stratégie par API

**Stokt API** :
- Utilise le paramètre `max_age` existant (nombre de jours depuis création)
- Calcul dynamique basé sur `last_sync` avec marge de sécurité (minimum 7 jours)

**Railway API** :
- Nouveaux query params ajoutés : `since_created_at`, `since_synced_at`
- Filtre côté serveur pour ne retourner que les climbs créés/modifiés après une date

### Interface Utilisateur

Dialog de synchronisation avec :
- Choix du mode : **Incrémentale** (recommandé) ou **Complète**
- Statistiques affichées : climbs téléchargés, ajoutés, mis à jour, total en base
- Mode incrémental désactivé si première synchronisation

## Conséquences

### Positif

| Scénario | Avant | Après | Gain |
|----------|-------|-------|------|
| Sync quotidienne | ~1000 climbs | ~5-10 climbs | **~99%** |
| Sync hebdomadaire | ~1000 climbs | ~50-70 climbs | **~93%** |

- Temps de synchronisation réduit de plusieurs secondes à millisecondes
- Réduction significative de la bande passante
- Meilleure expérience utilisateur

### Négatif

- Complexité accrue du code de synchronisation
- Risque théorique de rater des modifications (mitigé par marge de sécurité)
- Option "Sync complète" nécessaire en fallback

## Implémentation

### Core (sync.py)

```python
class SyncResult:
    mode: str  # "full" ou "incremental"
    climbs_downloaded: int  # Nombre téléchargés depuis API
    total_climbs_local: int  # Total en base après sync
    # ... autres champs existants

class SyncManager:
    def _calculate_max_age(self, last_sync, min_days=7) -> int:
        days_since = (datetime.now() - last_sync).days + 1
        return max(days_since, min_days)

    def sync_incremental(self, callback=None) -> SyncResult:
        # Utilise max_age calculé dynamiquement
        max_age = self._calculate_max_age(last_sync)
        climbs = self.api.get_all_gym_climbs(gym_id, max_age=max_age)
        # ... compare et sauvegarde les nouveaux/modifiés
```

### Serveur Railway (climbs.py)

```python
@router.get("/")
async def get_climbs(
    since_created_at: datetime | None = None,
    since_synced_at: datetime | None = None,
    ...
):
    query = select(Climb)
    if since_created_at:
        query = query.where(Climb.created_at >= since_created_at)
    if since_synced_at:
        query = query.where(Climb.synced_at >= since_synced_at)
```

### UI (dialogs/sync.py)

- `SyncDialog` : Dialog avec choix full/incremental
- `SyncWorker` : Thread worker pour sync non-bloquante
- Affichage des résultats détaillés post-sync

## Fichiers modifiés

```
mastoc/src/mastoc/core/sync.py          # SyncResult enrichi, sync_incremental()
mastoc/src/mastoc/gui/dialogs/sync.py   # Nouveau dialog
mastoc/src/mastoc/gui/app.py            # Utilise SyncDialog
server/src/mastoc_api/routers/climbs.py # Query params since_*
server/src/mastoc_api/schemas/climb.py  # Expose created_at
mastoc/src/mastoc/api/railway_client.py # Param since_created_at
```

## Références

- TODO 15 : Synchronisation Incrémentale
- ADR-006 : Deux Bases SQLite Séparées
