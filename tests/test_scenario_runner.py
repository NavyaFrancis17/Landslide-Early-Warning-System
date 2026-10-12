"""
Unit tests for scenario runner and WhatIfSimulator (Phase 7).
"""

import pytest
from landslide_early_warning.simulation.what_if_simulator import WhatIfSimulator


def test_what_if_simulator_simulate_scenario():
    simulator = WhatIfSimulator.load_from_saved_models()

    sample_obs = {
        "event_id": "SIM_TEST_001",
        "event_date": "2026-01-01",
        "landslide_latitude": 32.5,
        "landslide_longitude": 107.4,
        "precipitation_1h": 2.5,
        "precipitation_3h": 10.0,
        "precipitation_6h": 25.0,
        "precipitation_12h": 45.0,
        "precipitation_24h": 50.0,
        "precipitation_72h": 100.0,
        "precipitation_168h": 150.0,
        "precipitation_max_intensity_24h": 15.0,
        "soil_moisture_layer1_current": 0.35,
        "soil_moisture_layer1_mean_24h": 0.30,
        "soil_moisture_layer1_mean_72h": 0.28,
        "soil_moisture_layer1_change_24h": 0.05,
        "soil_moisture_layer1_change_72h": 0.10,
        "soil_moisture_layer2_current": 0.35,
        "soil_moisture_layer3_current": 0.38,
        "temperature_2m_mean_24h": 20.0,
        "relative_humidity_2m_mean_24h": 85.0,
        "matched_grid_elevation": 500.0,
        "event_month": 7,
        "event_day_of_year": 200,
    }

    scen = {
        "scenario_name": "test_rf_plus_50",
        "category": "RAINFALL",
        "rainfall_multiplier": 1.50,
        "soil_moisture_multiplier": 1.0,
    }

    res = simulator.simulate_scenario(sample_obs, scen)

    assert "baseline_result" in res
    assert "scenario_result" in res
    assert "comparison" in res
    assert res["comparison"]["scenario_name"] == "test_rf_plus_50"
    assert "explanation" in res
