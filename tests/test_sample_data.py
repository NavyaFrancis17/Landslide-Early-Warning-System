"""
Tests for sample environmental data dataset loading and schema verification.
"""

from pathlib import Path
import pandas as pd
from landslide_early_warning.validator import (
    REQUIRED_SAMPLE_COLUMNS,
    verify_sample_data,
)


def test_sample_csv_reading():
    """Test that sample_environmental_data.csv can be read successfully by pandas."""
    root_dir = Path(__file__).resolve().parent.parent
    sample_csv = root_dir / "data" / "sample" / "sample_environmental_data.csv"
    assert sample_csv.exists(), "Sample CSV file must exist"

    df = pd.read_csv(sample_csv, comment="#")
    assert not df.empty, "Sample CSV dataframe must not be empty"


def test_sample_csv_columns():
    """Test that sample CSV contains all required environmental & event schema columns."""
    root_dir = Path(__file__).resolve().parent.parent
    sample_csv = root_dir / "data" / "sample" / "sample_environmental_data.csv"

    df = pd.read_csv(sample_csv, comment="#")
    for col in REQUIRED_SAMPLE_COLUMNS:
        assert col in df.columns, f"Required column '{col}' missing from sample CSV"


def test_sample_csv_validator_function():
    """Test validator function for sample data."""
    root_dir = Path(__file__).resolve().parent.parent
    sample_csv = root_dir / "data" / "sample" / "sample_environmental_data.csv"
    valid, message = verify_sample_data(sample_csv)
    assert valid, f"Sample data verification failed: {message}"
