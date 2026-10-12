"""
Simulation Statistical Metrics Aggregator Module.

Aggregates summary statistics across batch scenario simulation runs,
computing mean/median risk changes, state transition counts, and domain boundary flags.
"""

from typing import Any, Dict, List
import numpy as np
import pandas as pd


def aggregate_simulation_summary_metrics(
    comparison_results_list: List[Dict[str, Any]],
    extrapolation_flags_list: List[bool],
) -> Dict[str, Any]:
    """
    Computes statistical summary across all scenario run comparisons.

    Args:
        comparison_results_list: List of comparison result dictionaries.
        extrapolation_flags_list: List of extrapolation booleans per run.

    Returns:
        Dict[str, Any]: Summary metrics dictionary.
    """
    if not comparison_results_list:
        return {
            "total_simulations_evaluated": 0,
            "mean_risk_probability_change": 0.0,
            "median_risk_probability_change": 0.0,
            "max_risk_increase": 0.0,
            "min_risk_change": 0.0,
            "total_warning_state_transitions": 0,
            "transition_breakdown": {},
            "in_domain_scenarios_count": 0,
            "extrapolation_scenarios_count": 0,
            "extrapolation_percentage": 0.0,
        }

    deltas = [float(c["risk_probability_change"]) for c in comparison_results_list]
    transitions = [c["transition_type"] for c in comparison_results_list if c["warning_state_changed"]]

    trans_breakdown: Dict[str, int] = {}
    for t in transitions:
        trans_breakdown[t] = trans_breakdown.get(t, 0) + 1

    extrap_cnt = sum(1 for e in extrapolation_flags_list if e)
    in_dom_cnt = len(extrapolation_flags_list) - extrap_cnt
    extrap_pct = round((extrap_cnt / len(extrapolation_flags_list)) * 100.0, 2) if extrapolation_flags_list else 0.0

    return {
        "total_simulations_evaluated": len(comparison_results_list),
        "mean_risk_probability_change": round(float(np.mean(deltas)), 4),
        "median_risk_probability_change": round(float(np.median(deltas)), 4),
        "max_risk_increase": round(float(np.max(deltas)), 4),
        "min_risk_change": round(float(np.min(deltas)), 4),
        "total_warning_state_transitions": len(transitions),
        "transition_breakdown": trans_breakdown,
        "in_domain_scenarios_count": in_dom_cnt,
        "extrapolation_scenarios_count": extrap_cnt,
        "extrapolation_percentage": extrap_pct,
    }
