"""
Temporal Warning State Persistence and De-Escalation Engine.

Enforces minimum observation persistence requirements before state escalation,
maintains warning locks, and controls de-escalation transition rates.
"""

from typing import Any, Dict, List


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


def apply_warning_state_persistence(
    raw_states_history: List[str],
    current_raw_state: str,
    min_warning_persistence: int = 2,
    min_high_risk_persistence: int = 3,
    deescalation_low_obs: int = 2,
) -> Dict[str, Any]:
    """
    Applies persistence and hysteresis logic over chronological warning state history.

    Args:
        raw_states_history: Chronological list of un-persisted mapped warning states.
        current_raw_state: Current raw un-persisted mapped warning state.
        min_warning_persistence: Required consecutive observations for WARNING.
        min_high_risk_persistence: Required consecutive observations for HIGH_RISK.
        deescalation_low_obs: Required consecutive low observations before de-escalation.

    Returns:
        Dict[str, Any]: Persisted warning state evaluation dictionary.
    """
    if not raw_states_history:
        return {
            "raw_state": current_raw_state,
            "persisted_state": current_raw_state,
            "consecutive_elevated_count": 0,
            "consecutive_low_count": 0,
            "persistence_lock_active": False,
        }

    raw_rank = STATE_RANKS.get(current_raw_state, 0)

    # Count consecutive observations >= current raw rank
    consecutive_elevated = 0
    for s in reversed(raw_states_history):
        if STATE_RANKS.get(s, 0) >= raw_rank and raw_rank > 0:
            consecutive_elevated += 1
        else:
            break

    # Count consecutive low observations (NORMAL)
    consecutive_low = 0
    for s in reversed(raw_states_history):
        if STATE_RANKS.get(s, 0) == 0:
            consecutive_low += 1
        else:
            break

    # Escalation gating
    persisted_rank = raw_rank
    if raw_rank == 3:  # HIGH_RISK
        if consecutive_elevated < min_high_risk_persistence:
            persisted_rank = 2  # Hold at WARNING until 3 consecutive HIGH_RISK observations
    elif raw_rank == 2:  # WARNING
        if consecutive_elevated < min_warning_persistence:
            persisted_rank = 1  # Hold at WATCH until 2 consecutive WARNING observations

    # De-escalation hold check
    prev_persisted_rank = STATE_RANKS.get(raw_states_history[-2], 0) if len(raw_states_history) >= 2 else raw_rank
    if prev_persisted_rank > raw_rank:
        if consecutive_low < deescalation_low_obs:
            # Hold previous rank during de-escalation transition
            persisted_rank = max(raw_rank, prev_persisted_rank - 1)

    persisted_state = RANK_TO_STATE[persisted_rank]

    return {
        "raw_state": current_raw_state,
        "persisted_state": persisted_state,
        "consecutive_elevated_count": consecutive_elevated,
        "consecutive_low_count": consecutive_low,
        "persistence_lock_active": persisted_rank != raw_rank,
    }
