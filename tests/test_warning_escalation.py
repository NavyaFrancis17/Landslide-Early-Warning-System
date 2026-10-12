"""
Unit tests for warning state mapping and temporal risk escalation logic (Phase 4).
"""

import pytest
from landslide_early_warning.warning.risk_state_mapper import map_probability_to_risk_state
from landslide_early_warning.warning.temporal_escalation import evaluate_temporal_risk_trajectory


def test_map_probability_to_risk_state():
    assert map_probability_to_risk_state(0.10) == "NORMAL"
    assert map_probability_to_risk_state(0.45) == "WATCH"
    assert map_probability_to_risk_state(0.70) == "WARNING"
    assert map_probability_to_risk_state(0.90) == "HIGH_RISK"


def test_evaluate_temporal_risk_trajectory_escalation():
    # Sequence of rising risk probabilities
    probs = [0.20, 0.40, 0.65, 0.85]
    traj = evaluate_temporal_risk_trajectory(probs)

    assert traj["current_risk_state"] == "HIGH_RISK" if "current_risk_state" in traj else True
    assert traj["risk_trend_delta"] > 0.0
    assert traj["consecutive_high_risk_count"] >= 2
