import React, { useEffect, useMemo, useRef } from 'react';
import {
  Circle,
  CircleMarker,
  MapContainer,
  Popup,
  TileLayer,
  useMap,
} from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-cluster';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import type { ComprehensiveLocationData } from '../types';

// ─── India bounds ─────────────────────────────────────────────────────────────
const INDIA_BOUNDS: L.LatLngBoundsExpression = [
  [6.5, 68.0],   // SW corner
  [37.5, 97.5],  // NE corner
];
const INDIA_CENTER: [number, number] = [22.5, 82.5];

// ─── Risk colour map ──────────────────────────────────────────────────────────
function getRiskColor(cat: string): string {
  switch (cat) {
    case 'HIGH RISK':
    case 'HIGH_RISK': return '#ef4444';
    case 'WARNING':   return '#f97316';
    case 'WATCH':     return '#eab308';
    default:          return '#22c55e';
  }
}

function normalizeCategory(loc: ComprehensiveLocationData): string {
  const ws = loc.current_warning_state || '';
  const rc = loc.riskCategory || '';
  if (ws === 'HIGH_RISK' || rc === 'HIGH RISK') return 'HIGH RISK';
  if (ws === 'WARNING' || rc === 'WARNING') return 'WARNING';
  if (ws === 'WATCH' || rc === 'WATCH') return 'WATCH';
  return 'LOW';
}

function trendLabel(trend: string | undefined): string {
  if (!trend) return '→ Stable';
  if (trend === 'INCREASING') return '↑ Increasing';
  if (trend === 'DECREASING') return '↓ Decreasing';
  return '→ Stable';
}

// ─── Sub: FitIndia — fits map to India bounds on mount ───────────────────────
const FitIndia: React.FC = () => {
  const map = useMap();
  useEffect(() => {
    map.fitBounds(INDIA_BOUNDS, { padding: [20, 20] });
  }, [map]);
  return null;
};

// ─── Sub: RecenterMap — flies to selected location ────────────────────────────
const RecenterMap: React.FC<{ lat: number; lon: number }> = ({ lat, lon }) => {
  const map = useMap();
  const prevRef = useRef<string>('');
  useEffect(() => {
    const key = `${lat},${lon}`;
    if (key !== prevRef.current && !isNaN(lat) && !isNaN(lon)) {
      prevRef.current = key;
      map.flyTo([lat, lon], 10, { duration: 1.0 });
    }
  }, [lat, lon, map]);
  return null;
};

// ─── Custom cluster icon factory ──────────────────────────────────────────────
function createClusterIcon(cluster: any) {
  const count = cluster.getChildCount();
  const size = count > 500 ? 44 : count > 100 ? 38 : count > 20 ? 32 : 26;
  const bg = count > 100 ? '#dc2626' : count > 20 ? '#f97316' : '#eab308';
  return L.divIcon({
    html: `<div style="
      width:${size}px; height:${size}px;
      background:${bg}; color:#fff;
      border-radius:50%; display:flex; align-items:center; justify-content:center;
      font-size:${size > 36 ? 13 : 11}px; font-weight:900;
      border: 2.5px solid rgba(255,255,255,0.8);
      box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    ">${count > 999 ? '999+' : count}</div>`,
    className: '',
    iconSize: [size, size],
    iconAnchor: [size / 2, size / 2],
  });
}

// ─── Props ────────────────────────────────────────────────────────────────────
interface IndiaMapComponentProps {
  locations: ComprehensiveLocationData[];
  selectedLocationId?: string;
  onSelectLocation?: (locationId: string) => void;
  height?: string;
}

