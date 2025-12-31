# État Actuel du Projet mastoc

**Date** : 2025-12-31
**Dernière mise à jour** : Refonte complète post-TODO 14

---

## 1. Architecture du code

### Structure du package Python (Client)

```
mastoc/
├── pyproject.toml              # Configuration package
├── src/mastoc/
│   ├── api/                    # Communication API
│   │   ├── client.py           # Client HTTP Stokt
│   │   ├── railway_client.py   # Client HTTP Railway (NEW)
│   │   └── models.py           # Dataclasses
│   ├── core/                   # Logique métier
│   │   ├── backend.py          # BackendSwitch + BackendSource (NEW)
│   │   ├── config.py           # Config persistante ~/.mastoc/config.json (NEW)
│   │   ├── assets.py           # Cache d'assets/images (NEW)
│   │   ├── sync.py             # SyncManager + RailwaySyncManager
│   │   ├── colormaps.py        # Palettes de couleurs heatmaps
│   │   ├── filters.py          # Filtres par grade, setter
│   │   ├── hold_index.py       # Index prises ↔ blocs
│   │   ├── picto.py            # Génération pictos
│   │   ├── picto_cache.py      # Cache disque des miniatures
│   │   ├── social_actions.py   # Actions like/bookmark/send
│   │   └── social_loader.py    # Chargement async
│   ├── db/                     # Persistance
│   │   ├── database.py         # Connexion SQLite
│   │   └── repository.py       # CRUD climbs/holds
│   └── gui/                    # Interface graphique
│       ├── app.py              # Application principale
│       ├── climb_viewer.py     # Visualiseur bloc
│       ├── hold_selector.py    # Sélection par prises
│       ├── creation_app.py     # Point d'entrée création
│       ├── creation/           # Module création de blocs
│       │   ├── controller.py   # Navigation wizard
│       │   ├── wizard.py       # Fenêtre principale
│       │   └── screens/
│       │       ├── select_holds.py
│       │       └── climb_info.py
│       ├── widgets/
│       │   ├── climb_detail.py
│       │   ├── climb_list.py
│       │   ├── hold_overlay.py # Overlay pyqtgraph
│       │   ├── social_panel.py
│       │   └── ...
│       └── dialogs/
│           └── login.py        # Dialog authentification Stokt
└── tests/                      # 301 tests
```

### Structure du serveur (Railway)

```
server/
├── pyproject.toml
├── requirements.txt            # Pour Railway
├── Procfile                    # Commande de démarrage
├── src/mastoc_api/
│   ├── main.py                 # App FastAPI
│   ├── config.py               # Pydantic Settings
│   ├── database.py             # SQLAlchemy engine/session
│   ├── auth.py                 # API Key auth
│   ├── models/                 # SQLAlchemy models
│   │   ├── gym.py
│   │   ├── face.py
│   │   ├── hold.py
│   │   ├── climb.py
│   │   ├── user.py
│   │   └── mapping.py          # IdMapping Stokt ↔ Railway
│   └── routers/
│       ├── health.py
│       ├── climbs.py
│       ├── holds.py
│       ├── faces.py
│       └── sync.py             # Import batch depuis Stokt
└── tests/
```

### Métriques de code

| Module | Lignes | Tests | Couverture |
|--------|--------|-------|------------|
| api/ | ~1 400 | 60 | Complète |
| core/ | ~2 200 | 100 | Complète |
| db/ | ~500 | 40 | Complète |
| gui/ | ~5 000 | 70 | Partielle (UI) |
| server/ | ~1 500 | 31 | Complète |
| **Total** | ~12 000 | **301** | ~85% |

---

## 2. Infrastructure déployée

### Serveur Railway (mastoc-api)

| Élément | Valeur |
|---------|--------|
| URL | https://mastoc-production.up.railway.app |
| Stack | FastAPI + PostgreSQL |
| Auth | API Key (`X-API-Key` header) |
| Endpoints | /health, /api/climbs, /api/holds, /api/faces, /api/sync |

### Données Railway

| Table | Enregistrements |
|-------|-----------------|
| climbs | 1012 |
| holds | 776 |
| faces | 1 |
| users | 79 |
| gyms | 1 |

### Client - Bases SQLite (ADR-006)

| Base | Emplacement | Contenu |
|------|-------------|---------|
| `stokt.db` | `~/.mastoc/stokt.db` | Sync depuis Stokt |
| `railway.db` | `~/.mastoc/railway.db` | Sync depuis Railway |

---

## 3. Fonctionnalités implémentées

### 3.1 API Client

