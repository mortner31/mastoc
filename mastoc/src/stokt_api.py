"""
Stokt API Client - Client pour l'API sostokt.com

Endpoints fonctionnels découverts par analyse du code décompilé de l'app React Native.
"""

import requests
from dataclasses import dataclass
from typing import Optional


@dataclass
class StoktConfig:
    """Configuration pour l'API Stokt"""
    base_url: str = "https://www.sostokt.com"
    timeout: int = 60


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
        """Construit l'URL complète"""
        return f"{self.config.base_url}/{endpoint}"

    def _auth_headers(self) -> dict:
        """Retourne les headers d'authentification"""
        if not self.token:
            raise ValueError("Non authentifié. Appelez login() d'abord.")
        return {"Authorization": f"Token {self.token}"}

    def login(self, username: str, password: str) -> dict:
        """
        Authentification via api/token-auth
        Retourne le token d'authentification
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
        """Définit le token d'authentification manuellement"""
        self.token = token

    def get_user_profile(self) -> dict:
        """
        GET api/users/me
        Retourne le profil de l'utilisateur connecté
        """
        response = self.session.get(
            self._url("api/users/me"),
            headers=self._auth_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_gym_summary(self, gym_id: str) -> dict:
        """
        GET api/gyms/{gym_id}/summary
        Retourne le résumé du gym (walls, stats, managers)
        """
        response = self.session.get(
            self._url(f"api/gyms/{gym_id}/summary"),
            headers=self._auth_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_gym_walls(self, gym_id: str) -> list:
        """
        GET api/gyms/{gym_id}/walls
        Retourne la liste des murs avec leurs faces
        """
        response = self.session.get(
            self._url(f"api/gyms/{gym_id}/walls"),
            headers=self._auth_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_gym_climbs(self, gym_id: str, max_age: int = 60) -> dict:
        """
        GET api/gyms/{gym_id}/climbs?max_age={max_age}
        Retourne les climbs récents du gym (première page)

        Args:
            gym_id: ID du gym
            max_age: Nombre de jours (défaut: 60, utiliser 9999 pour tous)
        """
        response = self.session.get(
            self._url(f"api/gyms/{gym_id}/climbs"),
            params={"max_age": max_age},
            headers=self._auth_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_all_gym_climbs(self, gym_id: str) -> list:
        """
        Récupère TOUS les climbs d'un gym avec pagination automatique.
        Utilise max_age=9999 pour ne pas avoir de limite temporelle.

        Args:
            gym_id: ID du gym

        Returns:
            Liste de tous les climbs
        """
        all_climbs = []

        # Première page
        data = self.get_gym_climbs(gym_id, max_age=9999)
        all_climbs.extend(data.get("results", []))
        total = data.get("count", 0)

        # Pagination
        while data.get("next"):
            response = self.session.get(
                data["next"],
                headers=self._auth_headers(),
                timeout=self.config.timeout
            )
            response.raise_for_status()
            data = response.json()
            all_climbs.extend(data.get("results", []))

        return all_climbs

    def get_my_sent_climbs(self, gym_id: str) -> list:
        """
        GET api/gyms/{gym_id}/my-sent-climbs
        Retourne les climbs validés par l'utilisateur dans ce gym
        """
        response = self.session.get(
            self._url(f"api/gyms/{gym_id}/my-sent-climbs"),
            headers=self._auth_headers(),
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()

    def get_face_image_url(self, face_path: str) -> str:
        """
        Construit l'URL complète pour une image de face

        Args:
            face_path: Chemin relatif (ex: CACHE/images/walls/.../ref_pic.jpg)
        """
        return f"{self.config.base_url}/media/{face_path}"

    def download_image(self, image_path: str, save_path: str) -> bool:
        """
        Télécharge une image

        Args:
            image_path: Chemin relatif de l'image
            save_path: Chemin local où sauvegarder
        """
        url = self.get_face_image_url(image_path)
        response = self.session.get(url, timeout=self.config.timeout)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return True


def parse_holds_list(holds_str: str) -> list[dict]:
    """
    Parse le format holdsList d'un climb

    Format: "S829279 S829528 O828906 T829009"
    - S = Start (prise de départ)
    - O = Other (prise normale)
    - F = Feet (pied obligatoire)
    - T = Top (prise finale)

    Retourne une liste de dicts: [{"type": "S", "id": 829279}, ...]
    """
    if not holds_str:
        return []

    holds = []
    for hold in holds_str.split():
        if len(hold) > 1:
            hold_type = hold[0]
            hold_id = int(hold[1:])
            holds.append({"type": hold_type, "id": hold_id})
    return holds


# Constantes
MONTOBOARD_GYM_ID = "be149ef2-317d-4c73-8d7d-50074577d2fa"


if __name__ == "__main__":
    # Exemple d'utilisation
    import json

    # Token existant (ou utiliser login())
    TOKEN = "dba723cbee34ff3cf049b12150a21dc8919c3cf8"

    api = StoktAPI()
    api.set_token(TOKEN)

    # Récupérer le résumé du gym
    print("=== Gym Summary ===")
    summary = api.get_gym_summary(MONTOBOARD_GYM_ID)
    print(f"Gym: {summary['displayName']}")
    print(f"Total climbs: {summary['numberOfClimbs']}")
    print(f"Total climbers: {summary['numberOfClimbers']}")

    # Récupérer les walls
    print("\n=== Walls ===")
    walls = api.get_gym_walls(MONTOBOARD_GYM_ID)
    for wall in walls:
        print(f"Wall: {wall['name']} (ID: {wall['id']})")
        for face in wall.get('faces', []):
            print(f"  Face: {face['id']} - {face['totalClimbs']} climbs")

    # Récupérer mes climbs validés
    print("\n=== My Sent Climbs ===")
    my_climbs = api.get_my_sent_climbs(MONTOBOARD_GYM_ID)
    print(f"Nombre de climbs validés: {len(my_climbs)}")
    for climb in my_climbs[:3]:  # Afficher les 3 premiers
        print(f"  - {climb['name']} ({climb['crowdGrade']['font']})")
        holds = parse_holds_list(climb['holdsList'])
        print(f"    Prises: {len(holds)} (Start: {sum(1 for h in holds if h['type']=='S')}, Top: {sum(1 for h in holds if h['type']=='T')})")

    # Récupérer les climbs récents
    print("\n=== Recent Climbs (60 days) ===")
    recent = api.get_gym_climbs(MONTOBOARD_GYM_ID, max_age=60)
    print(f"Nombre de climbs récents: {recent['count']}")
