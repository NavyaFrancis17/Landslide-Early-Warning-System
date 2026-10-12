"""
Master Feature Matrix Pipeline & Phase 3 Visual Diagnostics Script.

Spatially and temporally aligns real landslide events with ERA5-Land reanalysis observations,
computes pre-event environmental features, creates data quality flags, enforces leakage exclusions,
exports data/processed/event_environment_features.csv, and generates diagnostic plots under docs/figures/phase3/.
"""

import json
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# Add src to module search path
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from landslide_early_warning.config_loader import load_config
from landslide_early_warning.environmental_data import write_reproducibility_metadata
from landslide_early_warning.feature_builder import build_event_environment_feature_matrix


def generate_phase3_diagnostic_plots(
    df: pd.DataFrame, output_dir: Path = Path("docs/figures/phase3")
) -> None:
    """Generates Phase 3 diagnostic plots and saves them as PNG files."""
    output_dir.mkdir(parents=True, exist_ok=True)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Event vs Grid Spatial Matching Scatter Plot
    if "landslide_latitude" in df.columns and "matched_env_latitude" in df.columns:
        valid_df = df.dropna(subset=["landslide_latitude", "matched_env_latitude"])
        if not valid_df.empty:
            fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
            ax.scatter(
                valid_df["landslide_longitude"], valid_df["landslide_latitude"],
                s=12, c="#1f77b4", alpha=0.5, label="Landslide Event Coordinates"
            )
            ax.scatter(
                valid_df["matched_env_longitude"], valid_df["matched_env_latitude"],
                s=6, c="#ff7f0e", alpha=0.3, label="Matched ERA5-Land Grid Coordinates"
            )
            ax.set_title("Landslide Event Locations vs Matched ERA5-Land Grid Coordinates", fontsize=12, fontweight="bold")
            ax.set_xlabel("Longitude (°)", fontsize=10)
            ax.set_ylabel("Latitude (°)", fontsize=10)
            ax.legend()
            plt.tight_layout()
            fig.savefig(output_dir / "event_vs_grid_matching.png")
            plt.close(fig)

    # 2. Spatial Distance Distribution Histogram
    if "spatial_distance_km" in df.columns:
        dist_s = df["spatial_distance_km"].dropna()
        if not dist_s.empty:
            fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
            ax.hist(dist_s, bins=30, color="#2ca02c", edgecolor="black", alpha=0.8)
            ax.set_title("Distribution of Spatial Matching Distances (Landslide to ERA5 Grid)", fontsize=12, fontweight="bold")
            ax.set_xlabel("Haversine Spatial Distance (km)", fontsize=10)
            ax.set_ylabel("Event Count", fontsize=10)
            ax.axvline(50.0, color="red", linestyle="--", label="Max Allowed Threshold (50 km)")
            ax.legend()
            plt.tight_layout()
            fig.savefig(output_dir / "spatial_distance_distribution.png")
            plt.close(fig)

    # 3. Pre-Event Rainfall Accumulation Histogram
    if "precipitation_24h" in df.columns and "precipitation_72h" in df.columns:
        precip_df = df[["precipitation_24h", "precipitation_72h"]].dropna()
        if not precip_df.empty:
            fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
            ax.hist(precip_df["precipitation_24h"], bins=30, alpha=0.6, label="24h Pre-Event Rainfall (mm)", color="#1f77b4")
            ax.hist(precip_df["precipitation_72h"], bins=30, alpha=0.5, label="72h Pre-Event Rainfall (mm)", color="#d62728")
            ax.set_title("Pre-Event Cumulative Precipitation Distributions (ERA5-Land)", fontsize=12, fontweight="bold")
            ax.set_xlabel("Accumulated Precipitation (mm)", fontsize=10)
            ax.set_ylabel("Event Count", fontsize=10)
            ax.set_yscale("log")
            ax.legend()
            plt.tight_layout()
            fig.savefig(output_dir / "preevent_rainfall_accumulation.png")
            plt.close(fig)

    # 4. Soil Moisture Distribution
    if "soil_moisture_layer1_current" in df.columns:
        sm_s = df["soil_moisture_layer1_current"].dropna()
        if not sm_s.empty:
            fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
            ax.hist(sm_s, bins=25, color="#8c564b", edgecolor="black", alpha=0.8)
            ax.set_title("Pre-Event Volumetric Soil Moisture Distribution (0–7 cm depth)", fontsize=12, fontweight="bold")
            ax.set_xlabel("Volumetric Soil Water Content (m^3 / m^3)", fontsize=10)
            ax.set_ylabel("Event Count", fontsize=10)
            plt.tight_layout()
            fig.savefig(output_dir / "soil_moisture_distribution.png")
            plt.close(fig)

    # 5. Quality Flags Summary
    flag_cols = [c for c in df.columns if c.endswith("_valid") or c.endswith("_flag") or c.endswith("_available")]
    if flag_cols:
        flag_summary = {}
        for fc in flag_cols:
            flag_summary[fc] = int(df[fc].value_counts().get(True, 0))

        fig, ax = plt.subplots(figsize=(9, 4.5), dpi=300)
        ax.barh(list(flag_summary.keys()), list(flag_summary.values()), color="#9467bd", edgecolor="black")
        ax.set_title("Phase 3 Data Quality Flags Summary", fontsize=12, fontweight="bold")
        ax.set_xlabel("Event Record Count (True)", fontsize=10)
        plt.tight_layout()
        fig.savefig(output_dir / "missing_flags_and_quality.png")
        plt.close(fig)


