"""
Backend Switch - Abstraction pour basculer entre Stokt et Railway.

Permet d'utiliser soit l'API Stokt (legacy) soit l'API Railway (mastoc-api)
de manière transparente.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable
from pathlib import Path

from mastoc.api.models import Climb, Hold, Face, Wall


class BackendSource(Enum):
    """Source de données."""
    RAILWAY = "railway"
    STOKT = "stokt"


@dataclass
class BackendConfig:
    """Configuration du backend."""
    source: BackendSource = BackendSource.RAILWAY

    # Railway config
    railway_url: str = "https://mastoc-production.up.railway.app"
    railway_api_key: Optional[str] = None

    # Stokt config (pour fallback ou mode legacy)
    stokt_username: Optional[str] = None
    stokt_password: Optional[str] = None
    stokt_token: Optional[str] = None

    # Comportement
    fallback_to_stokt: bool = True  # Si Railway échoue, essayer Stokt
    timeout: int = 30


ProgressCallback = Callable[[int, int], None]


class BackendInterface(ABC):
    """Interface commune pour les backends."""

    @abstractmethod
    def is_authenticated(self) -> bool:
        """Vérifie si le backend est authentifié."""
        pass

    @abstractmethod
    def get_climbs(
        self,
        face_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Climb], int]:
        """Récupère les climbs avec pagination."""
        pass

    @abstractmethod
    def get_all_climbs(
        self,
        face_id: Optional[str] = None,
        callback: Optional[ProgressCallback] = None,
    ) -> list[Climb]:
        """Récupère tous les climbs."""
        pass

    @abstractmethod
    def get_climb(self, climb_id: str) -> Climb:
        """Récupère un climb par ID."""
        pass

    @abstractmethod
    def get_holds(self, face_id: str) -> list[Hold]:
        """Récupère les holds d'une face."""
        pass

    @abstractmethod
    def get_face_setup(self, face_id: str) -> Face:
        """Récupère une face avec ses holds."""
        pass

    @abstractmethod
    def create_climb(
        self,
        face_id: str,
        name: str,
        holds_list: str,
        grade_font: Optional[str] = None,
        feet_rule: Optional[str] = None,
        description: Optional[str] = None,
        is_private: bool = False,
    ) -> Climb:
        """Crée un nouveau climb."""
        pass

    @property
    @abstractmethod
    def source(self) -> BackendSource:
        """Retourne la source du backend."""
        pass


class RailwayBackend(BackendInterface):
    """Backend Railway (mastoc-api)."""

    def __init__(self, config: BackendConfig):
        from mastoc.api.railway_client import MastocAPI, RailwayConfig

        self.config = config
        self._api = MastocAPI(RailwayConfig(
            base_url=config.railway_url,
            api_key=config.railway_api_key,
            timeout=config.timeout,
        ))
        # Face ID par défaut (Montoboard)
        self._default_face_id: Optional[str] = None

    @property
    def source(self) -> BackendSource:
        return BackendSource.RAILWAY

    @property
    def api(self):
        """Accès direct à l'API (pour cas avancés)."""
        return self._api

    def is_authenticated(self) -> bool:
        return self._api.is_authenticated()

    def set_api_key(self, api_key: str):
        """Définit l'API Key."""
        self._api.set_api_key(api_key)
        self.config.railway_api_key = api_key

    def get_climbs(
        self,
        face_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Climb], int]:
        return self._api.get_climbs(
            face_id=face_id,
            page=page,
            page_size=page_size,
        )

    def get_all_climbs(
        self,
        face_id: Optional[str] = None,
        callback: Optional[ProgressCallback] = None,
    ) -> list[Climb]:
        return self._api.get_all_climbs(face_id=face_id, callback=callback)

    def get_climb(self, climb_id: str) -> Climb:
        return self._api.get_climb(climb_id)

    def get_holds(self, face_id: str) -> list[Hold]:
        return self._api.get_holds(face_id)

    def get_face_setup(self, face_id: str) -> Face:
        """
        Récupère une face avec ses holds.

        Utilise l'endpoint GET /api/faces/{id}/setup.
        """
        return self._api.get_face_setup(face_id)

    def create_climb(
        self,
        face_id: str,
        name: str,
        holds_list: str,
        grade_font: Optional[str] = None,
        feet_rule: Optional[str] = None,
        description: Optional[str] = None,
        is_private: bool = False,
    ) -> Climb:
        return self._api.create_climb(
            face_id=face_id,
            name=name,
            holds_list=holds_list,
            grade_font=grade_font,
            feet_rule=feet_rule,
            description=description,
            is_private=is_private,
        )

    def health(self) -> dict:
        """Vérifie la santé du serveur."""
        return self._api.health()

    def get_stats(self) -> dict:
        """Récupère les statistiques."""
        return self._api.get_stats()


