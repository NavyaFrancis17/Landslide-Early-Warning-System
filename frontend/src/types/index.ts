export type WarningState = 'NORMAL' | 'WATCH' | 'WARNING' | 'HIGH_RISK';
export type RiskCategory = 'LOW' | 'WATCH' | 'WARNING' | 'HIGH RISK';
export type RiskTrend = 'INCREASING' | 'STABLE' | 'DECREASING';
export type AnomalyState = 'NORMAL' | 'ABNORMAL' | 'STRONGLY_ABNORMAL';

export type AssessmentType =
  | 'HISTORICAL OBSERVATION'
  | 'MODEL ASSESSMENT'
  | 'FORECAST'
  | 'SIMULATION'
  | 'DATA UNAVAILABLE';

export interface DashboardSummary {
  total_observations: number;
  total_locations: number;
  total_warning_events: number;
  state_distribution: Record<WarningState, number>;
  evaluation_metrics: Record<string, number | string>;
  assessment_mode: string;
}

export interface ComprehensiveLocationData {
  id: string;
  name: string;
  country: string;
  stateOrRegion: string;
  district?: string;
  region?: string;
  latitude: number;
  longitude: number;

  rainfall: number; // current rainfall (mm)
  rainfall24h: number; // 24h cumulative rainfall (mm)
  rainfall7d: number; // 7d cumulative rainfall (mm)
  soilMoisture: number; // soil moisture (%)
  slope: number; // slope (degrees)
  elevation: number; // elevation (m)
  temperature: number; // temperature (°C)

  landslideProbability: number;
  riskCategory: RiskCategory;
  riskScore: number;
  confidence: number;

  highRiskCount: number;
  warningCount: number;
  watchCount: number;

  historicalLandslides: number;
  recentEscalations: number;

  lastUpdated: string;
  baselineStatus: string;

  contributingFactors: string[];

  // Aliases for compatibility
  location_id?: string;
  place_name?: string;
  risk_probability?: number;
  current_warning_state?: WarningState;
  anomaly_z_score?: number;
  anomaly_state?: AnomalyState;
  risk_trend?: RiskTrend;
  trend_delta?: number;
  persistence_count?: number;
  warning_reason?: string;
  assessment_type?: AssessmentType;
  data_coverage_status?: string;
  latest_timestamp?: string;
  explanation?: string;
  missing_fields?: string[];

  historyTimeline?: Array<{
    timestamp: string;
    risk_probability: number;
    current_warning_state: WarningState | RiskCategory;
    rainfall?: number;
    soilMoisture?: number;
  }>;

  riskCategoryDistribution?: Partial<Record<string, number>>;
}

export type LocationSummary = ComprehensiveLocationData;

export interface HistoryPoint {
  timestamp: string;
  risk_probability: number;
  current_warning_state: WarningState;
  anomaly_z_score: number;
  risk_trend: RiskTrend;
  assessment_type?: AssessmentType;
  rainfall?: number;
  soilMoisture?: number;
}

export interface AdaptiveAnalysis {
  current_rainfall_168h_mm: number;
  current_soil_moisture_m3m3: number;
  local_historical_mean_rainfall: number;
  local_historical_std_rainfall: number;
  anomaly_z_score: number;
  anomaly_state: AnomalyState;
  explanation: string;
}

export interface LocationDetail extends ComprehensiveLocationData {
  raw_warning_state?: WarningState;
  trend_delta?: number;
  anomaly_state?: AnomalyState;
  persistence_count?: number;
  warning_reason?: string;
  adaptive_analysis?: AdaptiveAnalysis;
  history_timeline?: HistoryPoint[];
}

export interface WarningEvent {
  warning_event_id: string;
  location_id: string;
  place_name: string;
  district?: string;
  region?: string;
  country: string;
  latitude: number;
  longitude: number;
  warning_start_time: string;
  initial_state: WarningState;
  maximum_state: WarningState;
  warning_end_time?: string;
  observation_duration: number;
  assessment_type?: AssessmentType;
}

export interface WarningListResponse {
  total: number;
  offset: number;
  limit: number;
  items: WarningEvent[];
}

export interface ModelPerformanceMetrics {
  primary_model: {
    model_name: string;
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    pr_auc: number;
    brier_score: number;
    decision_threshold: number;
    training_samples: number;
    test_samples: number;
    training_period: string;
    last_trained_date: string;
    pre_event_median_lead_time_hours: number;
    pre_event_mean_lead_time_hours: number;
  };
  all_models: Array<{
    model_name: string;
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
    pr_auc: number;
    balanced_accuracy: number;
    brier_score: number;
    optimal_threshold: number;
  }>;
  academic_mode: string;
  disclaimer: string;
}

export interface EvaluationResults {
  metrics: Record<string, number>;
  lead_time_statistics: {
    matched_events_count: number;
    min_lead_time_hours: number;
    max_lead_time_hours: number;
    mean_lead_time_hours: number;
    median_lead_time_hours: number;
    bucket_counts: Record<string, number>;
  };
  false_alarm_analysis: {
    total_false_warning_events: number;
    false_alarm_rate: number;
    false_alarm_reasons_breakdown: Record<string, number>;
  };
  missed_event_analysis: {
    total_missed_landslide_events: number;
    miss_rate: number;
    miss_reasons_breakdown: Record<string, number>;
  };
  leakage_checks: Record<string, boolean>;
}

export interface SimulationScenarioDef {
  scenario_name: string;
  category: string;
  description: string;
  rainfall_multiplier: number;
  soil_moisture_multiplier: number;
}

export interface SimulationRunResponse {
  place_name: string;
  district?: string;
  region?: string;
  country: string;
  latitude: number;
  longitude: number;
  baseline_observation: Record<string, any>;
  simulated_observation: Record<string, any>;
  modifications?: Record<string, {
    original_value: number;
    scenario_value: number;
    change_amount: number;
    change_percent: number;
  }>;
  baseline_result: {
    risk_probability: number;
    warning_state: WarningState | RiskCategory;
  };
  scenario_result: {
    risk_probability: number;
    warning_state: WarningState | RiskCategory;
    anomaly_state?: AnomalyState;
    anomaly_z_score?: number;
    warning_reason?: string;
  };
  comparison: {
    scenario_name: string;
    risk_probability_change: number;
    risk_probability_change_percent: number;
    baseline_warning_state: WarningState | RiskCategory;
    scenario_warning_state: WarningState | RiskCategory;
    warning_state_changed: boolean;
    transition_type: string;
  };
  is_extrapolation: boolean;
  domain_warnings?: string[];
  explanation: string;
  assessment_type?: AssessmentType;
}

export interface SensitivityPoint {
  parameter: string;
  change_percent: number;
  multiplier: number;
  risk_probability: number;
  warning_state: WarningState;
  is_extrapolation: boolean;
}
