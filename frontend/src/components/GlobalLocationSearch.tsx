import React, { useEffect, useState, useRef } from 'react';
import { Search, AlertCircle, X, Loader2 } from 'lucide-react';
import { useLocation } from '../context/LocationContext';
import type { ComprehensiveLocationData } from '../types';
import { WarningBadge } from './WarningBadge';
import { api } from '../services/api';

interface GlobalLocationSearchProps {
  onSelectLocation?: (locationId: string) => void;
  placeholder?: string;
}

export const GlobalLocationSearch: React.FC<GlobalLocationSearchProps> = ({
  onSelectLocation,
  placeholder = 'Search globally by City, District, State/Region, Country (e.g. Coimbatore, Chennai)...',
}) => {
  const { locations, selectLocation, addLocation } = useLocation();
  const [query, setQuery] = useState<string>('');
  
  // Results can be local or live suggestions
  const [results, setResults] = useState<any[]>([]);
  const [isOpen, setIsOpen] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const trimmed = query.trim().toLowerCase();
    if (!trimmed) {
      setResults([]);
      setIsOpen(false);
      setError(null);
      return;
    }

    const timer = setTimeout(async () => {
      // Fetch global suggestions
      try {
        const liveSuggestions = await api.autocompleteGlobalLocation(trimmed);
        
        if (liveSuggestions && liveSuggestions.length > 0) {
          setResults(liveSuggestions.map(s => ({ ...s, isLiveSuggestion: true })));
          setIsOpen(true);
        } else {
          // Fallback to local filtering
          const filtered = locations.filter((l) => {
            const locId = l.id || l.location_id || '';
            const name = l.name || l.place_name || '';
            const district = l.district || '';
            const state = l.stateOrRegion || l.region || '';
            const combined = `${name} ${district} ${state} ${locId}`.toLowerCase();
            return combined.includes(trimmed);
          });
          setResults(filtered.slice(0, 15).map(f => ({ ...f, isLiveSuggestion: false })));
          setIsOpen(true);
        }
      } catch (e) {
        // Fallback to local
        const filtered = locations.filter((l) => (l.name || l.place_name || '').toLowerCase().includes(trimmed));
        setResults(filtered.slice(0, 15).map(f => ({ ...f, isLiveSuggestion: false })));
        setIsOpen(true);
      }
    }, 400); // 400ms debounce

    return () => clearTimeout(timer);
  }, [query, locations]);

  // Click outside to close
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelect = (locId: string) => {
    setIsOpen(false);
    setQuery('');
    setError(null);
    selectLocation(locId);
    if (onSelectLocation) {
      onSelectLocation(locId);
    }
  };

  const handleGlobalSearch = async (explicitQuery?: string, explicitLat?: number, explicitLon?: number) => {
    const searchQuery = explicitQuery || query;
    if (!searchQuery.trim()) return;
    setLoading(true);
    setError(null);
    setIsOpen(false);
    setQuery(searchQuery);
    
    try {
      // Pass the exact coordinates if we got them from autocomplete
      const res = await api.assessGlobalLocation(searchQuery, explicitLat, explicitLon);
      
      const customLocId = 'live_' + Date.now();
      const customLoc: ComprehensiveLocationData = {
        ...res,
        id: customLocId,
        location_id: customLocId,
        place_name: res.location_name,
        name: res.location_name,
        stateOrRegion: res.region,
        landslideProbability: res.risk_probability || 0,
        riskCategory: res.risk_category || res.warning_state || 'NORMAL',
        current_warning_state: res.warning_state || 'NORMAL',
        rainfall: res.rainfall || 0,
        rainfall24h: res.rainfall || 0,
        rainfall7d: res.rainfall7d || 0,
        soilMoisture: res.soil_moisture || 0,
        slope: 0,
        elevation: 0,
        temperature: 0,
        confidence: 0,
        highRiskCount: 0,
        warningCount: 0,
        watchCount: 0,
        historicalLandslides: 0,
        recentEscalations: 0,
        baselineStatus: 'LIVE_ASSESSMENT',
        contributingFactors: [],
        lastUpdated: res.data_timestamp || new Date().toISOString(),
        riskScore: res.risk_probability || 0,
        data_coverage_status: res.coverage_status
      };

      addLocation(customLoc);
      handleSelect(customLocId);
    } catch (err: any) {
      setError(err.message || 'Failed to assess location');
      setIsOpen(true);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setIsOpen(false);
    } else if (e.key === 'Enter') {
      if (results.length > 0 && !error) {
        const first = results[0];
        if (first.isLiveSuggestion) {
          handleGlobalSearch(first.display_name, first.latitude, first.longitude);
        } else {
          handleSelect(first.id || first.location_id || '');
        }
      } else {
        handleGlobalSearch();
      }
    }
  };

  return (
    <div ref={containerRef} className="relative w-full max-w-xl z-30">
      <div className="relative flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={query}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              if (query.trim()) setIsOpen(true);
            }}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={placeholder}
            className="w-full pl-10 pr-8 py-2.5 bg-white border border-slate-300 rounded-xl text-sm font-medium text-slate-900 placeholder:text-slate-400 focus:ring-2 focus:ring-emerald-500 focus:outline-none shadow-sm transition"
          />
          {query && (
            <button 
              type="button" 
              onClick={() => { setQuery(''); setResults([]); setError(null); }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <button 
          type="button"
          onClick={() => handleGlobalSearch()}
          disabled={loading || !query.trim()}
          className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-300 text-white rounded-xl text-sm font-bold shadow-sm transition flex items-center gap-2 shrink-0"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : 'Assess Location'}
        </button>
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-slate-200 overflow-hidden max-h-80 overflow-y-auto">
          {error ? (
            <div className="p-4 text-xs text-red-500 text-center space-y-1">
              <AlertCircle className="w-5 h-5 mx-auto text-red-500" />
              <div className="font-bold">{error}</div>
            </div>
          ) : results.length === 0 ? (
            <div className="p-4 text-xs text-slate-500 text-center space-y-1">
              <AlertCircle className="w-5 h-5 mx-auto text-amber-500" />
              <div className="font-bold text-slate-700">No matching evaluated location found for "{query}"</div>
              <p className="text-[11px] text-slate-400">
                Click "Assess Location" or press Enter to run a live global assessment.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-slate-100">
              <div className="p-2 text-[10px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50 border-b border-slate-100">
                {results[0]?.isLiveSuggestion ? 'Global Place Suggestions' : 'Local Verified Results'}
              </div>
              {results.map((item) => {
                if (item.isLiveSuggestion) {
                  return (
                    <button
                      key={item.id || item.place_name}
                      type="button"
                      onClick={() => handleGlobalSearch(item.display_name, item.latitude, item.longitude)}
                      className="w-full p-3 text-left hover:bg-slate-50 transition flex items-center justify-between group"
                    >
                      <div className="space-y-0.5 min-w-0 pr-2">
                        <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-600 transition truncate">
                          📍 {item.place_name || item.display_name.split(',')[0]}
                        </div>
                        <div className="text-[11px] text-slate-500 truncate">
                          {item.display_name}
                        </div>
                      </div>
                      <div className="flex flex-col items-end gap-1 shrink-0">
                        <span className="text-[10px] font-bold text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                          Search
                        </span>
                      </div>
                    </button>
                  );
                }

                const itemId = item.id || item.location_id || '';
                const prob = item.landslideProbability ?? item.risk_probability ?? 0;
                return (
                  <button
                    key={itemId}
                    type="button"
                    onClick={() => handleSelect(itemId)}
                    className="w-full p-3 text-left hover:bg-slate-50 transition flex items-center justify-between group"
                  >
                    <div className="space-y-0.5 min-w-0 pr-2">
                      <div className="font-bold text-xs text-slate-900 group-hover:text-emerald-600 transition truncate">
                        📍 {item.name || item.place_name}
                      </div>
                      <div className="text-[11px] text-slate-500 truncate">
                        {[item.district, item.stateOrRegion || item.region, item.country].filter(Boolean).join(', ')}
                      </div>
                    </div>
                    <div className="flex flex-col items-end gap-1 shrink-0">
                      <WarningBadge state={item.current_warning_state || (item.riskCategory as any)} size="sm" />
                      <span className="text-[10px] font-extrabold text-slate-700">
                        P(L): {(prob * 100).toFixed(1)}%
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
