"""
État de création de bloc.

Dataclass contenant l'état partagé entre les écrans du wizard de création.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from mastoc.api.models import HoldType


class GradeSystem(Enum):
    """Système de notation."""
    # Valeurs en minuscule pour l'API Stokt
    FONT = "font"       # Fontainebleau (4, 5+, 6A, 6A+, 7B, etc.)
    V_SCALE = "hueco"   # USA (V0, V1, V2, etc.) - API utilise "hueco"
    DANKYU = "dankyu"   # Japon (6Q, 5Q, 4D, etc.)


# Valeurs de grade par système (lettres en MAJUSCULE pour Font)
GRADE_VALUES = {
    GradeSystem.FONT: [
        "4", "4+", "5", "5+",
        "6A", "6A+", "6B", "6B+", "6C", "6C+",
        "7A", "7A+", "7B", "7B+", "7C", "7C+",
        "8A", "8A+", "8B", "8B+", "8C", "8C+",
    ],
    GradeSystem.V_SCALE: [
        "V0", "V1", "V2", "V3", "V4", "V5", "V6", "V7",
        "V8", "V9", "V10", "V11", "V12", "V13", "V14",
        "V15", "V16", "V17",
    ],
    GradeSystem.DANKYU: [
        "6Q", "5Q", "4Q", "3Q", "2Q", "1Q",
        "1D", "2D", "3D", "4D", "5D", "6D",
    ],
}


@dataclass
class HoldSelection:
    """Sélection d'une prise avec son type."""
    hold_id: int
    hold_type: HoldType

    def to_api_format(self) -> str:
        """Convertit en format API (ex: 'S829279')."""
        return f"{self.hold_type.value}{self.hold_id}"


