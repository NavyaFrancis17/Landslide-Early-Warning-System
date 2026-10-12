"""
Unit tests for environmental feature modifier and physical domain checks (Phase 7).
"""

import pytest
from landslide_early_warning.simulation.feature_modifier import modify_observation_features


def test_modify_observation_features_rainfall_multiplier():
    baseline_obs = {
        "precipitation_24h": 40.0,
        "soil_moisture_layer1_current": 0.35,
    }

    sim_obs, mods, is_extrap, domain_warns = modify_observation_features(
        baseline_obs, rainfall_multiplier=1.50
    )

    assert sim_obs["precipitation_24h"] == 60.0
    assert sim_obs["soil_moisture_layer1_current"] == 0.35
    assert mods["precipitation_24h"]["original_value"] == 40.0
    assert mods["precipitation_24h"]["scenario_value"] == 60.0
    assert is_extrap is False


def test_modify_observation_features_extrapolation_check():
    baseline_obs = {
        "precipitation_24h": 300.0,
        "soil_moisture_layer1_current": 0.35,
    }

    sim_obs, mods, is_extrap, domain_warns = modify_observation_features(
        baseline_obs, rainfall_multiplier=2.00
    )

    assert sim_obs["precipitation_24h"] == 600.0
    assert is_extrap is True
    assert len(domain_warns) > 0
