"""
Types et classes de base pour les modèles.
"""

from enum import Enum


class DataSource(str, Enum):
    """Source des données."""
    MASTOC = "mastoc"
    STOKT = "stokt"


class UserRole(str, Enum):
    """Rôle utilisateur."""
    USER = "user"
    ADMIN = "admin"
