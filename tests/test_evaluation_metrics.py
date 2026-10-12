"""
Unit tests for event-level evaluation metrics calculation (Phase 6).
"""

import numpy as np
import pytest
from landslide_early_warning.evaluation.evaluation_metrics import compute_event_evaluation_metrics


def test_compute_event_evaluation_metrics_success():
    metrics = compute_event_evaluation_metrics(
        total_actual_events=100,
        detected_events_count=80,
        missed_events_count=20,
        total_actionable_warnings=100,
        matched_warnings_count=80,
        false_warnings_count=20,
    )

    assert metrics["event_detection_rate"] == 0.80
    assert metrics["warning_precision"] == 0.80
    assert metrics["miss_rate"] == 0.20
    assert metrics["event_f1_score"] == 0.80


def test_compute_event_evaluation_metrics_zero_division():
    metrics = compute_event_evaluation_metrics(
        total_actual_events=0,
        detected_events_count=0,
        missed_events_count=0,
        total_actionable_warnings=0,
        matched_warnings_count=0,
        false_warnings_count=0,
    )

    assert np.isnan(metrics["event_detection_rate"])
    assert np.isnan(metrics["warning_precision"])
    assert np.isnan(metrics["miss_rate"])
