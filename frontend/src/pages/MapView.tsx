import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import {
  AlertTriangle,
  Compass,
  Filter,
  Info,
  Layers,
  MapPin,
  Search,
  Shield,
  X,
} from 'lucide-react';
import { api } from '../services/api';
import type { ComprehensiveLocationData } from '../types';
import { IndiaMapComponent } from '../components/IndiaMapComponent';
import { WarningBadge } from '../components/WarningBadge';

// ─── India states (all states + UTs) ─────────────────────────────────────────
const INDIA_STATES = [
  'Andaman & Nicobar Islands',
  'Andhra Pradesh',
  'Arunachal Pradesh',
  'Assam',
  'Bihar',
  'Chandigarh',
  'Chhattisgarh',
  'Dadra & Nagar Haveli',
  'Daman & Diu',
  'Delhi',
  'Goa',
  'Gujarat',
  'Haryana',
  'Himachal Pradesh',
  'Jammu & Kashmir',
  'Jharkhand',
  'Karnataka',
  'Kerala',
  'Ladakh',
  'Lakshadweep',
  'Madhya Pradesh',
  'Maharashtra',
  'Manipur',
  'Meghalaya',
  'Mizoram',
  'Nagaland',
  'Odisha',
  'Puducherry',
  'Punjab',
  'Rajasthan',
  'Sikkim',
  'Tamil Nadu',
  'Telangana',
  'Tripura',
  'Uttar Pradesh',
  'Uttarakhand',
  'West Bengal',
];

// ─── Risk colour helpers ───────────────────────────────────────────────────────
function trendIcon(trend: string) {
  if (trend === 'INCREASING') return '↑';
  if (trend === 'DECREASING') return '↓';
  return '→';
}

// ─── Types ────────────────────────────────────────────────────────────────────
interface IndiaStats {
  total_locations: number;
  verified_assessments: number;
  high_risk_count: number;
  warning_count: number;
  watch_count: number;
  low_count: number;
  data_unavailable: number;
  by_state: Record<string, number>;
  coverage_note: string;
}

