"""
Dataset Inspection Entrypoint Script.

Executes dataset analysis on data/raw/Global_Landslide_Catalog_Export.csv
and outputs comprehensive validation metrics.
"""

import sys
from pathlib import Path

# Add src directory to search path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from landslide_early_warning.dataset_inspector import (
    format_inspection_report,
    inspect_raw_dataset,
)


def main() -> int:
    """Runs raw dataset inspection and displays summary results."""
    root_dir = Path(__file__).resolve().parent
    raw_csv = root_dir / "data" / "raw" / "Global_Landslide_Catalog_Export.csv"

    if not raw_csv.exists():
        print(f"Error: Raw dataset file does not exist at: {raw_csv.resolve()}")
        print("Please download the raw dataset into data/raw/ before running inspection.")
        return 1

    try:
        report = inspect_raw_dataset(raw_csv)
        report_text = format_inspection_report(report)
        print(report_text)
        return 0
    except Exception as exc:
        print(f"Dataset inspection failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
