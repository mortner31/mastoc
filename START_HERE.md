# Start Here - mastoc

**Point d'entrée rapide pour comprendre le projet et commencer à travailler.**

## Qu'est-ce que mastoc ?

mastoc est un projet visant à créer une application personnelle pour visualiser et gérer des blocs d'escalade. Le projet part de l'analyse d'une application existante (Stokt) avec pour objectif de créer une version indépendante, offline-first, spécialisée sur la salle **Montoboard** (Caraman, France).

## Architecture actuelle (ADR-006)

```
┌─────────────────────────────────────────────────────────────┐
│                        Railway                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   mastoc-api        │    │      PostgreSQL             │ │
│  │   (FastAPI)         │───▶│   776 holds, 1012 climbs    │ │
│  │   X-API-Key auth    │    │   79 users                  │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
│  https://mastoc-production.up.railway.app                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ sync
┌──────────────────────▼──────────────────────────────────────┐
│  Client mastoc (Python + PyQtGraph)                         │
│  - BackendSwitch : basculement Stokt / Railway              │
│  - Deux bases SQLite séparées (ADR-006) :                   │
│    ~/.mastoc/stokt.db   ← sync depuis Stokt                 │
│    ~/.mastoc/railway.db ← sync depuis Railway               │
│  - Visualisation, filtrage, création de blocs               │
└─────────────────────────────────────────────────────────────┘
```

## Serveur Railway (TODO 13 - COMPLET)

**URL** : https://mastoc-production.up.railway.app

### Endpoints principaux

| Endpoint | Description |
|----------|-------------|
| `/health` | Status serveur + DB |
| `/docs` | Swagger UI (documentation interactive) |
| `/api/climbs` | CRUD climbs (GET, POST, PATCH, DELETE) |
| `/api/holds` | Liste holds |
| `/api/faces` | Liste faces |
| `/api/faces/{id}/setup` | Face avec tous ses holds |
| `/api/sync/stats` | Statistiques de la base |
| `/api/sync/import/*` | Import depuis Stokt |

### Script d'import

```bash
cd server
python scripts/init_from_stokt.py \
  --username USER --password PASS \
  --api-key "mastoc-2025-1213-brosse-lesprises-secret"

# Options utiles :
--save-cache     # Sauvegarde les données en cache local
--use-cache      # Utilise le cache (évite appels Stokt)
--climbs-only    # Skip gym/faces/holds
--batch-size 50  # Taille des lots
```

## Client Python

### 1. Application principale

```bash
cd mastoc
python -m mastoc.gui.app
```

### 2. Sélecteur par prises

```bash
python -m mastoc.gui.hold_selector
```

### 3. Création de bloc

```bash
python -m mastoc.gui.creation_app
```

## TODOs

| TODO | Description | Statut |
|------|-------------|--------|
| **15** | **Sync Incrémentale (Optimisation)** | **90% - EN COURS** |
| **16** | **Tableau de Bord Sync** | **0% - PLANIFIÉ** |
| **17** | **Authentification & Users mastoc** | **0% - PLANIFIÉ** |
| **18** | **Sync Données Sociales** | **0% - PLANIFIÉ** |
| 14 | Portage Client vers Railway | 100% - ARCHIVÉ |
| 13 | Serveur Railway mastoc-api | 100% - COMPLET |
| 12 | Hold Annotations | 0% - À faire |
| 09 | Listes Personnalisées | 70% - API OK |

## Documentation clé

### ADRs (Architecture Decision Records)

| ADR | Titre |
|-----|-------|
| [001](docs/adr/001_railway_first_architecture.md) | Architecture Railway-First avec Mapping d'IDs |
| [002](docs/adr/002_api_key_authentication.md) | Authentification par API Key |
| [003](docs/adr/003_stack_serveur.md) | Stack serveur (FastAPI + PostgreSQL) |
| [004](docs/adr/004_client_pyqtgraph.md) | Client PyQtGraph + SQLite |
| [005](docs/adr/005_batch_import.md) | Batch Import pour Holds, Users et Climbs |
| [006](docs/adr/006_dual_sqlite_databases.md) | Deux Bases SQLite Séparées (Stokt + Railway) |

### Autres documents

- `/docs/TIMELINE.md` - Historique chronologique complet
- `/docs/TODOS/13_serveur_railway_STATUS.md` - Statut serveur Railway
- `/docs/04_strategie_independance.md` - Stratégie d'indépendance Stokt
- `/docs/reports/` - Rapports de session

## Données

| Entité | Quantité | Source |
|--------|----------|--------|
| Gyms | 1 | Stokt → Railway |
| Faces | 1 | Stokt → Railway |
| Holds | 776 | Stokt → Railway |
| Climbs | 1012 | Stokt → Railway |
| Users | 79 | Stokt → Railway |

## Prochaines étapes

1. **TODO 15** : Sync Incrémentale (90% - finir documentation)
   - ✅ Phase 1-4 : Complétées
   - ⏳ Phase 5 : Documentation (optionnel)
2. **TODO 16** : Tableau de Bord Sync
   - Dashboard stats (climbs sync vs locaux)
   - CLI + intégration GUI
3. **TODO 17** : Authentification & Users mastoc
   - Email/password + JWT
   - Rôles User/Admin
4. **TODO 18** : Sync Données Sociales
   - Refresh compteurs (climbed_by, likes, comments)
   - Détection changements non captés par sync incrémentale
5. **TODO 12** : Hold Annotations (tags crowd-sourcés pour les prises)

---

**Dernière mise à jour** : 2025-12-31
**Statut du projet** : TODO 15 EN COURS (90%), TODO 16 simplifié, TODO 18 créé
