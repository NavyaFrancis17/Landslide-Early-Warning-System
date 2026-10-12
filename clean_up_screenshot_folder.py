from pathlib import Path

out_dir = Path(r"C:\Users\ragav\OneDrive\Documents\Resume_Projects\Landslide\results\review_screenshots")

expected_files = {
    "01_overall_system_architecture.png",
    "02_project_process_flow.png",
    "03_dataset_validation.png",
    "04_data_preprocessing.png",
    "05_events_by_year.png",
    "06_events_by_month.png",
    "07_geographic_distribution.png",
    "08_missing_values_summary.png",
    "09_ai_risk_model_output.png",
    "10_ai_risk_prediction_chart.png",
    "11_location_adaptive_baseline.png",
    "12_environmental_anomaly.png",
    "13_anomaly_vs_risk.png",
    "14_warning_state_distribution.png",
    "15_risk_trajectory.png",
    "16_warning_transitions.png",
    "17_warning_alert_explanation.png",
    "18_event_warning_matching.png",
    "19_lead_time_distribution.png",
    "20_detection_vs_missed_events.png",
    "21_warning_match_outcomes.png",
    "22_lead_time_by_warning_state.png",
    "23_spatial_warning_event_matches.png",
    "24_scenario_risk_comparison.png",
    "25_rainfall_sensitivity_curve.png",
    "26_soil_moisture_sensitivity_curve.png",
    "27_warning_state_scenario_transition.png",
    "28_location_scenario_comparison.png",
    "29_simulation_output.png",
    "30_dashboard_home.png",
    "31_dashboard_map.png",
    "32_dashboard_warnings.png",
    "33_dashboard_evaluation.png",
    "34_dashboard_simulation.png",
    "35_dashboard_location_details.png",
    "36_dashboard_about.png",
    "37_testing_validation.png",
    "38_frontend_build.png",
    "39_backend_api_health.png",
}

# Remove files not in expected list
removed_count = 0
for p in out_dir.glob("*.png"):
    if p.name not in expected_files:
        print(f"Removing old file: {p.name}")
        p.unlink()
        removed_count += 1

remaining = sorted(list(out_dir.glob("*.png")))
print(f"\nCleanup complete. Total PNG files remaining: {len(remaining)} / 39")
for f in remaining:
    print(f"  - {f.name:<42} ({f.stat().st_size:,} bytes)")
