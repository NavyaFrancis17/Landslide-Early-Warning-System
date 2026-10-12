"""
Unit tests for feature builder pipeline and leakage prevention assertions (Phase 3).
"""

from pathlib import Path
import pandas as pd
import pytest

from landslide_early_warning.leakage import (
    FORBIDDEN_PREDICTIVE_COLUMNS,
    assert_no_leakage_features,
)


def test_assert_no_leakage_features_clean():
    clean_features = ["latitude", "longitude", "precipitation_24h", "soil_moisture_layer1_current"]
    assert assert_no_leakage_features(clean_features) is True


def test_assert_no_leakage_features_detects_leakage():
    dirty_features = ["latitude", "longitude", "landslide_size", "precipitation_24h"]
    with pytest.raises(ValueError, match="DATA LEAKAGE DETECTED"):
        assert_no_leakage_features(dirty_features)


def test_assert_no_leakage_features_detects_post_event_timestamps():
    dirty_features = ["latitude", "longitude", "submitted_date", "precipitation_24h"]
    with pytest.raises(ValueError, match="DATA LEAKAGE DETECTED"):
        assert_no_leakage_features(dirty_features)
