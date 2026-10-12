"""
Unit tests for simulation configuration loader (Phase 7).
"""

from pathlib import Path
import pytest
from landslide_early_warning.simulation.scenario_config import load_simulation_config


def test_load_simulation_config_fallback():
    cfg = load_simulation_config(Path("non_existent.yaml"))
    assert isinstance(cfg, dict)
    assert "simulation" in cfg
    assert "rainfall" in cfg["simulation"]


def test_load_simulation_config_file():
    cfg = load_simulation_config(Path("config/simulation_config.yaml"))
    assert isinstance(cfg, dict)
    assert "simulation" in cfg
    assert cfg["simulation"]["enabled_features"]["rainfall"] is True
