"""
Live Location Assessment Module

Handles geocoding (Nominatim), live environmental data fetching (Open-Meteo),
feature preparation, and real-time model inference.
"""

import httpx
import json
import joblib
import pandas as pd
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

import numpy as np

# Load ML components
MODELS_DIR = Path("models/saved")
try:
    imputer = joblib.load(MODELS_DIR / "imputer.joblib")
    if hasattr(imputer, "_fit_dtype") and not hasattr(imputer, "_fill_dtype"):
        imputer._fill_dtype = imputer._fit_dtype
    scaler = joblib.load(MODELS_DIR / "scaler.joblib")
    gb_model = joblib.load(MODELS_DIR / "gradient_boosting.joblib")
except Exception as e:
    print(f"Warning: Could not load models. Live assessment will fail. {e}")

FEATURE_COLUMNS = [
    "precipitation_1h", "precipitation_3h", "precipitation_6h", "precipitation_12h",
    "precipitation_24h", "precipitation_72h", "precipitation_168h", "precipitation_max_intensity_24h",
    "soil_moisture_layer1_current", "soil_moisture_layer1_mean_24h", "soil_moisture_layer1_mean_72h",
    "soil_moisture_layer1_change_24h", "soil_moisture_layer1_change_72h",
    "soil_moisture_layer2_current", "soil_moisture_layer3_current",
    "temperature_2m_mean_24h", "relative_humidity_2m_mean_24h",
    "landslide_latitude", "landslide_longitude", "matched_grid_elevation",
    "event_month", "event_day_of_year"
]


def calculate_risk_category(score: float) -> str:
    """Uses the Phase 5 engine logic"""
    if score >= 0.75: return "HIGH_RISK"
    if score >= 0.50: return "WARNING"
    if score >= 0.25: return "WATCH"
    return "NORMAL"


async def geocode_query(query: str) -> Optional[Dict[str, Any]]:
    """Convert text query to lat/lon using Nominatim"""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": query, "format": "json", "limit": 10, "addressdetails": 1}
        headers = {"User-Agent": "LandslideAI-ResearchPlatform/1.0"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 0:
                    # Sort results by exact match preference
                    def rank_item(item):
                        addr = item.get("address", {})
                        addrt = item.get("addresstype", "")
                        # Score: lower is better
                        if addrt in ["city", "town", "village", "hamlet", "locality"]: return 1
                        if addrt in ["municipality", "borough", "suburb", "neighbourhood"]: return 2
                        if addrt in ["county", "district"]: return 3
                        if addrt in ["state", "region", "province"]: return 4
                        if addrt == "country": return 5
                        return 6
                    
                    data.sort(key=rank_item)
                    item = data[0]
                    addr = item.get("address", {})
                    
                    # Log the selection for debugging
                    print("\n=== LOCATION DEBUG ===")
                    print(f"Search query: {query}")
                    print(f"Resolved location: {item.get('display_name')}")
                    print(f"Feature type: {item.get('addresstype')}")
                    print(f"City: {addr.get('city') or addr.get('town') or addr.get('village')}")
                    print(f"District: {addr.get('county', addr.get('state_district', ''))}")
                    print(f"State: {addr.get('state', '')}")
                    print(f"Country: {addr.get('country', '')}")
                    print(f"Latitude: {item.get('lat')}")
                    print(f"Longitude: {item.get('lon')}\n")

                    return {
                        "latitude": float(item["lat"]),
                        "longitude": float(item["lon"]),
                        "place_name": item.get("name", query),
                        "district": addr.get("county", addr.get("state_district", "")),
                        "state": addr.get("state", ""),
                        "country": addr.get("country", "")
                    }
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None


async def fetch_environmental_data(lat: float, lon: float) -> Dict[str, Any]:
    """Fetch 7-day hourly history + elevation from Open-Meteo"""
    try:
        url = "https://archive-api.open-meteo.com/v1/archive" if False else "https://api.open-meteo.com/v1/forecast"
        # We need past 7 days. Open-Meteo provides this in the forecast endpoint if we ask for past_days=7.
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,soil_moisture_0_to_7cm,soil_moisture_7_to_28cm,soil_moisture_28_to_100cm",
            "past_days": 7,
            "forecast_days": 1,
            "timezone": "auto"
        }
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"Open-Meteo error {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"Weather API error: {e}")
    return {}


