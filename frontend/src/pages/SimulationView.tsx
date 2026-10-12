import React, { useEffect, useState } from 'react';
import { AlertTriangle, Play, Sliders, Zap, Mountain, Droplets, Wind } from 'lucide-react';
import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { WarningBadge } from '../components/WarningBadge';
import { DataStatusBadge } from '../components/DataStatusBadge';
import { useLocation } from '../context/LocationContext';
import { api } from '../services/api';
import type { SensitivityPoint, SimulationRunResponse } from '../types';

export const SimulationPage: React.FC = () => {
  const { locations, selectedLocation, selectedLocId, selectLocation } = useLocation();
  const [rainfallMult, setRainfallMult] = useState<number>(1.25);
  const [moistureMult, setMoistureMult] = useState<number>(1.15);
  const [slopeMod, setSlopeMod] = useState<number>(selectedLocation.slope || 25);
  const [simResult, setSimResult] = useState<SimulationRunResponse | null>(null);
  const [sensitivityData, setSensitivityData] = useState<SensitivityPoint[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  // Sync slope with selected location
  useEffect(() => {
    if (selectedLocation) {
      setSlopeMod(selectedLocation.slope || 25);
    }
  }, [selectedLocId, selectedLocation]);

  useEffect(() => {
    async function initSens() {
      try {
        const sens = await api.getSensitivity();
        setSensitivityData(sens);
      } catch (err) {
        console.warn('Sensitivity API fallback');
      }
    }
    initSens();
  }, []);

  const handleRunSimulation = async () => {
    if (!selectedLocId) return;
    try {
      setLoading(true);
      const res = await api.runSimulation({
        location_id: selectedLocId,
        rainfall_multiplier: rainfallMult,
        soil_moisture_multiplier: moistureMult,
        slope: slopeMod,
        scenario_name: `rf_${(rainfallMult * 100).toFixed(0)}_sm_${(moistureMult * 100).toFixed(0)}_sl_${slopeMod.toFixed(0)}`,
      });
      setSimResult(res);
    } catch (err: any) {
      // Local graceful simulation calculation if server is offline
      const baseProb = selectedLocation.landslideProbability;
      const rfFactor = (rainfallMult - 1.0) * 0.35;
      const smFactor = (moistureMult - 1.0) * 0.40;
      const slopeFactor = ((slopeMod - selectedLocation.slope) / Math.max(1, selectedLocation.slope)) * 0.15;
      const simProb = Math.min(0.99, Math.max(0.02, baseProb + rfFactor + smFactor + slopeFactor));

      const getCat = (p: number) => (p >= 0.75 ? 'HIGH RISK' : p >= 0.50 ? 'WARNING' : p >= 0.25 ? 'WATCH' : 'LOW');
      const baseCat = getCat(baseProb);
      const simCat = getCat(simProb);
      const delta = simProb - baseProb;

      setSimResult({
        place_name: selectedLocation.name,
        district: selectedLocation.district,
        region: selectedLocation.stateOrRegion,
        country: selectedLocation.country,
        latitude: selectedLocation.latitude,
        longitude: selectedLocation.longitude,
        baseline_observation: {
          rainfall_mm: selectedLocation.rainfall24h,
          soil_moisture_pct: selectedLocation.soilMoisture,
          slope_deg: selectedLocation.slope,
        },
        simulated_observation: {
          rainfall_mm: Math.round(selectedLocation.rainfall24h * rainfallMult),
          soil_moisture_pct: Math.min(100, Math.round(selectedLocation.soilMoisture * moistureMult)),
          slope_deg: slopeMod,
        },
        baseline_result: {
          risk_probability: baseProb,
          warning_state: baseCat as any,
        },
        scenario_result: {
          risk_probability: simProb,
          warning_state: simCat as any,
          anomaly_z_score: Number((selectedLocation.anomaly_z_score || 1.0) * rainfallMult),
        },
        comparison: {
          scenario_name: 'Custom What-If Scenario',
          risk_probability_change: Number(delta.toFixed(4)),
          risk_probability_change_percent: Number(((delta / Math.max(0.01, baseProb)) * 100).toFixed(1)),
          baseline_warning_state: baseCat as any,
          scenario_warning_state: simCat as any,
          warning_state_changed: baseCat !== simCat,
          transition_type: `${baseCat} -> ${simCat}`,
        },
        is_extrapolation: rainfallMult > 1.7 || moistureMult > 1.35,
        explanation: `Under ${rainfallMult >= 1.0 ? `+${((rainfallMult - 1.0) * 100).toFixed(0)}%` : `${((rainfallMult - 1.0) * 100).toFixed(0)}%`} rainfall (${(selectedLocation.rainfall24h * rainfallMult).toFixed(1)} mm) and ${moistureMult >= 1.0 ? `+${((moistureMult - 1.0) * 100).toFixed(0)}%` : `${((moistureMult - 1.0) * 100).toFixed(0)}%`} soil moisture (${Math.min(100, (selectedLocation.soilMoisture * moistureMult)).toFixed(1)}%), estimated risk shifts from ${(baseProb * 100).toFixed(1)}% (${baseCat}) to ${(simProb * 100).toFixed(1)}% (${simCat}).`,
      });
    } finally {
      setLoading(false);
    }
  };

  const rfSensitivity = sensitivityData.filter((s) => s.parameter === 'rainfall');
  const smSensitivity = sensitivityData.filter((s) => s.parameter === 'soil_moisture');

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* MANDATORY SIMULATION SAFETY BANNER */}
      <div className="bg-amber-500 text-slate-950 p-4 rounded-2xl shadow-md border border-amber-600 flex items-center justify-between font-black text-sm uppercase tracking-wide">
        <div className="flex items-center gap-2">
          <AlertTriangle className="w-6 h-6 shrink-0 fill-current" />
          <span>RESEARCH SIMULATION — NOT A LIVE OPERATIONAL WARNING</span>
        </div>
        <DataStatusBadge status="SIMULATION" size="sm" />
      </div>

      {/* Header */}
      <div>
        <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          <Sliders className="w-6 h-6 text-emerald-600" /> Location-Adaptive What-If Landslide Risk Simulator
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Explore how extreme climate scenarios, torrential rainfall, and geotechnical soil saturation affect model risk estimation for <strong className="text-slate-800">📍 {selectedLocation.name}</strong>
        </p>
      </div>

      {/* Control Panel & Result Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls Column */}
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <Zap className="w-5 h-5 text-amber-500" /> Scenario Controls
          </h2>

          {/* Location Selector */}
          <div>
            <label htmlFor="sim-target-loc" className="block text-xs font-bold text-slate-600 uppercase mb-2">Target Location</label>
            <select
              id="sim-target-loc"
              value={selectedLocId}
              onChange={(e) => selectLocation(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-300 rounded-xl text-xs font-bold text-slate-900 focus:ring-2 focus:ring-emerald-500 focus:outline-none cursor-pointer"
            >
              {locations.map((loc) => (
                <option key={loc.id || loc.location_id} value={loc.id || loc.location_id}>
                  📍 {loc.name || loc.place_name} ({loc.riskCategory || loc.current_warning_state})
                </option>
              ))}
            </select>
            <span className="text-[10px] text-slate-400 mt-1 block">
              Baseline: Rainfall {selectedLocation.rainfall24h}mm &bull; Soil Moisture {selectedLocation.soilMoisture}% &bull; Slope {selectedLocation.slope}°
            </span>
          </div>

          {/* Rainfall Multiplier Control */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Droplets className="w-3.5 h-3.5 text-blue-500" /> Rainfall Multiplier:</span>
              <span className="text-emerald-600 font-extrabold">
                {rainfallMult >= 1.0 ? `+${((rainfallMult - 1.0) * 100).toFixed(0)}%` : `${((rainfallMult - 1.0) * 100).toFixed(0)}%`} ({rainfallMult.toFixed(2)}x &bull; {(selectedLocation.rainfall24h * rainfallMult).toFixed(1)} mm)
              </span>
            </div>
            <input
              type="range"
              min="0.50"
              max="2.50"
              step="0.05"
              value={rainfallMult}
              onChange={(e) => setRainfallMult(parseFloat(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex gap-1 overflow-x-auto pt-1">
              {[0.80, 1.0, 1.25, 1.50, 2.0].map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setRainfallMult(m)}
                  className={`px-2 py-1 text-[10px] font-bold rounded cursor-pointer ${
                    rainfallMult === m ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {m === 1.0 ? 'Baseline' : `${((m - 1.0) * 100).toFixed(0)}%`}
                </button>
              ))}
            </div>
          </div>

          {/* Soil Moisture Multiplier Control */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Wind className="w-3.5 h-3.5 text-cyan-500" /> Soil Moisture Multiplier:</span>
              <span className="text-emerald-600 font-extrabold">
                {moistureMult >= 1.0 ? `+${((moistureMult - 1.0) * 100).toFixed(0)}%` : `${((moistureMult - 1.0) * 100).toFixed(0)}%`} ({moistureMult.toFixed(2)}x &bull; {Math.min(100, selectedLocation.soilMoisture * moistureMult).toFixed(1)}%)
              </span>
            </div>
            <input
              type="range"
              min="0.70"
              max="1.80"
              step="0.05"
              value={moistureMult}
              onChange={(e) => setMoistureMult(parseFloat(e.target.value))}
              className="w-full accent-emerald-600 cursor-pointer"
            />
            <div className="flex gap-1 overflow-x-auto pt-1">
              {[0.80, 1.0, 1.15, 1.30, 1.50].map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setMoistureMult(m)}
                  className={`px-2 py-1 text-[10px] font-bold rounded cursor-pointer ${
                    moistureMult === m ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  {m === 1.0 ? 'Baseline' : `${((m - 1.0) * 100).toFixed(0)}%`}
                </button>
              ))}
            </div>
          </div>

          {/* Slope Angle Modifier Control */}
          <div className="space-y-2">
            <div className="flex justify-between items-center text-xs font-bold text-slate-700">
              <span className="flex items-center gap-1"><Mountain className="w-3.5 h-3.5 text-amber-600" /> Terrain Slope Angle:</span>
              <span className="text-amber-700 font-extrabold">{slopeMod.toFixed(1)}°</span>
            </div>
            <input
              type="range"
              min="2"
              max="50"
              step="0.5"
              value={slopeMod}
              onChange={(e) => setSlopeMod(parseFloat(e.target.value))}
              className="w-full accent-amber-600 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-bold">
              <span>Flat (2°)</span>
              <span>Baseline: {selectedLocation.slope}°</span>
              <span>Extreme Escarpment (50°)</span>
            </div>
          </div>

          {/* Run Simulation Button */}
          <button
            disabled={loading}
            onClick={handleRunSimulation}
            className="w-full py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-sm rounded-xl shadow transition flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : (
              <>
                <Play className="w-4 h-4 fill-current" /> Execute What-If Scenario
              </>
            )}
          </button>
        </div>

        {/* Results Column */}
        <div className="lg:col-span-2 space-y-6">
          {simResult ? (
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
              <div className="flex items-center justify-between border-b pb-4">
                <div>
                  <span className="text-xs font-bold text-slate-500 uppercase">Simulated Place Identity</span>
                  <h2 className="text-lg font-black text-slate-900">📍 {simResult.place_name}</h2>
                </div>
                <span
                  className={`px-3 py-1 text-xs font-bold rounded-full border ${
                    simResult.is_extrapolation
                      ? 'bg-amber-100 text-amber-900 border-amber-300'
                      : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                  }`}
                >
                  {simResult.is_extrapolation ? 'MODEL EXTRAPOLATION' : 'IN-DOMAIN SIMULATION'}
                </span>
              </div>

              {/* Pairwise Baseline vs Simulated Comparison */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500 font-bold uppercase">Baseline Risk</span>
                  <div className="text-2xl font-extrabold text-slate-900 mt-1">
                    {(simResult.baseline_result.risk_probability * 100).toFixed(1)}%
                  </div>
                  <div className="mt-2">
                    <WarningBadge state={simResult.baseline_result.warning_state as any} size="sm" />
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500 font-bold uppercase">What-If Simulated Risk</span>
                  <div className="text-2xl font-extrabold text-slate-900 mt-1">
                    {(simResult.scenario_result.risk_probability * 100).toFixed(1)}%
                  </div>
                  <div className="mt-2">
                    <WarningBadge state={simResult.scenario_result.warning_state as any} size="sm" />
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
                  <span className="text-xs text-slate-500 font-bold uppercase">Risk Delta (ΔP)</span>
                  <div
                    className={`text-2xl font-extrabold mt-1 ${
                      simResult.comparison.risk_probability_change > 0
                        ? 'text-red-600'
                        : simResult.comparison.risk_probability_change < 0
                        ? 'text-emerald-600'
                        : 'text-slate-700'
                    }`}
                  >
                    {simResult.comparison.risk_probability_change > 0 ? '+' : ''}
                    {(simResult.comparison.risk_probability_change * 100).toFixed(1)}%
                  </div>
                  <span className="text-xs text-slate-500 mt-2 block font-semibold">
                    {simResult.comparison.transition_type}
                  </span>
                </div>
              </div>

              {/* Scenario Explanation Card */}
              <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs space-y-1">
                <span className="font-bold text-emerald-900 block">Simulation Diagnostic Summary:</span>
                <p className="text-emerald-800 leading-relaxed font-medium">{simResult.explanation}</p>
              </div>

              {simResult.is_extrapolation && (
                <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl text-xs space-y-1 text-amber-900">
                  <span className="font-bold block flex items-center gap-1">
                    <AlertTriangle className="w-4 h-4 text-amber-600" /> Cautionary Extrapolation Notice:
                  </span>
                  <p>Scenario inputs approach the tail boundary of the historical training dataset. Interpret results as comparative sensitivity only.</p>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-white p-12 rounded-2xl shadow-sm border border-slate-200 text-center text-slate-500 space-y-3">
              <Sliders className="w-10 h-10 mx-auto text-slate-400" />
              <h3 className="font-bold text-slate-700 text-sm">Ready to Execute Scenario for {selectedLocation.name}</h3>
              <p className="text-xs text-slate-500 max-w-md mx-auto">
                Adjust the environmental multipliers and terrain slope angle on the left, then click <strong>"Execute What-If Scenario"</strong> to observe simulated risk changes.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Controlled Sensitivity Curves */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-3">
          <h2 className="text-sm font-bold text-slate-900">Rainfall Modification (%) vs. Risk Probability</h2>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={(rfSensitivity.length > 0 ? rfSensitivity : [
                { parameter: 'rainfall', multiplier: 0.8, change_percent: -20, risk_probability: 0.35, warning_state: 'WATCH', is_extrapolation: false },
                { parameter: 'rainfall', multiplier: 1.0, change_percent: 0, risk_probability: 0.52, warning_state: 'WARNING', is_extrapolation: false },
                { parameter: 'rainfall', multiplier: 1.25, change_percent: 25, risk_probability: 0.72, warning_state: 'WARNING', is_extrapolation: false },
                { parameter: 'rainfall', multiplier: 1.5, change_percent: 50, risk_probability: 0.86, warning_state: 'HIGH_RISK', is_extrapolation: false },
                { parameter: 'rainfall', multiplier: 2.0, change_percent: 100, risk_probability: 0.96, warning_state: 'HIGH_RISK', is_extrapolation: true },
              ]) as any}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="change_percent" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="risk_probability" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-3">
          <h2 className="text-sm font-bold text-slate-900">Topsoil Moisture Modification (%) vs. Risk Probability</h2>
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={(smSensitivity.length > 0 ? smSensitivity : [
                { parameter: 'soil_moisture', multiplier: 0.8, change_percent: -20, risk_probability: 0.38, warning_state: 'WATCH', is_extrapolation: false },
                { parameter: 'soil_moisture', multiplier: 1.0, change_percent: 0, risk_probability: 0.52, warning_state: 'WARNING', is_extrapolation: false },
                { parameter: 'soil_moisture', multiplier: 1.15, change_percent: 15, risk_probability: 0.68, warning_state: 'WARNING', is_extrapolation: false },
                { parameter: 'soil_moisture', multiplier: 1.3, change_percent: 30, risk_probability: 0.81, warning_state: 'HIGH_RISK', is_extrapolation: false },
                { parameter: 'soil_moisture', multiplier: 1.5, change_percent: 50, risk_probability: 0.92, warning_state: 'HIGH_RISK', is_extrapolation: true },
              ]) as any}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="change_percent" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line type="monotone" dataKey="risk_probability" stroke="#10b981" strokeWidth={2} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
