# Chronological Train / Validation / Test Split Protocol

## 1. Research Rationale

Landslide risk forecasting systems operate sequentially in real time. Random k-fold cross-validation or random train-test splitting introduces **temporal lookahead leakage** by allowing models to train on future events while predicting past events.

Therefore, Phase 3 defines a strict **chronological split protocol**:

$$\text{Train Period} < \text{Validation Period} < \text{Test Period}$$

---

## 2. Dataset Chronological Split Boundaries

Based on the temporal distribution of the NASA Global Landslide Catalog (1988–2017):

| Dataset Split | Date Range | Event Count | Percentage | Research Function |
| :--- | :--- | :--- | :--- | :--- |
| **Training Set** | `1988-11-07` to `2010-12-31` | `6,624` | `60.03%` | Primary model parameter estimation & baseline calibration. |
| **Validation Set**| `2011-01-01` to `2014-12-31` | `2,207` | `20.00%` | Hyperparameter optimization & threshold tuning. |
| **Test Set** | `2015-01-01` to `2017-09-28` | `2,202` | `19.96%` | Final out-of-sample evaluation & lead-time simulation. |

---

## 3. Strict Temporal Split Enforcement

* No sample from `2011-01-01` or later may be present in the training set.
* The test set occurs strictly after the training and validation windows.
