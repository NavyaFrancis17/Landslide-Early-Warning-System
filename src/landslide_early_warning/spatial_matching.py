"""
Spatial Matching and Geodesic Distance Validation Module.

Provides exact Haversine spatial distance calculations between landslide event coordinates
and ERA5-Land reanalysis grid cells, with configurable maximum distance threshold validation.
"""

import math
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


EARTH_RADIUS_KM: float = 6371.0088  # Mean Earth radius in kilometers (IUGG WGS84)


def calculate_haversine_distance(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """
    Calculates the great-circle geodesic distance between two points on Earth using the Haversine formula.

    Args:
        lat1: Latitude of point 1 in decimal degrees.
        lon1: Longitude of point 1 in decimal degrees.
        lat2: Latitude of point 2 in decimal degrees.
        lon2: Longitude of point 2 in decimal degrees.

    Returns:
        float: Distance between points in kilometers (km).
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return EARTH_RADIUS_KM * c


def find_nearest_grid_cell(
    event_lat: float,
    event_lon: float,
    grid_coords: List[Tuple[float, float]],
) -> Tuple[Tuple[float, float], float]:
    """
    Finds the nearest grid cell coordinate from a list of environmental grid coordinates.

    Args:
        event_lat: Latitude of event.
        event_lon: Longitude of event.
        grid_coords: List of available (grid_lat, grid_lon) tuples.

    Returns:
        Tuple[Tuple[float, float], float]:
            - Nearest (matched_lat, matched_lon) tuple.
            - Minimum spatial matching distance in kilometers.
    """
    if not grid_coords:
        raise ValueError("Grid coordinates list cannot be empty.")

    min_dist = float("inf")
    best_grid = grid_coords[0]

    for grid_lat, grid_lon in grid_coords:
        dist = calculate_haversine_distance(event_lat, event_lon, grid_lat, grid_lon)
        if dist < min_dist:
            min_dist = dist
            best_grid = (grid_lat, grid_lon)

    return best_grid, min_dist


def validate_spatial_distance(
    distance_km: float, max_allowed_km: float = 50.0
) -> Dict[str, Any]:
    """
    Validates whether spatial matching distance is within acceptable research limits.

    Args:
        distance_km: Spatial matching distance in kilometers.
        max_allowed_km: Configurable threshold limit in kilometers.

    Returns:
        Dict[str, Any]: Validation report with boolean flag and distance metrics.
    """
    is_valid = distance_km <= max_allowed_km
    return {
        "spatial_match_valid": is_valid,
        "distance_km": round(distance_km, 4),
        "max_allowed_km": max_allowed_km,
        "flag_excessive": not is_valid,
    }
