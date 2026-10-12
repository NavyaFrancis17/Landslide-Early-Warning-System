"""
Unit tests for automated leakage guard (Phase 4).
"""

import pandas as pd
import pytest
from landslide_early_warning.ml.leakage_guard import verify_feature_matrix_leakage_free


def test_verify_feature_matrix_leakage_free_valid():
    df = pd.DataFrame(columns=["precipitation_24h", "soil_moisture_layer1_current", "temperature_2m_mean_24h"])
    assert verify_feature_matrix_leakage_free(df) is True


def test_verify_feature_matrix_leakage_free_rejects_fatality_count():
    df = pd.DataFrame(columns=["precipitation_24h", "fatality_count"])
    with pytest.raises(ValueError, match="LEAKAGE GUARD FAILURE"):
        verify_feature_matrix_leakage_free(df)


def test_verify_feature_matrix_leakage_free_rejects_post_event_keywords():
    df = pd.DataFrame(columns=["precipitation_24h", "submitted_date"])
    with pytest.raises(ValueError, match="LEAKAGE GUARD FAILURE"):
        verify_feature_matrix_leakage_free(df)
