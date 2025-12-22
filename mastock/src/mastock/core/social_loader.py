"""
Chargeur asynchrone pour les données sociales.

Les données sociales (sends, comments, likes) sont chargées en arrière-plan
pour ne jamais bloquer la navigation entre les blocs.
"""

from dataclasses import dataclass, field
from typing import Optional, Callable
from threading import Thread, Lock
from queue import Queue
import time

from mastock.api.client import StoktAPI, AuthenticationError
from mastock.api.models import Effort, Comment, Like


@dataclass
class SocialData:
    """Données sociales d'un climb."""
    climb_id: str
    sends: list[Effort] = field(default_factory=list)
    comments: list[Comment] = field(default_factory=list)
    likes: list[Like] = field(default_factory=list)
    loaded: bool = False
    error: Optional[str] = None


class SocialLoader:
    """
    Charge les données sociales en arrière-plan.

    Usage:
        loader = SocialLoader(api)
        loader.on_data_loaded = lambda data: update_ui(data)
        loader.load(climb_id)  # Non bloquant
    """

    def __init__(self, api: StoktAPI, cache_ttl: int = 300):
        """
        Args:
            api: Client API Stokt
            cache_ttl: Durée de vie du cache en secondes (défaut: 5 min)
        """
        self.api = api
        self.cache_ttl = cache_ttl

        # Cache: climb_id -> (SocialData, timestamp)
        self._cache: dict[str, tuple[SocialData, float]] = {}
        self._cache_lock = Lock()

        # Queue de requêtes
        self._queue: Queue[str] = Queue()
        self._current_climb_id: Optional[str] = None

        # Callback quand les données sont chargées
        self.on_data_loaded: Optional[Callable[[SocialData], None]] = None
        self.on_error: Optional[Callable[[str, str], None]] = None

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
        self._queue.put(None)  # Signal d'arrêt
        if self._worker:
            self._worker.join(timeout=2)

    def load(self, climb_id: str):
        """
        Demande le chargement des données sociales pour un climb.

        Non bloquant. Les données seront livrées via on_data_loaded.
        Si les données sont en cache et valides, elles sont retournées immédiatement.
        """
        self._current_climb_id = climb_id

        # Vérifier le cache
        cached = self._get_cached(climb_id)
        if cached:
            if self.on_data_loaded:
                self.on_data_loaded(cached)
            return

        # Ajouter à la queue
        self._queue.put(climb_id)

        # Démarrer le worker si nécessaire
        if not self._running:
            self.start()

    def _get_cached(self, climb_id: str) -> Optional[SocialData]:
        """Retourne les données du cache si valides."""
        with self._cache_lock:
            if climb_id in self._cache:
                data, timestamp = self._cache[climb_id]
                if time.time() - timestamp < self.cache_ttl:
                    return data
                else:
                    del self._cache[climb_id]
        return None

    def _set_cached(self, climb_id: str, data: SocialData):
        """Ajoute des données au cache."""
        with self._cache_lock:
            self._cache[climb_id] = (data, time.time())

    def invalidate(self, climb_id: str):
        """Invalide le cache pour un climb."""
        with self._cache_lock:
            if climb_id in self._cache:
                del self._cache[climb_id]

    def clear_cache(self):
        """Vide tout le cache."""
        with self._cache_lock:
            self._cache.clear()

    def _worker_loop(self):
        """Boucle principale du worker."""
        while self._running:
            try:
                climb_id = self._queue.get(timeout=1)
                if climb_id is None:
                    break

                # Si l'utilisateur a changé de climb, ignorer cette requête
                if climb_id != self._current_climb_id:
                    continue

                # Charger les données
                data = self._fetch_social_data(climb_id)

                # Si toujours le climb actuel, livrer les données
                if climb_id == self._current_climb_id:
                    self._set_cached(climb_id, data)
                    if self.on_data_loaded:
                        self.on_data_loaded(data)

            except Exception:
                # Timeout de la queue, continuer
                pass

    def _fetch_social_data(self, climb_id: str) -> SocialData:
        """Récupère les données sociales depuis l'API."""
        data = SocialData(climb_id=climb_id)

        try:
            # Charger les sends
            try:
                data.sends = self.api.get_climb_sends(climb_id, limit=20)
            except Exception as e:
                data.error = f"Sends: {e}"

            # Charger les commentaires
            try:
                data.comments = self.api.get_climb_comments(climb_id, limit=20)
            except Exception as e:
                if data.error:
                    data.error += f"; Comments: {e}"
                else:
                    data.error = f"Comments: {e}"

            # Charger les likes
            try:
                data.likes = self.api.get_climb_likes(climb_id)
            except Exception as e:
                if data.error:
                    data.error += f"; Likes: {e}"
                else:
                    data.error = f"Likes: {e}"

            data.loaded = True

        except AuthenticationError as e:
            data.error = f"Auth: {e}"
            if self.on_error:
                self.on_error(climb_id, str(e))

        return data


class SocialLoaderSync:
    """
    Version synchrone du loader pour les cas simples.

    Utilisé quand on veut charger les données de manière bloquante
    (ex: tests, scripts).
    """

    def __init__(self, api: StoktAPI):
        self.api = api

    def load(self, climb_id: str) -> SocialData:
        """Charge les données sociales de manière synchrone."""
        data = SocialData(climb_id=climb_id)

        try:
            data.sends = self.api.get_climb_sends(climb_id, limit=20)
        except Exception as e:
            data.error = f"Sends: {e}"

        try:
            data.comments = self.api.get_climb_comments(climb_id, limit=20)
        except Exception as e:
            err = f"Comments: {e}"
            data.error = f"{data.error}; {err}" if data.error else err

        try:
            data.likes = self.api.get_climb_likes(climb_id)
        except Exception as e:
            err = f"Likes: {e}"
            data.error = f"{data.error}; {err}" if data.error else err

        data.loaded = True
        return data
