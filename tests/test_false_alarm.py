"""
Unit tests for false warning event analysis (Phase 6).
"""

import pytest
from landslide_early_warning.evaluation.false_alarm import analyze_false_warning_events


def test_analyze_false_warning_events():
    false_list = [
        {"warning_event_id": "WE_001", "false_alarm_reason": "NO_PREDICTED_LANDSLIDE_EVENT_MATCHED"},
        {"warning_event_id": "WE_002", "false_alarm_reason": "NO_PREDICTED_LANDSLIDE_EVENT_MATCHED"},
    ]

    res = analyze_false_warning_events(false_list, total_actionable_warnings=10)

    assert res["total_false_warning_events"] == 2
    assert res["false_alarm_rate"] == 0.20
    assert "NO_PREDICTED_LANDSLIDE_EVENT_MATCHED" in res["false_alarm_reasons_breakdown"]
