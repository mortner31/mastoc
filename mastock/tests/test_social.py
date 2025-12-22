"""
Tests pour les modules sociaux (TODO 07).

Tests couverts :
- SocialLoader : chargement async et cache
- SocialActionsService : actions like/bookmark
- Modèles : UserRef, Effort, Comment, Like
"""

import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from threading import Event

from mastock.api.models import UserRef, Effort, Comment, Like
from mastock.core.social_loader import SocialLoader, SocialLoaderSync, SocialData
from mastock.core.social_actions import SocialActionsService, UserClimbState


# =============================================================================
# Tests des modèles
# =============================================================================

class TestUserRef:
    """Tests pour UserRef."""

    def test_from_api_basic(self):
        data = {"id": "user123", "fullName": "John Doe", "avatar": "http://example.com/avatar.jpg"}
        user = UserRef.from_api(data)
        assert user.id == "user123"
        assert user.full_name == "John Doe"
        assert user.avatar == "http://example.com/avatar.jpg"

    def test_from_api_snake_case(self):
        data = {"id": "user123", "full_name": "Jane Doe"}
        user = UserRef.from_api(data)
        assert user.full_name == "Jane Doe"

    def test_from_api_no_avatar(self):
        data = {"id": "user123", "fullName": "John"}
        user = UserRef.from_api(data)
        assert user.avatar is None


class TestEffort:
    """Tests pour Effort."""

    def test_from_api_basic(self):
        data = {
            "id": "effort123",
            "climbId": "climb456",
            "effortBy": {"id": "user1", "fullName": "Alice"},
            "effortDate": "2025-12-22",
            "isFlash": True,
            "attemptsNumber": 1,
            "gradeFeel": -1
        }
        effort = Effort.from_api(data)
        assert effort.id == "effort123"
        assert effort.climb_id == "climb456"
        assert effort.user.full_name == "Alice"
        assert effort.is_flash is True
        assert effort.attempts == 1
        assert effort.grade_feel == -1

    def test_from_api_snake_case(self):
        # Test avec les anciens noms de champs (fallback)
        data = {
            "id": "e1",
            "climb_id": "c1",
            "user": {"id": "u1", "fullName": "Bob"},
            "dateCreated": "2025-01-01",
            "is_flash": False,
            "grade_feel": 1
        }
        effort = Effort.from_api(data)
        assert effort.climb_id == "c1"
        assert effort.date == "2025-01-01"
        assert effort.grade_feel == 1


class TestComment:
    """Tests pour Comment."""

    def test_from_api_basic(self):
        data = {
            "id": "comment123",
            "climbId": "climb456",
            "user": {"id": "user1", "fullName": "Charlie"},
            "text": "Great climb!",
            "date": "2025-12-22",
            "repliedToId": None
        }
        comment = Comment.from_api(data)
        assert comment.id == "comment123"
        assert comment.text == "Great climb!"
        assert comment.user.full_name == "Charlie"
        assert comment.replied_to_id is None

    def test_from_api_with_reply(self):
        data = {
            "id": "c2",
            "climbId": "climb1",
            "user": {"id": "u1", "fullName": "Dave"},
            "text": "I agree!",
            "date": "2025-12-22",
            "replied_to_id": "c1"
        }
        comment = Comment.from_api(data)
        assert comment.replied_to_id == "c1"


class TestLike:
    """Tests pour Like."""

    def test_from_api_with_user_object(self):
        data = {
            "user": {"id": "user1", "fullName": "Eve"},
            "date": "2025-12-22"
        }
        like = Like.from_api(data)
        assert like.user.full_name == "Eve"
        assert like.date == "2025-12-22"

    def test_from_api_flat_structure(self):
        data = {"id": "user2", "fullName": "Frank", "dateCreated": "2025-12-21"}
        like = Like.from_api(data)
        assert like.user.full_name == "Frank"
        assert like.date == "2025-12-21"


# =============================================================================
# Tests SocialData
# =============================================================================

