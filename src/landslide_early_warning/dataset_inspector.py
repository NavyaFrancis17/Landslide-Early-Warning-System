"""
Dataset Inspection and Validation Module.

Performs empirical inspection and summary reporting of the real primary dataset
(NASA Global Landslide Catalog) stored in data/raw/ without model training or data fabrication.
"""

from pathlib import Path
from typing import Any, Dict, List
import numpy as np
import pandas as pd


def inspect_raw_dataset(csv_path: Path) -> Dict[str, Any]:
    """
    Reads and inspects the raw CSV dataset, generating a comprehensive validation report.

    Args:
        csv_path: Path to the raw CSV file.

    Returns:
        Dict[str, Any]: Detailed inspection dictionary containing metrics, types, ranges,
                        missing counts, date ranges, and unique location counts.
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"Raw dataset file not found at: {csv_path.resolve()}")

    # Ingest raw dataset
    df = pd.read_csv(csv_path, low_memory=False)

    num_rows, num_cols = df.shape
    duplicate_rows = int(df.duplicated().sum())

    # Column details & data types
    cols_info: List[Dict[str, Any]] = []
    missing_counts: Dict[str, int] = {}
    dtypes_dict: Dict[str, str] = {}

    for col in df.columns:
        dt = str(df[col].dtype)
        dtypes_dict[col] = dt
        null_cnt = int(df[col].isnull().sum())
        missing_counts[col] = null_cnt
        cols_info.append({
            "column": col,
            "dtype": dt,
            "missing_count": null_cnt,
            "missing_percentage": round((null_cnt / num_rows) * 100, 2)
        })

    # Date range parsing (from event_date column if present)
    date_range: Dict[str, Any] = {"min_date": None, "max_date": None, "valid_dates_count": 0}
    if "event_date" in df.columns:
        try:
            parsed_dates = pd.to_datetime(df["event_date"], errors="coerce")
            valid_dates = parsed_dates.dropna()
            if not valid_dates.empty:
                date_range["min_date"] = str(valid_dates.min().date())
                date_range["max_date"] = str(valid_dates.max().date())
                date_range["valid_dates_count"] = len(valid_dates)
        except Exception:
            pass

    # Unique locations count
    unique_locations_count = 0
    if "latitude" in df.columns and "longitude" in df.columns:
        valid_coords = df.dropna(subset=["latitude", "longitude"])
        unique_locations_count = len(valid_coords.groupby(["latitude", "longitude"]))
    elif "location_description" in df.columns:
        unique_locations_count = int(df["location_description"].nunique())

    # Landslide event records count
    landslide_event_count = num_rows  # All entries in GLC catalog represent recorded landslide events
    if "landslide_category" in df.columns:
        category_counts = df["landslide_category"].value_counts(dropna=False).to_dict()
    else:
        category_counts = {}

    # Numerical ranges summary
    numerical_summary: Dict[str, Dict[str, float]] = {}
    num_cols_list = df.select_dtypes(include=[np.number]).columns
    for num_col in num_cols_list:
        valid_s = df[num_col].dropna()
        if not valid_s.empty:
            numerical_summary[num_col] = {
                "min": float(valid_s.min()),
                "max": float(valid_s.max()),
                "mean": round(float(valid_s.mean()), 4),
                "std": round(float(valid_s.std()), 4) if len(valid_s) > 1 else 0.0,
            }

    return {
        "dataset_name": csv_path.name,
        "num_rows": num_rows,
        "num_columns": num_cols,
        "column_names": list(df.columns),
        "data_types": dtypes_dict,
        "missing_value_counts": missing_counts,
        "duplicate_rows_count": duplicate_rows,
        "date_range": date_range,
        "unique_locations_count": unique_locations_count,
        "landslide_event_records_count": landslide_event_count,
        "category_breakdown": category_counts,
        "numerical_ranges": numerical_summary,
    }


def format_inspection_report(report: Dict[str, Any]) -> str:
    """Formats the inspection report dictionary into a clean terminal/markdown summary."""
    lines: List[str] = [
        "=" * 70,
        "RAW DATASET INSPECTION REPORT",
        "=" * 70,
        f"Dataset File: {report['dataset_name']}",
        f"Total Rows: {report['num_rows']:,}",
        f"Total Columns: {report['num_columns']}",
        f"Duplicate Rows: {report['duplicate_rows_count']:,}",
        f"Unique Geographic Locations (Lat/Lon Pairs): {report['unique_locations_count']:,}",
        f"Total Confirmed Landslide Event Records: {report['landslide_event_records_count']:,}",
        "-" * 70,
        "TEMPORAL COVERAGE (event_date):",
        f"  Start Date: {report['date_range'].get('min_date', 'N/A')}",
        f"  End Date:   {report['date_range'].get('max_date', 'N/A')}",
        f"  Parsed Event Dates: {report['date_range'].get('valid_dates_count', 0):,} / {report['num_rows']:,}",
        "-" * 70,
        "COLUMN MISSING-VALUE SUMMARY:",
    ]

    for col, count in report["missing_value_counts"].items():
        pct = (count / report["num_rows"]) * 100
        dtype = report["data_types"][col]
        lines.append(f"  - {col:<30} ({dtype:<8}): {count:>6,} missing ({pct:>5.1f}%)")

    lines.append("-" * 70)
    lines.append("NUMERICAL RANGES SUMMARY:")
    for num_col, stats in report["numerical_ranges"].items():
        lines.append(
            f"  - {num_col:<28}: Min={stats['min']:<10.2f} Max={stats['max']:<10.2f} "
            f"Mean={stats['mean']:<10.2f} Std={stats['std']:<10.2f}"
        )

    lines.append("=" * 70)
    return "\n".join(lines)
