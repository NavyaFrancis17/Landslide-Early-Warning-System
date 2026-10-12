"""
Data Quality and Validation Module.

Provides reusable, structured functions for inspecting, auditing, and validating
raw landslide event datasets. Includes coordinate validation, missing-value profiling,
duplicate detection, and schema verification without mutating raw inputs.
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


def validate_schema(df: pd.DataFrame, expected_columns: List[str]) -> Dict[str, Any]:
    """
    Validates presence of expected schema columns in dataframe.

    Args:
        df: Pandas DataFrame to validate.
        expected_columns: List of mandatory column names.

    Returns:
        Dict[str, Any]: Validation report with boolean flag and missing columns list.
    """
    missing = [col for col in expected_columns if col not in df.columns]
    return {
        "valid": len(missing) == 0,
        "missing_columns": missing,
        "total_columns_found": len(df.columns),
    }


def validate_coordinates(
    df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude"
) -> Dict[str, Any]:
    """
    Validates geographic latitude and longitude values.

    Args:
        df: Pandas DataFrame.
        lat_col: Name of latitude column.
        lon_col: Name of longitude column.

    Returns:
        Dict[str, Any]: Validation metrics including invalid range counts and missing counts.
    """
    if lat_col not in df.columns or lon_col not in df.columns:
        return {"valid": False, "error": f"Columns {lat_col} or {lon_col} missing"}

    lat_series = pd.to_numeric(df[lat_col], errors="coerce")
    lon_series = pd.to_numeric(df[lon_col], errors="coerce")

    missing_lat = int(lat_series.isna().sum())
    missing_lon = int(lon_series.isna().sum())
    missing_both = int((lat_series.isna() | lon_series.isna()).sum())

    invalid_lat = int(((lat_series < -90.0) | (lat_series > 90.0)).sum())
    invalid_lon = int(((lon_series < -180.0) | (lon_series > 180.0)).sum())

    valid_coords_mask = (
        lat_series.notna()
        & lon_series.notna()
        & (lat_series >= -90.0)
        & (lat_series <= 90.0)
        & (lon_series >= -180.0)
        & (lon_series <= 180.0)
    )

    valid_count = int(valid_coords_mask.sum())
    unique_pairs = int(df.loc[valid_coords_mask, [lat_col, lon_col]].drop_duplicates().shape[0])

    return {
        "valid": invalid_lat == 0 and invalid_lon == 0 and missing_both == 0,
        "total_records": len(df),
        "valid_coordinates_count": valid_count,
        "missing_latitude": missing_lat,
        "missing_longitude": missing_lon,
        "missing_both_coordinates": missing_both,
        "out_of_range_latitude": invalid_lat,
        "out_of_range_longitude": invalid_lon,
        "unique_location_pairs": unique_pairs,
        "latitude_min": float(lat_series.min()) if lat_series.notna().any() else None,
        "latitude_max": float(lat_series.max()) if lat_series.notna().any() else None,
        "longitude_min": float(lon_series.min()) if lon_series.notna().any() else None,
        "longitude_max": float(lon_series.max()) if lon_series.notna().any() else None,
    }


def profile_missing_values(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """
    Profiles missing values across all columns of a dataframe.

    Args:
        df: Pandas DataFrame.

    Returns:
        Dict[str, Dict[str, Any]]: Per-column missing count and percentage dictionary.
    """
    total_rows = len(df)
    report: Dict[str, Dict[str, Any]] = {}
    for col in df.columns:
        null_count = int(df[col].isna().sum())
        pct = round((null_count / total_rows) * 100, 2) if total_rows > 0 else 0.0
        report[col] = {
            "dtype": str(df[col].dtype),
            "missing_count": null_count,
            "missing_percentage": pct,
        }
    return report


def detect_duplicates(
    df: pd.DataFrame, id_col: str = "event_id"
) -> Dict[str, Any]:
    """
    Detects full row duplicates and duplicate unique identifiers.

    Args:
        df: Pandas DataFrame.
        id_col: Identifier column name.

    Returns:
        Dict[str, Any]: Duplicate metrics.
    """
    full_row_dups = int(df.duplicated().sum())
    id_dups = int(df[id_col].duplicated().sum()) if id_col in df.columns else 0

    return {
        "full_row_duplicates": full_row_dups,
        "identifier_column": id_col,
        "identifier_duplicates": id_dups,
    }


def compute_numerical_ranges(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Computes summary statistics (min, max, mean, median, std) for numerical columns.

    Args:
        df: Pandas DataFrame.

    Returns:
        Dict[str, Dict[str, float]]: Numerical column statistics.
    """
    num_df = df.select_dtypes(include=[np.number])
    stats_dict: Dict[str, Dict[str, float]] = {}

    for col in num_df.columns:
        s = num_df[col].dropna()
        if not s.empty:
            stats_dict[col] = {
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": round(float(s.mean()), 4),
                "median": round(float(s.median()), 4),
                "std": round(float(s.std()), 4) if len(s) > 1 else 0.0,
            }
    return stats_dict
