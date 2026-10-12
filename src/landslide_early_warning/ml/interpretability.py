"""
Model Interpretability and Feature Importance Analysis Module.

Computes Gini feature importances for tree-based ensemble models.
Generates results/metrics/feature_importance.csv and results/figures/feature_importance.png.
"""

from pathlib import Path
from typing import Any, List
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def compute_and_plot_feature_importance(
    model: Any,
    feature_names: List[str],
    results_dir: Path = Path("results/metrics"),
    fig_dir: Path = Path("results/figures"),
) -> pd.DataFrame:
    """
    Extracts Gini feature importances from a trained tree model and plots summary.

    Args:
        model: Trained tree ensemble model (RandomForest or GradientBoosting).
        feature_names: List of feature names.
        results_dir: Path to export CSV metrics.
        fig_dir: Path to export PNG plot.

    Returns:
        pd.DataFrame: Feature importances dataframe.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    fig_dir.mkdir(parents=True, exist_ok=True)

    if not hasattr(model, "feature_importances_"):
        raise ValueError("Model does not expose feature_importances_ attribute.")

    importances = model.feature_importances_
    df = pd.DataFrame({
        "Feature": feature_names,
        "Importance": importances,
    }).sort_values(by="Importance", ascending=False).reset_index(drop=True)

    df["Normalized_Importance"] = round(df["Importance"] / df["Importance"].sum(), 4)
    df["Importance"] = round(df["Importance"], 4)

    df.to_csv(results_dir / "feature_importance.csv", index=False)
    print(f"Saved feature importance table to: {(results_dir / 'feature_importance.csv').resolve()}")

    # Plot top 15 features
    top_df = df.head(15).iloc[::-1]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=300)
    ax.barh(top_df["Feature"], top_df["Normalized_Importance"], color="#1f77b4", edgecolor="black")
    ax.set_title("Relative Model Feature Importance (Gradient Boosting Gini Index)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Normalized Feature Importance Weight", fontsize=10)
    plt.tight_layout()
    fig.savefig(fig_dir / "feature_importance.png")
    plt.close(fig)

    return df