| Fonctionnalité | Stokt | Railway | Statut |
|----------------|-------|---------|--------|
| Authentification | Token | API Key | OK |
| Liste climbs | GET | GET | OK |
| Détail climb | GET | GET | OK |
| Création climb | POST | POST | OK |
| Setup face | GET | GET | OK |
| Interactions sociales | GET | — | OK |

### 3.2 Interface graphique

| Application | Description | Statut |
|-------------|-------------|--------|
| `app.py` | Liste principale + visualisation | OK |
| `hold_selector.py` | Recherche par prises | OK |
| `creation_app.py` | Wizard création bloc | OK |
| `climb_viewer.py` | Visualisation standalone | OK |

### 3.3 Backend Switch (ADR-006)

| Feature | Description | Statut |
|---------|-------------|--------|
| BackendSource | Enum STOKT / RAILWAY | OK |
| BackendSwitch | Basculement dynamique | OK |
| Dual SQLite | Deux bases séparées | OK |
| Config persistante | `~/.mastoc/config.json` | OK |
| Menu source | UI pour changer de source | OK |

### 3.4 Visualisation

| Feature | Description | Statut |
|---------|-------------|--------|
| Image haute résolution | 2263x3000 pixels | OK |
| Polygones des prises | Contours colorés | OK |
| Marqueurs START | Lignes tape (V ou centrale) | OK |
| Marqueurs TOP | Double polygone 135% | OK |
| Marqueurs FEET | Contour cyan | OK |
| Heatmaps | 7 palettes + 4 modes | OK |
| Pictos (miniatures) | Cache disque | OK |

---

## 4. ADRs (Architecture Decision Records)

| ADR | Titre | Statut |
|-----|-------|--------|
| 001 | Architecture Railway-First avec Mapping d'IDs | Accepté |
| 002 | Authentification par API Key | Accepté |
| 003 | Stack serveur (FastAPI + PostgreSQL) | Accepté |
| 004 | Client PyQtGraph + SQLite | Accepté |
| 005 | Batch Import pour Holds, Users et Climbs | Accepté |
| 006 | Deux Bases SQLite Séparées (Stokt + Railway) | Accepté |

---

## 5. TODOs et progression

### TODOs terminés (archivés)

| TODO | Description | Date archivage |
|------|-------------|----------------|
| 01-08 | Analyse, extraction, package, UI | 2025-12-22 |
| 10 | Interface Création Blocs | 2025-12-30 |
| 11 | Ergonomie UI/UX | 2025-12-22 |
| 13 | Serveur Railway | 2025-12-30 |
| 14 | Portage Client Railway | 2025-12-31 |

### TODOs en cours

| TODO | Description | Progression | Prochaine action |
|------|-------------|-------------|------------------|
| 09 | Listes personnalisées | 70% | UI client |
| 12 | Hold Annotations | 0% | Nécessite serveur |
| 15 | Sync Incrémentale | 0% | Quick win max_age Stokt |
| 16 | Sync Tool mastoc ↔ Stokt | 0% | DiffEngine |
| 17 | Authentification & Users | 0% | Phase 1 serveur |

---

## 6. Dépendances

### Client Python

```toml
dependencies = [
    "PyQt6>=6.6.0",
    "pyqtgraph>=0.13.0",
    "requests>=2.31.0",
    "Pillow>=10.0.0",
    "python-dotenv>=1.0.0",
]
```

### Serveur

```
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pydantic-settings>=2.1.0
```

---

## 7. Points forts

1. **Architecture modulaire** : Séparation claire api/core/db/gui + serveur
2. **Tests solides** : 301 tests, couverture >85%
3. **Documentation** : 6 ADRs, TODOs structurés, timeline complète
4. **Offline-first** : Toutes les données en local (dual SQLite)
5. **Indépendance Stokt** : Serveur Railway fonctionnel, BackendSwitch
6. **Performance** : Chargement rapide, cache pictos et assets

---

## 8. Points d'amélioration

1. **Sync inefficace** : Télécharge tout à chaque sync (TODO 15)
2. **Pas d'auth utilisateur** : API Key partagée (TODO 17)
3. **UI Python** : PyQt6 n'est pas idéal pour mobile
4. **Pas d'export** : Données non portables

---

## 9. Risques identifiés

| Risque | Probabilité | Impact | Mitigation |
|--------|-------------|--------|------------|
| API Stokt change | Moyenne | Moyen | Serveur Railway (backup) |
| Ban compte Stokt | Faible | Moyen | Données déjà sur Railway |
| Railway pricing | Faible | Faible | Migration possible vers VPS |
| Perte données locales | Faible | Moyen | Sync Railway = backup |

---

*Document mis à jour le 2025-12-31*
