"""
False Warning Event Analysis Module.

Analyzes actionable warning events (WARNING/HIGH_RISK) that failed to match
an actual historical landslide event under the spatial-temporal criteria.
"""

from typing import Any, Dict, List
import pandas as pd


def analyze_false_warning_events(
    false_warning_list: List[Dict[str, Any]],
    total_actionable_warnings: int,
) -> Dict[str, Any]:
    """
    Computes summary metrics for false warning events.

    Args:
        false_warning_list: List of false warning event dictionaries.
        total_actionable_warnings: Total actionable warning events evaluated.

    Returns:
        Dict[str, Any]: False alarm analysis dictionary.
    """
    false_count = len(false_warning_list)
    false_alarm_rate = (
        round(false_count / total_actionable_warnings, 4)
        if total_actionable_warnings > 0
        else 0.0
    )

    reasons_count: Dict[str, int] = {}
    for fw in false_warning_list:
        r = fw.get("false_alarm_reason", "NO_EVENT_MATCH")
        reasons_count[r] = reasons_count.get(r, 0) + 1

    return {
        "total_false_warning_events": false_count,
        "total_actionable_warnings_evaluated": total_actionable_warnings,
        "false_alarm_rate": false_alarm_rate,
        "false_alarm_reasons_breakdown": reasons_count,
    }