class StoktBackend(BackendInterface):
    """Backend Stokt (legacy)."""

    # ID du gym Montoboard
    MONTOBOARD_GYM_ID = "be149ef2-317d-4c73-8d7d-50074577d2fa"

    def __init__(self, config: BackendConfig):
        from mastoc.api.client import StoktAPI, StoktConfig

        self.config = config
        self._api = StoktAPI(StoktConfig(timeout=config.timeout))
        self._gym_id = self.MONTOBOARD_GYM_ID

        # Restaurer le token si présent
        if config.stokt_token:
            self._api.set_token(config.stokt_token)

    @property
    def source(self) -> BackendSource:
        return BackendSource.STOKT

    @property
    def api(self):
        """Accès direct à l'API (pour cas avancés)."""
        return self._api

    def is_authenticated(self) -> bool:
        return self._api.is_authenticated()

    def login(self, username: str, password: str) -> dict:
        """Authentification Stokt."""
        result = self._api.login(username, password)
        self.config.stokt_token = self._api.token
        return result

    def set_token(self, token: str):
        """Définit le token manuellement."""
        self._api.set_token(token)
        self.config.stokt_token = token

    def get_climbs(
        self,
        face_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Climb], int]:
        # Stokt n'a pas de vraie pagination serveur, on simule
        climbs, total, _ = self._api.get_gym_climbs(self._gym_id, max_age=9999)

        # Filtrer par face si demandé
        if face_id:
            climbs = [c for c in climbs if c.face_id == face_id]
            total = len(climbs)

        # Pagination côté client
        start = (page - 1) * page_size
        end = start + page_size
        return climbs[start:end], total

    def get_all_climbs(
        self,
        face_id: Optional[str] = None,
        callback: Optional[ProgressCallback] = None,
    ) -> list[Climb]:
        climbs = self._api.get_all_gym_climbs(self._gym_id, callback=callback)

        if face_id:
            climbs = [c for c in climbs if c.face_id == face_id]

        return climbs

    def get_climb(self, climb_id: str) -> Climb:
        # Stokt n'a pas d'endpoint direct pour un climb
        # On récupère tous les climbs et on filtre
        climbs = self._api.get_all_gym_climbs(self._gym_id)
        for climb in climbs:
            if climb.id == climb_id:
                return climb
        raise ValueError(f"Climb {climb_id} not found")

    def get_holds(self, face_id: str) -> list[Hold]:
        face = self._api.get_face_setup(face_id)
        return face.holds

    def get_face_setup(self, face_id: str) -> Face:
        return self._api.get_face_setup(face_id)

    def create_climb(
        self,
        face_id: str,
        name: str,
        holds_list: str,
        grade_font: Optional[str] = None,
        feet_rule: Optional[str] = None,
        description: Optional[str] = None,
        is_private: bool = False,
    ) -> Climb:
        # Convertir au format Stokt
        payload = self._build_stokt_payload(
            name=name,
            holds_list=holds_list,
            grade_font=grade_font,
            feet_rule=feet_rule,
            description=description,
            is_private=is_private,
        )
        return self._api.create_climb(face_id, payload)

    def _build_stokt_payload(
        self,
        name: str,
        holds_list: str,
        grade_font: Optional[str],
        feet_rule: Optional[str],
        description: Optional[str],
        is_private: bool,
    ) -> dict:
        """Construit le payload pour l'API Stokt."""
        # Parser holds_list format "S123 O456 T789"
        start = []
        others = []
        top = []
        feet_only = []

        for hold in holds_list.split():
            if len(hold) > 1:
                hold_type = hold[0]
                hold_id = hold[1:]
                if hold_type == "S":
                    start.append(hold_id)
                elif hold_type == "O":
                    others.append(hold_id)
                elif hold_type == "T":
                    top.append(hold_id)
                elif hold_type == "F":
                    feet_only.append(hold_id)

        payload = {
            "name": name,
            "holdsList": {
                "start": start,
                "others": others,
                "top": top,
                "feetOnly": feet_only,
            },
        }

        if grade_font:
            payload["grade"] = {
                "gradingSystem": "font",
                "value": grade_font,
            }

        if feet_rule:
            payload["feetRule"] = feet_rule

        if description:
            payload["description"] = description

        if is_private:
            payload["isPrivate"] = True

        return payload

    # Méthodes spécifiques Stokt (social, etc.)
    def get_gym_walls(self, gym_id: Optional[str] = None) -> list[Wall]:
        """Récupère les murs du gym."""
        return self._api.get_gym_walls(gym_id or self._gym_id)

    def get_climb_sends(self, climb_id: str, limit: int = 20):
        """Récupère les ascensions d'un climb."""
        return self._api.get_climb_sends(climb_id, limit)

    def get_climb_comments(self, climb_id: str, limit: int = 20):
        """Récupère les commentaires d'un climb."""
        return self._api.get_climb_comments(climb_id, limit)

    def get_climb_likes(self, climb_id: str):
        """Récupère les likes d'un climb."""
        return self._api.get_climb_likes(climb_id)