// ─── Main page ────────────────────────────────────────────────────────────────
export const MapPage: React.FC = () => {
  const [allLocations, setAllLocations] = useState<ComprehensiveLocationData[]>([]);
  const [stats, setStats] = useState<IndiaStats | null>(null);
  const [hierarchy, setHierarchy] = useState<Record<string, string[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [filterState, setFilterState] = useState('ALL');
  const [filterDistrict, setFilterDistrict] = useState('ALL');
  const [filterWarning, setFilterWarning] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<ComprehensiveLocationData[]>([]);
  const [showSearch, setShowSearch] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);

  // Selected location for map
  const [selectedLocId, setSelectedLocId] = useState<string>('');

  // Side panel
  const [sidePanel, setSidePanel] = useState<'high-risk' | 'warning' | null>('high-risk');

  // ── Load data ──────────────────────────────────────────────────────────────
  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true);
        const [locs, statsData, hierData] = await Promise.allSettled([
          api.getIndiaLocations(),
          api.getIndiaStats(),
          api.getIndiaHierarchy(),
        ]);

        if (locs.status === 'fulfilled') setAllLocations(locs.value);
        if (statsData.status === 'fulfilled') setStats(statsData.value);
        if (hierData.status === 'fulfilled') {
          // Build state → districts map
          const h: Record<string, string[]> = {};
          Object.entries(hierData.value.states || {}).forEach(([state, data]) => {
            h[state] = Object.keys((data as any).districts || {}).sort();
          });
          setHierarchy(h);
        }
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // ── Search ─────────────────────────────────────────────────────────────────
  const handleGlobalSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    setShowSearch(false);
    try {
      const res = await api.assessGlobalLocation(searchQuery);
      
      // We assign it a unique ID so it doesn't conflict
      const customLocId = 'live_' + Date.now();
      const customLoc: ComprehensiveLocationData = {
        ...res,
        id: customLocId,
        location_id: customLocId,
        place_name: res.location_name,
        name: res.location_name,
        stateOrRegion: res.region,
        landslideProbability: res.risk_probability,
        riskCategory: res.risk_category || res.warning_state,
        current_warning_state: res.warning_state,
        rainfall24h: res.rainfall,
        lastUpdated: res.data_timestamp,
        riskScore: res.risk_probability,
        data_coverage_status: res.coverage_status
      };

      // Clear any previous live_ search results to prevent stale data
      setAllLocations(prev => [customLoc, ...prev.filter(l => !(l.id || '').toString().startsWith('live_'))]);
      setSelectedLocId(customLocId);
      setSearchQuery('');
    } catch (err: any) {
      setError(err.message || 'Failed to assess global location');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!searchQuery.trim()) { setSearchResults([]); return; }
    const q = searchQuery.toLowerCase();
    const results = allLocations.filter((l) => {
      const txt = `${l.name} ${l.place_name} ${l.district} ${l.stateOrRegion} ${l.country} ${l.id} ${l.latitude} ${l.longitude}`.toLowerCase();
      return txt.includes(q);
    }).slice(0, 15);
    setSearchResults(results);
  }, [searchQuery, allLocations]);

  // Close search on outside click
  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(e.target as Node)) {
        setShowSearch(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ── Available districts from selected state ────────────────────────────────
  const availableDistricts = useMemo(() => {
    if (filterState === 'ALL') return [];
    return hierarchy[filterState] || [];
  }, [filterState, hierarchy]);

  // ── Filtered locations for map ─────────────────────────────────────────────
  const filteredLocations = useMemo(() => {
    return allLocations.filter((loc) => {
      const matchState = filterState === 'ALL' || str(loc.stateOrRegion).toLowerCase().includes(filterState.toLowerCase());
      const matchDistrict = filterDistrict === 'ALL' || str(loc.district).toLowerCase().includes(filterDistrict.toLowerCase());
      const matchWarning = filterWarning === 'ALL' || loc.current_warning_state === filterWarning;
      return matchState && matchDistrict && matchWarning;
    });
  }, [allLocations, filterState, filterDistrict, filterWarning]);

  // ── High-risk & warning locations ──────────────────────────────────────────
  const highRiskLocs = useMemo(
    () => allLocations.filter((l) => l.current_warning_state === 'HIGH_RISK' || l.riskCategory === 'HIGH RISK')
          .sort((a, b) => (b.risk_probability ?? 0) - (a.risk_probability ?? 0)),
    [allLocations]
  );
  const warningLocs = useMemo(
    () => allLocations.filter((l) => l.current_warning_state === 'WARNING' || l.riskCategory === 'WARNING')
          .sort((a, b) => (b.risk_probability ?? 0) - (a.risk_probability ?? 0)),
    [allLocations]
  );

  const handleSelectLocation = useCallback((id: string) => {
    setSelectedLocId(id);
    setShowSearch(false);
    setSearchQuery('');
  }, []);

  const handleStateChange = (s: string) => {
    setFilterState(s);
    setFilterDistrict('ALL');
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* ── Left side panel ──────────────────────────────────────────────── */}
      <div className="w-80 bg-slate-900 text-white flex flex-col shrink-0 border-r border-slate-700 overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-700">
          <div className="flex items-center gap-2 mb-1">
            <Compass className="w-5 h-5 text-emerald-400" />
            <h1 className="text-sm font-black tracking-wide">India Hazard Map</h1>
          </div>
          <p className="text-[10px] text-slate-400 font-medium leading-snug">
            India — Verified Project Coverage<br />
            NASA GLC + ERA5 Environmental Data
          </p>
        </div>

        {/* Coverage stats */}
        {stats && (
          <div className="p-3 border-b border-slate-700 space-y-2">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Coverage Summary</div>
            <div className="grid grid-cols-2 gap-1.5">
              <div className="bg-slate-800 rounded-lg p-2 text-center col-span-2 flex justify-between items-center px-4">
                <div className="text-[9px] text-slate-400 font-bold uppercase text-left">Total Verified Locations</div>
                <div className="text-lg font-black text-emerald-400">{stats.verified_assessments.toLocaleString()}</div>
              </div>
              <div className="bg-red-950/80 rounded-lg p-2 text-center border border-red-800">
                <div className="text-lg font-black text-red-400">{stats.high_risk_count}</div>
                <div className="text-[9px] text-red-400 font-bold uppercase">High Risk</div>
              </div>
              <div className="bg-orange-950/80 rounded-lg p-2 text-center border border-orange-800">
                <div className="text-lg font-black text-orange-400">{stats.warning_count}</div>
                <div className="text-[9px] text-orange-400 font-bold uppercase">Warning</div>
              </div>
              <div className="bg-yellow-950/80 rounded-lg p-2 text-center border border-yellow-800">
                <div className="text-lg font-black text-yellow-400">{stats.watch_count}</div>
                <div className="text-[9px] text-yellow-400 font-bold uppercase">Watch</div>
              </div>
              <div className="bg-emerald-950/80 rounded-lg p-2 text-center border border-emerald-800">
                <div className="text-lg font-black text-emerald-400">{stats.low_count}</div>
                <div className="text-[9px] text-emerald-400 font-bold uppercase">Normal</div>
              </div>
              <div className="bg-slate-800 rounded-lg p-2 text-center border border-slate-600 col-span-2 flex justify-between items-center px-4">
                <div className="text-[9px] text-slate-400 font-bold uppercase text-left">Data Unavailable</div>
                <div className="text-lg font-black text-slate-400">{stats.data_unavailable}</div>
              </div>
            </div>
          </div>
        )}

        {/* Panel toggle */}
        <div className="flex border-b border-slate-700">
          <button
            type="button"
            onClick={() => setSidePanel(sidePanel === 'high-risk' ? null : 'high-risk')}
            className={`flex-1 py-2 text-[10px] font-bold uppercase tracking-wide transition ${
              sidePanel === 'high-risk' ? 'bg-red-900/60 text-red-300 border-b-2 border-red-500' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <AlertTriangle className="w-3 h-3 inline mr-1" />
            High Risk ({highRiskLocs.length})
          </button>
          <button
            type="button"
            onClick={() => setSidePanel(sidePanel === 'warning' ? null : 'warning')}
            className={`flex-1 py-2 text-[10px] font-bold uppercase tracking-wide transition ${
              sidePanel === 'warning' ? 'bg-orange-900/60 text-orange-300 border-b-2 border-orange-500' : 'text-slate-400 hover:text-white hover:bg-slate-800'
            }`}
          >
            <Shield className="w-3 h-3 inline mr-1" />
            Warning ({warningLocs.length})
          </button>
        </div>

        {/* Location list */}
        <div className="flex-1 overflow-y-auto">
          {sidePanel === 'high-risk' && (
            <div className="p-3 space-y-2">
              <div className="text-[9px] text-red-400 font-bold uppercase tracking-widest flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-red-500 rounded-full animate-pulse" />
                Current High-Risk Locations
              </div>
              {highRiskLocs.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">No high-risk locations in current dataset</p>
              ) : (
                highRiskLocs.slice(0, 30).map((loc) => {
                  const id = loc.id || loc.location_id || '';
                  const prob = loc.landslideProbability ?? loc.risk_probability ?? 0;
                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => handleSelectLocation(id)}
                      className={`w-full text-left p-2.5 rounded-lg border transition-all ${
                        selectedLocId === id
                          ? 'bg-red-900/80 border-red-500'
                          : 'bg-slate-800 border-slate-700 hover:bg-red-900/40 hover:border-red-700'
                      }`}
                    >
                      <div className="text-xs font-bold text-white truncate flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-red-400 shrink-0" />
                        {loc.name || loc.place_name}
                      </div>
                      <div className="text-[9px] text-slate-400 truncate mt-0.5">
                        {[loc.district, loc.stateOrRegion, 'India'].filter(Boolean).join(', ')}
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-[9px] bg-red-700 text-red-100 px-1.5 py-0.5 rounded font-bold">HIGH RISK</span>
                        <span className="text-[10px] font-extrabold text-red-300">{(prob * 100).toFixed(0)}%</span>
                        <span className="text-[9px] text-slate-400">{trendIcon(loc.risk_trend || 'STABLE')}</span>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          )}

          {sidePanel === 'warning' && (
            <div className="p-3 space-y-2">
              <div className="text-[9px] text-orange-400 font-bold uppercase tracking-widest flex items-center gap-1">
                <span className="w-1.5 h-1.5 bg-orange-500 rounded-full animate-pulse" />
                Active Warning Locations
              </div>
              {warningLocs.length === 0 ? (
                <p className="text-xs text-slate-500 text-center py-4">No active warning locations</p>
              ) : (
                warningLocs.slice(0, 30).map((loc) => {
                  const id = loc.id || loc.location_id || '';
                  const prob = loc.landslideProbability ?? loc.risk_probability ?? 0;
                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => handleSelectLocation(id)}
                      className={`w-full text-left p-2.5 rounded-lg border transition-all ${
                        selectedLocId === id
                          ? 'bg-orange-900/80 border-orange-500'
                          : 'bg-slate-800 border-slate-700 hover:bg-orange-900/40 hover:border-orange-700'
                      }`}
                    >
                      <div className="text-xs font-bold text-white truncate flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-orange-400 shrink-0" />
                        {loc.name || loc.place_name}
                      </div>
                      <div className="text-[9px] text-slate-400 truncate mt-0.5">
                        {[loc.district, loc.stateOrRegion, 'India'].filter(Boolean).join(', ')}
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <span className="text-[9px] bg-orange-700 text-orange-100 px-1.5 py-0.5 rounded font-bold">WARNING</span>
                        <span className="text-[10px] font-extrabold text-orange-300">{(prob * 100).toFixed(0)}%</span>
                        <span className="text-[9px] text-slate-400">{trendIcon(loc.risk_trend || 'STABLE')}</span>
                      </div>
                    </button>
                  );
                })
              )}
            </div>
          )}

          {sidePanel === null && (
            <div className="p-4 text-center text-xs text-slate-500 mt-4">
              Select a panel above to view locations
            </div>
          )}
        </div>

        {/* Legend */}
        <div className="p-3 border-t border-slate-700 bg-slate-950">
          <div className="text-[9px] text-slate-400 font-bold uppercase tracking-widest mb-2">Map Legend</div>
          <div className="space-y-1">
            {[
              { color: 'bg-red-500', label: 'VERIFIED HIGH RISK (≥75%)' },
              { color: 'bg-orange-500', label: 'VERIFIED WARNING (50–75%)' },
              { color: 'bg-yellow-400', label: 'VERIFIED WATCH (25–50%)' },
              { color: 'bg-emerald-500', label: 'VERIFIED NORMAL (<25%)' },
              { color: 'bg-slate-500', label: 'DATA UNAVAILABLE' },
            ].map(({ color, label }) => (
              <div key={label} className="flex items-center gap-2 text-[10px] text-slate-300">
                <span className={`w-2.5 h-2.5 rounded-full ${color} shrink-0`} />
                {label}
              </div>
            ))}
          </div>
          <p className="text-[8.5px] text-slate-400 mt-3 leading-tight italic border-t border-slate-800 pt-2">
            Risk assessments shown on this map are derived only from verified project outputs. Locations without verified assessment data are explicitly marked as Data Unavailable. Data unavailable does NOT mean low risk.
          </p>
        </div>
      </div>

      {/* ── Main map area ─────────────────────────────────────────────────── */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Toolbar */}
        <div className="bg-white border-b border-slate-200 px-4 py-2.5 flex items-center gap-3 shrink-0 shadow-sm">
          {/* Search */}
          <div ref={searchRef} className="relative w-96 flex gap-2">
            <div className="relative flex-1">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search global location (e.g. Ernakulam, Kerala)..."
                value={searchQuery}
                onChange={(e) => { setSearchQuery(e.target.value); setShowSearch(true); }}
                onFocus={() => setShowSearch(true)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && searchQuery.trim()) {
                    handleGlobalSearch();
                  }
                }}
                className="w-full pl-8 pr-3 py-1.5 text-xs bg-slate-50 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-400"
              />
              {searchQuery && (
                <button type="button" onClick={() => { setSearchQuery(''); setSearchResults([]); }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600">
                  <X className="w-3 h-3" />
                </button>
              )}
            </div>
            <button 
              type="button" 
              onClick={handleGlobalSearch}
              disabled={loading || !searchQuery.trim()}
              className="bg-emerald-600 hover:bg-emerald-700 disabled:bg-emerald-300 text-white px-3 py-1.5 rounded-lg text-xs font-bold transition flex items-center gap-1 shrink-0"
            >
              {loading ? <span className="animate-pulse">Assessing...</span> : 'Assess Location'}
            </button>
            
            {showSearch && searchResults.length > 0 && (
              <div className="absolute top-full left-0 right-0 mt-1 bg-white border border-slate-200 rounded-xl shadow-xl z-50 max-h-72 overflow-y-auto">
                <div className="p-2 text-[9px] font-bold text-slate-400 uppercase tracking-wider bg-slate-50 border-b border-slate-100">Local Verified Results</div>
                {searchResults.map((loc) => {
                  const id = loc.id || loc.location_id || '';
                  const prob = loc.landslideProbability ?? loc.risk_probability ?? 0;
                  const cat = loc.riskCategory || loc.current_warning_state || 'LOW';
                  return (
                    <button
                      key={id}
                      type="button"
                      onClick={() => handleSelectLocation(id)}
                      className="w-full text-left px-3 py-2 hover:bg-slate-50 border-b border-slate-100 last:border-0"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-xs font-bold text-slate-900 truncate flex items-center gap-1">
                            <MapPin className="w-3 h-3 text-emerald-500 shrink-0" />
                            {loc.name || loc.place_name}
                          </div>
                          <div className="text-[10px] text-slate-500 truncate">
                            {[loc.district, loc.stateOrRegion, 'India'].filter(Boolean).join(', ')}
                          </div>
                        </div>
                        <div className="text-right shrink-0">
                          <WarningBadge state={cat as any} size="sm" />
                          <div className="text-[9px] text-slate-500 mt-0.5">{(prob * 100).toFixed(0)}%</div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}
          </div>

          <div className="h-5 w-px bg-slate-200" />

          {/* State filter */}
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={filterState}
              onChange={(e) => handleStateChange(e.target.value)}
              className="text-xs border border-slate-300 rounded-lg px-2 py-1.5 bg-slate-50 font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-400"
            >
              <option value="ALL">All India</option>
              {INDIA_STATES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          {/* District filter */}
          {availableDistricts.length > 0 && (
            <div className="flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              <select
                value={filterDistrict}
                onChange={(e) => setFilterDistrict(e.target.value)}
                className="text-xs border border-slate-300 rounded-lg px-2 py-1.5 bg-slate-50 font-bold text-slate-800 focus:outline-none focus:ring-2 focus:ring-emerald-400"
              >
                <option value="ALL">All Districts</option>
                {availableDistricts.map((d) => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
          )}

          <div className="h-5 w-px bg-slate-200" />

          {/* Warning state filter */}
          <div className="flex items-center gap-1">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            {['ALL', 'HIGH_RISK', 'WARNING', 'WATCH', 'NORMAL'].map((st) => {
              const labels: Record<string, string> = { ALL: 'All', HIGH_RISK: 'High Risk', WARNING: 'Warning', WATCH: 'Watch', NORMAL: 'Normal' };
              const colors: Record<string, string> = {
                ALL: 'bg-slate-900 text-white', HIGH_RISK: 'bg-red-600 text-white',
                WARNING: 'bg-orange-500 text-white', WATCH: 'bg-yellow-500 text-white', NORMAL: 'bg-emerald-600 text-white',
              };
              const inactiveColors: Record<string, string> = {
                ALL: 'text-slate-600', HIGH_RISK: 'text-red-600', WARNING: 'text-orange-600',
                WATCH: 'text-yellow-700', NORMAL: 'text-emerald-700',
              };
              return (
                <button
                  key={st}
                  type="button"
                  onClick={() => setFilterWarning(st)}
                  className={`px-2.5 py-1 text-[10px] font-bold rounded-lg transition ${
                    filterWarning === st ? colors[st] : `bg-slate-100 ${inactiveColors[st]} hover:bg-slate-200`
                  }`}
                >
                  {labels[st]}
                </button>
              );
            })}
          </div>

          <div className="ml-auto text-[10px] text-slate-500 font-semibold">
            <span className="text-emerald-700 font-black">{filteredLocations.length.toLocaleString()}</span> locations
          </div>
        </div>

        {/* Map */}
        <div className="flex-1 relative overflow-hidden">
          {loading ? (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-50">
              <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-3" />
              <p className="text-sm font-bold text-slate-600">Loading India location data…</p>
              <p className="text-xs text-slate-400 mt-1">Fetching 1,340+ verified locations</p>
            </div>
          ) : error ? (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-50">
              <div className="text-center p-8">
                <AlertTriangle className="w-10 h-10 text-orange-500 mx-auto mb-3" />
                <p className="text-sm font-bold text-slate-700">Could not load India data</p>
                <p className="text-xs text-slate-500 mt-1">{error}</p>
              </div>
            </div>
          ) : (
            <IndiaMapComponent
              locations={filteredLocations}
              selectedLocationId={selectedLocId}
              onSelectLocation={handleSelectLocation}
            />
          )}
        </div>

        {/* Footer */}
        <div className="bg-white border-t border-slate-200 px-4 py-1.5 flex items-center gap-4 text-[10px] text-slate-500 shrink-0">
          <Info className="w-3 h-3 text-slate-400 shrink-0" />
          <span>
            <strong className="text-slate-700">Research / Historical Assessment Mode</strong> — AI-assisted risk assessment.
            Only verified project data is displayed. Locations without current model output show DATA UNAVAILABLE.
            Not a replacement for official geological or disaster-management warnings.
          </span>
          <span className="ml-auto text-emerald-700 font-bold shrink-0">India Verified Coverage</span>
        </div>
      </div>
    </div>
  );
};

// ── Utility ───────────────────────────────────────────────────────────────────
function str(v: any): string {
  return v == null ? '' : String(v);
}
