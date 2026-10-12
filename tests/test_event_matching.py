"""
Unit tests for spatial-temporal event matching (Phase 6).
"""

import pandas as pd
import pytest
from landslide_early_warning.evaluation.event_matcher import match_warning_events_to_landslides


def test_match_warning_events_to_landslides_valid_pre_event():
    warning_events_df = pd.DataFrame({
        "warning_event_id": ["WE_0001"],
        "location_id": ["loc_32.56_107.45"],
        "warning_start_time": ["2008-07-31 12:00:00"],
        "initial_state": ["WARNING"],
        "maximum_state": ["HIGH_RISK"],
    })

    landslide_events_df = pd.DataFrame({
        "event_id": [684],
        "event_date": ["08-01-2008 00:00"],
        "event_datetime": ["2008-08-01 00:00:00"],
        "latitude": [32.5625],
        "longitude": [107.4500],
    })

    location_coords_map = {"loc_32.56_107.45": (32.5625, 107.4500)}

    matches_df, detected, missed, false_warns = match_warning_events_to_landslides(
        warning_events_df, landslide_events_df, location_coords_map, max_distance_km=50.0
    )

    assert len(detected) == 1
    assert detected[0]["event_id"] == 684
    assert detected[0]["matched_warning_event_id"] == "WE_0001"
    assert detected[0]["lead_time_hours"] == 12.0
    assert len(missed) == 0
    assert len(false_warns) == 0


def test_match_warning_events_post_event_warning_rejected():
    # Warning starts AFTER landslide event -> Must be rejected as early warning
    warning_events_df = pd.DataFrame({
        "warning_event_id": ["WE_0002"],
        "location_id": ["loc_32.56_107.45"],
        "warning_start_time": ["2008-08-02 12:00:00"],
        "initial_state": ["WARNING"],
        "maximum_state": ["HIGH_RISK"],
    })

    landslide_events_df = pd.DataFrame({
        "event_id": [684],
        "event_date": ["08-01-2008 00:00"],
        "event_datetime": ["2008-08-01 00:00:00"],
        "latitude": [32.5625],
        "longitude": [107.4500],
    })

    location_coords_map = {"loc_32.56_107.45": (32.5625, 107.4500)}

    matches_df, detected, missed, false_warns = match_warning_events_to_landslides(
        warning_events_df, landslide_events_df, location_coords_map, max_distance_km=50.0
    )

    assert len(detected) == 0  # Rejects post-event warning
    assert len(missed) == 1
    assert len(false_warns) == 1
