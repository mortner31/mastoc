"""
Endpoints pour les climbs (blocs).
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel

from mastoc_api.database import get_db
from mastoc_api.models import Climb, Face, User

router = APIRouter(prefix="/api/climbs", tags=["climbs"])


# --- Schemas Pydantic ---

class ClimbBase(BaseModel):
    """Données de base d'un climb."""
    name: str
    holds_list: str
    grade_font: Optional[str] = None
    grade_ircra: Optional[float] = None
    feet_rule: Optional[str] = None
    description: Optional[str] = None
    is_private: bool = False


class ClimbCreate(ClimbBase):
    """Création d'un climb."""
    face_id: UUID


class ClimbUpdate(BaseModel):
    """Mise à jour d'un climb."""
    name: Optional[str] = None
    holds_list: Optional[str] = None
    grade_font: Optional[str] = None
    description: Optional[str] = None
    is_private: Optional[bool] = None
    personal_notes: Optional[str] = None
    personal_rating: Optional[int] = None
    is_project: Optional[bool] = None


class ClimbResponse(ClimbBase):
    """Réponse climb."""
    id: UUID
    stokt_id: Optional[UUID] = None
    face_id: UUID
    setter_id: Optional[UUID] = None
    setter_name: Optional[str] = None
    climbed_by: int = 0
    total_likes: int = 0
    source: str
    personal_notes: Optional[str] = None
    is_project: bool = False

    class Config:
        from_attributes = True


class ClimbsListResponse(BaseModel):
    """Liste paginée de climbs."""
    results: list[ClimbResponse]
    count: int
    page: int
    page_size: int


# --- Endpoints ---

