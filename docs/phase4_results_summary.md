# Phase 4 Machine Learning Results & Paper-Ready Tables

## Table 1: Model Comparison (Untouched Out-of-Sample Test Set)

| Model               |   Accuracy |   Precision |   Recall |     F1 |   ROC_AUC |   PR_AUC |   Balanced_Accuracy |   Brier_Score |   Val_Optimal_Threshold |
|:--------------------|-----------:|------------:|---------:|-------:|----------:|---------:|--------------------:|--------------:|------------------------:|
| Dummy_Classifier    |     0.5    |      0      |   0      | 0      |    0.5    |   0.5    |              0.5    |        0.5    |                    0.2  |
| Logistic_Regression |     0.9869 |      0.9877 |   0.986  | 0.9869 |    0.9992 |   0.9992 |              0.9869 |        0.0107 |                    0.49 |
| Random_Forest       |     0.994  |      0.9904 |   0.9977 | 0.994  |    0.9999 |   0.9999 |              0.994  |        0.0036 |                    0.32 |
| Gradient_Boosting   |     0.9943 |      0.994  |   0.9946 | 0.9943 |    0.9998 |   0.9998 |              0.9943 |        0.0055 |                    0.22 |

---

## Table 2: Feature Group Ablation Study Results

| Experiment                           |   Feature_Count |   Accuracy |   Precision |   Recall |     F1 |   ROC_AUC |   PR_AUC |   Balanced_Accuracy |   Brier_Score |
|:-------------------------------------|----------------:|-----------:|------------:|---------:|-------:|----------:|---------:|--------------------:|--------------:|
| Exp_A_Rainfall_Only                  |               8 |     0.9324 |      0.9209 |   0.9461 | 0.9333 |    0.9891 |   0.9892 |              0.9324 |        0.0427 |
| Exp_B_Rainfall_SoilMoisture          |              15 |     0.9942 |      0.9943 |   0.994  | 0.9942 |    0.9998 |   0.9998 |              0.9942 |        0.0056 |
| Exp_C_Rainfall_SoilMoisture_Temporal |              17 |     0.994  |      0.994  |   0.994  | 0.994  |    0.9993 |   0.9993 |              0.994  |        0.0058 |
| Exp_D_All_Environmental_Spatial      |              22 |     0.9944 |      0.9943 |   0.9946 | 0.9944 |    0.9998 |   0.9998 |              0.9944 |        0.0055 |

---

## Table 3: Probability Calibration & Brier Score Summary

| Model               |   Raw_Brier_Score |   Calibrated_Brier_Score |   Brier_Score_Improvement |
|:--------------------|------------------:|-------------------------:|--------------------------:|
| Logistic_Regression |            0.0107 |                   0.0106 |                    0      |
| Random_Forest       |            0.0036 |                   0.0026 |                    0.001  |
| Gradient_Boosting   |            0.0055 |                   0.0053 |                    0.0002 |

---

## Table 4: Controlled What-If Environmental Sensitivity Analysis

| Scenario           |   Precipitation_Multiplier |   Soil_Moisture_Multiplier |   Mean_Predicted_Probability |   Median_Predicted_Probability |   Mean_Probability_Delta |
|:-------------------|---------------------------:|---------------------------:|-----------------------------:|-------------------------------:|-------------------------:|
| Base (Observed)    |                       1    |                       1    |                       0.5    |                         0.5154 |                   0      |
| Precipitation +25% |                       1.25 |                       1    |                       0.5004 |                         0.6794 |                   0.0005 |
| Precipitation +50% |                       1.5  |                       1    |                       0.5009 |                         0.8008 |                   0.0009 |
| Precipitation -25% |                       0.75 |                       1    |                       0.4992 |                         0.1423 |                  -0.0007 |
| Soil Moisture +25% |                       1    |                       1.25 |                       0.4686 |                         0.013  |                  -0.0314 |
| Soil Moisture -25% |                       1    |                       0.75 |                       0.3768 |                         0.0023 |                  -0.1232 |

---

## Table 5: Feature Importance Summary (Top 10)

| Feature                         |   Importance |   Normalized_Importance |
|:--------------------------------|-------------:|------------------------:|
| soil_moisture_layer1_mean_24h   |       0.7136 |                  0.7136 |
| soil_moisture_layer1_change_72h |       0.2559 |                  0.2559 |
| precipitation_3h                |       0.0113 |                  0.0113 |
| soil_moisture_layer1_mean_72h   |       0.0053 |                  0.0053 |
| precipitation_168h              |       0.0037 |                  0.0037 |
| soil_moisture_layer1_change_24h |       0.0031 |                  0.0031 |
| soil_moisture_layer2_current    |       0.0023 |                  0.0023 |
| temperature_2m_mean_24h         |       0.0014 |                  0.0014 |
| soil_moisture_layer1_current    |       0.0014 |                  0.0014 |
| soil_moisture_layer3_current    |       0.0008 |                  0.0008 |
