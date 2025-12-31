"""
Gestionnaire d'authentification mastoc.

Gère :
- Login/Register/Logout
- Persistance des tokens (access + refresh)
- Auto-refresh avant expiration
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable
import base64
import requests

logger = logging.getLogger(__name__)


@dataclass
class TokenInfo:
    """Information sur les tokens."""
    access_token: str
    refresh_token: str
    expires_at: float  # timestamp
    user_id: str
    email: str
    username: str
    full_name: str
    role: str


@dataclass
class UserProfile:
    """Profil utilisateur mastoc."""
    id: str
    email: Optional[str]
    username: Optional[str]
    full_name: str
    role: str
    avatar_path: Optional[str] = None


class AuthError(Exception):
    """Erreur d'authentification."""
    pass


class AuthManager:
    """
    Gestionnaire d'authentification mastoc.

    Usage:
        auth = AuthManager(base_url="https://mastoc-production.up.railway.app")

        # Login
        if auth.login("user@example.com", "password"):
            print(f"Connecté en tant que {auth.current_user.full_name}")

        # Check auth
        if auth.is_authenticated:
            print(f"Token valide pour {auth.current_user.email}")

        # Logout
        auth.logout()
    """

    AUTH_FILE = Path.home() / ".mastoc" / "auth.json"
    REFRESH_MARGIN = 300  # Refresh 5 min avant expiration

    def __init__(self, base_url: str = "https://mastoc-production.up.railway.app"):
        self.base_url = base_url.rstrip("/")
        self._token_info: Optional[TokenInfo] = None
        self._on_auth_change: Optional[Callable[[bool], None]] = None
        self._load_tokens()

    @property
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié avec un token valide."""
        if not self._token_info:
            return False

        # Vérifier l'expiration
        if time.time() >= self._token_info.expires_at:
            # Essayer de refresh
            if self._try_refresh():
                return True
            return False

        return True

    @property
    def current_user(self) -> Optional[UserProfile]:
        """Retourne le profil de l'utilisateur connecté."""
        if not self._token_info:
            return None

        return UserProfile(
            id=self._token_info.user_id,
            email=self._token_info.email,
            username=self._token_info.username,
            full_name=self._token_info.full_name,
            role=self._token_info.role,
        )

    @property
    def access_token(self) -> Optional[str]:
        """Retourne l'access token courant (avec auto-refresh si nécessaire)."""
        if not self._token_info:
            return None

        # Auto-refresh si proche de l'expiration
        time_left = self._token_info.expires_at - time.time()
        if time_left < self.REFRESH_MARGIN:
            self._try_refresh()

        return self._token_info.access_token if self._token_info else None

    def set_on_auth_change(self, callback: Callable[[bool], None]):
        """Définit un callback appelé quand l'état d'auth change."""
        self._on_auth_change = callback

    # =========================================================================
    # Actions d'authentification
    # =========================================================================

    def register(
        self,
        email: str,
        username: str,
        password: str,
        full_name: str
    ) -> UserProfile:
        """
        Crée un nouveau compte utilisateur.

        Args:
            email: Email (unique)
            username: Nom d'utilisateur (unique, 3-50 chars)
            password: Mot de passe (min 8 chars)
            full_name: Nom complet

        Returns:
            Profil de l'utilisateur créé

        Raises:
            AuthError: Si l'inscription échoue
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/register",
                json={
                    "email": email,
                    "username": username,
                    "password": password,
                    "full_name": full_name,
                },
                timeout=30,
            )

            if response.status_code == 201:
                data = response.json()
                return UserProfile(
                    id=data["id"],
                    email=data["email"],
                    username=data["username"],
                    full_name=data["full_name"],
                    role="user",
                )
            elif response.status_code == 400:
                error = response.json().get("detail", "Erreur d'inscription")
                raise AuthError(error)
            else:
                raise AuthError(f"Erreur serveur: {response.status_code}")

        except requests.RequestException as e:
            raise AuthError(f"Erreur de connexion: {e}")

    def login(self, email_or_username: str, password: str) -> bool:
        """
        Connexion avec email/username et mot de passe.

        Args:
            email_or_username: Email ou nom d'utilisateur
            password: Mot de passe

        Returns:
            True si connexion réussie

        Raises:
            AuthError: Si la connexion échoue
        """
        try:
            # OAuth2 form data
            response = requests.post(
                f"{self.base_url}/api/auth/login",
                data={
                    "username": email_or_username,
                    "password": password,
                },
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                self._save_login_response(data)
                self._notify_auth_change(True)
                logger.info(f"Connecté en tant que {data['email']}")
                return True
            elif response.status_code in (401, 403):
                error = response.json().get("detail", "Identifiants incorrects")
                raise AuthError(error)
            else:
                raise AuthError(f"Erreur serveur: {response.status_code}")

        except requests.RequestException as e:
            raise AuthError(f"Erreur de connexion: {e}")

    def logout(self):
        """Déconnexion (supprime les tokens locaux)."""
        self._token_info = None
        self._delete_tokens()
        self._notify_auth_change(False)
        logger.info("Déconnecté")

    def refresh(self) -> bool:
        """
        Renouvelle l'access token avec le refresh token.

        Returns:
            True si le refresh a réussi
        """
        return self._try_refresh()

    def request_password_reset(self, email: str) -> bool:
        """
        Demande un reset de mot de passe.

        Args:
            email: Email du compte

        Returns:
            True (toujours, pour ne pas révéler si l'email existe)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/reset-password",
                json={"email": email},
                timeout=30,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def confirm_password_reset(self, token: str, new_password: str) -> bool:
        """
        Confirme le reset de mot de passe.

        Args:
            token: Token de reset (reçu par email)
            new_password: Nouveau mot de passe

        Returns:
            True si réussi

        Raises:
            AuthError: Si le reset échoue
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/auth/reset-password/confirm",
                json={"token": token, "new_password": new_password},
                timeout=30,
            )

            if response.status_code == 200:
                return True
            else:
                error = response.json().get("detail", "Erreur de reset")
                raise AuthError(error)

        except requests.RequestException as e:
            raise AuthError(f"Erreur de connexion: {e}")

    # =========================================================================
    # Profil utilisateur
    # =========================================================================

    def get_profile(self) -> Optional[UserProfile]:
        """
        Récupère le profil complet depuis le serveur.

        Returns:
            Profil utilisateur ou None si non authentifié
        """
        if not self.access_token:
            return None

        try:
            response = requests.get(
                f"{self.base_url}/api/users/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                return UserProfile(
                    id=data["id"],
                    email=data.get("email"),
                    username=data.get("username"),
                    full_name=data["full_name"],
                    role=data["role"],
                    avatar_path=data.get("avatar_path"),
                )

        except requests.RequestException:
            pass

        return None

    def update_profile(
        self,
        full_name: Optional[str] = None,
        username: Optional[str] = None
    ) -> Optional[UserProfile]:
        """
        Met à jour le profil utilisateur.

        Args:
            full_name: Nouveau nom complet
            username: Nouveau username

        Returns:
            Profil mis à jour ou None si échec
        """
        if not self.access_token:
            return None

        data = {}
        if full_name:
            data["full_name"] = full_name
        if username:
            data["username"] = username

        if not data:
            return self.current_user

        try:
            response = requests.patch(
                f"{self.base_url}/api/users/me",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json=data,
                timeout=30,
            )

            if response.status_code == 200:
                resp_data = response.json()
                # Mettre à jour le token info local
                if self._token_info:
                    if full_name:
                        self._token_info.full_name = full_name
                    if username:
                        self._token_info.username = username
                    self._save_tokens()

                return UserProfile(
                    id=resp_data["id"],
                    email=resp_data.get("email"),
                    username=resp_data.get("username"),
                    full_name=resp_data["full_name"],
                    role=resp_data["role"],
                    avatar_path=resp_data.get("avatar_path"),
                )

        except requests.RequestException:
            pass

        return None

    def change_password(self, current_password: str, new_password: str) -> bool:
        """
        Change le mot de passe.

        Args:
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe

        Returns:
            True si réussi

        Raises:
            AuthError: Si le changement échoue
        """
        if not self.access_token:
            raise AuthError("Non authentifié")

        try:
            response = requests.post(
                f"{self.base_url}/api/users/me/password",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json={
                    "current_password": current_password,
                    "new_password": new_password,
                },
                timeout=30,
            )

            if response.status_code == 200:
                return True
            else:
                error = response.json().get("detail", "Erreur de changement")
                raise AuthError(error)

        except requests.RequestException as e:
            raise AuthError(f"Erreur de connexion: {e}")

    # =========================================================================
    # Gestion interne des tokens
    # =========================================================================

    def _save_login_response(self, data: dict):
        """Sauvegarde la réponse de login."""
        expires_in = data.get("expires_in", 86400)

        self._token_info = TokenInfo(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_at=time.time() + expires_in,
            user_id=data["user_id"],
            email=data["email"],
            username=data["username"],
            full_name=data["full_name"],
            role=data["role"],
        )

        self._save_tokens()

    def _try_refresh(self) -> bool:
        """Essaie de rafraîchir le token."""
        if not self._token_info or not self._token_info.refresh_token:
            return False

        try:
            response = requests.post(
                f"{self.base_url}/api/auth/refresh",
                json={"refresh_token": self._token_info.refresh_token},
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                expires_in = data.get("expires_in", 86400)

                self._token_info.access_token = data["access_token"]
                self._token_info.refresh_token = data["refresh_token"]
                self._token_info.expires_at = time.time() + expires_in

                self._save_tokens()
                logger.debug("Token rafraîchi")
                return True
            else:
                # Refresh token expiré, déconnecter
                logger.warning("Refresh token invalide, déconnexion")
                self.logout()
                return False

        except requests.RequestException as e:
            logger.error(f"Erreur refresh: {e}")
            return False

    def _save_tokens(self):
        """Sauvegarde les tokens dans le fichier."""
        if not self._token_info:
            return

        self.AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "access_token": self._token_info.access_token,
            "refresh_token": self._token_info.refresh_token,
            "expires_at": self._token_info.expires_at,
            "user_id": self._token_info.user_id,
            "email": self._token_info.email,
            "username": self._token_info.username,
            "full_name": self._token_info.full_name,
            "role": self._token_info.role,
        }

        try:
            with open(self.AUTH_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            logger.debug(f"Tokens sauvegardés dans {self.AUTH_FILE}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde tokens: {e}")

    def _load_tokens(self):
        """Charge les tokens depuis le fichier."""
        if not self.AUTH_FILE.exists():
            return

        try:
            with open(self.AUTH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._token_info = TokenInfo(
                access_token=data["access_token"],
                refresh_token=data["refresh_token"],
                expires_at=data["expires_at"],
                user_id=data["user_id"],
                email=data["email"],
                username=data["username"],
                full_name=data["full_name"],
                role=data["role"],
            )

            logger.debug(f"Tokens chargés pour {self._token_info.email}")

        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Tokens invalides, suppression: {e}")
            self._delete_tokens()
        except Exception as e:
            logger.error(f"Erreur chargement tokens: {e}")

    def _delete_tokens(self):
        """Supprime le fichier de tokens."""
        try:
            if self.AUTH_FILE.exists():
                self.AUTH_FILE.unlink()
                logger.debug("Fichier tokens supprimé")
        except Exception as e:
            logger.error(f"Erreur suppression tokens: {e}")

    def _notify_auth_change(self, is_authenticated: bool):
        """Notifie le changement d'état d'authentification."""
        if self._on_auth_change:
            try:
                self._on_auth_change(is_authenticated)
            except Exception as e:
                logger.error(f"Erreur callback auth: {e}")
