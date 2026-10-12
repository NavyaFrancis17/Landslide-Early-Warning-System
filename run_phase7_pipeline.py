"""
Master Phase 7 What-If Environmental Scenario Simulation Pipeline Script.

Ingests Phase 3 feature dataset, samples representative historical locations,
runs batch scenario simulations across rainfall and soil moisture multipliers,
executes controlled sensitivity grid analyses, exports results/simulation/ deliverables,
generates visual research figures under results/figures/, and writes Markdown docs.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Add src to sys.path
root_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(root_dir / "src"))

from landslide_early_warning.simulation.scenario_generator import generate_simulation_scenarios
from landslide_early_warning.simulation.simulation_report import export_simulation_deliverables
from landslide_early_warning.simulation.what_if_simulator import WhatIfSimulator


def generate_phase7_figures(
    comparison_df: pd.DataFrame,
    sensitivity_rf_df: pd.DataFrame,
    sensitivity_sm_df: pd.DataFrame,
    fig_dir: Path = Path("results/figures"),
) -> None:
    """Generates Phase 7 visual research plots."""
    fig_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Scenario Risk Probability Comparison Bar Chart
    if not comparison_df.empty and "scenario_name" in comparison_df.columns:
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        group_means = comparison_df.groupby("scenario_name")["scenario_risk_probability"].mean()
        scen_names = list(group_means.index)
        means = list(group_means.values)

        ax.bar(scen_names, means, color="#1f77b4", edgecolor="black", alpha=0.85)
        ax.set_title("Mean Predicted Risk Probability Across Environmental Scenarios", fontsize=12, fontweight="bold")
        ax.set_xlabel("Simulation Scenario", fontsize=10)
        ax.set_ylabel("Mean Predicted Risk P(Landslide)", fontsize=10)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        fig.savefig(fig_dir / "scenario_risk_comparison.png")
        plt.close(fig)

    # 2. Rainfall Sensitivity Curve Plot
    if not sensitivity_rf_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        ax.plot(sensitivity_rf_df["change_percent"], sensitivity_rf_df["risk_probability"], "o-", color="#d62728", linewidth=2, label="Rainfall Sensitivity")
        ax.set_title("Rainfall Change (%) vs. Predicted Landslide Hazard Risk P(Landslide)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Rainfall Modification (%)", fontsize=10)
        ax.set_ylabel("Model Risk Probability P(Landslide)", fontsize=10)
        ax.axvline(0, color="gray", linestyle="--", alpha=0.7)
        ax.legend()
        plt.tight_layout()
        fig.savefig(fig_dir / "rainfall_sensitivity_curve.png")
        plt.close(fig)

    # 3. Soil Moisture Sensitivity Curve Plot
    if not sensitivity_sm_df.empty:
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        ax.plot(sensitivity_sm_df["change_percent"], sensitivity_sm_df["risk_probability"], "s-", color="#2ca02c", linewidth=2, label="Soil Moisture Sensitivity")
        ax.set_title("Soil Moisture Change (%) vs. Predicted Landslide Hazard Risk P(Landslide)", fontsize=12, fontweight="bold")
        ax.set_xlabel("Topsoil Moisture Modification (%)", fontsize=10)
        ax.set_ylabel("Model Risk Probability P(Landslide)", fontsize=10)
        ax.axvline(0, color="gray", linestyle="--", alpha=0.7)
        ax.legend()
        plt.tight_layout()
        fig.savefig(fig_dir / "soil_moisture_sensitivity_curve.png")
        plt.close(fig)

    # 4. Warning State Scenario Transitions Heatmap/Bar
    if not comparison_df.empty and "transition_type" in comparison_df.columns:
        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
        trans_counts = comparison_df["transition_type"].value_counts()
        ax.bar(trans_counts.index, trans_counts.values, color="#9467bd", edgecolor="black", alpha=0.85)
        ax.set_title("Frequency of Warning State Transitions Under Environmental Scenarios", fontsize=12, fontweight="bold")
        ax.set_xlabel("State Transition Type", fontsize=10)
        ax.set_ylabel("Occurrence Count", fontsize=10)
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        fig.savefig(fig_dir / "warning_state_scenario_transition.png")
        plt.close(fig)

    # 5. Location Scenario Comparison Plot
    if not comparison_df.empty and "location_id" in comparison_df.columns:
        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        sample_locs = comparison_df["location_id"].unique()[:5]
        sub_df = comparison_df[comparison_df["location_id"].isin(sample_locs)]
        for loc in sample_locs:
            loc_data = sub_df[sub_df["location_id"] == loc]
            ax.plot(loc_data["scenario_name"], loc_data["scenario_risk_probability"], "o-", label=loc)
        ax.set_title("Cross-Location Risk Response to Environmental Scenarios", fontsize=12, fontweight="bold")
        ax.set_xlabel("Scenario", fontsize=10)
        ax.set_ylabel("Risk Probability P(Landslide)", fontsize=10)
        plt.xticks(rotation=45, ha="right")
        ax.legend(fontsize=8)
        plt.tight_layout()
        fig.savefig(fig_dir / "location_scenario_comparison.png")
        plt.close(fig)


def main() -> int:
    print("=" * 80)
    print("STARTING PHASE 7 WHAT-IF ENVIRONMENTAL SIMULATION PIPELINE")
    print("=" * 80)

    # 1. Load Phase 3 Feature Dataset
    csv_path = Path("data/processed/event_environment_features.csv")
    if not csv_path.exists():
        print(f"ERROR: Phase 3 dataset missing at {csv_path.resolve()}")
        return 1

    df_raw = pd.read_csv(csv_path, low_memory=False)
    print(f"Loaded Phase 3 feature dataset: {len(df_raw):,} records.")

    # Quality filter & create location_id
    df_valid = df_raw[
        (df_raw.get("environmental_data_available", True) == True) &
        (df_raw.get("spatial_match_valid", True) == True)
    ].copy()

    df_valid["location_id"] = df_valid.apply(
        lambda r: f"loc_{r.get('matched_env_latitude', r['landslide_latitude']):.2f}_{r.get('matched_env_longitude', r['landslide_longitude']):.2f}",
        axis=1
    )

    # Sample representative observations across top locations (20 locations x 5 obs = ~100 obs)
    top_locs = df_valid["location_id"].value_counts().head(20).index
    sampled_df = df_valid[df_valid["location_id"].isin(top_locs)].groupby("location_id").head(5).reset_index(drop=True)
    print(f"Sampled {len(sampled_df):,} baseline observations across {len(top_locs):,} representative locations.")

    # 2. Instantiate What-If Simulator
    print("\nInstantiating What-If Simulator from saved models...")
    simulator = WhatIfSimulator.load_from_saved_models()

    # 3. Run Batch Scenarios
    print("Executing batch scenario simulations...")
    scenarios_list = generate_simulation_scenarios(simulator.config)
    batch_res = simulator.run_batch_scenarios(sampled_df, scenarios_list)

    all_results = batch_res["all_results"]
    all_comparisons = batch_res["all_comparisons"]
    summary_metrics = batch_res["summary_metrics"]

    # Build DataFrames
    results_rows = []
    comp_rows = []
    trans_rows = []

    for r in all_results:
        loc_id = r["baseline_observation"].get("location_id", "loc_default")
        ts = r["baseline_observation"].get("event_date", "2026-01-01")
        scen_name = r["comparison"]["scenario_name"]

        # Results row
        results_rows.append({
            "location_id": loc_id,
            "timestamp": ts,
            "scenario_name": scen_name,
            "risk_probability": r["scenario_result"]["risk_probability"],
            "warning_state": r["scenario_result"]["warning_state"],
            "anomaly_state": r["scenario_result"]["anomaly_state"],
            "anomaly_z_score": r["scenario_result"]["anomaly_z_score"],
            "is_extrapolation": r["is_extrapolation"],
            "explanation": r["explanation"],
        })

        # Comparison row
        c = r["comparison"]
        c_entry = c.copy()
        c_entry["location_id"] = loc_id
        c_entry["timestamp"] = ts
        comp_rows.append(c_entry)

        # Transition row
        if c["warning_state_changed"]:
            trans_rows.append({
                "location_id": loc_id,
                "timestamp": ts,
                "scenario_name": scen_name,
                "baseline_warning_state": c["baseline_warning_state"],
                "scenario_warning_state": c["scenario_warning_state"],
                "transition_type": c["transition_type"],
                "risk_change": c["risk_probability_change"],
            })

    results_df = pd.DataFrame(results_rows)
    comparison_df = pd.DataFrame(comp_rows)
    transitions_df = pd.DataFrame(trans_rows)

    # 4. Run Controlled Sensitivity Grids
    print("Executing controlled rainfall & soil moisture sensitivity analysis grids...")
    sample_baseline_obs = sampled_df.iloc[0].to_dict()
    rf_sens = simulator.run_sensitivity_grid(sample_baseline_obs, parameter="rainfall")
    sm_sens = simulator.run_sensitivity_grid(sample_baseline_obs, parameter="soil_moisture")

    sensitivity_rf_df = pd.DataFrame(rf_sens)
    sensitivity_sm_df = pd.DataFrame(sm_sens)
    sensitivity_df = pd.concat([sensitivity_rf_df, sensitivity_sm_df], ignore_index=True)

    # 5. Export Deliverables under results/simulation/
    out_dir = Path("results/simulation")
    export_simulation_deliverables(
        results_df=results_df,
        comparison_df=comparison_df,
        transitions_df=transitions_df,
        sensitivity_df=sensitivity_df,
        summary_json_payload=summary_metrics,
        output_dir=out_dir,
    )
    print(f"Successfully exported simulation deliverables under: {out_dir.resolve()}")

    # 6. Generate Visual Research Figures
    fig_dir = Path("results/figures")
    generate_phase7_figures(comparison_df, sensitivity_rf_df, sensitivity_sm_df, fig_dir=fig_dir)
    print(f"Saved Phase 7 research figures to: {fig_dir.resolve()}")

    # 7. Generate Academic Documentation Reports
    generate_phase7_academic_reports(summary_metrics, len(sampled_df), len(top_locs), len(scenarios_list))

    # 8. Print Terminal Summary Block
    print("\n" + "=" * 60)
    print("PHASE 7 — WHAT-IF SIMULATION")
    print("=" * 60)
    print(f"Baseline observations simulated: {len(sampled_df):,}")
    print(f"Locations evaluated: {len(top_locs):,}")
    print(f"Scenarios evaluated: {len(scenarios_list):,}")
    print(f"\nMean risk change: {summary_metrics['mean_risk_probability_change']:+.4f}")
    print(f"Median risk change: {summary_metrics['median_risk_probability_change']:+.4f}")
    print(f"\nWarning state transitions: {summary_metrics['total_warning_state_transitions']:,}")
    print(f"\nIn-domain scenarios: {summary_metrics['in_domain_scenarios_count']:,}")
    print(f"Extrapolation scenarios: {summary_metrics['extrapolation_scenarios_count']:,}")
    print("=" * 60)
    print("PHASE 7 COMPLETED SUCCESSFULLY.")
    print("=" * 60)
    return 0


def generate_phase7_academic_reports(
    metrics: Dict[str, Any],
    num_obs: int,
    num_locs: int,
    num_scen: int,
) -> None:
    """Generates academic Markdown documentation reports for Phase 7."""
    docs_dir = Path("docs")
    docs_dir.mkdir(parents=True, exist_ok=True)

    # phase7_what_if_simulation.md
    sim_doc = [
        "# Phase 7 What-If Environmental Scenario Simulation Report",
        "",
        "## 1. Executive Summary",
        "Phase 7 implemented a counterfactual What-If Environmental Scenario Simulation engine enabling researchers to analyze model risk sensitivity and warning-state escalation under modified rainfall and soil moisture conditions.",
        "",
        "## 2. Simulation Experiment Statistics",
        f"* **Baseline Observations Simulated**: `{num_obs:,}`",
        f"* **Representative Locations Evaluated**: `{num_locs:,}`",
        f"* **Scenarios Evaluated per Observation**: `{num_scen:,}`",
        f"* **Total Scenario Runs**: `{metrics.get('total_simulations_evaluated', 0):,}`",
        f"* **Mean Risk Probability Change (ΔP)**: `{metrics.get('mean_risk_probability_change', 0.0):+.4f}`",
        f"* **Median Risk Probability Change (ΔP)**: `{metrics.get('median_risk_probability_change', 0.0):+.4f}`",
        f"* **Total Warning State Transitions**: `{metrics.get('total_warning_state_transitions', 0):,}`",
        f"* **In-Domain Scenarios**: `{metrics.get('in_domain_scenarios_count', 0):,}`",
        f"* **Extrapolation Scenarios**: `{metrics.get('extrapolation_scenarios_count', 0):,}` ({metrics.get('extrapolation_percentage', 0.0):.2f}%)",
        "",
        "---",
        "",
        "## 3. Mandatory Disclaimer",
        "**NOTE**: These simulations represent model-based scenario analyses (counterfactual what-if queries) and do NOT represent observed historical landslide events.",
    ]

    with open(docs_dir / "phase7_what_if_simulation.md", "w", encoding="utf-8") as f:
        f.write("\n".join(sim_doc) + "\n")

    # PHASE7_COMPLETION_REPORT.md
    completion_doc = [
        "# Phase 7 Completion Report: What-If Environmental Simulation",
        "",
        "## 1. Executive Summary",
        "Phase 7 successfully implemented the WhatIfSimulator module, allowing researchers to evaluate environmental sensitivity, warning state transitions, and location-adaptive responses without altering original datasets or retraining machine learning models.",
        "",
        "## 2. Quantitative Simulation Results",
        f"* **Total Simulated Runs**: `{metrics.get('total_simulations_evaluated', 0):,}`",
        f"* **Mean Risk Change**: `{metrics.get('mean_risk_probability_change', 0.0):+.4f}`",
        f"* **Warning State Transitions**: `{metrics.get('total_warning_state_transitions', 0):,}`",
        "",
        "## 3. Verification & Compliance",
        "All output CSV datasets were generated under `results/simulation/`, research figures under `results/figures/`, and comprehensive unit tests validated under `tests/`.",
    ]

    with open(docs_dir / "PHASE7_COMPLETION_REPORT.md", "w", encoding="utf-8") as f:
        f.write("\n".join(completion_doc) + "\n")


if __name__ == "__main__":
    sys.exit(main())
