"""
Probability Calibration and Brier Score Reliability Module.

Evaluates raw model probabilities against Sigmoid (Platt) and Isotonic calibrated probabilities.
Calibration parameters are fitted strictly on validation data to prevent test set data leakage.
"""

from pathlib import Path
from typing import Any, Dict, Tuple
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import brier_score_loss


def evaluate_and_plot_calibration(
    models_dict: Dict[str, Any],
    X_val_proc: np.ndarray,
    y_val: np.ndarray,
    X_test_proc: np.ndarray,
    y_test: np.ndarray,
    output_dir: Path = Path("results/figures"),
) -> pd.DataFrame:
    """
    Fits probability calibration on validation data and evaluates Brier scores on the untouched test set.

    Args:
        models_dict: Dictionary of fitted models.
        X_val_proc: Preprocessed validation feature matrix.
        y_val: Validation targets.
        X_test_proc: Preprocessed test feature matrix.
        y_test: Test targets.
        output_dir: Output directory for figures.

    Returns:
        pd.DataFrame: Calibration summary table comparing raw vs calibrated Brier scores.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    results = []

    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    ax.plot([0, 1], [0, 1], "k--", label="Perfectly Calibrated (Ideal)")

    for name, model in models_dict.items():
        if name == "Dummy_Classifier":
            continue

        raw_test_probs = model.predict_proba(X_test_proc)[:, 1]
        raw_brier = brier_score_loss(y_test, raw_test_probs)

        # Fit Sigmoid Calibrator on Validation Data Only
        calibrator = CalibratedClassifierCV(estimator=model, method="sigmoid", cv="prefit")
        calibrator.fit(X_val_proc, y_val)
        calib_test_probs = calibrator.predict_proba(X_test_proc)[:, 1]
        calib_brier = brier_score_loss(y_test, calib_test_probs)

        # Compute calibration curve for plot
        prob_true, prob_pred = calibration_curve(y_test, calib_test_probs, n_bins=10)
        ax.plot(prob_pred, prob_true, "s-", label=f"{name} (Brier={calib_brier:.4f})")

        results.append({
            "Model": name,
            "Raw_Brier_Score": round(raw_brier, 4),
            "Calibrated_Brier_Score": round(calib_brier, 4),
            "Brier_Score_Improvement": round(raw_brier - calib_brier, 4),
        })

    ax.set_title("Probability Calibration Reliability Diagram (Untouched Test Set)", fontsize=12, fontweight="bold")
    ax.set_xlabel("Mean Predicted Risk Probability", fontsize=10)
    ax.set_ylabel("Fraction of Positives (Observed Frequency)", fontsize=10)
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig.savefig(output_dir / "calibration_curve.png")
    plt.close(fig)

    calib_df = pd.DataFrame(results)
    return calib_df
