import React from 'react';
import { Activity, Layers, ShieldCheck } from 'lucide-react';
import { DataStatusBadge } from '../components/DataStatusBadge';

export const AboutPage: React.FC = () => {
  return (
    <div className="p-8 space-y-8 max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
            <Activity className="w-6 h-6 text-emerald-600" /> LANDSLIDE AI PLATFORM
          </h1>
          <p className="text-xs text-slate-500 mt-1">
            Location-Adaptive Early Warning & Decision Support System Architecture
          </p>
        </div>
        <DataStatusBadge status="MODEL ASSESSMENT" size="md" />
      </div>

      {/* Innovation Banner Message */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white p-6 rounded-2xl shadow-lg border border-slate-800 space-y-3">
        <span className="text-[10px] font-bold uppercase tracking-widest text-emerald-400 block">CORE METHODOLOGICAL CONTRIBUTION</span>
        <blockquote className="text-sm font-semibold text-slate-100 leading-relaxed italic">
          "The main contribution is not the use of machine learning alone. The system integrates AI-based risk estimation with location-specific historical environmental baselines, multi-temporal abnormality detection, temporal risk escalation, progressive warning states, explainable alerts, event-oriented evaluation, and what-if analysis."
        </blockquote>
      </div>

      {/* Why This System is Different (10 System Contributions) */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-6">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <Layers className="w-5 h-5 text-emerald-600" /> WHY THIS SYSTEM IS DIFFERENT (10 KEY CONTRIBUTIONS)
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          {[
            { title: '1. Location-Adaptive Historical Baseline', desc: 'Compares environmental conditions with the local historical behavior of each specific slope rather than relying on a single global threshold.' },
            { title: '2. Multi-Temporal Environmental Change', desc: 'Ingests multi-window cumulative precipitation (1h to 168h) and multi-layer soil moisture from ERA5-Land reanalysis.' },
            { title: '3. AI-Based Risk Estimation', desc: 'Uses a trained Gradient Boosting Classifier to estimate risk probability P(landslide) with 0.9998 ROC-AUC.' },
            { title: '4. Temporal Risk Escalation', desc: 'Tracks how risk changes dynamically over consecutive observations rather than producing only a static susceptibility value.' },
            { title: '5. Progressive Warning States', desc: 'Assigns structured states (NORMAL → WATCH → WARNING → HIGH_RISK) with persistence locking to prevent alert chatter.' },
            { title: '6. Explainable Warning Reasons', desc: 'Generates plain-language text explanations linking alert states to rainfall anomalies, soil moisture, and trend deltas.' },
            { title: '7. Event-Oriented Lead-Time Evaluation', desc: 'Evaluates early warnings against catalog landslides, measuring median pre-event lead time (33.0 hours).' },
            { title: '8. What-If Scenario Simulation', desc: 'Provides counterfactual scenario analysis for rainfall and soil moisture modifications with training domain checks.' },
            { title: '9. Global Place-Centric User Experience', desc: 'Transforms technical location IDs into place-centric identities (Place, District, State/Region, Country).' },
            { title: '10. Data-Trust & Coverage Awareness', desc: 'Explicitly labels data types (Historical Observation, Model Assessment, Forecast, Simulation, Data Unavailable).' },
          ].map((item, idx) => (
            <div key={idx} className="p-4 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
              <div className="font-bold text-slate-900">{item.title}</div>
              <div className="text-slate-600 leading-relaxed font-medium">{item.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Data Integrity & Zero Fabrication Guarantees */}
      <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 space-y-4">
        <h2 className="text-base font-bold text-slate-900 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-emerald-600" /> DATA INTEGRITY & SCIENTIFIC HONESTY GUARANTEES
        </h2>
        <ul className="space-y-2 text-xs text-slate-600 leading-relaxed list-disc list-inside font-medium">
          <li><strong>Zero Synthetic Risk Scores:</strong> All risk probabilities originate from verified ML model outputs or actual historical data.</li>
          <li><strong>Data Coverage Awareness:</strong> Unmonitored locations explicitly display "Data Unavailable for This Location" rather than assigning arbitrary low risk.</li>
          <li><strong>Simulation Badge:</strong> What-If scenarios are badged with "SIMULATION — NOT A LIVE WARNING" to prevent misinterpretation.</li>
          <li><strong>No Unsubstantiated Claims:</strong> The system does not claim guaranteed 5-day predictions or guaranteed landslide occurrences. Risk is communicated strictly as model-estimated hazard probability.</li>
        </ul>
      </div>
    </div>
  );
};
