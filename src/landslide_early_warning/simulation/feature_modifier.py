"""
Environmental Feature Modifier and Physical Domain Boundary Engine.

Applies scenario multipliers to rainfall and soil moisture feature columns,
enforces physical non-negativity and saturation limits, and checks training domain boundaries.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


RAINFALL_FEATURES: List[str] = [
    "precipitation_1h",
    "precipitation_3h",
    "precipitation_6h",
    "precipitation_12h",
    "precipitation_24h",
    "precipitation_72h",
    "precipitation_168h",
    "precipitation_max_intensity_24h",
]

SOIL_MOISTURE_FEATURES: List[str] = [
    "soil_moisture_layer1_current",
    "soil_moisture_layer1_mean_24h",
    "soil_moisture_layer1_mean_72h",
    "soil_moisture_layer2_current",
    "soil_moisture_layer3_current",
]

# Historical training feature limits for domain extrapolation checks
TRAINING_DOMAIN_BOUNDS: Dict[str, Tuple[float, float]] = {
    "precipitation_24h": (0.0, 350.0),
    "precipitation_72h": (0.0, 600.0),
    "soil_moisture_layer1_current": (0.0, 0.75),
}


def modify_observation_features(
    baseline_obs: Dict[str, Any],
    rainfall_multiplier: float = 1.0,
    soil_moisture_multiplier: float = 1.0,
) -> Tuple[Dict[str, Any], Dict[str, Dict[str, float]], bool, List[str]]:
    """
    Applies scenario multipliers to baseline observation features safely.

    Args:
        baseline_obs: Original historical observation dictionary.
        rainfall_multiplier: Multiplier for rainfall features.
        soil_moisture_multiplier: Multiplier for soil moisture features.

    Returns:
        Tuple[Dict[str, Any], Dict[str, Dict[str, float]], bool, List[str]]:
            - Modified observation dictionary.
            - Modifications record dictionary.
            - is_extrapolation flag.
            - Domain warning messages list.
    """
    sim_obs = baseline_obs.copy()
    modifications: Dict[str, Dict[str, float]] = {}
    domain_warnings: List[str] = []
    is_extrapolation = False

    # 1. Modify Rainfall Features
    if rainfall_multiplier != 1.0:
        for fn in RAINFALL_FEATURES:
            if fn in sim_obs and pd.notna(sim_obs[fn]):
                orig_val = float(sim_obs[fn])
                sim_val = max(0.0, round(orig_val * rainfall_multiplier, 4))
                sim_obs[fn] = sim_val

                delta = round(sim_val - orig_val, 4)
                pct = round(((sim_val / orig_val) - 1.0) * 100.0, 2) if orig_val > 0 else 0.0

                modifications[fn] = {
                    "original_value": orig_val,
                    "scenario_value": sim_val,
                    "change_amount": delta,
                    "change_percent": pct,
                }

    # 2. Modify Soil Moisture Features
    if soil_moisture_multiplier != 1.0:
        for fn in SOIL_MOISTURE_FEATURES:
            if fn in sim_obs and pd.notna(sim_obs[fn]):
                orig_val = float(sim_obs[fn])
                # Physical saturation clamp [0.0, 0.95] m^3/m^3
                sim_val = max(0.0, min(0.95, round(orig_val * soil_moisture_multiplier, 4)))
                sim_obs[fn] = sim_val

                delta = round(sim_val - orig_val, 4)
                pct = round(((sim_val / orig_val) - 1.0) * 100.0, 2) if orig_val > 0 else 0.0

                modifications[fn] = {
                    "original_value": orig_val,
                    "scenario_value": sim_val,
                    "change_amount": delta,
                    "change_percent": pct,
                }

    # 3. Check Physical Domain Extrapolation Bounds
    for fn, (min_b, max_b) in TRAINING_DOMAIN_BOUNDS.items():
        if fn in sim_obs and pd.notna(sim_obs[fn]):
            val = float(sim_obs[fn])
            if val < min_b or val > max_b:
                is_extrapolation = True
                msg = f"Feature '{fn}' simulated value ({val:.2f}) exceeds historical training bounds [{min_b:.1f}, {max_b:.1f}]"
                domain_warnings.append(msg)

    return sim_obs, modifications, is_extrapolation, domain_warnings
