"""
Modèles de données pour l'API Stokt.

Ces dataclasses correspondent aux structures JSON retournées par l'API.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class HoldType(Enum):
    """Type de prise dans un climb."""
    START = "S"  # Prise de départ
    OTHER = "O"  # Prise normale
    FEET = "F"   # Prise de pied obligatoire
    TOP = "T"    # Prise finale


# =============================================================================
# Modèles pour les interactions sociales (TODO 07)
# =============================================================================

@dataclass
class UserRef:
    """Référence à un utilisateur (pour likes, comments, sends)."""
    id: str
    full_name: str
    avatar: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "UserRef":
        """Crée un UserRef depuis la réponse API."""
        return cls(
            id=data.get("id", ""),
            full_name=data.get("fullName", data.get("full_name", "")),
            avatar=data.get("avatar")
        )


@dataclass
class Effort:
    """Ascension d'un climb par un utilisateur."""
    id: str
    climb_id: str
    user: UserRef
    date: str
    is_flash: bool = False
    attempts: Optional[int] = None
    grade_feel: int = 0  # -1 (soft), 0 (ok), +1 (hard)

    @classmethod
    def from_api(cls, data: dict) -> "Effort":
        """Crée un Effort depuis la réponse API."""
        # L'API utilise "effortBy" pour l'utilisateur, pas "user"
        user_data = data.get("effortBy", data.get("user", {}))
        return cls(
            id=data.get("id", ""),
            climb_id=data.get("climbId", data.get("climb_id", "")),
            user=UserRef.from_api(user_data),
            # L'API utilise "effortDate" pas "date"
            date=data.get("effortDate", data.get("date", data.get("dateCreated", ""))),
            is_flash=data.get("isFlash", data.get("is_flash", False)),
            attempts=data.get("attemptsNumber", data.get("attempts")),
            grade_feel=data.get("gradeFeel", data.get("grade_feel", 0)),
        )


@dataclass
class Comment:
    """Commentaire sur un climb."""
    id: str
    climb_id: str
    user: UserRef
    text: str
    date: str
    replied_to_id: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "Comment":
        """Crée un Comment depuis la réponse API."""
        user_data = data.get("user", {})
        return cls(
            id=data.get("id", ""),
            climb_id=data.get("climbId", data.get("climb_id", "")),
            user=UserRef.from_api(user_data),
            text=data.get("text", ""),
            date=data.get("date", data.get("dateCreated", "")),
            replied_to_id=data.get("repliedToId", data.get("replied_to_id")),
        )


@dataclass
class Like:
    """Like sur un climb."""
    user: UserRef
    date: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "Like":
        """Crée un Like depuis la réponse API."""
        # L'API peut retourner directement les infos user ou un objet user
        if "user" in data:
            user = UserRef.from_api(data["user"])
        else:
            user = UserRef.from_api(data)
        return cls(
            user=user,
            date=data.get("date", data.get("dateCreated")),
        )


@dataclass
class ClimbSetter:
    """Créateur d'un climb."""
    id: str
    full_name: str
    avatar: Optional[str] = None


@dataclass
class Grade:
    """Note de difficulté (système de notation)."""
    ircra: float  # IRCRA (0-30+)
    hueco: str    # USA (V0-V17)
    font: str     # Fontainebleau (4-9A)
    dankyu: str   # Japon (6Q-6D)


@dataclass
class ClimbHold:
    """Référence à une prise dans un climb."""
    hold_type: HoldType
    hold_id: int


