"""
Temporal Alignment and Pre-Event Feature Extraction Module.

Strictly enforces the NO-FUTURE-LEAKAGE rule by extracting environmental features
derived exclusively from observations prior to the event timestamp (t < t_event).
"""

from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
import numpy as np
import pandas as pd


def filter_preevent_observations(
    env_df: pd.DataFrame,
    event_timestamp: pd.Timestamp,
    prediction_cutoff_hours: int = 0,
    max_history_days: int = 7,
) -> pd.DataFrame:
    """
    Slices environmental DataFrame to include ONLY observations prior to event prediction cutoff.

    STRICT TEMPORAL RULE:
    Observation time <= event_timestamp - cutoff_hours.
    Observations after the prediction cutoff are strictly excluded.

    Args:
        env_df: Environmental DataFrame with DatetimeIndex in UTC.
        event_timestamp: Exact timestamp of the landslide event.
        prediction_cutoff_hours: Configurable cutoff offset in hours (default 0).
        max_history_days: History window lookback limit in days (default 7 days / 168 hours).

    Returns:
        pd.DataFrame: Filtered pre-event environmental observations.
    """
    if env_df.empty:
        return env_df

    # Ensure index is DatetimeIndex
    if not isinstance(env_df.index, pd.DatetimeIndex):
        if "datetime" in env_df.columns:
            env_df = env_df.set_index("datetime")
        else:
            raise TypeError("Environmental DataFrame must have DatetimeIndex.")

    # Calculate cutoff bounds
    cutoff_time = event_timestamp - timedelta(hours=prediction_cutoff_hours)
    history_start = cutoff_time - timedelta(days=max_history_days)

    # Filter observations strictly within pre-event window
    mask = (env_df.index >= history_start) & (env_df.index <= cutoff_time)
    filtered_df = env_df.loc[mask].sort_index()

    return filtered_df


def compute_preevent_features(
    env_df: pd.DataFrame,
    event_timestamp: pd.Timestamp,
    prediction_cutoff_hours: int = 0,
) -> Dict[str, Any]:
    """
    Calculates pre-event environmental history features from preceding ERA5-Land observations.

    Features computed:
    - precipitation_1h, 3h, 6h, 12h, 24h, 72h (3-day), 168h (7-day) sum (mm)
    - precipitation_max_intensity_24h (mm/hr)
    - soil_moisture_layer1_current, mean_24h, mean_72h, change_24h, change_72h (m^3/m^3)
    - soil_moisture_layer2_current, layer3_current
    - temperature_2m_mean_24h (°C)
    - relative_humidity_2m_mean_24h (%)

    Args:
        env_df: Hourly environmental observations DataFrame.
        event_timestamp: Event timestamp.
        prediction_cutoff_hours: Cutoff offset.

    Returns:
        Dict[str, Any]: Pre-event feature metrics dictionary.
    """
    preevent_df = filter_preevent_observations(
        env_df, event_timestamp, prediction_cutoff_hours=prediction_cutoff_hours, max_history_days=7
    )

    features: Dict[str, Any] = {
        "temporal_match_valid": not preevent_df.empty and len(preevent_df) >= 24,
        "pre_event_observations_count": len(preevent_df),
    }

    if preevent_df.empty:
        # Fill features with NaN if no pre-event observations exist
        keys = [
            "precipitation_1h", "precipitation_3h", "precipitation_6h", "precipitation_12h",
            "precipitation_24h", "precipitation_72h", "precipitation_168h", "precipitation_max_intensity_24h",
            "soil_moisture_layer1_current", "soil_moisture_layer1_mean_24h", "soil_moisture_layer1_mean_72h",
            "soil_moisture_layer1_change_24h", "soil_moisture_layer1_change_72h",
            "soil_moisture_layer2_current", "soil_moisture_layer3_current",
            "temperature_2m_mean_24h", "relative_humidity_2m_mean_24h"
        ]
        for k in keys:
            features[k] = np.nan
        return features

    # Sort descending from cutoff time
    df_rev = preevent_df.iloc[::-1]

    # Helper for rolling sum/mean
    def get_series(col_name: str) -> pd.Series:
        return df_rev[col_name] if col_name in df_rev.columns else pd.Series(dtype=float)

    precip = get_series("precipitation")
    sm1 = get_series("soil_moisture_0_to_7cm")
    sm2 = get_series("soil_moisture_7_to_28cm")
    sm3 = get_series("soil_moisture_28_to_100cm")
    temp = get_series("temperature_2m")
    rh = get_series("relative_humidity_2m")

    # Precipitation accumulations (sum over preceding N hours)
    features["precipitation_1h"] = float(precip.iloc[:1].sum()) if len(precip) >= 1 else np.nan
    features["precipitation_3h"] = float(precip.iloc[:3].sum()) if len(precip) >= 1 else np.nan
    features["precipitation_6h"] = float(precip.iloc[:6].sum()) if len(precip) >= 1 else np.nan
    features["precipitation_12h"] = float(precip.iloc[:12].sum()) if len(precip) >= 1 else np.nan
    features["precipitation_24h"] = float(precip.iloc[:24].sum()) if len(precip) >= 1 else np.nan
    features["precipitation_72h"] = float(precip.iloc[:72].sum()) if len(precip) >= 1 else np.nan
    features["precipitation_168h"] = float(precip.iloc[:168].sum()) if len(precip) >= 1 else np.nan
    features["precipitation_max_intensity_24h"] = float(precip.iloc[:24].max()) if len(precip) >= 1 else np.nan

    # Soil moisture dynamics
    if len(sm1) >= 1:
        current_sm1 = float(sm1.iloc[0])
        features["soil_moisture_layer1_current"] = current_sm1
        features["soil_moisture_layer1_mean_24h"] = float(sm1.iloc[:24].mean())
        features["soil_moisture_layer1_mean_72h"] = float(sm1.iloc[:72].mean())

        # Soil moisture deltas (Current - Past)
        sm1_24h_ago = float(sm1.iloc[min(23, len(sm1)-1)])
        sm1_72h_ago = float(sm1.iloc[min(71, len(sm1)-1)])
        features["soil_moisture_layer1_change_24h"] = round(current_sm1 - sm1_24h_ago, 4)
        features["soil_moisture_layer1_change_72h"] = round(current_sm1 - sm1_72h_ago, 4)
    else:
        for k in ["soil_moisture_layer1_current", "soil_moisture_layer1_mean_24h", "soil_moisture_layer1_mean_72h", "soil_moisture_layer1_change_24h", "soil_moisture_layer1_change_72h"]:
            features[k] = np.nan

    features["soil_moisture_layer2_current"] = float(sm2.iloc[0]) if len(sm2) >= 1 else np.nan
    features["soil_moisture_layer3_current"] = float(sm3.iloc[0]) if len(sm3) >= 1 else np.nan

    features["temperature_2m_mean_24h"] = float(temp.iloc[:24].mean()) if len(temp) >= 1 else np.nan
    features["relative_humidity_2m_mean_24h"] = float(rh.iloc[:24].mean()) if len(rh) >= 1 else np.nan

    return features
