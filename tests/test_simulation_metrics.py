"""
Unit tests for simulation metrics aggregation (Phase 7).
"""

import pytest
from landslide_early_warning.simulation.simulation_metrics import aggregate_simulation_summary_metrics


def test_aggregate_simulation_summary_metrics():
    comp_list = [
        {"risk_probability_change": 0.10, "warning_state_changed": False, "transition_type": "NO_CHANGE"},
        {"risk_probability_change": 0.25, "warning_state_changed": True, "transition_type": "WATCH_TO_WARNING"},
    ]
    extrap_list = [False, True]

    summary = aggregate_simulation_summary_metrics(comp_list, extrap_list)

    assert summary["total_simulations_evaluated"] == 2
    assert summary["mean_risk_probability_change"] == 0.175
    assert summary["total_warning_state_transitions"] == 1
    assert summary["extrapolation_scenarios_count"] == 1
    assert summary["extrapolation_percentage"] == 50.0
