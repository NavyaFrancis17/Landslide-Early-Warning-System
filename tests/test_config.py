"""
Tests for configuration loading functionality.
"""

from pathlib import Path
import pytest
from landslide_early_warning.config_loader import load_config


def test_load_config_success():
    """Test that config.yaml loads successfully and contains required fields."""
    root_dir = Path(__file__).resolve().parent.parent
    config_file = root_dir / "config.yaml"
    assert config_file.exists(), "config.yaml must exist in project root"

    config = load_config(config_file)
    assert isinstance(config, dict), "Config must load as a dictionary"
    assert "project" in config, "Config must contain 'project' section"
    assert "paths" in config, "Config must contain 'paths' section"
    assert config["project"]["name"] == "AI-Based Location-Adaptive Landslide Early-Warning System"
    assert config["project"]["phase"] in (1, 2, 3)


def test_load_config_missing_file():
    """Test that loading a non-existent config file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        load_config(Path("non_existent_config.yaml"))
