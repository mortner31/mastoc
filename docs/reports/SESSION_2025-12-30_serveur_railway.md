# Rapport de Session - Serveur Railway

**Date** : 2025-12-30

## Objectifs de la session

1. ✅ Mettre à jour la stratégie d'indépendance (Railway-First)
2. ✅ Archiver TODO 10 (création de blocs)
3. ⏳ Créer le serveur Railway (interrompu à 90%)

## Travail effectué

### 1. Architecture Railway-First avec Mapping

Refonte complète de `docs/04_strategie_independance.md` (v3.0) :

- **Single-source sélectionnable** : Railway par défaut, Stokt optionnel
- **Mapping stokt_id** nullable sur chaque entité
- **Push/Import manuel** (pas de sync auto)
- **BackendSwitch** remplace DataSourceManager

Documents mis à jour :
- `docs/04_strategie_independance.md`
- `docs/devplan/00_OVERVIEW.md`
- `docs/devplan/02_SHORT_TERM.md`
- `docs/devplan/05_ARCHITECTURE.md` (ADR-005)

### 2. Archivage TODO 10

TODO 10 (Interface de Création de Blocs) archivé à 97% :
- Premier bloc créé avec succès via mastoc
- API création fonctionnelle
- 3 tâches polish reportées

Fichiers déplacés vers `/archive/TODOS/`

### 3. Structure Serveur Railway

Création de la structure FastAPI dans `server/` :

```
server/
├── pyproject.toml              ✅
├── src/mastoc_api/
│   ├── __init__.py             ✅
│   ├── config.py               ✅
│   ├── database.py             ✅
│   ├── main.py                 ⏳ (interrompu)
│   ├── models/                 ✅ (7 fichiers)
│   │   ├── base.py
│   │   ├── gym.py
│   │   ├── face.py
│   │   ├── hold.py
│   │   ├── climb.py
│   │   ├── user.py
│   │   └── mapping.py
│   └── routers/                ✅ (4 fichiers)
│       ├── health.py
│       ├── climbs.py
│       ├── holds.py
│       └── sync.py
```

**Fonctionnalités implémentées :**
- CRUD complet pour climbs
- Endpoints de synchronisation Stokt
- Mapping stokt_id sur tous les modèles
- Configuration via variables d'environnement

## État des commits

```
2856251 docs: Architecture Railway-First avec Mapping d'IDs
```

Fichiers non commités :
- `server/` (nouvelle structure)
- `docs/TODOS/13_serveur_railway*.md`
- `docs/TIMELINE.md` (mise à jour)
- `archive/TODOS/10_creation_blocs*.md`

## Prochaines étapes

### Priorité 1 : Finaliser serveur

1. Terminer `main.py` (app FastAPI)
2. Créer README serveur
3. Tester localement :
   ```bash
   cd server
   pip install -e ".[dev]"
   docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
   uvicorn mastoc_api.main:app --reload
   ```

### Priorité 2 : Script d'import

1. Créer `scripts/init_from_stokt.py`
2. Importer données Montoboard (776 prises, ~1000 blocs)
3. Dupliquer images (CRITIQUE)

### Priorité 3 : Déploiement

1. Créer projet Railway
2. Configurer PostgreSQL
3. Déployer et tester

## Commande pour reprendre

```bash
# Voir l'état
cat docs/TODOS/13_serveur_railway_STATUS.md

# Fichier à terminer
code server/src/mastoc_api/main.py
```

## Risques identifiés

- PostgreSQL local nécessaire pour tester
- Images Stokt à dupliquer (volume important)
- Rate limiting Stokt lors de l'import initial
