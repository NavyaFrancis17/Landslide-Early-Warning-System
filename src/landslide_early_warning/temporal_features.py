"""
Temporal Feature Engineering Module.

Provides robust date parsing, chronological sorting, and temporal component extraction
(year, month, day, day of year, weekday, season) for landslide event records.

IMPORTANT SCIENTIFIC NOTICE:
Do not compute rolling/lag rainfall or soil moisture features directly on discrete event records.
Rolling and lag features require continuous, daily meteorological time series streams.
"""

from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def parse_event_dates(
    df: pd.DataFrame, date_col: str = "event_date"
) -> Tuple[pd.Series, Dict[str, Any]]:
    """
    Safely parses event dates from string representations into pandas DatetimeSeries.

    Args:
        df: Input DataFrame.
        date_col: Name of date column.

    Returns:
        Tuple[pd.Series, Dict[str, Any]]:
            - Datetime Series with NaT for unparseable dates.
            - Metrics dictionary (total, valid count, invalid count, missing count, date min/max).
    """
    if date_col not in df.columns:
        raise KeyError(f"Date column '{date_col}' not found in DataFrame.")

    raw_series = df[date_col]
    total_records = len(df)
    missing_count = int(raw_series.isna().sum())

    # Multi-format mixed parsing using pandas to_datetime
    try:
        parsed_dates = pd.to_datetime(raw_series, format="mixed", errors="coerce")
    except Exception:
        parsed_dates = pd.to_datetime(raw_series, errors="coerce")

    valid_mask = parsed_dates.notna()
    valid_count = int(valid_mask.sum())
    invalid_count = total_records - valid_count

    min_date_str = str(parsed_dates[valid_mask].min().date()) if valid_count > 0 else None
    max_date_str = str(parsed_dates[valid_mask].max().date()) if valid_count > 0 else None

    metrics = {
        "total_records": total_records,
        "missing_date_count": missing_count,
        "valid_date_count": valid_count,
        "invalid_or_missing_count": invalid_count,
        "valid_date_percentage": round((valid_count / total_records) * 100, 2) if total_records > 0 else 0.0,
        "min_date": min_date_str,
        "max_date": max_date_str,
    }

    return parsed_dates, metrics


def extract_temporal_components(
    df: pd.DataFrame, date_series: pd.Series
) -> pd.DataFrame:
    """
    Extracts temporal components from parsed date series into new DataFrame columns.

    Extracted fields:
    - event_datetime (datetime64[ns])
    - event_year (Int64 nullable)
    - event_month (Int64 nullable)
    - event_day (Int64 nullable)
    - event_day_of_year (Int64 nullable)
    - event_weekday (Int64 nullable, 0=Monday .. 6=Sunday)
    - season (string: Winter, Spring, Summer, Autumn)

    Args:
        df: Original DataFrame.
        date_series: Parsed Datetime Series.

    Returns:
        pd.DataFrame: Copy of DataFrame with added temporal feature columns.
    """
    df_out = df.copy()

    df_out["event_datetime"] = date_series

    valid_dt = date_series.dt

    df_out["event_year"] = valid_dt.year.astype("Int64")
    df_out["event_month"] = valid_dt.month.astype("Int64")
    df_out["event_day"] = valid_dt.day.astype("Int64")
    df_out["event_day_of_year"] = valid_dt.dayofyear.astype("Int64")
    df_out["event_weekday"] = valid_dt.weekday.astype("Int64")

    # Meteorological season mapping based on Northern Hemisphere conventions
    def map_season(month: Optional[int]) -> Optional[str]:
        if pd.isna(month):
            return None
        m = int(month)
        if m in (12, 1, 2):
            return "Winter"
        elif m in (3, 4, 5):
            return "Spring"
        elif m in (6, 7, 8):
            return "Summer"
        elif m in (9, 10, 11):
            return "Autumn"
        return None

    df_out["season"] = df_out["event_month"].apply(map_season)

    return df_out


def sort_chronologically(
    df: pd.DataFrame, datetime_col: str = "event_datetime"
) -> pd.DataFrame:
    """
    Sorts dataframe chronologically by event datetime while placing missing dates at the end.

    Args:
        df: DataFrame containing datetime column.
        datetime_col: Column name containing parsed datetimes.

    Returns:
        pd.DataFrame: Chronologically sorted DataFrame with reset index.
    """
    if datetime_col not in df.columns:
        raise KeyError(f"Datetime column '{datetime_col}' not found.")

    return df.sort_values(by=datetime_col, na_position="last").reset_index(drop=True)


def create_time_series_rolling_features_stub(
    series: pd.Series, window: int = 3
) -> pd.Series:
    """
    Helper stub for computing rolling mean on a continuous, daily ordered time series.

    WARNING:
    Do NOT apply this function directly to discrete event-only datasets.
    This helper function is designed exclusively for continuous daily weather streams
    (e.g., NASA GPM IMERG daily precipitation grids) in Phase 3+.

    Args:
        series: Continuous daily numerical series.
        window: Rolling window size in days.

    Returns:
        pd.Series: Rolling mean series.
    """
    return series.rolling(window=window, min_periods=1).mean()