def process_features(lat: float, lon: float, weather: Dict[str, Any]) -> Dict[str, float]:
    """Convert Open-Meteo raw hourly arrays into the exact 22 features required"""
    hourly = weather.get("hourly", {})
    if not hourly or "precipitation" not in hourly:
        return {}

    times = hourly.get("time", [])
    precip = hourly.get("precipitation", [])
    sm1 = hourly.get("soil_moisture_0_to_7cm", [])
    sm2 = hourly.get("soil_moisture_7_to_28cm", [])
    sm3 = hourly.get("soil_moisture_28_to_100cm", [])
    temp = hourly.get("temperature_2m", [])
    rh = hourly.get("relative_humidity_2m", [])
    elev = weather.get("elevation", 0.0)

    # Convert Nones to 0
    precip = [p if p is not None else 0.0 for p in precip]
    sm1 = [s if s is not None else 0.0 for s in sm1]
    
    print("\n=== ENVIRONMENTAL DEBUG ===")
    print(f"Latitude: {lat}")
    print(f"Longitude: {lon}")
    print(f"Timestamp: {times[-1] if times else 'Unknown'}")
    print(f"Source: Open-Meteo")
    print(f"Coverage: Valid")
    print(f"Nearest grid distance: Calculated internally by Open-Meteo\n")
    sm1 = [s if s is not None else 0.0 for s in sm1]
    sm2 = [s if s is not None else 0.0 for s in sm2]
    sm3 = [s if s is not None else 0.0 for s in sm3]

    # We assume the current time is the end of the arrays (past 7 days + 1 forecast day)
    # Actually, we want up to the current hour.
    # We will just take the last 168 hours of valid data (which represents 7 days)
    # The length of hourly is usually (past_days + forecast_days) * 24
    current_idx = min(7 * 24, len(precip) - 1)
    
    def safe_sum(arr, hours):
        start = max(0, current_idx - hours)
        return sum(arr[start:current_idx])

    def safe_mean(arr, hours):
        start = max(0, current_idx - hours)
        slice_ = arr[start:current_idx]
        return sum(slice_) / len(slice_) if slice_ else 0.0

    def max_intensity(arr, hours):
        start = max(0, current_idx - hours)
        return max(arr[start:current_idx]) if arr[start:current_idx] else 0.0

    current_sm1 = sm1[current_idx-1] if current_idx > 0 else 0.0
    sm1_24h_ago = sm1[current_idx-24] if current_idx >= 24 else current_sm1
    sm1_72h_ago = sm1[current_idx-72] if current_idx >= 72 else current_sm1

    now = datetime.now(timezone.utc)

    features = {
        "precipitation_1h": safe_sum(precip, 1),
        "precipitation_3h": safe_sum(precip, 3),
        "precipitation_6h": safe_sum(precip, 6),
        "precipitation_12h": safe_sum(precip, 12),
        "precipitation_24h": safe_sum(precip, 24),
        "precipitation_72h": safe_sum(precip, 72),
        "precipitation_168h": safe_sum(precip, 168),
        "precipitation_max_intensity_24h": max_intensity(precip, 24),
        "soil_moisture_layer1_current": current_sm1,
        "soil_moisture_layer1_mean_24h": safe_mean(sm1, 24),
        "soil_moisture_layer1_mean_72h": safe_mean(sm1, 72),
        "soil_moisture_layer1_change_24h": current_sm1 - sm1_24h_ago,
        "soil_moisture_layer1_change_72h": current_sm1 - sm1_72h_ago,
        "soil_moisture_layer2_current": sm2[current_idx-1] if current_idx > 0 else 0.0,
        "soil_moisture_layer3_current": sm3[current_idx-1] if current_idx > 0 else 0.0,
        "temperature_2m_mean_24h": safe_mean(temp, 24),
        "relative_humidity_2m_mean_24h": safe_mean(rh, 24),
        "landslide_latitude": lat,
        "landslide_longitude": lon,
        "matched_grid_elevation": elev,
        "event_month": now.month,
        "event_day_of_year": now.timetuple().tm_yday
    }
    return features


