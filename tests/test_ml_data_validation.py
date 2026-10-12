"""
Unit tests for ML dataset validation module (Phase 4).
"""

import pandas as pd
import pytest
from landslide_early_warning.ml.data_validation import validate_ml_ready_dataset


def test_validate_ml_ready_dataset():
    df = pd.DataFrame({
        "event_id": [1, 2, 3],
        "precipitation_24h": [10.5, 25.0, 0.0],
        "soil_moisture_layer1_current": [0.35, 0.45, 0.20],
        "environmental_data_available": [True, True, False],
        "spatial_match_valid": [True, True, True],
        "landslide_size": ["Large", "Medium", "Small"],  # Forbidden leakage
    })

    val_df, report = validate_ml_ready_dataset(df, require_valid_quality_flags=True)

    # 1. Leakage column removed
    assert "landslide_size" not in val_df.columns
    assert "landslide_size" in report["removed_leakage_columns"]

    # 2. Low quality flag sample filtered (sample 3 has environmental_data_available=False)
    assert len(val_df) == 2
    assert report["quality_filter_summary"]["retained_samples"] == 2
