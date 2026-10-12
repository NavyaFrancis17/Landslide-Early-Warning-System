"""
Unit tests for pre-event temporal alignment and no-future-data rule (Phase 3).
"""

from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import pytest

from landslide_early_warning.temporal_alignment import (
    compute_preevent_features,
    filter_preevent_observations,
)


def create_synthetic_hourly_env_df():
    # 7 days of hourly observations
    times = pd.date_range(start="2026-01-01 00:00", end="2026-01-08 00:00", freq="1h", tz="UTC")
    df = pd.DataFrame({
        "precipitation": [0.5 if i % 6 == 0 else 0.0 for i in range(len(times))],
        "soil_moisture_0_to_7cm": [0.30 + (i * 0.001) for i in range(len(times))],
        "soil_moisture_7_to_28cm": [0.35] * len(times),
        "soil_moisture_28_to_100cm": [0.40] * len(times),
        "temperature_2m": [22.0] * len(times),
        "relative_humidity_2m": [80.0] * len(times),
    }, index=times)
    return df


def test_filter_preevent_observations_no_future_leakage():
    env_df = create_synthetic_hourly_env_df()
    event_ts = pd.Timestamp("2026-01-05 12:00:00", tz="UTC")

    filtered = filter_preevent_observations(env_df, event_ts, prediction_cutoff_hours=0)

    # Maximum observation timestamp must be <= event_ts
    assert filtered.index.max() <= event_ts
    # Observations strictly after event_ts must not be in filtered dataframe
    assert (filtered.index > event_ts).sum() == 0


def test_compute_preevent_features():
    env_df = create_synthetic_hourly_env_df()
    event_ts = pd.Timestamp("2026-01-05 12:00:00", tz="UTC")

    feats = compute_preevent_features(env_df, event_ts, prediction_cutoff_hours=0)

    assert feats["temporal_match_valid"] is True
    assert feats["pre_event_observations_count"] > 0
    assert "precipitation_24h" in feats
    assert "precipitation_72h" in feats
    assert "soil_moisture_layer1_current" in feats
    assert "soil_moisture_layer1_change_24h" in feats
    assert feats["precipitation_24h"] >= 0.0
