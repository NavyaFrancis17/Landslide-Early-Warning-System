"""
Scenario Definition Generator Module.

Generates structured simulation scenario objects for single-variable rainfall changes,
soil moisture changes, combined environmental scenarios, and fine-grained sensitivity grids.
"""

from typing import Any, Dict, List, Optional
from landslide_early_warning.simulation.scenario_config import load_simulation_config


def generate_simulation_scenarios(
    config: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    Generates list of simulation scenario definition dictionaries.

    Args:
        config: Optional simulation configuration dictionary.

    Returns:
        List[Dict[str, Any]]: List of scenario definitions.
    """
    if config is None:
        config = load_simulation_config()

    sim_cfg = config.get("simulation", {})
    scenarios: List[Dict[str, Any]] = []

    # 1. Baseline Scenario
    scenarios.append({
        "scenario_name": "baseline",
        "category": "BASELINE",
        "description": "Unmodified historical environmental baseline observation",
        "rainfall_multiplier": 1.0,
        "soil_moisture_multiplier": 1.0,
    })

    # 2. Rainfall Scenarios
    rf_list = sim_cfg.get("rainfall", {}).get("scenarios", [])
    for r in rf_list:
        name = r["name"]
        mult = float(r["multiplier"])
        if name != "baseline":
            pct = round((mult - 1.0) * 100.0, 1)
            sign_str = f"+{pct:.0f}%" if pct > 0 else f"{pct:.0f}%"
            scenarios.append({
                "scenario_name": name,
                "category": "RAINFALL",
                "description": f"Rainfall modified by {sign_str}",
                "rainfall_multiplier": mult,
                "soil_moisture_multiplier": 1.0,
            })

    # 3. Soil Moisture Scenarios
    sm_list = sim_cfg.get("soil_moisture", {}).get("scenarios", [])
    for s in sm_list:
        name = s["name"]
        mult = float(s["multiplier"])
        if name != "baseline":
            pct = round((mult - 1.0) * 100.0, 1)
            sign_str = f"+{pct:.0f}%" if pct > 0 else f"{pct:.0f}%"
            scenarios.append({
                "scenario_name": name,
                "category": "SOIL_MOISTURE",
                "description": f"Topsoil moisture modified by {sign_str}",
                "rainfall_multiplier": 1.0,
                "soil_moisture_multiplier": mult,
            })

    # 4. Combined Scenarios
    comb_list = sim_cfg.get("combined", {}).get("scenarios", [])
    for c in comb_list:
        name = c["name"]
        rf_m = float(c["rainfall_multiplier"])
        sm_m = float(c["moisture_multiplier"])
        rf_pct = round((rf_m - 1.0) * 100.0, 1)
        sm_pct = round((sm_m - 1.0) * 100.0, 1)
        scenarios.append({
            "scenario_name": f"combined_{name}",
            "category": "COMBINED",
            "description": f"Combined rainfall +{rf_pct:.0f}% and soil moisture +{sm_pct:.0f}%",
            "rainfall_multiplier": rf_m,
            "soil_moisture_multiplier": sm_m,
        })

    return scenarios