def main() -> int:
    """Executes Phase 3 feature builder pipeline."""
    root_dir = Path(__file__).resolve().parent
    config = load_config(root_dir / "config.yaml")

    clean_csv_path = root_dir / config.get("files", {}).get("processed_clean_csv", "data/processed/landslide_events_clean.csv")
    out_csv_path = root_dir / config.get("files", {}).get("event_environment_features_csv", "data/processed/event_environment_features.csv")

    max_dist_km = config.get("spatial_matching", {}).get("max_distance_km", 50.0)
    cutoff_hours = config.get("temporal_alignment", {}).get("prediction_cutoff_hours", 0)

    if not clean_csv_path.exists():
        print(f"Error: Processed clean dataset missing at: {clean_csv_path.resolve()}")
        return 1

    df_clean = pd.read_csv(clean_csv_path, low_memory=False)

    # Build master feature matrix
    master_df, report = build_event_environment_feature_matrix(
        landslide_df=df_clean,
        max_spatial_distance_km=max_dist_km,
        prediction_cutoff_hours=cutoff_hours,
        cache_dir=root_dir / "data" / "environmental" / "raw",
    )

    out_csv_path.parent.mkdir(parents=True, exist_ok=True)
    master_df.to_csv(out_csv_path, index=False)
    print(f"\nSuccessfully generated feature matrix: {out_csv_path.resolve()}")
    print(f"Feature Matrix Shape: {master_df.shape[0]:,} rows x {master_df.shape[1]} columns.")

    # Save reproducibility metadata JSON
    meta_path = root_dir / "data" / "environmental" / "metadata" / "phase3_feature_builder_metadata.json"
    write_reproducibility_metadata(report, meta_path)
    print(f"Saved Reproducibility Metadata: {meta_path.resolve()}")

    # Generate diagnostic plots
    fig_dir = root_dir / "docs" / "figures" / "phase3"
    generate_phase3_diagnostic_plots(master_df, output_dir=fig_dir)
    print(f"Generated Phase 3 Diagnostic Plots under: {fig_dir.resolve()}")

    print("\n" + "=" * 70)
    print("PHASE 3 FEATURE BUILDER PIPELINE COMPLETED SUCCESSFULLY.")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
