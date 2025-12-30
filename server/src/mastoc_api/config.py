"""
Configuration de l'application.

Utilise pydantic-settings pour charger depuis variables d'environnement.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration de l'application."""

    # Application
    app_name: str = "mastoc-api"
    debug: bool = False

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/mastoc"

    # Stokt (pour import)
    stokt_base_url: str = "https://www.sostokt.com"
    stokt_token: str = ""
    montoboard_gym_id: str = "be149ef2-317d-4c73-8d7d-50074577d2fa"

    # Auth
    secret_key: str = "dev-secret-key-change-in-production"
    access_token_expire_minutes: int = 60 * 24  # 24 heures

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """Retourne les settings (cached)."""
    return Settings()
