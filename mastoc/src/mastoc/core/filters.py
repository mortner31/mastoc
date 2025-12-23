"""
Filtres pour les climbs.

Permet de filtrer par niveau, auteur, prises utilisées, etc.
"""

from dataclasses import dataclass, field
from typing import Optional

from mastoc.api.models import Climb, HoldType
from mastoc.db import Database, ClimbRepository


@dataclass
class ClimbFilter:
    """Critères de filtrage pour les climbs."""

    # Filtres par grade (Fontainebleau)
    grades: list[str] = field(default_factory=list)
    grade_min: Optional[float] = None  # IRCRA min
    grade_max: Optional[float] = None  # IRCRA max

    # Filtres par setter
    setter_ids: list[str] = field(default_factory=list)
    setter_name: Optional[str] = None  # Recherche partielle

    # Filtres par prises
    hold_ids: list[int] = field(default_factory=list)
    hold_match_mode: str = "all"  # "all" = toutes les prises, "any" = au moins une

    # Filtres par caractéristiques
    feet_rules: list[str] = field(default_factory=list)
    is_benchmark: Optional[bool] = None
    has_symmetric: Optional[bool] = None

    # Tri
    sort_by: str = "date_created"  # date_created, grade, name, climbed_by
    sort_desc: bool = True

    # Recherche texte
    search_text: Optional[str] = None


class ClimbFilterService:
    """Service de filtrage des climbs."""

    def __init__(self, db: Database):
        self.db = db
        self.climb_repo = ClimbRepository(db)

    def filter_climbs(self, filter_criteria: ClimbFilter) -> list[Climb]:
        """
        Filtre les climbs selon les critères spécifiés.

        Args:
            filter_criteria: Critères de filtrage

        Returns:
            Liste des climbs correspondants
        """
        # Si filtrage par prises, utiliser la méthode optimisée du repo
        if filter_criteria.hold_ids:
            if filter_criteria.hold_match_mode == "all":
                climbs = self.climb_repo.get_climbs_by_holds(filter_criteria.hold_ids)
            else:
                # Mode "any" - climbs avec au moins une des prises
                climbs_set = set()
                for hold_id in filter_criteria.hold_ids:
                    for c in self.climb_repo.get_climbs_by_hold(hold_id):
                        climbs_set.add(c.id)
                # Récupérer les objets Climb complets
                all_climbs = self.climb_repo.get_all_climbs()
                climbs = [c for c in all_climbs if c.id in climbs_set]
        else:
            climbs = self.climb_repo.get_all_climbs()

        # Appliquer les autres filtres
        climbs = self._apply_filters(climbs, filter_criteria)

        # Trier
        climbs = self._sort_climbs(climbs, filter_criteria)

        return climbs

    def _apply_filters(
        self,
        climbs: list[Climb],
        criteria: ClimbFilter
    ) -> list[Climb]:
        """Applique les filtres sur une liste de climbs."""
        result = climbs

        # Filtre par grades (liste)
        if criteria.grades:
            result = [c for c in result if c.grade and c.grade.font in criteria.grades]

        # Filtre par grade IRCRA min/max
        if criteria.grade_min is not None:
            result = [c for c in result if c.grade and c.grade.ircra >= criteria.grade_min]
        if criteria.grade_max is not None:
            result = [c for c in result if c.grade and c.grade.ircra <= criteria.grade_max]

        # Filtre par setter IDs
        if criteria.setter_ids:
            result = [c for c in result if c.setter and c.setter.id in criteria.setter_ids]

        # Filtre par nom de setter (recherche partielle)
        if criteria.setter_name:
            search = criteria.setter_name.lower()
            result = [
                c for c in result
                if c.setter and search in c.setter.full_name.lower()
            ]

        # Filtre par feet rules
        if criteria.feet_rules:
            result = [c for c in result if c.feet_rule in criteria.feet_rules]

        # Filtre benchmark
        if criteria.is_benchmark is not None:
            result = [c for c in result if c.is_benchmark == criteria.is_benchmark]

        # Filtre symétrie
        if criteria.has_symmetric is not None:
            result = [c for c in result if c.has_symmetric == criteria.has_symmetric]

        # Recherche texte (nom du climb)
        if criteria.search_text:
            search = criteria.search_text.lower()
            result = [c for c in result if search in c.name.lower()]

        return result

    def _sort_climbs(
        self,
        climbs: list[Climb],
        criteria: ClimbFilter
    ) -> list[Climb]:
        """Trie les climbs selon les critères."""
        if criteria.sort_by == "date_created":
            key = lambda c: c.date_created or ""
        elif criteria.sort_by == "grade":
            key = lambda c: c.grade.ircra if c.grade else 0
        elif criteria.sort_by == "name":
            key = lambda c: c.name.lower()
        elif criteria.sort_by == "climbed_by":
            key = lambda c: c.climbed_by
        elif criteria.sort_by == "likes":
            key = lambda c: c.total_likes
        else:
            key = lambda c: c.date_created or ""

        return sorted(climbs, key=key, reverse=criteria.sort_desc)

    def get_available_grades(self) -> list[str]:
        """Retourne les grades disponibles triés par difficulté."""
        return self.climb_repo.get_unique_grades()

    def get_available_setters(self) -> list[tuple[str, str]]:
        """Retourne les setters disponibles (id, nom)."""
        return self.climb_repo.get_unique_setters()

    def get_available_feet_rules(self) -> list[str]:
        """Retourne les feet rules disponibles."""
        with self.db.connection() as conn:
            cursor = conn.execute(
                "SELECT DISTINCT feet_rule FROM climbs WHERE feet_rule IS NOT NULL ORDER BY feet_rule"
            )
            return [row[0] for row in cursor.fetchall() if row[0]]


def filter_climbs_simple(
    climbs: list[Climb],
    grades: list[str] = None,
    setter_name: str = None,
    search_text: str = None
) -> list[Climb]:
    """
    Fonction utilitaire pour filtrer rapidement une liste de climbs.

    Args:
        climbs: Liste de climbs à filtrer
        grades: Grades à inclure (Fontainebleau)
        setter_name: Nom du setter (recherche partielle)
        search_text: Texte à rechercher dans le nom

    Returns:
        Liste filtrée
    """
    result = climbs

    if grades:
        result = [c for c in result if c.grade and c.grade.font in grades]

    if setter_name:
        search = setter_name.lower()
        result = [
            c for c in result
            if c.setter and search in c.setter.full_name.lower()
        ]

    if search_text:
        search = search_text.lower()
        result = [c for c in result if search in c.name.lower()]

    return result
