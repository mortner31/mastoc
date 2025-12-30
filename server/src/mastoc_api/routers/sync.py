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

router = APIRouter(prefix="/sync", tags=["sync"])


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


class BatchImportHoldsRequest(BaseModel):
    """Batch import de holds."""
    holds: list[ImportHoldRequest]


@router.post("/import/holds/batch", response_model=BatchImportResult)
def import_holds_batch(data: BatchImportHoldsRequest, db: Session = Depends(get_db)):
    """Importe plusieurs holds en une seule transaction."""
    created = 0
    updated = 0
    errors = 0

    # Pré-charger les faces
    face_stokt_ids = {h.face_stokt_id for h in data.holds}
    faces = db.query(Face).filter(Face.stokt_id.in_(face_stokt_ids)).all()
    face_map = {f.stokt_id: f for f in faces}

    # Pré-charger les holds existants
    hold_stokt_ids = {h.stokt_id for h in data.holds}
    existing_holds = db.query(Hold).filter(Hold.stokt_id.in_(hold_stokt_ids)).all()
    existing_map = {h.stokt_id: h for h in existing_holds}

    for hold_data in data.holds:
        try:
            if hold_data.stokt_id in existing_map:
                updated += 1
                continue

            face = face_map.get(hold_data.face_stokt_id)
            if not face:
                errors += 1
                continue

            hold = Hold(
                stokt_id=hold_data.stokt_id,
                face_id=face.id,
                polygon_str=hold_data.polygon_str,
                centroid_x=hold_data.centroid_x,
                centroid_y=hold_data.centroid_y,
                area=hold_data.area,
                path_str=hold_data.path_str,
            )
            db.add(hold)
            created += 1

        except Exception:
            errors += 1

    db.commit()
    return BatchImportResult(created=created, updated=updated, errors=errors, total=len(data.holds))


class BatchImportUsersRequest(BaseModel):
    """Batch import de users."""
    users: list[ImportUserRequest]


@router.post("/import/users/batch", response_model=BatchImportResult)
def import_users_batch(data: BatchImportUsersRequest, db: Session = Depends(get_db)):
    """Importe plusieurs users en une seule transaction."""
    created = 0
    updated = 0
    errors = 0

    # Pré-charger les users existants
    user_stokt_ids = {u.stokt_id for u in data.users}
    existing_users = db.query(User).filter(User.stokt_id.in_(user_stokt_ids)).all()
    existing_map = {u.stokt_id: u for u in existing_users}

    for user_data in data.users:
        try:
            if user_data.stokt_id in existing_map:
                updated += 1
                continue

            user = User(
                stokt_id=user_data.stokt_id,
                full_name=user_data.full_name,
                avatar_path=user_data.avatar_path,
                source="stokt",
            )
            db.add(user)
            created += 1

        except Exception:
            errors += 1

    db.commit()
    return BatchImportResult(created=created, updated=updated, errors=errors, total=len(data.users))


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


class BatchImportClimbsRequest(BaseModel):
    """Batch import de climbs."""
    climbs: list[ImportClimbRequest]


class BatchImportResult(BaseModel):
    """Résultat du batch import."""
    created: int
    updated: int
    errors: int
    total: int


@router.post("/import/climbs/batch", response_model=BatchImportResult)
def import_climbs_batch(data: BatchImportClimbsRequest, db: Session = Depends(get_db)):
    """Importe plusieurs climbs en une seule transaction."""
    created = 0
    updated = 0
    errors = 0

    # Pré-charger les faces et users pour éviter les requêtes N+1
    face_stokt_ids = {c.face_stokt_id for c in data.climbs}
    faces = db.query(Face).filter(Face.stokt_id.in_(face_stokt_ids)).all()
    face_map = {f.stokt_id: f for f in faces}

    setter_stokt_ids = {c.setter_stokt_id for c in data.climbs if c.setter_stokt_id}
    users = db.query(User).filter(User.stokt_id.in_(setter_stokt_ids)).all()
    user_map = {u.stokt_id: u for u in users}

    # Pré-charger les climbs existants
    climb_stokt_ids = {c.stokt_id for c in data.climbs}
    existing_climbs = db.query(Climb).filter(Climb.stokt_id.in_(climb_stokt_ids)).all()
    existing_map = {c.stokt_id: c for c in existing_climbs}

    for climb_data in data.climbs:
        try:
            # Vérifier si déjà importé
            if climb_data.stokt_id in existing_map:
                existing = existing_map[climb_data.stokt_id]
                existing.climbed_by = climb_data.climbed_by
                existing.total_likes = climb_data.total_likes
                existing.synced_at = datetime.utcnow()
                updated += 1
                continue

            # Trouver la face
            face = face_map.get(climb_data.face_stokt_id)
            if not face:
                errors += 1
                continue

            # Trouver le setter
            setter = user_map.get(climb_data.setter_stokt_id) if climb_data.setter_stokt_id else None

            climb = Climb(
                stokt_id=climb_data.stokt_id,
                face_id=face.id,
                setter_id=setter.id if setter else None,
                name=climb_data.name,
                holds_list=climb_data.holds_list,
                grade_font=climb_data.grade_font,
                grade_ircra=climb_data.grade_ircra,
                feet_rule=climb_data.feet_rule,
                description=climb_data.description,
                is_private=climb_data.is_private,
                climbed_by=climb_data.climbed_by,
                total_likes=climb_data.total_likes,
                source="stokt",
                synced_at=datetime.utcnow(),
            )
            db.add(climb)
            created += 1

        except Exception:
            errors += 1

    db.commit()
    return BatchImportResult(
        created=created,
        updated=updated,
        errors=errors,
        total=len(data.climbs),
    )


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
