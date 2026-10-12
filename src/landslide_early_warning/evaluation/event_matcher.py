"""
Optimized Deterministic Spatial-Temporal Event Matching Engine.
"""

from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd

from landslide_early_warning.evaluation.lead_time import calculate_lead_time_metrics
from landslide_early_warning.spatial_matching import calculate_haversine_distance


STATE_RANKS: Dict[str, int] = {
    "NORMAL": 0,
    "WATCH": 1,
    "WARNING": 2,
    "HIGH_RISK": 3,
}


def match_warning_events_to_landslides(
    warning_events_df: pd.DataFrame,
    landslide_events_df: pd.DataFrame,
    location_coords_map: Dict[str, Tuple[float, float]],
    max_distance_km: float = 50.0,
    max_lead_time_hours: float = 168.0,
    actionable_states: List[str] = None,
) -> Tuple[pd.DataFrame, List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Executes fast, vectorized 1-to-1 deterministic spatial-temporal event matching.
    """
    if actionable_states is None:
        actionable_states = ["WARNING", "HIGH_RISK"]

    actionable_warnings = warning_events_df[
        warning_events_df["maximum_state"].isin(actionable_states)
    ].copy()

    # Parse timestamps
    landslide_events_df["event_ts"] = pd.to_datetime(
        landslide_events_df["event_datetime"], format="mixed", errors="coerce"
    )
    invalid_mask = landslide_events_df["event_ts"].isna()
    if invalid_mask.any():
        landslide_events_df.loc[invalid_mask, "event_ts"] = pd.to_datetime(
            landslide_events_df.loc[invalid_mask, "event_date"], format="mixed", errors="coerce"
        )

    actionable_warnings["warn_start_ts"] = pd.to_datetime(
        actionable_warnings["warning_start_time"], format="mixed", errors="coerce"
    )

    # Pre-extract arrays for fast bounding box filtering
    e_lats = landslide_events_df["latitude"].values
    e_lons = landslide_events_df["longitude"].values
    e_ids = landslide_events_df["event_id"].values
    e_tss = landslide_events_df["event_ts"].values

    candidate_pairs = []
    lat_deg_bound = max_distance_km / 111.0
    lon_deg_bound = max_distance_km / 80.0

    for w_idx, w_row in actionable_warnings.iterrows():
        w_id = w_row["warning_event_id"]
        loc_id = w_row["location_id"]
        w_start_ts = w_row["warn_start_ts"]
        max_st = w_row["maximum_state"]

        if loc_id in location_coords_map:
            w_lat, w_lon = location_coords_map[loc_id]
        else:
            try:
                parts = loc_id.split("_")
                w_lat, w_lon = float(parts[1]), float(parts[2])
            except Exception:
                continue

        if pd.isna(w_start_ts):
            continue

        # Fast bounding box pre-filtering
        lat_mask = np.abs(e_lats - w_lat) <= lat_deg_bound
        lon_mask = np.abs(e_lons - w_lon) <= lon_deg_bound
        spatial_candidates_idx = np.where(lat_mask & lon_mask)[0]

        for e_idx in spatial_candidates_idx:
            e_id = e_ids[e_idx]
            e_ts = pd.Timestamp(e_tss[e_idx])
            e_lat = float(e_lats[e_idx])
            e_lon = float(e_lons[e_idx])

            if pd.isna(e_ts):
                continue

            dist_km = calculate_haversine_distance(w_lat, w_lon, e_lat, e_lon)
            if dist_km > max_distance_km:
                continue

            lead_h, lead_d, is_valid_pre = calculate_lead_time_metrics(w_start_ts, e_ts)

            if lead_h <= 0.0:
                match_status = "POST_EVENT_WARNING"
            elif lead_h > max_lead_time_hours:
                match_status = "NO_TEMPORAL_MATCH"
            else:
                match_status = "MATCHED"

            candidate_pairs.append({
                "warning_event_id": w_id,
                "landslide_event_id": e_id,
                "location_id": loc_id,
                "warning_start_time": str(w_start_ts),
                "event_time": str(e_ts),
                "warning_state": w_row.get("initial_state"),
                "maximum_warning_state": max_st,
                "distance_km": round(dist_km, 4),
                "lead_time_hours": lead_h,
                "lead_time_days": lead_d,
                "match_status": match_status,
                "state_rank": STATE_RANKS.get(max_st, 0),
                "warning_lat": w_lat,
                "warning_lon": w_lon,
                "event_lat": e_lat,
                "event_lon": e_lon,
            })

    # Sort candidate pairs deterministically
    valid_candidates = [c for c in candidate_pairs if c["match_status"] == "MATCHED"]
    valid_candidates.sort(
        key=lambda x: (x["distance_km"], -x["state_rank"], abs(x["lead_time_hours"] - 24.0))
    )

    # 1-to-1 Deterministic Matching Assignment
    matched_warning_ids = set()
    matched_event_ids = set()
    matched_pairs = []

    for cand in valid_candidates:
        w_id = cand["warning_event_id"]
        e_id = cand["landslide_event_id"]

        if w_id not in matched_warning_ids and e_id not in matched_event_ids:
            matched_warning_ids.add(w_id)
            matched_event_ids.add(e_id)
            cand["match_reason"] = "Valid pre-event 1-to-1 spatial-temporal match"
            matched_pairs.append(cand)

    # Detected events list
    detected_events = []
    for m in matched_pairs:
        detected_events.append({
            "event_id": m["landslide_event_id"],
            "event_time": m["event_time"],
            "event_latitude": m["event_lat"],
            "event_longitude": m["event_lon"],
            "matched_warning_event_id": m["warning_event_id"],
            "warning_start_time": m["warning_start_time"],
            "warning_state": m["maximum_warning_state"],
            "lead_time_hours": m["lead_time_hours"],
            "lead_time_days": m["lead_time_days"],
            "distance_km": m["distance_km"],
        })

    # Missed events list
    missed_events = []
    for e_idx, e_row in landslide_events_df.iterrows():
        e_id = e_row["event_id"]
        if e_id not in matched_event_ids:
            e_ts = e_row.get("event_ts")
            missed_events.append({
                "event_id": e_id,
                "event_time": str(e_ts) if pd.notna(e_ts) else str(e_row.get("event_date")),
                "latitude": float(e_row["latitude"]),
                "longitude": float(e_row["longitude"]),
                "miss_reason": "NO_MATCHED_ACTIONABLE_PRE_EVENT_WARNING",
            })

    # False warning events list
    false_warnings = []
    for w_idx, w_row in actionable_warnings.iterrows():
        w_id = w_row["warning_event_id"]
        if w_id not in matched_warning_ids:
            false_warnings.append({
                "warning_event_id": w_id,
                "location_id": w_row["location_id"],
                "warning_start_time": str(w_row["warning_start_time"]),
                "maximum_warning_state": w_row["maximum_state"],
                "observation_duration": w_row.get("observation_duration", 1),
                "false_alarm_reason": "NO_PREDICTED_LANDSLIDE_EVENT_MATCHED",
            })

    full_matches_df = pd.DataFrame(matched_pairs if matched_pairs else candidate_pairs)
    return full_matches_df, detected_events, missed_events, false_warnings
