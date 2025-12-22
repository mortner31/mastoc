"""
Synchronisation entre l'API Stokt et la base de données locale.

Gère le téléchargement initial et les mises à jour incrémentales.
"""

from datetime import datetime
from typing import Callable, Optional

from mastock.api.client import StoktAPI, AuthenticationError, MONTOBOARD_GYM_ID
from mastock.db import Database, ClimbRepository, HoldRepository
from mastock.api.models import Climb


class SyncResult:
    """Résultat d'une synchronisation."""

    def __init__(self):
        self.climbs_added = 0
        self.climbs_updated = 0
        self.holds_added = 0
        self.errors: list[str] = []
        self.success = True

    def __repr__(self):
        return (
            f"SyncResult(added={self.climbs_added}, updated={self.climbs_updated}, "
            f"holds={self.holds_added}, success={self.success})"
        )


ProgressCallback = Callable[[int, int, str], None]


class SyncManager:
    """Gère la synchronisation API ↔ BD locale."""

    def __init__(
        self,
        api: StoktAPI,
        db: Database,
        gym_id: str = MONTOBOARD_GYM_ID
    ):
        self.api = api
        self.db = db
        self.gym_id = gym_id
        self.climb_repo = ClimbRepository(db)
        self.hold_repo = HoldRepository(db)

    def get_sync_status(self) -> dict:
        """Retourne le statut de synchronisation."""
        last_sync = self.db.get_last_sync()
        climb_count = self.db.get_climb_count()
        hold_count = self.db.get_hold_count()

        return {
            "last_sync": last_sync.isoformat() if last_sync else None,
            "climb_count": climb_count,
            "hold_count": hold_count,
            "is_synced": climb_count > 0 and hold_count > 0,
        }

    def sync_full(
        self,
        callback: Optional[ProgressCallback] = None,
        clear_existing: bool = False
    ) -> SyncResult:
        """
        Synchronisation complète depuis l'API.

        Args:
            callback: Fonction (current, total, message) pour la progression
            clear_existing: Si True, supprime les données existantes

        Returns:
            SyncResult avec les statistiques
        """
        result = SyncResult()

        try:
            if clear_existing:
                if callback:
                    callback(0, 0, "Suppression des données existantes...")
                self.db.clear_all()

            # 1. Récupérer les walls/faces pour avoir les face_ids
            if callback:
                callback(0, 0, "Récupération des murs...")

            walls = self.api.get_gym_walls(self.gym_id)
            face_ids = []
            for wall in walls:
                for face in wall.faces:
                    face_ids.append(face.id)

            # 2. Récupérer les prises de chaque face
            if callback:
                callback(0, len(face_ids), "Récupération des prises...")

            for i, face_id in enumerate(face_ids):
                try:
                    face = self.api.get_face_setup(face_id)
                    self.hold_repo.save_face(face)
                    result.holds_added += len(face.holds)
                    if callback:
                        callback(i + 1, len(face_ids), f"Face {face_id}: {len(face.holds)} prises")
                except Exception as e:
                    result.errors.append(f"Erreur face {face_id}: {e}")

            # 3. Récupérer tous les climbs
            if callback:
                callback(0, 0, "Récupération des climbs...")

            def climb_progress(current, total):
                if callback:
                    callback(current, total, f"Climbs: {current}/{total}")

            climbs = self.api.get_all_gym_climbs(self.gym_id, callback=climb_progress)

            # 4. Sauvegarder les climbs
            if callback:
                callback(0, len(climbs), "Sauvegarde des climbs...")

            def save_progress(current, total):
                if callback:
                    callback(current, total, f"Sauvegarde: {current}/{total}")

            self.climb_repo.save_climbs(climbs, callback=save_progress)
            result.climbs_added = len(climbs)

            # 5. Mettre à jour la date de sync
            self.db.set_last_sync()

            if callback:
                callback(len(climbs), len(climbs), "Synchronisation terminée!")

        except AuthenticationError as e:
            result.success = False
            result.errors.append(f"Erreur d'authentification: {e}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Erreur: {e}")

        return result

    def sync_incremental(
        self,
        callback: Optional[ProgressCallback] = None
    ) -> SyncResult:
        """
        Synchronisation incrémentale (nouveaux climbs seulement).

        Récupère les climbs depuis la dernière synchronisation.

        Returns:
            SyncResult avec les statistiques
        """
        result = SyncResult()
        last_sync = self.db.get_last_sync()

        if not last_sync:
            # Pas de sync précédente, faire une sync complète
            return self.sync_full(callback=callback)

        try:
            if callback:
                callback(0, 0, "Vérification des nouveaux climbs...")

            # Récupérer les climbs existants
            existing_climbs = self.climb_repo.get_all_climbs()
            existing_ids = {c.id for c in existing_climbs}

            # Récupérer les climbs depuis l'API
            def climb_progress(current, total):
                if callback:
                    callback(current, total, f"Téléchargement: {current}/{total}")

            all_climbs = self.api.get_all_gym_climbs(self.gym_id, callback=climb_progress)

            # Identifier les nouveaux et les mis à jour
            new_climbs = []
            updated_climbs = []

            for climb in all_climbs:
                if climb.id not in existing_ids:
                    new_climbs.append(climb)
                else:
                    # Vérifier si le climb a été modifié
                    existing = next((c for c in existing_climbs if c.id == climb.id), None)
                    if existing and self._climb_changed(existing, climb):
                        updated_climbs.append(climb)

            if callback:
                callback(0, len(new_climbs) + len(updated_climbs),
                        f"{len(new_climbs)} nouveaux, {len(updated_climbs)} mis à jour")

            # Sauvegarder les changements
            for i, climb in enumerate(new_climbs + updated_climbs):
                self.climb_repo.save_climb(climb)
                if callback:
                    callback(i + 1, len(new_climbs) + len(updated_climbs), "Sauvegarde...")

            result.climbs_added = len(new_climbs)
            result.climbs_updated = len(updated_climbs)

            # Mettre à jour la date de sync
            self.db.set_last_sync()

            if callback:
                msg = f"Sync terminée: {len(new_climbs)} ajoutés, {len(updated_climbs)} mis à jour"
                callback(len(new_climbs) + len(updated_climbs),
                        len(new_climbs) + len(updated_climbs), msg)

        except AuthenticationError as e:
            result.success = False
            result.errors.append(f"Erreur d'authentification: {e}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Erreur: {e}")

        return result

    def _climb_changed(self, existing: Climb, new: Climb) -> bool:
        """Vérifie si un climb a été modifié."""
        return (
            existing.holds_list != new.holds_list or
            existing.climbed_by != new.climbed_by or
            existing.total_likes != new.total_likes or
            existing.total_comments != new.total_comments
        )

    def needs_sync(self) -> bool:
        """Vérifie si une synchronisation est nécessaire."""
        status = self.get_sync_status()
        if not status["is_synced"]:
            return True

        last_sync = self.db.get_last_sync()
        if not last_sync:
            return True

        # Considérer une sync comme nécessaire après 24h
        hours_since_sync = (datetime.now() - last_sync).total_seconds() / 3600
        return hours_since_sync > 24
