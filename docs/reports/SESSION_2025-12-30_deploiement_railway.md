# Rapport de Session - Déploiement Railway mastoc-api

**Date** : 2025-12-30

## Objectifs Atteints

- [x] Finalisation du serveur FastAPI (main.py)
- [x] Création README serveur avec documentation endpoints
- [x] Configuration Railway (Procfile, requirements.txt)
- [x] Déploiement sur Railway avec PostgreSQL
- [x] API en production et fonctionnelle

## Travail Effectué

### 1. Finalisation du code serveur

**Fichiers créés :**
- `server/src/mastoc_api/main.py` - Application FastAPI principale
- `server/README.md` - Documentation du serveur
- `server/Procfile` - Configuration Railway
- `server/requirements.txt` - Dépendances Python
- `server/.env.example` - Template de configuration

**Contenu de main.py :**
- Lifespan pour création des tables au démarrage
- Configuration CORS (localhost + production)
- Inclusion des routers (health, climbs, holds, sync)

### 2. Déploiement Railway

**Étapes effectuées :**

1. Push du code sur GitHub (mortner31/mastoc)
2. Création projet Railway connecté au repo
3. Configuration Root Directory : `server`
4. Ajout base PostgreSQL
5. Configuration variable `DATABASE_URL` via Shared Variables
6. Génération domaine public (port 8080)

**Problèmes rencontrés et solutions :**

| Problème | Solution |
|----------|----------|
| `uvicorn: command not found` | Création `requirements.txt` (Railway ne détecte pas pyproject.toml) |
| Module mastoc_api non trouvé | Ajout `PYTHONPATH=src` dans Procfile |

### 3. Résultat Final

**URL Production :** https://mastoc-production.up.railway.app

**Endpoints testés :**
```
GET /        → {"message": "mastoc-api", "version": "0.1.0"}
GET /health  → {"status": "ok", "database": "ok"}
GET /docs    → Swagger UI
```

## Prochaines Étapes

1. Créer script `init_from_stokt.py` pour importer les données
2. Importer gym Montoboard + faces + holds (776 prises)
3. Importer climbs (~1000 blocs)
4. Mettre à jour le client mastoc pour utiliser Railway

## Commits

- `1783584` - feat: TODO 13 - Serveur FastAPI mastoc-api (Phase 1 complète)
- `ab0e336` - fix: requirements.txt et PYTHONPATH pour Railway
