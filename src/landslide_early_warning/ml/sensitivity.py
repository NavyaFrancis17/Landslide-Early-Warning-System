"""
Controlled What-If Environmental Sensitivity Analysis Module.

Evaluates how systematic perturbations in key environmental forcing variables
(24h/72h precipitation and soil moisture) affect predicted landslide hazard probabilities.
Outputs results/metrics/what_if_sensitivity.csv and results/figures/what_if_sensitivity.png.
"""

from pathlib import Path
from typing import Any, Dict, List
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline


def run_what_if_sensitivity_analysis(
    model: Any,
    imputer: Any,
    scaler: Any,
    test_df: pd.DataFrame,
    features: List[str],
    results_dir: Path = Path("results/metrics"),
    fig_dir: Path = Path("results/figures"),
) -> pd.DataFrame:
    """
    Executes controlled what-if environmental perturbations on test samples.

    Perturbation scenarios evaluated:
    - Base (Observed ERA5-Land conditions)
    - Precipitation +25%
    - Precipitation +50%
    - Precipitation -25%
    - Soil Moisture +25%
    - Soil Moisture -25%

    Args:
        model: Trained model.
        imputer: Fitted SimpleImputer.
        scaler: Fitted StandardScaler.
        test_df: Test set DataFrame.
        features: Feature column list.
        results_dir: Metrics output directory.
        fig_dir: Figures output directory.

    Returns:
        pd.DataFrame: What-if sensitivity summary dataframe.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    X_test_base = test_df[features].copy()
    base_proc = scaler.transform(imputer.transform(X_test_base))
    base_probs = model.predict_proba(base_proc)[:, 1]

    scenarios = [
        ("Base (Observed)", 1.0, 1.0),
        ("Precipitation +25%", 1.25, 1.0),
        ("Precipitation +50%", 1.50, 1.0),
        ("Precipitation -25%", 0.75, 1.0),
        ("Soil Moisture +25%", 1.0, 1.25),
        ("Soil Moisture -25%", 1.0, 0.75),
    ]

    precip_cols = [c for c in features if "precipitation" in c]
    sm_cols = [c for c in features if "soil_moisture" in c]

    sensitivity_rows = []

    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)

    for name, p_mult, sm_mult in scenarios:
        X_pert = X_test_base.copy()

        if p_mult != 1.0:
            for pc in precip_cols:
                X_pert[pc] = X_pert[pc] * p_mult

        if sm_mult != 1.0:
            for smc in sm_cols:
                # Soil moisture bounded in physical range [0.0, 0.85]
                X_pert[smc] = np.clip(X_pert[smc] * sm_mult, 0.0, 0.85)

        pert_proc = scaler.transform(imputer.transform(X_pert))
        pert_probs = model.predict_proba(pert_proc)[:, 1]

        mean_p = float(np.mean(pert_probs))
        median_p = float(np.median(pert_probs))
        delta_p = float(mean_p - np.mean(base_probs))

        sensitivity_rows.append({
            "Scenario": name,
            "Precipitation_Multiplier": p_mult,
            "Soil_Moisture_Multiplier": sm_mult,
            "Mean_Predicted_Probability": round(mean_p, 4),
            "Median_Predicted_Probability": round(median_p, 4),
            "Mean_Probability_Delta": round(delta_p, 4),
        })

        ax.hist(pert_probs, bins=25, alpha=0.4, label=f"{name} (Mean={mean_p:.3f})")

    ax.set_title("What-If Sensitivity Analysis: Landslide Risk Probability Shift", fontsize=12, fontweight="bold")
    ax.set_xlabel("Predicted Landslide Risk Probability P(Landslide)", fontsize=10)
    ax.set_ylabel("Sample Count", fontsize=10)
    ax.legend(fontsize=8)
    plt.tight_layout()
    fig.savefig(fig_dir / "what_if_sensitivity.png")
    plt.close(fig)

    sens_df = pd.DataFrame(sensitivity_rows)
    sens_df.to_csv(results_dir / "what_if_sensitivity.csv", index=False)
    print(f"Saved what-if sensitivity analysis to: {(results_dir / 'what_if_sensitivity.csv').resolve()}")
    return sens_df
