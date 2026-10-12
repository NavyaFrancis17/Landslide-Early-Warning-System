"""
Pairwise Scenario Comparison and State Transition Module.

Calculates risk probability deltas, percentage changes, warning state transition types,
and anomaly Z-score shifts between baseline and simulated scenario outcomes.
"""

from typing import Any, Dict


def compare_baseline_and_scenario(
    baseline_result: Dict[str, Any],
    scenario_result: Dict[str, Any],
    scenario_meta: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compares baseline and scenario prediction outputs.

    Args:
        baseline_result: Output dict from baseline inference.
        scenario_result: Output dict from scenario inference.
        scenario_meta: Metadata dict for the scenario (name, multipliers).

    Returns:
        Dict[str, Any]: Structured comparison dictionary.
    """
    base_p = float(baseline_result["risk_probability"])
    scen_p = float(scenario_result["risk_probability"])

    delta_p = round(scen_p - base_p, 4)
    pct_change_p = round(((scen_p / base_p) - 1.0) * 100.0, 2) if base_p > 0 else 0.0

    base_st = str(baseline_result["warning_state"])
    scen_st = str(scenario_result["warning_state"])

    st_changed = base_st != scen_st
    transition_type = f"{base_st}_TO_{scen_st}" if st_changed else "NO_CHANGE"

    base_z = float(baseline_result.get("anomaly_z_score", 0.0))
    scen_z = float(scenario_result.get("anomaly_z_score", 0.0))
    delta_z = round(scen_z - base_z, 2)

    return {
        "scenario_name": scenario_meta.get("scenario_name", "custom"),
        "category": scenario_meta.get("category", "CUSTOM"),
        "rainfall_multiplier": scenario_meta.get("rainfall_multiplier", 1.0),
        "soil_moisture_multiplier": scenario_meta.get("soil_moisture_multiplier", 1.0),
        "baseline_risk_probability": base_p,
        "scenario_risk_probability": scen_p,
        "risk_probability_change": delta_p,
        "risk_probability_change_percent": pct_change_p,
        "baseline_warning_state": base_st,
        "scenario_warning_state": scen_st,
        "warning_state_changed": st_changed,
        "transition_type": transition_type,
        "baseline_anomaly_z": base_z,
        "scenario_anomaly_z": scen_z,
        "anomaly_z_change": delta_z,
        "baseline_anomaly_state": baseline_result.get("anomaly_state", "NORMAL"),
        "scenario_anomaly_state": scenario_result.get("anomaly_state", "NORMAL"),
    }