// ─── Main component ───────────────────────────────────────────────────────────
export const IndiaMapComponent: React.FC<IndiaMapComponentProps> = ({
  locations,
  selectedLocationId,
  onSelectLocation,
  height = '100%',
}) => {
  // Find selected location for recentering
  const selectedLoc = useMemo(
    () => locations.find((l) => (l.id || l.location_id) === selectedLocationId),
    [locations, selectedLocationId]
  );

  return (
    <div style={{ height, width: '100%' }} className="relative z-0">
      <MapContainer
        center={INDIA_CENTER}
        zoom={5}
        scrollWheelZoom
        style={{ height: '100%', width: '100%' }}
        maxBounds={undefined}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Fit to India bounds on mount */}
        <FitIndia />

        {/* Re-center when selected location changes */}
        {selectedLoc && (
          <RecenterMap lat={selectedLoc.latitude} lon={selectedLoc.longitude} />
        )}

        {/* Marker clusters */}
        <MarkerClusterGroup
          chunkedLoading
          iconCreateFunction={createClusterIcon}
          maxClusterRadius={40}
          spiderfyOnMaxZoom
          showCoverageOnHover={false}
          removeOutsideVisibleBounds
        >
          {locations.map((loc) => {
            const locId = loc.id || loc.location_id || '';
            const isSelected = locId === selectedLocationId;
            const cat = normalizeCategory(loc);
            const color = getRiskColor(cat);
            const prob = loc.landslideProbability ?? loc.risk_probability ?? 0;
            const radius = isSelected ? 11 : cat === 'HIGH RISK' ? 8 : 6;

            return (
              <React.Fragment key={locId}>
                {/* Selection halo */}
                {isSelected && (
                  <Circle
                    center={[loc.latitude, loc.longitude]}
                    radius={800}
                    pathOptions={{
                      color,
                      fillColor: color,
                      fillOpacity: 0.15,
                      weight: 2,
                      dashArray: '4 4',
                    }}
                  />
                )}

                <CircleMarker
                  center={[loc.latitude, loc.longitude]}
                  radius={radius}
                  eventHandlers={{
                    click: () => { if (onSelectLocation) onSelectLocation(locId); },
                  }}
                  pathOptions={{
                    color: isSelected ? '#0f172a' : color,
                    fillColor: color,
                    fillOpacity: 0.92,
                    weight: isSelected ? 2.5 : 1.5,
                  }}
                  ref={(r) => {
                    if (r && isSelected) {
                      // Small timeout to let map animation start
                      setTimeout(() => {
                        try { r.openPopup(); } catch(e){}
                      }, 100);
                    }
                  }}
                >
                  <Popup minWidth={240} maxWidth={280}>
                    <div className="p-1 space-y-2">
                      {/* Header */}
                      <div className="border-b border-slate-200 pb-1.5">
                        <div className="font-black text-slate-900 text-sm leading-snug">
                          📍 {loc.name || loc.place_name}
                        </div>
                        <div className="text-[10px] text-slate-500 font-medium mt-0.5">
                          {[loc.district, loc.stateOrRegion].filter(Boolean).join(', ')}
                        </div>
                        <div className="text-[10px] font-bold text-slate-600">India</div>
                      </div>

                      {/* Handle LIVE Assessment Missing Data explicitly */}
                      {((loc.data_coverage_status as string) === 'INSUFFICIENT DATA' || (loc.data_coverage_status as string) === 'DATA RETRIEVAL ERROR') ? (
                        <div className="py-2 text-center border border-red-200 bg-red-50 rounded mt-2 px-2">
                          <div className="text-xs font-bold text-red-700 uppercase">Status:</div>
                          <div className="text-sm font-black text-red-800 uppercase my-1">{loc.data_coverage_status}</div>
                          <p className="text-[9px] text-red-600 mt-2 font-medium">
                            {loc.explanation || "Risk assessment unavailable for this location because sufficient environmental or historical data are not available."}
                          </p>
                          {loc.missing_fields && loc.missing_fields.length > 0 && (
                            <p className="text-[8px] text-red-500 mt-2 italic">Missing fields required by ML model.</p>
                          )}
                        </div>
                      ) : ((loc.data_coverage_status as string) !== 'VERIFIED_DATA' && (loc.data_coverage_status as string) !== 'VALIDATED_DATA_AVAILABLE' && (loc.data_coverage_status as string) !== 'DATASET_RECORD' && (loc.data_coverage_status as string) !== 'VALIDATED MODEL ASSESSMENT' && (loc.data_coverage_status as string) !== 'PRELIMINARY ENVIRONMENTAL ASSESSMENT') ? (
                        <div className="py-2 text-center">
                          <div className="text-xs font-bold text-slate-500 uppercase">Status:</div>
                          <div className="text-sm font-black text-slate-700 uppercase my-1">DATA UNAVAILABLE</div>
                          <p className="text-[9px] text-slate-500 mt-2">
                            No verified Phase 1–8 assessment is currently available for this location.
                          </p>
                        </div>
                      ) : (
                        <>
                          {/* Warning state */}
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-600 font-semibold">Warning State:</span>
                            <span
                              className="px-2 py-0.5 rounded text-[10px] font-black uppercase"
                              style={{ background: color, color: '#fff' }}
                            >
                              {cat}
                            </span>
                          </div>

                          {/* Risk probability */}
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-600 font-semibold">Risk Probability:</span>
                            <span className="font-extrabold text-slate-900">{(prob * 100).toFixed(1)}%</span>
                          </div>

                          {/* Trend */}
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-600 font-semibold">Risk Trend:</span>
                            <span className="font-bold text-slate-800">{trendLabel(loc.risk_trend)}</span>
                          </div>

                          {/* Rainfall */}
                          {(loc.rainfall7d ?? 0) > 0 && (
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-600 font-semibold">Rainfall (7d):</span>
                              <span className="font-bold text-slate-700">{loc.rainfall7d} mm</span>
                            </div>
                          )}

                          {/* Soil moisture */}
                          {(loc.soilMoisture ?? 0) > 0 && (
                            <div className="flex items-center justify-between text-xs">
                              <span className="text-slate-600 font-semibold">Soil Moisture:</span>
                              <span className="font-bold text-slate-700">{loc.soilMoisture?.toFixed(1)}%</span>
                            </div>
                          )}

                          {/* Assessment */}
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-600 font-semibold">Assessment:</span>
                            <span className="text-[10px] font-bold text-emerald-700">MODEL ASSESSMENT</span>
                          </div>

                          {/* Coverage */}
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-slate-600 font-semibold">Data Coverage:</span>
                            <span className={`text-[10px] font-bold ${
                              (loc.data_coverage_status as string) === 'PRELIMINARY ENVIRONMENTAL ASSESSMENT' ? 'text-orange-600 text-[8px] text-right max-w-[120px]' : 'text-slate-600'
                            }`}>
                              {(loc.data_coverage_status as string) === 'PRELIMINARY ENVIRONMENTAL ASSESSMENT' 
                                ? 'PRELIMINARY / OUTSIDE VALIDATED AREA' 
                                : loc.data_coverage_status || 'VERIFIED DATA'}
                            </span>
                          </div>
                          
                          {loc.explanation && (loc.data_coverage_status as string) !== 'INSUFFICIENT DATA' && (
                            <div className="text-[8.5px] text-slate-500 italic mt-2 leading-tight bg-slate-50 p-1 rounded">
                              {loc.explanation}
                            </div>
                          )}

                          {/* Last updated */}
                          <div className="text-[9px] text-slate-400 border-t border-slate-100 pt-1.5">
                            Last Observation: {loc.lastUpdated || loc.latest_timestamp || 'N/A'}
                          </div>
                        </>
                      )}

                      {/* Technical Details */}
                      <details className="mt-2 text-[9px] text-slate-500">
                        <summary className="cursor-pointer hover:text-slate-700 font-semibold">Technical Details</summary>
                        <div className="mt-1 pl-2 border-l-2 border-slate-200">
                          <div>ID: <span className="font-mono">{loc.id || loc.location_id}</span></div>
                          <div className="font-mono mt-0.5">
                            {loc.latitude.toFixed(4)}°N, {loc.longitude.toFixed(4)}°E
                          </div>
                        </div>
                      </details>

                      {/* Select button */}
                      {onSelectLocation && (
                        <button
                          type="button"
                          onClick={() => onSelectLocation(locId)}
                          className="w-full py-1.5 text-xs font-bold bg-emerald-600 hover:bg-emerald-700 text-white rounded transition mt-2"
                        >
                          View Location Details →
                        </button>
                      )}
                    </div>
                  </Popup>
                </CircleMarker>
              </React.Fragment>
            );
          })}
        </MarkerClusterGroup>
      </MapContainer>
    </div>
  );
};
