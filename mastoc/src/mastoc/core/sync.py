"""
Synchronisation entre l'API Stokt et la base de données locale.

Gère le téléchargement initial et les mises à jour incrémentales.
"""

from datetime import datetime
from typing import Callable, Optional

from mastoc.api.client import StoktAPI, AuthenticationError, MONTOBOARD_GYM_ID
from mastoc.db import Database, ClimbRepository, HoldRepository
from mastoc.api.models import Climb


class SyncResult:
    """Résultat d'une synchronisation."""

    def __init__(self):
        self.climbs_added = 0
        self.climbs_updated = 0
        self.holds_added = 0
        self.errors: list[str] = []
        self.success = True
        # Informations sur le mode de synchronisation
        self.mode: str = "full"  # "full" ou "incremental"
        self.climbs_downloaded = 0  # Nombre de climbs téléchargés depuis l'API
        self.total_climbs_local = 0  # Total de climbs en base après sync

    def __repr__(self):
        return (
            f"SyncResult(mode={self.mode}, added={self.climbs_added}, updated={self.climbs_updated}, "
            f"holds={self.holds_added}, downloaded={self.climbs_downloaded}, success={self.success})"
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
            result.climbs_downloaded = len(climbs)

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

            # 6. Statistiques finales
            result.total_climbs_local = self.db.get_climb_count()

            if callback:
                callback(len(climbs), len(climbs), "Synchronisation terminée!")

        except AuthenticationError as e:
            result.success = False
            result.errors.append(f"Erreur d'authentification: {e}")
        except Exception as e:
            result.success = False
            result.errors.append(f"Erreur: {e}")

        return result

    def _calculate_max_age(self, last_sync: datetime, min_days: int = 7) -> int:
        """
        Calcule max_age basé sur la dernière synchronisation.

        Args:
            last_sync: Date de dernière synchronisation
            min_days: Nombre minimum de jours (marge de sécurité)

        Returns:
            Nombre de jours à demander à l'API
        """
        days_since = (datetime.now() - last_sync).days + 1
        return max(days_since, min_days)

    def sync_incremental(
        self,
        callback: Optional[ProgressCallback] = None
    ) -> SyncResult:
        """
        Synchronisation incrémentale (nouveaux climbs seulement).

        Utilise le paramètre max_age de l'API Stokt pour ne télécharger
        que les climbs créés depuis la dernière synchronisation.

        Returns:
            SyncResult avec les statistiques
        """
        result = SyncResult()
        result.mode = "incremental"
        last_sync = self.db.get_last_sync()

        if not last_sync:
            # Pas de sync précédente, faire une sync complète
            return self.sync_full(callback=callback)

        # Calculer max_age dynamiquement
        max_age = self._calculate_max_age(last_sync)

        try:
            if callback:
                callback(0, 0, f"Sync incrémentale (derniers {max_age} jours)...")

            # Récupérer les climbs existants
            existing_climbs = self.climb_repo.get_all_climbs()
            existing_ids = {c.id for c in existing_climbs}

            # Récupérer uniquement les climbs récents depuis l'API
            def climb_progress(current, total):
                if callback:
                    callback(current, total, f"Téléchargement: {current}/{total}")

            all_climbs = self.api.get_all_gym_climbs(self.gym_id, max_age=max_age, callback=climb_progress)
            result.climbs_downloaded = len(all_climbs)

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

            # Statistiques finales
            result.total_climbs_local = self.db.get_climb_count()

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

    # =========================================================================
    # Refresh social counts (TODO 18)
    # =========================================================================

    def refresh_social_counts(self, climb_id: str) -> dict:
        """
        Rafraîchit les compteurs sociaux d'un climb depuis Stokt.

        Args:
            climb_id: ID du climb (Stokt UUID)

        Returns:
            Dict avec les nouveaux compteurs {climbed_by, total_likes, total_comments}
        """
        stats = self.api.get_climb_social_stats(climb_id)
        self.climb_repo.update_social_counts(
            climb_id,
            climbed_by=stats["climbed_by"],
            total_likes=stats["total_likes"],
            total_comments=stats["total_comments"]
        )
        return stats

    def refresh_all_social_counts(
        self,
        callback: Optional[ProgressCallback] = None,
        delay_seconds: float = 1.0
    ) -> dict:
        """
        Rafraîchit les compteurs sociaux de tous les climbs.

        Args:
            callback: Fonction (current, total, message) pour la progression
            delay_seconds: Délai entre chaque requête (throttling)

        Returns:
            Dict avec {total, updated, errors}
        """
        import time

        climbs = self.climb_repo.get_all_climbs()
        total = len(climbs)
        updated = 0
        errors = []

        for i, climb in enumerate(climbs):
            try:
                if callback:
                    callback(i, total, f"Refresh {climb.name[:30]}...")

                self.refresh_social_counts(climb.id)
                updated += 1

                # Throttling pour éviter le rate limiting
                if i < total - 1:
                    time.sleep(delay_seconds)

            except Exception as e:
                errors.append(f"{climb.id}: {e}")

        if callback:
            callback(total, total, f"Terminé: {updated}/{total} mis à jour")

        return {"total": total, "updated": updated, "errors": errors}


class RailwaySyncManager:
    """Gère la synchronisation Railway ↔ BD locale (ADR-006)."""

    # Face ID par défaut pour Montoboard
    DEFAULT_FACE_ID = "61b42d14-c629-434a-8827-801512151a18"

    def __init__(self, api, db: Database):
        """
        Args:
            api: MastocAPI (railway_client)
            db: Database SQLite locale
        """
        from mastoc.api.railway_client import MastocAPI
        self.api: MastocAPI = api
        self.db = db
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
            "is_synced": climb_count > 0,
        }

    def sync_full(
        self,
        face_id: Optional[str] = None,
        callback: Optional[ProgressCallback] = None,
        clear_existing: bool = False
    ) -> SyncResult:
        """
        Synchronisation complète depuis Railway.

        Ordre : climbs d'abord, puis prises (pour extraire les face_id).

        Args:
            face_id: ID de la face à synchroniser (optionnel)
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

            # 1. Récupérer les climbs d'ABORD (pour extraire les face_id)
            if callback:
                callback(0, 0, "Récupération des climbs...")

            def climb_progress(current, total):
                if callback:
                    callback(current, total, f"Téléchargement climbs: {current}/{total}")

            all_climbs = self.api.get_all_climbs(face_id=face_id, callback=climb_progress)
            result.climbs_downloaded = len(all_climbs)

            if callback:
                callback(0, len(all_climbs), f"Sauvegarde de {len(all_climbs)} climbs...")

            # 2. Sauvegarder les climbs
            for i, climb in enumerate(all_climbs):
                self.climb_repo.save_climb(climb)
                result.climbs_added += 1
                if callback and i % 50 == 0:
                    callback(i, len(all_climbs), f"Sauvegarde climbs: {i}/{len(all_climbs)}")

            # 3. Extraire les face_id uniques des climbs
            if face_id:
                face_ids = {face_id}
            else:
                face_ids = {c.face_id for c in all_climbs if c.face_id}
                # Fallback sur le face_id par défaut si aucun trouvé
                if not face_ids:
                    face_ids = {self.DEFAULT_FACE_ID}

            # 4. Récupérer les prises pour chaque face
            if callback:
                callback(0, len(face_ids), f"Récupération des prises ({len(face_ids)} face(s))...")

            for i, fid in enumerate(face_ids):
                if callback:
                    callback(i, len(face_ids), f"Prises face {fid[:8]}...")
                try:
                    face = self.api.get_face_setup(fid)
                    # Sauvegarder la face complète (avec picture_name) et ses holds
                    self.hold_repo.save_face(face)
                    result.holds_added += len(face.holds)
                    if callback:
                        callback(i + 1, len(face_ids), f"Face {fid[:8]}: {len(face.holds)} prises")
                except Exception as e:
                    result.errors.append(f"Erreur prises face {fid}: {e}")

            # 5. Mettre à jour la date de sync
            self.db.set_last_sync()

            # 6. Statistiques finales
            result.total_climbs_local = self.db.get_climb_count()

            if callback:
                callback(len(face_ids), len(face_ids),
                        f"Sync terminée: {result.climbs_added} climbs, {result.holds_added} prises")

        except Exception as e:
            result.success = False
            result.errors.append(f"Erreur: {e}")

        return result

    def _calculate_since_date(self, last_sync: datetime, margin_days: int = 1) -> datetime:
        """
        Calcule la date depuis laquelle récupérer les climbs.

        Args:
            last_sync: Date de dernière synchronisation
            margin_days: Marge de sécurité en jours

        Returns:
            Date à utiliser pour since_created_at
        """
        from datetime import timedelta
        return last_sync - timedelta(days=margin_days)

    def sync_incremental(
        self,
        face_id: Optional[str] = None,
        callback: Optional[ProgressCallback] = None
    ) -> SyncResult:
        """
        Synchronisation incrémentale depuis Railway.

        Utilise since_created_at pour ne télécharger que les climbs
        créés depuis la dernière synchronisation.

        Args:
            face_id: ID de la face à synchroniser (optionnel)
            callback: Fonction (current, total, message) pour la progression

        Returns:
            SyncResult avec les statistiques
        """
        result = SyncResult()
        result.mode = "incremental"
        last_sync = self.db.get_last_sync()

        if not last_sync:
            # Pas de sync précédente, faire une sync complète
            return self.sync_full(face_id=face_id, callback=callback)

        # Calculer la date depuis laquelle récupérer (avec marge de sécurité)
        since_date = self._calculate_since_date(last_sync)

        try:
            if callback:
                callback(0, 0, f"Sync incrémentale depuis {since_date.strftime('%Y-%m-%d')}...")

            # Récupérer les climbs existants
            existing_climbs = self.climb_repo.get_all_climbs()
            existing_ids = {c.id for c in existing_climbs}

            # Récupérer uniquement les climbs récents depuis l'API
            def climb_progress(current, total):
                if callback:
                    callback(current, total, f"Téléchargement: {current}/{total}")

            new_climbs = self.api.get_all_climbs(
                face_id=face_id,
                since_created_at=since_date,
                callback=climb_progress
            )
            result.climbs_downloaded = len(new_climbs)

            if callback:
                callback(0, len(new_climbs), f"Analyse de {len(new_climbs)} climbs récents...")

            # Identifier les nouveaux et les mis à jour
            added = 0
            updated = 0

            for climb in new_climbs:
                if climb.id not in existing_ids:
                    self.climb_repo.save_climb(climb)
                    added += 1
                else:
                    # Mettre à jour si existant
                    self.climb_repo.save_climb(climb)
                    updated += 1

            result.climbs_added = added
            result.climbs_updated = updated

            # Mettre à jour la date de sync
            self.db.set_last_sync()

            # Statistiques finales
            result.total_climbs_local = self.db.get_climb_count()

            if callback:
                callback(len(new_climbs), len(new_climbs),
                        f"Sync terminée: {added} ajoutés, {updated} mis à jour")

        except Exception as e:
            result.success = False
            result.errors.append(f"Erreur: {e}")

        return result

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
