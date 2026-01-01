# Architecture Decision Records (ADR)

Ce dossier contient les décisions architecturales du projet mastoc.

## Index des ADRs

| ADR | Titre | Statut |
|-----|-------|--------|
| [001](001_railway_first_architecture.md) | Architecture Railway-First avec Mapping d'IDs | Accepté |
| [002](002_api_key_authentication.md) | Authentification par API Key | Accepté |
| [003](003_stack_serveur.md) | Stack technique serveur (FastAPI + PostgreSQL) | Accepté |
| [004](004_client_pyqtgraph.md) | Client Python avec PyQtGraph + SQLite | Accepté |
| [005](005_batch_import.md) | Batch Import pour Holds, Users et Climbs | Accepté |
| [006](006_dual_sqlite_databases.md) | Deux Bases SQLite Séparées (Stokt + Railway) | Accepté |
| [007](007_incremental_sync.md) | Synchronisation Incrémentale | Accepté |
| [008](008_hold_annotations.md) | Hold Annotations (Annotations Crowd-Sourcées) | Accepté |
| [009](009_climb_rendering_system.md) | Système de Rendu des Blocs (Climb Rendering) | Accepté |

## Format ADR

Chaque ADR suit le format :

```markdown
# ADR XXX - Titre

**Date** : YYYY-MM-DD
**Statut** : Proposé | Accepté | Déprécié | Remplacé

## Contexte
[Situation qui nécessite une décision]

## Décision
[Ce qui a été décidé]

## Conséquences
[Impacts positifs et négatifs]

## Implémentation
[Détails techniques de l'implémentation]
```

## Références

- [ADR GitHub](https://adr.github.io/)
- [Michael Nygard - Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
