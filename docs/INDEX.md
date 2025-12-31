# Index de la Documentation - mastoc

Ce fichier recense toute la documentation du projet mastoc.

## 🏗️ ADRs (Architecture Decision Records)

**IMPORTANT** : Les ADRs documentent les décisions architecturales majeures. Toujours les consulter avant de modifier l'architecture.

| ADR | Titre | Résumé |
|-----|-------|--------|
| [001](adr/001_railway_first_architecture.md) | Railway-First avec Mapping | IDs mastoc + stokt_id nullable |
| [002](adr/002_api_key_authentication.md) | Auth API Key | Header X-API-Key sur /api/* |
| [003](adr/003_stack_serveur.md) | Stack serveur | FastAPI + SQLAlchemy + PostgreSQL |
| [004](adr/004_client_pyqtgraph.md) | Client Python | PyQtGraph + PySide6 + SQLite |
| [005](adr/005_batch_import.md) | Batch Import | Endpoints /batch pour import rapide |

Voir `/docs/adr/README.md` pour le format et créer de nouveaux ADRs.

## 🖥️ Serveur Railway

**URL Production** : https://mastoc-production.up.railway.app

| Ressource | URL |
|-----------|-----|
| Swagger UI | `/docs` |
| Health Check | `/health` |
| Stats | `/api/sync/stats` (auth requise) |

Documentation serveur : `/server/README.md`

## 📋 Fichiers Système

- `INDEX.md` - Ce fichier (index de la documentation)
- `TIMELINE.md` - Historique chronologique du projet

## 📂 TODOs Actifs

| ID | Nom | Statut |
|----|-----|--------|
| 13 | Serveur Railway | **100%** |
| 12 | Hold Annotations | 0% |
| 11 | Principes Ergonomie UI/UX | 100% |
| 10 | Creation de Blocs | 97% (archivé) |
| 09 | Listes Personnalisees | 60% |
| 07 | Interactions Blocs | 100% |

Voir `/docs/TODOS/` pour les details.

## 📊 Rapports

Les rapports de sessions sont dans `/docs/reports/`.

| Date | Description |
|------|-------------|
| 2025-12-30 | Serveur Railway complet + import Stokt |
| 2025-12-22 | Améliorations UI (filtres, pictos, viewer) |

## 📚 Documentation Technique

| Fichier | Description |
|---------|-------------|
| `01_architecture.md` | Architecture du projet mastoc |
| `02_design_decisions.md` | Decisions de design (UI, pictos, couleurs) |
| `03_ergonomie_ui_ux.md` | Guide d'ergonomie Android (Material Design 3) |
| `04_strategie_independance.md` | **Stratégie d'indépendance Stokt** |
| `05_theme_design_system.md` | Theme et Design System |
| `backend_spec.md` | Spécification API backend |

## 📅 Plan de Développement

Le plan de développement est dans `/docs/devplan/`.

## 🗃️ Archive

Les TODOs complétés et documents obsolètes sont dans `/archive/`.

---

**Dernière mise à jour** : 2025-12-30
