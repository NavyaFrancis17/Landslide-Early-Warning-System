import React from 'react';
import type { WarningState } from '../types';

interface WarningBadgeProps {
  state: WarningState;
  size?: 'sm' | 'md' | 'lg';
}

export const WarningBadge: React.FC<WarningBadgeProps> = ({ state, size = 'md' }) => {
  const styles: Record<WarningState, string> = {
    NORMAL: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    WATCH: 'bg-amber-100 text-amber-800 border-amber-300',
    WARNING: 'bg-orange-100 text-orange-800 border-orange-300',
    HIGH_RISK: 'bg-red-100 text-red-900 border-red-400 font-bold animate-pulse',
  };

  const sizes = {
    sm: 'px-2 py-0.5 text-xs font-semibold rounded-full border',
    md: 'px-3 py-1 text-sm font-semibold rounded-full border',
    lg: 'px-4 py-1.5 text-base font-bold rounded-full border-2',
  };

  return (
    <span className={`inline-flex items-center gap-1.5 ${styles[state] || styles.NORMAL} ${sizes[size]}`}>
      <span className="w-2 h-2 rounded-full bg-current" />
      {state}
    </span>
  );
};
