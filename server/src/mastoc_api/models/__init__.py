"""
Modèles SQLAlchemy pour mastoc-api.

Architecture Railway-First avec mapping stokt_id nullable.
"""

from mastoc_api.models.base import DataSource
from mastoc_api.models.gym import Gym
from mastoc_api.models.face import Face
from mastoc_api.models.hold import Hold
from mastoc_api.models.climb import Climb
from mastoc_api.models.user import User
from mastoc_api.models.mapping import IdMapping

__all__ = [
    "DataSource",
    "Gym",
    "Face",
    "Hold",
    "Climb",
    "User",
    "IdMapping",
]