@dataclass
class Climb:
    """Bloc/Problème d'escalade."""
    id: str
    name: str
    holds_list: str
    feet_rule: str
    face_id: str
    wall_id: str
    wall_name: str
    date_created: str
    is_private: bool = False
    is_benchmark: bool = False
    climbed_by: int = 0
    total_likes: int = 0
    total_comments: int = 0
    has_symmetric: bool = False
    mirror_holds_list: str = ""
    angle: str = ""
    is_angle_adjustable: bool = False
    circuit: str = ""
    tags: str = ""
    setter: Optional[ClimbSetter] = None
    grade: Optional[Grade] = None

    def get_holds(self) -> list[ClimbHold]:
        """Parse holdsList et retourne la liste des prises."""
        return parse_holds_list(self.holds_list)

    def get_mirror_holds(self) -> list[ClimbHold]:
        """Parse mirrorHoldsList et retourne la liste des prises miroir."""
        return parse_holds_list(self.mirror_holds_list)

    @classmethod
    def from_api(cls, data: dict) -> "Climb":
        """Crée un Climb depuis la réponse API."""
        setter = None
        if data.get("climbSetters"):
            s = data["climbSetters"]
            setter = ClimbSetter(
                id=s.get("id", ""),
                full_name=s.get("fullName", ""),
                avatar=s.get("avatar")
            )

        grade = None
        if data.get("crowdGrade"):
            g = data["crowdGrade"]
            grade = Grade(
                ircra=g.get("ircra", 0),
                hueco=g.get("hueco", ""),
                font=g.get("font", ""),
                dankyu=g.get("dankyu", "")
            )

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            holds_list=data.get("holdsList", ""),
            mirror_holds_list=data.get("mirrorHoldsList", ""),
            feet_rule=data.get("feetRule", ""),
            face_id=data.get("faceId", ""),
            wall_id=data.get("wallId", ""),
            wall_name=data.get("wallName", ""),
            date_created=data.get("dateCreated", ""),
            is_private=data.get("isPrivate", False),
            is_benchmark=data.get("isBenchmark", False),
            climbed_by=data.get("climbedBy", 0),
            total_likes=data.get("totalLikes", 0),
            total_comments=data.get("totalComments", 0),
            has_symmetric=data.get("hasSymmetric", False),
            angle=data.get("angle", ""),
            is_angle_adjustable=data.get("isAngleAdjustable", False),
            circuit=data.get("circuit", ""),
            tags=data.get("tags", ""),
            setter=setter,
            grade=grade,
        )


@dataclass
class Hold:
    """Prise physique sur le mur (depuis face setup)."""
    id: int
    area: float
    polygon_str: str
    touch_polygon_str: str
    path_str: str
    centroid_str: str
    top_polygon_str: str = ""
    center_tape_str: str = ""
    right_tape_str: str = ""
    left_tape_str: str = ""

    @property
    def centroid(self) -> tuple[float, float]:
        """Retourne les coordonnées du centre (x, y) en pixels."""
        parts = self.centroid_str.split()
        return float(parts[0]), float(parts[1])

    def get_polygon_points(self) -> list[tuple[float, float]]:
        """Parse polygonStr et retourne la liste des points (x, y)."""
        points = []
        for point in self.polygon_str.split():
            if "," in point:
                x, y = point.split(",")
                points.append((float(x), float(y)))
        return points

    @classmethod
    def from_api(cls, data: dict) -> "Hold":
        """Crée un Hold depuis la réponse API."""
        return cls(
            id=data.get("id", 0),
            area=float(data.get("area", 0)),
            polygon_str=data.get("polygonStr", ""),
            touch_polygon_str=data.get("touchPolygonStr", ""),
            path_str=data.get("pathStr", ""),
            centroid_str=data.get("centroidStr", "0 0"),
            top_polygon_str=data.get("topPolygonStr", ""),
            center_tape_str=data.get("centerTapeStr", ""),
            right_tape_str=data.get("rightTapeStr", ""),
            left_tape_str=data.get("leftTapeStr", ""),
        )


@dataclass
class FacePicture:
    """Image d'une face du mur."""
    name: str
    width: int
    height: int


@dataclass
class Face:
    """Face d'un mur d'escalade."""
    id: str
    is_active: bool
    total_climbs: int
    date_modified: str = ""
    gym: str = ""
    wall: str = ""
    picture: Optional[FacePicture] = None
    small_picture: Optional[FacePicture] = None
    feet_rules_options: list[str] = field(default_factory=list)
    has_symmetry: bool = False
    holds: list[Hold] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict) -> "Face":
        """Crée une Face depuis la réponse API."""
        picture = None
        if data.get("picture"):
            p = data["picture"]
            picture = FacePicture(
                name=p.get("name", ""),
                width=p.get("width", 0),
                height=p.get("height", 0)
            )

        small_picture = None
        if data.get("smallPicture"):
            p = data["smallPicture"]
            small_picture = FacePicture(
                name=p.get("name", ""),
                width=p.get("width", 0),
                height=p.get("height", 0)
            )

        holds = [Hold.from_api(h) for h in data.get("holds", [])]

        return cls(
            id=data.get("id", ""),
            is_active=data.get("isActive", True),
            total_climbs=data.get("totalClimbs", 0),
            date_modified=data.get("dateModified", ""),
            gym=data.get("gym", ""),
            wall=data.get("wall", ""),
            picture=picture,
            small_picture=small_picture,
            feet_rules_options=data.get("feetRulesOptions", []),
            has_symmetry=data.get("hasSymmetry", False),
            holds=holds,
        )


