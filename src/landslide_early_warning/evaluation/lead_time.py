"""
Lead-Time Calculation and Statistical Analysis Module.

Computes exact lead times (hours and days) between warning initiation timestamps
and actual landslide event timestamps (lead_time = event_time - warning_start_time).
Calculates distribution statistics (min, max, mean, median, percentiles) and bucket counts.
"""

from datetime import datetime
from typing import Any, Dict, List, Tuple
import numpy as np
import pandas as pd


def calculate_lead_time_metrics(
    warning_start_time: pd.Timestamp,
    event_time: pd.Timestamp,
) -> Tuple[float, float, bool]:
    """
    Calculates lead time in hours and days between warning start and actual landslide event.

    Args:
        warning_start_time: Timestamp when actionable warning started.
        event_time: Timestamp when actual landslide event occurred.

    Returns:
        Tuple[float, float, bool]: (lead_time_hours, lead_time_days, is_valid_pre_event)
    """
    if pd.isna(warning_start_time) or pd.isna(event_time):
        return 0.0, 0.0, False

    diff_sec = (event_time - warning_start_time).total_seconds()
    lead_hours = diff_sec / 3600.0
    lead_days = lead_hours / 24.0
    is_valid_pre_event = lead_hours > 0.0

    return round(lead_hours, 2), round(lead_days, 2), is_valid_pre_event


def compute_lead_time_distribution_statistics(
    lead_times_hours: List[float],
) -> Dict[str, Any]:
    """
    Computes statistical metrics and distribution bucket counts for valid lead times.

    Args:
        lead_times_hours: List of lead times in hours for matched events.

    Returns:
        Dict[str, Any]: Summary statistics dictionary.
    """
    valid_lt = [float(lt) for lt in lead_times_hours if lt > 0.0]

    if not valid_lt:
        return {
            "matched_events_count": 0,
            "min_lead_time_hours": 0.0,
            "max_lead_time_hours": 0.0,
            "mean_lead_time_hours": 0.0,
            "median_lead_time_hours": 0.0,
            "std_lead_time_hours": 0.0,
            "p25_lead_time_hours": 0.0,
            "p75_lead_time_hours": 0.0,
            "bucket_counts": {
                "less_than_1h": 0,
                "hours_1_to_6": 0,
                "hours_6_to_12": 0,
                "hours_12_to_24": 0,
                "days_1_to_3": 0,
                "days_3_to_7": 0,
            },
        }

    arr = np.array(valid_lt)
    buckets = {
        "less_than_1h": int(np.sum((arr > 0.0) & (arr <= 1.0))),
        "hours_1_to_6": int(np.sum((arr > 1.0) & (arr <= 6.0))),
        "hours_6_to_12": int(np.sum((arr > 6.0) & (arr <= 12.0))),
        "hours_12_to_24": int(np.sum((arr > 12.0) & (arr <= 24.0))),
        "days_1_to_3": int(np.sum((arr > 24.0) & (arr <= 72.0))),
        "days_3_to_7": int(np.sum((arr > 72.0) & (arr <= 168.0))),
    }

    return {
        "matched_events_count": len(valid_lt),
        "min_lead_time_hours": round(float(np.min(arr)), 2),
        "max_lead_time_hours": round(float(np.max(arr)), 2),
        "mean_lead_time_hours": round(float(np.mean(arr)), 2),
        "median_lead_time_hours": round(float(np.median(arr)), 2),
        "std_lead_time_hours": round(float(np.std(arr)), 2),
        "p25_lead_time_hours": round(float(np.percentile(arr, 25)), 2),
        "p75_lead_time_hours": round(float(np.percentile(arr, 75)), 2),
        "bucket_counts": buckets,
    }
