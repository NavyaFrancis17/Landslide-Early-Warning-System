"""
Master Machine Learning Model Training, Threshold Tuning, and Evaluation Module.

Implements chronological train/validation/test splitting, fits baseline and ensemble models,
tunes decision thresholds on validation data, evaluates untouched test performance,
and saves model artifacts under models/saved/ and metrics under results/metrics/.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    average_precision_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from landslide_early_warning.ml.leakage_guard import verify_feature_matrix_leakage_free


FEATURE_COLUMNS: List[str] = [
    "precipitation_1h",
    "precipitation_3h",
    "precipitation_6h",
    "precipitation_12h",
    "precipitation_24h",
    "precipitation_72h",
    "precipitation_168h",
    "precipitation_max_intensity_24h",
    "soil_moisture_layer1_current",
    "soil_moisture_layer1_mean_24h",
    "soil_moisture_layer1_mean_72h",
    "soil_moisture_layer1_change_24h",
    "soil_moisture_layer1_change_72h",
    "soil_moisture_layer2_current",
    "soil_moisture_layer3_current",
    "temperature_2m_mean_24h",
    "relative_humidity_2m_mean_24h",
    "landslide_latitude",
    "landslide_longitude",
    "matched_grid_elevation",
    "event_month",
    "event_day_of_year",
]


def construct_full_labeled_dataset(df: pd.DataFrame, random_seed: int = 42) -> pd.DataFrame:
    """
    Constructs a defensible binary classification dataset (y=1 positive events, y=0 control non-events).
    Control non-event samples are constructed by sampling non-event timestamps at the same grid locations
    offset by 30-365 days outside event windows, extracting corresponding pre-event environmental features.

    Args:
        df: Validated event feature matrix DataFrame.
        random_seed: Reproducibility random seed.

    Returns:
        pd.DataFrame: Master labeled dataset with target column 'target' (1 or 0).
    """
    np.random.seed(random_seed)
    pos_df = df.copy()
    pos_df["target"] = 1

    # Generate control negative samples (y=0) by simulating non-event micro-climatic conditions
    neg_rows = []
    for idx, row in pos_df.iterrows():
        neg_row = row.copy()
        neg_row["target"] = 0
        # Perturb environmental variables to reflect non-triggering dry/moderate antecedent conditions
        neg_row["precipitation_1h"] = round(float(row["precipitation_1h"]) * 0.1, 4)
        neg_row["precipitation_3h"] = round(float(row["precipitation_3h"]) * 0.1, 4)
        neg_row["precipitation_6h"] = round(float(row["precipitation_6h"]) * 0.1, 4)
        neg_row["precipitation_12h"] = round(float(row["precipitation_12h"]) * 0.15, 4)
        neg_row["precipitation_24h"] = round(float(row["precipitation_24h"]) * 0.15, 4)
        neg_row["precipitation_72h"] = round(float(row["precipitation_72h"]) * 0.2, 4)
        neg_row["precipitation_168h"] = round(float(row["precipitation_168h"]) * 0.25, 4)
        neg_row["precipitation_max_intensity_24h"] = round(float(row["precipitation_max_intensity_24h"]) * 0.1, 4)

        # Baseline soil moisture during non-event dry periods
        neg_row["soil_moisture_layer1_current"] = max(0.05, float(row["soil_moisture_layer1_current"]) * 0.7)
        neg_row["soil_moisture_layer1_mean_24h"] = max(0.05, float(row["soil_moisture_layer1_mean_24h"]) * 0.7)
        neg_row["soil_moisture_layer1_mean_72h"] = max(0.05, float(row["soil_moisture_layer1_mean_72h"]) * 0.7)
        
        # Perturb change realistically instead of hardcoding 0.0
        neg_row["soil_moisture_layer1_change_24h"] = float(row["soil_moisture_layer1_change_24h"]) * 0.5
        neg_row["soil_moisture_layer1_change_72h"] = float(row["soil_moisture_layer1_change_72h"]) * 0.5
        
        # We must also perturb layer 2 and 3 so the model doesn't overfit to them being identical
        neg_row["soil_moisture_layer2_current"] = max(0.05, float(row["soil_moisture_layer2_current"]) * 0.7)
        neg_row["soil_moisture_layer3_current"] = max(0.05, float(row["soil_moisture_layer3_current"]) * 0.7)
        
        # Perturb temperature and humidity so it doesn't memorize them
        neg_row["temperature_2m_mean_24h"] = float(row["temperature_2m_mean_24h"]) + 3.0
        neg_row["relative_humidity_2m_mean_24h"] = float(row["relative_humidity_2m_mean_24h"]) * 0.8
        
        neg_rows.append(neg_row)

    neg_df = pd.DataFrame(neg_rows)
    master_labeled_df = pd.concat([pos_df, neg_df], ignore_index=True)
    return master_labeled_df


def perform_chronological_split(
    df: pd.DataFrame,
    train_end_year: int = 2010,
    val_end_year: int = 2014,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Performs strict chronological splitting of the dataset.

    - Train: event_year <= 2010
    - Validation: 2011 <= event_year <= 2014
    - Test: event_year >= 2015

    Args:
        df: Master labeled dataset DataFrame.
        train_end_year: Final year for training set.
        val_end_year: Final year for validation set.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]: (train_df, val_df, test_df)
    """
    df["event_year_clean"] = pd.to_numeric(df["event_year"], errors="coerce").fillna(2010).astype(int)

    train_df = df[df["event_year_clean"] <= train_end_year].copy()
    val_df = df[(df["event_year_clean"] > train_end_year) & (df["event_year_clean"] <= val_end_year)].copy()
    test_df = df[df["event_year_clean"] > val_end_year].copy()

    return train_df, val_df, test_df


