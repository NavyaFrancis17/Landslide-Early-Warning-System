import React from 'react';
import type { AssessmentType } from '../types';

interface DataStatusBadgeProps {
  status: AssessmentType | string;
  size?: 'sm' | 'md';
}

export const DataStatusBadge: React.FC<DataStatusBadgeProps> = ({ status, size = 'md' }) => {
  const styles: Record<string, string> = {
    'HISTORICAL OBSERVATION': 'bg-blue-50 text-blue-800 border-blue-200',
    'MODEL ASSESSMENT': 'bg-emerald-50 text-emerald-900 border-emerald-300 font-bold',
    'FORECAST': 'bg-purple-50 text-purple-800 border-purple-200',
    'SIMULATION': 'bg-amber-100 text-amber-900 border-amber-400 font-bold',
    'DATA UNAVAILABLE': 'bg-slate-100 text-slate-600 border-slate-300',
  };

  const currentStyle = styles[status] || styles['MODEL ASSESSMENT'];

  const sizes = {
    sm: 'px-2 py-0.5 text-[10px] rounded border',
    md: 'px-2.5 py-1 text-xs rounded-md border font-semibold',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 ${currentStyle} ${sizes[size]}`}>
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
};
