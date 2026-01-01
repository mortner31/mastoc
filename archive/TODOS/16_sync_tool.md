# TODO 16 - Tableau de Bord Sync

## Objectif

Créer un outil simple pour visualiser l'état de synchronisation entre les sources de données et identifier les climbs créés localement.

## Contexte

**Situation actuelle (ADR-006) :**
- Deux bases SQLite : `stokt.db` et `railway.db`
- Les climbs créés sur mastoc ont `stokt_id = NULL`
- La sync incrémentale (TODO 15) gère l'import des nouveaux climbs
- Aucune visibilité sur l'état global de la sync

**Besoin :**
- Voir combien de climbs sont synchronisés vs locaux
- Lister les climbs créés localement (pour décider quoi en faire)
- Optionnellement, rafraîchir les compteurs sociaux (likes, sends)

## Tâches

### Phase 1 : Dashboard Stats

- [ ] Créer `mastoc/core/sync_stats.py`
  - [ ] `get_sync_stats()` : compte climbs par catégorie
  - [ ] `get_local_climbs()` : liste climbs avec `stokt_id=NULL`
  - [ ] `get_last_sync_date()` : date dernière sync
- [ ] Créer CLI `python -m mastoc.tools.sync_status`
  - [ ] Afficher stats en console (tableau simple)
- [ ] Intégrer dans GUI existante
  - [ ] Menu "Outils > État sync" ou barre de statut
  - [ ] Dialog simple avec stats + liste climbs locaux

**Modèle de données :**

```python
@dataclass
class SyncStats:
    """Statistiques de synchronisation."""
    total_climbs: int           # Total climbs en base
    synced_climbs: int          # Avec stokt_id renseigné
    local_climbs: int           # stokt_id = NULL
    last_sync: datetime | None  # Dernière sync

    @property
    def sync_percentage(self) -> float:
        if self.total_climbs == 0:
            return 100.0
        return (self.synced_climbs / self.total_climbs) * 100
```

**Sortie CLI exemple :**

```
=== État Synchronisation mastoc ===
Source active : Railway

Climbs :
  Total     : 1012
  Syncronisés : 1007 (99.5%)
  Locaux    : 5

Dernière sync : 2025-12-31 14:30

Climbs locaux (stokt_id=NULL) :
  • Mon projet test (6A+) - créé 2025-12-30
  • Nouveau bloc (5) - créé 2025-12-31
  ...
```

### Phase 2 : Refresh Compteurs Sociaux (optionnel)

- [ ] Ajouter méthode `refresh_social_counts(climb_id)` dans `MastocAPI`
  - [ ] GET climb depuis Stokt (via `stokt_id`)
  - [ ] Mettre à jour `climbed_by`, `total_likes`, `total_comments` localement
- [ ] Ajouter option "Rafraîchir stats sociales" dans GUI
  - [ ] Pour un climb sélectionné
  - [ ] Pour tous les climbs syncronisés (batch avec throttling)

**Note** : Pas de tables dédiées `sends`/`comments`. On stocke uniquement les compteurs agrégés dans la table `climbs` existante.

## Fichiers à Créer

```
mastoc/src/mastoc/
├── core/
│   └── sync_stats.py      # Stats et requêtes
├── tools/
│   └── sync_status.py     # CLI
└── gui/
    └── dialogs/
        └── sync_status.py # Dialog GUI (optionnel)
```

## Ce qui a été retiré (v2 du TODO)

Les éléments suivants ont été retirés car sur-ingénierie pour le cas d'usage actuel :

| Élément | Raison |
|---------|--------|
| Push vers Stokt | API non validée, nécessite compte setter |
| Import depuis Stokt | Déjà couvert par sync incrémentale (TODO 15) |
| Diff Engine complet | Un simple filtre `stokt_id=NULL` suffit |
| Tables `sends`/`comments` | Compteurs agrégés suffisent |
| Gestion conflits | Cas quasi inexistant |
| UI 3 onglets | Overkill pour le besoin |

Ces éléments pourront être ajoutés dans un TODO futur si le besoin se confirme.

## Dépendances

- TODO 14 (Portage Client Railway) : ✅ Complété
- TODO 15 (Sync Incrémentale) : ✅ Phases 1-3 complétées

## Références

- ADR-006 : Deux Bases SQLite Séparées
- `/mastoc/src/mastoc/core/sync.py` : SyncManager existant
