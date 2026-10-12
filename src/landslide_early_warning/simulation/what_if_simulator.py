"""
Master What-If Simulator Module.

Orchestrates counterfactual environmental feature modification, model inference,
Phase 5 warning engine prediction, pairwise baseline comparison, and sensitivity analysis.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from landslide_early_warning.simulation.feature_modifier import modify_observation_features
from landslide_early_warning.simulation.scenario_comparator import compare_baseline_and_scenario
from landslide_early_warning.simulation.scenario_config import load_simulation_config
from landslide_early_warning.simulation.scenario_generator import generate_simulation_scenarios
from landslide_early_warning.simulation.scenario_runner import run_scenario_inference
from landslide_early_warning.simulation.simulation_metrics import aggregate_simulation_summary_metrics
from landslide_early_warning.simulation.simulation_report import generate_scenario_explanation_text
from landslide_early_warning.warning.warning_engine import EarlyWarningEngine


class WhatIfSimulator:
    """Master What-If Environmental Scenario Simulator."""

    def __init__(
        self,
        warning_engine: EarlyWarningEngine,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.warning_engine = warning_engine
        self.config = config if config is not None else load_simulation_config()

    @classmethod
    def load_from_saved_models(
        cls,
        models_dir: Path = Path("models/saved"),
        config_path: Optional[Path] = None,
    ) -> "WhatIfSimulator":
        """Factory method instantiating simulator using saved pre-trained model artifacts."""
        engine = EarlyWarningEngine.load_from_saved_models(models_dir=models_dir)
        config = load_simulation_config(config_path)
        return cls(warning_engine=engine, config=config)

    def simulate_scenario(
        self,
        input_observation: Dict[str, Any],
        scenario: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Runs single scenario simulation for one environmental observation.

        Args:
            input_observation: Original historical baseline observation dictionary.
            scenario: Scenario definition dictionary (rainfall_multiplier, soil_moisture_multiplier).

        Returns:
            Dict[str, Any]: Structured simulation result dictionary.
        """
        rf_m = float(scenario.get("rainfall_multiplier", 1.0))
        sm_m = float(scenario.get("soil_moisture_multiplier", 1.0))

        # 1. Baseline Inference
        base_res = run_scenario_inference(input_observation, self.warning_engine)

        # 2. Modify Features & Domain Boundary Check
        sim_obs, mods, is_extrap, domain_warns = modify_observation_features(
            input_observation,
            rainfall_multiplier=rf_m,
            soil_moisture_multiplier=sm_m,
        )

        # 3. Scenario Inference
        scen_res = run_scenario_inference(sim_obs, self.warning_engine)

        # 4. Pairwise Comparison
        comp_res = compare_baseline_and_scenario(base_res, scen_res, scenario)

        # 5. Generate Explanation Text
        explanation = generate_scenario_explanation_text(
            scenario_name=scenario.get("scenario_name", "custom"),
            baseline_p=base_res["risk_probability"],
            scenario_p=scen_res["risk_probability"],
            baseline_state=base_res["warning_state"],
            scenario_state=scen_res["warning_state"],
            is_extrapolation=is_extrap,
        )

        return {
            "baseline_observation": input_observation,
            "simulated_observation": sim_obs,
            "modifications": mods,
            "baseline_result": base_res,
            "scenario_result": scen_res,
            "comparison": comp_res,
            "is_extrapolation": is_extrap,
            "domain_warnings": domain_warns,
            "explanation": explanation,
        }

    def run_sensitivity_grid(
        self,
        baseline_obs: Dict[str, Any],
        parameter: str = "rainfall",
        grid_percents: Optional[List[float]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Runs controlled parameter change grid for sensitivity curves.
        """
        if grid_percents is None:
            grid_percents = [-25.0, -10.0, 0.0, 10.0, 25.0, 50.0, 75.0, 100.0]

        results = []
        for pct in grid_percents:
            mult = 1.0 + (pct / 100.0)
            scen = {
                "scenario_name": f"{parameter}_grid_{pct:+.0f}pct",
                "category": f"SENSITIVITY_{parameter.upper()}",
                "rainfall_multiplier": mult if parameter == "rainfall" else 1.0,
                "soil_moisture_multiplier": mult if parameter == "soil_moisture" else 1.0,
            }
            res = self.simulate_scenario(baseline_obs, scen)
            results.append({
                "parameter": parameter,
                "change_percent": pct,
                "multiplier": mult,
                "risk_probability": res["scenario_result"]["risk_probability"],
                "warning_state": res["scenario_result"]["warning_state"],
                "is_extrapolation": res["is_extrapolation"],
            })
        return results

    def run_batch_scenarios(
        self,
        observations_df: pd.DataFrame,
        scenarios_list: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Runs batch simulations across multiple historical observations.
        """
        if scenarios_list is None:
            scenarios_list = generate_simulation_scenarios(self.config)

        all_results = []
        all_comparisons = []
        extrap_flags = []

        for idx, row in observations_df.iterrows():
            obs_dict = row.to_dict()
            for scen in scenarios_list:
                res = self.simulate_scenario(obs_dict, scen)
                all_results.append(res)
                all_comparisons.append(res["comparison"])
                extrap_flags.append(res["is_extrapolation"])

        summary_metrics = aggregate_simulation_summary_metrics(all_comparisons, extrap_flags)

        return {
            "all_results": all_results,
            "all_comparisons": all_comparisons,
            "summary_metrics": summary_metrics,
        }
