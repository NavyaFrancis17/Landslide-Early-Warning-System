# Temporal Alignment Protocol & No-Future-Data Rule

> **CRITICAL SCIENTIFIC DIRECTIVE**:
> In operational landslide early-warning systems, predictions must be generated strictly before an event occurs. Incorporating environmental observations recorded during or after the event timestamp constitutes **temporal data leakage**.

---

## 1. Mathematical Cutoff Rule

For any landslide event $i$ occurring at timestamp $t_{\text{event}, i}$:

$$\text{Valid Feature Observation Window} = \{ t \mid t_{\text{history\_start}} \le t \le (t_{\text{event}, i} - \delta_t) \}$$

Where:
* $t_{\text{event}, i}$: Recorded timestamp of landslide event $i$.
* $\delta_t$: Prediction cutoff offset ($\delta_t = 0$ hours for real-time nowcasting, or $\delta_t = 24$ hours for 24-hour advance forecasting).
* $t_{\text{history\_start}} = t_{\text{event}, i} - 168\text{ hours}$ (7 days preceding lookback window).

Observations where $t > (t_{\text{event}, i} - \delta_t)$ are strictly excluded.

---

## 2. Pre-Event Feature Accumulation Formulas

1. **Short-Term Precipitation Accumulation ($P_{1h}, P_{3h}, P_{6h}, P_{12h}, P_{24h}$)**:
   $$P_{\Delta h} = \sum_{k=0}^{\Delta h - 1} \text{precipitation}(t_{\text{event}} - k)$$

2. **Long-Term Antecedent Rainfall Accumulation ($P_{72h}, P_{168h}$)**:
   * $P_{72h}$ (3-day cumulative precipitation in mm)
   * $P_{168h}$ (7-day cumulative precipitation in mm)

3. **Soil Moisture Saturation Dynamics ($\Delta \theta_{24h}, \Delta \theta_{72h}$)**:
   $$\Delta \theta_{24h} = \theta_{0}(t_{\text{event}}) - \theta_{0}(t_{\text{event}} - 24\text{h})$$
   $$\Delta \theta_{72h} = \theta_{0}(t_{\text{event}}) - \theta_{0}(t_{\text{event}} - 72\text{h})$$
