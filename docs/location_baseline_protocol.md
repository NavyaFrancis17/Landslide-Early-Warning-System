# Location-Adaptive Baseline Protocol & Anomaly Feature Framework

## 1. Research Objective

Landslides are location-adaptive phenomena: a 50 mm daily rainfall event in an arid terrain may represent a catastrophic anomaly, whereas the same 50 mm in a tropical monsoon region may be well within historical norms. To account for local micro-climatic baselines without introducing data leakage, location-adaptive anomaly features are computed relative to historical pre-event baselines.

---

## 2. Pre-Event Historical Baseline Calculation

For any location $L = (\text{lat}, \text{lon})$ and event timestamp $t_{\text{event}}$:

1. **Pre-Event Baseline Window**:
   Historical observations at location $L$ during the pre-event baseline period:
   $$\mathcal{H}_{L, t_{\text{event}}} = \{ X(L, t) \mid t < t_{\text{event}} \}$$

2. **Historical Mean ($\mu_L$) and Standard Deviation ($\sigma_L$)**:
   $$\mu_L = \mathbb{E}[\mathcal{H}_{L, t_{\text{event}}}], \quad \sigma_L = \text{Std}[\mathcal{H}_{L, t_{\text{event}}}]$$

3. **Standardized Anomaly ($Z$-score)**:
   $$Z(L, t_{\text{event}}) = \frac{X(L, t_{\text{event}}) - \mu_L}{\sigma_L}$$

---

## 3. Strict Data Leakage Prohibition

> **DATA LEAKAGE PREVENTION RULE**:
> Baselines ($\mu_L, \sigma_L$) must NEVER be computed using future observations ($t \ge t_{\text{event}}$) or post-event data. Calculating regional baselines over the entire multi-year dataset inclusive of future years introduces future lookahead leakage.
