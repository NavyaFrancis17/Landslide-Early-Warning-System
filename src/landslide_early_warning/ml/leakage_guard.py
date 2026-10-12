"""
Automated Data Leakage Guard Module for Phase 4 Machine Learning.

Enforces zero-tolerance validation against forbidden post-event outcome variables,
administrative timestamps, and future environmental lookahead variables.
"""

from typing import List, Set
import pandas as pd

from landslide_early_warning.leakage import FORBIDDEN_PREDICTIVE_COLUMNS


def verify_feature_matrix_leakage_free(df: pd.DataFrame) -> bool:
    """
    Programmatically verifies that a candidate model feature matrix contains zero leakage columns.

    Args:
        df: Candidate feature matrix DataFrame.

    Returns:
        bool: True if clean.

    Raises:
        ValueError: If any forbidden column or post-event field is detected.
    """
    found = [c for c in df.columns if c in FORBIDDEN_PREDICTIVE_COLUMNS]
    if found:
        raise ValueError(
            f"LEAKAGE GUARD FAILURE! Prohibited outcome/metadata columns detected in model feature matrix: {found}."
        )

    # Check for post-event timestamp string patterns in feature column names
    forbidden_time_keywords = ["after_event", "post_event", "future_", "submitted_", "created_"]
    suspicious_cols = [
        c for c in df.columns
        if any(kw in c.lower() for kw in forbidden_time_keywords)
    ]
    if suspicious_cols:
        raise ValueError(
            f"LEAKAGE GUARD FAILURE! Suspicious post-event feature columns detected: {suspicious_cols}."
        )

    return True
