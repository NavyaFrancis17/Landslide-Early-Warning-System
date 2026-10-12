"""
Unit tests for spatial matching and Haversine distance calculations (Phase 3).
"""

import pytest
from landslide_early_warning.spatial_matching import (
    calculate_haversine_distance,
    find_nearest_grid_cell,
    validate_spatial_distance,
)


def test_haversine_same_point():
    # Distance between identical points must be zero
    dist = calculate_haversine_distance(10.0, 75.0, 10.0, 75.0)
    assert round(dist, 5) == 0.0


def test_haversine_known_distance():
    # London (51.5074, -0.1278) to Paris (48.8566, 2.3522) ~ 343.5 km
    dist = calculate_haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
    assert 340.0 <= dist <= 347.0


def test_find_nearest_grid_cell():
    event_lat, event_lon = 10.1234, 76.5432
    grid_coords = [(10.1, 76.5), (10.5, 76.9), (11.0, 77.0)]

    best_grid, min_dist = find_nearest_grid_cell(event_lat, event_lon, grid_coords)
    assert best_grid == (10.1, 76.5)
    assert min_dist < 10.0  # Should be ~ 5 km


def test_validate_spatial_distance():
    res_valid = validate_spatial_distance(12.5, max_allowed_km=50.0)
    assert res_valid["spatial_match_valid"] is True
    assert res_valid["flag_excessive"] is False

    res_invalid = validate_spatial_distance(75.2, max_allowed_km=50.0)
    assert res_invalid["spatial_match_valid"] is False
    assert res_invalid["flag_excessive"] is True
