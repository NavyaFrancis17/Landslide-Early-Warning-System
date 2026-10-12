import React from 'react';
import { ShieldCheck } from 'lucide-react';
import { DataStatusBadge } from './DataStatusBadge';

export const Header: React.FC = () => {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 px-8 py-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 sticky top-0 z-20 shadow-md">
      <div>
        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold tracking-wider uppercase rounded border border-emerald-500/30">
            Decision Support Platform
          </span>
          <DataStatusBadge status="MODEL ASSESSMENT" size="sm" />
        </div>
        <h1 className="text-xl font-black tracking-tight mt-1 flex items-center gap-2">
          LANDSLIDE AI PLATFORM
        </h1>
        <p className="text-xs text-slate-300 font-medium mt-0.5">
          Location-Adaptive Early Warning & Decision Support System
        </p>
      </div>

      <div className="flex items-center gap-3 bg-slate-950 px-4 py-2 rounded-xl border border-slate-800">
        <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
        <div>
          <span className="text-[10px] uppercase text-slate-400 font-bold block">Assessment Mode</span>
          <span className="text-xs font-semibold text-slate-200">Research / Historical Assessment Mode</span>
        </div>
      </div>
    </header>
  );
};
