"""
Data Leakage Prevention and Validation Module.

Programmatically identifies and excludes forbidden post-event outcome fields
and administrative metadata from model input feature sets.
"""

from typing import List, Set

# Master List of Forbidden Predictive Input Columns
FORBIDDEN_PREDICTIVE_COLUMNS: Set[str] = {
    "landslide_size",
    "fatality_count",
    "injury_count",
    "event_title",
    "event_description",
    "source_name",
    "source_link",
    "photo_link",
    "notes",
    "submitted_date",
    "created_date",
    "last_edited_date",
    "event_import_id",
    "event_import_source",
}


def assert_no_leakage_features(feature_list: List[str]) -> bool:
    """
    Validates that a list of candidate model input features contains zero forbidden leakage columns.

    Args:
        feature_list: List of feature column names.

    Returns:
        bool: True if clean.

    Raises:
        ValueError: If any forbidden column is found in candidate feature list.
    """
    found_leakage = [col for col in feature_list if col in FORBIDDEN_PREDICTIVE_COLUMNS]

    if found_leakage:
        raise ValueError(
            f"DATA LEAKAGE DETECTED! The following forbidden outcome/metadata fields "
            f"were found in model input features: {found_leakage}. "
            f"Refer to docs/data_leakage_notes.md for guidelines."
        )

    return True
