"""
Configuration persistante pour mastoc.

Sauvegarde les préférences utilisateur dans ~/.mastoc/config.json
"""

import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AppConfig:
    """Configuration de l'application."""

    # Source de données
    source: str = "stokt"  # "stokt" ou "railway"

    # Railway
    railway_api_key: Optional[str] = None
    railway_url: str = "https://mastoc-production.up.railway.app"

    # Stokt (token expire, donc on ne le persiste pas)
    # stokt_token n'est pas persisté volontairement

    @classmethod
    def get_config_path(cls) -> Path:
        """Retourne le chemin du fichier de configuration."""
        return Path.home() / ".mastoc" / "config.json"

    @classmethod
    def load(cls) -> "AppConfig":
        """Charge la configuration depuis le fichier."""
        config_path = cls.get_config_path()

        if not config_path.exists():
            logger.info("Pas de fichier de configuration, utilisation des défauts")
            return cls()

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Créer l'instance avec les valeurs chargées
            config = cls(
                source=data.get("source", "stokt"),
                railway_api_key=data.get("railway_api_key"),
                railway_url=data.get("railway_url", "https://mastoc-production.up.railway.app"),
            )
            logger.info(f"Configuration chargée depuis {config_path}")
            logger.debug(f"  Source: {config.source}")
            logger.debug(f"  Railway API Key: {'***' if config.railway_api_key else 'non configurée'}")
            return config

        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {e}")
            return cls()
        except Exception as e:
            logger.error(f"Erreur de chargement config: {e}")
            return cls()

    def save(self) -> bool:
        """Sauvegarde la configuration dans le fichier."""
        config_path = self.get_config_path()

        # Créer le dossier si nécessaire
        config_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            data = {
                "source": self.source,
                "railway_api_key": self.railway_api_key,
                "railway_url": self.railway_url,
            }

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            logger.info(f"Configuration sauvegardée dans {config_path}")
            return True

        except Exception as e:
            logger.error(f"Erreur de sauvegarde config: {e}")
            return False
