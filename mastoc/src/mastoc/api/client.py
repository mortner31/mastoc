"""
Client API pour sostokt.com

Endpoints fonctionnels découverts par analyse du code décompilé de l'app React Native.
"""

import requests
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

from mastoc.api.models import Climb, Face, Wall, GymSummary, Effort, Comment, Like, ClimbList, ListItem


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
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Stokt/6.1.13 (Android)",
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

    # =========================================================================
    # Interactions sociales (TODO 07)
    # =========================================================================

    def get_climb_sends(self, climb_id: str, limit: int = 20) -> list[Effort]:
        """
        GET api/climbs/{climbId}/latest-sends

        Récupère les dernières ascensions d'un climb.

        Args:
            climb_id: ID du climb
            limit: Nombre max de résultats

        Returns:
            Liste des ascensions récentes
        """
        response = self._request("get", f"api/climbs/{climb_id}/latest-sends", params={"limit": limit})
        return [Effort.from_api(e) for e in response.json()]

    def get_climb_comments(self, climb_id: str, limit: int = 20) -> list[Comment]:
        """
        GET api/climbs/{climbId}/comments

        Récupère les commentaires d'un climb.

        Args:
            climb_id: ID du climb
            limit: Nombre max de résultats

        Returns:
            Liste des commentaires
        """
        response = self._request("get", f"api/climbs/{climb_id}/comments", params={"limit": limit})
        return [Comment.from_api(c) for c in response.json()]

    def get_climb_likes(self, climb_id: str) -> list[Like]:
        """
        GET api/climbs/{climbId}/likes

        Récupère les likes d'un climb.

        Args:
            climb_id: ID du climb

        Returns:
            Liste des likes
        """
        response = self._request("get", f"api/climbs/{climb_id}/likes")
        return [Like.from_api(lk) for lk in response.json()]

    def like_climb(self, climb_id: str) -> bool:
        """
        POST api/climbs/{climbId}/likes

        Ajoute un like à un climb.

        Args:
            climb_id: ID du climb

        Returns:
            True si succès
        """
        self._request("post", f"api/climbs/{climb_id}/likes")
        return True

    def unlike_climb(self, climb_id: str) -> bool:
        """
        DELETE api/climbs/{climbId}/likes

        Retire un like d'un climb.

        Args:
            climb_id: ID du climb

        Returns:
            True si succès
        """
        self._request("delete", f"api/climbs/{climb_id}/likes")
        return True

    def post_comment(self, climb_id: str, text: str, replied_to_id: Optional[str] = None) -> Comment:
        """
        POST api/climbs/{climbId}/comments

        Poste un commentaire sur un climb.

        Args:
            climb_id: ID du climb
            text: Texte du commentaire
            replied_to_id: ID du commentaire auquel on répond (optionnel)

        Returns:
            Commentaire créé
        """
        data = {"text": text}
        if replied_to_id:
            data["replied_to_id"] = replied_to_id

        response = self._request(
            "post",
            f"api/climbs/{climb_id}/comments",
            data=data
        )
        return Comment.from_api(response.json())

    def delete_comment(self, climb_id: str, comment_id: str) -> bool:
        """
        DELETE api/climbs/{climbId}/comments/{commentId}

        Supprime un commentaire.

        Args:
            climb_id: ID du climb
            comment_id: ID du commentaire

        Returns:
            True si succès
        """
        self._request("delete", f"api/climbs/{climb_id}/comments/{comment_id}")
        return True

    def bookmark_climb(self, climb_id: str, add: bool = True) -> bool:
        """
        PATCH api/climbs/{climbId}/bookmarked

        Ajoute ou retire un climb des favoris.

        Args:
            climb_id: ID du climb
            add: True pour ajouter, False pour retirer

        Returns:
            True si succès
        """
        data = {"added": add, "removed": not add}
        self._request("patch", f"api/climbs/{climb_id}/bookmarked", data=data)
        return True

    def get_my_bookmarked_climbs(self, gym_id: str) -> list[Climb]:
        """
        GET api/gyms/{gymId}/my-bookmarked-climbs

        Récupère les climbs favoris de l'utilisateur.

        Args:
            gym_id: ID du gym

        Returns:
            Liste des climbs favoris
        """
        response = self._request("get", f"api/gyms/{gym_id}/my-bookmarked-climbs")
        return [Climb.from_api(c) for c in response.json()]

    def get_my_liked_climbs(self, gym_id: str) -> list[Climb]:
        """
        GET api/gyms/{gymId}/my-liked-climbs

        Récupère les climbs likés par l'utilisateur.

        Args:
            gym_id: ID du gym

        Returns:
            Liste des climbs likés
        """
        response = self._request("get", f"api/gyms/{gym_id}/my-liked-climbs")
        return [Climb.from_api(c) for c in response.json()]

    def get_crowd_grades(self, climb_id: str) -> dict:
        """
        GET api/climbs/{climbId}/crowd-grades

        Récupère les notes de difficulté de la communauté.

        Args:
            climb_id: ID du climb

        Returns:
            Dict avec les notes (ircra, hueco, font, dankyu)
        """
        response = self._request("get", f"api/climbs/{climb_id}/crowd-grades")
        return response.json()

    # =========================================================================
    # Création et modification de climbs (TODO 10)
    # =========================================================================

    def create_climb(self, face_id: str, payload: dict) -> Climb:
        """
        POST api/faces/{faceId}/climbs

        Crée un nouveau climb.

        Args:
            face_id: ID de la face
            payload: Données du climb avec structure:
                {
                    "name": str,                    # Nom (min 3 caractères)
                    "holdsList": {
                        "start": List[str],         # IDs prises de départ (min 2)
                        "others": List[str],        # IDs prises intermédiaires
                        "top": List[str],           # IDs prises de finition
                        "feetOnly": List[str]       # IDs prises pieds uniquement
                    },
                    "grade": {
                        "gradingSystem": str,       # "V-Scale", "Font", "Dankyu"
                        "value": str                # "V0", "6a+", etc.
                    },
                    "description": str | None,      # Optionnel
                    "isPrivate": bool,              # Défaut: False
                    "feetRule": str | None,         # Règle des pieds
                }

        Returns:
            Climb créé

        Raises:
            StoktAPIError: Si la création échoue
        """
        # L'API attend du JSON pour les structures complexes
        response = self._request(
            "post",
            f"api/faces/{face_id}/climbs",
            json=payload,
            headers={**self._auth_headers(), "Content-Type": "application/json"}
        )
        return Climb.from_api(response.json())

    def update_climb(self, face_id: str, climb_id: str, payload: dict) -> Climb:
        """
        PATCH api/faces/{faceId}/climbs/{climbId}

        Modifie un climb existant.

        Args:
            face_id: ID de la face
            climb_id: ID du climb
            payload: Données à modifier (même structure que create_climb)

        Returns:
            Climb modifié

        Raises:
            StoktAPIError: Si la modification échoue
        """
        response = self._request(
            "patch",
            f"api/faces/{face_id}/climbs/{climb_id}",
            json=payload,
            headers={**self._auth_headers(), "Content-Type": "application/json"}
        )
        return Climb.from_api(response.json())

    def delete_climb(self, climb_id: str) -> bool:
        """
        DELETE api/climbs/{climbId}

        Supprime un climb.

        Args:
            climb_id: ID du climb

        Returns:
            True si succès

        Raises:
            StoktAPIError: Si la suppression échoue
        """
        self._request("delete", f"api/climbs/{climb_id}")
        return True

    def set_climb_privacy(self, climb_id: str, is_private: bool) -> bool:
        """
        PATCH api/climbs/{climbId}/privacy-status

        Change la visibilité d'un climb (public/privé).

        Args:
            climb_id: ID du climb
            is_private: True pour privé, False pour public

        Returns:
            True si succès

        Raises:
            StoktAPIError: Si la modification échoue
        """
        self._request(
            "patch",
            f"api/climbs/{climb_id}/privacy-status",
            json={"is_private": is_private},
            headers={**self._auth_headers(), "Content-Type": "application/json"}
        )
        return True

    def get_climb_permissions(self, climb_id: str) -> dict:
        """
        GET api/climbs/{climbId}/permissions-to-modify

        Récupère les permissions de modification pour un climb.

        Args:
            climb_id: ID du climb

        Returns:
            Dict avec les permissions:
                {
                    "canDelete": bool,
                    "canEditHolds": bool,
                    "canEditNameAndGrade": bool,
                    "canHide": bool,
                    "canSetPrivate": bool,
                    "canSetPublic": bool
                }
        """
        response = self._request("get", f"api/climbs/{climb_id}/permissions-to-modify")
        return response.json()

    # =========================================================================
    # Listes personnalisées (TODO 09)
    # =========================================================================

    def get_user_lists(self, user_id: str, ordering: str = "-dateModified") -> list[ClimbList]:
        """
        GET api/users/lists/{userId}/personal

        Récupère les listes personnelles d'un utilisateur.

        Args:
            user_id: ID de l'utilisateur
            ordering: Tri des résultats (défaut: -dateModified)

        Returns:
            Liste des listes de l'utilisateur
        """
        response = self._request(
            "get",
            f"api/users/lists/{user_id}/personal",
            params={"ordering": ordering}
        )
        return [ClimbList.from_api(lst) for lst in response.json()]

    def get_lists(
        self,
        filter_for: str,
        owner_id: Optional[str] = None,
        gym_id: Optional[str] = None,
        climbs_count_gte: Optional[int] = None
    ) -> list[ClimbList]:
        """
        GET api/lists

        Récupère des listes avec filtres.

        Args:
            filter_for: Type de filtre ('user', 'gym', 'style', 'from_others')
            owner_id: ID du propriétaire (pour filter_for='user')
            gym_id: ID du gym (pour filter_for='gym', 'style', 'from_others')
            climbs_count_gte: Nombre minimum de climbs

        Returns:
            Liste des listes correspondantes
        """
        params = {"filter_for": filter_for}
        if owner_id:
            params["owner_id"] = owner_id
        if gym_id:
            params["gym_id"] = gym_id
        if climbs_count_gte is not None:
            params["climbs_count_gte"] = climbs_count_gte

        response = self._request("get", "api/lists", params=params)
        return [ClimbList.from_api(lst) for lst in response.json()]

    def get_list(self, list_id: str) -> ClimbList:
        """
        GET api/lists/{listId}

        Récupère le détail d'une liste.

        Args:
            list_id: ID de la liste

        Returns:
            Détail de la liste
        """
        response = self._request("get", f"api/lists/{list_id}")
        return ClimbList.from_api(response.json())

    def get_list_items(
        self,
        list_id: str,
        page_size: int = 1000,
        exclude_mine: bool = False,
        grade_from: Optional[str] = None,
        grade_to: Optional[str] = None,
        ordering: Optional[str] = None,
        tags: Optional[str] = None,
        search: Optional[str] = None,
        show_circuit_only: bool = False
    ) -> list[ListItem]:
        """
        GET api/lists/{listId}/items

        Récupère les items (climbs) d'une liste.

        Args:
            list_id: ID de la liste
            page_size: Nombre d'items par page
            exclude_mine: Exclure mes climbs
            grade_from: Grade minimum
            grade_to: Grade maximum
            ordering: Tri
            tags: Tags à filtrer
            search: Recherche texte
            show_circuit_only: Uniquement les circuits

        Returns:
            Liste des items
        """
        params = {"page_size": page_size}
        if exclude_mine:
            params["exclude_mine"] = "true"
        if grade_from:
            params["grade_from"] = grade_from
        if grade_to:
            params["grade_to"] = grade_to
        if ordering:
            params["ordering"] = ordering
        if tags:
            params["tags"] = tags
        if search:
            params["search"] = search
        if show_circuit_only:
            params["show_circuit_only"] = "true"

        response = self._request("get", f"api/lists/{list_id}/items", params=params)
        data = response.json()
        # L'API retourne {results: [...]} ou directement [...]
        items = data.get("results", data) if isinstance(data, dict) else data
        return [ListItem.from_api(item) for item in items]

    def get_my_set_climbs(self, gym_id: str) -> list[Climb]:
        """
        GET api/gyms/{gymId}/my-set-climbs

        Récupère les climbs créés par l'utilisateur (ouvreur).

        Args:
            gym_id: ID du gym

        Returns:
            Liste des climbs créés par l'utilisateur
        """
        response = self._request("get", f"api/gyms/{gym_id}/my-set-climbs")
        return [Climb.from_api(c) for c in response.json()]

    def create_list(self, user_id: str, name: str, data: Optional[dict] = None) -> ClimbList:
        """
        POST api/users/{userId}/lists

        Crée une nouvelle liste.

        Args:
            user_id: ID de l'utilisateur
            name: Nom de la liste
            data: Données supplémentaires optionnelles

        Returns:
            Liste créée
        """
        payload = {"name": name}
        if data:
            payload.update(data)

        response = self._request(
            "post",
            f"api/users/{user_id}/lists",
            json=payload,
            headers={**self._auth_headers(), "Content-Type": "application/json"}
        )
        return ClimbList.from_api(response.json())

    def update_list(self, list_id: str, data: dict) -> ClimbList:
        """
        PATCH api/lists/{listId}

        Modifie une liste.

        Args:
            list_id: ID de la liste
            data: Données à modifier

        Returns:
            Liste modifiée
        """
        response = self._request(
            "patch",
            f"api/lists/{list_id}",
            json=data,
            headers={**self._auth_headers(), "Content-Type": "application/json"}
        )
        return ClimbList.from_api(response.json())

    def delete_list(self, list_id: str) -> bool:
        """
        DELETE api/lists/{listId}

        Supprime une liste.

        Args:
            list_id: ID de la liste

        Returns:
            True si succès
        """
        self._request("delete", f"api/lists/{list_id}")
        return True

    def add_climb_to_list(self, list_id: str, climb_id: str) -> bool:
        """
        POST api/lists/{listId}/items

        Ajoute un climb à une liste.

        Args:
            list_id: ID de la liste
            climb_id: ID du climb à ajouter

        Returns:
            True si succès
        """
        self._request(
            "post",
            f"api/lists/{list_id}/items",
            json={"climbId": climb_id},
            headers={**self._auth_headers(), "Content-Type": "application/json"}
        )
        return True

    def remove_climb_from_list(self, list_id: str, item_id: str) -> bool:
        """
        DELETE api/lists/{listId}/items/{itemId}

        Retire un climb d'une liste.

        Args:
            list_id: ID de la liste
            item_id: ID de l'item à retirer

        Returns:
            True si succès
        """
        self._request("delete", f"api/lists/{list_id}/items/{item_id}")
        return True

    def follow_list(self, list_id: str) -> bool:
        """
        POST api/lists/{listId}/follow

        Suit une liste.

        Args:
            list_id: ID de la liste

        Returns:
            True si succès
        """
        self._request("post", f"api/lists/{list_id}/follow")
        return True

    def unfollow_list(self, list_id: str) -> bool:
        """
        DELETE api/lists/{listId}/follow

        Ne plus suivre une liste.

        Args:
            list_id: ID de la liste

        Returns:
            True si succès
        """
        self._request("delete", f"api/lists/{list_id}/follow")
        return True

    def get_gym_lists(self, gym_id: str, page_size: int = 20) -> list[ClimbList]:
        """
        GET api/gyms/{gymId}/lists

        Récupère les listes populaires d'un gym.

        Args:
            gym_id: ID du gym
            page_size: Nombre de résultats

        Returns:
            Liste des listes populaires
        """
        response = self._request(
            "get",
            f"api/gyms/{gym_id}/lists",
            params={"page_size": page_size}
        )
        data = response.json()
        # Réponse paginée : {count, next, previous, results}
        results = data.get("results", data) if isinstance(data, dict) else data
        return [ClimbList.from_api(lst) for lst in results]
