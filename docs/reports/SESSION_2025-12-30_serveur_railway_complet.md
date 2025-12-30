# Rapport de Session - Serveur Railway mastoc-api (Complet)

**Date** : 2025-12-30

## Objectifs Atteints

- [x] Finalisation du serveur FastAPI
- [x] Déploiement sur Railway avec PostgreSQL
- [x] Script d'import des données Stokt
- [x] Suite de tests (28 tests)
- [x] Authentification par API Key
- [x] Documentation complète

## Résumé

Cette session a permis de déployer le backend mastoc-api sur Railway avec une architecture Railway-First. L'API est maintenant en production, sécurisée par API Key, et prête à recevoir les données Stokt.

---

## 1. Structure du Serveur

### Fichiers créés

```
server/
├── pyproject.toml              # Config Python
├── requirements.txt            # Dépendances (pour Railway)
├── Procfile                    # Commande de démarrage Railway
├── README.md                   # Documentation complète
├── .env.example                # Template de configuration
├── src/
│   └── mastoc_api/
│       ├── __init__.py
│       ├── config.py           # Settings pydantic
│       ├── database.py         # SQLAlchemy
│       ├── auth.py             # API Key authentication
│       ├── main.py             # App FastAPI
│       ├── models/             # 7 modèles SQLAlchemy
│       │   ├── base.py         # DataSource enum
│       │   ├── gym.py          # Salle d'escalade
│       │   ├── face.py         # Face de mur
│       │   ├── hold.py         # Prise
│       │   ├── climb.py        # Bloc
│       │   ├── user.py         # Utilisateur
│       │   └── mapping.py      # Mapping IDs Stokt
│       └── routers/            # 4 routers
│           ├── health.py       # /health, /
│           ├── climbs.py       # /api/climbs
│           ├── holds.py        # /api/holds
│           └── sync.py         # /api/sync
├── scripts/
│   └── init_from_stokt.py      # Import données Stokt
└── tests/
    ├── conftest.py             # Fixtures SQLite
    ├── test_health.py          # 2 tests
    ├── test_sync.py            # 8 tests
    ├── test_climbs.py          # 7 tests
    └── test_auth.py            # 11 tests
```

### Endpoints

| Endpoint | Méthode | Auth | Description |
|----------|---------|------|-------------|
| `/` | GET | Non | Info API |
| `/health` | GET | Non | Status serveur + DB |
| `/docs` | GET | Non | Swagger UI |
| `/api/climbs` | GET | Oui | Liste climbs (filtres, pagination) |
| `/api/climbs/{id}` | GET | Oui | Détail climb |
| `/api/climbs` | POST | Oui | Créer climb |
| `/api/climbs/{id}` | PATCH | Oui | Modifier climb |
| `/api/climbs/{id}` | DELETE | Oui | Supprimer climb |
| `/api/holds` | GET | Oui | Liste holds d'une face |
| `/api/sync/stats` | GET | Oui | Statistiques de la base |
| `/api/sync/import/*` | POST | Oui | Import depuis Stokt |

---

## 2. Déploiement Railway

### Configuration

