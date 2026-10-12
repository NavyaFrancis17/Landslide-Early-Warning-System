# Final Academic Project Report Figures & Screenshots Index

**Project Title:** AI-Based Location-Adaptive Landslide Early-Warning Using Abnormal Environmental Change and Temporal Risk Escalation

This directory contains the complete collection of 39 report-ready figures, charts, maps, process flows, terminal outputs, and live browser screenshots captured directly from the actual completed project implementation (Phases 1–8).

> **Scientific Integrity & Zero-Fabrication Guarantee**: Every screenshot and figure in this directory originates strictly from verified project datasets (`data/`), trained ML models (`models/`), Phase 1–7 generated outputs (`results/`), or live running application endpoints (`http://localhost:5173` and `http://127.0.0.1:8000`). Zero artificial values or mock representations were fabricated.

---

## Master Report Figure Mapping Table

| Figure No. | Filename | Figure Title | Source Phase | Source File / Command | Actual / Generated | Notes |
|:---|:---|:---|:---|:---|:---|:---|
| **Figure 3.1** | `01_overall_system_architecture.png` | Overall System Architecture | Architecture | 10-Stage Pipeline Specifications | Actual Implemented | Diagram of 10-stage system architecture from data stream to decision support. |
| **Figure 5.1** | `02_project_process_flow.png` | Project Data Processing Workflow | Process Flow | Phase 1–8 End-to-End Workflow | Actual Implemented | Process-flow diagram showing raw data ingestion to web dashboard. |
| **Figure 6.1** | `03_dataset_validation.png` | Dataset Validation Output | Phase 1 | `inspect_dataset.py` | Actual Output | Terminal validation report of 11,033 catalog events, 31 attributes, 0 duplicates. |
| **Figure 6.2** | `04_data_preprocessing.png` | Data Preprocessing Output | Phase 2 | `data/processed/event_environment_features.csv` | Actual Output | Tabular preview of processed feature matrix (168h cumulative precip & soil water). |
| **Figure 6.3** | `05_events_by_year.png` | Events by Year | Phase 2 | `docs/figures/events_by_year.png` | Actual Generated Plot | Annual distribution histogram of catalog landslide events. |
| **Figure 6.4** | `06_events_by_month.png` | Events by Month | Phase 2 | `docs/figures/events_by_month.png` | Actual Generated Plot | Monthly seasonal distribution histogram of catalog landslide events. |
| **Figure 6.5** | `07_geographic_distribution.png` | Geographic Distribution | Phase 2 | `docs/figures/geographic_distribution.png` | Actual Generated Plot | Global spatial density scatter plot of catalog landslide locations. |
| **Figure 6.6** | `08_missing_values_summary.png` | Missing Values Summary | Phase 2 | `docs/figures/missing_values_summary.png` | Actual Generated Plot | Quality profiling bar chart of missing value percentages across raw columns. |
| **Figure 6.7** | `09_ai_risk_model_output.png` | AI Risk Model Output | Phase 3 | `results/metrics/model_comparison.csv` | Actual Output | Terminal evaluation output (`GradientBoosting`: ROC-AUC 0.9998, Acc 99.43%, F1 99.27%). |
| **Figure 6.8** | `10_ai_risk_prediction_chart.png` | AI Risk Prediction Calibration | Phase 3 | `results/figures/calibration_curve.png` | Actual Generated Plot | Calibration curve comparing predicted probability against true outcome. |
| **Figure 6.9** | `11_location_adaptive_baseline.png` | Location-Adaptive Historical Baseline | Phase 4 | `results/warnings/warning_predictions.csv` | Actual Output | Terminal report of location historical mean ($\mu$), std ($\sigma$), and Z-score calculation. |
| **Figure 6.10** | `12_environmental_anomaly.png` | Environmental Anomaly Analysis | Phase 4 | `results/figures/anomaly_vs_risk.png` | Actual Generated Plot | Scatter plot comparing environmental anomaly Z-scores vs ML risk probabilities. |
| **Figure 6.11** | `13_anomaly_vs_risk.png` | Anomaly versus Risk Scatter | Phase 4 | `results/figures/anomaly_vs_risk.png` | Actual Generated Plot | Anomaly Z-score distribution across model risk states. |
| **Figure 6.12** | `14_warning_state_distribution.png` | Warning State Distribution | Phase 5 | `results/figures/warning_state_distribution.png` | Actual Generated Plot | Bar chart of Phase 5 warning state distribution (NORMAL, WATCH, WARNING, HIGH_RISK). |
| **Figure 6.13** | `15_risk_trajectory.png` | Risk Trajectory Escalation | Phase 5 | `results/figures/risk_trajectory.png` | Actual Generated Plot | Chronological trajectory plot of risk escalation over consecutive observations. |
| **Figure 6.14** | `16_warning_transitions.png` | Warning State Transitions | Phase 5 | `results/figures/warning_transitions.png` | Actual Generated Plot | State transition matrix heatmap showing progressive escalation & persistence locking. |
| **Figure 6.15** | `17_warning_alert_explanation.png` | Explainable Warning Alert | Phase 5 | `results/warnings/warning_predictions.csv` | Actual Output | Terminal output of EarlyWarningEngine record with explainable warning reason. |
| **Figure 6.16** | `18_event_warning_matching.png` | Event-Warning Matching | Phase 6 | `results/figures/spatial_warning_event_matches.png` | Actual Generated Plot | Spatial mapping of matched warning events against catalog landslide locations. |
| **Figure 6.17** | `19_lead_time_distribution.png` | Lead-Time Distribution | Phase 6 | `results/figures/lead_time_distribution.png` | Actual Generated Plot | Pre-event warning lead time distribution histogram (Median: 33.0 hours). |
| **Figure 6.18** | `20_detection_vs_missed_events.png` | Detection versus Missed Events | Phase 6 | `results/figures/detection_vs_missed_events.png` | Actual Generated Plot | Performance comparison bar chart between detected vs missed catalog landslides. |
| **Figure 6.19** | `21_warning_match_outcomes.png` | Warning Match Outcomes | Phase 6 | `results/figures/warning_match_outcomes.png` | Actual Generated Plot | Outcome breakdown of actionable warnings (True Positive matched vs False Warning). |
| **Figure 6.20** | `22_lead_time_by_warning_state.png` | Lead Time by Warning State | Phase 6 | `results/figures/lead_time_by_warning_state.png` | Actual Generated Plot | Box plot of pre-event warning lead times categorized by maximum warning state. |
| **Figure 6.21** | `23_spatial_warning_event_matches.png` | Spatial Warning-Event Matches Map | Phase 6 | `results/figures/spatial_warning_event_matches.png` | Actual Generated Plot | Geographic map visualization of spatial warning matches within 50 km radius. |
| **Figure 6.22** | `24_scenario_risk_comparison.png` | Scenario Risk Comparison | Phase 7 | `results/figures/scenario_risk_comparison.png` | Actual Generated Plot | Comparison plot of baseline vs simulated risk probabilities across 14 scenarios. |
| **Figure 6.23** | `25_rainfall_sensitivity_curve.png` | Rainfall Sensitivity Analysis | Phase 7 | `results/figures/rainfall_sensitivity_curve.png` | Actual Generated Plot | Controlled sensitivity curve of precipitation modifications (-10% to +100%) vs Risk. |
| **Figure 6.24** | `26_soil_moisture_sensitivity_curve.png` | Soil-Moisture Sensitivity Analysis | Phase 7 | `results/figures/soil_moisture_sensitivity_curve.png` | Actual Generated Plot | Controlled sensitivity curve of soil moisture modifications (-10% to +50%) vs Risk. |
| **Figure 6.25** | `27_warning_state_scenario_transition.png` | Warning-State Scenario Transition | Phase 7 | `results/figures/warning_state_scenario_transition.png` | Actual Generated Plot | Transition matrix heatmap of warning states under counterfactual scenarios. |
| **Figure 6.26** | `28_location_scenario_comparison.png` | Location Scenario Comparison | Phase 7 | `results/figures/location_scenario_comparison.png` | Actual Generated Plot | Multi-location counterfactual comparison plot across 20 evaluated location grid cells. |
| **Figure 6.27** | `29_simulation_output.png` | What-If Simulation Output | Phase 7 | `results/simulation/simulation_summary.json` | Actual Output | Terminal summary output of 1,400 scenario runs (99.29% in-domain, 0.71% extrapolation). |
| **Figure 6.28** | `30_dashboard_home.png` | Final Web Dashboard Home | Phase 8 | `http://localhost:5173/dashboard` | Live Web Screenshot | Main overview dashboard with search, map, KPI cards, priority list, trajectory chart. |
| **Figure 6.29** | `31_dashboard_map.png` | Geographic Warning Map View | Phase 8 | `http://localhost:5173/map` | Live Web Screenshot | Full-screen interactive Leaflet map view with place-centric popups & filters. |
| **Figure 6.30** | `32_dashboard_warnings.png` | Early Warning Management Log | Phase 8 | `http://localhost:5173/warnings` | Live Web Screenshot | Paginated warning history table with multi-filters and place identity columns. |
| **Figure 6.31** | `33_dashboard_evaluation.png` | Event Evaluation Dashboard | Phase 8 | `http://localhost:5173/evaluation` | Live Web Screenshot | Quantitative Phase 6 evaluation metrics page & software validation section. |
| **Figure 6.32** | `34_dashboard_simulation.png` | What-If Simulation Dashboard | Phase 8 | `http://localhost:5173/simulation` | Live Web Screenshot | Interactive scenario controls, ΔP comparison cards, and sensitivity curves page. |
| **Figure 6.33** | `35_dashboard_location_details.png` | Location Details Dashboard | Phase 8 | `http://localhost:5173/location/loc_12.97_80.18` | Live Web Screenshot | Location-adaptive analysis panel, forecast architecture tabs, and risk evolution. |
| **Figure 6.34** | `36_dashboard_about.png` | About / System Information Page | Phase 8 | `http://localhost:5173/about` | Live Web Screenshot | 10 key methodological contributions, sitemap, and scientific integrity guarantees. |
| **Figure 7.1** | `37_testing_validation.png` | Automated Testing Validation | Phase 8 | `pytest -v` | Actual Output | Terminal output of 68/68 automated integration tests passed (100% test validation). |
| **Figure 7.2** | `38_frontend_build.png` | Frontend Production Build | Phase 8 | `npm run build` | Actual Output | Terminal output of Vite production bundle build (0 compilation errors). |
| **Figure 7.3** | `39_backend_api_health.png` | Backend API Health Check | Phase 8 | `http://127.0.0.1:8000/api/health` | Actual Output | HTTP 200 OK health check response (`{"status": "healthy", "service": "..."}`). |

---

## Directory Summary
- **Total PNG Figures**: 39
- **Index File**: `README.md`
- **Location**: `results/review_screenshots/`
