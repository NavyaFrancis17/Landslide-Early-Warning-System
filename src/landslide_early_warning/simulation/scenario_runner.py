"""
Scenario Inference Execution Module.

Runs modified observation feature vectors through the fitted preprocessing pipeline,
trained machine learning risk model, and Phase 5 EarlyWarningEngine.
"""

from typing import Any, Dict, Optional
import numpy as np
import pandas as pd

from landslide_early_warning.warning.warning_engine import EarlyWarningEngine


def run_scenario_inference(
    simulated_obs: Dict[str, Any],
    warning_engine: EarlyWarningEngine,
) -> Dict[str, Any]:
    """
    Executes model inference and warning state prediction for a simulated observation.

    Args:
        simulated_obs: Modified observation dictionary.
        warning_engine: Loaded EarlyWarningEngine instance.

    Returns:
        Dict[str, Any]: Simulated prediction output dictionary.
    """
    res = warning_engine.predict_warning(simulated_obs)

    return {
        "risk_probability": res["risk_probability"],
        "warning_state": res["current_warning_state"],
        "raw_warning_state": res["raw_warning_state"],
        "risk_trend": res["risk_trend"],
        "anomaly_state": res["anomaly_state"],
        "anomaly_z_score": res["anomaly_z_score"],
        "warning_reason": res["warning_reason"],
    }
