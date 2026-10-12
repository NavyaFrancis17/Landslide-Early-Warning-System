"""
Tests for real dataset inspection module.
"""

from pathlib import Path
from landslide_early_warning.dataset_inspector import inspect_raw_dataset


def test_inspect_raw_dataset_glc():
    """Test that inspect_raw_dataset runs on the downloaded NASA Global Landslide Catalog dataset."""
    root_dir = Path(__file__).resolve().parent.parent
    raw_csv = root_dir / "data" / "raw" / "Global_Landslide_Catalog_Export.csv"
    assert raw_csv.exists(), "Raw dataset CSV must exist in data/raw/"

    report = inspect_raw_dataset(raw_csv)
    assert report["num_rows"] > 10000, "Dataset should have > 10,000 rows"
    assert report["num_columns"] == 31, "Dataset should have 31 columns"
    assert "latitude" in report["column_names"]
    assert "longitude" in report["column_names"]
    assert "event_date" in report["column_names"]
    assert report["duplicate_rows_count"] == 0
