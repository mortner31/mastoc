"""
Module pour les statistiques de synchronisation.

Interroge l'API Railway pour obtenir les stats de sync
et lister les climbs créés localement.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from mastoc.api.railway_client import MastocAPI
from mastoc.core.config import AppConfig


@dataclass
class SyncStats:
    """Statistiques de synchronisation."""
    total_climbs: int
    synced_climbs: int
    local_climbs: int
    total_holds: int
    total_users: int
    last_sync: Optional[datetime] = None

    @property
    def sync_percentage(self) -> float:
        """Pourcentage de climbs synchronisés."""
        if self.total_climbs == 0:
            return 100.0
        return (self.synced_climbs / self.total_climbs) * 100


@dataclass
class LocalClimb:
    """Climb créé localement (sans stokt_id)."""
    id: str
    name: str
    grade: Optional[str]
    created_at: Optional[str]
    setter_name: Optional[str] = None


def get_sync_stats(api: Optional[MastocAPI] = None) -> SyncStats:
    """
    Récupère les statistiques de synchronisation depuis Railway.

    Args:
        api: Instance MastocAPI (créée automatiquement si None)

    Returns:
        SyncStats avec les compteurs
    """
    if api is None:
        config = AppConfig.load()
        api = MastocAPI(
            base_url=config.railway_url or "https://mastoc-production.up.railway.app",
            api_key=config.railway_api_key
        )

    stats = api.get_sync_stats()

    return SyncStats(
        total_climbs=stats.get("climbs", 0),
        synced_climbs=stats.get("climbs_synced", 0),
        local_climbs=stats.get("climbs_local", 0),
        total_holds=stats.get("holds", 0),
        total_users=stats.get("users", 0),
    )


def get_local_climbs(api: Optional[MastocAPI] = None) -> list[LocalClimb]:
    """
    Récupère la liste des climbs créés localement (stokt_id = NULL).

    Args:
        api: Instance MastocAPI (créée automatiquement si None)

    Returns:
        Liste de LocalClimb
    """
    if api is None:
        config = AppConfig.load()
        api = MastocAPI(
            base_url=config.railway_url or "https://mastoc-production.up.railway.app",
            api_key=config.railway_api_key
        )

    # Utiliser le paramètre local_only=true
    climbs_list, _ = api.get_climbs(local_only=True, page_size=100)

    result = []
    for c in climbs_list:
        result.append(LocalClimb(
            id=c.id,
            name=c.name,
            grade=c.grade.font if c.grade else None,
            created_at=c.date_created,
            setter_name=c.setter.full_name if c.setter else None,
        ))

    return result
