"""
Tests pour le gestionnaire d'assets (core/assets.py).
"""

import hashlib
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from mastoc.core.assets import AssetManager, get_asset_manager, STOKT_MEDIA_URL


class TestAssetManager:
    """Tests pour AssetManager."""

    def test_init_default_cache_dir(self, tmp_path, monkeypatch):
        """Le cache par défaut est ~/.mastoc/images/."""
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager = AssetManager()

        expected = tmp_path / ".mastoc" / "images"
        assert manager.cache_dir == expected
        assert expected.exists()

    def test_init_custom_cache_dir(self, tmp_path):
        """On peut spécifier un répertoire de cache personnalisé."""
        cache_dir = tmp_path / "custom_cache"

        manager = AssetManager(cache_dir=cache_dir)

        assert manager.cache_dir == cache_dir
        assert cache_dir.exists()

    def test_session_lazy_creation(self, tmp_path):
        """La session HTTP est créée paresseusement."""
        manager = AssetManager(cache_dir=tmp_path)

        # Pas de session au départ
        assert manager._session is None

        # Accéder à la session la crée
        session = manager.session
        assert session is not None
        assert manager._session is session

        # Réutilisation de la même session
        assert manager.session is session


class TestAssetManagerCachePath:
    """Tests pour _get_cache_path."""

    def test_cache_path_uses_hash(self, tmp_path):
        """Le chemin de cache utilise un hash MD5 du chemin distant."""
        manager = AssetManager(cache_dir=tmp_path)
        remote_path = "CACHE/images/walls/123/face.jpg"

        cache_path = manager._get_cache_path(remote_path)

        expected_hash = hashlib.md5(remote_path.encode()).hexdigest()
        assert cache_path.name == f"{expected_hash}.jpg"
        assert cache_path.parent == tmp_path

    def test_cache_path_preserves_extension(self, tmp_path):
        """L'extension du fichier est préservée."""
        manager = AssetManager(cache_dir=tmp_path)

        jpg_path = manager._get_cache_path("path/to/image.jpg")
        png_path = manager._get_cache_path("path/to/image.png")

        assert jpg_path.suffix == ".jpg"
        assert png_path.suffix == ".png"

    def test_cache_path_default_extension(self, tmp_path):
        """Extension par défaut .jpg si pas d'extension."""
        manager = AssetManager(cache_dir=tmp_path)

        cache_path = manager._get_cache_path("path/without/extension")

        assert cache_path.suffix == ".jpg"


class TestAssetManagerRemoteUrl:
    """Tests pour _get_remote_url."""

    def test_remote_url_format(self, tmp_path):
        """L'URL distante est construite correctement."""
        manager = AssetManager(cache_dir=tmp_path)
        remote_path = "CACHE/images/walls/123/face.jpg"

        url = manager._get_remote_url(remote_path)

        assert url == f"{STOKT_MEDIA_URL}/{remote_path}"


class TestAssetManagerGetFaceImage:
    """Tests pour get_face_image."""

    def test_returns_none_for_empty_path(self, tmp_path):
        """Retourne None si le chemin est vide."""
        manager = AssetManager(cache_dir=tmp_path)

        result = manager.get_face_image("")
        assert result is None

        result = manager.get_face_image(None)
        assert result is None

    def test_returns_cached_image(self, tmp_path):
        """Retourne l'image depuis le cache si disponible."""
        manager = AssetManager(cache_dir=tmp_path)
        remote_path = "CACHE/images/face.jpg"

        # Créer le fichier en cache
        cache_path = manager._get_cache_path(remote_path)
        cache_path.write_bytes(b"fake image data")

        # Mock la session pour vérifier qu'elle n'est pas appelée
        mock_session = Mock()
        manager._session = mock_session

        result = manager.get_face_image(remote_path)

        mock_session.get.assert_not_called()
        assert result == cache_path

    def test_downloads_if_not_cached(self, tmp_path):
        """Télécharge l'image si pas en cache."""
        manager = AssetManager(cache_dir=tmp_path)
        remote_path = "CACHE/images/face.jpg"
        image_data = b"PNG image data here"

        # Mock de la session HTTP
        mock_response = Mock()
        mock_response.content = image_data
        mock_response.raise_for_status = Mock()

        mock_session = Mock()
        mock_session.get.return_value = mock_response
        manager._session = mock_session

        result = manager.get_face_image(remote_path)

        # Vérifie que la requête a été faite
        mock_session.get.assert_called_once()
        call_args = mock_session.get.call_args
        assert remote_path in call_args[0][0]

        # Vérifie que le fichier a été sauvegardé
        assert result.exists()
        assert result.read_bytes() == image_data

    def test_force_download_ignores_cache(self, tmp_path):
        """force_download=True ignore le cache."""
        manager = AssetManager(cache_dir=tmp_path)
        remote_path = "CACHE/images/face.jpg"

        # Créer un fichier en cache
        cache_path = manager._get_cache_path(remote_path)
        cache_path.write_bytes(b"old cached data")

        new_data = b"new downloaded data"
        mock_response = Mock()
        mock_response.content = new_data
        mock_response.raise_for_status = Mock()

        mock_session = Mock()
        mock_session.get.return_value = mock_response
        manager._session = mock_session

        result = manager.get_face_image(remote_path, force_download=True)

        # La requête HTTP a été faite malgré le cache
        mock_session.get.assert_called_once()
        # Le fichier a été mis à jour
        assert result.read_bytes() == new_data

    def test_returns_none_on_http_error(self, tmp_path):
        """Retourne None si le téléchargement échoue."""
        import requests

        manager = AssetManager(cache_dir=tmp_path)
        remote_path = "CACHE/images/nonexistent.jpg"

        mock_session = Mock()
        mock_session.get.side_effect = requests.RequestException("Network error")
        manager._session = mock_session

        result = manager.get_face_image(remote_path)

        assert result is None


