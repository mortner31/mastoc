# STATUS - TODO 13 : Serveur Railway

**Progression** : 85%

---

## Phase 1 : Structure de base (100%)

- [x] pyproject.toml
- [x] config.py
- [x] database.py
- [x] Modèles SQLAlchemy (7 fichiers)
- [x] Routers (4 fichiers)
- [x] main.py
- [x] README.md

## Phase 2 : Déploiement Railway (100%)

- [x] Projet Railway connecté au repo GitHub
- [x] PostgreSQL Railway configuré
- [x] Variable DATABASE_URL partagée
- [x] Domaine public généré (port 8080)
- [x] API en ligne et fonctionnelle

## Phase 3 : Script d'import (100%)

- [x] init_from_stokt.py créé
- [x] Import gym Montoboard
- [x] Import faces et holds (776 prises)
- [x] Import climbs (~1000 blocs)
- [ ] Duplication images (reporté)

## Phase 4 : Tests (100%)

- [x] conftest.py (fixtures SQLite en mémoire)
- [x] test_health.py (2 tests)
- [x] test_sync.py (8 tests)
- [x] test_climbs.py (7 tests)

## Phase 5 : Intégration client (0%)

- [ ] Modifier client mastoc pour utiliser Railway
- [ ] Tests end-to-end

---

## URL Production

https://mastoc-production.up.railway.app

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `/health` | Status serveur + DB |
| `/docs` | Swagger UI |
| `/api/sync/stats` | Statistiques de la base |
| `/api/sync/import/*` | Import depuis Stokt |
| `/api/climbs` | CRUD climbs |
| `/api/holds` | Liste holds |

## Notes

### Session 2025-12-30

**Travail effectué :**
- Finalisation main.py (app FastAPI)
- Création README serveur avec doc Railway complète
- Création Procfile + requirements.txt
- Déploiement Railway réussi
- PostgreSQL connecté et fonctionnel
- Script d'import `init_from_stokt.py`
- Suite de tests (17 tests)

**Problèmes résolus :**
- `uvicorn: command not found` → ajout requirements.txt
- Module non trouvé → ajout PYTHONPATH=src dans Procfile
- 404 sur import/gym → correction endpoint (JSON body au lieu de query params)
- Double prefix `/api/api` → correction des routers

### Prochaine session

1. Vérifier import complet
2. Mettre à jour client mastoc pour utiliser Railway
3. Tests end-to-end
