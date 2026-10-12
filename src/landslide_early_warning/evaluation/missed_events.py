"""
Missed Landslide Event Analysis Module.

Analyzes actual historical catalog landslide events for which no preceding
actionable warning match was found under spatial-temporal criteria.
"""

from typing import Any, Dict, List
import pandas as pd


def analyze_missed_landslide_events(
    missed_events_list: List[Dict[str, Any]],
    total_evaluable_actual_events: int,
) -> Dict[str, Any]:
    """
    Computes summary metrics for missed landslide events.

    Args:
        missed_events_list: List of missed event dictionaries.
        total_evaluable_actual_events: Total actual landslide events evaluated.

    Returns:
        Dict[str, Any]: Missed event analysis dictionary.
    """
    missed_count = len(missed_events_list)
    miss_rate = (
        round(missed_count / total_evaluable_actual_events, 4)
        if total_evaluable_actual_events > 0
        else 0.0
    )

    reasons_count: Dict[str, int] = {}
    for me in missed_events_list:
        r = me.get("miss_reason", "NO_WARNING")
        reasons_count[r] = reasons_count.get(r, 0) + 1

    return {
        "total_missed_landslide_events": missed_count,
        "total_evaluable_actual_events": total_evaluable_actual_events,
        "miss_rate": miss_rate,
        "miss_reasons_breakdown": reasons_count,
    }