class TestSocialData:
    """Tests pour SocialData."""

    def test_init_empty(self):
        data = SocialData(climb_id="test123")
        assert data.climb_id == "test123"
        assert data.sends == []
        assert data.comments == []
        assert data.likes == []
        assert data.loaded is False
        assert data.error is None

    def test_with_data(self):
        user = UserRef(id="u1", full_name="Test")
        effort = Effort(id="e1", climb_id="c1", user=user, date="2025-01-01")

        data = SocialData(
            climb_id="c1",
            sends=[effort],
            loaded=True
        )
        assert len(data.sends) == 1
        assert data.loaded is True


# =============================================================================
# Tests SocialLoader
# =============================================================================

class TestSocialLoader:
    """Tests pour SocialLoader."""

    @pytest.fixture
    def mock_api(self):
        api = Mock()
        api.get_climb_sends.return_value = []
        api.get_climb_comments.return_value = []
        api.get_climb_likes.return_value = []
        return api

    def test_init(self, mock_api):
        loader = SocialLoader(mock_api, cache_ttl=60)
        assert loader.api == mock_api
        assert loader.cache_ttl == 60
        assert loader.on_data_loaded is None

    def test_cache_miss(self, mock_api):
        loader = SocialLoader(mock_api)
        cached = loader._get_cached("climb123")
        assert cached is None

    def test_cache_hit(self, mock_api):
        loader = SocialLoader(mock_api, cache_ttl=300)
        data = SocialData(climb_id="climb123", loaded=True)
        loader._set_cached("climb123", data)

        cached = loader._get_cached("climb123")
        assert cached is not None
        assert cached.climb_id == "climb123"

    def test_cache_expired(self, mock_api):
        loader = SocialLoader(mock_api, cache_ttl=0)  # TTL 0 = expire immédiatement
        data = SocialData(climb_id="climb123", loaded=True)
        loader._set_cached("climb123", data)

        time.sleep(0.01)  # Attendre un peu
        cached = loader._get_cached("climb123")
        assert cached is None

    def test_invalidate(self, mock_api):
        loader = SocialLoader(mock_api)
        data = SocialData(climb_id="climb123", loaded=True)
        loader._set_cached("climb123", data)

        loader.invalidate("climb123")
        assert loader._get_cached("climb123") is None

    def test_clear_cache(self, mock_api):
        loader = SocialLoader(mock_api)
        loader._set_cached("c1", SocialData(climb_id="c1"))
        loader._set_cached("c2", SocialData(climb_id="c2"))

        loader.clear_cache()
        assert loader._get_cached("c1") is None
        assert loader._get_cached("c2") is None

    def test_fetch_social_data(self, mock_api):
        user = UserRef(id="u1", full_name="Test")
        mock_api.get_climb_sends.return_value = [
            Effort(id="e1", climb_id="c1", user=user, date="2025-01-01")
        ]
        mock_api.get_climb_comments.return_value = [
            Comment(id="cm1", climb_id="c1", user=user, text="Hello", date="2025-01-01")
        ]
        mock_api.get_climb_likes.return_value = [
            Like(user=user, date="2025-01-01")
        ]

        loader = SocialLoader(mock_api)
        data = loader._fetch_social_data("c1")

        assert data.loaded is True
        assert len(data.sends) == 1
        assert len(data.comments) == 1
        assert len(data.likes) == 1

    def test_fetch_social_data_with_errors(self, mock_api):
        mock_api.get_climb_sends.side_effect = Exception("Network error")
        mock_api.get_climb_comments.return_value = []
        mock_api.get_climb_likes.return_value = []

        loader = SocialLoader(mock_api)
        data = loader._fetch_social_data("c1")

        assert data.loaded is True  # Toujours True car on continue malgré les erreurs
        assert "Sends" in data.error

    def test_load_with_cache(self, mock_api):
        """Test que load() utilise le cache."""
        loader = SocialLoader(mock_api)
        cached_data = SocialData(climb_id="c1", loaded=True)
        loader._set_cached("c1", cached_data)

        callback_called = []
        loader.on_data_loaded = lambda d: callback_called.append(d)

        loader.load("c1")

        # Le callback doit être appelé immédiatement avec les données cachées
        assert len(callback_called) == 1
        assert callback_called[0].climb_id == "c1"
        # L'API ne doit pas être appelée
        mock_api.get_climb_sends.assert_not_called()


