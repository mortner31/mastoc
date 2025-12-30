"""
Authentification par API Key.
"""

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from mastoc_api.config import get_settings

# Header attendu : X-API-Key
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Vérifie l'API Key.

    Si API_KEY n'est pas configurée (vide), l'auth est désactivée (dev mode).
    """
    settings = get_settings()

    # Dev mode : pas d'API key configurée = pas d'auth
    if not settings.api_key:
        return "dev-mode"

    # Vérification de l'API key
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key manquante. Header 'X-API-Key' requis.",
        )

    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API Key invalide.",
        )

    return api_key