class TestAssetManagerUserAvatar:
    """Tests pour get_user_avatar."""

    def test_get_user_avatar_uses_same_logic(self, tmp_path):
        """get_user_avatar utilise la même logique que get_face_image."""
        manager = AssetManager(cache_dir=tmp_path)
        avatar_path = "avatars/user123.jpg"

        # Créer le fichier en cache
        cache_path = manager._get_cache_path(avatar_path)
        cache_path.write_bytes(b"avatar data")

        result = manager.get_user_avatar(avatar_path)

        assert result == cache_path


class TestAssetManagerCacheManagement:
    """Tests pour la gestion du cache."""

    def test_is_cached_true(self, tmp_path):
        """is_cached retourne True si le fichier existe."""
        manager = AssetManager(cache_dir=tmp_path)
        remote_path = "path/to/image.jpg"

        # Créer le fichier
        cache_path = manager._get_cache_path(remote_path)
        cache_path.write_bytes(b"data")

        assert manager.is_cached(remote_path) is True

    def test_is_cached_false(self, tmp_path):
        """is_cached retourne False si le fichier n'existe pas."""
        manager = AssetManager(cache_dir=tmp_path)

        assert manager.is_cached("nonexistent/path.jpg") is False
        assert manager.is_cached("") is False

    def test_get_cache_size(self, tmp_path):
        """get_cache_size retourne la taille totale du cache."""
        manager = AssetManager(cache_dir=tmp_path)

        # Créer quelques fichiers
        (tmp_path / "file1.jpg").write_bytes(b"x" * 100)
        (tmp_path / "file2.jpg").write_bytes(b"y" * 200)

        size = manager.get_cache_size()

        assert size == 300

    def test_get_cache_size_empty(self, tmp_path):
        """get_cache_size retourne 0 pour un cache vide."""
        manager = AssetManager(cache_dir=tmp_path)

        assert manager.get_cache_size() == 0

    def test_clear_cache(self, tmp_path):
        """clear_cache supprime tous les fichiers du cache."""
        manager = AssetManager(cache_dir=tmp_path)

        # Créer quelques fichiers
        (tmp_path / "file1.jpg").write_bytes(b"data1")
        (tmp_path / "file2.jpg").write_bytes(b"data2")
        (tmp_path / "file3.png").write_bytes(b"data3")

        count = manager.clear_cache()

        assert count == 3
        assert list(tmp_path.glob("*")) == []


class TestGetAssetManager:
    """Tests pour get_asset_manager singleton."""

    def test_returns_singleton(self, monkeypatch, tmp_path):
        """get_asset_manager retourne toujours la même instance."""
        # Reset le singleton pour le test
        import mastoc.core.assets as assets_module
        assets_module._asset_manager = None
        monkeypatch.setattr(Path, "home", lambda: tmp_path)

        manager1 = get_asset_manager()
        manager2 = get_asset_manager()

        assert manager1 is manager2

        # Cleanup
        assets_module._asset_manager = None
