"""
Gestionnaire d'assets (images) pour mastoc.

Télécharge et cache les images localement dans ~/.mastoc/images/
"""

import hashlib
import logging
import requests
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# URL de base Stokt pour les images (les images sont publiques)
STOKT_MEDIA_URL = "https://www.sostokt.com/media"


class AssetManager:
    """
    Gestionnaire de cache d'assets (images).

    Télécharge les images depuis Stokt et les cache localement.
    Le cache est dans ~/.mastoc/images/ avec un hash du chemin comme nom de fichier.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Args:
            cache_dir: Répertoire de cache (défaut: ~/.mastoc/images/)
        """
        self.cache_dir = cache_dir or (Path.home() / ".mastoc" / "images")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._session: Optional[requests.Session] = None

    @property
    def session(self) -> requests.Session:
        """Session HTTP réutilisable."""
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({
                "User-Agent": "mastoc/1.0",
            })
        return self._session

    def _get_cache_path(self, remote_path: str) -> Path:
        """
        Génère le chemin de cache local pour un chemin distant.

        Utilise un hash MD5 du chemin + l'extension originale.

        Args:
            remote_path: Chemin relatif de l'image (ex: "CACHE/images/walls/.../face.jpg")

        Returns:
            Chemin local du fichier caché
        """
        # Extraire l'extension
        ext = Path(remote_path).suffix or ".jpg"

        # Hash du chemin pour éviter les caractères spéciaux
        path_hash = hashlib.md5(remote_path.encode()).hexdigest()

        return self.cache_dir / f"{path_hash}{ext}"

    def _get_remote_url(self, remote_path: str) -> str:
        """
        Construit l'URL complète pour télécharger l'image.

        Args:
            remote_path: Chemin relatif de l'image

        Returns:
            URL complète
        """
        return f"{STOKT_MEDIA_URL}/{remote_path}"

    def get_face_image(self, picture_path: str, force_download: bool = False) -> Optional[Path]:
        """
        Récupère l'image d'une face (mur).

        Télécharge depuis Stokt si non présente dans le cache.

        Args:
            picture_path: Chemin de l'image (ex: "CACHE/images/walls/.../face.jpg")
            force_download: Force le re-téléchargement même si en cache

        Returns:
            Chemin local de l'image, ou None si échec
        """
        if not picture_path:
            logger.warning("picture_path est vide")
            return None

        cache_path = self._get_cache_path(picture_path)

        # Vérifier le cache
        if cache_path.exists() and not force_download:
            logger.debug(f"Image en cache: {cache_path}")
            return cache_path

        # Télécharger
        url = self._get_remote_url(picture_path)
        logger.info(f"Téléchargement image: {url}")

        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()

            # Sauvegarder
            cache_path.write_bytes(response.content)
            logger.info(f"Image sauvegardée: {cache_path} ({len(response.content)} bytes)")

            return cache_path

        except requests.RequestException as e:
            logger.error(f"Erreur téléchargement {url}: {e}")
            return None

    def get_user_avatar(self, avatar_path: str, force_download: bool = False) -> Optional[Path]:
        """
        Récupère l'avatar d'un utilisateur.

        Args:
            avatar_path: Chemin de l'avatar
            force_download: Force le re-téléchargement

        Returns:
            Chemin local de l'avatar, ou None si échec
        """
        # Même logique que pour les images de face
        return self.get_face_image(avatar_path, force_download)

    def is_cached(self, remote_path: str) -> bool:
        """Vérifie si une image est en cache."""
        if not remote_path:
            return False
        return self._get_cache_path(remote_path).exists()

    def get_cache_size(self) -> int:
        """Retourne la taille totale du cache en bytes."""
        total = 0
        for f in self.cache_dir.glob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total

    def clear_cache(self) -> int:
        """
        Vide le cache.

        Returns:
            Nombre de fichiers supprimés
        """
        count = 0
        for f in self.cache_dir.glob("*"):
            if f.is_file():
                f.unlink()
                count += 1
        logger.info(f"Cache vidé: {count} fichiers supprimés")
        return count


# Instance globale (singleton)
_asset_manager: Optional[AssetManager] = None


def get_asset_manager() -> AssetManager:
    """Retourne l'instance globale du gestionnaire d'assets."""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager()
    return _asset_manager
