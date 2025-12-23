"""
Application de test pour le wizard de création de blocs.

Usage:
    python -m mastock.gui.creation_app
"""

import sys
import logging

from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt6.QtCore import Qt

from mastock.db import Database
from mastock.core.hold_index import HoldClimbIndex
from mastock.api.client import StoktAPI, MONTOBOARD_GYM_ID
from mastock.gui.creation import CreationWizard

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d | %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# Face ID de Montoboard (récupéré via GET /api/gyms/{gymId}/walls)
MONTOBOARD_FACE_ID = "61b42d14-c629-434a-8827-801512151a18"


class CreationTestApp(QMainWindow):
    """Application de test pour le wizard de création."""

    def __init__(self):
        super().__init__()
        logger.info("Démarrage CreationTestApp...")

        # Charger les données
        self.db = Database()
        self.index = HoldClimbIndex.from_database(self.db)
        logger.info(f"Index: {len(self.index.climbs)} climbs, {len(self.index.holds)} holds")

        # Initialiser l'API
        self.api = self._init_api()

        # Configurer la fenêtre
        self.setWindowTitle("mastock - Création de bloc (TEST)")
        self.setMinimumSize(1200, 800)

        # Créer le wizard
        self.wizard = CreationWizard(
            index=self.index,
            api=self.api,
            face_id=MONTOBOARD_FACE_ID
        )
        self.wizard.climb_created.connect(self._on_climb_created)
        self.wizard.cancelled.connect(self._on_cancelled)

        self.setCentralWidget(self.wizard)

        logger.info("CreationTestApp prêt")

    def _init_api(self) -> StoktAPI | None:
        """Initialise l'API avec le token stocké."""
        TOKEN = "dba723cbee34ff3cf049b12150a21dc8919c3cf8"
        try:
            api = StoktAPI()
            api.set_token(TOKEN)
            # Vérifier le token
            api.get_user_profile()
            logger.info("API initialisée avec succès")
            return api
        except Exception as e:
            logger.warning(f"API non disponible: {e}")
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
    app.setApplicationName("mastock Creation Test")

    window = CreationTestApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
