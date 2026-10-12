"""
Early-Warning Configuration Loader Module.

Ingests and validates warning thresholds, persistence limits, risk trend parameters,
and location-adaptive abnormality cutoffs from config/warning_config.yaml.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml


DEFAULT_WARNING_CONFIG: Dict[str, Any] = {
    "risk_states": {
        "NORMAL": {"min_probability": 0.00, "max_probability": 0.35},
        "WATCH": {"min_probability": 0.35, "max_probability": 0.60},
        "WARNING": {"min_probability": 0.60, "max_probability": 0.80},
        "HIGH_RISK": {"min_probability": 0.80, "max_probability": 1.00},
    },
    "persistence": {
        "minimum_warning_persistence_observations": 2,
        "minimum_high_risk_persistence_observations": 3,
        "deescalation_consecutive_low_observations": 2,
    },
    "trend": {
        "trend_window_size": 3,
        "increasing_delta_threshold": 0.05,
        "decreasing_delta_threshold": -0.05,
    },
    "abnormality": {
        "abnormal_z_threshold": 1.5,
        "strongly_abnormal_z_threshold": 2.5,
    },
    "hysteresis": {
        "escalation_margin": 0.02,
        "deescalation_margin": 0.03,
    },
}


def load_warning_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads warning configuration from YAML file with fallback to default parameters.

    Args:
        config_path: Path to warning_config.yaml file.

    Returns:
        Dict[str, Any]: Validated warning configuration dictionary.
    """
    if config_path is None:
        config_path = Path("config/warning_config.yaml")

    if not config_path.exists():
        return DEFAULT_WARNING_CONFIG.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            if not isinstance(cfg, dict):
                return DEFAULT_WARNING_CONFIG.copy()
            return cfg
    except Exception:
        return DEFAULT_WARNING_CONFIG.copy()
