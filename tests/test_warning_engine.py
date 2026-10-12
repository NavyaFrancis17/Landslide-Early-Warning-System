"""
Comprehensive unit tests for the EarlyWarningEngine (Phase 5).
"""

from pathlib import Path
import pytest
import numpy as np

from landslide_early_warning.warning.alert_explanation import generate_warning_explanation
from landslide_early_warning.warning.persistence import apply_warning_state_persistence
from landslide_early_warning.warning.risk_state_mapper import map_probability_to_risk_state
from landslide_early_warning.warning.risk_trend import compute_temporal_risk_trend
from landslide_early_warning.warning.warning_engine import EarlyWarningEngine


def test_warning_state_assignments():
    assert map_probability_to_risk_state(0.10) == "NORMAL"
    assert map_probability_to_risk_state(0.40) == "WATCH"
    assert map_probability_to_risk_state(0.70) == "WARNING"
    assert map_probability_to_risk_state(0.90) == "HIGH_RISK"


def test_risk_trend_calculation():
    # Rising trend
    rising = compute_temporal_risk_trend([0.20, 0.40, 0.65])
    assert rising["risk_trend"] == "INCREASING"
    assert rising["trend_delta"] > 0.0

    # Falling trend
    falling = compute_temporal_risk_trend([0.80, 0.50, 0.20])
    assert falling["risk_trend"] == "DECREASING"
    assert falling["trend_delta"] < 0.0


def test_warning_state_persistence_locking():
    # High risk requires 3 consecutive observations to lock into HIGH_RISK
    history_2obs = ["HIGH_RISK", "HIGH_RISK"]
    res_2 = apply_warning_state_persistence(history_2obs, "HIGH_RISK", min_high_risk_persistence=3)
    assert res_2["persisted_state"] == "WARNING"  # Gated at WARNING until 3 obs

    history_3obs = ["HIGH_RISK", "HIGH_RISK", "HIGH_RISK"]
    res_3 = apply_warning_state_persistence(history_3obs, "HIGH_RISK", min_high_risk_persistence=3)
    assert res_3["persisted_state"] == "HIGH_RISK"  # Locked into HIGH_RISK


def test_generate_warning_explanation():
    exp = generate_warning_explanation(
        warning_state="HIGH_RISK",
        risk_probability=0.85,
        anomaly_status="STRONGLY_ABNORMAL",
        anomaly_z_score=2.85,
        risk_trend="INCREASING",
        trend_delta=0.15,
        consecutive_high_count=3,
    )
    assert "Research Warning State: HIGH_RISK" in exp
    assert "strongly abnormal" in exp
    assert "INCREASING" in exp


def test_early_warning_engine_predict_warning():
    engine = EarlyWarningEngine.load_from_saved_models()

    sample_obs = {
        "event_id": "TEST_EVENT_001",
        "event_date": "2026-01-01",
        "landslide_latitude": 32.5,
        "landslide_longitude": 107.4,
        "precipitation_1h": 2.5,
        "precipitation_3h": 10.0,
        "precipitation_6h": 25.0,
        "precipitation_12h": 45.0,
        "precipitation_24h": 80.0,
        "precipitation_72h": 120.0,
        "precipitation_168h": 180.0,
        "precipitation_max_intensity_24h": 15.0,
        "soil_moisture_layer1_current": 0.45,
        "soil_moisture_layer1_mean_24h": 0.35,
        "soil_moisture_layer1_mean_72h": 0.30,
        "soil_moisture_layer1_change_24h": 0.10,
        "soil_moisture_layer1_change_72h": 0.15,
        "soil_moisture_layer2_current": 0.40,
        "soil_moisture_layer3_current": 0.42,
        "temperature_2m_mean_24h": 20.0,
        "relative_humidity_2m_mean_24h": 85.0,
        "matched_grid_elevation": 500.0,
        "event_month": 7,
        "event_day_of_year": 200,
    }

    res = engine.predict_warning(sample_obs)

    assert "risk_probability" in res
    assert 0.0 <= res["risk_probability"] <= 1.0
    assert res["current_warning_state"] in ["NORMAL", "WATCH", "WARNING", "HIGH_RISK"]
    assert "warning_reason" in res
    assert "Research Warning State" in res["warning_reason"]
