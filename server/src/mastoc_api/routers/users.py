"""
Endpoints utilisateurs.

Routes protégées par JWT :
- GET /users/me - Profil utilisateur connecté
- PATCH /users/me - Modifier son profil
- POST /users/me/avatar - Upload avatar
- GET /users/{id} - Profil public d'un utilisateur
- GET /users - Liste des utilisateurs (admin)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import os
from pathlib import Path

from mastoc_api.database import get_db
from mastoc_api.models import User
from mastoc_api.models.base import UserRole
from mastoc_api.dependencies import (
    get_current_active_user,
    get_admin_user,
    AuthenticatedUser,
)
from mastoc_api.security import get_password_hash


router = APIRouter(prefix="/users", tags=["users"])

# Dossier pour les avatars
AVATAR_DIR = Path("/tmp/mastoc_avatars")
AVATAR_DIR.mkdir(exist_ok=True)


# --- Schemas ---

class UserProfile(BaseModel):
    """Profil utilisateur."""
    id: UUID
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: str
    avatar_path: Optional[str] = None
    role: str
    source: str
    created_at: datetime
    last_login_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """Profil public (visible par tous)."""
    id: UUID
    username: Optional[str] = None
    full_name: str
    avatar_path: Optional[str] = None

    class Config:
        from_attributes = True


class UpdateProfile(BaseModel):
    """Mise à jour du profil."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class ChangePassword(BaseModel):
    """Changement de mot de passe."""
    current_password: str
    new_password: str = Field(..., min_length=8)


class UsersListResponse(BaseModel):
    """Liste paginée d'utilisateurs."""
    results: list[UserProfile]
    count: int
    page: int
    page_size: int


class MessageResponse(BaseModel):
    """Réponse simple."""
    message: str


# --- Endpoints ---

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Récupère le profil de l'utilisateur connecté.
    """
    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_path=current_user.avatar_path,
        role=current_user.role,
        source=current_user.source,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
    )


@router.patch("/me", response_model=UserProfile)
def update_current_user_profile(
    update_data: UpdateProfile,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Met à jour le profil de l'utilisateur connecté.
    """
    # Vérifier unicité du username si modifié
    if update_data.username and update_data.username != current_user.username:
        existing = db.query(User).filter(User.username == update_data.username).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom d'utilisateur est déjà pris"
            )

    # Appliquer les modifications
    update_dict = update_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(current_user, field, value)

    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)

    return UserProfile(
        id=current_user.id,
        email=current_user.email,
        username=current_user.username,
        full_name=current_user.full_name,
        avatar_path=current_user.avatar_path,
        role=current_user.role,
        source=current_user.source,
        created_at=current_user.created_at,
        last_login_at=current_user.last_login_at,
    )


@router.post("/me/password", response_model=MessageResponse)
def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Changer son mot de passe.
    """
    from mastoc_api.security import verify_password

    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte n'a pas de mot de passe. Utilisez 'Mot de passe oublié'."
        )

    if not verify_password(data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect"
        )

    current_user.password_hash = get_password_hash(data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return MessageResponse(message="Mot de passe mis à jour")


@router.post("/me/avatar", response_model=MessageResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload un nouvel avatar.

    Formats acceptés : JPG, PNG, GIF
    Taille max : 2 MB
    """
    # Vérifier le type
    if file.content_type not in ["image/jpeg", "image/png", "image/gif"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format non supporté. Utilisez JPG, PNG ou GIF."
        )

    # Lire le fichier
    content = await file.read()

    # Vérifier la taille (2 MB max)
    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop volumineux. Maximum 2 MB."
        )

    # Déterminer l'extension
    ext = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/gif": ".gif",
    }.get(file.content_type, ".jpg")

    # Sauvegarder
    avatar_filename = f"{current_user.id}{ext}"
    avatar_path = AVATAR_DIR / avatar_filename

    # Supprimer l'ancien avatar si existe
    if current_user.avatar_path:
        old_path = AVATAR_DIR / current_user.avatar_path.split("/")[-1]
        if old_path.exists():
            old_path.unlink()

    # Écrire le nouveau
    with open(avatar_path, "wb") as f:
        f.write(content)

    # Mettre à jour le chemin en DB
    current_user.avatar_path = f"/api/users/{current_user.id}/avatar"
    current_user.updated_at = datetime.utcnow()
    db.commit()

    return MessageResponse(message="Avatar mis à jour")


@router.get("/{user_id}", response_model=UserPublicProfile)
def get_user_public_profile(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Récupère le profil public d'un utilisateur.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    return UserPublicProfile(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        avatar_path=user.avatar_path,
    )


@router.get("/{user_id}/avatar")
def get_user_avatar(user_id: UUID, db: Session = Depends(get_db)):
    """
    Télécharge l'avatar d'un utilisateur.
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )

    # Chercher le fichier avatar
    for ext in [".jpg", ".png", ".gif"]:
        avatar_path = AVATAR_DIR / f"{user_id}{ext}"
        if avatar_path.exists():
            media_type = {
                ".jpg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
            }.get(ext, "image/jpeg")
            return FileResponse(avatar_path, media_type=media_type)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Avatar non trouvé"
    )


@router.get("", response_model=UsersListResponse)
def list_users(
    search: Optional[str] = None,
    role: Optional[str] = None,
    page: int = 1,
    page_size: int = 50,
    admin: AuthenticatedUser = Depends(get_admin_user),
    db: Session = Depends(get_db),
):
    """
    Liste tous les utilisateurs (admin seulement).
    """
    query = select(User)

    if search:
        query = query.where(
            User.full_name.ilike(f"%{search}%") |
            User.email.ilike(f"%{search}%") |
            User.username.ilike(f"%{search}%")
        )

    if role:
        query = query.where(User.role == role)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(User.created_at.desc())

    users = db.execute(query).scalars().all()

    results = [
        UserProfile(
            id=u.id,
            email=u.email,
            username=u.username,
            full_name=u.full_name,
            avatar_path=u.avatar_path,
            role=u.role,
            source=u.source,
            created_at=u.created_at,
            last_login_at=u.last_login_at,
        )
        for u in users
    ]

    return UsersListResponse(
        results=results,
        count=total,
        page=page,
        page_size=page_size,
    )
