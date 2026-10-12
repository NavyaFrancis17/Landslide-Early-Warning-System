# Label Definition & Control Sampling Strategy

## 1. Positive Event Labels ($y = 1$)

* **Definition**: Historical landslide records documented in the NASA Global Landslide Catalog (`data/processed/landslide_events_clean.csv`) with validated coordinates and timestamps.
* **Positive Sample Representation**: Each row in `data/processed/event_environment_features.csv` represents a confirmed positive landslide event ($y = 1$).

---

## 2. Scientific Limitations of Catalog Labels

1. **Absence of Negative Observations ($y = 0$)**: The NASA catalog is an *incident-only catalog*. Absence of a record on a given day/location does not guarantee zero slope failure (under-reporting bias).
2. **Imbalance & False Controls**: Indiscriminately labeling all non-landslide timestamps as negative examples introduces noisy or invalid control labels.

---

## 3. Control Sampling Strategy Framework (Phase 4 Foundation)

To construct balanced training matrices in Phase 4 without label contamination:

1. **Spatio-Temporal Exclusion Windows**:
   Control/negative samples ($y = 0$) must be sampled at locations $L_c$ and timestamps $t_c$ satisfying:
   * $\text{Distance}(L_c, L_{\text{event}}) \ge 50\text{ km}$ OR
   * $|t_c - t_{\text{event}}| \ge 30\text{ days}$

2. **Environmental Availability**:
   Control samples must undergo identical spatial and temporal ERA5-Land feature extraction ($t < t_c$).
