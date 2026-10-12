"""
Explainable Alert Reason Generation Module.

Composes transparent, evidence-based human-readable alert reasons
from model risk probabilities, location-adaptive environmental anomalies,
temporal trends, and persistence states.
"""

from typing import List, Optional


def generate_warning_explanation(
    warning_state: str,
    risk_probability: float,
    anomaly_status: str,
    anomaly_z_score: Optional[float] = None,
    risk_trend: str = "STABLE",
    trend_delta: float = 0.0,
    consecutive_high_count: int = 0,
) -> str:
    """
    Generates a structured human-readable explanation string for a warning prediction.

    Args:
        warning_state: Warning state ('NORMAL', 'WATCH', 'WARNING', 'HIGH_RISK').
        risk_probability: Model risk probability P(Landslide).
        anomaly_status: Environmental abnormality state ('NORMAL', 'ABNORMAL', 'STRONGLY_ABNORMAL').
        anomaly_z_score: Optional standardized anomaly z-score.
        risk_trend: Risk trend string ('INCREASING', 'STABLE', 'DECREASING').
        trend_delta: Short-term risk delta (R_t - R_{t-1}).
        consecutive_high_count: Number of consecutive elevated observations.

    Returns:
        str: Human-readable explanation string.
    """
    reasons: List[str] = []

    # 1. Model Risk Probability Reason
    if risk_probability >= 0.80:
        reasons.append(f"Model landslide hazard probability is severely elevated ({risk_probability:.2f})")
    elif risk_probability >= 0.60:
        reasons.append(f"Model landslide hazard probability is elevated ({risk_probability:.2f})")
    elif risk_probability >= 0.35:
        reasons.append(f"Model landslide hazard probability is moderate ({risk_probability:.2f})")
    else:
        reasons.append(f"Model landslide hazard probability is low ({risk_probability:.2f})")

    # 2. Environmental Abnormality Reason
    if anomaly_status == "STRONGLY_ABNORMAL":
        z_str = f" (Z={anomaly_z_score:.2f})" if anomaly_z_score is not None else ""
        reasons.append(f"Environmental conditions are strongly abnormal relative to location baseline{z_str}")
    elif anomaly_status == "ABNORMAL":
        z_str = f" (Z={anomaly_z_score:.2f})" if anomaly_z_score is not None else ""
        reasons.append(f"Environmental conditions are unusual relative to location baseline{z_str}")

    # 3. Risk Trend Reason
    if risk_trend == "INCREASING":
        reasons.append(f"Risk probability trajectory is INCREASING (+{trend_delta:.2f})")
    elif risk_trend == "DECREASING":
        reasons.append(f"Risk probability trajectory is DECREASING ({trend_delta:.2f})")

    # 4. Persistence Reason
    if consecutive_high_count >= 2:
        reasons.append(f"Elevated risk conditions persisted across {consecutive_high_count} consecutive observations")

    explanation_body = "; ".join(reasons)
    return f"Research Warning State: {warning_state}. Evidence: [{explanation_body}]."
