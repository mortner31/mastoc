"""
Application de test pour le wizard de création de blocs.

Usage:
    python -m mastoc.gui.creation_app
"""

import sys
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

from mastoc.db import Database
from mastoc.core.hold_index import HoldClimbIndex
from mastoc.api.client import StoktAPI
from mastoc.core.backend import BackendSwitch, BackendConfig, BackendSource, MONTOBOARD_GYM_ID
from mastoc.core.config import AppConfig
from mastoc.gui.creation import CreationWizard

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Face ID de Montoboard (utilisé comme fallback)
MONTOBOARD_FACE_ID = "61b42d14-c629-434a-8827-801512151a18"


class CreationTestApp(QMainWindow):
    """Application de test pour le wizard de création."""

    def __init__(self):
        super().__init__()
        logger.info("Démarrage CreationTestApp...")

        # Charger la configuration persistante
        self._app_config = AppConfig.load()
        self._current_source = BackendSource(self._app_config.source)
        logger.info(f"Config: source={self._current_source.value}")

        # Charger les données (base selon source ADR-006)
        db_path = self._get_db_path()
        self.db = Database(db_path)
        self.index = HoldClimbIndex.from_database(self.db)
        logger.info(f"Index: {len(self.index.climbs)} climbs, {len(self.index.holds)} holds ({db_path.name})")

        # Initialiser l'API
        self.api = self._init_api()

        # Déterminer le face_id (depuis la DB ou fallback)
        face_id = self._get_face_id()

        # Configurer la fenêtre
        self.setWindowTitle("mastoc - Création de bloc (TEST)")
        self.setMinimumSize(1200, 800)

        # Créer le wizard
        self.wizard = CreationWizard(
            index=self.index,
            api=self.api,
            face_id=face_id
        )
        self.wizard.climb_created.connect(self._on_climb_created)
        self.wizard.cancelled.connect(self._on_cancelled)

        self.setCentralWidget(self.wizard)

        logger.info("CreationTestApp prêt")

    def _get_db_path(self) -> Path:
        """Retourne le chemin de la base SQLite selon la source (ADR-006)."""
        base_dir = Path.home() / ".mastoc"
        if self._current_source == BackendSource.RAILWAY:
            return base_dir / "railway.db"
        return base_dir / "stokt.db"

    def _get_face_id(self) -> str:
        """Récupère le face_id depuis la base de données ou utilise le fallback."""
        if self.index.climbs:
            # Utiliser le face_id du premier climb (climbs est un dict)
            first_climb = next(iter(self.index.climbs.values()))
            return first_climb.face_id
        return MONTOBOARD_FACE_ID

    def _init_api(self):
        """Initialise le backend avec la config persistante."""
        try:
            self.backend = BackendSwitch(BackendConfig(
                source=self._current_source,
                railway_api_key=self._app_config.railway_api_key,
                railway_url=self._app_config.railway_url,
                stokt_token="dba723cbee34ff3cf049b12150a21dc8919c3cf8",  # Token Stokt legacy
            ))

            # Sélectionner l'API selon la source
            if self._current_source == BackendSource.RAILWAY and self.backend.railway:
                logger.info("Backend Railway initialisé")
                return self.backend.railway.api
            elif self.backend.stokt:
                api = self.backend.stokt.api
                if api and hasattr(api, 'get_user_profile'):
                    try:
                        api.get_user_profile()
                        logger.info("Backend Stokt initialisé avec succès")
                    except Exception:
                        logger.warning("Token Stokt invalide")
                return api
            return None

        except Exception as e:
            logger.warning(f"Backend non disponible: {e}")
            self.backend = None
            QMessageBox.warning(
                self,
                "API",
                f"L'API n'est pas disponible:\n{e}\n\n"
                "Le wizard fonctionnera en mode démo (pas de soumission réelle)."
            )
            return None

    def _on_climb_created(self, climb_id: str):
        """Appelé quand un climb est créé."""
        logger.info(f"Climb créé: {climb_id}")
        QMessageBox.information(
            self,
            "Succès",
            f"Bloc créé avec succès!\n\nID: {climb_id}"
        )
        self.close()

    def _on_cancelled(self):
        """Appelé quand la création est annulée."""
        logger.info("Création annulée")
        self.close()


def main():
    """Point d'entrée de l'application."""
    app = QApplication(sys.argv)
    app.setApplicationName("mastoc Creation Test")

    window = CreationTestApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
