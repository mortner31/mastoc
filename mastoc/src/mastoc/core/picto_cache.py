"""
Cache persistant pour les pictos des blocs.

Stocke les pictos sur disque pour éviter de les régénérer à chaque lancement.
"""

import logging
import hashlib
from pathlib import Path
from typing import Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed

from PIL import Image as PILImage

from mastoc.api.models import Climb, Hold
from mastoc.core.picto import generate_climb_picto, compute_top_holds

logger = logging.getLogger(__name__)

# Dossier de cache par défaut
DEFAULT_CACHE_DIR = Path.home() / ".mastoc" / "pictos"


class PictoCache:
    """Gestionnaire de cache pour les pictos."""

    def __init__(self, cache_dir: Path = None, size: int = 48):
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
        self.size = size
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache pictos: {self.cache_dir}")

    def _get_picto_path(self, climb_id: str) -> Path:
        """Retourne le chemin du fichier picto pour un climb."""
        # Hash court pour éviter les problèmes de noms de fichiers
        safe_id = hashlib.md5(climb_id.encode()).hexdigest()[:12]
        return self.cache_dir / f"{safe_id}.png"

    def has_picto(self, climb_id: str) -> bool:
        """Vérifie si le picto existe dans le cache."""
        return self._get_picto_path(climb_id).exists()

    def get_picto(self, climb_id: str) -> Optional[PILImage.Image]:
        """Récupère un picto depuis le cache."""
        path = self._get_picto_path(climb_id)
        if path.exists():
            try:
                return PILImage.open(path)
            except Exception as e:
                logger.warning(f"Erreur lecture picto {climb_id}: {e}")
        return None

    def save_picto(self, climb_id: str, picto: PILImage.Image):
        """Sauvegarde un picto dans le cache."""
        path = self._get_picto_path(climb_id)
        try:
            picto.save(path, format='PNG')
        except Exception as e:
            logger.error(f"Erreur sauvegarde picto {climb_id}: {e}")

    def clear(self):
        """Vide le cache."""
        count = 0
        for f in self.cache_dir.glob("*.png"):
            f.unlink()
            count += 1
        logger.info(f"Cache vidé: {count} pictos supprimés")

    def get_cached_count(self) -> int:
        """Retourne le nombre de pictos en cache."""
        return len(list(self.cache_dir.glob("*.png")))

    def generate_all(
        self,
        climbs: list[Climb],
        holds_map: dict[int, Hold],
        wall_image: PILImage.Image = None,
        progress_callback: Callable[[int, int, str], None] = None,
        force: bool = False
    ):
        """
        Génère tous les pictos manquants.

        Args:
            climbs: Liste des blocs
            holds_map: Mapping hold_id -> Hold
            wall_image: Image du mur
            progress_callback: Callback(current, total, message)
            force: Régénérer même si existe déjà
        """
        # Filtrer les climbs à générer
        if force:
            to_generate = climbs
        else:
            to_generate = [c for c in climbs if not self.has_picto(c.id)]

        if not to_generate:
            logger.info("Tous les pictos sont déjà en cache")
            if progress_callback:
                progress_callback(len(climbs), len(climbs), "Pictos à jour")
            return

        logger.info(f"Génération de {len(to_generate)}/{len(climbs)} pictos...")

        # Calculer les top holds
        top_holds = compute_top_holds(climbs, n=20)

        # Générer les pictos
        for i, climb in enumerate(to_generate):
            if progress_callback:
                progress_callback(i, len(to_generate), f"Picto: {climb.name[:20]}...")

            try:
                picto = generate_climb_picto(
                    climb,
                    holds_map,
                    wall_image,
                    size=self.size,
                    top_holds=top_holds
                )
                self.save_picto(climb.id, picto)
            except Exception as e:
                logger.error(f"Erreur génération picto {climb.name}: {e}")

        if progress_callback:
            progress_callback(len(to_generate), len(to_generate), "Pictos générés")

        logger.info(f"Génération terminée: {len(to_generate)} pictos")
