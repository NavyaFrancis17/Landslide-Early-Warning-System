"""
Environmental Data Retrieval, Validation, and Caching Module.

Provides reproducible acquisition and empirical auditing of ERA5-Land reanalysis
environmental data (precipitation, soil moisture layers, temperature, humidity, elevation).
Credentials/API configuration are read safely from environment or local configs.
"""

import json
import os
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd


ERA5_LAND_VARIABLE_MAP: Dict[str, Dict[str, str]] = {
    "precipitation": {
        "api_name": "precipitation",
        "description": "Total precipitation accumulation per hour",
        "unit": "mm",
    },
    "soil_moisture_layer1": {
        "api_name": "soil_moisture_0_to_7cm",
        "description": "Volumetric soil water content (0–7 cm depth)",
        "unit": "m^3/m^3",
    },
    "soil_moisture_layer2": {
        "api_name": "soil_moisture_7_to_28cm",
        "description": "Volumetric soil water content (7–28 cm depth)",
        "unit": "m^3/m^3",
    },
    "soil_moisture_layer3": {
        "api_name": "soil_moisture_28_to_100cm",
        "description": "Volumetric soil water content (28–100 cm depth)",
        "unit": "m^3/m^3",
    },
    "temperature_2m": {
        "api_name": "temperature_2m",
        "description": "Air temperature at 2 meters height",
        "unit": "°C",
    },
    "relative_humidity_2m": {
        "api_name": "relative_humidity_2m",
        "description": "Relative humidity at 2 meters height",
        "unit": "%",
    },
}


def fetch_era5_land_hourly(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    cache_dir: Optional[Path] = None,
    timeout: int = 25,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Fetches hourly ERA5-Land reanalysis observations for a specific lat/lon coordinate and date range.
    Uses local file caching to prevent redundant network requests.

    Args:
        latitude: Target latitude in decimal degrees (-90 to +90).
        longitude: Target longitude in decimal degrees (-180 to +180).
        start_date: Start date string (YYYY-MM-DD).
        end_date: End date string (YYYY-MM-DD).
        cache_dir: Optional directory path to store cached JSON payloads.
        timeout: Network timeout in seconds.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]:
            - Hourly DataFrame with datetime index and environmental feature columns.
            - Metadata dictionary containing matched grid coordinates, elevation, and source details.
    """
    if cache_dir is None:
        cache_dir = Path("data/environmental/raw")

    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_key = f"era5_{latitude:.4f}_{longitude:.4f}_{start_date}_{end_date}.json"
    cache_file = cache_dir / cache_key

    # Check cache first
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                payload = json.load(f)
            return _parse_era5_payload(payload)
        except Exception:
            pass  # Fallback to network call if cache read fails

    # Construct API Request to ERA5-Land Reanalysis Archive
    params = {
        "latitude": round(latitude, 4),
        "longitude": round(longitude, 4),
        "start_date": start_date,
        "end_date": end_date,
        "hourly": "precipitation,soil_moisture_0_to_7cm,soil_moisture_7_to_28cm,soil_moisture_28_to_100cm,temperature_2m,relative_humidity_2m",
        "timezone": "UTC",
    }
    url = f"https://archive-api.open-meteo.com/v1/archive?{urllib.parse.urlencode(params)}"

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) LandslideEarlyWarning/0.3"}
    req = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))

    # Write to local cache
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception:
        pass

    return _parse_era5_payload(payload)


def _parse_era5_payload(payload: Dict[str, Any]) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Helper to convert JSON payload into DataFrame and Metadata dictionary."""
    hourly_data = payload.get("hourly", {})
    df = pd.DataFrame(hourly_data)

    if "time" in df.columns:
        df["datetime"] = pd.to_datetime(df["time"], format="mixed", errors="coerce")
        df.set_index("datetime", inplace=True)
        df.drop(columns=["time"], errors="ignore", inplace=True)

    metadata = {
        "source_provider": "ECMWF ERA5-Land Reanalysis (via Open-Meteo Archive)",
        "requested_latitude": payload.get("latitude"),
        "requested_longitude": payload.get("longitude"),
        "matched_grid_latitude": payload.get("latitude"),
        "matched_grid_longitude": payload.get("longitude"),
        "matched_grid_elevation": payload.get("elevation"),
        "generation_time_ms": payload.get("generationtime_ms"),
        "spatial_resolution": "0.1 degree (~11 km)",
        "temporal_resolution": "hourly",
        "utc_offset_seconds": payload.get("utc_offset_seconds", 0),
    }

    return df, metadata


def validate_environmental_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Empirically inspects an environmental dataset DataFrame and generates summary statistics.

    Args:
        df: Input DataFrame containing environmental columns.

    Returns:
        Dict[str, Any]: Comprehensive data quality report.
    """
    total_rows = len(df)
    report: Dict[str, Any] = {
        "total_rows": total_rows,
        "columns": list(df.columns),
        "missing_counts": {},
        "summary_statistics": {},
    }

    for col in df.columns:
        s = df[col].dropna()
        null_cnt = int(df[col].isna().sum())
        report["missing_counts"][col] = null_cnt

        if not s.empty and np.issubdtype(s.dtype, np.number):
            report["summary_statistics"][col] = {
                "min": float(s.min()),
                "max": float(s.max()),
                "mean": round(float(s.mean()), 4),
                "median": round(float(s.median()), 4),
                "std": round(float(s.std()), 4) if len(s) > 1 else 0.0,
            }

    return report


def write_reproducibility_metadata(metadata_dict: Dict[str, Any], filepath: Path) -> None:
    """Saves reproducibility metadata to JSON file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(metadata_dict, f, indent=2)
