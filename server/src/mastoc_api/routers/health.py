"""
Endpoint de santé.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from mastoc_api.database import get_db
from mastoc_api.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Vérifie l'état du serveur et de la base de données."""
    settings = get_settings()

    # Test connexion DB
    try:
        db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "app_name": settings.app_name,
        "version": "0.1.0",
        "database": db_status,
    }


@router.get("/")
def root():
    """Endpoint racine."""
    return {
        "message": "mastoc-api",
        "version": "0.1.0",
        "docs": "/docs",
    }
