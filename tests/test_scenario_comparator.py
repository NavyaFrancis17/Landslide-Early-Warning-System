"""
Unit tests for scenario comparison and transition detection (Phase 7).
"""

import pytest
from landslide_early_warning.simulation.scenario_comparator import compare_baseline_and_scenario


def test_compare_baseline_and_scenario():
    base_res = {
        "risk_probability": 0.40,
        "warning_state": "WATCH",
        "anomaly_z_score": 1.2,
        "anomaly_state": "NORMAL",
    }

    scen_res = {
        "risk_probability": 0.65,
        "warning_state": "WARNING",
        "anomaly_z_score": 2.0,
        "anomaly_state": "ABNORMAL",
    }

    scen_meta = {"scenario_name": "rf_plus_50", "category": "RAINFALL"}

    comp = compare_baseline_and_scenario(base_res, scen_res, scen_meta)

    assert comp["risk_probability_change"] == 0.25
    assert comp["warning_state_changed"] is True
    assert comp["transition_type"] == "WATCH_TO_WARNING"
    assert comp["baseline_warning_state"] == "WATCH"
    assert comp["scenario_warning_state"] == "WARNING"
