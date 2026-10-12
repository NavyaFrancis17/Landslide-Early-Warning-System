# AI-Based Location-Adaptive Landslide Early-Warning System

An academic research prototype for **"AI-Based Location-Adaptive Landslide Early-Warning Using Abnormal Environmental Change and Temporal Risk Escalation"**.

---

## 1. Project Phases Overview

* **Phase 1: Project Foundation & Architecture Setup** — *Completed & Validated*
* **Phase 2: Data Quality, Cleaning & Temporal Feature Engineering** — *Completed & Validated*
* **Phase 3: Real Environmental Data Integration + Spatial-Temporal Feature Construction** — *Completed & Validated*
* **Phase 4: Machine Learning Model Development, Training, Evaluation, and Risk Prediction** — *Completed & Validated*

---

## 2. Phase 4 Machine Learning Empirical Results

All models were evaluated on an untouched out-of-sample test set (`2015–2017`, `7,012 samples`) using decision thresholds tuned strictly on the validation set (`2011–2014`):

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Balanced Accuracy | Brier Score | Val Optimal Threshold |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Dummy Classifier** | `0.5000` | `0.0000` | `0.0000` | `0.0000` | `0.5000` | `0.5000` | `0.5000` | `0.5000` | `0.200` |
| **Logistic Regression** | `0.9869` | `0.9877` | `0.9860` | `0.9869` | `0.9992` | `0.9992` | `0.9869` | `0.0107` | `0.490` |
| **Random Forest** | `0.9940` | `0.9904` | `0.9977` | `0.9940` | **`0.9999`** | **`0.9999`** | `0.9940` | **`0.0036`** | `0.320` |
| **Gradient Boosting** | **`0.9943`** | **`0.9940`** | `0.9946` | **`0.9943`** | `0.9998` | `0.9998` | **`0.9943`** | `0.0055` | `0.220` |

---

## 3. Key Feature Group Ablation Summary

| Experiment | Features | Accuracy | Precision | Recall | F1-Score | ROC-AUC | PR-AUC | Brier Score |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Exp A: Rainfall Only** | 8 | `0.9324` | `0.9209` | `0.9461` | `0.9333` | `0.9891` | `0.9892` | `0.0427` |
| **Exp B: Rainfall + Soil Moisture** | 15 | `0.9942` | `0.9943` | `0.9940` | `0.9942` | `0.9998` | `0.9998` | `0.0056` |
| **Exp C: Rainfall + Soil Moisture + Temporal** | 17 | `0.9940` | `0.9940` | `0.9940` | `0.9940` | `0.9993` | `0.9993` | `0.0058` |
| **Exp D: All Environmental + Spatial** | 22 | **`0.9944`** | **`0.9943`** | `0.9946` | **`0.9944`** | **`0.9998`** | **`0.9998`** | **`0.0055`** |

---

## 4. Master Pipeline Execution

To run the complete end-to-end training and evaluation pipeline:
```bash
.\.venv\Scripts\python run_phase4_pipeline.py
```

To run the automated pytest suite (36 unit tests):
```bash
.\.venv\Scripts\pytest -v
```
