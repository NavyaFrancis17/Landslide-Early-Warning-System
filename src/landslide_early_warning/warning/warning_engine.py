"""
Master Early-Warning Engine Module.

Orchestrates machine learning probability scoring, location-adaptive environmental anomaly assessment,
chronological risk trend calculation, temporal persistence locking, and explainable warning state generation.
Includes a reusable real-time inference method predict_warning(input_observation).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import joblib
import numpy as np
import pandas as pd

from landslide_early_warning.ml.train import FEATURE_COLUMNS
from landslide_early_warning.warning.alert_explanation import generate_warning_explanation
from landslide_early_warning.warning.persistence import apply_warning_state_persistence
from landslide_early_warning.warning.risk_state_mapper import map_probability_to_risk_state
from landslide_early_warning.warning.risk_trend import compute_temporal_risk_trend
from landslide_early_warning.warning.warning_config import load_warning_config


class EarlyWarningEngine:
    """Master AI-Based Location-Adaptive Landslide Early-Warning Engine."""

    def __init__(
        self,
        model: Any,
        imputer: Any,
        scaler: Any,
        feature_names: List[str] = FEATURE_COLUMNS,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.model = model
        self.imputer = imputer
        self.scaler = scaler
        self.feature_names = feature_names
        self.config = config if config is not None else load_warning_config()

        # State tracking per location
        self.location_history: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def load_from_saved_models(
        cls,
        models_dir: Path = Path("models/saved"),
        config_path: Optional[Path] = None,
    ) -> "EarlyWarningEngine":
        """Factory method to instantiate engine using pre-trained model artifacts."""
        model_file = models_dir / "gradient_boosting.joblib"
        imputer_file = models_dir / "imputer.joblib"
        scaler_file = models_dir / "scaler.joblib"

        if not model_file.exists():
            raise FileNotFoundError(f"Trained model artifact missing at: {model_file.resolve()}")

        try:
            import types
            import sklearn._loss.loss
            _loss_mod = types.ModuleType('_loss')
            for attr in dir(sklearn._loss.loss):
                setattr(_loss_mod, attr, getattr(sklearn._loss.loss, attr))
            sys.modules['_loss'] = _loss_mod
        except Exception:
            pass

        model = joblib.load(model_file)
        imputer = joblib.load(imputer_file)
        if hasattr(imputer, "_fit_dtype") and not hasattr(imputer, "_fill_dtype"):
            imputer._fill_dtype = imputer._fit_dtype
        scaler = joblib.load(scaler_file)
        config = load_warning_config(config_path)

        return cls(model=model, imputer=imputer, scaler=scaler, config=config)

    def calculate_location_adaptive_anomaly(
        self, input_obs: Dict[str, Any]
    ) -> Tuple[str, float]:
        """
        Computes location-adaptive environmental anomaly status and Z-score.
        """
        sm_current = float(input_obs.get("soil_moisture_layer1_current", 0.30))
        sm_mean = float(input_obs.get("soil_moisture_layer1_mean_24h", 0.30))
        precip_24h = float(input_obs.get("precipitation_24h", 0.0))

        # Standardized anomaly Z-score approximation relative to pre-event baseline
        std_est = 0.05
        z_score = round((sm_current - sm_mean) / std_est + (precip_24h / 15.0), 2)

        ab_cfg = self.config.get("abnormality", {})
        abnormal_th = ab_cfg.get("abnormal_z_threshold", 1.5)
        strongly_th = ab_cfg.get("strongly_abnormal_z_threshold", 2.5)

        if z_score >= strongly_th:
            status = "STRONGLY_ABNORMAL"
        elif z_score >= abnormal_th:
            status = "ABNORMAL"
        else:
            status = "NORMAL"

        return status, z_score

    def predict_warning(self, input_obs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reusable real-time inference function for generating explainable warning alerts.

        Args:
            input_obs: Dictionary of observation features for a single location/timestamp.

        Returns:
            Dict[str, Any]: Structured warning prediction dictionary.
        """
        loc_id = str(input_obs.get("location_id", input_obs.get("event_id", "default_loc")))
        timestamp_str = str(input_obs.get("event_date", input_obs.get("timestamp", "2026-01-01")))

        # Extract features vector
        feat_vals = []
        for fn in self.feature_names:
            val = input_obs.get(fn, np.nan)
            feat_vals.append(float(val) if pd.notna(val) else np.nan)

        X_raw = np.array(feat_vals).reshape(1, -1)

        # Apply fitted preprocessing & model prediction
        X_proc = self.scaler.transform(self.imputer.transform(X_raw))
        prob = float(self.model.predict_proba(X_proc)[0, 1]) if hasattr(self.model, "predict_proba") else float(self.model.predict(X_proc)[0])

        # 1. Location-Adaptive Anomaly Assessment
        anomaly_status, z_score = self.calculate_location_adaptive_anomaly(input_obs)

        # 2. Update Location History
        if loc_id not in self.location_history:
            self.location_history[loc_id] = []

        history = self.location_history[loc_id]
        past_probs = [h["risk_probability"] for h in history] + [prob]

        # 3. Calculate Risk Trend Trajectory
        trend_cfg = self.config.get("trend", {})
        trend_res = compute_temporal_risk_trend(
            past_probs,
            window_size=trend_cfg.get("trend_window_size", 3),
            increasing_delta_th=trend_cfg.get("increasing_delta_threshold", 0.05),
            decreasing_delta_th=trend_cfg.get("decreasing_delta_threshold", -0.05),
        )

        # 4. Map Raw Warning State
        raw_state = map_probability_to_risk_state(prob, self.config.get("risk_states"))

        # 5. Apply Temporal Persistence & De-escalation Locking
        past_raw_states = [h["raw_warning_state"] for h in history] + [raw_state]
        pers_cfg = self.config.get("persistence", {})
        pers_res = apply_warning_state_persistence(
            past_raw_states,
            raw_state,
            min_warning_persistence=pers_cfg.get("minimum_warning_persistence_observations", 2),
            min_high_risk_persistence=pers_cfg.get("minimum_high_risk_persistence_observations", 3),
            deescalation_low_obs=pers_cfg.get("deescalation_consecutive_low_observations", 2),
        )

        persisted_state = pers_res["persisted_state"]
        elevated_cnt = pers_res["consecutive_elevated_count"]

        # 6. Compose Human-Readable Explanation
        reason = generate_warning_explanation(
            warning_state=persisted_state,
            risk_probability=prob,
            anomaly_status=anomaly_status,
            anomaly_z_score=z_score,
            risk_trend=trend_res["risk_trend"],
            trend_delta=trend_res["trend_delta"],
            consecutive_high_count=elevated_cnt,
        )

        result_record = {
            "location_id": loc_id,
            "timestamp": timestamp_str,
            "latitude": input_obs.get("landslide_latitude"),
            "longitude": input_obs.get("landslide_longitude"),
            "risk_probability": round(prob, 4),
            "risk_trend": trend_res["risk_trend"],
            "trend_delta": trend_res["trend_delta"],
            "anomaly_z_score": z_score,
            "anomaly_state": anomaly_status,
            "raw_warning_state": raw_state,
            "current_warning_state": persisted_state,
            "persistence_count": elevated_cnt,
            "warning_reason": reason,
        }

        # Store in location history
        self.location_history[loc_id].append(result_record)
        return result_record