@router.get("", response_model=ClimbsListResponse)
def list_climbs(
    face_id: Optional[UUID] = None,
    grade_min: Optional[str] = None,
    grade_max: Optional[str] = None,
    setter_id: Optional[UUID] = None,
    search: Optional[str] = None,
    source: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """Liste les climbs avec filtres."""
    query = select(Climb)

    if face_id:
        query = query.where(Climb.face_id == face_id)
    if setter_id:
        query = query.where(Climb.setter_id == setter_id)
    if source:
        query = query.where(Climb.source == source)
    if search:
        query = query.where(Climb.name.ilike(f"%{search}%"))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = db.execute(count_query).scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    climbs = db.execute(query).scalars().all()

    results = []
    for climb in climbs:
        resp = ClimbResponse(
            id=climb.id,
            stokt_id=climb.stokt_id,
            face_id=climb.face_id,
            setter_id=climb.setter_id,
            setter_name=climb.setter.full_name if climb.setter else None,
            name=climb.name,
            holds_list=climb.holds_list,
            grade_font=climb.grade_font,
            grade_ircra=climb.grade_ircra,
            feet_rule=climb.feet_rule,
            description=climb.description,
            is_private=climb.is_private,
            climbed_by=climb.climbed_by,
            total_likes=climb.total_likes,
            source=climb.source,
            personal_notes=climb.personal_notes,
            is_project=climb.is_project,
        )
        results.append(resp)

    return ClimbsListResponse(
        results=results,
        count=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{climb_id}", response_model=ClimbResponse)
def get_climb(climb_id: UUID, db: Session = Depends(get_db)):
    """Récupère un climb par ID."""
    climb = db.get(Climb, climb_id)
    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    return ClimbResponse(
        id=climb.id,
        stokt_id=climb.stokt_id,
        face_id=climb.face_id,
        setter_id=climb.setter_id,
        setter_name=climb.setter.full_name if climb.setter else None,
        name=climb.name,
        holds_list=climb.holds_list,
        grade_font=climb.grade_font,
        grade_ircra=climb.grade_ircra,
        feet_rule=climb.feet_rule,
        description=climb.description,
        is_private=climb.is_private,
        climbed_by=climb.climbed_by,
        total_likes=climb.total_likes,
        source=climb.source,
        personal_notes=climb.personal_notes,
        is_project=climb.is_project,
    )


@router.get("/by-stokt-id/{stokt_id}", response_model=ClimbResponse)
def get_climb_by_stokt_id(stokt_id: UUID, db: Session = Depends(get_db)):
    """Récupère un climb par son ID Stokt."""
    query = select(Climb).where(Climb.stokt_id == stokt_id)
    climb = db.execute(query).scalar_one_or_none()
    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    return ClimbResponse(
        id=climb.id,
        stokt_id=climb.stokt_id,
        face_id=climb.face_id,
        setter_id=climb.setter_id,
        setter_name=climb.setter.full_name if climb.setter else None,
        name=climb.name,
        holds_list=climb.holds_list,
        grade_font=climb.grade_font,
        grade_ircra=climb.grade_ircra,
        feet_rule=climb.feet_rule,
        description=climb.description,
        is_private=climb.is_private,
        climbed_by=climb.climbed_by,
        total_likes=climb.total_likes,
        source=climb.source,
        personal_notes=climb.personal_notes,
        is_project=climb.is_project,
    )


@router.post("", response_model=ClimbResponse, status_code=201)
def create_climb(climb_data: ClimbCreate, db: Session = Depends(get_db)):
    """Crée un nouveau climb."""
    # Vérifier que la face existe
    face = db.get(Face, climb_data.face_id)
    if not face:
        raise HTTPException(status_code=404, detail="Face not found")

    climb = Climb(
        face_id=climb_data.face_id,
        name=climb_data.name,
        holds_list=climb_data.holds_list,
        grade_font=climb_data.grade_font,
        grade_ircra=climb_data.grade_ircra,
        feet_rule=climb_data.feet_rule,
        description=climb_data.description,
        is_private=climb_data.is_private,
        source="mastoc",
        stokt_id=None,  # Pas encore sync
    )

    db.add(climb)
    db.commit()
    db.refresh(climb)

    return ClimbResponse(
        id=climb.id,
        stokt_id=climb.stokt_id,
        face_id=climb.face_id,
        setter_id=climb.setter_id,
        setter_name=None,
        name=climb.name,
        holds_list=climb.holds_list,
        grade_font=climb.grade_font,
        grade_ircra=climb.grade_ircra,
        feet_rule=climb.feet_rule,
        description=climb.description,
        is_private=climb.is_private,
        climbed_by=climb.climbed_by,
        total_likes=climb.total_likes,
        source=climb.source,
        personal_notes=climb.personal_notes,
        is_project=climb.is_project,
    )


@router.patch("/{climb_id}", response_model=ClimbResponse)
def update_climb(
    climb_id: UUID,
    climb_data: ClimbUpdate,
    db: Session = Depends(get_db),
):
    """Met à jour un climb."""
    climb = db.get(Climb, climb_id)
    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    update_data = climb_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(climb, field, value)

    db.commit()
    db.refresh(climb)

    return ClimbResponse(
        id=climb.id,
        stokt_id=climb.stokt_id,
        face_id=climb.face_id,
        setter_id=climb.setter_id,
        setter_name=climb.setter.full_name if climb.setter else None,
        name=climb.name,
        holds_list=climb.holds_list,
        grade_font=climb.grade_font,
        grade_ircra=climb.grade_ircra,
        feet_rule=climb.feet_rule,
        description=climb.description,
        is_private=climb.is_private,
        climbed_by=climb.climbed_by,
        total_likes=climb.total_likes,
        source=climb.source,
        personal_notes=climb.personal_notes,
        is_project=climb.is_project,
    )


@router.delete("/{climb_id}", status_code=204)
def delete_climb(climb_id: UUID, db: Session = Depends(get_db)):
    """Supprime un climb."""
    climb = db.get(Climb, climb_id)
    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    db.delete(climb)
    db.commit()


@router.patch("/{climb_id}/stokt-id")
def update_stokt_id(
    climb_id: UUID,
    stokt_id: UUID,
    db: Session = Depends(get_db),
):
    """Met à jour le stokt_id d'un climb (après push vers Stokt)."""
    climb = db.get(Climb, climb_id)
    if not climb:
        raise HTTPException(status_code=404, detail="Climb not found")

    climb.stokt_id = stokt_id
    db.commit()

    return {"message": "stokt_id updated", "stokt_id": str(stokt_id)}
