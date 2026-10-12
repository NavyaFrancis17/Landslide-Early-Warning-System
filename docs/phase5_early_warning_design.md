# Phase 5 Early-Warning Engine Architecture & Design Document

## 1. System Architecture
The early-warning engine converts Phase 3 ML risk probabilities and Phase 4 location-adaptive environmental anomalies into transparent, explainable warning alert states.

```
ML Risk Probability
        +
Location-Adaptive Anomaly
        +
Temporal Risk Trend
        +
Persistence & Hysteresis
        ↓
Early-Warning Engine
        ↓
Warning State (NORMAL | WATCH | WARNING | HIGH_RISK)
        ↓
Explainable Alert String
```

## 2. Warning Alert States
* **NORMAL**: $P(\text{Landslide}) < 0.35$ (Baseline micro-climatic conditions)
* **WATCH**: $0.35 \le P(\text{Landslide}) < 0.60$ (Moderate antecedent moisture / rainfall)
* **WARNING**: $0.60 \le P(\text{Landslide}) < 0.80$ (Elevated slope instability risk)
* **HIGH_RISK**: $P(\text{Landslide}) \ge 0.80$ (Severe imminent landslide hazard)