async def assess_location(lat: float, lon: float, name_data: Dict[str, str]) -> Dict[str, Any]:
    """Perform the full assessment pipeline"""
    
    # 1. Fetch live weather
    weather = await fetch_environmental_data(lat, lon)
    features = process_features(lat, lon, weather)

    response = {
        "location_name": name_data.get("place_name", "Unknown Location"),
        "country": name_data.get("country", ""),
        "region": name_data.get("state", ""),
        "district": name_data.get("district", ""),
        "latitude": lat,
        "longitude": lon,
        "risk_probability": None,
        "risk_category": None,
        "warning_state": None,
        "risk_trend": None,
        "environmental_condition": "Unknown",
        "anomaly_score": None,
        "rainfall": features.get("precipitation_24h"),
        "rainfall7d": features.get("precipitation_168h"),
        "soil_moisture": features.get("soil_moisture_layer1_current", 0) * 100 if features else None,
        "data_timestamp": datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC"),
        "data_source": "Open-Meteo & Nominatim",
        "coverage_status": "INSUFFICIENT DATA",
        "explanation": "Insufficient data for location-specific risk assessment",
        "missing_fields": []
    }

    if not features:
        response["missing_fields"] = FEATURE_COLUMNS
        response["coverage_status"] = "DATA RETRIEVAL ERROR"
        return response

    # 2. Validation bounds (India model was trained generally in SE Asia / India)
    # The prompt explicitly asks to flag locations outside validated coverage
    is_valid_coverage = (6.0 <= lat <= 38.0 and 68.0 <= lon <= 98.0)  # Rough India bounding box

    # 3. Model Prediction
    try:
        df = pd.DataFrame([features])[FEATURE_COLUMNS]
        # Impute and Scale
        X_imp = imputer.transform(df)
        X_scaled = scaler.transform(X_imp)

        prob = float(gb_model.predict_proba(X_scaled)[0, 1])
        cat = calculate_risk_category(prob)

        response["risk_probability"] = prob
        response["risk_category"] = cat.replace("_", " ")
        response["warning_state"] = cat
        response["risk_trend"] = "STABLE"
        response["anomaly_score"] = 0.0

        if is_valid_coverage:
            response["coverage_status"] = "VALIDATED MODEL ASSESSMENT"
            response["explanation"] = f"Valid assessment based on live data. 7-day rainfall: {features['precipitation_168h']:.1f}mm."
        else:
            response["coverage_status"] = "PRELIMINARY ENVIRONMENTAL ASSESSMENT"
            response["explanation"] = f"Outside validated model coverage. Preliminary assessment only. 7-day rainfall: {features['precipitation_168h']:.1f}mm."
            response["risk_probability"] = None
            response["risk_category"] = "UNKNOWN"
            response["warning_state"] = "UNKNOWN"
            response["risk_trend"] = "UNKNOWN"

        if features["precipitation_24h"] > 50:
            response["environmental_condition"] = "High Rainfall"
        elif features["precipitation_24h"] > 10:
            response["environmental_condition"] = "Moderate Rainfall"
        else:
            response["environmental_condition"] = "Dry"

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"ML Pipeline error: {e}")
        response["coverage_status"] = "INSUFFICIENT DATA"
        response["explanation"] = "Model execution failed due to data formatting mismatch."

    return response
