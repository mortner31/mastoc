"""
Client API pour sostokt.com

Endpoints fonctionnels découverts par analyse du code décompilé de l'app React Native.
"""

import requests
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from mastock.api.models import Climb, Face, Wall, GymSummary


@dataclass
class StoktConfig:
    """Configuration pour l'API Stokt."""
    base_url: str = "https://www.sostokt.com"
    timeout: int = 60


# Constante pour Montoboard
MONTOBOARD_GYM_ID = "be149ef2-317d-4c73-8d7d-50074577d2fa"


class StoktAPIError(Exception):
    """Erreur lors d'un appel API."""
    pass


class AuthenticationError(StoktAPIError):
    """Erreur d'authentification (token invalide ou expiré)."""
    pass


class StoktAPI:
    """Client API pour sostokt.com"""

    def __init__(self, config: Optional[StoktConfig] = None):
        self.config = config or StoktConfig()
        self.token: Optional[str] = None
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded"
        })

    def _url(self, endpoint: str) -> str:
        """Construit l'URL complète."""
        return f"{self.config.base_url}/{endpoint}"

    def _auth_headers(self) -> dict:
        """Retourne les headers d'authentification."""
        if not self.token:
            raise AuthenticationError("Non authentifié. Appelez login() d'abord.")
        return {"Authorization": f"Token {self.token}"}

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Effectue une requête avec gestion des erreurs."""
        kwargs.setdefault("timeout", self.config.timeout)
        kwargs.setdefault("headers", {}).update(self._auth_headers())

        response = getattr(self.session, method)(self._url(endpoint), **kwargs)

        if response.status_code == 401:
            raise AuthenticationError("Token invalide ou expiré")
        response.raise_for_status()
        return response

    def login(self, username: str, password: str) -> dict:
        """
        Authentification via api/token-auth.

        Args:
            username: Nom d'utilisateur
            password: Mot de passe

        Returns:
            Dict avec le token et les infos utilisateur
        """
        response = self.session.post(
            self._url("api/token-auth"),
            data={"username": username, "password": password},
            timeout=self.config.timeout
        )
        response.raise_for_status()
        data = response.json()
        self.token = data.get("token")
        return data

    def set_token(self, token: str):
        """Définit le token d'authentification manuellement."""
        self.token = token

    def is_authenticated(self) -> bool:
        """Vérifie si le client est authentifié."""
        return self.token is not None

    def get_user_profile(self) -> dict:
        """
        GET api/users/me

        Returns:
            Profil de l'utilisateur connecté
        """
        response = self._request("get", "api/users/me")
        return response.json()

    def get_gym_summary(self, gym_id: str) -> GymSummary:
        """
        GET api/gyms/{gym_id}/summary

        Args:
            gym_id: ID du gym

        Returns:
            Résumé du gym
        """
        response = self._request("get", f"api/gyms/{gym_id}/summary")
        return GymSummary.from_api(response.json())

    def get_gym_walls(self, gym_id: str) -> list[Wall]:
        """
        GET api/gyms/{gym_id}/walls

        Args:
            gym_id: ID du gym

        Returns:
            Liste des murs avec leurs faces
        """
        response = self._request("get", f"api/gyms/{gym_id}/walls")
        return [Wall.from_api(w) for w in response.json()]

    def get_gym_climbs(self, gym_id: str, max_age: int = 60) -> tuple[list[Climb], int, Optional[str]]:
        """
        GET api/gyms/{gym_id}/climbs?max_age={max_age}

        Args:
            gym_id: ID du gym
            max_age: Nombre de jours (défaut: 60, utiliser 9999 pour tous)

        Returns:
            Tuple (climbs, total_count, next_url)
        """
        response = self._request("get", f"api/gyms/{gym_id}/climbs", params={"max_age": max_age})
        data = response.json()
        climbs = [Climb.from_api(c) for c in data.get("results", [])]
        return climbs, data.get("count", 0), data.get("next")

    def get_all_gym_climbs(self, gym_id: str, callback=None) -> list[Climb]:
        """
        Récupère TOUS les climbs d'un gym avec pagination automatique.

        Args:
            gym_id: ID du gym
            callback: Fonction appelée avec (current, total) pour la progression

        Returns:
            Liste de tous les climbs
        """
        all_climbs = []

        # Première page
        climbs, total, next_url = self.get_gym_climbs(gym_id, max_age=9999)
        all_climbs.extend(climbs)

        if callback:
            callback(len(all_climbs), total)

        # Pagination
        while next_url:
            response = self.session.get(
                next_url,
                headers=self._auth_headers(),
                timeout=self.config.timeout
            )
            response.raise_for_status()
            data = response.json()
            page_climbs = [Climb.from_api(c) for c in data.get("results", [])]
            all_climbs.extend(page_climbs)
            next_url = data.get("next")

            if callback:
                callback(len(all_climbs), total)

        return all_climbs

    def get_face_setup(self, face_id: str) -> Face:
        """
        GET api/faces/{face_id}/setup

        Args:
            face_id: ID de la face

        Returns:
            Face avec les coordonnées de toutes les prises
        """
        response = self._request("get", f"api/faces/{face_id}/setup")
        return Face.from_api(response.json())

    def get_my_sent_climbs(self, gym_id: str) -> list[Climb]:
        """
        GET api/gyms/{gym_id}/my-sent-climbs

        Args:
            gym_id: ID du gym

        Returns:
            Climbs validés par l'utilisateur
        """
        response = self._request("get", f"api/gyms/{gym_id}/my-sent-climbs")
        return [Climb.from_api(c) for c in response.json()]

    def get_face_image_url(self, face_path: str) -> str:
        """
        Construit l'URL complète pour une image de face.

        Args:
            face_path: Chemin relatif (ex: CACHE/images/walls/.../ref_pic.jpg)

        Returns:
            URL complète de l'image
        """
        return f"{self.config.base_url}/media/{face_path}"

    def download_image(self, image_path: str, save_path: Path | str) -> bool:
        """
        Télécharge une image.

        Args:
            image_path: Chemin relatif de l'image
            save_path: Chemin local où sauvegarder

        Returns:
            True si succès
        """
        url = self.get_face_image_url(image_path)
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()

        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        save_path.write_bytes(response.content)
        return True
