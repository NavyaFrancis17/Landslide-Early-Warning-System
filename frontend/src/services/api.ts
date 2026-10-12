import type {
  ComprehensiveLocationData,
  DashboardSummary,
  EvaluationResults,
  LocationDetail,
  ModelPerformanceMetrics,
  SensitivityPoint,
  SimulationRunResponse,
  SimulationScenarioDef,
  WarningListResponse,
} from '../types';

const API_BASE = '/api';

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`API Error ${res.status}: ${errText || res.statusText}`);
  }
  return res.json();
}

export const api = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    return fetchJson<DashboardSummary>(`${API_BASE}/dashboard/summary`);
  },

  async getLocations(limit: number = 100): Promise<ComprehensiveLocationData[]> {
    return fetchJson<ComprehensiveLocationData[]>(`${API_BASE}/locations?limit=${limit}`);
  },

  async getAllLocations(): Promise<ComprehensiveLocationData[]> {
    return fetchJson<ComprehensiveLocationData[]>(`${API_BASE}/locations/all`);
  },

  async getIndiaLocations(state?: string, district?: string, warningState?: string): Promise<ComprehensiveLocationData[]> {
    let url = `${API_BASE}/locations/india`;
    const params: string[] = [];
    if (state) params.push(`state=${encodeURIComponent(state)}`);
    if (district) params.push(`district=${encodeURIComponent(district)}`);
    if (warningState) params.push(`warning_state=${encodeURIComponent(warningState)}`);
    if (params.length > 0) url += '?' + params.join('&');
    return fetchJson<ComprehensiveLocationData[]>(url);
  },

  async getIndiaStats(): Promise<{
    total_locations: number;
    verified_assessments: number;
    high_risk_count: number;
    warning_count: number;
    watch_count: number;
    low_count: number;
    data_unavailable: number;
    by_state: Record<string, number>;
    by_warning_state: Record<string, number>;
    coverage_note: string;
  }> {
    return fetchJson(`${API_BASE}/locations/india/stats`);
  },

  async getIndiaHierarchy(): Promise<{
    country: string;
    total_states: number;
    states: Record<string, { total_districts: number; districts: Record<string, { total_places: number; places: any[] }> }>;
  }> {
    return fetchJson(`${API_BASE}/locations/india/hierarchy`);
  },

  async assessGlobalLocation(query: string, lat?: number, lon?: number): Promise<any> {
    return fetchJson(`${API_BASE}/location-assessment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        location_name: query,
        latitude: lat,
        longitude: lon
      }),
    });
  },

  async autocompleteGlobalLocation(query: string): Promise<any[]> {
    if (!query) return [];
    try {
      return await fetchJson(`${API_BASE}/locations/autocomplete?q=${encodeURIComponent(query)}`);
    } catch {
      return [];
    }
  },

  async searchLocations(query: string): Promise<ComprehensiveLocationData[]> {
    return fetchJson<ComprehensiveLocationData[]>(
      `${API_BASE}/locations/search?q=${encodeURIComponent(query)}`
    );
  },

  async getLocationDetail(locationId: string): Promise<LocationDetail> {
    return fetchJson<LocationDetail>(`${API_BASE}/location/${encodeURIComponent(locationId)}`);
  },

  async getModelMetrics(): Promise<ModelPerformanceMetrics> {
    return fetchJson<ModelPerformanceMetrics>(`${API_BASE}/model/metrics`);
  },

  async getWarnings(
    state?: string,
    limit: number = 50,
    offset: number = 0,
    country?: string
  ): Promise<WarningListResponse> {
    let url = `${API_BASE}/warnings?limit=${limit}&offset=${offset}`;
    if (state) {
      url += `&state=${encodeURIComponent(state)}`;
    }
    if (country) {
      url += `&country=${encodeURIComponent(country)}`;
    }
    return fetchJson<WarningListResponse>(url);
  },

  async getEvaluationSummary(): Promise<EvaluationResults> {
    return fetchJson<EvaluationResults>(`${API_BASE}/evaluation/summary`);
  },

  async getSimulationScenarios(): Promise<SimulationScenarioDef[]> {
    return fetchJson<SimulationScenarioDef[]>(`${API_BASE}/simulation/scenarios`);
  },

  async runSimulation(payload: {
    location_id: string;
    rainfall_multiplier: number;
    soil_moisture_multiplier: number;
    scenario_name?: string;
    slope?: number;
  }): Promise<SimulationRunResponse> {
    return fetchJson<SimulationRunResponse>(`${API_BASE}/simulation/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
  },

  async getSensitivity(): Promise<SensitivityPoint[]> {
    return fetchJson<SensitivityPoint[]>(`${API_BASE}/simulation/sensitivity`);
  },
};
