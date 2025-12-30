# STATUS - TODO 13 : Serveur Railway

**Progression** : 100%

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
- [x] Endpoints batch (holds, users, climbs)
- [x] Cache local pour éviter re-téléchargement
- [ ] Duplication images (reporté - optionnel)

## Phase 4 : Tests (100%)

- [x] conftest.py (fixtures SQLite en mémoire)
- [x] test_health.py (2 tests)
- [x] test_sync.py (8 tests)
- [x] test_climbs.py (7 tests)
- [x] test_auth.py (11 tests)

## Phase 5 : Authentification (100%)

- [x] auth.py (API Key verification)
- [x] Endpoints /api/* protégés
- [x] /health, /docs, /redoc publics
- [x] Mode dev (sans API_KEY = pas d'auth)
- [x] API_KEY configurée sur Railway

## Phase 6 : Documentation (100%)

- [x] ADRs créés (5 ADRs dans docs/adr/)
- [x] Rapport de session complet
- [x] README serveur

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
| `/api/sync/import/*/batch` | Import batch (holds, users, climbs) |
| `/api/climbs` | CRUD climbs |
| `/api/holds` | Liste holds |

## Données importées

| Entité | Quantité |
|--------|----------|
| Gyms | 1 |
| Faces | 1 |
| Holds | 776 |
| Climbs | ~1000 |
| Users | ~50 |

## Notes

### Session 2025-12-30 (suite)

**Import complet réussi :**
- Endpoints batch implémentés (10x plus rapide)
- Import des données Stokt terminé
- ADRs documentant l'architecture
- Cache local pour éviter les appels répétés à Stokt

**Options du script :**
```bash
# Import complet
python scripts/init_from_stokt.py --username USER --password PASS --api-key KEY

# Sauvegarder en cache
python scripts/init_from_stokt.py ... --save-cache

# Utiliser le cache (pas d'appels Stokt)
python scripts/init_from_stokt.py --api-key KEY --use-cache --climbs-only
```

### TODO terminé

Ce TODO est complet. L'intégration client sera un nouveau TODO séparé.
