import React, { useState } from 'react';
import { ChevronDown, ChevronUp, MapPin } from 'lucide-react';

interface LocationIdentityProps {
  placeName: string;
  district?: string;
  region?: string;
  country: string;
  latitude: number;
  longitude: number;
  locationId: string;
  size?: 'sm' | 'md' | 'lg';
}

export const LocationIdentity: React.FC<LocationIdentityProps> = ({
  placeName,
  district,
  region,
  country,
  latitude,
  longitude,
  locationId,
  size = 'md',
}) => {
  const [showTechId, setShowTechId] = useState<boolean>(false);

  const regionHierarchy = [district, region, country].filter(Boolean).join(', ');

  const titleSizes = {
    sm: 'text-sm font-bold text-slate-900',
    md: 'text-base font-extrabold text-slate-900',
    lg: 'text-2xl font-black text-slate-900',
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center gap-2">
        <MapPin className="w-5 h-5 text-emerald-600 shrink-0" />
        <h2 className={titleSizes[size]}>📍 {placeName}</h2>
      </div>

      <p className="text-xs text-slate-600 font-semibold pl-7">
        {regionHierarchy}
      </p>

      <div className="text-[11px] text-slate-500 font-medium pl-7 flex items-center gap-3 pt-0.5">
        <span>Coordinates: {latitude.toFixed(4)}°, {longitude.toFixed(4)}°</span>
        <button
          type="button"
          onClick={() => setShowTechId(!showTechId)}
          className="text-slate-400 hover:text-slate-600 transition flex items-center gap-1 font-mono"
        >
          {showTechId ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          {showTechId ? 'Hide Technical ID' : 'Technical ID'}
        </button>
      </div>

      {showTechId && (
        <div className="pl-7 pt-1">
          <span className="inline-block px-2 py-0.5 bg-slate-100 border border-slate-200 rounded text-[10px] font-mono text-slate-600">
            Technical ID: {locationId}
          </span>
        </div>
      )}
    </div>
  );
};
