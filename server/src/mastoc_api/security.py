"""
Module de sécurité : hashing passwords et JWT.
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid

import bcrypt
from jose import JWTError, jwt
from pydantic import BaseModel

from mastoc_api.config import get_settings

# Algorithme JWT
ALGORITHM = "HS256"


class TokenData(BaseModel):
    """Données extraites du token JWT."""
    user_id: uuid.UUID
    email: Optional[str] = None
    role: str = "user"


class Token(BaseModel):
    """Réponse token."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def get_password_hash(password: str) -> str:
    """Hash un mot de passe."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def create_access_token(
    user_id: uuid.UUID,
    email: str,
    role: str,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Crée un token JWT d'accès.

    Args:
        user_id: ID de l'utilisateur
        email: Email de l'utilisateur
        role: Rôle (user/admin)
        expires_delta: Durée de validité (optionnel)

    Returns:
        Token JWT encodé
    """
    settings = get_settings()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    """
    Crée un token JWT de refresh (longue durée).

    Valide 7 jours.
    """
    settings = get_settings()

    expire = datetime.utcnow() + timedelta(days=7)

    to_encode = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": datetime.utcnow(),
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    """
    Décode un token JWT.

    Returns:
        TokenData si valide, None sinon
    """
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None

        return TokenData(
            user_id=uuid.UUID(user_id_str),
            email=payload.get("email"),
            role=payload.get("role", "user")
        )
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[uuid.UUID]:
    """
    Décode un refresh token.

    Returns:
        user_id si valide, None sinon
    """
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])

        # Vérifier que c'est bien un refresh token
        if payload.get("type") != "refresh":
            return None

        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None

        return uuid.UUID(user_id_str)
    except JWTError:
        return None


def generate_reset_token() -> str:
    """Génère un token de reset password (UUID simple)."""
    return str(uuid.uuid4())
