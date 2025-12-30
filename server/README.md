# mastoc-api

Backend FastAPI pour mastoc - gestion de blocs d'escalade.

## Architecture

Architecture **Railway-First** avec mapping d'identifiants Stokt :
- Chaque entité possède un `stokt_id` nullable
- Les entités créées localement ont `stokt_id = NULL`
- L'import depuis Stokt remplit `stokt_id`

## Prérequis

- Python 3.11+
- PostgreSQL 15+

## Installation

```bash
cd server

# Environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installation avec dépendances dev
pip install -e ".[dev]"
```

## Configuration

Créer un fichier `.env` :

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/mastoc
DEBUG=true
SECRET_KEY=your-secret-key
STOKT_TOKEN=your-stokt-token
```

## Démarrage

### PostgreSQL avec Docker

```bash
docker run -d \
  --name mastoc-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=mastoc \
  -p 5432:5432 \
  postgres:15
```

### Serveur de développement

```bash
uvicorn mastoc_api.main:app --reload --host 0.0.0.0 --port 8000
```

Ou directement :

```bash
python -m mastoc_api.main
```

## Endpoints

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/` | GET | Info API |
| `/health` | GET | Status serveur + DB |
| `/docs` | GET | Documentation Swagger |
| `/redoc` | GET | Documentation ReDoc |

### Climbs

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/climbs` | GET | Liste climbs (filtres, pagination) |
| `/api/climbs/{id}` | GET | Détail climb |
| `/api/climbs/by-stokt-id/{id}` | GET | Climb par stokt_id |
| `/api/climbs` | POST | Créer climb |
| `/api/climbs/{id}` | PATCH | Modifier climb |
| `/api/climbs/{id}` | DELETE | Supprimer climb |
| `/api/climbs/{id}/stokt-id` | PATCH | MAJ stokt_id (après push) |

### Holds

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/holds` | GET | Liste holds d'une face |
| `/api/holds/{id}` | GET | Détail hold |

### Sync

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/sync/stats` | GET | Stats de la base |
| `/api/sync/import/gym` | POST | Import gym Stokt |
| `/api/sync/import/face` | POST | Import face Stokt |
| `/api/sync/import/hold` | POST | Import hold Stokt |
| `/api/sync/import/climb` | POST | Import climb Stokt |
| `/api/sync/import/user` | POST | Import user Stokt |

## Tests

```bash
pytest
```

## Déploiement Railway

**URL Production** : https://mastoc-production.up.railway.app

### Configuration initiale

1. **Créer un projet Railway**
   - Aller sur [railway.app/dashboard](https://railway.app/dashboard)
   - Cliquer "New Project" → "Deploy from GitHub repo"
   - Sélectionner le repo `mastoc`

2. **Configurer le service**
   - Dans Settings → Source : **Root Directory** = `server`
   - Railway détecte automatiquement Python via `requirements.txt`

3. **Ajouter PostgreSQL**
   - Dans le projet, cliquer "+ New" → "Database" → "PostgreSQL"

4. **Configurer les variables**
   - Aller dans "Shared Variables" du projet
   - Ajouter : `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`

   Ou dans le service API → Variables :
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   DEBUG=false
   SECRET_KEY=<clé-secrète-générée>
   ```

5. **Générer le domaine public**
   - Service API → Settings → Networking → "Generate"
   - Choisir port **8080**

### Fichiers de configuration

| Fichier | Description |
|---------|-------------|
| `Procfile` | Commande de démarrage : `PYTHONPATH=src uvicorn mastoc_api.main:app --host 0.0.0.0 --port $PORT` |
| `requirements.txt` | Dépendances Python (Railway ne détecte pas pyproject.toml) |

### Redéploiement

Railway redéploie automatiquement à chaque push sur `main`. Pour forcer un redéploiement :
- Service → Deployments → ⋮ → Redeploy
