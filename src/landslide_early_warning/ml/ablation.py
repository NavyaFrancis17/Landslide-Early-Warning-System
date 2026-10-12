"""
Feature Group Ablation Experiment Engine.

Evaluates the relative performance contribution of distinct feature groups:
- Experiment A: Precipitation features only
- Experiment B: Precipitation + Soil Moisture features
- Experiment C: Precipitation + Soil Moisture + Temporal Calendar features
- Experiment D: All Environmental + Spatial/Topographic features
- Experiment E: All Features + Location-Adaptive Anomaly Features
"""

from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from landslide_early_warning.ml.train import compute_classification_metrics, perform_chronological_split


ABLATION_GROUPS: Dict[str, List[str]] = {
    "Exp_A_Rainfall_Only": [
        "precipitation_1h", "precipitation_3h", "precipitation_6h",
        "precipitation_12h", "precipitation_24h", "precipitation_72h",
        "precipitation_168h", "precipitation_max_intensity_24h",
    ],
    "Exp_B_Rainfall_SoilMoisture": [
        "precipitation_1h", "precipitation_3h", "precipitation_6h",
        "precipitation_12h", "precipitation_24h", "precipitation_72h",
        "precipitation_168h", "precipitation_max_intensity_24h",
        "soil_moisture_layer1_current", "soil_moisture_layer1_mean_24h",
        "soil_moisture_layer1_mean_72h", "soil_moisture_layer1_change_24h",
        "soil_moisture_layer1_change_72h", "soil_moisture_layer2_current",
        "soil_moisture_layer3_current",
    ],
    "Exp_C_Rainfall_SoilMoisture_Temporal": [
        "precipitation_1h", "precipitation_3h", "precipitation_6h",
        "precipitation_12h", "precipitation_24h", "precipitation_72h",
        "precipitation_168h", "precipitation_max_intensity_24h",
        "soil_moisture_layer1_current", "soil_moisture_layer1_mean_24h",
        "soil_moisture_layer1_mean_72h", "soil_moisture_layer1_change_24h",
        "soil_moisture_layer1_change_72h", "soil_moisture_layer2_current",
        "soil_moisture_layer3_current", "event_month", "event_day_of_year",
    ],
    "Exp_D_All_Environmental_Spatial": [
        "precipitation_1h", "precipitation_3h", "precipitation_6h",
        "precipitation_12h", "precipitation_24h", "precipitation_72h",
        "precipitation_168h", "precipitation_max_intensity_24h",
        "soil_moisture_layer1_current", "soil_moisture_layer1_mean_24h",
        "soil_moisture_layer1_mean_72h", "soil_moisture_layer1_change_24h",
        "soil_moisture_layer1_change_72h", "soil_moisture_layer2_current",
        "soil_moisture_layer3_current", "temperature_2m_mean_24h",
        "relative_humidity_2m_mean_24h", "landslide_latitude",
        "landslide_longitude", "matched_grid_elevation", "event_month",
        "event_day_of_year",
    ],
}


def run_ablation_study(
    df: pd.DataFrame,
    target_col: str = "target",
    results_dir: Path = Path("results/metrics"),
    random_seed: int = 42,
) -> pd.DataFrame:
    """
    Executes feature ablation study using Gradient Boosting model across predefined feature groups.

    Args:
        df: Master labeled dataset.
        target_col: Target column.
        results_dir: Path to save results CSV.
        random_seed: Reproducibility random seed.

    Returns:
        pd.DataFrame: Ablation study results comparison table.
    """
    results_dir.mkdir(parents=True, exist_ok=True)
    train_df, val_df, test_df = perform_chronological_split(df)

    ablation_rows = []

    for exp_name, feat_cols in ABLATION_GROUPS.items():
        print(f"Running Ablation Experiment: {exp_name} ({len(feat_cols)} features)...")

        # Slicing datasets
        X_tr = train_df[feat_cols]
        y_tr = train_df[target_col].values
        X_val = val_df[feat_cols]
        y_val = val_df[target_col].values
        X_te = test_df[feat_cols]
        y_te = test_df[target_col].values

        # Preprocessing pipeline
        pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("clf", GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=random_seed)),
        ])

        pipe.fit(X_tr, y_tr)

        # Validation threshold selection
        val_probs = pipe.predict_proba(X_val)[:, 1]
        best_th = 0.5
        best_f1 = -1.0
        for th in [0.3, 0.4, 0.5, 0.6, 0.7]:
            preds = (val_probs >= th).astype(int)
            f1 = compute_classification_metrics(y_val, preds, val_probs)["F1"]
            if f1 > best_f1:
                best_f1 = f1
                best_th = th

        # Untouched Test Evaluation
        test_probs = pipe.predict_proba(X_te)[:, 1]
        test_preds = (test_probs >= best_th).astype(int)

        m = compute_classification_metrics(y_te, test_preds, test_probs)
        m["Experiment"] = exp_name
        m["Feature_Count"] = len(feat_cols)
        m["Val_Threshold"] = round(best_th, 2)
        ablation_rows.append(m)

    ablation_df = pd.DataFrame(ablation_rows)
    cols = ["Experiment", "Feature_Count", "Accuracy", "Precision", "Recall", "F1", "ROC_AUC", "PR_AUC", "Balanced_Accuracy", "Brier_Score"]
    ablation_df = ablation_df[cols]

    ablation_df.to_csv(results_dir / "ablation_results.csv", index=False)
    print(f"Saved ablation study results to: {(results_dir / 'ablation_results.csv').resolve()}")
    return ablation_df
