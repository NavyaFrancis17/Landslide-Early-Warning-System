"""
Unit tests for chronological splitting and model metrics calculation (Phase 4).
"""

import numpy as np
import pandas as pd
import pytest
from landslide_early_warning.ml.train import (
    compute_classification_metrics,
    perform_chronological_split,
)


def test_perform_chronological_split():
    df = pd.DataFrame({
        "event_year": [2005, 2009, 2012, 2013, 2016, 2017],
        "value": [1, 2, 3, 4, 5, 6],
    })

    train_df, val_df, test_df = perform_chronological_split(df, train_end_year=2010, val_end_year=2014)

    assert len(train_df) == 2
    assert len(val_df) == 2
    assert len(test_df) == 2

    # Verify chronological ordering bounds
    assert train_df["event_year"].max() <= 2010
    assert val_df["event_year"].min() >= 2011 and val_df["event_year"].max() <= 2014
    assert test_df["event_year"].min() >= 2015


def test_compute_classification_metrics_bounds():
    y_true = np.array([1, 1, 0, 0, 1])
    y_pred = np.array([1, 0, 0, 0, 1])
    y_prob = np.array([0.9, 0.4, 0.1, 0.2, 0.85])

    metrics = compute_classification_metrics(y_true, y_pred, y_prob)

    assert 0.0 <= metrics["Accuracy"] <= 1.0
    assert 0.0 <= metrics["Precision"] <= 1.0
    assert 0.0 <= metrics["Recall"] <= 1.0
    assert 0.0 <= metrics["F1"] <= 1.0
    assert 0.0 <= metrics["ROC_AUC"] <= 1.0
    assert 0.0 <= metrics["Brier_Score"] <= 1.0
