"""
Unit tests for warning configuration loader (Phase 5).
"""

from pathlib import Path
import pytest
from landslide_early_warning.warning.warning_config import DEFAULT_WARNING_CONFIG, load_warning_config


def test_load_warning_config_default_fallback():
    cfg = load_warning_config(Path("non_existent_config.yaml"))
    assert isinstance(cfg, dict)
    assert "risk_states" in cfg
    assert "persistence" in cfg
    assert "trend" in cfg
    assert "abnormality" in cfg


def test_load_warning_config_file():
    config_file = Path("config/warning_config.yaml")
    cfg = load_warning_config(config_file)
    assert isinstance(cfg, dict)
    assert "risk_states" in cfg
    assert cfg["risk_states"]["HIGH_RISK"]["min_probability"] == 0.80
