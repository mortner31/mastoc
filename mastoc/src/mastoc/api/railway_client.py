"""
Client API pour mastoc-api (Railway).

Ce client remplace StoktAPI pour les opérations de lecture/écriture
sur le serveur Railway personnel.
"""

import requests
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from pathlib import Path

from mastoc.api.models import Climb, Hold, Face, ClimbHold, HoldType, Grade, ClimbSetter


@dataclass
class RailwayConfig:
    """Configuration pour l'API Railway."""
    base_url: str = "https://mastoc-production.up.railway.app"
    api_key: Optional[str] = None
    timeout: int = 30


class MastocAPIError(Exception):
    """Erreur lors d'un appel API."""
    pass


class AuthenticationError(MastocAPIError):
    """Erreur d'authentification (API Key invalide ou manquante)."""
    pass


class MastocAPI:
    """Client API pour mastoc-api (Railway)."""

    def __init__(self, config: Optional[RailwayConfig] = None, auth_manager=None):
        """
        Initialise le client API.

        Args:
            config: Configuration Railway (API Key)
            auth_manager: AuthManager pour authentification JWT (optionnel)
        """
        self.config = config or RailwayConfig()
        self.session = requests.Session()
        self._auth_manager = auth_manager
        self._update_headers()

    def set_auth_manager(self, auth_manager):
        """Définit l'AuthManager pour l'authentification JWT."""
        self._auth_manager = auth_manager

    def _update_headers(self):
        """Met à jour les headers de session."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key
        self.session.headers.update(headers)

    def _get_auth_headers(self) -> dict:
        """Retourne les headers d'authentification."""
        headers = {}

        # Priorité : JWT > API Key
        if self._auth_manager and self._auth_manager.access_token:
            headers["Authorization"] = f"Bearer {self._auth_manager.access_token}"
        elif self.config.api_key:
            headers["X-API-Key"] = self.config.api_key

        return headers

    def set_api_key(self, api_key: str):
        """Définit l'API Key."""
        self.config.api_key = api_key
        self._update_headers()

    def is_authenticated(self) -> bool:
        """Vérifie si une authentification est configurée (API Key ou JWT)."""
        if self._auth_manager and self._auth_manager.is_authenticated:
            return True
        return self.config.api_key is not None

    @property
    def current_user(self):
        """Retourne l'utilisateur connecté (si JWT)."""
        if self._auth_manager:
            return self._auth_manager.current_user
        return None

    def _url(self, endpoint: str) -> str:
        """Construit l'URL complète."""
        return f"{self.config.base_url}/{endpoint}"

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Effectue une requête avec gestion des erreurs."""
        kwargs.setdefault("timeout", self.config.timeout)

        # Ajouter les headers d'auth (JWT ou API Key)
        headers = kwargs.get("headers", {})
        headers.update(self._get_auth_headers())
        kwargs["headers"] = headers

        url = self._url(endpoint)
        response = getattr(self.session, method)(url, **kwargs)

        if response.status_code == 401:
            raise AuthenticationError("Non authentifié (JWT ou API Key invalide)")
        if response.status_code == 403:
            raise AuthenticationError("Accès refusé")

        response.raise_for_status()
        return response

    # =========================================================================
    # Health & Stats
    # =========================================================================

    def health(self) -> dict:
        """
        GET /health

        Returns:
            Status du serveur et de la base de données
        """
        response = self.session.get(
            self._url("health"),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_stats(self) -> dict:
        """
        GET /api/sync/stats

        Returns:
            Statistiques de la base (counts par entité)
        """
        response = self._request("get", "api/sync/stats")
        return response.json()

    # =========================================================================
    # Climbs
    # =========================================================================

    def get_climbs(
        self,
        face_id: Optional[str] = None,
        grade_min: Optional[str] = None,
        grade_max: Optional[str] = None,
        setter_id: Optional[str] = None,
        search: Optional[str] = None,
        source: Optional[str] = None,
        since_created_at: Optional[datetime] = None,
        local_only: bool = False,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[Climb], int]:
        """
        GET /api/climbs

        Args:
            face_id: Filtrer par face
            grade_min: Grade minimum (ex: "4")
            grade_max: Grade maximum (ex: "6A")
            setter_id: Filtrer par ouvreur
            search: Recherche par nom
            source: Filtrer par source ("stokt", "mastoc")
            since_created_at: Retourne uniquement les climbs créés après cette date
            local_only: Si True, retourne uniquement les climbs locaux (stokt_id=NULL)
            page: Page (1-indexed)
            page_size: Nombre par page (max 500)

        Returns:
            Tuple (climbs, total_count)
        """
        params = {
            "page": page,
            "page_size": page_size,
        }
        if face_id:
            params["face_id"] = face_id
        if grade_min:
            params["grade_min"] = grade_min
        if grade_max:
            params["grade_max"] = grade_max
        if setter_id:
            params["setter_id"] = setter_id
        if search:
            params["search"] = search
        if source:
            params["source"] = source
        if since_created_at:
            params["since_created_at"] = since_created_at.isoformat()
        if local_only:
            params["local_only"] = "true"

        response = self._request("get", "api/climbs", params=params)
        data = response.json()

        climbs = [self._climb_from_railway(c) for c in data.get("results", [])]
        total = data.get("count", 0)

        return climbs, total

    def get_all_climbs(
        self,
        face_id: Optional[str] = None,
        since_created_at: Optional[datetime] = None,
        callback=None,
    ) -> list[Climb]:
        """
        Récupère les climbs avec pagination automatique.

        Args:
            face_id: Filtrer par face
            since_created_at: Retourne uniquement les climbs créés après cette date
            callback: Fonction appelée avec (current, total) pour la progression

        Returns:
            Liste des climbs correspondants
        """
        all_climbs = []
        page = 1
        page_size = 500

        while True:
            climbs, total = self.get_climbs(
                face_id=face_id,
                since_created_at=since_created_at,
                page=page,
                page_size=page_size,
            )
            all_climbs.extend(climbs)

            if callback:
                callback(len(all_climbs), total)

            if len(all_climbs) >= total:
                break

            page += 1

        return all_climbs

    def get_climb(self, climb_id: str) -> Climb:
        """
        GET /api/climbs/{climb_id}

        Args:
            climb_id: ID du climb

        Returns:
            Climb
        """
        response = self._request("get", f"api/climbs/{climb_id}")
        return self._climb_from_railway(response.json())

    def get_climb_by_stokt_id(self, stokt_id: str) -> Climb:
        """
        GET /api/climbs/by-stokt-id/{stokt_id}

        Args:
            stokt_id: ID Stokt du climb

        Returns:
            Climb
        """
        response = self._request("get", f"api/climbs/by-stokt-id/{stokt_id}")
        return self._climb_from_railway(response.json())

    def create_climb(
        self,
        face_id: str,
        name: str,
        holds_list: str,
        grade_font: Optional[str] = None,
        grade_ircra: Optional[float] = None,
        feet_rule: Optional[str] = None,
        description: Optional[str] = None,
        is_private: bool = False,
    ) -> Climb:
        """
        POST /api/climbs

        Args:
            face_id: ID de la face
            name: Nom du climb
            holds_list: Liste des prises (format "S123 O456 T789")
            grade_font: Grade Fontainebleau
            grade_ircra: Grade IRCRA
            feet_rule: Règle pieds
            description: Description
            is_private: Privé ou public

        Returns:
            Climb créé
        """
        data = {
            "face_id": face_id,
            "name": name,
            "holds_list": holds_list,
            "is_private": is_private,
        }
        if grade_font:
            data["grade_font"] = grade_font
        if grade_ircra is not None:
            data["grade_ircra"] = grade_ircra
        if feet_rule:
            data["feet_rule"] = feet_rule
        if description:
            data["description"] = description

        response = self._request("post", "api/climbs", json=data)
        return self._climb_from_railway(response.json())

    def update_climb(
        self,
        climb_id: str,
        name: Optional[str] = None,
        holds_list: Optional[str] = None,
        grade_font: Optional[str] = None,
        description: Optional[str] = None,
        is_private: Optional[bool] = None,
        personal_notes: Optional[str] = None,
        personal_rating: Optional[int] = None,
        is_project: Optional[bool] = None,
    ) -> Climb:
        """
        PATCH /api/climbs/{climb_id}

        Returns:
            Climb mis à jour
        """
        data = {}
        if name is not None:
            data["name"] = name
        if holds_list is not None:
            data["holds_list"] = holds_list
        if grade_font is not None:
            data["grade_font"] = grade_font
        if description is not None:
            data["description"] = description
        if is_private is not None:
            data["is_private"] = is_private
        if personal_notes is not None:
            data["personal_notes"] = personal_notes
        if personal_rating is not None:
            data["personal_rating"] = personal_rating
        if is_project is not None:
            data["is_project"] = is_project

        response = self._request("patch", f"api/climbs/{climb_id}", json=data)
        return self._climb_from_railway(response.json())

    def delete_climb(self, climb_id: str) -> bool:
        """
        DELETE /api/climbs/{climb_id}

        Returns:
            True si supprimé
        """
        self._request("delete", f"api/climbs/{climb_id}")
        return True

    # =========================================================================
    # Holds
    # =========================================================================

    def get_holds(self, face_id: str) -> list[Hold]:
        """
        GET /api/holds?face_id={face_id}

        Args:
            face_id: ID de la face

        Returns:
            Liste des holds
        """
        response = self._request("get", "api/holds", params={"face_id": face_id})
        data = response.json()

        holds = [self._hold_from_railway(h) for h in data.get("results", [])]
        return holds

    # =========================================================================
    # Faces
    # =========================================================================

    def get_faces(self) -> list[dict]:
        """
        GET /api/faces

        Liste toutes les faces disponibles.

        Returns:
            Liste des faces (id, holds_count, climbs_count, etc.)
        """
        response = self._request("get", "api/faces")
        return response.json()

    def get_face_setup(self, face_id: str) -> Face:
        """
        GET /api/faces/{face_id}/setup

        Récupère une face avec tous ses holds et leur configuration.

        Args:
            face_id: ID de la face

        Returns:
            Face avec les holds
        """
        response = self._request("get", f"api/faces/{face_id}/setup")
        return self._face_from_railway(response.json())

    def _face_from_railway(self, data: dict) -> Face:
        """Convertit une face Railway en modèle Face."""
        from mastoc.api.models import FacePicture

        picture = None
        if data.get("picture"):
            p = data["picture"]
            picture = FacePicture(
                name=p.get("name", ""),
                width=p.get("width", 0),
                height=p.get("height", 0),
            )

        # Convertir les holds
        holds = []
        for h in data.get("holds", []):
            holds.append(Hold(
                id=h.get("id", 0),
                area=h.get("area", 0) or 0,
                polygon_str=h.get("polygon_str", ""),
                touch_polygon_str=h.get("touch_polygon_str", ""),
                path_str=h.get("path_str", ""),
                centroid_str=h.get("centroid_str", "0 0"),
                center_tape_str=h.get("center_tape_str", ""),
                right_tape_str=h.get("right_tape_str", ""),
                left_tape_str=h.get("left_tape_str", ""),
            ))

        return Face(
            id=str(data.get("id", "")),
            is_active=data.get("is_active", True),
            total_climbs=data.get("total_climbs", 0),
            picture=picture,
            feet_rules_options=data.get("feet_rules_options", []),
            has_symmetry=data.get("has_symmetry", False),
            holds=holds,
        )

    # =========================================================================
    # Conversion des données Railway vers modèles
    # =========================================================================

    def _climb_from_railway(self, data: dict) -> Climb:
        """Convertit un climb Railway en modèle Climb."""
        # Le serveur Railway utilise snake_case
        setter = None
        if data.get("setter_name"):
            setter = ClimbSetter(
                id=str(data.get("setter_id", "")),
                full_name=data.get("setter_name", ""),
                avatar=None,
            )

        grade = None
        grade_font = data.get("grade_font")
        grade_ircra = data.get("grade_ircra")
        if grade_font or grade_ircra:
            grade = Grade(
                ircra=grade_ircra or 0,
                hueco="",
                font=grade_font or "",
                dankyu="",
            )

        return Climb(
            id=str(data.get("id", "")),
            name=data.get("name", ""),
            holds_list=data.get("holds_list", ""),
            mirror_holds_list="",
            feet_rule=data.get("feet_rule", "") or "",
            face_id=str(data.get("face_id", "")),
            wall_id="",
            wall_name="",
            date_created="",
            is_private=data.get("is_private", False),
            is_benchmark=False,
            climbed_by=data.get("climbed_by", 0),
            total_likes=data.get("total_likes", 0),
            total_comments=0,
            has_symmetric=False,
            angle="",
            is_angle_adjustable=False,
            circuit="",
            tags="",
            setter=setter,
            grade=grade,
        )

    def _hold_from_railway(self, data: dict) -> Hold:
        """Convertit un hold Railway en modèle Hold."""
        centroid_x = data.get("centroid_x", 0)
        centroid_y = data.get("centroid_y", 0)
        centroid_str = f"{centroid_x} {centroid_y}"

        return Hold(
            id=data.get("stokt_id") or data.get("id", 0),
            area=data.get("area", 0) or 0,
            polygon_str=data.get("polygon_str", ""),
            touch_polygon_str="",
            path_str="",
            centroid_str=centroid_str,
        )

    # =========================================================================
    # Sync Stats
    # =========================================================================

    def get_sync_stats(self) -> dict:
        """
        GET /api/sync/stats

        Récupère les statistiques de synchronisation.

        Returns:
            Dict avec gyms, faces, holds, climbs, users,
            climbs_synced (avec stokt_id), climbs_local (sans stokt_id)
        """
        response = self._request("get", "api/sync/stats")
        return response.json()
