"""
Evaluation Configuration Loader Module.

Ingests and validates matching rules, actionable warning state lists,
spatial matching thresholds, and lead-time window parameters from config/evaluation_config.yaml.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml


DEFAULT_EVALUATION_CONFIG: Dict[str, Any] = {
    "evaluation": {
        "actionable_warning_states": ["WARNING", "HIGH_RISK"],
        "advisory_warning_states": ["WATCH"],
        "spatial": {"max_distance_km": 50.0},
        "temporal": {
            "pre_event_window_hours": 168.0,
            "post_warning_matching_hours": 168.0,
        },
        "matching": {
            "one_warning_per_event": True,
            "one_event_per_warning": True,
            "prefer_highest_warning_state": True,
            "prefer_shortest_distance": True,
        },
        "lead_time_buckets": {
            "less_than_1h": [0.0, 1.0],
            "hours_1_to_6": [1.0, 6.0],
            "hours_6_to_12": [6.0, 12.0],
            "hours_12_to_24": [12.0, 24.0],
            "days_1_to_3": [24.0, 72.0],
            "days_3_to_7": [72.0, 168.0],
        },
    }
}


def load_evaluation_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Loads evaluation configuration from YAML file with fallback to default parameters.

    Args:
        config_path: Path to evaluation_config.yaml file.

    Returns:
        Dict[str, Any]: Validated evaluation configuration dictionary.
    """
    if config_path is None:
        config_path = Path("config/evaluation_config.yaml")

    if not config_path.exists():
        return DEFAULT_EVALUATION_CONFIG.copy()

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            if not isinstance(cfg, dict):
                return DEFAULT_EVALUATION_CONFIG.copy()
            return cfg
    except Exception:
        return DEFAULT_EVALUATION_CONFIG.copy()
