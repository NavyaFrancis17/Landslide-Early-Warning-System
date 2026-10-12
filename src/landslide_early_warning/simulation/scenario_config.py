"""
Simulation Configuration Loader Module.

Ingests and validates scenario parameters, multiplier grids, feature limits,
and sampling settings from config/simulation_config.yaml.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml


DEFAULT_SIMULATION_CONFIG: Dict[str, Any] = {
    "simulation": {
        "enabled_features": {"rainfall": True, "soil_moisture": True},
        "rainfall": {
            "scenarios": [
                {"name": "baseline", "multiplier": 1.0},
                {"name": "rainfall_plus_10", "multiplier": 1.10},
                {"name": "rainfall_plus_25", "multiplier": 1.25},
                {"name": "rainfall_plus_50", "multiplier": 1.50},
                {"name": "rainfall_plus_100", "multiplier": 2.00},
                {"name": "rainfall_minus_10", "multiplier": 0.90},
                {"name": "rainfall_minus_25", "multiplier": 0.75},
            ]
        },
        "soil_moisture": {
            "scenarios": [
                {"name": "baseline", "multiplier": 1.0},
                {"name": "moisture_plus_10", "multiplier": 1.10},
                {"name": "moisture_plus_25", "multiplier": 1.25},
                {"name": "moisture_plus_50", "multiplier": 1.50},
                {"name": "moisture_minus_10", "multiplier": 0.90},
            ]
        },
        "combined": {
            "scenarios": [
                {
                    "name": "moderate_increase",
                    "rainfall_multiplier": 1.25,
                    "moisture_multiplier": 1.10,
                },
                {
                    "name": "severe_increase",
                    "rainfall_multiplier": 1.50,
                    "moisture_multiplier": 1.25,
                },
                {
                    "name": "extreme_event",
                    "rainfall_multiplier": 2.00,
                    "moisture_multiplier": 1.50,
                },
            ]
        },
        "sensitivity": {
            "parameter_grid_percent": [-25, -10, 0, 10, 25, 50, 75, 100]
        },
        "sampling": {"max_locations": 20, "observations_per_location": 5},
    }
}


def load_simulation_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads simulation configuration from YAML file with fallback to default parameters.

    Args:
        config_path: Path to simulation_config.yaml file.

    Returns:
        Dict[str, Any]: Validated simulation configuration dictionary.
    """
    if config_path is None:
        config_path = Path("config/simulation_config.yaml")

    if not config_path.exists():
        return DEFAULT_SIMULATION_CONFIG.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            if not isinstance(cfg, dict):
                return DEFAULT_SIMULATION_CONFIG.copy()
            return cfg
    except Exception:
        return DEFAULT_SIMULATION_CONFIG.copy()
