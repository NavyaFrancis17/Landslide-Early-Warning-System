"""
Tests for data quality and validation module (Phase 2).
"""

import numpy as np
import pandas as pd
import pytest
from landslide_early_warning.data_quality import (
    detect_duplicates,
    profile_missing_values,
    validate_coordinates,
    validate_schema,
)


def test_validate_schema_pass():
    df = pd.DataFrame({"col1": [1, 2], "col2": ["a", "b"]})
    res = validate_schema(df, ["col1", "col2"])
    assert res["valid"] is True
    assert len(res["missing_columns"]) == 0


def test_validate_schema_fail():
    df = pd.DataFrame({"col1": [1, 2]})
    res = validate_schema(df, ["col1", "missing_col"])
    assert res["valid"] is False
    assert "missing_col" in res["missing_columns"]


def test_validate_coordinates():
    df = pd.DataFrame({
        "latitude": [10.5, -45.0, 95.0, np.nan],
        "longitude": [75.2, -170.0, 185.0, 50.0]
    })
    res = validate_coordinates(df, lat_col="latitude", lon_col="longitude")
    assert res["total_records"] == 4
    assert res["valid_coordinates_count"] == 2
    assert res["out_of_range_latitude"] == 1
    assert res["out_of_range_longitude"] == 1
    assert res["missing_latitude"] == 1
    assert res["unique_location_pairs"] == 2


def test_detect_duplicates():
    df = pd.DataFrame({
        "event_id": [101, 102, 101],
        "val": ["A", "B", "A"]
    })
    res = detect_duplicates(df, id_col="event_id")
    assert res["full_row_duplicates"] == 1
    assert res["identifier_duplicates"] == 1


def test_profile_missing_values():
    df = pd.DataFrame({
        "a": [1, None, 3],
        "b": ["x", "y", "z"]
    })
    profile = profile_missing_values(df)
    assert profile["a"]["missing_count"] == 1
    assert profile["a"]["missing_percentage"] == 33.33
    assert profile["b"]["missing_count"] == 0
