import type { RiskCategory, WarningState } from '../types';

export interface RiskThresholdConfig {
  min: number;
  max: number;
  category: RiskCategory;
  label: string;
  color: string;
  bgColor: string;
  badgeClass: string;
}

export const RISK_THRESHOLDS: Record<RiskCategory, RiskThresholdConfig> = {
  LOW: {
    min: 0.0,
    max: 0.25,
    category: 'LOW',
    label: 'LOW RISK',
    color: '#10b981',
    bgColor: 'rgba(16, 185, 129, 0.1)',
    badgeClass: 'bg-emerald-50 text-emerald-800 border-emerald-300',
  },
  WATCH: {
    min: 0.25,
    max: 0.50,
    category: 'WATCH',
    label: 'WATCH',
    color: '#f59e0b',
    bgColor: 'rgba(245, 158, 11, 0.1)',
    badgeClass: 'bg-amber-50 text-amber-900 border-amber-300',
  },
  WARNING: {
    min: 0.50,
    max: 0.75,
    category: 'WARNING',
    label: 'WARNING',
    color: '#f97316',
    bgColor: 'rgba(249, 115, 22, 0.1)',
    badgeClass: 'bg-orange-50 text-orange-900 border-orange-300',
  },
  'HIGH RISK': {
    min: 0.75,
    max: 1.00,
    category: 'HIGH RISK',
    label: 'HIGH RISK',
    color: '#ef4444',
    bgColor: 'rgba(239, 68, 68, 0.1)',
    badgeClass: 'bg-red-50 text-red-900 border-red-300',
  },
};

export function calculateRiskCategory(score: number): RiskCategory {
  if (score >= 0.75) return 'HIGH RISK';
  if (score >= 0.50) return 'WARNING';
  if (score >= 0.25) return 'WATCH';
  return 'LOW';
}

export function normalizeRiskCategory(val: string | undefined): RiskCategory {
  if (!val) return 'LOW';
  const clean = val.toUpperCase().trim().replace(/_/g, ' ');
  if (clean.includes('HIGH')) return 'HIGH RISK';
  if (clean.includes('WARN')) return 'WARNING';
  if (clean.includes('WATCH')) return 'WATCH';
  return 'LOW';
}

export function getRiskColor(categoryOrScore: RiskCategory | WarningState | number): string {
  if (typeof categoryOrScore === 'number') {
    const cat = calculateRiskCategory(categoryOrScore);
    return RISK_THRESHOLDS[cat].color;
  }
  const norm = normalizeRiskCategory(categoryOrScore);
  return RISK_THRESHOLDS[norm].color;
}

export function getRiskBadgeClass(categoryOrScore: RiskCategory | WarningState | number): string {
  if (typeof categoryOrScore === 'number') {
    const cat = calculateRiskCategory(categoryOrScore);
    return RISK_THRESHOLDS[cat].badgeClass;
  }
  const norm = normalizeRiskCategory(categoryOrScore);
  return RISK_THRESHOLDS[norm].badgeClass;
}
