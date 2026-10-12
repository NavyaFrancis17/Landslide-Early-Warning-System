"""
Unit tests for missed landslide event analysis (Phase 6).
"""

import pytest
from landslide_early_warning.evaluation.missed_events import analyze_missed_landslide_events


def test_analyze_missed_landslide_events():
    missed_list = [
        {"event_id": 101, "miss_reason": "NO_MATCHED_ACTIONABLE_PRE_EVENT_WARNING"},
    ]

    res = analyze_missed_landslide_events(missed_list, total_evaluable_actual_events=10)

    assert res["total_missed_landslide_events"] == 1
    assert res["miss_rate"] == 0.10
    assert "NO_MATCHED_ACTIONABLE_PRE_EVENT_WARNING" in res["miss_reasons_breakdown"]
