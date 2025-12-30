"""
Endpoints pour les holds (prises).
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import BaseModel

from mastoc_api.database import get_db
from mastoc_api.models import Hold, Face

router = APIRouter(prefix="/holds", tags=["holds"])


# --- Schemas Pydantic ---

class HoldResponse(BaseModel):
    """Réponse hold."""
    id: int
    stokt_id: Optional[int] = None
    face_id: UUID
    polygon_str: str
    centroid_x: Optional[float] = None
    centroid_y: Optional[float] = None
    area: Optional[float] = None

    class Config:
        from_attributes = True


class HoldsListResponse(BaseModel):
    """Liste de holds."""
    results: list[HoldResponse]
    count: int


# --- Endpoints ---

@router.get("", response_model=HoldsListResponse)
def list_holds(
    face_id: UUID,
    db: Session = Depends(get_db),
):
    """Liste les holds d'une face."""
    query = select(Hold).where(Hold.face_id == face_id)
    holds = db.execute(query).scalars().all()

    results = [
        HoldResponse(
            id=h.id,
            stokt_id=h.stokt_id,
            face_id=h.face_id,
            polygon_str=h.polygon_str,
            centroid_x=h.centroid_x,
            centroid_y=h.centroid_y,
            area=h.area,
        )
        for h in holds
    ]

    return HoldsListResponse(results=results, count=len(results))


@router.get("/{hold_id}", response_model=HoldResponse)
def get_hold(hold_id: int, db: Session = Depends(get_db)):
    """Récupère un hold par ID."""
    hold = db.get(Hold, hold_id)
    if not hold:
        raise HTTPException(status_code=404, detail="Hold not found")

    return HoldResponse(
        id=hold.id,
        stokt_id=hold.stokt_id,
        face_id=hold.face_id,
        polygon_str=hold.polygon_str,
        centroid_x=hold.centroid_x,
        centroid_y=hold.centroid_y,
        area=hold.area,
    )


@router.get("/by-stokt-id/{stokt_id}", response_model=HoldResponse)
def get_hold_by_stokt_id(stokt_id: int, db: Session = Depends(get_db)):
    """Récupère un hold par son ID Stokt."""
    query = select(Hold).where(Hold.stokt_id == stokt_id)
    hold = db.execute(query).scalar_one_or_none()
    if not hold:
        raise HTTPException(status_code=404, detail="Hold not found")

    return HoldResponse(
        id=hold.id,
        stokt_id=hold.stokt_id,
        face_id=hold.face_id,
        polygon_str=hold.polygon_str,
        centroid_x=hold.centroid_x,
        centroid_y=hold.centroid_y,
        area=hold.area,
    )
