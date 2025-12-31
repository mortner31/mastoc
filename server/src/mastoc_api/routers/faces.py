"""
Endpoints pour les faces (configurations de murs).
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from mastoc_api.database import get_db
from mastoc_api.models import Face, Hold

router = APIRouter(prefix="/faces", tags=["faces"])


# --- Schemas Pydantic ---

class HoldSetupResponse(BaseModel):
    """Hold dans le setup d'une face."""
    id: int
    stokt_id: Optional[int] = None
    polygon_str: str
    centroid_x: Optional[float] = None
    centroid_y: Optional[float] = None
    path_str: Optional[str] = None
    area: Optional[float] = None
    # Champs supplémentaires pour compatibilité client
    touch_polygon_str: str = ""
    centroid_str: str = ""
    top_polygon_str: str = ""
    center_tape_str: str = ""
    right_tape_str: str = ""
    left_tape_str: str = ""

    class Config:
        from_attributes = True


class PictureResponse(BaseModel):
    """Image d'une face."""
    name: str
    width: int
    height: int


class FaceSetupResponse(BaseModel):
    """Réponse complète du setup d'une face."""
    id: UUID
    stokt_id: Optional[UUID] = None
    is_active: bool = True
    total_climbs: int = 0
    picture: Optional[PictureResponse] = None
    small_picture: Optional[PictureResponse] = None
    feet_rules_options: list[str] = []
    has_symmetry: bool = False
    holds: list[HoldSetupResponse] = []

    class Config:
        from_attributes = True


class FaceListResponse(BaseModel):
    """Liste des faces."""
    id: UUID
    stokt_id: Optional[UUID] = None
    gym_id: UUID
    picture_path: str
    picture_width: Optional[int] = None
    picture_height: Optional[int] = None
    holds_count: int = 0
    climbs_count: int = 0

    class Config:
        from_attributes = True


# --- Endpoints ---

@router.get("", response_model=list[FaceListResponse])
def list_faces(
    gym_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
):
    """Liste les faces."""
    query = select(Face)
    if gym_id:
        query = query.where(Face.gym_id == gym_id)

    faces = db.execute(query).scalars().all()

    results = []
    for face in faces:
        results.append(FaceListResponse(
            id=face.id,
            stokt_id=face.stokt_id,
            gym_id=face.gym_id,
            picture_path=face.picture_path,
            picture_width=face.picture_width,
            picture_height=face.picture_height,
            holds_count=len(face.holds),
            climbs_count=len(face.climbs),
        ))

    return results


@router.get("/{face_id}", response_model=FaceListResponse)
def get_face(face_id: UUID, db: Session = Depends(get_db)):
    """Récupère une face par ID."""
    face = db.get(Face, face_id)
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    return FaceListResponse(
        id=face.id,
        stokt_id=face.stokt_id,
        gym_id=face.gym_id,
        picture_path=face.picture_path,
        picture_width=face.picture_width,
        picture_height=face.picture_height,
        holds_count=len(face.holds),
        climbs_count=len(face.climbs),
    )


@router.get("/{face_id}/setup", response_model=FaceSetupResponse)
def get_face_setup(face_id: UUID, db: Session = Depends(get_db)):
    """
    Récupère le setup complet d'une face avec tous ses holds.

    C'est l'endpoint principal pour charger la configuration
    d'un mur avec toutes les prises et leurs polygones.
    """
    face = db.get(Face, face_id)
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    # Construire la réponse picture
    picture = None
    if face.picture_path:
        picture = PictureResponse(
            name=face.picture_path,
            width=face.picture_width or 0,
            height=face.picture_height or 0,
        )

    # Construire les holds
    holds = []
    for hold in face.holds:
        # Construire centroid_str à partir de centroid_x, centroid_y
        centroid_str = ""
        if hold.centroid_x is not None and hold.centroid_y is not None:
            centroid_str = f"{hold.centroid_x} {hold.centroid_y}"

        holds.append(HoldSetupResponse(
            id=hold.stokt_id or hold.id,  # Utiliser stokt_id pour compatibilité
            stokt_id=hold.stokt_id,
            polygon_str=hold.polygon_str,
            centroid_x=hold.centroid_x,
            centroid_y=hold.centroid_y,
            path_str=hold.path_str,
            area=hold.area,
            centroid_str=centroid_str,
        ))

    # Récupérer les options de pieds
    feet_rules = face.feet_rules_options or []
    if isinstance(feet_rules, dict):
        feet_rules = list(feet_rules.values()) if feet_rules else []

    return FaceSetupResponse(
        id=face.id,
        stokt_id=face.stokt_id,
        is_active=True,
        total_climbs=len(face.climbs),
        picture=picture,
        feet_rules_options=feet_rules,
        has_symmetry=face.has_symmetry,
        holds=holds,
    )


@router.get("/by-stokt-id/{stokt_id}/setup", response_model=FaceSetupResponse)
def get_face_setup_by_stokt_id(stokt_id: UUID, db: Session = Depends(get_db)):
    """Récupère le setup d'une face par son ID Stokt."""
    query = select(Face).where(Face.stokt_id == stokt_id)
    face = db.execute(query).scalar_one_or_none()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    # Réutiliser la logique de get_face_setup
    return get_face_setup(face.id, db)
