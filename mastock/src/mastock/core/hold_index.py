"""
Index pour le mapping prises ↔ blocs et grades.

Optimise les recherches pour le filtrage par prises.
"""

from collections import defaultdict
from typing import Optional

from mastock.api.models import Climb, Hold
from mastock.db import Database, ClimbRepository, HoldRepository


class HoldClimbIndex:
    """Index bidirectionnel prises ↔ blocs."""

    def __init__(self):
        # Prise → liste de blocs
        self.hold_to_climbs: dict[int, list[str]] = defaultdict(list)

        # Bloc → grade IRCRA
        self.climb_grades: dict[str, float] = {}

        # Bloc → données complètes
        self.climbs: dict[str, Climb] = {}

        # Prises
        self.holds: dict[int, Hold] = {}

    @classmethod
    def from_database(cls, db: Database) -> "HoldClimbIndex":
        """Crée l'index depuis la base de données."""
        index = cls()

        climb_repo = ClimbRepository(db)
        hold_repo = HoldRepository(db)

        # Charger toutes les prises
        holds = hold_repo.get_all_holds()
        for hold in holds:
            index.holds[hold.id] = hold

        # Charger tous les climbs
        climbs = climb_repo.get_all_climbs()
        for climb in climbs:
            index.climbs[climb.id] = climb

            # Grade
            if climb.grade:
                index.climb_grades[climb.id] = climb.grade.ircra
            else:
                # Pas de grade = exclu du filtrage par niveau
                index.climb_grades[climb.id] = 0

            # Index prise → blocs
            for ch in climb.get_holds():
                index.hold_to_climbs[ch.hold_id].append(climb.id)

        return index

    def get_climbs_for_hold(self, hold_id: int) -> list[Climb]:
        """Retourne les blocs contenant une prise."""
        climb_ids = self.hold_to_climbs.get(hold_id, [])
        return [self.climbs[cid] for cid in climb_ids if cid in self.climbs]

    def get_climbs_for_holds(self, hold_ids: list[int]) -> list[Climb]:
        """Retourne les blocs contenant TOUTES les prises spécifiées."""
        if not hold_ids:
            return list(self.climbs.values())

        # Intersection des blocs pour chaque prise
        result_ids = None
        for hold_id in hold_ids:
            climb_ids = set(self.hold_to_climbs.get(hold_id, []))
            if result_ids is None:
                result_ids = climb_ids
            else:
                result_ids &= climb_ids

        if not result_ids:
            return []

        return [self.climbs[cid] for cid in result_ids if cid in self.climbs]

    def get_climbs_in_grade_range(
        self,
        min_ircra: float,
        max_ircra: float
    ) -> list[Climb]:
        """Retourne les blocs dans une plage de grade."""
        return [
            climb for climb_id, climb in self.climbs.items()
            if min_ircra <= self.climb_grades.get(climb_id, 0) <= max_ircra
        ]

    def get_filtered_climbs(
        self,
        hold_ids: list[int] = None,
        min_ircra: float = None,
        max_ircra: float = None
    ) -> list[Climb]:
        """
        Retourne les blocs filtrés par prises ET plage de grade.

        Args:
            hold_ids: Liste des prises à inclure (logique ET)
            min_ircra: Grade minimum (inclus)
            max_ircra: Grade maximum (inclus)
        """
        # Commencer avec tous les blocs ou ceux filtrés par prises
        if hold_ids:
            climbs = self.get_climbs_for_holds(hold_ids)
        else:
            climbs = list(self.climbs.values())

        # Filtrer par grade
        if min_ircra is not None or max_ircra is not None:
            min_g = min_ircra if min_ircra is not None else 0
            max_g = max_ircra if max_ircra is not None else 100
            climbs = [
                c for c in climbs
                if min_g <= self.climb_grades.get(c.id, 0) <= max_g
            ]

        return climbs

    def get_hold_min_grade(
        self,
        hold_id: int,
        min_ircra: float = None,
        max_ircra: float = None,
        valid_climb_ids: set[str] = None
    ) -> Optional[float]:
        """
        Retourne le grade IRCRA du bloc le plus facile contenant cette prise
        dans la plage spécifiée.

        Args:
            hold_id: ID de la prise
            min_ircra: Grade minimum
            max_ircra: Grade maximum
            valid_climb_ids: Si fourni, ne considère que ces blocs

        Returns:
            Grade IRCRA ou None si aucun bloc dans la plage
        """
        climb_ids = self.hold_to_climbs.get(hold_id, [])
        if not climb_ids:
            return None

        min_g = min_ircra if min_ircra is not None else 0
        max_g = max_ircra if max_ircra is not None else 100

        grades = []
        for cid in climb_ids:
            # Filtre par valid_climb_ids si fourni
            if valid_climb_ids is not None and cid not in valid_climb_ids:
                continue
            if cid in self.climb_grades and min_g <= self.climb_grades[cid] <= max_g:
                grades.append(self.climb_grades[cid])

        return min(grades) if grades else None

    def get_holds_usage(
        self,
        min_ircra: float = None,
        max_ircra: float = None
    ) -> dict[int, int]:
        """
        Retourne le nombre de blocs utilisant chaque prise dans la plage.

        Returns:
            dict[hold_id, count]
        """
        # Blocs dans la plage
        if min_ircra is not None or max_ircra is not None:
            valid_climb_ids = set(
                c.id for c in self.get_climbs_in_grade_range(
                    min_ircra or 0, max_ircra or 100
                )
            )
        else:
            valid_climb_ids = set(self.climbs.keys())

        usage = {}
        for hold_id, climb_ids in self.hold_to_climbs.items():
            count = sum(1 for cid in climb_ids if cid in valid_climb_ids)
            if count > 0:
                usage[hold_id] = count

        return usage
