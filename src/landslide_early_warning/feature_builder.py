"""
Master Feature Builder Engine Module.

Spatially and temporally merges real landslide event records with ERA5-Land reanalysis observations,
calculates pre-event environmental features, computes spatial distances, assigns quality flags,
and outputs the primary ML dataset foundation (data/processed/event_environment_features.csv).
"""

import concurrent.futures
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

from landslide_early_warning.environmental_data import (
    fetch_era5_land_hourly,
    write_reproducibility_metadata,
)
from landslide_early_warning.leakage import assert_no_leakage_features
from landslide_early_warning.spatial_matching import (
    calculate_haversine_distance,
    validate_spatial_distance,
)
from landslide_early_warning.temporal_alignment import compute_preevent_features


def _process_single_event(args: Tuple[int, pd.Series, float, int, Path]) -> Dict[str, Any]:
    idx, row, max_spatial_distance_km, prediction_cutoff_hours, cache_dir = args

    event_id = row.get("event_id")
    lat = float(row["latitude"])
    lon = float(row["longitude"])

    raw_date_str = str(row.get("event_date", ""))
    event_dt_str = str(row.get("event_datetime", ""))

    row_dict: Dict[str, Any] = {
        "event_id": event_id,
        "landslide_category": row.get("landslide_category"),
        "landslide_trigger": row.get("landslide_trigger"),
        "landslide_latitude": lat,
        "landslide_longitude": lon,
        "event_date": raw_date_str,
        "event_datetime": event_dt_str,
        "event_year": row.get("event_year"),
        "event_month": row.get("event_month"),
        "event_day": row.get("event_day"),
        "event_day_of_year": row.get("event_day_of_year"),
        "season": row.get("season"),
        "country_name": row.get("country_name"),
        "admin_division_population": row.get("admin_division_population"),
    }

    event_ts = pd.to_datetime(event_dt_str, errors="coerce")
    if pd.isna(event_ts):
        event_ts = pd.to_datetime(raw_date_str, format="mixed", errors="coerce")

    if pd.isna(event_ts):
        row_dict.update({
            "matched_env_latitude": None,
            "matched_env_longitude": None,
            "spatial_distance_km": None,
            "environmental_data_available": False,
            "spatial_match_valid": False,
            "temporal_match_valid": False,
            "excessive_spatial_distance": False,
            "incomplete_history_flag": True,
        })
        return row_dict

    start_date = (event_ts - pd.Timedelta(days=8)).strftime("%Y-%m-%d")
    end_date = (event_ts + pd.Timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        env_df, env_meta = fetch_era5_land_hourly(
            latitude=lat,
            longitude=lon,
            start_date=start_date,
            end_date=end_date,
            cache_dir=cache_dir,
        )

        matched_lat = float(env_meta["matched_grid_latitude"])
        matched_lon = float(env_meta["matched_grid_longitude"])
        grid_elev = env_meta.get("matched_grid_elevation")

        dist_km = calculate_haversine_distance(lat, lon, matched_lat, matched_lon)
        spatial_valid = dist_km <= max_spatial_distance_km

        preevent_feats = compute_preevent_features(
            env_df, event_ts, prediction_cutoff_hours=prediction_cutoff_hours
        )

        row_dict.update({
            "matched_env_latitude": matched_lat,
            "matched_env_longitude": matched_lon,
            "matched_grid_elevation": grid_elev,
            "spatial_distance_km": round(dist_km, 4),
            "environmental_data_available": True,
            "spatial_match_valid": spatial_valid,
            "excessive_spatial_distance": not spatial_valid,
            "incomplete_history_flag": not preevent_feats.get("temporal_match_valid", False),
        })
        row_dict.update(preevent_feats)

    except Exception:
        row_dict.update({
            "matched_env_latitude": None,
            "matched_env_longitude": None,
            "spatial_distance_km": None,
            "environmental_data_available": False,
            "spatial_match_valid": False,
            "temporal_match_valid": False,
            "excessive_spatial_distance": False,
            "incomplete_history_flag": True,
        })

    return row_dict


def build_event_environment_feature_matrix(
    landslide_df: pd.DataFrame,
    max_spatial_distance_km: float = 50.0,
    prediction_cutoff_hours: int = 0,
    cache_dir: Optional[Path] = None,
    max_workers: int = 16,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Constructs the event-centered environmental feature dataset in parallel.

    Args:
        landslide_df: Cleaned landslide events DataFrame.
        max_spatial_distance_km: Maximum acceptable distance threshold in km.
        prediction_cutoff_hours: Prediction cutoff offset in hours.
        cache_dir: Cache directory path for environmental payloads.
        max_workers: ThreadPoolExecutor worker count.

    Returns:
        Tuple[pd.DataFrame, Dict[str, Any]]:
            - Master feature DataFrame (event_environment_features.csv).
            - Pipeline summary report dictionary.
    """
    if cache_dir is None:
        cache_dir = Path("data/environmental/raw")

    cache_dir.mkdir(parents=True, exist_ok=True)

    print(f"Building feature matrix for {len(landslide_df):,} landslide events using {max_workers} parallel workers...")

    tasks = [
        (idx, row, max_spatial_distance_km, prediction_cutoff_hours, cache_dir)
        for idx, row in landslide_df.iterrows()
    ]

    feature_rows: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(_process_single_event, tasks))
        feature_rows.extend(results)

    master_df = pd.DataFrame(feature_rows)

    # Count summary metrics
    matched_count = int(master_df["environmental_data_available"].sum())
    missing_env_count = len(master_df) - matched_count
    flagged_distance_count = int(master_df["excessive_spatial_distance"].sum())

    # Validate zero data leakage columns in generated feature set
    predictive_candidates = [
        c for c in master_df.columns
        if c not in ["event_id", "landslide_category", "landslide_trigger"]
    ]
    assert_no_leakage_features(predictive_candidates)

    report = {
        "total_events": len(landslide_df),
        "successfully_matched_events": matched_count,
        "missing_environmental_events": missing_env_count,
        "excessive_distance_flagged": flagged_distance_count,
        "max_spatial_distance_allowed_km": max_spatial_distance_km,
        "total_features_generated": len(master_df.columns),
    }

    return master_df, report
