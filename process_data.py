"""
Data Processing Pipeline Script — Phase 2.

Ingests data/raw/Global_Landslide_Catalog_Export.csv, runs schema & coordinate validation,
parses event dates, extracts temporal features, generates processed dataset CSVs under data/processed/,
and triggers EDA plot generation under docs/figures/.
"""

import sys
from pathlib import Path

# Add src to module search path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from landslide_early_warning.config_loader import load_config
from landslide_early_warning.data_quality import (
    compute_numerical_ranges,
    detect_duplicates,
    profile_missing_values,
    validate_coordinates,
)
from landslide_early_warning.eda import generate_eda_plots
from landslide_early_warning.temporal_features import (
    extract_temporal_components,
    parse_event_dates,
    sort_chronologically,
)


def run_pipeline() -> int:
    """Executes the Phase 2 data processing pipeline."""
    root_dir = Path(__file__).resolve().parent
    config = load_config(root_dir / "config.yaml")

    raw_rel = config.get("paths", {}).get("raw_data", "data/raw")
    processed_rel = config.get("paths", {}).get("processed_data", "data/processed")

    raw_csv = root_dir / raw_rel / "Global_Landslide_Catalog_Export.csv"
    processed_dir = root_dir / processed_rel
    processed_dir.mkdir(parents=True, exist_ok=True)

    if not raw_csv.exists():
        print(f"Pipeline Error: Raw CSV missing at {raw_csv.resolve()}")
        return 1

    print("=" * 70)
    print("PHASE 2 DATA PROCESSING PIPELINE EXECUTION")
    print("=" * 70)
    print(f"Source Dataset: {raw_csv.resolve()}")

    # 1. Ingest Raw Dataset (Preserve original intact)
    import pandas as pd
    df_raw = pd.read_csv(raw_csv, low_memory=False)
    print(f"Loaded Raw Dataset: {len(df_raw):,} rows, {len(df_raw.columns)} columns.")

    # 2. Quality Audits
    coord_report = validate_coordinates(df_raw)
    print(f"Coordinate Validation: {coord_report['valid_coordinates_count']:,} / {len(df_raw):,} valid coordinates.")
    print(f"Unique Lat/Lon Pairs: {coord_report['unique_location_pairs']:,}")

    # 3. Temporal Processing
    date_series, date_metrics = parse_event_dates(df_raw, date_col="event_date")
    print(f"Parsed Event Dates: {date_metrics['valid_date_count']:,} valid dates ({date_metrics['valid_date_percentage']}%).")

    df_clean = extract_temporal_components(df_raw, date_series)

    # 4. Save Clean Processed Dataset (All records with extracted features)
    clean_csv_path = processed_dir / "landslide_events_clean.csv"
    df_clean.to_csv(clean_csv_path, index=False)
    print(f"Saved Processed Clean Dataset: {clean_csv_path.resolve()} ({len(df_clean):,} rows)")

    # 5. Save Temporal Subset (Only valid dates, chronologically sorted)
    df_temporal = df_clean[df_clean["event_datetime"].notna()].copy()
    df_temporal = sort_chronologically(df_temporal, datetime_col="event_datetime")

    temporal_csv_path = processed_dir / "landslide_events_temporal.csv"
    df_temporal.to_csv(temporal_csv_path, index=False)
    print(f"Saved Processed Temporal Dataset: {temporal_csv_path.resolve()} ({len(df_temporal):,} rows)")

    # 6. Generate EDA Figures
    fig_dir = root_dir / "docs" / "figures"
    saved_figures = generate_eda_plots(df_clean, output_dir=fig_dir)
    print(f"Generated {len(saved_figures)} EDA plots in {fig_dir.resolve()}:")
    for fig_name, fig_path in saved_figures.items():
        print(f"  - {fig_name}: {fig_path.name}")

    print("=" * 70)
    print("PHASE 2 PIPELINE COMPLETED SUCCESSFULLY.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(run_pipeline())
