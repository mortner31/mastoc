# Start Here - mastoc

**Point d'entrée rapide pour comprendre le projet et commencer à travailler.**

## Qu'est-ce que mastoc ?

mastoc est un projet visant à créer une application personnelle pour visualiser et gérer des blocs d'escalade. Le projet part de l'analyse d'une application existante (Stokt) avec pour objectif de créer une version indépendante, offline-first, spécialisée sur la salle **Montoboard** (Caraman, France).

## Architecture actuelle

```
┌─────────────────────────────────────────────────────────────┐
│                        Railway                               │
│  ┌─────────────────────┐    ┌─────────────────────────────┐ │
│  │   mastoc-api        │    │      PostgreSQL             │ │
│  │   (FastAPI)         │───▶│   776 holds, ~1000 climbs   │ │
│  │   X-API-Key auth    │    │   ~50 users                 │ │
│  └─────────────────────┘    └─────────────────────────────┘ │
│  https://mastoc-production.up.railway.app                    │
└─────────────────────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│  Client mastoc (Python + PyQtGraph)                         │
│  - Visualisation des blocs                                  │
│  - Filtrage par grade, prises, setter                       │
│  - Création de nouveaux blocs                               │
└─────────────────────────────────────────────────────────────┘
```

## Serveur Railway (TODO 13 - COMPLET)

**URL** : https://mastoc-production.up.railway.app

### Endpoints principaux

| Endpoint | Description |
|----------|-------------|
| `/health` | Status serveur + DB |
| `/docs` | Swagger UI (documentation interactive) |
| `/api/climbs` | CRUD climbs |
| `/api/holds` | Liste holds |
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
| **14** | **Portage Client vers Railway** | **80% - EN COURS** |
| 15 | Sync Tool mastoc <-> Stokt | 0% - À faire |
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
| Climbs | ~1000 | Stokt → Railway |
| Users | ~50 | Stokt → Railway |

## Prochaines étapes

1. **TODO 14 (ACTIF)** : Portage client Python vers Railway
   - Créer `MastocAPI` (client Railway avec API Key)
   - Implémenter `BackendSwitch` (basculement Stokt/Railway)
   - Migrer les 18 fichiers GUI
2. **TODO 12** : Hold Annotations (tags crowd-sourcés pour les prises)
3. **Application mobile** : Porter le prototype vers React Native ou Flutter

---

**Dernière mise à jour** : 2025-12-31
**Statut du projet** : Serveur Railway déployé, portage client en cours (TODO 14)
