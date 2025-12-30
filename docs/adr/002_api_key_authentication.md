# ADR 002 - Authentification par API Key

**Date** : 2025-12-30
**Statut** : Accepté

## Contexte

L'API mastoc-api déployée sur Railway est accessible publiquement. Sans authentification :
- N'importe qui peut lire les données (blocs, prises)
- N'importe qui peut créer/modifier/supprimer des blocs
- Risque de spam ou d'abus

Options considérées :
1. **OAuth2/JWT** : Complexe, nécessite gestion des utilisateurs
2. **API Key simple** : Simple, suffisant pour un projet personnel/petit groupe
3. **IP Whitelist** : Trop restrictif, pas adapté au mobile

## Décision

Utiliser une **authentification par API Key** via header HTTP :
- Header : `X-API-Key`
- Clé unique partagée entre les clients autorisés
- Mode développement : sans clé configurée, pas d'auth requise

## Conséquences

### Positives
- Simple à implémenter et utiliser
- Pas de gestion de sessions ou tokens
- Suffisant pour un projet personnel
- Mode dev facilite les tests locaux

### Négatives
- Pas de granularité par utilisateur
- Clé à distribuer manuellement aux clients
- Si compromise, doit être changée partout

## Implémentation

### Configuration (config.py)

```python
class Settings(BaseSettings):
    database_url: str = "sqlite:///./mastoc.db"
    api_key: str = ""  # Si vide, pas d'auth requise (dev mode)

    model_config = SettingsConfigDict(env_file=".env")
```

### Middleware d'authentification (auth.py)

```python
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    settings = get_settings()

    # Mode dev : pas d'API_KEY configurée = pas d'auth
    if not settings.api_key:
        return "dev-mode"

    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="API Key manquante. Header X-API-Key requis."
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=403,
            detail="API Key invalide."
        )

    return api_key
```

### Application aux routes (main.py)

```python
from mastoc_api.auth import verify_api_key

# Routes publiques (pas d'auth)
app.include_router(health_router)

# Routes protégées
api_dependencies = [Depends(verify_api_key)]
app.include_router(climbs_router, prefix="/api", dependencies=api_dependencies)
app.include_router(holds_router, prefix="/api", dependencies=api_dependencies)
app.include_router(sync_router, prefix="/api", dependencies=api_dependencies)
```

### Endpoints publics vs protégés

| Endpoint | Auth | Raison |
|----------|------|--------|
| `/` | Non | Info API |
| `/health` | Non | Health checks |
| `/docs`, `/redoc` | Non | Documentation |
| `/api/*` | Oui | Toutes les données |

### Usage client

```bash
# Sans auth (401)
curl https://mastoc-production.up.railway.app/api/climbs

# Avec auth (200)
curl -H "X-API-Key: votre-clé-secrète" \
  https://mastoc-production.up.railway.app/api/climbs
```

### Configuration Railway

Variable d'environnement sur Railway :
- `API_KEY` = `mastoc-2025-1213-brosse-lesprises-secret`

## Fichiers concernés

- `server/src/mastoc_api/config.py` - Setting `api_key`
- `server/src/mastoc_api/auth.py` - Logique de vérification
- `server/src/mastoc_api/main.py` - Application des dépendances
- `server/tests/test_auth.py` - Tests d'authentification
