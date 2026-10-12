import React, { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { ComprehensiveLocationData, ModelPerformanceMetrics } from '../types';
import { FEATURED_LOCATIONS } from '../data/featuredLocations';
import { api } from '../services/api';

interface LocationContextType {
  locations: ComprehensiveLocationData[];
  selectedLocation: ComprehensiveLocationData;
  selectedLocId: string;
  selectLocation: (id: string) => Promise<void>;
  loading: boolean;
  error: string | null;
  modelMetrics: ModelPerformanceMetrics | null;
  refreshData: () => Promise<void>;
  addLocation: (loc: ComprehensiveLocationData) => void;
}

const defaultLocation = FEATURED_LOCATIONS[0]; // Wayanad, Kerala

const LocationContext = createContext<LocationContextType>({
  locations: FEATURED_LOCATIONS,
  selectedLocation: defaultLocation,
  selectedLocId: defaultLocation.id,
  selectLocation: async () => {},
  loading: false,
  error: null,
  modelMetrics: null,
  refreshData: async () => {},
  addLocation: () => {},
});

export const LocationProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [locations, setLocations] = useState<ComprehensiveLocationData[]>(FEATURED_LOCATIONS);
  const [selectedLocId, setSelectedLocId] = useState<string>(defaultLocation.id);
  const [selectedLocation, setSelectedLocation] = useState<ComprehensiveLocationData>(defaultLocation);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [modelMetrics, setModelMetrics] = useState<ModelPerformanceMetrics | null>(null);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch ALL locations and metrics in parallel
      const [fetchedLocs, metrics] = await Promise.allSettled([
        api.getAllLocations(),
        api.getModelMetrics(),
      ]);

      let mergedLocs: ComprehensiveLocationData[] = [...FEATURED_LOCATIONS];

      if (fetchedLocs.status === 'fulfilled' && fetchedLocs.value.length > 0) {
        // Merge fetched locations ensuring all featured locations are present at top
        const fetchedMap = new Map<string, ComprehensiveLocationData>();
        fetchedLocs.value.forEach((l) => fetchedMap.set(l.id || l.location_id || '', l));

        // Update featured locations with any fresh server data
        const updatedFeatured = FEATURED_LOCATIONS.map((f) => {
          const serverMatch = fetchedMap.get(f.id);
          return serverMatch ? { ...f, ...serverMatch } : f;
        });

        // Add additional locations from server
        const additional: ComprehensiveLocationData[] = [];
        fetchedLocs.value.forEach((l) => {
          const lId = l.id || l.location_id || '';
          if (!FEATURED_LOCATIONS.some((f) => f.id === lId)) {
            additional.push(l);
          }
        });

        mergedLocs = [...updatedFeatured, ...additional];
      }

      setLocations(mergedLocs);

      if (metrics.status === 'fulfilled') {
        setModelMetrics(metrics.value);
      }

      // Keep current selection or default to first location
      const current = mergedLocs.find((l) => (l.id || l.location_id) === selectedLocId) || mergedLocs[0];
      setSelectedLocation(current);
      setSelectedLocId(current.id || current.location_id || '');
    } catch (err: any) {
      console.warn('Backend loading fallback to internal repository data:', err.message);
      // Fail-safe: Always have rich featured locations ready
      setLocations(FEATURED_LOCATIONS);
      setSelectedLocation(FEATURED_LOCATIONS[0]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadInitialData();
  }, []);

  const selectLocation = async (id: string) => {
    if (!id) return;
    setSelectedLocId(id);

    // 1. Check local list first for instant responsiveness
    const found = locations.find((l) => (l.id || l.location_id) === id);
    if (found) {
      setSelectedLocation(found);
    }

    // 2. Fetch full detail from backend if available
    try {
      const detail = await api.getLocationDetail(id);
      if (detail) {
        setSelectedLocation((prev) => ({ ...prev, ...detail }));
      }
    } catch (err) {
      console.warn('Using existing cached location detail for', id);
    }
  };

  const addLocation = (loc: ComprehensiveLocationData) => {
    // Clear any previous live_ search results to prevent stale data
    setLocations(prev => [loc, ...prev.filter(l => !(l.id || '').toString().startsWith('live_'))]);
  };

  return (
    <LocationContext.Provider
      value={{
        locations,
        selectedLocation,
        selectedLocId,
        selectLocation,
        loading,
        error,
        modelMetrics,
        refreshData: loadInitialData,
        addLocation,
      }}
    >
      {children}
    </LocationContext.Provider>
  );
};

export const useLocation = () => useContext(LocationContext);
