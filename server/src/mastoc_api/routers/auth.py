"""
Endpoints d'authentification.

Routes publiques (pas de token requis) :
- POST /auth/register - Créer un compte
- POST /auth/login - Se connecter (obtenir JWT)
- POST /auth/refresh - Renouveler le token
- POST /auth/reset-password - Demander reset
- POST /auth/reset-password/confirm - Confirmer reset
"""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from mastoc_api.database import get_db
from mastoc_api.models import User
from mastoc_api.models.base import UserRole, DataSource
from mastoc_api.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    generate_reset_token,
    Token,
)
from mastoc_api.config import get_settings


router = APIRouter(prefix="/auth", tags=["auth"])


# --- Schemas ---

class RegisterRequest(BaseModel):
    """Demande d'inscription."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)


class RegisterResponse(BaseModel):
    """Réponse inscription."""
    id: UUID
    email: str
    username: str
    full_name: str
    message: str = "Compte créé avec succès"


class LoginResponse(Token):
    """Réponse login avec info utilisateur."""
    user_id: UUID
    email: str
    username: str
    full_name: str
    role: str


class RefreshRequest(BaseModel):
    """Demande de refresh token."""
    refresh_token: str


class ResetPasswordRequest(BaseModel):
    """Demande de reset password."""
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    """Confirmation reset password."""
    token: str
    new_password: str = Field(..., min_length=8)


class MessageResponse(BaseModel):
    """Réponse simple."""
    message: str


# --- Endpoints ---

@router.post("/register", response_model=RegisterResponse, status_code=201)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Créer un nouveau compte utilisateur mastoc.

    - Email et username doivent être uniques
    - Mot de passe minimum 8 caractères
    """
    # Vérifier email unique
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé"
        )

    # Vérifier username unique
    existing = db.query(User).filter(User.username == request.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris"
        )

    # Créer l'utilisateur
    user = User(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        password_hash=get_password_hash(request.password),
        source=DataSource.MASTOC.value,
        role=UserRole.USER.value,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return RegisterResponse(
        id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
    )


@router.post("/login", response_model=LoginResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authentification par email/username + mot de passe.

    Retourne un access token et un refresh token.
    Le username peut être l'email ou le username.
    """
    # Chercher par email ou username
    user = db.query(User).filter(
        or_(
            User.email == form_data.username,
            User.username == form_data.username
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier que l'utilisateur a un mot de passe (pas un user importé de Stokt)
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ce compte n'a pas de mot de passe mastoc. Utilisez 'Mot de passe oublié' pour en créer un.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier le mot de passe
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/username ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Vérifier compte actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé",
        )

    # Mettre à jour last_login
    user.last_login_at = datetime.utcnow()
    db.commit()

    # Créer les tokens
    settings = get_settings()
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )
    refresh_token = create_refresh_token(user_id=user.id)

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
        user_id=user.id,
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        role=user.role,
    )


@router.post("/refresh", response_model=Token)
def refresh_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """
    Renouveler l'access token avec un refresh token.
    """
    user_id = decode_refresh_token(request.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token invalide ou expiré",
        )

    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur non trouvé",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé",
        )

    settings = get_settings()
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        role=user.role,
    )
    new_refresh_token = create_refresh_token(user_id=user.id)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/logout", response_model=MessageResponse)
def logout():
    """
    Déconnexion.

    Avec JWT stateless, la déconnexion se fait côté client en supprimant le token.
    Cet endpoint existe pour la cohérence de l'API.
    """
    return MessageResponse(message="Déconnecté")


@router.post("/reset-password", response_model=MessageResponse)
def request_reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Demander un reset de mot de passe.

    Un email sera envoyé avec un lien de réinitialisation.
    (Pour l'instant, le token est retourné directement pour les tests)
    """
    user = db.query(User).filter(User.email == request.email).first()

    # Ne pas révéler si l'email existe ou non
    if not user:
        return MessageResponse(
            message="Si cet email existe, un lien de réinitialisation a été envoyé"
        )

    # Générer token de reset
    token = generate_reset_token()
    user.reset_token = token
    user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
    db.commit()

    # TODO: Envoyer l'email avec le token
    # Pour l'instant, on log le token (dev mode)
    settings = get_settings()
    if settings.debug:
        print(f"[DEBUG] Reset token for {user.email}: {token}")

    return MessageResponse(
        message="Si cet email existe, un lien de réinitialisation a été envoyé"
    )


@router.post("/reset-password/confirm", response_model=MessageResponse)
def confirm_reset_password(request: ResetPasswordConfirm, db: Session = Depends(get_db)):
    """
    Confirmer le reset de mot de passe avec le token.
    """
    user = db.query(User).filter(User.reset_token == request.token).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token invalide",
        )

    if user.reset_token_expires and user.reset_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expiré",
        )

    # Mettre à jour le mot de passe
    user.password_hash = get_password_hash(request.new_password)
    user.reset_token = None
    user.reset_token_expires = None
    user.updated_at = datetime.utcnow()
    db.commit()

    return MessageResponse(message="Mot de passe mis à jour")
