"""
Tests pour BackendSwitch.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from mastoc.core.backend import (
    BackendSwitch,
    BackendConfig,
    BackendSource,
    RailwayBackend,
    StoktBackend,
    MONTOBOARD_GYM_ID,
)
from mastoc.api.models import Climb, Hold, Face


class TestBackendConfig:
    """Tests pour BackendConfig."""

    def test_default_config(self):
        """Test configuration par défaut."""
        config = BackendConfig()
        assert config.source == BackendSource.RAILWAY
        assert config.railway_url == "https://mastoc-production.up.railway.app"
        assert config.railway_api_key is None
        assert config.fallback_to_stokt is True

    def test_custom_config(self):
        """Test configuration personnalisée."""
        config = BackendConfig(
            source=BackendSource.STOKT,
            railway_api_key="my-key",
            stokt_token="stokt-token",
        )
        assert config.source == BackendSource.STOKT
        assert config.railway_api_key == "my-key"
        assert config.stokt_token == "stokt-token"


class TestBackendSource:
    """Tests pour BackendSource enum."""

    def test_railway_value(self):
        assert BackendSource.RAILWAY.value == "railway"

    def test_stokt_value(self):
        assert BackendSource.STOKT.value == "stokt"


class TestRailwayBackend:
    """Tests pour RailwayBackend."""

    def test_source(self):
        """Test que source retourne RAILWAY."""
        config = BackendConfig(railway_api_key="test")
        backend = RailwayBackend(config)
        assert backend.source == BackendSource.RAILWAY

    def test_is_authenticated_without_key(self):
        """Test non authentifié sans API key."""
        config = BackendConfig()
        backend = RailwayBackend(config)
        assert not backend.is_authenticated()

    def test_is_authenticated_with_key(self):
        """Test authentifié avec API key."""
        config = BackendConfig(railway_api_key="my-key")
        backend = RailwayBackend(config)
        assert backend.is_authenticated()

    def test_set_api_key(self):
        """Test set_api_key."""
        config = BackendConfig()
        backend = RailwayBackend(config)
        assert not backend.is_authenticated()

        backend.set_api_key("new-key")
        assert backend.is_authenticated()
        assert config.railway_api_key == "new-key"

    def test_get_climbs(self):
        """Test get_climbs délègue à MastocAPI."""
        config = BackendConfig(railway_api_key="test")
        backend = RailwayBackend(config)

        # Mock l'API
        mock_climbs = [
            Mock(spec=Climb, id="1", name="Bloc 1"),
            Mock(spec=Climb, id="2", name="Bloc 2"),
        ]
        backend._api.get_climbs = Mock(return_value=(mock_climbs, 2))

        climbs, total = backend.get_climbs()
        assert total == 2
        assert len(climbs) == 2
        backend._api.get_climbs.assert_called_once()

    def test_get_face_setup_delegates_to_api(self):
        """Test que get_face_setup délègue à MastocAPI."""
        config = BackendConfig(railway_api_key="test")
        backend = RailwayBackend(config)

        mock_face = Mock(spec=Face, id="face-uuid")
        mock_face.holds = [Mock(spec=Hold, id=1), Mock(spec=Hold, id=2)]
        backend._api.get_face_setup = Mock(return_value=mock_face)

        face = backend.get_face_setup("face-uuid")
        assert face.id == "face-uuid"
        backend._api.get_face_setup.assert_called_once_with("face-uuid")


class TestStoktBackend:
    """Tests pour StoktBackend."""

    def test_source(self):
        """Test que source retourne STOKT."""
        config = BackendConfig(source=BackendSource.STOKT)
        backend = StoktBackend(config)
        assert backend.source == BackendSource.STOKT

    def test_montoboard_gym_id(self):
        """Test constante gym ID."""
        assert StoktBackend.MONTOBOARD_GYM_ID == MONTOBOARD_GYM_ID

    def test_is_authenticated_without_token(self):
        """Test non authentifié sans token."""
        config = BackendConfig(source=BackendSource.STOKT)
        backend = StoktBackend(config)
        assert not backend.is_authenticated()

    def test_is_authenticated_with_token(self):
        """Test authentifié avec token."""
        config = BackendConfig(source=BackendSource.STOKT, stokt_token="my-token")
        backend = StoktBackend(config)
        assert backend.is_authenticated()

    def test_build_stokt_payload(self):
        """Test construction du payload Stokt."""
        config = BackendConfig(source=BackendSource.STOKT)
        backend = StoktBackend(config)

        payload = backend._build_stokt_payload(
            name="Test Bloc",
            holds_list="S1 S2 O3 O4 F5 T6",
            grade_font="6A",
            feet_rule="Free feet",
            description="Description",
            is_private=True,
        )

        assert payload["name"] == "Test Bloc"
        assert payload["holdsList"]["start"] == ["1", "2"]
        assert payload["holdsList"]["others"] == ["3", "4"]
        assert payload["holdsList"]["feetOnly"] == ["5"]
        assert payload["holdsList"]["top"] == ["6"]
        assert payload["grade"]["gradingSystem"] == "font"
        assert payload["grade"]["value"] == "6A"
        assert payload["feetRule"] == "Free feet"
        assert payload["isPrivate"] is True


class TestBackendSwitch:
    """Tests pour BackendSwitch."""

    def test_default_source_is_railway(self):
        """Test que la source par défaut est Railway."""
        switch = BackendSwitch()
        assert switch.source == BackendSource.RAILWAY

    def test_primary_is_railway_by_default(self):
        """Test que primary retourne Railway par défaut."""
        switch = BackendSwitch()
        assert isinstance(switch.primary, RailwayBackend)

    def test_switch_to_stokt(self):
        """Test changement de source vers Stokt."""
        config = BackendConfig(source=BackendSource.STOKT)
        switch = BackendSwitch(config)
        assert switch.source == BackendSource.STOKT
        assert isinstance(switch.primary, StoktBackend)

    def test_railway_and_stokt_accessible(self):
        """Test accès aux deux backends."""
        config = BackendConfig(
            source=BackendSource.RAILWAY,
            railway_api_key="railway-key",
            fallback_to_stokt=True,
        )
        switch = BackendSwitch(config)

        assert switch.railway is not None
        assert switch.stokt is not None

    def test_set_railway_api_key(self):
        """Test set_railway_api_key."""
        switch = BackendSwitch()
        assert not switch.is_authenticated()

        switch.set_railway_api_key("my-key")
        assert switch.is_authenticated()

    def test_set_stokt_token(self):
        """Test set_stokt_token."""
        config = BackendConfig(source=BackendSource.STOKT)
        switch = BackendSwitch(config)
        assert not switch.is_authenticated()

        switch.set_stokt_token("my-token")
        assert switch.is_authenticated()

    def test_switch_source(self):
        """Test changement de source dynamique."""
        switch = BackendSwitch()
        assert switch.source == BackendSource.RAILWAY

        switch.switch_source(BackendSource.STOKT)
        assert switch.source == BackendSource.STOKT
        assert isinstance(switch.primary, StoktBackend)

    def test_get_climbs_delegates_to_primary(self):
        """Test que get_climbs délègue au backend principal."""
        config = BackendConfig(railway_api_key="test")
        switch = BackendSwitch(config)

        mock_climbs = [Mock(spec=Climb)]
        switch.railway._api.get_climbs = Mock(return_value=(mock_climbs, 1))

        climbs, total = switch.get_climbs()
        assert len(climbs) == 1
        switch.railway._api.get_climbs.assert_called_once()

    def test_fallback_when_primary_fails(self):
        """Test fallback vers Stokt si Railway échoue."""
        config = BackendConfig(
            source=BackendSource.RAILWAY,
            railway_api_key="test",
            fallback_to_stokt=True,
            stokt_token="stokt-token",
        )
        switch = BackendSwitch(config)

        # Railway échoue
        switch.railway._api.get_climbs = Mock(side_effect=Exception("Railway down"))

        # Stokt fonctionne
        mock_climbs = [Mock(spec=Climb)]
        switch.stokt._api.get_gym_climbs = Mock(return_value=(mock_climbs, 1, None))

        climbs, total = switch.get_climbs()
        assert len(climbs) == 1

    def test_no_fallback_when_disabled(self):
        """Test pas de fallback si désactivé."""
        config = BackendConfig(
            source=BackendSource.RAILWAY,
            railway_api_key="test",
            fallback_to_stokt=False,
        )
        switch = BackendSwitch(config)

        # Railway échoue
        switch.railway._api.get_climbs = Mock(side_effect=Exception("Railway down"))

        with pytest.raises(Exception, match="Railway down"):
            switch.get_climbs()


class TestBackendSwitchCreateClimb:
    """Tests pour create_climb via BackendSwitch."""

    def test_create_climb_railway(self):
        """Test création via Railway."""
        config = BackendConfig(railway_api_key="test")
        switch = BackendSwitch(config)

        mock_climb = Mock(spec=Climb, id="new-id", name="Test")
        switch.railway._api.create_climb = Mock(return_value=mock_climb)

        result = switch.create_climb(
            face_id="face-uuid",
            name="Test",
            holds_list="S1 T2",
            grade_font="5",
        )

        assert result.id == "new-id"
        switch.railway._api.create_climb.assert_called_once()


class TestBackendIntegration:
    """Tests d'intégration simples."""

    def test_full_workflow_railway(self):
        """Test workflow complet avec Railway."""
        config = BackendConfig(railway_api_key="test-key")
        switch = BackendSwitch(config)

        # Mock all API calls
        switch.railway._api.get_climbs = Mock(return_value=([], 0))
        switch.railway._api.get_all_climbs = Mock(return_value=[])
        switch.railway._api.get_holds = Mock(return_value=[])

        # Test workflow
        assert switch.is_authenticated()
        climbs, _ = switch.get_climbs()
        assert climbs == []

        all_climbs = switch.get_all_climbs()
        assert all_climbs == []

        holds = switch.get_holds("face-uuid")
        assert holds == []
