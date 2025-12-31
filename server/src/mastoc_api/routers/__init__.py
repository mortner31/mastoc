"""
Routers FastAPI pour mastoc-api.
"""

from mastoc_api.routers.health import router as health_router
from mastoc_api.routers.climbs import router as climbs_router
from mastoc_api.routers.holds import router as holds_router
from mastoc_api.routers.faces import router as faces_router
from mastoc_api.routers.sync import router as sync_router

__all__ = [
    "health_router",
    "climbs_router",
    "holds_router",
    "faces_router",
    "sync_router",
]
