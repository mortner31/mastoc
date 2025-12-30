"""
Endpoints pour la synchronisation Stokt.
"""

from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from mastoc_api.database import get_db
from mastoc_api.models import Climb, Face, Hold, User, Gym, IdMapping
from mastoc_api.config import get_settings

router = APIRouter(prefix="/api/sync", tags=["sync"])


# --- Schemas ---

class SyncStats(BaseModel):
    """Statistiques de synchronisation."""
    gyms: int
    faces: int
    holds: int
    climbs: int
    users: int


class ImportClimbRequest(BaseModel):
    """Données pour importer un climb depuis Stokt."""
    stokt_id: UUID
    face_stokt_id: UUID
    setter_stokt_id: UUID | None = None
    name: str
    holds_list: str
    grade_font: str | None = None
    grade_ircra: float | None = None
    feet_rule: str | None = None
    description: str | None = None
    is_private: bool = False
    climbed_by: int = 0
    total_likes: int = 0
    date_created: str | None = None


class ImportUserRequest(BaseModel):
    """Données pour importer un user depuis Stokt."""
    stokt_id: UUID
    full_name: str
    avatar_path: str | None = None


class ImportFaceRequest(BaseModel):
    """Données pour importer une face depuis Stokt."""
    stokt_id: UUID
    gym_stokt_id: UUID
    picture_path: str
    picture_width: int | None = None
    picture_height: int | None = None
    feet_rules_options: list[str] = []
    has_symmetry: bool = False


class ImportHoldRequest(BaseModel):
    """Données pour importer un hold depuis Stokt."""
    stokt_id: int
    face_stokt_id: UUID
    polygon_str: str
    centroid_x: float | None = None
    centroid_y: float | None = None
    area: float | None = None
    path_str: str | None = None


# --- Endpoints ---

@router.get("/stats", response_model=SyncStats)
def get_sync_stats(db: Session = Depends(get_db)):
    """Retourne les statistiques de la base."""
    return SyncStats(
        gyms=db.query(Gym).count(),
        faces=db.query(Face).count(),
        holds=db.query(Hold).count(),
        climbs=db.query(Climb).count(),
        users=db.query(User).count(),
    )


@router.post("/import/user")
def import_user(data: ImportUserRequest, db: Session = Depends(get_db)):
    """Importe un user depuis Stokt."""
    # Vérifier si déjà importé
    existing = db.query(User).filter(User.stokt_id == data.stokt_id).first()
    if existing:
        return {"id": str(existing.id), "status": "exists"}

    user = User(
        stokt_id=data.stokt_id,
        full_name=data.full_name,
        avatar_path=data.avatar_path,
        source="stokt",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Log mapping
    mapping = IdMapping(
        entity_type="user",
        mastoc_id=user.id,
        stokt_id=data.stokt_id,
        sync_direction="stokt_to_mastoc",
    )
    db.add(mapping)
    db.commit()

    return {"id": str(user.id), "status": "created"}


@router.post("/import/face")
def import_face(data: ImportFaceRequest, db: Session = Depends(get_db)):
    """Importe une face depuis Stokt."""
    # Vérifier si déjà importé
    existing = db.query(Face).filter(Face.stokt_id == data.stokt_id).first()
    if existing:
        return {"id": str(existing.id), "status": "exists"}

    # Trouver le gym
    gym = db.query(Gym).filter(Gym.stokt_id == data.gym_stokt_id).first()
    if not gym:
        raise HTTPException(status_code=404, detail="Gym not found")

    face = Face(
        stokt_id=data.stokt_id,
        gym_id=gym.id,
        picture_path=data.picture_path,
        picture_width=data.picture_width,
        picture_height=data.picture_height,
        feet_rules_options=data.feet_rules_options,
        has_symmetry=data.has_symmetry,
        source="stokt",
        synced_at=datetime.utcnow(),
    )
    db.add(face)
    db.commit()
    db.refresh(face)

    return {"id": str(face.id), "status": "created"}


@router.post("/import/hold")
def import_hold(data: ImportHoldRequest, db: Session = Depends(get_db)):
    """Importe un hold depuis Stokt."""
    # Vérifier si déjà importé
    existing = db.query(Hold).filter(Hold.stokt_id == data.stokt_id).first()
    if existing:
        return {"id": existing.id, "status": "exists"}

    # Trouver la face
    face = db.query(Face).filter(Face.stokt_id == data.face_stokt_id).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    hold = Hold(
        stokt_id=data.stokt_id,
        face_id=face.id,
        polygon_str=data.polygon_str,
        centroid_x=data.centroid_x,
        centroid_y=data.centroid_y,
        area=data.area,
        path_str=data.path_str,
    )
    db.add(hold)
    db.commit()
    db.refresh(hold)

    return {"id": hold.id, "status": "created"}


@router.post("/import/climb")
def import_climb(data: ImportClimbRequest, db: Session = Depends(get_db)):
    """Importe un climb depuis Stokt."""
    # Vérifier si déjà importé
    existing = db.query(Climb).filter(Climb.stokt_id == data.stokt_id).first()
    if existing:
        # Optionnel : mettre à jour les stats
        existing.climbed_by = data.climbed_by
        existing.total_likes = data.total_likes
        existing.synced_at = datetime.utcnow()
        db.commit()
        return {"id": str(existing.id), "status": "updated"}

    # Trouver la face
    face = db.query(Face).filter(Face.stokt_id == data.face_stokt_id).first()
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    # Trouver le setter (optionnel)
    setter = None
    if data.setter_stokt_id:
        setter = db.query(User).filter(User.stokt_id == data.setter_stokt_id).first()

    climb = Climb(
        stokt_id=data.stokt_id,
        face_id=face.id,
        setter_id=setter.id if setter else None,
        name=data.name,
        holds_list=data.holds_list,
        grade_font=data.grade_font,
        grade_ircra=data.grade_ircra,
        feet_rule=data.feet_rule,
        description=data.description,
        is_private=data.is_private,
        climbed_by=data.climbed_by,
        total_likes=data.total_likes,
        source="stokt",
        synced_at=datetime.utcnow(),
    )
    db.add(climb)
    db.commit()
    db.refresh(climb)

    # Log mapping
    mapping = IdMapping(
        entity_type="climb",
        mastoc_id=climb.id,
        stokt_id=data.stokt_id,
        sync_direction="stokt_to_mastoc",
    )
    db.add(mapping)
    db.commit()

    return {"id": str(climb.id), "status": "created"}


class ImportGymRequest(BaseModel):
    """Données pour importer un gym depuis Stokt."""
    stokt_id: UUID
    display_name: str
    location_string: str | None = None


@router.post("/import/gym")
def import_gym(data: ImportGymRequest, db: Session = Depends(get_db)):
    """Importe un gym depuis Stokt."""
    existing = db.query(Gym).filter(Gym.stokt_id == data.stokt_id).first()
    if existing:
        return {"id": str(existing.id), "status": "exists"}

    gym = Gym(
        stokt_id=data.stokt_id,
        display_name=data.display_name,
        location_string=data.location_string,
        source="stokt",
    )
    db.add(gym)
    db.commit()
    db.refresh(gym)

    return {"id": str(gym.id), "status": "created"}
