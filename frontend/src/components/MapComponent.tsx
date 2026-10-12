import React, { useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import type { ComprehensiveLocationData } from '../types';
import { WarningBadge } from './WarningBadge';
import { getRiskColor, normalizeRiskCategory } from '../utils/riskThresholds';

interface MapComponentProps {
  locations: ComprehensiveLocationData[];
  selectedLocationId?: string;
  onSelectLocation?: (locationId: string) => void;
  height?: string;
}

// Helper component that pans and zooms the Leaflet map when the selected location changes
const RecenterMap: React.FC<{ lat: number; lon: number }> = ({ lat, lon }) => {
  const map = useMap();
  useEffect(() => {
    if (lat !== undefined && lon !== undefined && !isNaN(lat) && !isNaN(lon)) {
      map.flyTo([lat, lon], 7, { duration: 1.2 });
    }
  }, [lat, lon, map]);
  return null;
};

export const MapComponent: React.FC<MapComponentProps> = ({
  locations,
  selectedLocationId,
  onSelectLocation,
  height = '500px',
}) => {
  const activeLoc = locations.find((l) => (l.id || l.location_id) === selectedLocationId) || locations[0];
  const centerLat = activeLoc ? activeLoc.latitude : 15.0;
  const centerLon = activeLoc ? activeLoc.longitude : 77.0;

  return (
    <div style={{ height, width: '100%' }} className="rounded-xl overflow-hidden shadow-sm border border-slate-200 relative z-0">
      <MapContainer
        center={[centerLat, centerLon]}
        zoom={5}
        scrollWheelZoom={true}
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Dynamic map re-centering */}
        {activeLoc && <RecenterMap lat={activeLoc.latitude} lon={activeLoc.longitude} />}

        {locations.map((loc) => {
          const locId = loc.id || loc.location_id || '';
          const isSelected = locId === selectedLocationId;
          const riskCat = loc.riskCategory || normalizeRiskCategory(loc.current_warning_state);
          const color = getRiskColor(riskCat);
          const prob = loc.landslideProbability ?? loc.risk_probability ?? 0;

          return (
            <React.Fragment key={locId}>
              {/* Outer halo for selected marker */}
              {isSelected && (
                <CircleMarker
                  center={[loc.latitude, loc.longitude]}
                  radius={16}
                  pathOptions={{
                    color: color,
                    fillColor: color,
                    fillOpacity: 0.25,
                    weight: 2,
                    dashArray: '3, 3',
                  }}
                />
              )}

              {/* Core location marker */}
              <CircleMarker
                center={[loc.latitude, loc.longitude]}
                radius={isSelected ? 10 : 7}
                eventHandlers={{
                  click: () => {
                    if (onSelectLocation) onSelectLocation(locId);
                  },
                }}
                pathOptions={{
                  color: isSelected ? '#0f172a' : color,
                  fillColor: color,
                  fillOpacity: 0.9,
                  weight: isSelected ? 3 : 1.5,
                }}
              >
                <Popup>
                  <div className="p-2 space-y-2 min-w-[220px]">
                    <div className="border-b pb-1">
                      <div className="font-bold text-slate-900 text-sm">📍 {loc.name || loc.place_name}</div>
                      <div className="text-[10px] text-slate-500 font-medium">
                        {[loc.district, loc.stateOrRegion || loc.region, loc.country].filter(Boolean).join(', ')}
                      </div>
                      <div className="text-[9px] font-mono text-slate-400">
                        {loc.latitude.toFixed(4)}°, {loc.longitude.toFixed(4)}°
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-semibold">Risk Category:</span>
                      <WarningBadge state={loc.current_warning_state || (riskCat as any)} size="sm" />
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-semibold">Probability P(L):</span>
                      <span className="font-extrabold text-slate-900">{(prob * 100).toFixed(1)}%</span>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-semibold">Rainfall (7d):</span>
                      <span className="font-bold text-slate-700">{loc.rainfall7d} mm</span>
                    </div>

                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-500 font-semibold">Slope / Elev:</span>
                      <span className="font-bold text-slate-700">{loc.slope}° / {loc.elevation}m</span>
                    </div>

                    {onSelectLocation && !isSelected && (
                      <button
                        type="button"
                        onClick={() => onSelectLocation(locId)}
                        className="w-full mt-2 py-1.5 px-2 bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold rounded transition shadow-sm"
                      >
                        Select This Location &rarr;
                      </button>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            </React.Fragment>
          );
        })}
      </MapContainer>
    </div>
  );
};
