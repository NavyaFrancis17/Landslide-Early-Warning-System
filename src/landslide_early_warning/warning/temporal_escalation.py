"""
Temporal Risk Trajectory and Alert Escalation Logic Engine.

Analyzes sequential risk probability trends over time to manage warning state escalation,
consecutive high-risk observation tracking, and de-escalation transitions.
"""

from typing import Any, Dict, List
import pandas as pd

from landslide_early_warning.warning.risk_state_mapper import map_probability_to_risk_state


STATE_RANKS: Dict[str, int] = {
    "NORMAL": 0,
    "WATCH": 1,
    "WARNING": 2,
    "HIGH_RISK": 3,
}

RANK_TO_STATE: Dict[int, str] = {
    0: "NORMAL",
    1: "WATCH",
    2: "WARNING",
    3: "HIGH_RISK",
}


def evaluate_temporal_risk_trajectory(
    risk_probabilities: List[float],
    escalation_sensitivity: float = 0.05,
    thresholds: Dict[str, float] = None,
) -> Dict[str, Any]:
    """
    Evaluates sequential risk probability series for a location to track risk trajectory and escalation.

    Args:
        risk_probabilities: Chronologically ordered list of risk probabilities [R_0, R_1, ..., R_t].
        escalation_sensitivity: Risk trend delta sensitivity threshold.
        thresholds: Alert mapping thresholds.

    Returns:
        Dict[str, Any]: Trajectory summary report.
    """
    if not risk_probabilities:
        return {
            "current_risk_probability": 0.0,
            "current_risk_state": "NORMAL",
            "escalated_risk_state": "NORMAL",
            "consecutive_high_risk_count": 0,
            "risk_trend_delta": 0.0,
            "escalation_event_triggered": False,
        }

    raw_states = [map_probability_to_risk_state(p, thresholds) for p in risk_probabilities]

    current_prob = float(risk_probabilities[-1])
    current_state = raw_states[-1]

    # Calculate trend delta (R_t - R_{t-1})
    prev_prob = float(risk_probabilities[-2]) if len(risk_probabilities) >= 2 else current_prob
    trend_delta = round(current_prob - prev_prob, 4)

    # Count consecutive elevated/high risk observations
    consecutive_high_cnt = 0
    for s in reversed(raw_states):
        if s in ["WARNING", "HIGH_RISK"]:
            consecutive_high_cnt += 1
        else:
            break

    # Escalation / De-escalation rule logic
    current_rank = STATE_RANKS[current_state]
    escalated_rank = current_rank

    if trend_delta >= escalation_sensitivity and consecutive_high_cnt >= 2:
        # Escalate warning level by +1 step
        escalated_rank = min(3, current_rank + 1)
    elif trend_delta <= -escalation_sensitivity and consecutive_high_cnt == 0:
        # De-escalate warning level by -1 step
        escalated_rank = max(0, current_rank - 1)

    escalated_state = RANK_TO_STATE[escalated_rank]

    return {
        "current_risk_probability": round(current_prob, 4),
        "previous_risk_probability": round(prev_prob, 4),
        "risk_trend_delta": trend_delta,
        "current_raw_risk_state": current_state,
        "escalated_risk_state": escalated_state,
        "consecutive_high_risk_count": consecutive_high_cnt,
        "escalation_event_triggered": escalated_rank > current_rank,
        "deescalation_event_triggered": escalated_rank < current_rank,
    }