class TestSocialLoaderSync:
    """Tests pour SocialLoaderSync."""

    def test_load_sync(self):
        api = Mock()
        user = UserRef(id="u1", full_name="Test")
        api.get_climb_sends.return_value = [
            Effort(id="e1", climb_id="c1", user=user, date="2025-01-01")
        ]
        api.get_climb_comments.return_value = []
        api.get_climb_likes.return_value = []

        loader = SocialLoaderSync(api)
        data = loader.load("c1")

        assert data.climb_id == "c1"
        assert data.loaded is True
        assert len(data.sends) == 1


# =============================================================================
# Tests SocialActionsService
# =============================================================================

class TestUserClimbState:
    """Tests pour UserClimbState."""

    def test_default_values(self):
        state = UserClimbState()
        assert state.liked is False
        assert state.bookmarked is False

    def test_custom_values(self):
        state = UserClimbState(liked=True, bookmarked=True)
        assert state.liked is True
        assert state.bookmarked is True


class TestSocialActionsService:
    """Tests pour SocialActionsService."""

    @pytest.fixture
    def mock_api(self):
        api = Mock()
        api.like_climb.return_value = True
        api.unlike_climb.return_value = True
        api.bookmark_climb.return_value = True
        return api

    def test_get_state_new(self, mock_api):
        service = SocialActionsService(mock_api)
        state = service.get_state("climb123")
        assert state.liked is False
        assert state.bookmarked is False

    def test_get_state_existing(self, mock_api):
        service = SocialActionsService(mock_api)
        service.set_initial_state("climb123", liked=True, bookmarked=False)

        state = service.get_state("climb123")
        assert state.liked is True
        assert state.bookmarked is False

    def test_set_initial_state(self, mock_api):
        service = SocialActionsService(mock_api)
        service.set_initial_state("c1", liked=True, bookmarked=True)

        state = service.get_state("c1")
        assert state.liked is True
        assert state.bookmarked is True

    def test_like_sync(self, mock_api):
        service = SocialActionsService(mock_api)
        result = service.like_sync("c1", True)

        assert result is True
        mock_api.like_climb.assert_called_once_with("c1")
        assert service.get_state("c1").liked is True

    def test_unlike_sync(self, mock_api):
        service = SocialActionsService(mock_api)
        service.set_initial_state("c1", liked=True, bookmarked=False)

        result = service.like_sync("c1", False)

        assert result is True
        mock_api.unlike_climb.assert_called_once_with("c1")
        assert service.get_state("c1").liked is False

    def test_bookmark_sync(self, mock_api):
        service = SocialActionsService(mock_api)
        result = service.bookmark_sync("c1", True)

        assert result is True
        mock_api.bookmark_climb.assert_called_once_with("c1", add=True)
        assert service.get_state("c1").bookmarked is True

    def test_unbookmark_sync(self, mock_api):
        service = SocialActionsService(mock_api)
        service.set_initial_state("c1", liked=False, bookmarked=True)

        result = service.bookmark_sync("c1", False)

        assert result is True
        mock_api.bookmark_climb.assert_called_once_with("c1", add=False)
        assert service.get_state("c1").bookmarked is False

    def test_like_sync_error(self, mock_api):
        mock_api.like_climb.side_effect = Exception("Network error")
        service = SocialActionsService(mock_api)

        result = service.like_sync("c1", True)

        assert result is False

    def test_toggle_like_async(self, mock_api):
        """Test toggle_like en mode async."""
        service = SocialActionsService(mock_api)

        callback_results = []
        service.on_like_changed = lambda cid, val: callback_results.append((cid, val))

        # Toggle like (False -> True)
        service.toggle_like("c1")

        # Attendre que le thread se termine
        time.sleep(0.1)

        assert len(callback_results) == 1
        assert callback_results[0] == ("c1", True)
        assert service.get_state("c1").liked is True

    def test_toggle_bookmark_async(self, mock_api):
        """Test toggle_bookmark en mode async."""
        service = SocialActionsService(mock_api)

        callback_results = []
        service.on_bookmark_changed = lambda cid, val: callback_results.append((cid, val))

        service.toggle_bookmark("c1")
        time.sleep(0.1)

        assert len(callback_results) == 1
        assert callback_results[0] == ("c1", True)
        assert service.get_state("c1").bookmarked is True
