import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Activity,
  AlertTriangle,
  BarChart2,
  Compass,
  LayoutDashboard,
  Sliders,
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const navItems = [
    { to: '/dashboard', label: 'Overview Dashboard', icon: <LayoutDashboard className="w-4 h-4" /> },
    { to: '/map', label: 'Geographic Hazard Map', icon: <Compass className="w-4 h-4" /> },
    { to: '/warnings', label: 'Early Warning Log', icon: <AlertTriangle className="w-4 h-4" /> },
    { to: '/evaluation', label: 'Performance Evaluation', icon: <BarChart2 className="w-4 h-4" /> },
    { to: '/simulation', label: 'What-If Simulator', icon: <Sliders className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-100 flex flex-col h-screen sticky top-0 border-r border-slate-800 shrink-0">
      <div className="p-5 border-b border-slate-800 flex items-center gap-3">
        <div className="p-2 bg-emerald-500 rounded-lg text-slate-950 font-bold shadow-md">
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-black text-white tracking-wide leading-snug">Landslide AI Platform</h1>
          <p className="text-[11px] text-slate-400 font-medium">Early Warning System</p>
        </div>
      </div>

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold transition-all ${
                isActive
                  ? 'bg-emerald-500 text-slate-950 shadow-md font-extrabold'
                  : 'text-slate-300 hover:bg-slate-800/80 hover:text-white'
              }`
            }
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="p-4 border-t border-slate-800 bg-slate-950 text-xs text-slate-400">
        <div className="flex items-center gap-2 font-bold text-slate-200 mb-1">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          System Status: Operational
        </div>
        <p className="text-[10px] text-slate-500 font-medium">Real-Time Hazard Monitoring v1.0</p>
      </div>
    </aside>
  );
};
