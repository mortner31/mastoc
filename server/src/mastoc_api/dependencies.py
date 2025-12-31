"""
Dependencies FastAPI pour l'authentification.

Supporte:
- API Key (header X-API-Key) - pour scripts et admin
- JWT Bearer token (header Authorization: Bearer <token>) - pour utilisateurs
"""

from typing import Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from sqlalchemy.orm import Session

from mastoc_api.config import get_settings
from mastoc_api.database import get_db
from mastoc_api.models import User
from mastoc_api.security import decode_token, TokenData


# Headers de sécurité
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


class AuthenticatedUser:
    """
    Utilisateur authentifié.

    Peut être soit un utilisateur DB (via JWT) soit un "service account" (via API Key).
    """

    def __init__(
        self,
        user: Optional[User] = None,
        is_api_key: bool = False,
        api_key_value: Optional[str] = None
    ):
        self.user = user
        self.is_api_key = is_api_key
        self.api_key_value = api_key_value

    @property
    def user_id(self) -> Optional[uuid.UUID]:
        """ID de l'utilisateur (None si API Key)."""
        return self.user.id if self.user else None

    @property
    def is_admin(self) -> bool:
        """True si admin (API Key ou role admin)."""
        if self.is_api_key:
            return True  # API Key = admin
        return self.user.is_admin if self.user else False

    @property
    def is_authenticated(self) -> bool:
        """True si authentifié."""
        return self.user is not None or self.is_api_key


async def get_current_user_optional(
    api_key: Optional[str] = Depends(api_key_header),
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[AuthenticatedUser]:
    """
    Récupère l'utilisateur courant (optionnel).

    Ordre de priorité:
    1. API Key (si présente et valide)
    2. JWT Bearer token (si présent et valide)
    3. None (pas authentifié)
    """
    settings = get_settings()

    # 1. Vérifier API Key
    if api_key:
        # Dev mode : pas d'API key configurée
        if not settings.api_key:
            return AuthenticatedUser(is_api_key=True, api_key_value="dev-mode")

        if api_key == settings.api_key:
            return AuthenticatedUser(is_api_key=True, api_key_value=api_key)

    # 2. Vérifier JWT
    if token:
        token_data = decode_token(token)
        if token_data:
            user = db.query(User).filter(User.id == token_data.user_id).first()
            if user and user.is_active:
                return AuthenticatedUser(user=user)

    # 3. Pas authentifié
    return None


async def get_current_user(
    auth_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional)
) -> AuthenticatedUser:
    """
    Récupère l'utilisateur courant (requis).

    Raises:
        HTTPException 401 si non authentifié
    """
    if not auth_user or not auth_user.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Non authentifié. Utilisez un token JWT ou une API Key.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return auth_user


async def get_current_active_user(
    auth_user: AuthenticatedUser = Depends(get_current_user)
) -> User:
    """
    Récupère l'utilisateur DB courant (requis).

    Ne fonctionne qu'avec JWT (pas API Key).

    Raises:
        HTTPException 401 si non authentifié par JWT
        HTTPException 403 si compte désactivé
    """
    if auth_user.is_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cette route requiert une authentification JWT (pas API Key).",
        )

    if not auth_user.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé.",
        )

    if not auth_user.user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé.",
        )

    return auth_user.user


async def get_admin_user(
    auth_user: AuthenticatedUser = Depends(get_current_user)
) -> AuthenticatedUser:
    """
    Vérifie que l'utilisateur est admin.

    Admin = API Key ou role admin.

    Raises:
        HTTPException 403 si non admin
    """
    if not auth_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs.",
        )
    return auth_user
