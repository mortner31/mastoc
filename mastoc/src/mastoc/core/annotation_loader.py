"""
Chargeur asynchrone pour les annotations de prises.

ADR-008 : Hold Annotations (Annotations Crowd-Sourcées).

Les annotations (consensus + annotation utilisateur) sont chargées en arrière-plan
pour ne jamais bloquer l'interface.
"""

from typing import Optional, Callable
from threading import Thread, Lock
from queue import Queue
import time

from mastoc.api.railway_client import MastocAPI, AuthenticationError
from mastoc.api.models import AnnotationData, HoldConsensus


class AnnotationLoader:
    """
    Charge les annotations de prises en arrière-plan.

    Usage:
        loader = AnnotationLoader(api)
        loader.on_data_loaded = lambda data: update_ui(data)
        loader.load(hold_id)  # Non bloquant
    """

    def __init__(self, api: MastocAPI, cache_ttl: int = 600):
        """
        Args:
            api: Client API mastoc (Railway)
            cache_ttl: Durée de vie du cache en secondes (défaut: 10 min)
        """
        self.api = api
        self.cache_ttl = cache_ttl

        # Cache: hold_id -> (AnnotationData, timestamp)
        self._cache: dict[int, tuple[AnnotationData, float]] = {}
        self._cache_lock = Lock()

        # Queue de requêtes
        self._queue: Queue[int] = Queue()
        self._current_hold_id: Optional[int] = None

        # Callbacks
        self.on_data_loaded: Optional[Callable[[AnnotationData], None]] = None
        self.on_error: Optional[Callable[[int, str], None]] = None

        # Thread de chargement
        self._worker: Optional[Thread] = None
        self._running = False

    def start(self):
        """Démarre le worker de chargement."""
        if self._running:
            return
        self._running = True
        self._worker = Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def stop(self):
        """Arrête le worker."""
        self._running = False
        self._queue.put(-1)  # Signal d'arrêt
        if self._worker:
            self._worker.join(timeout=2)

    def load(self, hold_id: int):
        """
        Demande le chargement des annotations pour une prise.

        Non bloquant. Les données seront livrées via on_data_loaded.
        Si les données sont en cache et valides, elles sont retournées immédiatement.
        """
        self._current_hold_id = hold_id

        # Vérifier le cache
        cached = self._get_cached(hold_id)
        if cached:
            if self.on_data_loaded:
                self.on_data_loaded(cached)
            return

        # Ajouter à la queue
        self._queue.put(hold_id)

        # Démarrer le worker si nécessaire
        if not self._running:
            self.start()

    def load_batch(self, hold_ids: list[int]):
        """
        Demande le chargement des annotations pour plusieurs prises.

        Utilise l'endpoint batch pour optimiser les requêtes.
        """
        # Filtrer les prises déjà en cache
        missing = []
        for hold_id in hold_ids:
            if not self._get_cached(hold_id):
                missing.append(hold_id)

        if not missing:
            return

        # Charger en batch
        try:
            batch_data = self.api.get_hold_annotations_batch(missing)
            for hold_id, data in batch_data.items():
                self._set_cached(hold_id, data)
        except Exception as e:
            if self.on_error:
                self.on_error(0, f"Batch load error: {e}")

    def _get_cached(self, hold_id: int) -> Optional[AnnotationData]:
        """Retourne les données du cache si valides."""
        with self._cache_lock:
            if hold_id in self._cache:
                data, timestamp = self._cache[hold_id]
                if time.time() - timestamp < self.cache_ttl:
                    return data
                else:
                    del self._cache[hold_id]
        return None

    def _set_cached(self, hold_id: int, data: AnnotationData):
        """Ajoute des données au cache."""
        with self._cache_lock:
            self._cache[hold_id] = (data, time.time())

    def get_cached(self, hold_id: int) -> Optional[AnnotationData]:
        """
        Retourne les données du cache (sans vérifier l'expiration).

        Utile pour l'affichage UI quand on veut les données même périmées.
        """
        with self._cache_lock:
            if hold_id in self._cache:
                data, _ = self._cache[hold_id]
                return data
        return None

    def invalidate(self, hold_id: int):
        """Invalide le cache pour une prise."""
        with self._cache_lock:
            if hold_id in self._cache:
                del self._cache[hold_id]

    def clear_cache(self):
        """Vide tout le cache."""
        with self._cache_lock:
            self._cache.clear()

    def _worker_loop(self):
        """Boucle principale du worker."""
        while self._running:
            try:
                hold_id = self._queue.get(timeout=1)
                if hold_id == -1:
                    break

                # Si l'utilisateur a changé de prise, ignorer cette requête
                if hold_id != self._current_hold_id:
                    continue

                # Charger les données
                data = self._fetch_annotation_data(hold_id)

                # Si toujours la prise actuelle, livrer les données
                if hold_id == self._current_hold_id:
                    self._set_cached(hold_id, data)
                    if self.on_data_loaded:
                        self.on_data_loaded(data)

            except Exception:
                # Timeout de la queue, continuer
                pass

    def _fetch_annotation_data(self, hold_id: int) -> AnnotationData:
        """Récupère les annotations depuis l'API."""
        try:
            return self.api.get_hold_annotations(hold_id)
        except AuthenticationError as e:
            error_data = AnnotationData(
                hold_id=hold_id,
                consensus=HoldConsensus(hold_id=hold_id),
                loaded=False,
                error=f"Auth: {e}",
            )
            if self.on_error:
                self.on_error(hold_id, str(e))
            return error_data
        except Exception as e:
            return AnnotationData(
                hold_id=hold_id,
                consensus=HoldConsensus(hold_id=hold_id),
                loaded=False,
                error=str(e),
            )


class AnnotationLoaderSync:
    """
    Version synchrone du loader pour les cas simples.

    Utilisé quand on veut charger les données de manière bloquante
    (ex: tests, scripts).
    """

    def __init__(self, api: MastocAPI):
        self.api = api

    def load(self, hold_id: int) -> AnnotationData:
        """Charge les annotations de manière synchrone."""
        try:
            return self.api.get_hold_annotations(hold_id)
        except Exception as e:
            return AnnotationData(
                hold_id=hold_id,
                consensus=HoldConsensus(hold_id=hold_id),
                loaded=False,
                error=str(e),
            )

    def load_batch(self, hold_ids: list[int]) -> dict[int, AnnotationData]:
        """Charge les annotations pour plusieurs prises."""
        try:
            return self.api.get_hold_annotations_batch(hold_ids)
        except Exception as e:
            return {
                hold_id: AnnotationData(
                    hold_id=hold_id,
                    consensus=HoldConsensus(hold_id=hold_id),
                    loaded=False,
                    error=str(e),
                )
                for hold_id in hold_ids
            }
