# Guide des Tests mastoc

Ce document explique comment lancer et ecrire des tests pour le projet mastoc.

## Structure des Tests

```
mastoc/
├── server/tests/           # Tests API FastAPI
│   ├── conftest.py         # Fixtures partagees
│   ├── test_health.py      # Health endpoints
│   ├── test_auth.py        # API Key authentication
│   ├── test_jwt_auth.py    # JWT authentication
│   ├── test_users.py       # User endpoints
│   ├── test_holds.py       # Hold endpoints
│   ├── test_permissions.py # Permission tests
│   ├── test_climbs.py      # Climb CRUD
│   ├── test_faces.py       # Face/setup endpoints
│   └── test_sync.py        # Batch import
│
└── mastoc/tests/           # Tests client Python
    ├── test_models.py          # Data models
    ├── test_api_crud.py        # Stokt API CRUD
    ├── test_railway_client.py  # Railway API
    ├── test_auth_manager.py    # Authentication manager
    ├── test_api_errors.py      # API configuration
    ├── test_database.py        # SQLite layer
    ├── test_sync.py            # Sync managers
    ├── test_filters.py         # Climb filtering
    ├── test_creation.py        # Climb creation
    ├── test_hold_selector.py   # Hold indexing
    ├── test_social.py          # Social features
    ├── test_config.py          # Configuration
    ├── test_assets.py          # Asset management
    ├── test_backend.py         # Backend switching
    └── test_integration.py     # Integration tests
```

## Lancer les Tests

### Serveur (FastAPI)

```bash
cd server
PYTHONPATH=src python -m pytest tests/ -v
```

Avec couverture :
```bash
PYTHONPATH=src python -m pytest tests/ -v --cov=src/mastoc_api
```

### Client (mastoc)

```bash
cd mastoc
python -m pytest tests/ -v
```

Avec couverture :
```bash
python -m pytest tests/ -v --cov=src/mastoc
```

### Tests specifiques

```bash
# Un seul fichier
python -m pytest tests/test_users.py -v

# Un seul test
python -m pytest tests/test_users.py::test_login_success -v

# Pattern de nom
python -m pytest tests/ -k "login" -v
```

## Fixtures Partagees

### Serveur (conftest.py)

- `db_session` : Session SQLite in-memory
- `client` : TestClient FastAPI
- `api_key_header` : Header avec API Key

### Client

Chaque fichier de test definit ses propres fixtures avec `@pytest.fixture`.

## Ecrire un Test

### Serveur

```python
"""Tests pour mon_module."""

import pytest
from mastoc_api.models import MonModel

def test_fonction_success(client, db_session):
    """Description du test."""
    response = client.get("/api/endpoint")
    assert response.status_code == 200
    assert "expected" in response.json()

def test_fonction_error(client):
    """Test erreur attendue."""
    response = client.get("/api/invalid")
    assert response.status_code == 404
```

### Client

```python
"""Tests pour mon_module."""

import pytest
from unittest.mock import Mock, patch

from mastoc.core.mon_module import MaClasse

@pytest.fixture
def instance():
    return MaClasse()

def test_methode_success(instance):
    """Description du test."""
    result = instance.methode()
    assert result == "expected"

def test_avec_mock():
    """Test avec mock API."""
    with patch("requests.get") as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"data": "test"}

        result = fonction_api()

        assert result["data"] == "test"
```

## Regles Importantes

1. **Importer depuis production** : Toujours utiliser les modules de production, jamais de copies
2. **Isolation** : Chaque test doit etre independant
3. **Naming** : `test_<fonction>_<scenario>`
4. **Assertions claires** : Un assert principal par test

## Troubleshooting

### ModuleNotFoundError

```bash
# Serveur
PYTHONPATH=src python -m pytest tests/

# Client
cd mastoc && python -m pytest tests/
```

### DB locked

Utiliser `scope="function"` pour les fixtures DB.

### Tests lents

```bash
# Parallele
python -m pytest tests/ -n auto
```
