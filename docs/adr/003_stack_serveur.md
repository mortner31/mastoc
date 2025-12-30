# ADR 003 - Stack technique serveur (FastAPI + PostgreSQL)

**Date** : 2025-12-30
**Statut** : Accepté

## Contexte

Le projet mastoc nécessite un backend pour :
- Stocker les données (gyms, faces, prises, blocs)
- Exposer une API REST pour le client
- Être déployable facilement sur un service cloud

Options considérées :

| Option | Avantages | Inconvénients |
|--------|-----------|---------------|
| Django REST | Batteries included | Lourd, ORM moins flexible |
| Flask + SQLAlchemy | Léger, mature | Pas de validation native |
| **FastAPI + SQLAlchemy** | Moderne, async, validation | Plus récent |
| Node.js + Express | Populaire | Changement de langage |

## Décision

Utiliser **FastAPI** avec **SQLAlchemy** et **PostgreSQL** :
- FastAPI pour l'API REST (validation Pydantic, async, docs auto)
- SQLAlchemy 2.0 pour l'ORM (typed, migrations)
- PostgreSQL en production (via Railway)
- SQLite pour les tests (en mémoire)

## Conséquences

### Positives
- Validation automatique des requêtes (Pydantic)
- Documentation OpenAPI générée automatiquement
- Typage Python natif
- Excellente performance
- SQLAlchemy 2.0 moderne avec mapped_column

### Négatives
- Moins de ressources que Django (framework plus jeune)
- Async peut complexifier certains patterns

## Implémentation

### Structure du projet

```
server/
├── pyproject.toml
├── requirements.txt      # Pour Railway
├── Procfile              # Commande de démarrage
├── src/
│   └── mastoc_api/
│       ├── __init__.py
│       ├── config.py     # Pydantic Settings
│       ├── database.py   # SQLAlchemy engine/session
│       ├── auth.py       # API Key auth
│       ├── main.py       # App FastAPI
│       ├── models/       # SQLAlchemy models
│       │   ├── base.py
│       │   ├── gym.py
│       │   ├── face.py
│       │   ├── hold.py
│       │   ├── climb.py
│       │   ├── user.py
│       │   └── mapping.py
│       └── routers/      # FastAPI routers
│           ├── health.py
│           ├── climbs.py
│           ├── holds.py
│           └── sync.py
└── tests/
    ├── conftest.py
    └── test_*.py
```

### Configuration (config.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./mastoc.db"
    api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

### Database (database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

class Base(DeclarativeBase):
    pass

def get_engine(database_url: str):
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args)

def get_session_maker(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Modèle exemple (models/climb.py)

```python
from sqlalchemy import ForeignKey, String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as Uuid
import uuid

class Climb(Base):
    __tablename__ = "climbs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    stokt_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, unique=True, nullable=True, index=True
    )
    face_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("faces.id")
    )
    name: Mapped[str | None] = mapped_column(String(255))
    grade_font: Mapped[str | None] = mapped_column(String(10))
    is_private: Mapped[bool] = mapped_column(Boolean, default=False)

    face: Mapped["Face"] = relationship(back_populates="climbs")
```

### Router exemple (routers/climbs.py)

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

router = APIRouter(prefix="/climbs", tags=["climbs"])

class ClimbResponse(BaseModel):
    id: str
    name: str | None
    grade_font: str | None

    class Config:
        from_attributes = True

@router.get("", response_model=list[ClimbResponse])
def list_climbs(
    face_id: str | None = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(Climb)
    if face_id:
        query = query.filter(Climb.face_id == face_id)
    return query.offset(skip).limit(limit).all()
```

### Déploiement Railway

**Procfile** :
```
web: PYTHONPATH=src uvicorn mastoc_api.main:app --host 0.0.0.0 --port $PORT
```

**Variables d'environnement** :
- `DATABASE_URL` = `${{Postgres.DATABASE_URL}}`
- `API_KEY` = `(votre clé secrète)`

## Fichiers concernés

- `server/pyproject.toml` - Dépendances Python
- `server/requirements.txt` - Pour Railway
- `server/Procfile` - Commande de démarrage
- `server/src/mastoc_api/` - Code source
- `server/tests/` - Tests pytest
