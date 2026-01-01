"""
Endpoints pour les annotations de prises.

ADR-008 : Système d'annotations crowd-sourcées avec consensus.
"""

from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from pydantic import BaseModel

from mastoc_api.database import get_db
from mastoc_api.models import Hold, User, HoldAnnotation
from mastoc_api.dependencies import (
    get_current_user_optional,
    get_current_active_user,
    AuthenticatedUser,
)

router = APIRouter(prefix="/holds", tags=["hold_annotations"])


# --- Schemas Pydantic ---

class AnnotationInput(BaseModel):
    """Données d'annotation en entrée."""
    grip_type: Optional[str] = None
    condition: Optional[str] = None
    difficulty: Optional[str] = None
    notes: Optional[str] = None


class UserAnnotationResponse(BaseModel):
    """Annotation de l'utilisateur courant."""
    grip_type: Optional[str] = None
    condition: Optional[str] = None
    difficulty: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConsensusResponse(BaseModel):
    """Consensus communautaire pour une prise."""
    grip_type: Optional[str] = None
    grip_type_votes: int = 0
    grip_type_confidence: float = 0.0
    condition: Optional[str] = None
    condition_votes: int = 0
    condition_confidence: float = 0.0
    difficulty: Optional[str] = None
    difficulty_votes: int = 0
    difficulty_confidence: float = 0.0
    total_annotators: int = 0


class HoldAnnotationsResponse(BaseModel):
    """Réponse complète pour une prise."""
    hold_id: int
    consensus: ConsensusResponse
    user_annotation: Optional[UserAnnotationResponse] = None


class BatchAnnotationsRequest(BaseModel):
    """Requête batch pour plusieurs prises."""
    hold_ids: list[int]


class BatchAnnotationsResponse(BaseModel):
    """Réponse batch pour plusieurs prises."""
    annotations: dict[int, HoldAnnotationsResponse]


# --- Helpers ---

def _calculate_consensus(db: Session, hold_id: int) -> ConsensusResponse:
    """
    Calcule le consensus pour une prise.

    Le consensus est la valeur modale (la plus fréquente).
    La confiance = votes_mode / total_votes.
    """
    # Récupérer toutes les annotations pour cette prise
    query = select(HoldAnnotation).where(HoldAnnotation.hold_id == hold_id)
    annotations = db.execute(query).scalars().all()

    if not annotations:
        return ConsensusResponse()

    total = len(annotations)

    # Calculer le mode pour chaque dimension
    def get_mode(values: list[str]) -> tuple[Optional[str], int, float]:
        """Retourne (mode, votes, confidence)."""
        if not values:
            return None, 0, 0.0
        counts = {}
        for v in values:
            counts[v] = counts.get(v, 0) + 1
        if not counts:
            return None, 0, 0.0
        mode_val = max(counts, key=counts.get)
        mode_count = counts[mode_val]
        confidence = mode_count / len(values) if values else 0.0
        return mode_val, mode_count, confidence

    grip_types = [a.grip_type for a in annotations if a.grip_type]
    conditions = [a.condition for a in annotations if a.condition]
    difficulties = [a.difficulty for a in annotations if a.difficulty]

    grip_mode, grip_votes, grip_conf = get_mode(grip_types)
    cond_mode, cond_votes, cond_conf = get_mode(conditions)
    diff_mode, diff_votes, diff_conf = get_mode(difficulties)

    return ConsensusResponse(
        grip_type=grip_mode,
        grip_type_votes=grip_votes,
        grip_type_confidence=round(grip_conf, 2),
        condition=cond_mode,
        condition_votes=cond_votes,
        condition_confidence=round(cond_conf, 2),
        difficulty=diff_mode,
        difficulty_votes=diff_votes,
        difficulty_confidence=round(diff_conf, 2),
        total_annotators=total,
    )


def _get_user_annotation(
    db: Session,
    hold_id: int,
    user: Optional[User]
) -> Optional[UserAnnotationResponse]:
    """Récupère l'annotation de l'utilisateur courant."""
    if not user:
        return None

    query = select(HoldAnnotation).where(
        HoldAnnotation.hold_id == hold_id,
        HoldAnnotation.user_id == user.id
    )
    annotation = db.execute(query).scalar_one_or_none()

    if not annotation:
        return None

    return UserAnnotationResponse(
        grip_type=annotation.grip_type,
        condition=annotation.condition,
        difficulty=annotation.difficulty,
        notes=annotation.notes,
        created_at=annotation.created_at,
        updated_at=annotation.updated_at,
    )


