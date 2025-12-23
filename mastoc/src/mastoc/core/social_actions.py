"""
Service pour les actions sociales (like, bookmark, comment).

Gère les appels API et l'état local pour une expérience réactive.
"""

from typing import Optional, Callable
from dataclasses import dataclass, field
from threading import Thread

from mastoc.api.client import StoktAPI, AuthenticationError
from mastoc.api.models import Comment


@dataclass
class UserClimbState:
    """État utilisateur pour un climb."""
    liked: bool = False
    bookmarked: bool = False


class SocialActionsService:
    """
    Service pour les actions sociales.

    Gère :
    - Like/unlike
    - Bookmark/unbookmark
    - Post/delete comment

    Les actions sont exécutées en arrière-plan avec callbacks.
    """

    def __init__(self, api: StoktAPI):
        self.api = api

        # Cache de l'état utilisateur: climb_id -> UserClimbState
        self._states: dict[str, UserClimbState] = {}

        # Callbacks
        self.on_like_changed: Optional[Callable[[str, bool], None]] = None
        self.on_bookmark_changed: Optional[Callable[[str, bool], None]] = None
        self.on_comment_posted: Optional[Callable[[str, Comment], None]] = None
        self.on_error: Optional[Callable[[str, str], None]] = None

    def get_state(self, climb_id: str) -> UserClimbState:
        """Retourne l'état utilisateur pour un climb."""
        if climb_id not in self._states:
            self._states[climb_id] = UserClimbState()
        return self._states[climb_id]

    def set_initial_state(self, climb_id: str, liked: bool, bookmarked: bool):
        """Initialise l'état depuis les données de l'API."""
        self._states[climb_id] = UserClimbState(liked=liked, bookmarked=bookmarked)

    def toggle_like(self, climb_id: str):
        """Toggle le like (async)."""
        state = self.get_state(climb_id)
        new_value = not state.liked

        def do_like():
            try:
                if new_value:
                    self.api.like_climb(climb_id)
                else:
                    self.api.unlike_climb(climb_id)

                state.liked = new_value
                if self.on_like_changed:
                    self.on_like_changed(climb_id, new_value)

            except AuthenticationError as e:
                if self.on_error:
                    self.on_error(climb_id, f"Auth: {e}")
            except Exception as e:
                if self.on_error:
                    self.on_error(climb_id, f"Like error: {e}")

        Thread(target=do_like, daemon=True).start()

    def toggle_bookmark(self, climb_id: str):
        """Toggle le bookmark (async)."""
        state = self.get_state(climb_id)
        new_value = not state.bookmarked

        def do_bookmark():
            try:
                self.api.bookmark_climb(climb_id, add=new_value)
                state.bookmarked = new_value
                if self.on_bookmark_changed:
                    self.on_bookmark_changed(climb_id, new_value)

            except AuthenticationError as e:
                if self.on_error:
                    self.on_error(climb_id, f"Auth: {e}")
            except Exception as e:
                if self.on_error:
                    self.on_error(climb_id, f"Bookmark error: {e}")

        Thread(target=do_bookmark, daemon=True).start()

    def post_comment(self, climb_id: str, text: str, replied_to: Optional[str] = None):
        """Poste un commentaire (async)."""
        def do_post():
            try:
                comment = self.api.post_comment(climb_id, text, replied_to)
                if self.on_comment_posted:
                    self.on_comment_posted(climb_id, comment)

            except AuthenticationError as e:
                if self.on_error:
                    self.on_error(climb_id, f"Auth: {e}")
            except Exception as e:
                if self.on_error:
                    self.on_error(climb_id, f"Comment error: {e}")

        Thread(target=do_post, daemon=True).start()

    def like_sync(self, climb_id: str, like: bool) -> bool:
        """Like/unlike de manière synchrone. Retourne True si succès."""
        try:
            if like:
                self.api.like_climb(climb_id)
            else:
                self.api.unlike_climb(climb_id)
            state = self.get_state(climb_id)
            state.liked = like
            return True
        except Exception:
            return False

    def bookmark_sync(self, climb_id: str, bookmark: bool) -> bool:
        """Bookmark de manière synchrone. Retourne True si succès."""
        try:
            self.api.bookmark_climb(climb_id, add=bookmark)
            state = self.get_state(climb_id)
            state.bookmarked = bookmark
            return True
        except Exception:
            return False
