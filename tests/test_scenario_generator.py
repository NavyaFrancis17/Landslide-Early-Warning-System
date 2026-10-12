"""
Unit tests for scenario generator (Phase 7).
"""

import pytest
from landslide_early_warning.simulation.scenario_generator import generate_simulation_scenarios


def test_generate_simulation_scenarios():
    scenarios = generate_simulation_scenarios()
    assert isinstance(scenarios, list)
    assert len(scenarios) > 0
    assert scenarios[0]["scenario_name"] == "baseline"
    categories = {s["category"] for s in scenarios}
    assert "BASELINE" in categories
    assert "RAINFALL" in categories
    assert "SOIL_MOISTURE" in categories
    assert "COMBINED" in categories
