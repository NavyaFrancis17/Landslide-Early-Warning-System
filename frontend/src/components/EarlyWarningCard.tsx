import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowUpRight,
  ChevronDown,
  ChevronUp,
  Droplets,
  Info,
  Layers,
  Mountain,
  ShieldAlert,
  Thermometer,
  Wind,
} from 'lucide-react';
import { LocationIdentity } from './LocationIdentity';
import { WarningBadge } from './WarningBadge';
import { DataStatusBadge } from './DataStatusBadge';
import type { ComprehensiveLocationData } from '../types';
import { normalizeRiskCategory } from '../utils/riskThresholds';

interface EarlyWarningCardProps {
  locationData: ComprehensiveLocationData;
}

export const EarlyWarningCard: React.FC<EarlyWarningCardProps> = ({ locationData }) => {
  const navigate = useNavigate();
  const [showTechDetails, setShowTechDetails] = useState<boolean>(false);

  const loc = locationData;
  const locId = loc.id || loc.location_id || '';
  const placeName = loc.name || loc.place_name || 'Evaluated Location';
  const region = loc.stateOrRegion || loc.region || '';
  const district = loc.district || region;
  const country = loc.country || 'International Coverage';
  const lat = loc.latitude;
  const lon = loc.longitude;
  const riskProb = loc.landslideProbability ?? loc.risk_probability ?? 0;
  const riskCat = loc.riskCategory || normalizeRiskCategory(loc.current_warning_state);
  const trend = loc.risk_trend || (loc.recentEscalations > 0 ? 'INCREASING' : 'STABLE');

  const getTrendIcon = (t: string) => {
    switch (t) {
      case 'INCREASING':
        return <span className="text-red-600 font-bold">↑ Increasing</span>;
      case 'DECREASING':
        return <span className="text-emerald-600 font-bold">↓ Decreasing</span>;
      case 'STABLE':
      default:
        return <span className="text-slate-600 font-semibold">→ Stable</span>;
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6 space-y-5 hover:shadow-md transition">
      {/* Header Row */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b pb-4">
        <LocationIdentity
          placeName={placeName}
          district={district}
          region={region}
          country={country}
          latitude={lat}
          longitude={lon}
          locationId={locId}
          size="md"
        />
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <WarningBadge state={loc.current_warning_state || (riskCat as any)} size="md" />
          <DataStatusBadge status={loc.assessment_type || 'MODEL ASSESSMENT'} size="sm" />
        </div>
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-3 gap-2.5">
        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold text-slate-500 uppercase block">Risk Probability</span>
          <span className="text-xl font-black text-slate-900 mt-0.5 block">
            {(riskProb * 100).toFixed(1)}%
          </span>
          <span className="text-[10px] text-slate-400 font-semibold mt-0.5 block">
            Conf: {((loc.confidence || 0.9) * 100).toFixed(0)}%
          </span>
        </div>

        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold text-slate-500 uppercase block">Risk Trend</span>
          <div className="text-xs mt-1">{getTrendIcon(trend)}</div>
          <span className="text-[10px] text-slate-400 font-semibold mt-0.5 block">
            {loc.recentEscalations} escalations
          </span>
        </div>

        <div className="p-3 bg-slate-50 rounded-xl border border-slate-200">
          <span className="text-[10px] font-bold text-slate-500 uppercase block">Risk Category</span>
          <span
            className={`text-xs font-black mt-1 block uppercase px-2 py-0.5 rounded border inline-block ${
              riskCat === 'HIGH RISK'
                ? 'bg-red-100 text-red-900 border-red-300'
                : riskCat === 'WARNING'
                ? 'bg-orange-100 text-orange-900 border-orange-300'
                : riskCat === 'WATCH'
                ? 'bg-amber-100 text-amber-900 border-amber-300'
                : 'bg-emerald-100 text-emerald-900 border-emerald-300'
            }`}
          >
            {riskCat}
          </span>
        </div>
      </div>

      {/* Environmental Parameters Grid */}
      <div className="space-y-2">
        <span className="text-[11px] font-extrabold uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-emerald-600" /> Environmental Features & Terrain
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
          <div className="p-2.5 bg-slate-50/80 rounded-xl border border-slate-200">
            <div className="flex items-center gap-1 text-slate-500 text-[10px] font-bold uppercase">
              <Droplets className="w-3 h-3 text-blue-500" /> Rainfall (24h / 7d)
            </div>
            <div className="font-extrabold text-slate-900 mt-1">
              {loc.rainfall24h} mm <span className="text-[10px] text-slate-500 font-normal">/ {loc.rainfall7d} mm</span>
            </div>
          </div>

          <div className="p-2.5 bg-slate-50/80 rounded-xl border border-slate-200">
            <div className="flex items-center gap-1 text-slate-500 text-[10px] font-bold uppercase">
              <Wind className="w-3 h-3 text-cyan-600" /> Topsoil Moisture
            </div>
            <div className="font-extrabold text-slate-900 mt-1">
              {loc.soilMoisture}% <span className="text-[10px] text-slate-500 font-normal">vol</span>
            </div>
          </div>

          <div className="p-2.5 bg-slate-50/80 rounded-xl border border-slate-200">
            <div className="flex items-center gap-1 text-slate-500 text-[10px] font-bold uppercase">
              <Mountain className="w-3 h-3 text-amber-700" /> Slope / Elev
            </div>
            <div className="font-extrabold text-slate-900 mt-1">
              {loc.slope}° <span className="text-[10px] text-slate-500 font-normal">/ {loc.elevation}m</span>
            </div>
          </div>

          <div className="p-2.5 bg-slate-50/80 rounded-xl border border-slate-200">
            <div className="flex items-center gap-1 text-slate-500 text-[10px] font-bold uppercase">
              <Thermometer className="w-3 h-3 text-orange-500" /> Temperature
            </div>
            <div className="font-extrabold text-slate-900 mt-1">
              {loc.temperature}°C
            </div>
          </div>
        </div>
      </div>

      {/* Triggering & Contributing Factors */}
      {loc.contributingFactors && loc.contributingFactors.length > 0 && (
        <div className="p-3.5 bg-emerald-50 border border-emerald-200 rounded-xl text-xs space-y-1.5">
          <span className="font-bold text-emerald-950 block flex items-center gap-1.5 text-[11px] uppercase tracking-wide">
            <ShieldAlert className="w-4 h-4 text-emerald-700" /> Primary Contributing Factors
          </span>
          <ul className="space-y-1 text-emerald-900 font-medium list-disc list-inside">
            {loc.contributingFactors.map((factor, idx) => (
              <li key={idx} className="leading-snug">{factor}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Technical Expandable Details */}
      <div>
        <button
          type="button"
          onClick={() => setShowTechDetails(!showTechDetails)}
          className="text-xs font-semibold text-slate-500 hover:text-slate-800 transition flex items-center gap-1 font-mono"
        >
          {showTechDetails ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          {showTechDetails ? 'Hide Technical Parameters' : 'Technical Details & Baseline'}
        </button>

        {showTechDetails && (
          <div className="mt-2 p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs font-mono space-y-1 text-slate-700">
            <div>Technical ID: {locId}</div>
            <div>Anomaly Z-Score: {(loc.anomaly_z_score ?? 0).toFixed(2)}</div>
            <div>High Risk Assessments: {loc.highRiskCount}</div>
            <div>Warning Assessments: {loc.warningCount}</div>
            <div>Watch Assessments: {loc.watchCount}</div>
            <div>Baseline Status: {loc.baselineStatus || 'VALIDATED_DATA_AVAILABLE'}</div>
            <div>Last Updated: {loc.lastUpdated}</div>
          </div>
        )}
      </div>

      {/* Footer Disclaimer & Deep Dive Navigation */}
      <div className="pt-3 border-t border-slate-100 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="text-slate-500 text-[11px] font-medium flex items-center gap-1.5">
          <Info className="w-3.5 h-3.5 text-slate-400 shrink-0" />
          Last Updated: <span className="font-bold text-slate-700">{loc.lastUpdated}</span>
        </div>
        <button
          onClick={() => navigate(`/location/${encodeURIComponent(locId)}`)}
          className="px-3.5 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl transition flex items-center gap-1 shrink-0 text-xs shadow-sm"
        >
          Detailed Analysis <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
