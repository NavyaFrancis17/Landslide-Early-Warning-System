import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Navbar } from './components/Navbar';
import { Header } from './components/Header';
import { DashboardPage } from './pages/Dashboard';
import { MapPage } from './pages/MapView';
import { WarningHistoryPage } from './pages/WarningHistory';
import { EvaluationPage } from './pages/EvaluationView';
import { SimulationPage } from './pages/SimulationView';
import { LocationDetailPage } from './pages/LocationDetail';
import { AboutPage } from './pages/AboutView';
import { LocationProvider } from './context/LocationContext';

export const App: React.FC = () => {
  return (
    <LocationProvider>
      <Router>
        <div className="flex min-h-screen bg-slate-100 text-slate-900 font-sans antialiased">
          <Navbar />
          <div className="flex-1 flex flex-col min-w-0">
            <Header />
            <main className="flex-1 overflow-y-auto">
              <Routes>
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/map" element={<MapPage />} />
                <Route path="/warnings" element={<WarningHistoryPage />} />
                <Route path="/evaluation" element={<EvaluationPage />} />
                <Route path="/simulation" element={<SimulationPage />} />
                <Route path="/location/:locationId" element={<LocationDetailPage />} />
                <Route path="/about" element={<AboutPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
              </Routes>
            </main>
          </div>
        </div>
      </Router>
    </LocationProvider>
  );
};

export default App;