@dataclass
class ClimbCreationState:
    """
    État de création de bloc partagé entre les écrans du wizard.

    Correspond à la structure Redux identifiée dans le code décompilé
    (lignes 414464-414505 de stokt_decompiled.js).
    """

    # === Prises sélectionnées ===
    start_holds: list[int] = field(default_factory=list)   # Min 2 requis
    other_holds: list[int] = field(default_factory=list)
    feet_holds: list[int] = field(default_factory=list)
    top_holds: list[int] = field(default_factory=list)     # Min 1 requis

    # Type de sélection actif (pour l'UI)
    selection_type: HoldType = field(default=HoldType.OTHER)

    # === Informations du bloc ===
    name: str = ""
    description: str = ""
    grade_system: GradeSystem = field(default=GradeSystem.FONT)
    grade_value: str = ""
    feet_rule: str = ""
    is_private: bool = False
    tags: list[str] = field(default_factory=list)

    # === État UI ===
    is_submitting: bool = False
    submit_error: Optional[str] = None
    created_climb_id: Optional[str] = None

    # === Face ID (contexte) ===
    face_id: str = ""

    def get_all_holds(self) -> list[HoldSelection]:
        """Retourne toutes les prises sélectionnées avec leur type."""
        holds = []
        for hold_id in self.start_holds:
            holds.append(HoldSelection(hold_id, HoldType.START))
        for hold_id in self.other_holds:
            holds.append(HoldSelection(hold_id, HoldType.OTHER))
        for hold_id in self.feet_holds:
            holds.append(HoldSelection(hold_id, HoldType.FEET))
        for hold_id in self.top_holds:
            holds.append(HoldSelection(hold_id, HoldType.TOP))
        return holds

    def get_holds_list_str(self) -> str:
        """
        Construit la chaîne holdsList pour l'API.

        Format: "S829279 S829528 O828906 F828907 T829009"
        """
        parts = []
        for hold in self.get_all_holds():
            parts.append(hold.to_api_format())
        return " ".join(parts)

    def get_holds_dict(self) -> dict:
        """
        Construit le dictionnaire holdsList pour l'API.

        Format attendu par POST api/faces/{faceId}/climbs:
        {
            "start": ["829279", "829528"],
            "others": ["828906"],
            "top": ["829009"],
            "feetOnly": ["828907"]
        }
        """
        return {
            "start": [str(h) for h in self.start_holds],
            "others": [str(h) for h in self.other_holds],
            "top": [str(h) for h in self.top_holds],
            "feetOnly": [str(h) for h in self.feet_holds],
        }

    def add_hold(self, hold_id: int, hold_type: Optional[HoldType] = None):
        """
        Ajoute une prise avec le type spécifié ou le type actif.

        Si la prise existe déjà dans un autre type, elle est déplacée.
        """
        if hold_type is None:
            hold_type = self.selection_type

        # Retirer des autres listes si présent
        self.remove_hold(hold_id)

        # Ajouter dans la bonne liste
        if hold_type == HoldType.START:
            self.start_holds.append(hold_id)
        elif hold_type == HoldType.OTHER:
            self.other_holds.append(hold_id)
        elif hold_type == HoldType.FEET:
            self.feet_holds.append(hold_id)
        elif hold_type == HoldType.TOP:
            self.top_holds.append(hold_id)

    def remove_hold(self, hold_id: int) -> Optional[HoldType]:
        """
        Retire une prise de toutes les listes.

        Returns:
            Le type de la prise si elle existait, None sinon.
        """
        if hold_id in self.start_holds:
            self.start_holds.remove(hold_id)
            return HoldType.START
        if hold_id in self.other_holds:
            self.other_holds.remove(hold_id)
            return HoldType.OTHER
        if hold_id in self.feet_holds:
            self.feet_holds.remove(hold_id)
            return HoldType.FEET
        if hold_id in self.top_holds:
            self.top_holds.remove(hold_id)
            return HoldType.TOP
        return None

    def get_hold_type(self, hold_id: int) -> Optional[HoldType]:
        """Retourne le type d'une prise, ou None si non sélectionnée."""
        if hold_id in self.start_holds:
            return HoldType.START
        if hold_id in self.other_holds:
            return HoldType.OTHER
        if hold_id in self.feet_holds:
            return HoldType.FEET
        if hold_id in self.top_holds:
            return HoldType.TOP
        return None

    def total_holds(self) -> int:
        """Nombre total de prises sélectionnées."""
        return (
            len(self.start_holds)
            + len(self.other_holds)
            + len(self.feet_holds)
            + len(self.top_holds)
        )

    def is_valid_for_submit(self) -> tuple[bool, list[str]]:
        """
        Vérifie si l'état est valide pour soumission.

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Validations des prises (lignes 903059-903110 du code décompilé)
        if len(self.start_holds) < 2:
            errors.append("Minimum 2 prises de départ (START)")
        if len(self.top_holds) < 1:
            errors.append("Minimum 1 prise d'arrivée (TOP)")

        # Validations du nom (lignes 952433-952500)
        if not self.name:
            errors.append("Le nom est requis")
        elif len(self.name) < 3:
            errors.append("Le nom doit avoir au moins 3 caractères")

        # Validation du grade
        if not self.grade_value:
            errors.append("Le grade est requis")

        return len(errors) == 0, errors

    def can_go_to_info_screen(self) -> tuple[bool, list[str]]:
        """
        Vérifie si on peut passer à l'écran d'informations.

        Returns:
            (can_proceed, list_of_errors)
        """
        errors = []
        if len(self.start_holds) < 2:
            errors.append("Minimum 2 prises de départ (START)")
        if len(self.top_holds) < 1:
            errors.append("Minimum 1 prise d'arrivée (TOP)")
        return len(errors) == 0, errors

    def to_api_payload(self) -> dict:
        """
        Construit le payload pour POST api/faces/{faceId}/climbs.

        Correspond à la structure identifiée (lignes 952298-952325).
        """
        payload = {
            # Obligatoires
            "name": self.name,
            "holdsList": self.get_holds_dict(),
            "grade": {
                "gradingSystem": self.grade_system.value,  # "font", "hueco", "dankyu"
                "value": self.grade_value,                  # "6A+", "V5", "3D"
            },
            "attemptsNumber": None,  # Requis par l'API
            # Optionnels
            "isPrivate": self.is_private,
        }

        if self.description:
            payload["description"] = self.description

        if self.feet_rule:
            payload["feetRule"] = self.feet_rule

        if self.tags:
            payload["tags_list"] = self.tags

        return payload

    def reset(self):
        """Réinitialise l'état pour une nouvelle création."""
        self.start_holds.clear()
        self.other_holds.clear()
        self.feet_holds.clear()
        self.top_holds.clear()
        self.selection_type = HoldType.OTHER
        self.name = ""
        self.description = ""
        self.grade_system = GradeSystem.FONT
        self.grade_value = ""
        self.feet_rule = ""
        self.is_private = False
        self.tags.clear()
        self.is_submitting = False
        self.submit_error = None
        self.created_climb_id = None