# --- Endpoints ---

@router.get("/{hold_id}/annotations", response_model=HoldAnnotationsResponse)
def get_hold_annotations(
    hold_id: int,
    db: Session = Depends(get_db),
    auth_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
):
    """
    Récupère les annotations d'une prise.

    Retourne le consensus communautaire et l'annotation de l'utilisateur courant
    (si authentifié par JWT).
    """
    # Vérifier que la prise existe
    hold = db.get(Hold, hold_id)
    if not hold:
        raise HTTPException(status_code=404, detail="Hold not found")

    consensus = _calculate_consensus(db, hold_id)
    user = auth_user.user if auth_user and not auth_user.is_api_key else None
    user_annotation = _get_user_annotation(db, hold_id, user)

    return HoldAnnotationsResponse(
        hold_id=hold_id,
        consensus=consensus,
        user_annotation=user_annotation,
    )


@router.put("/{hold_id}/annotations", response_model=UserAnnotationResponse)
def set_hold_annotation(
    hold_id: int,
    data: AnnotationInput,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Crée ou modifie l'annotation de l'utilisateur pour une prise.

    Requiert une authentification JWT.
    """
    # Vérifier que la prise existe
    hold = db.get(Hold, hold_id)
    if not hold:
        raise HTTPException(status_code=404, detail="Hold not found")

    # Chercher annotation existante
    query = select(HoldAnnotation).where(
        HoldAnnotation.hold_id == hold_id,
        HoldAnnotation.user_id == user.id
    )
    annotation = db.execute(query).scalar_one_or_none()

    if annotation:
        # Mise à jour
        if data.grip_type is not None:
            annotation.grip_type = data.grip_type if data.grip_type else None
        if data.condition is not None:
            annotation.condition = data.condition if data.condition else None
        if data.difficulty is not None:
            annotation.difficulty = data.difficulty if data.difficulty else None
        if data.notes is not None:
            annotation.notes = data.notes if data.notes else None
        annotation.updated_at = datetime.utcnow()
    else:
        # Création
        annotation = HoldAnnotation(
            hold_id=hold_id,
            user_id=user.id,
            grip_type=data.grip_type,
            condition=data.condition,
            difficulty=data.difficulty,
            notes=data.notes,
        )
        db.add(annotation)

    db.commit()
    db.refresh(annotation)

    return UserAnnotationResponse(
        grip_type=annotation.grip_type,
        condition=annotation.condition,
        difficulty=annotation.difficulty,
        notes=annotation.notes,
        created_at=annotation.created_at,
        updated_at=annotation.updated_at,
    )


@router.delete("/{hold_id}/annotations", status_code=204)
def delete_hold_annotation(
    hold_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_active_user),
):
    """
    Supprime l'annotation de l'utilisateur pour une prise.

    Requiert une authentification JWT.
    """
    query = select(HoldAnnotation).where(
        HoldAnnotation.hold_id == hold_id,
        HoldAnnotation.user_id == user.id
    )
    annotation = db.execute(query).scalar_one_or_none()

    if not annotation:
        raise HTTPException(status_code=404, detail="Annotation not found")

    db.delete(annotation)
    db.commit()


@router.post("/annotations/batch", response_model=BatchAnnotationsResponse)
def get_annotations_batch(
    data: BatchAnnotationsRequest,
    db: Session = Depends(get_db),
    auth_user: Optional[AuthenticatedUser] = Depends(get_current_user_optional),
):
    """
    Récupère les annotations pour plusieurs prises.

    Utile pour charger les annotations de toutes les prises d'un mur.
    """
    if len(data.hold_ids) > 1000:
        raise HTTPException(
            status_code=400,
            detail="Maximum 1000 hold_ids par requête"
        )

    user = auth_user.user if auth_user and not auth_user.is_api_key else None

    annotations = {}
    for hold_id in data.hold_ids:
        # Vérifier que la prise existe
        hold = db.get(Hold, hold_id)
        if not hold:
            continue

        consensus = _calculate_consensus(db, hold_id)
        user_annotation = _get_user_annotation(db, hold_id, user)

        annotations[hold_id] = HoldAnnotationsResponse(
            hold_id=hold_id,
            consensus=consensus,
            user_annotation=user_annotation,
        )

    return BatchAnnotationsResponse(annotations=annotations)
