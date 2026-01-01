"""
Tests pour AnnotationLoader (TODO 12).

Tests couverts :
- AnnotationLoader : chargement async et cache
- AnnotationLoaderSync : version synchrone
"""

import pytest
import time
from unittest.mock import Mock

from mastoc.api.models import (
    HoldAnnotation, HoldConsensus, AnnotationData,
    HoldGripType, HoldCondition, HoldRelativeDifficulty
)
from mastoc.core.annotation_loader import AnnotationLoader, AnnotationLoaderSync


# =============================================================================
# Tests des modèles d'annotation
# =============================================================================

class TestHoldAnnotation:
    """Tests pour HoldAnnotation."""

    def test_from_api_basic(self):
        data = {
            "hold_id": 123,
            "grip_type": "plat",
            "condition": "ok",
            "difficulty": "normale",
            "notes": "Bonne prise"
        }
        ann = HoldAnnotation.from_api(data)
        assert ann.hold_id == 123
        assert ann.grip_type == HoldGripType.PLAT
        assert ann.condition == HoldCondition.OK
        assert ann.difficulty == HoldRelativeDifficulty.NORMALE
        assert ann.notes == "Bonne prise"

    def test_from_api_partial(self):
        data = {
            "hold_id": 456,
            "grip_type": "reglette",
            "condition": None
        }
        ann = HoldAnnotation.from_api(data)
        assert ann.hold_id == 456
        assert ann.grip_type == HoldGripType.REGLETTE
        assert ann.condition is None
        assert ann.difficulty is None

    def test_from_api_empty(self):
        data = {"hold_id": 789}
        ann = HoldAnnotation.from_api(data)
        assert ann.hold_id == 789
        assert ann.grip_type is None

    def test_from_api_unknown_enum(self):
        """Les valeurs enum inconnues sont ignorées."""
        data = {
            "hold_id": 100,
            "grip_type": "unknown_grip_type"
        }
        ann = HoldAnnotation.from_api(data)
        assert ann.grip_type is None


class TestHoldConsensus:
    """Tests pour HoldConsensus."""

    def test_from_api_basic(self):
        data = {
            "hold_id": 123,
            "grip_type": "pince",
            "grip_type_votes": 5,
            "grip_type_confidence": 0.8,
            "condition": "a_brosser",
            "condition_votes": 3,
            "condition_confidence": 0.6,
            "total_annotators": 10
        }
        consensus = HoldConsensus.from_api(data)
        assert consensus.hold_id == 123
        assert consensus.grip_type == HoldGripType.PINCE
        assert consensus.grip_type_votes == 5
        assert consensus.grip_type_confidence == 0.8
        assert consensus.condition == HoldCondition.A_BROSSER
        assert consensus.total_annotators == 10

    def test_from_api_empty(self):
        data = {"hold_id": 456}
        consensus = HoldConsensus.from_api(data)
        assert consensus.hold_id == 456
        assert consensus.grip_type is None
        assert consensus.total_annotators == 0


class TestAnnotationData:
    """Tests pour AnnotationData."""

    def test_init_empty(self):
        consensus = HoldConsensus(hold_id=123)
        data = AnnotationData(hold_id=123, consensus=consensus)
        assert data.hold_id == 123
        assert data.user_annotation is None
        assert data.loaded is False
        assert data.error is None

    def test_with_user_annotation(self):
        consensus = HoldConsensus(hold_id=123)
        user_ann = HoldAnnotation(
            hold_id=123,
            grip_type=HoldGripType.BAC,
            condition=HoldCondition.OK
        )
        data = AnnotationData(
            hold_id=123,
            consensus=consensus,
            user_annotation=user_ann,
            loaded=True
        )
        assert data.user_annotation is not None
        assert data.user_annotation.grip_type == HoldGripType.BAC
        assert data.loaded is True

    def test_from_api_complete(self):
        api_data = {
            "hold_id": 123,
            "grip_type": "plat",
            "grip_type_votes": 3,
            "grip_type_confidence": 0.75,
            "condition": "ok",
            "condition_votes": 4,
            "condition_confidence": 1.0,
            "total_annotators": 4,
            "user_annotation": {
                "hold_id": 123,
                "grip_type": "reglette",
                "condition": "a_brosser",
                "notes": "Mon avis"
            }
        }
        data = AnnotationData.from_api(api_data)
        assert data.hold_id == 123
        assert data.consensus.grip_type == HoldGripType.PLAT
        assert data.consensus.grip_type_votes == 3
        assert data.user_annotation is not None
        assert data.user_annotation.grip_type == HoldGripType.REGLETTE
        assert data.loaded is True


# =============================================================================
# Tests AnnotationLoader
# =============================================================================