1. **Projet Railway** connecté au repo GitHub `mortner31/mastoc`
2. **Root Directory** : `server`
3. **PostgreSQL** ajouté comme service
4. **Variables d'environnement** :
   - `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
   - `API_KEY` = `mastoc-2025-1213-brosse-lesprises-secret`
5. **Domaine public** : `mastoc-production.up.railway.app` (port 8080)

### URL Production

https://mastoc-production.up.railway.app

---

## 3. Authentification

### Implémentation

- Header requis : `X-API-Key`
- Endpoints publics : `/health`, `/docs`, `/redoc`
- Endpoints protégés : `/api/*`
- Mode dev : sans `API_KEY` configurée, pas d'auth

### Utilisation

```bash
# Sans auth (401)
curl https://mastoc-production.up.railway.app/api/climbs

# Avec auth (200)
curl -H "X-API-Key: mastoc-2025-1213-brosse-lesprises-secret" \
  https://mastoc-production.up.railway.app/api/climbs
```

---

## 4. Script d'Import

### Usage

```bash
python scripts/init_from_stokt.py \
  --username USER \
  --password PASS \
  --api-key "mastoc-2025-1213-brosse-lesprises-secret"
```

### Fonctionnalités

- Connexion à l'API Stokt
- Import gym Montoboard
- Import faces et holds (776 prises)
- Import climbs (~1000 blocs)
- Import users (setters)
- Support `--dry-run` pour test

---

## 5. Tests

### Couverture

| Fichier | Tests | Description |
|---------|-------|-------------|
| test_health.py | 2 | Endpoints publics |
| test_sync.py | 8 | Import gym/face/hold/climb/user |
| test_climbs.py | 7 | CRUD climbs |
| test_auth.py | 11 | Authentification API Key |
| **Total** | **28** | |

### Fixtures

- SQLite en mémoire pour isolation
- Client avec/sans API Key
- Reset DB entre chaque test

---

## 6. Problèmes Résolus

| Problème | Cause | Solution |
|----------|-------|----------|
| `uvicorn: command not found` | Railway ne lit pas pyproject.toml | Ajout `requirements.txt` |
| Module mastoc_api non trouvé | PYTHONPATH manquant | `PYTHONPATH=src` dans Procfile |
| 404 sur `/api/sync/import/gym` | Query params au lieu de JSON | Refactoring en Pydantic BaseModel |
| Double prefix `/api/api/` | Prefix dupliqué dans routers | Retrait `/api` des routers |
| API publique sans auth | Pas d'authentification | Ajout API Key |

---

## 7. État de l'Import

### Avant relance

```json
{
  "gyms": 1,
  "faces": 1,
  "holds": 176,
  "climbs": 0,
  "users": 0
}
```

L'import a été interrompu lors d'un redéploiement. À relancer avec l'API Key.

---

## 8. Commits de la Session

| Hash | Message |
|------|---------|
| `1783584` | feat: TODO 13 - Serveur FastAPI mastoc-api (Phase 1 complète) |
| `ab0e336` | fix: requirements.txt et PYTHONPATH pour Railway |
| `48314b8` | docs: Rapport session déploiement Railway + mise à jour STATUS |
| `5f90434` | feat: Script d'import Stokt + tests serveur |
| `22dc369` | fix: Endpoint import/gym utilise JSON body |
| `c0c97e0` | fix: Corrige double prefix /api/api → /api |
| `6321f23` | docs: Mise à jour STATUS TODO 13 (85%) et TIMELINE |
| `a63eb0b` | feat: Authentification par API Key |

---

## 9. Prochaines Étapes

1. **Relancer l'import complet** avec API Key
2. **Vérifier les données** importées (776 holds, ~1000 climbs)
3. **Modifier le client mastoc** pour utiliser Railway comme backend
4. **Tests end-to-end** client ↔ serveur
5. **Duplication des images** (optionnel, pour indépendance totale)

---

## Architecture Finale

```
┌─────────────────────────────────────────────────────────────┐
│                        Railway                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   mastoc-api        │    │      PostgreSQL             │ │
│  │   (FastAPI)         │───▶│   - gyms                    │ │
│  │                     │    │   - faces                   │ │
│  │ X-API-Key required  │    │   - holds                   │ │
│  └─────────────────────┘    │   - climbs                  │ │
│           │                  │   - users                   │ │
│           │                  │   - id_mappings             │ │
│           ▼                  └─────────────────────────────┘ │
│  mastoc-production.up.railway.app                            │
└─────────────────────────────────────────────────────────────┘
           │
           │ HTTPS + API Key
           ▼
┌─────────────────────────────────────────────────────────────┐
│  Client (mastoc GUI / future app mobile)                    │
│  - Lecture climbs, holds, faces                             │
│  - Création/modification de blocs                           │
│  - Sync avec Stokt (optionnel)                              │
└─────────────────────────────────────────────────────────────┘
```
