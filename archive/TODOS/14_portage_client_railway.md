# TODO 14 - Portage Client Python vers Railway

## Objectif

Migrer le client Python mastoc de l'API Stokt (`sostokt.com`) vers le serveur Railway (`mastoc-production.up.railway.app`) pour atteindre l'indépendance complète.

## Contexte

**État actuel :**
- Le client utilise `StoktAPI` qui pointe vers `sostokt.com`
- 18 fichiers dépendent de cette API
- Le serveur Railway est déployé avec 776 holds, ~1000 climbs, ~50 users

**Objectif final :**
- Le client utilise uniquement mastoc-api (Railway)
- Stokt devient optionnel (sync ponctuelle)
- Données locales SQLite synchronisées avec Railway

## Architecture Cible

```
┌─────────────────────────────────────────────────────────┐
│  Client mastoc (Python)                                 │
│  ┌─────────────────┐    ┌─────────────────────────────┐ │
│  │  MastocAPI      │───▶│  Railway (mastoc-api)       │ │
│  │  (nouveau)      │    │  Source principale          │ │
│  └─────────────────┘    └─────────────────────────────┘ │
│           │                                             │
│           ▼                                             │
│  ┌─────────────────┐                                    │
│  │  SQLite local   │  Cache offline                     │
│  └─────────────────┘                                    │
└─────────────────────────────────────────────────────────┘
                    │
                    ▼ (sync occasionnelle)
┌─────────────────────────────────────────────────────────┐
│  Stokt (sostokt.com) - Source upstream                  │
└─────────────────────────────────────────────────────────┘
```

## Tâches

### Phase 1 : Client API Railway

- [ ] Créer `mastoc/api/railway_client.py` (MastocAPI)
- [ ] Implémenter authentification API Key
- [ ] Endpoint GET /api/climbs (liste paginée)
- [ ] Endpoint GET /api/climbs/{id}
- [ ] Endpoint GET /api/holds
- [ ] Tests unitaires MastocAPI

### Phase 2 : Backend Switch

- [ ] Créer `mastoc/core/backend.py` (BackendSwitch)
- [ ] Interface commune pour Stokt et Railway
- [ ] Configuration dans settings (source: "railway" | "stokt")
- [ ] Fallback automatique si Railway indisponible

### Phase 3 : Migration GUI

- [ ] Adapter `app.py` pour utiliser BackendSwitch
- [ ] Adapter `hold_selector.py`
- [ ] Adapter `creation_app.py`
- [ ] Adapter dialogs de connexion (API Key vs login Stokt)
- [ ] Tester toutes les fonctionnalités

### Phase 4 : Endpoints Manquants sur Railway

Certains endpoints n'existent pas encore sur Railway :

- [ ] GET /api/faces/{id}/setup (holds avec polygones)
- [ ] POST /api/climbs (création de bloc)
- [ ] Endpoints social (sends, comments, likes) - optionnel
- [ ] Endpoints listes - optionnel

### Phase 5 : Sync Bidirectionnelle

- [ ] Script de sync Railway → SQLite local
- [ ] Détection de conflits
- [ ] Mode offline complet

## Fichiers Impactés

```
mastoc/src/mastoc/api/
├── client.py          → garder pour Stokt (legacy)
├── railway_client.py  → NOUVEAU (MastocAPI)
└── __init__.py        → exporter les deux

mastoc/src/mastoc/core/
├── backend.py         → NOUVEAU (BackendSwitch)
└── sync.py            → adapter pour Railway

mastoc/src/mastoc/gui/
├── app.py
├── hold_selector.py
├── creation_app.py
└── dialogs/login.py
```

## Références

- ADR 001 : Architecture Railway-First avec Mapping d'IDs
- ADR 004 : Client PyQtGraph + SQLite
- `/docs/04_strategie_independance.md`
- Serveur : https://mastoc-production.up.railway.app/docs