class TestAnnotationLoader:
    """Tests pour AnnotationLoader."""

    @pytest.fixture
    def mock_api(self):
        api = Mock()
        api.get_hold_annotations.return_value = AnnotationData(
            hold_id=123,
            consensus=HoldConsensus(hold_id=123),
            loaded=True
        )
        api.get_hold_annotations_batch.return_value = {}
        return api

    def test_init(self, mock_api):
        loader = AnnotationLoader(mock_api, cache_ttl=60)
        assert loader.api == mock_api
        assert loader.cache_ttl == 60
        assert loader.on_data_loaded is None

    def test_cache_miss(self, mock_api):
        loader = AnnotationLoader(mock_api)
        cached = loader._get_cached(123)
        assert cached is None

    def test_cache_hit(self, mock_api):
        loader = AnnotationLoader(mock_api, cache_ttl=300)
        data = AnnotationData(
            hold_id=123,
            consensus=HoldConsensus(hold_id=123),
            loaded=True
        )
        loader._set_cached(123, data)

        cached = loader._get_cached(123)
        assert cached is not None
        assert cached.hold_id == 123

    def test_cache_expired(self, mock_api):
        loader = AnnotationLoader(mock_api, cache_ttl=0)
        data = AnnotationData(
            hold_id=123,
            consensus=HoldConsensus(hold_id=123),
            loaded=True
        )
        loader._set_cached(123, data)

        time.sleep(0.01)
        cached = loader._get_cached(123)
        assert cached is None

    def test_invalidate(self, mock_api):
        loader = AnnotationLoader(mock_api)
        data = AnnotationData(
            hold_id=123,
            consensus=HoldConsensus(hold_id=123),
            loaded=True
        )
        loader._set_cached(123, data)

        loader.invalidate(123)
        assert loader._get_cached(123) is None

    def test_clear_cache(self, mock_api):
        loader = AnnotationLoader(mock_api)
        loader._set_cached(1, AnnotationData(hold_id=1, consensus=HoldConsensus(hold_id=1)))
        loader._set_cached(2, AnnotationData(hold_id=2, consensus=HoldConsensus(hold_id=2)))

        loader.clear_cache()
        assert loader._get_cached(1) is None
        assert loader._get_cached(2) is None

    def test_get_cached_public(self, mock_api):
        """get_cached() retourne les données même expirées."""
        loader = AnnotationLoader(mock_api, cache_ttl=0)
        data = AnnotationData(
            hold_id=123,
            consensus=HoldConsensus(hold_id=123),
            loaded=True
        )
        loader._set_cached(123, data)

        time.sleep(0.01)
        # get_cached (public) ignore l'expiration
        cached = loader.get_cached(123)
        assert cached is not None

    def test_fetch_annotation_data(self, mock_api):
        consensus = HoldConsensus(
            hold_id=123,
            grip_type=HoldGripType.PLAT,
            grip_type_votes=5
        )
        mock_api.get_hold_annotations.return_value = AnnotationData(
            hold_id=123,
            consensus=consensus,
            loaded=True
        )

        loader = AnnotationLoader(mock_api)
        data = loader._fetch_annotation_data(123)

        assert data.loaded is True
        assert data.consensus.grip_type == HoldGripType.PLAT

    def test_fetch_annotation_data_with_error(self, mock_api):
        mock_api.get_hold_annotations.side_effect = Exception("Network error")

        loader = AnnotationLoader(mock_api)
        data = loader._fetch_annotation_data(123)

        assert data.loaded is False
        assert "Network error" in data.error

    def test_load_with_cache(self, mock_api):
        """Test que load() utilise le cache."""
        loader = AnnotationLoader(mock_api)
        cached_data = AnnotationData(
            hold_id=123,
            consensus=HoldConsensus(hold_id=123),
            loaded=True
        )
        loader._set_cached(123, cached_data)

        callback_called = []
        loader.on_data_loaded = lambda d: callback_called.append(d)

        loader.load(123)

        # Le callback doit être appelé immédiatement avec les données cachées
        assert len(callback_called) == 1
        assert callback_called[0].hold_id == 123
        # L'API ne doit pas être appelée
        mock_api.get_hold_annotations.assert_not_called()

    def test_load_batch_filters_cached(self, mock_api):
        """load_batch() ne charge pas les IDs déjà en cache."""
        loader = AnnotationLoader(mock_api)
        # Mettre hold 1 en cache
        loader._set_cached(1, AnnotationData(
            hold_id=1,
            consensus=HoldConsensus(hold_id=1),
            loaded=True
        ))

        # Charger holds 1, 2, 3
        loader.load_batch([1, 2, 3])

        # Seuls 2 et 3 doivent être chargés
        mock_api.get_hold_annotations_batch.assert_called_once_with([2, 3])


class TestAnnotationLoaderSync:
    """Tests pour AnnotationLoaderSync."""

    def test_load_sync(self):
        api = Mock()
        consensus = HoldConsensus(
            hold_id=123,
            grip_type=HoldGripType.PINCE,
            grip_type_votes=3
        )
        api.get_hold_annotations.return_value = AnnotationData(
            hold_id=123,
            consensus=consensus,
            loaded=True
        )

        loader = AnnotationLoaderSync(api)
        data = loader.load(123)

        assert data.hold_id == 123
        assert data.loaded is True
        assert data.consensus.grip_type == HoldGripType.PINCE

    def test_load_sync_error(self):
        api = Mock()
        api.get_hold_annotations.side_effect = Exception("API error")

        loader = AnnotationLoaderSync(api)
        data = loader.load(123)

        assert data.loaded is False
        assert "API error" in data.error

    def test_load_batch_sync(self):
        api = Mock()
        api.get_hold_annotations_batch.return_value = {
            1: AnnotationData(hold_id=1, consensus=HoldConsensus(hold_id=1), loaded=True),
            2: AnnotationData(hold_id=2, consensus=HoldConsensus(hold_id=2), loaded=True),
        }

        loader = AnnotationLoaderSync(api)
        result = loader.load_batch([1, 2])

        assert len(result) == 2
        assert result[1].hold_id == 1
        assert result[2].hold_id == 2

    def test_load_batch_sync_error(self):
        api = Mock()
        api.get_hold_annotations_batch.side_effect = Exception("Batch error")

        loader = AnnotationLoaderSync(api)
        result = loader.load_batch([1, 2])

        assert len(result) == 2
        assert result[1].loaded is False
        assert result[2].loaded is False