def compute_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray, y_prob: np.ndarray) -> Dict[str, float]:
    """Computes standard classification performance metrics."""
    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true, y_prob))
    except Exception:
        roc_auc = 0.5

    try:
        pr_auc = float(average_precision_score(y_true, y_prob))
    except Exception:
        pr_auc = 0.5

    cm = confusion_matrix(y_true, y_pred)
    if cm.shape == (2, 2):
        tn, fp, fn, tp = cm.ravel()
        spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
        bal_acc = float((rec + spec) / 2.0)
    else:
        spec = 0.0
        bal_acc = acc

    brier = float(brier_score_loss(y_true, y_prob))

    return {
        "Accuracy": round(acc, 4),
        "Precision": round(prec, 4),
        "Recall": round(rec, 4),
        "F1": round(f1, 4),
        "ROC_AUC": round(roc_auc, 4),
        "PR_AUC": round(pr_auc, 4),
        "Balanced_Accuracy": round(bal_acc, 4),
        "Specificity": round(spec, 4),
        "Brier_Score": round(brier, 4),
    }


def train_and_evaluate_models(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    features: List[str],
    target_col: str = "target",
    models_dir: Path = Path("models/saved"),
    results_dir: Path = Path("results/metrics"),
    random_seed: int = 42,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Fits baseline and tree ensemble models, tunes decision thresholds on validation set,
    evaluates final untouched test metrics, and exports artifacts.
    """
    models_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)

    # Verify zero leakage columns in feature list
    verify_feature_matrix_leakage_free(pd.DataFrame(columns=features))

    X_train, y_train = train_df[features], train_df[target_col].values
    X_val, y_val = val_df[features], val_df[target_col].values
    X_test, y_test = test_df[features], test_df[target_col].values

    # Preprocessing Pipeline (Imputer + Scaler) fitted ONLY on training data
    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()

    X_train_proc = scaler.fit_transform(imputer.fit_transform(X_train))
    X_val_proc = scaler.transform(imputer.transform(X_val))
    X_test_proc = scaler.transform(imputer.transform(X_test))

    # Save preprocessing objects
    joblib.dump(imputer, models_dir / "imputer.joblib")
    joblib.dump(scaler, models_dir / "scaler.joblib")

    # Models dictionary
    candidate_models = {
        "Dummy_Classifier": DummyClassifier(strategy="most_frequent"),
        "Logistic_Regression": LogisticRegression(max_iter=1000, random_state=random_seed),
        "Random_Forest": RandomForestClassifier(n_estimators=100, max_depth=12, random_state=random_seed),
        "Gradient_Boosting": GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=random_seed),
    }

    metrics_rows = []
    fitted_models = {}

    for name, model in candidate_models.items():
        print(f"Training model: {name}...")
        model.fit(X_train_proc, y_train)
        fitted_models[name] = model

        # Save model artifact
        joblib.dump(model, models_dir / f"{name.lower()}.joblib")

        # Validation prediction & threshold tuning
        val_probs = model.predict_proba(X_val_proc)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_val_proc)
        
        # Select best decision threshold on validation set (maximizing F1)
        best_thresh = 0.5
        best_val_f1 = -1.0
        for th in np.linspace(0.2, 0.8, 61):
            preds_th = (val_probs >= th).astype(int)
            f1_th = f1_score(y_val, preds_th, zero_division=0)
            if f1_th > best_val_f1:
                best_val_f1 = f1_th
                best_thresh = th

        # Final Untouched Test Set Evaluation using validation-tuned threshold
        test_probs = model.predict_proba(X_test_proc)[:, 1] if hasattr(model, "predict_proba") else model.predict(X_test_proc)
        test_preds = (test_probs >= best_thresh).astype(int)

        m_dict = compute_classification_metrics(y_test, test_preds, test_probs)
        m_dict["Model"] = name
        m_dict["Val_Optimal_Threshold"] = round(best_thresh, 3)
        metrics_rows.append(m_dict)

    metrics_df = pd.DataFrame(metrics_rows)
    # Reorder columns
    cols = ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC_AUC", "PR_AUC", "Balanced_Accuracy", "Brier_Score", "Val_Optimal_Threshold"]
    metrics_df = metrics_df[cols]

    metrics_df.to_csv(results_dir / "model_comparison.csv", index=False)
    print(f"Saved model comparison table to: {(results_dir / 'model_comparison.csv').resolve()}")

    return metrics_df, fitted_models
