import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertTriangle, ChevronLeft, ChevronRight, Filter, Globe, MapPin } from 'lucide-react';
import { WarningBadge } from '../components/WarningBadge';
import { DataStatusBadge } from '../components/DataStatusBadge';
import { useLocation } from '../context/LocationContext';
import { api } from '../services/api';
import type { WarningEvent } from '../types';

export const WarningHistoryPage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedLocation, selectLocation, locations } = useLocation();
  const [events, setEvents] = useState<WarningEvent[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(0);
  const [filterState, setFilterState] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [showSelectedOnly, setShowSelectedOnly] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);
  const limit = 20;

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const data = await api.getWarnings(
          filterState || undefined,
          limit,
          page * limit
        );
        setEvents(data.items);
        setTotal(data.total);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, [page, filterState]);

  const maxPage = Math.ceil(total / limit) - 1;

  // Selected location's historical log entries generated from single source of truth
  const locTimeline = (selectedLocation.historyTimeline || []).map((pt, idx) => ({
    warning_event_id: `sel_hist_${idx}`,
    location_id: selectedLocation.id || selectedLocation.location_id || '',
    place_name: selectedLocation.name || selectedLocation.place_name || '',
    district: selectedLocation.district,
    region: selectedLocation.stateOrRegion || selectedLocation.region,
    country: selectedLocation.country,
    latitude: selectedLocation.latitude,
    longitude: selectedLocation.longitude,
    warning_start_time: pt.timestamp,
    initial_state: (pt.current_warning_state as any) || 'WATCH',
    maximum_state: (pt.current_warning_state as any) || selectedLocation.current_warning_state || 'WARNING',
    risk_score: pt.risk_probability,
    triggering_factors: selectedLocation.contributingFactors?.slice(0, 2).join(' & ') || 'Elevated antecedent rainfall & soil saturation',
    observation_duration: idx + 1,
    assessment_type: 'MODEL ASSESSMENT' as const,
  }));

  const displayedEvents = showSelectedOnly ? locTimeline : events.filter((e) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      e.place_name.toLowerCase().includes(q) ||
      (e.country && e.country.toLowerCase().includes(q)) ||
      (e.region && e.region.toLowerCase().includes(q))
    );
  });

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <AlertTriangle className="w-6 h-6 text-orange-600" /> Early Warning Log &amp; Historical Events
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Chronological warning log and historical escalations for <strong className="text-slate-800">📍 {selectedLocation.name}</strong> and evaluated repository stations
          </p>
        </div>

        {/* Selected Location Scope Toggle */}
        <div className="flex items-center gap-2 bg-white p-1.5 rounded-xl border border-slate-200 shadow-sm">
          <button
            type="button"
            onClick={() => setShowSelectedOnly(true)}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer flex items-center gap-1.5 ${
              showSelectedOnly
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            <MapPin className="w-3.5 h-3.5 text-emerald-400" /> Selected: {selectedLocation.name}
          </button>
          <button
            type="button"
            onClick={() => setShowSelectedOnly(false)}
            className={`px-3 py-1.5 text-xs font-bold rounded-lg transition cursor-pointer ${
              !showSelectedOnly
                ? 'bg-slate-900 text-white shadow-sm'
                : 'text-slate-600 hover:bg-slate-100'
            }`}
          >
            All Evaluated Locations ({total})
          </button>
        </div>
      </div>

      {/* Filter Toolbar (Visible when viewing All Locations) */}
      {!showSelectedOnly && (
        <div className="flex flex-wrap items-center justify-between gap-3 bg-white p-2.5 rounded-xl shadow-sm border border-slate-200">
          <div className="flex items-center gap-1.5">
            <Filter className="w-4 h-4 text-slate-400 ml-2" />
            <span className="text-xs font-bold text-slate-600 mr-1">State:</span>
            {['', 'HIGH_RISK', 'WARNING', 'WATCH'].map((st) => (
              <button
                key={st}
                onClick={() => {
                  setFilterState(st);
                  setPage(0);
                }}
                className={`px-3 py-1 text-xs font-bold rounded-lg transition cursor-pointer ${
                  filterState === st
                    ? 'bg-slate-900 text-white'
                    : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                {st || 'ALL'}
              </button>
            ))}
          </div>

          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter by place name..."
              className="px-3 py-1.5 bg-slate-50 border border-slate-300 rounded-lg text-xs font-semibold text-slate-900 placeholder:text-slate-400 focus:outline-none w-56"
            />
          </div>
        </div>
      )}

      {/* Selected Location Active Notice */}
      {showSelectedOnly && (
        <div className="bg-emerald-50 border border-emerald-200 p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
          <div>
            <span className="font-extrabold text-emerald-950 text-sm block">
              📍 Logged Sequential Warnings for {selectedLocation.name}
            </span>
            <p className="text-emerald-800 mt-0.5">
              Region: {selectedLocation.stateOrRegion}, {selectedLocation.country} &bull; Coordinates: {selectedLocation.latitude.toFixed(3)}°, {selectedLocation.longitude.toFixed(3)}° &bull; Current Risk: {(selectedLocation.landslideProbability * 100).toFixed(1)}% ({selectedLocation.riskCategory})
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <select
              value={selectedLocation.id || selectedLocation.location_id}
              onChange={(e) => selectLocation(e.target.value)}
              className="p-2 bg-white border border-emerald-300 rounded-lg text-xs font-bold text-slate-900 cursor-pointer"
            >
              {locations.map((loc) => (
                <option key={loc.id || loc.location_id} value={loc.id || loc.location_id}>
                  Switch to: {loc.name || loc.place_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Table Container */}
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden space-y-3 p-4">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-200 text-slate-500 text-xs font-bold uppercase tracking-wider">
                <th className="py-3.5 px-4">Date / Time</th>
                <th className="py-3.5 px-4">Location Identity</th>
                <th className="py-3.5 px-4">Risk Category</th>
                <th className="py-3.5 px-4">Risk Score</th>
                <th className="py-3.5 px-4">Main Triggering Factors</th>
                <th className="py-3.5 px-4">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-800 text-xs">
              {loading && !showSelectedOnly ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    Loading early warning log events...
                  </td>
                </tr>
              ) : displayedEvents.length === 0 ? (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-slate-500">
                    No early warning events found for selected parameters.
                  </td>
                </tr>
              ) : (
                displayedEvents.map((e: any, idx: number) => {
                  const prob = e.risk_score ?? selectedLocation.landslideProbability;
                  return (
                    <tr
                      key={e.warning_event_id || idx}
                      onClick={() => {
                        selectLocation(e.location_id);
                        navigate(`/location/${encodeURIComponent(e.location_id)}`);
                      }}
                      className="hover:bg-slate-50 transition cursor-pointer"
                    >
                      <td className="py-3.5 px-4 font-mono text-slate-600">
                        {e.warning_start_time || '22 Sep 2026, 13:30'}
                      </td>
                      <td className="py-3.5 px-4 font-bold text-slate-900">
                        📍 {e.place_name}
                      </td>
                      <td className="py-3.5 px-4">
                        <WarningBadge state={e.maximum_state || e.initial_state} size="sm" />
                      </td>
                      <td className="py-3.5 px-4 font-black text-slate-900">
                        {(prob * 100).toFixed(1)}%
                      </td>
                      <td className="py-3.5 px-4 text-slate-700 max-w-xs truncate">
                        {e.triggering_factors || selectedLocation.contributingFactors?.[0] || 'Extreme precipitation & terrain saturation'}
                      </td>
                      <td className="py-3.5 px-4">
                        <DataStatusBadge status={e.assessment_type || 'MODEL ASSESSMENT'} size="sm" />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination when in All Mode */}
        {!showSelectedOnly && (
          <div className="p-4 bg-slate-50 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600 font-semibold rounded-b-xl">
            <span>
              Showing {events.length > 0 ? page * limit + 1 : 0} to {Math.min((page + 1) * limit, total)} of {total} warning events
            </span>
            <div className="flex items-center gap-2">
              <button
                disabled={page === 0}
                onClick={() => setPage((p) => Math.max(0, p - 1))}
                className="p-1.5 rounded-lg border border-slate-300 bg-white text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition cursor-pointer"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span>Page {page + 1} of {Math.max(1, maxPage + 1)}</span>
              <button
                disabled={page >= maxPage}
                onClick={() => setPage((p) => Math.min(maxPage, p + 1))}
                className="p-1.5 rounded-lg border border-slate-300 bg-white text-slate-700 disabled:opacity-40 hover:bg-slate-100 transition cursor-pointer"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
