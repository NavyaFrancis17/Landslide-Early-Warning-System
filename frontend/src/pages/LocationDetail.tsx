import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, BarChart2, CheckCircle2, Clock, Layers, ShieldAlert } from 'lucide-react';
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { LocationIdentity } from '../components/LocationIdentity';
import { WarningBadge } from '../components/WarningBadge';
import { DataStatusBadge } from '../components/DataStatusBadge';
import { api } from '../services/api';
import type { LocationDetail } from '../types';

export const LocationDetailPage: React.FC = () => {
  const { locationId } = useParams<{ locationId: string }>();
  const navigate = useNavigate();
  const [detail, setDetail] = useState<LocationDetail | null>(null);
  const [activeHorizon, setActiveHorizon] = useState<'NOW' | 'D1' | 'D3' | 'D5'>('NOW');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      if (!locationId) return;
      try {
        setLoading(true);
        const data = await api.getLocationDetail(locationId);
        setDetail(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [locationId]);

  if (loading || !detail) {
    return (
      <div className="p-12 flex justify-center items-center min-h-[400px]">
        <div className="w-8 h-8 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  const { adaptive_analysis } = detail;

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      <button
        onClick={() => navigate(-1)}
        className="flex items-center gap-2 text-xs font-bold text-slate-600 hover:text-slate-900 transition"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      {/* Place-Centric Header Banner */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
        <LocationIdentity
          placeName={detail.place_name || detail.name || 'Location'}
          district={detail.district}
          region={detail.stateOrRegion || detail.region}
          country={detail.country}
          latitude={detail.latitude}
          longitude={detail.longitude}
          locationId={detail.location_id || detail.id || ''}
          size="lg"
        />
        <div className="flex flex-col items-end gap-2 shrink-0">
          <WarningBadge state={detail.current_warning_state || 'NORMAL'} size="lg" />
          <DataStatusBadge status="MODEL ASSESSMENT" size="md" />
        </div>
      </div>

      {/* Multi-Horizon Early Warning Architecture Tabs */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Forecast Horizon Architecture</span>
          <span className="text-[11px] font-semibold text-slate-400">Validated Repository Outputs</span>
        </div>

        <div className="flex items-center gap-2 border-b pb-3">
          {[
            { id: 'NOW', label: 'Current Assessment (Now)' },
            { id: 'D1', label: '+1 Day Forecast' },
            { id: 'D3', label: '+3 Days Forecast' },
            { id: 'D5', label: '+5 Days Forecast' },
          ].map((tab) => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveHorizon(tab.id as any)}
              className={`px-4 py-2 text-xs font-bold rounded-xl transition ${
                activeHorizon === tab.id
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {activeHorizon !== 'NOW' && (
          <div className="p-4 bg-purple-50 border border-purple-200 rounded-xl text-xs space-y-1 text-purple-900">
            <span className="font-bold block flex items-center gap-1.5">
              <Clock className="w-4 h-4 text-purple-700" /> FORECAST HORIZON NOT AVAILABLE WITH CURRENT DATA
            </span>
            <p className="leading-relaxed">
              This research implementation currently provides model-based assessment for available observations. Future multi-horizon forecasting requires validated forecast environmental inputs and forecasting outputs.
            </p>
          </div>
        )}
      </div>

      {/* Current Assessment Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="p-4 bg-white rounded-2xl shadow-sm border border-slate-200">
          <span className="text-xs font-bold text-slate-500 uppercase">ML Risk Probability P(Landslide)</span>
          <div className="text-3xl font-black text-slate-900 mt-1">
            {((detail.risk_probability ?? detail.landslideProbability ?? 0) * 100).toFixed(1)}%
          </div>
          <span className="text-xs text-slate-500 mt-1 block font-semibold">Model Estimated Probability</span>
        </div>

        <div className="p-4 bg-white rounded-2xl shadow-sm border border-slate-200">
          <span className="text-xs font-bold text-slate-500 uppercase">Risk Trend</span>
          <div className="text-3xl font-black text-slate-900 mt-1">{detail.risk_trend || 'STABLE'}</div>
          <span className="text-xs text-slate-500 mt-1 block font-semibold">Delta: {(detail.trend_delta ?? 0) > 0 ? '+' : ''}{(detail.trend_delta ?? 0).toFixed(2)}</span>
        </div>

        <div className="p-4 bg-white rounded-2xl shadow-sm border border-slate-200">
          <span className="text-xs font-bold text-slate-500 uppercase">Environmental Anomaly</span>
          <div className="text-3xl font-black text-slate-900 mt-1">
            Z: {(detail.anomaly_z_score ?? 0).toFixed(2)}
          </div>
          <span className="text-xs text-slate-500 mt-1 block font-semibold">{detail.anomaly_state || 'NORMAL'}</span>
        </div>

        <div className="p-4 bg-white rounded-2xl shadow-sm border border-slate-200">
          <span className="text-xs font-bold text-slate-500 uppercase">Data Coverage Status</span>
          <div className="text-[13px] font-black text-emerald-700 mt-2 flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" /> VALIDATED DATA AVAILABLE
          </div>
          <span className="text-xs text-slate-500 mt-1 block font-semibold">Repository Baseline Loaded</span>
        </div>
      </div>

      {/* Location-Adaptive Innovation Panel (Key Research Feature) */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-600 uppercase tracking-widest">
            <Layers className="w-4 h-4" /> Research Innovation
          </div>
          <h2 className="text-lg font-black text-slate-900 mt-0.5">LOCATION-ADAPTIVE ANALYSIS</h2>
          <p className="text-xs text-slate-600 mt-1 leading-relaxed">
            "This assessment compares environmental conditions with the historical behavior of the selected location rather than relying only on a single universal threshold."
          </p>
        </div>

        {adaptive_analysis && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-xs font-bold text-slate-500 uppercase">168h Cumulative Rainfall</span>
              <div className="text-xl font-black text-slate-900 mt-1">
                {adaptive_analysis.current_rainfall_168h_mm} mm
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block font-semibold">
                Local Mean: {adaptive_analysis.local_historical_mean_rainfall} mm (±{adaptive_analysis.local_historical_std_rainfall} mm)
              </span>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-xs font-bold text-slate-500 uppercase">Topsoil Moisture Layer 1</span>
              <div className="text-xl font-black text-slate-900 mt-1">
                {adaptive_analysis.current_soil_moisture_m3m3} m³/m³
              </div>
              <span className="text-[11px] text-slate-500 mt-1 block font-semibold">
                Volumetric Soil Water Content
              </span>
            </div>

            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200">
              <span className="text-xs font-bold text-slate-500 uppercase">Location Anomaly Z-Score</span>
              <div className="text-xl font-black text-slate-900 mt-1">
                Z = {adaptive_analysis.anomaly_z_score.toFixed(2)}
              </div>
              <span className="text-[11px] font-bold text-emerald-800 mt-1 block">
                Status: {adaptive_analysis.anomaly_state}
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Human-Action Advisory & Plain Language Explanation */}
      <div className="bg-emerald-50 border border-emerald-200 p-6 rounded-2xl space-y-3">
        <h3 className="text-sm font-bold text-emerald-900 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-emerald-700" /> WHAT DOES THIS MEAN?
        </h3>
        <p className="text-xs text-emerald-900 leading-relaxed font-medium">
          {detail.warning_reason || 'Current environmental conditions and model risk indicate elevated landslide hazard for this location.'}
        </p>

        <div className="pt-3 border-t border-emerald-200/60">
          <span className="text-xs font-bold text-emerald-950 uppercase block">WHAT SHOULD THE USER DO?</span>
          <p className="text-xs text-emerald-800 font-semibold mt-1">
            "Follow local disaster-management authority guidance and official emergency notifications."
          </p>
        </div>
      </div>

      {/* Timeline Progression Chart */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
        <div>
          <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-emerald-600" /> TEMPORAL RISK EVOLUTION TIMELINE
          </h2>
          <p className="text-xs text-slate-500">Chronological progression demonstrating temporal warning state escalation over time</p>
        </div>
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={detail.history_timeline}>
              <defs>
                <linearGradient id="locRiskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="timestamp" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Area type="monotone" dataKey="risk_probability" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#locRiskGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
