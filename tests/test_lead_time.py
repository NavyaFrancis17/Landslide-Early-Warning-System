"""
Unit tests for lead-time calculation and distribution stats (Phase 6).
"""

import pandas as pd
import pytest
from landslide_early_warning.evaluation.lead_time import (
    calculate_lead_time_metrics,
    compute_lead_time_distribution_statistics,
)


def test_calculate_lead_time_metrics():
    start_ts = pd.Timestamp("2026-01-01 00:00:00")
    event_ts = pd.Timestamp("2026-01-02 12:00:00")

    lead_h, lead_d, is_valid = calculate_lead_time_metrics(start_ts, event_ts)

    assert lead_h == 36.0
    assert lead_d == 1.5
    assert is_valid is True


def test_compute_lead_time_distribution_statistics():
    lead_times = [0.5, 3.0, 10.0, 18.0, 48.0, 100.0]
    stats = compute_lead_time_distribution_statistics(lead_times)

    assert stats["matched_events_count"] == 6
    assert stats["min_lead_time_hours"] == 0.5
    assert stats["max_lead_time_hours"] == 100.0
    assert stats["median_lead_time_hours"] == 14.0
    assert stats["bucket_counts"]["less_than_1h"] == 1
    assert stats["bucket_counts"]["days_1_to_3"] == 1
