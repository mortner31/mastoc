# ADR 006 - Deux Bases SQLite Séparées (Stokt + Railway)

**Date** : 2025-12-31
**Statut** : Accepté

## Contexte

Le client mastoc peut se connecter à deux sources de données différentes :
- **Stokt** : API legacy de l'application mobile
- **Railway** : Nouvelle API mastoc-api hébergée sur Railway

Ces deux sources contiennent des données potentiellement différentes :
- Stokt : données live de l'app mobile
- Railway : données importées + créations locales mastoc

Stocker les deux dans une seule base SQLite locale pose des problèmes :
- Conflits lors du changement de source
- Écrasement des données d'une source par l'autre
- Difficulté à distinguer l'origine des données

## Décision

Utiliser **deux bases SQLite séparées** :

```
~/.mastoc/
├── stokt.db      # Données synchronisées depuis Stokt
├── railway.db    # Données synchronisées depuis Railway
└── pictos/       # Cache des pictos (partagé)
```

Le client bascule automatiquement vers la bonne base selon le `BackendSource` actif.

## Alternatives Considérées

| Option | Description | Rejetée car |
|--------|-------------|-------------|
| Une base, source active | Sync depuis Stokt OU Railway | Écrase les données |
| Une base unifiée | Merge avec champ `source` | Conflits complexes |

## Conséquences

### Positives
- Isolation totale des données
- Pas de risque de conflit ou d'écrasement
- Peut comparer les deux sources indépendamment
- Simple à implémenter

### Négatives
- Deux syncs à gérer
- Duplication potentielle de données (les mêmes climbs dans les deux)
- Changement de source = changement de contexte complet

## Implémentation

1. **Database** : Accepte un `db_path` paramétrable (déjà le cas)

2. **MastockApp** :
   - Détermine le path selon `BackendSource`
   - Recrée `Database`, `SyncManager`, `ClimbListWidget` lors du changement

3. **Paths** :
   ```python
   if source == BackendSource.STOKT:
       db_path = Path.home() / ".mastoc" / "stokt.db"
   else:
       db_path = Path.home() / ".mastoc" / "railway.db"
   ```

4. **SyncManager** :
   - Stokt : utilise `StoktAPI.get_gym_climbs()` (existant)
   - Railway : utilise `MastocAPI.get_all_climbs()` (à créer)
