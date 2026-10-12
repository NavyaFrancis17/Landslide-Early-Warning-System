"""
Simulation Report and Explanation Generator Module.

Exports simulation CSV datasets, JSON payload metadata, human-readable explanations,
and academic Markdown documentation files.
"""

import json
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd


def generate_scenario_explanation_text(
    scenario_name: str,
    baseline_p: float,
    scenario_p: float,
    baseline_state: str,
    scenario_state: str,
    is_extrapolation: bool,
) -> str:
    """Generates human-readable scenario explanation text."""
    delta = scenario_p - baseline_p
    direction = "increased" if delta > 0 else ("decreased" if delta < 0 else "remained unchanged")

    state_msg = (
        f"The warning state escalated from {baseline_state} to {scenario_state}."
        if scenario_state != baseline_state
        else f"The warning state remained at {baseline_state}."
    )

    domain_msg = (
        "The simulated environmental parameters represent model extrapolation outside training bounds."
        if is_extrapolation
        else "The simulated environmental parameters remained within observed historical bounds."
    )

    return (
        f"Under the simulated '{scenario_name}' scenario, predicted landslide risk probability {direction} "
        f"from {baseline_p:.2f} to {scenario_p:.2f} ({delta:+.2f}). {state_msg} {domain_msg}"
    )


def export_simulation_deliverables(
    results_df: pd.DataFrame,
    comparison_df: pd.DataFrame,
    transitions_df: pd.DataFrame,
    sensitivity_df: pd.DataFrame,
    summary_json_payload: Dict[str, Any],
    output_dir: Path = Path("results/simulation"),
) -> None:
    """Exports CSV and JSON deliverables under results/simulation/."""
    output_dir.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(output_dir / "scenario_results.csv", index=False)
    comparison_df.to_csv(output_dir / "scenario_comparison.csv", index=False)
    transitions_df.to_csv(output_dir / "warning_state_transitions.csv", index=False)
    sensitivity_df.to_csv(output_dir / "sensitivity_analysis.csv", index=False)

    with open(output_dir / "simulation_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary_json_payload, f, indent=2)
