"""Tests pour le module de configuration persistante."""

import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open

from mastoc.core.config import AppConfig


class TestAppConfig:
    """Tests pour AppConfig."""

    def test_default_values(self):
        """Teste les valeurs par défaut."""
        config = AppConfig()

        assert config.source == "stokt"
        assert config.railway_api_key is None
        assert config.railway_url == "https://mastoc-production.up.railway.app"

    def test_custom_values(self):
        """Teste la création avec des valeurs personnalisées."""
        config = AppConfig(
            source="railway",
            railway_api_key="my-test-key",
            railway_url="https://custom.example.com",
        )

        assert config.source == "railway"
        assert config.railway_api_key == "my-test-key"
        assert config.railway_url == "https://custom.example.com"

    def test_config_path(self):
        """Teste le chemin du fichier de configuration."""
        path = AppConfig.get_config_path()

        assert path == Path.home() / ".mastoc" / "config.json"

    def test_load_no_file(self, tmp_path):
        """Teste le chargement quand le fichier n'existe pas."""
        with patch.object(AppConfig, "get_config_path", return_value=tmp_path / "nonexistent.json"):
            config = AppConfig.load()

        # Doit retourner les valeurs par défaut
        assert config.source == "stokt"
        assert config.railway_api_key is None

    def test_load_valid_file(self, tmp_path):
        """Teste le chargement d'un fichier valide."""
        config_path = tmp_path / "config.json"
        config_data = {
            "source": "railway",
            "railway_api_key": "saved-key",
            "railway_url": "https://saved.example.com",
        }
        config_path.write_text(json.dumps(config_data))

        with patch.object(AppConfig, "get_config_path", return_value=config_path):
            config = AppConfig.load()

        assert config.source == "railway"
        assert config.railway_api_key == "saved-key"
        assert config.railway_url == "https://saved.example.com"

    def test_load_partial_file(self, tmp_path):
        """Teste le chargement d'un fichier avec des valeurs partielles."""
        config_path = tmp_path / "config.json"
        config_data = {
            "source": "railway",
            # Pas d'API key
        }
        config_path.write_text(json.dumps(config_data))

        with patch.object(AppConfig, "get_config_path", return_value=config_path):
            config = AppConfig.load()

        assert config.source == "railway"
        assert config.railway_api_key is None  # Valeur par défaut
        assert config.railway_url == "https://mastoc-production.up.railway.app"  # Valeur par défaut

    def test_load_invalid_json(self, tmp_path):
        """Teste le chargement d'un fichier JSON invalide."""
        config_path = tmp_path / "config.json"
        config_path.write_text("{ invalid json }")

        with patch.object(AppConfig, "get_config_path", return_value=config_path):
            config = AppConfig.load()

        # Doit retourner les valeurs par défaut
        assert config.source == "stokt"

    def test_save(self, tmp_path):
        """Teste la sauvegarde de la configuration."""
        config_path = tmp_path / "config.json"

        config = AppConfig(
            source="railway",
            railway_api_key="my-key",
        )

        with patch.object(AppConfig, "get_config_path", return_value=config_path):
            result = config.save()

        assert result is True
        assert config_path.exists()

        # Vérifier le contenu
        saved_data = json.loads(config_path.read_text())
        assert saved_data["source"] == "railway"
        assert saved_data["railway_api_key"] == "my-key"

    def test_save_creates_directory(self, tmp_path):
        """Teste que save() crée le dossier parent si nécessaire."""
        config_path = tmp_path / "new_dir" / "config.json"

        config = AppConfig(source="railway")

        with patch.object(AppConfig, "get_config_path", return_value=config_path):
            result = config.save()

        assert result is True
        assert config_path.exists()
        assert config_path.parent.exists()

    def test_roundtrip(self, tmp_path):
        """Teste un cycle complet save/load."""
        config_path = tmp_path / "config.json"

        # Créer et sauvegarder
        config1 = AppConfig(
            source="railway",
            railway_api_key="roundtrip-key",
            railway_url="https://roundtrip.example.com",
        )

        with patch.object(AppConfig, "get_config_path", return_value=config_path):
            config1.save()

            # Charger
            config2 = AppConfig.load()

        assert config2.source == config1.source
        assert config2.railway_api_key == config1.railway_api_key
        assert config2.railway_url == config1.railway_url
