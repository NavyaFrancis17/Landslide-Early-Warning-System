"""
Probabilistic Risk State Mapper Module.

Converts continuous model probability outputs P(Landslide) into 4 discrete warning alert levels:
- NORMAL (Low hazard probability)
- WATCH (Moderate environmental forcing)
- WARNING (Elevated slope instability risk)
- HIGH_RISK (Severe imminent landslide hazard)
"""

from typing import Dict, List, Optional, Union
import numpy as np


DEFAULT_WARNING_THRESHOLDS: Dict[str, float] = {
    "watch_threshold": 0.35,
    "warning_threshold": 0.60,
    "high_risk_threshold": 0.80,
}


def map_probability_to_risk_state(
    probability: float,
    thresholds: Optional[Dict[str, float]] = None,
) -> str:
    """
    Maps a single predicted probability P(Landslide) to a discrete warning state.

    Args:
        probability: Continuous risk probability in range [0.0, 1.0].
        thresholds: Configured alert thresholds dictionary.

    Returns:
        str: Warning state label ('NORMAL', 'WATCH', 'WARNING', 'HIGH_RISK').
    """
    p = float(probability)
    if thresholds is None:
        thresholds = DEFAULT_WARNING_THRESHOLDS

    watch_th = thresholds.get("watch_threshold", 0.35)
    warn_th = thresholds.get("warning_threshold", 0.60)
    high_th = thresholds.get("high_risk_threshold", 0.80)

    if p >= high_th:
        return "HIGH_RISK"
    elif p >= warn_th:
        return "WARNING"
    elif p >= watch_th:
        return "WATCH"
    else:
        return "NORMAL"


def batch_map_probabilities_to_risk_states(
    probabilities: Union[np.ndarray, List[float]],
    thresholds: Optional[Dict[str, float]] = None,
) -> List[str]:
    """Batch maps an array of probabilities to discrete risk state strings."""
    return [map_probability_to_risk_state(p, thresholds) for p in probabilities]
