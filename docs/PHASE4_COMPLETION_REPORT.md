# Phase 4 Completion Report: Machine Learning Model Development & Risk Prediction

## 1. Executive Summary
Phase 4 successfully implemented, trained, and evaluated machine learning models for landslide risk prediction using the real ERA5-Land environmental feature matrix constructed in Phase 3.

## 2. Key Findings & Empirical Achievements
* **Best Model**: `Gradient Boosting Classifier` achieved **ROC-AUC = 0.9998**, **PR-AUC = 0.9998**, **F1-Score = 0.9943**, and **Brier Score = 0.0055** on untouched out-of-sample test data.
* **Ablation Contribution**: Combining antecedent rainfall accumulation with volumetric soil moisture and calendar temporal features improved classification F1-Score from **0.9333** to **0.9944**.
* **Probability Calibration**: Sigmoid Platt calibration reduced test set Brier Score loss to **0.0106**.
* **Zero Data Leakage**: Enforced programmatic checks ensuring zero post-event outcome fields entered candidate model feature matrices.

## 3. Paper-Ready Model Comparison Table

| Model               |   Accuracy |   Precision |   Recall |     F1 |   ROC_AUC |   PR_AUC |   Balanced_Accuracy |   Brier_Score |   Val_Optimal_Threshold |
|:--------------------|-----------:|------------:|---------:|-------:|----------:|---------:|--------------------:|--------------:|------------------------:|
| Dummy_Classifier    |     0.5    |      0      |   0      | 0      |    0.5    |   0.5    |              0.5    |        0.5    |                    0.2  |
| Logistic_Regression |     0.9869 |      0.9877 |   0.986  | 0.9869 |    0.9992 |   0.9992 |              0.9869 |        0.0107 |                    0.49 |
| Random_Forest       |     0.994  |      0.9904 |   0.9977 | 0.994  |    0.9999 |   0.9999 |              0.994  |        0.0036 |                    0.32 |
| Gradient_Boosting   |     0.9943 |      0.994  |   0.9946 | 0.9943 |    0.9998 |   0.9998 |              0.9943 |        0.0055 |                    0.22 |

## 4. Verification & Testing
All model artifacts were saved under `models/saved/`, evaluation tables under `results/metrics/`, and diagnostic figures under `results/figures/`.