@dataclass
class Wall:
    """Mur d'escalade."""
    id: str
    name: str
    is_active: bool
    angle: Optional[str] = None
    is_angle_adjustable: bool = False
    default_angle: str = ""
    faces: list[Face] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: dict) -> "Wall":
        """Crée un Wall depuis la réponse API."""
        faces = [Face.from_api(f) for f in data.get("faces", [])]
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            is_active=data.get("isActive", True),
            angle=data.get("angle"),
            is_angle_adjustable=data.get("isAngleAdjustable", False),
            default_angle=data.get("defaultAngle", ""),
            faces=faces,
        )


@dataclass
class GymSummary:
    """Résumé d'une salle d'escalade."""
    id: str
    display_name: str
    location_string: str
    number_of_climbs: int
    number_of_climbers: int
    number_of_sends: int
    gym_type: str
    wall_type: str
    is_favorite: bool = False
    is_editable: bool = False

    @classmethod
    def from_api(cls, data: dict) -> "GymSummary":
        """Crée un GymSummary depuis la réponse API."""
        return cls(
            id=data.get("id", ""),
            display_name=data.get("displayName", ""),
            location_string=data.get("locationString", ""),
            number_of_climbs=data.get("numberOfClimbs", 0),
            number_of_climbers=data.get("numberOfClimbers", 0),
            number_of_sends=data.get("numberOfSends", 0),
            gym_type=data.get("gymType", ""),
            wall_type=data.get("wallType", ""),
            is_favorite=data.get("isFavorite", False),
            is_editable=data.get("isEditable", False),
        )


# =============================================================================
# Modèles pour les listes personnalisées (TODO 09)
# =============================================================================

@dataclass
class ClimbList:
    """Liste personnalisée de climbs."""
    id: str
    name: str
    list_type: str
    climbs_count: int
    is_following: bool = False
    gym_id: Optional[str] = None
    gym_name: Optional[str] = None
    owner_id: str = ""
    owner_name: str = ""
    owner_avatar: Optional[str] = None
    image: Optional[str] = None
    image_thumbnail: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict) -> "ClimbList":
        """Crée une ClimbList depuis la réponse API."""
        # Extraction du gym
        gym = data.get("gym")
        gym_id = gym.get("id") if isinstance(gym, dict) else None
        gym_name = gym.get("name") if isinstance(gym, dict) else gym

        # Extraction du user (owner)
        user = data.get("user", {})
        if isinstance(user, dict):
            owner_id = user.get("id", "")
            # L'API utilise parfois 'name', parfois 'fullName'
            owner_name = user.get("name", user.get("fullName", user.get("full_name", "")))
            owner_avatar = user.get("avatar", user.get("avatarThumbnail"))
        else:
            owner_id = ""
            owner_name = ""
            owner_avatar = None

        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            list_type=data.get("listType", data.get("list_type", "")),
            climbs_count=data.get("climbsCount", data.get("climbs_count", 0)),
            is_following=data.get("isFollowing", data.get("is_following", False)),
            gym_id=gym_id,
            gym_name=gym_name,
            owner_id=owner_id,
            owner_name=owner_name,
            owner_avatar=owner_avatar,
            image=data.get("image"),
            image_thumbnail=data.get("imageThumbnail", data.get("image_thumbnail")),
        )


@dataclass
class ListItem:
    """Item dans une liste (référence à un climb)."""
    id: str
    climb: Climb
    order: int = 0

    @classmethod
    def from_api(cls, data: dict) -> "ListItem":
        """Crée un ListItem depuis la réponse API."""
        # L'API peut retourner le climb directement ou imbriqué
        climb_data = data.get("climb", data)
        return cls(
            id=data.get("id", ""),
            climb=Climb.from_api(climb_data),
            order=data.get("order", 0),
        )


def parse_holds_list(holds_str: str) -> list[ClimbHold]:
    """
    Parse le format holdsList d'un climb.

    Format: "S829279 S829528 O828906 T829009"
    - S = Start (prise de départ)
    - O = Other (prise normale)
    - F = Feet (pied obligatoire)
    - T = Top (prise finale)

    Returns:
        Liste de ClimbHold
    """
    if not holds_str:
        return []

    holds = []
    for hold in holds_str.split():
        if len(hold) > 1:
            try:
                hold_type = HoldType(hold[0])
                hold_id = int(hold[1:])
                holds.append(ClimbHold(hold_type=hold_type, hold_id=hold_id))
            except (ValueError, KeyError):
                continue
    return holds