class BackendSwitch:
    """
    Gestionnaire de backends avec fallback automatique.

    Usage:
        backend = BackendSwitch(BackendConfig(
            source=BackendSource.RAILWAY,
            railway_api_key="my-key",
        ))

        # Utiliser l'interface commune
        climbs = backend.get_all_climbs()

        # Accéder au backend spécifique si besoin
        if backend.source == BackendSource.STOKT:
            backend.stokt.get_climb_sends(climb_id)
    """

    def __init__(self, config: Optional[BackendConfig] = None):
        self.config = config or BackendConfig()

        self._railway: Optional[RailwayBackend] = None
        self._stokt: Optional[StoktBackend] = None

        # Initialiser le backend principal
        self._init_backends()

    def _init_backends(self):
        """Initialise les backends selon la config."""
        if self.config.source == BackendSource.RAILWAY:
            self._railway = RailwayBackend(self.config)
            if self.config.fallback_to_stokt:
                self._stokt = StoktBackend(self.config)
        else:
            self._stokt = StoktBackend(self.config)
            # Railway peut être utilisé en parallèle
            if self.config.railway_api_key:
                self._railway = RailwayBackend(self.config)

    @property
    def source(self) -> BackendSource:
        """Retourne la source active."""
        return self.config.source

    @property
    def primary(self) -> BackendInterface:
        """Retourne le backend principal."""
        if self.config.source == BackendSource.RAILWAY:
            return self._railway
        return self._stokt

    @property
    def railway(self) -> Optional[RailwayBackend]:
        """Accès au backend Railway."""
        return self._railway

    @property
    def stokt(self) -> Optional[StoktBackend]:
        """Accès au backend Stokt."""
        return self._stokt

    def is_authenticated(self) -> bool:
        """Vérifie si le backend principal est authentifié."""
        return self.primary.is_authenticated()

    def get_climbs(
        self,
        face_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Climb], int]:
        """Récupère les climbs avec pagination."""
        try:
            return self.primary.get_climbs(face_id, page, page_size)
        except Exception as e:
            if self._can_fallback():
                return self._fallback.get_climbs(face_id, page, page_size)
            raise

    def get_all_climbs(
        self,
        face_id: Optional[str] = None,
        callback: Optional[ProgressCallback] = None,
    ) -> list[Climb]:
        """Récupère tous les climbs."""
        try:
            return self.primary.get_all_climbs(face_id, callback)
        except Exception as e:
            if self._can_fallback():
                return self._fallback.get_all_climbs(face_id, callback)
            raise

    def get_climb(self, climb_id: str) -> Climb:
        """Récupère un climb par ID."""
        try:
            return self.primary.get_climb(climb_id)
        except Exception as e:
            if self._can_fallback():
                return self._fallback.get_climb(climb_id)
            raise

    def get_holds(self, face_id: str) -> list[Hold]:
        """Récupère les holds d'une face."""
        try:
            return self.primary.get_holds(face_id)
        except Exception as e:
            if self._can_fallback():
                return self._fallback.get_holds(face_id)
            raise

    def get_face_setup(self, face_id: str) -> Face:
        """Récupère une face avec ses holds."""
        try:
            return self.primary.get_face_setup(face_id)
        except Exception as e:
            if self._can_fallback():
                return self._fallback.get_face_setup(face_id)
            raise

    def create_climb(
        self,
        face_id: str,
        name: str,
        holds_list: str,
        grade_font: Optional[str] = None,
        feet_rule: Optional[str] = None,
        description: Optional[str] = None,
        is_private: bool = False,
    ) -> Climb:
        """Crée un nouveau climb."""
        return self.primary.create_climb(
            face_id=face_id,
            name=name,
            holds_list=holds_list,
            grade_font=grade_font,
            feet_rule=feet_rule,
            description=description,
            is_private=is_private,
        )

    def _can_fallback(self) -> bool:
        """Vérifie si le fallback est possible."""
        if not self.config.fallback_to_stokt:
            return False
        return self._fallback is not None and self._fallback.is_authenticated()

    @property
    def _fallback(self) -> Optional[BackendInterface]:
        """Retourne le backend de fallback."""
        if self.config.source == BackendSource.RAILWAY:
            return self._stokt
        return self._railway

    # Méthodes de configuration
    def set_railway_api_key(self, api_key: str):
        """Configure l'API Key Railway."""
        self.config.railway_api_key = api_key
        if self._railway:
            self._railway.set_api_key(api_key)
        elif self.config.source == BackendSource.RAILWAY:
            self._railway = RailwayBackend(self.config)

    def set_stokt_token(self, token: str):
        """Configure le token Stokt."""
        self.config.stokt_token = token
        if self._stokt:
            self._stokt.set_token(token)
        else:
            self._stokt = StoktBackend(self.config)

    def login_stokt(self, username: str, password: str) -> dict:
        """Authentification Stokt."""
        if not self._stokt:
            self._stokt = StoktBackend(self.config)
        return self._stokt.login(username, password)

    def switch_source(self, source: BackendSource):
        """Change la source active."""
        self.config.source = source
        self._init_backends()


# Constantes utiles
MONTOBOARD_GYM_ID = "be149ef2-317d-4c73-8d7d-50074577d2fa"
MONTOBOARD_FACE_ID = "e29cf833-4e78-4e78-b8c9-f8a31d7d8a01"  # À vérifier avec DB
