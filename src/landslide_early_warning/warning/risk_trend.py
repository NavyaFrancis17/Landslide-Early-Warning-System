"""
Temporal Risk Trend Trajectory Module.

Calculates short-term rolling risk trends (INCREASING, STABLE, DECREASING),
delta probabilities, and consecutive rising observation sequences.
"""

from typing import Any, Dict, List
import numpy as np


def compute_temporal_risk_trend(
    history_probabilities: List[float],
    window_size: int = 3,
    increasing_delta_th: float = 0.05,
    decreasing_delta_th: float = -0.05,
) -> Dict[str, Any]:
    """
    Computes risk trend trajectory metrics over a chronological window of probabilities.

    Args:
        history_probabilities: List of probabilities [R_0, ..., R_t].
        window_size: Sliding window size.
        increasing_delta_th: Delta threshold for INCREASING trend.
        decreasing_delta_th: Delta threshold for DECREASING trend.

    Returns:
        Dict[str, Any]: Trend metrics dictionary.
    """
    if not history_probabilities:
        return {
            "current_probability": 0.0,
            "previous_probability": 0.0,
            "trend_delta": 0.0,
            "rolling_mean_probability": 0.0,
            "risk_trend": "STABLE",
            "consecutive_increasing_count": 0,
        }

    probs = [float(p) for p in history_probabilities]
    curr_p = probs[-1]
    prev_p = probs[-2] if len(probs) >= 2 else curr_p
    delta = round(curr_p - prev_p, 4)

    recent_window = probs[-min(len(probs), window_size):]
    rolling_mean = round(float(np.mean(recent_window)), 4)

    if delta >= increasing_delta_th:
        trend = "INCREASING"
    elif delta <= decreasing_delta_th:
        trend = "DECREASING"
    else:
        trend = "STABLE"

    # Consecutive increasing observation count
    inc_cnt = 0
    for i in range(len(probs) - 1, 0, -1):
        if probs[i] - probs[i - 1] > 0.01:
            inc_cnt += 1
        else:
            break

    return {
        "current_probability": round(curr_p, 4),
        "previous_probability": round(prev_p, 4),
        "trend_delta": delta,
        "rolling_mean_probability": rolling_mean,
        "risk_trend": trend,
        "consecutive_increasing_count": inc_cnt,
    }
