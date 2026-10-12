"""
Event-Level Evaluation Metrics Calculator Module.

Calculates core research metrics: Event Detection Rate, Warning Precision,
Miss Rate, and Event F1-Score with zero-division safety guards.
"""

from typing import Any, Dict, Optional
import numpy as np


def compute_event_evaluation_metrics(
    total_actual_events: int,
    detected_events_count: int,
    missed_events_count: int,
    total_actionable_warnings: int,
    matched_warnings_count: int,
    false_warnings_count: int,
) -> Dict[str, Any]:
    """
    Computes event-level evaluation metrics.

    Args:
        total_actual_events: Total actual landslide events evaluated.
        detected_events_count: Number of successfully detected landslide events.
        missed_events_count: Number of missed landslide events.
        total_actionable_warnings: Total actionable warning events evaluated.
        matched_warnings_count: Number of matched warning events.
        false_warnings_count: Number of false warning events.

    Returns:
        Dict[str, Any]: Metrics dictionary.
    """
    # Safe division guards
    if total_actual_events > 0:
        detection_rate = round(detected_events_count / total_actual_events, 4)
        miss_rate = round(missed_events_count / total_actual_events, 4)
    else:
        detection_rate = np.nan
        miss_rate = np.nan

    if total_actionable_warnings > 0:
        warning_precision = round(matched_warnings_count / total_actionable_warnings, 4)
    else:
        warning_precision = np.nan

    if (
        pd_notna(warning_precision)
        and pd_notna(detection_rate)
        and (warning_precision + detection_rate) > 0
    ):
        event_f1 = round(
            2.0 * (warning_precision * detection_rate) / (warning_precision + detection_rate),
            4,
        )
    else:
        event_f1 = np.nan

    return {
        "total_actual_events_evaluated": total_actual_events,
        "detected_landslide_events": detected_events_count,
        "missed_landslide_events": missed_events_count,
        "total_actionable_warnings_evaluated": total_actionable_warnings,
        "matched_warning_events": matched_warnings_count,
        "false_warning_events": false_warnings_count,
        "event_detection_rate": detection_rate,
        "warning_precision": warning_precision,
        "miss_rate": miss_rate,
        "event_f1_score": event_f1,
    }


def pd_notna(val: Any) -> bool:
    """Helper to check non-nan float values."""
    if val is None:
        return False
    try:
        return not np.isnan(float(val))
    except Exception:
        return False
