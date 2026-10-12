"""
Exploratory Data Analysis (EDA) Visualization Module.

Generates publication-ready figures for data quality, temporal trends,
and geographic distributions, saving outputs under docs/figures/.
"""

from pathlib import Path
from typing import Dict, Optional
import matplotlib
matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd


def generate_eda_plots(
    df: pd.DataFrame, output_dir: Path = Path("docs/figures")
) -> Dict[str, Path]:
    """
    Generates EDA plots supported by actual raw dataset fields and saves them as PNG files.

    Args:
        df: Pandas DataFrame containing dataset records.
        output_dir: Directory path to save generated PNG figures.

    Returns:
        Dict[str, Path]: Dictionary mapping figure names to their saved file paths.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_plots: Dict[str, Path] = {}

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # 1. Events by Year Plot
    if "event_year" in df.columns:
        year_counts = df["event_year"].dropna().astype(int).value_counts().sort_index()
        if not year_counts.empty:
            fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
            year_counts.plot(kind="bar", ax=ax, color="#1f77b4", edgecolor="black")
            ax.set_title("Landslide Events by Year (NASA Global Landslide Catalog)", fontsize=13, fontweight="bold")
            ax.set_xlabel("Year", fontsize=11)
            ax.set_ylabel("Number of Recorded Events", fontsize=11)
            plt.xticks(rotation=45)
            plt.tight_layout()
            p1 = output_dir / "events_by_year.png"
            fig.savefig(p1)
            plt.close(fig)
            saved_plots["events_by_year"] = p1

    # 2. Events by Month Plot
    if "event_month" in df.columns:
        month_counts = df["event_month"].dropna().astype(int).value_counts().sort_index()
        month_names = {
            1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
        }
        if not month_counts.empty:
            labels = [month_names.get(m, str(m)) for m in month_counts.index]
            fig, ax = plt.subplots(figsize=(8, 4.5), dpi=300)
            ax.bar(labels, month_counts.values, color="#2ca02c", edgecolor="black")
            ax.set_title("Seasonal Distribution of Landslide Events by Month", fontsize=13, fontweight="bold")
            ax.set_xlabel("Month", fontsize=11)
            ax.set_ylabel("Number of Recorded Events", fontsize=11)
            plt.tight_layout()
            p2 = output_dir / "events_by_month.png"
            fig.savefig(p2)
            plt.close(fig)
            saved_plots["events_by_month"] = p2

    # 3. Geographic Distribution Map Scatter
    if "latitude" in df.columns and "longitude" in df.columns:
        valid_coords = df.dropna(subset=["latitude", "longitude"])
        if not valid_coords.empty:
            fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
            ax.scatter(
                valid_coords["longitude"],
                valid_coords["latitude"],
                alpha=0.4,
                s=8,
                c="#d62728",
                edgecolors="none",
            )
            ax.set_title("Global Geographic Distribution of Landslide Catalog Records", fontsize=13, fontweight="bold")
            ax.set_xlabel("Longitude (Decimal Degrees)", fontsize=11)
            ax.set_ylabel("Latitude (Decimal Degrees)", fontsize=11)
            ax.set_xlim(-180, 180)
            ax.set_ylim(-90, 90)
            plt.tight_layout()
            p3 = output_dir / "geographic_distribution.png"
            fig.savefig(p3)
            plt.close(fig)
            saved_plots["geographic_distribution"] = p3

    # 4. Missing Values Summary Bar Chart
    missing_pct = (df.isna().sum() / len(df)) * 100
    missing_pct = missing_pct[missing_pct > 0].sort_values(ascending=True)
    if not missing_pct.empty:
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        missing_pct.plot(kind="barh", ax=ax, color="#ff7f0e", edgecolor="black")
        ax.set_title("Missing Value Percentage per Column (Raw Dataset)", fontsize=13, fontweight="bold")
        ax.set_xlabel("Missing Percentage (%)", fontsize=11)
        ax.set_ylabel("Column Name", fontsize=11)
        ax.set_xlim(0, 100)
        plt.tight_layout()
        p4 = output_dir / "missing_values_summary.png"
        fig.savefig(p4)
        plt.close(fig)
        saved_plots["missing_values_summary"] = p4

    return saved_plots
