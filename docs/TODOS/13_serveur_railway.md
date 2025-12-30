# TODO 13 - Serveur Railway (mastoc-api)

## Objectif

Créer le backend FastAPI pour mastoc avec architecture Railway-First et mapping d'identifiants Stokt.

## Contexte

- Architecture documentée dans `docs/04_strategie_independance.md` (v3.0)
- Single-source sélectionnable (Railway par défaut)
- Mapping `stokt_id` nullable sur chaque entité
- Push/Import manuel vers Stokt

## Structure créée

```
server/
├── pyproject.toml              ✅ Créé
├── src/
│   └── mastoc_api/
│       ├── __init__.py         ✅ Créé
│       ├── config.py           ✅ Créé
│       ├── database.py         ✅ Créé
│       ├── main.py             ⏳ Interrompu
│       ├── models/
│       │   ├── __init__.py     ✅ Créé
│       │   ├── base.py         ✅ Créé
│       │   ├── gym.py          ✅ Créé
│       │   ├── face.py         ✅ Créé
│       │   ├── hold.py         ✅ Créé
│       │   ├── climb.py        ✅ Créé
│       │   ├── user.py         ✅ Créé
│       │   └── mapping.py      ✅ Créé
│       └── routers/
│           ├── __init__.py     ✅ Créé
│           ├── health.py       ✅ Créé
│           ├── climbs.py       ✅ Créé
│           ├── holds.py        ✅ Créé
│           └── sync.py         ✅ Créé
└── tests/
    └── (à créer)
```

## Tâches

### Phase 1 : Structure de base (90%)

- [x] Créer `pyproject.toml` avec dépendances FastAPI
- [x] Créer `config.py` (pydantic-settings)
- [x] Créer `database.py` (SQLAlchemy)
- [x] Créer modèles SQLAlchemy (Gym, Face, Hold, Climb, User, IdMapping)
- [x] Créer routers (health, climbs, holds, sync)
- [ ] Finaliser `main.py` (app FastAPI)
- [ ] Créer README.md serveur

### Phase 2 : Test local

- [ ] Installer dépendances (`pip install -e ".[dev]"`)
- [ ] Démarrer PostgreSQL local (Docker)
- [ ] Tester endpoints avec curl/httpie
- [ ] Vérifier création tables

### Phase 3 : Script d'import

- [ ] Créer `scripts/init_from_stokt.py`
- [ ] Importer gym Montoboard
- [ ] Importer faces et holds (776 prises)
- [ ] Importer climbs (~1000 blocs)
- [ ] Dupliquer images (CRITIQUE)

### Phase 4 : Déploiement Railway

- [ ] Créer projet Railway
- [ ] Configurer PostgreSQL
- [ ] Déployer l'API
- [ ] Tester en production

## Endpoints implémentés

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/health` | GET | Status serveur + DB |
| `/api/climbs` | GET | Liste climbs (filtres, pagination) |
| `/api/climbs/{id}` | GET | Détail climb |
| `/api/climbs/by-stokt-id/{id}` | GET | Climb par stokt_id |
| `/api/climbs` | POST | Créer climb |
| `/api/climbs/{id}` | PATCH | Modifier climb |
| `/api/climbs/{id}` | DELETE | Supprimer climb |
| `/api/climbs/{id}/stokt-id` | PATCH | MAJ stokt_id (après push) |
| `/api/holds` | GET | Liste holds d'une face |
| `/api/holds/{id}` | GET | Détail hold |
| `/api/sync/stats` | GET | Stats de la base |
| `/api/sync/import/gym` | POST | Import gym Stokt |
| `/api/sync/import/face` | POST | Import face Stokt |
| `/api/sync/import/hold` | POST | Import hold Stokt |
| `/api/sync/import/climb` | POST | Import climb Stokt |
| `/api/sync/import/user` | POST | Import user Stokt |

## Modèles avec mapping

Chaque modèle a un champ `stokt_id` nullable :

```python
class Climb(Base):
    id: UUID              # ID mastoc (toujours présent)
    stokt_id: UUID | None # ID Stokt (NULL si créé sur mastoc)
    # ... autres champs
```

## Références

- `docs/04_strategie_independance.md` - Architecture Railway-First
- `docs/devplan/02_SHORT_TERM.md` - Plan court terme
- `mastoc/src/mastoc/api/client.py` - Client Stokt existant
