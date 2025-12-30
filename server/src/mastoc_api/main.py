"""
Application FastAPI principale pour mastoc-api.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from mastoc_api.config import get_settings
from mastoc_api.database import Base, engine
from mastoc_api.auth import verify_api_key
from mastoc_api.routers import (
    health_router,
    climbs_router,
    holds_router,
    sync_router,
)
# Import des modèles pour créer les tables
from mastoc_api.models import Gym, Face, Hold, Climb, User, IdMapping  # noqa: F401


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    # Création des tables au démarrage
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup (si nécessaire)


app = FastAPI(
    title="mastoc-api",
    description="API de gestion de blocs d'escalade - Architecture Railway-First",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Dev frontend
        "http://localhost:8000",  # Dev local
        "https://mastoc.railway.app",  # Production Railway
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusion des routers
# Health : public (pour monitoring)
app.include_router(health_router)

# API : protégée par API Key
api_dependencies = [Depends(verify_api_key)]
app.include_router(climbs_router, prefix="/api", dependencies=api_dependencies)
app.include_router(holds_router, prefix="/api", dependencies=api_dependencies)
app.include_router(sync_router, prefix="/api", dependencies=api_dependencies)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "mastoc_api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
