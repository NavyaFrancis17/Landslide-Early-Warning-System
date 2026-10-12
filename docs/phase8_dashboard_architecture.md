# Phase 8 React Dashboard Architecture Document

## 1. System Architecture
The React web dashboard is structured around a modern decoupled client-server architecture:

```
React 18 + Vite + TypeScript Frontend (Port 5173)
        ↓ (REST API via /api Proxy)
FastAPI Backend Application Layer (Port 8000)
        ↓
Phase 1-7 Inference Modules (EarlyWarningEngine, WhatIfSimulator, EventEvaluator)
        ↓
Saved Models (gradient_boosting.joblib) & Feature Datasets (event_environment_features.csv)
```

## 2. Dashboard Pages
* **/dashboard**: KPI cards, interactive Leaflet map, and historical risk timeline.
* **/map**: Full-screen interactive map with color-coded warning state markers.
* **/warnings**: Filterable, paginated table of persistent Phase 5 warning events.
* **/evaluation**: Phase 6 quantitative evaluation results, lead-time distribution, and leakage audit.
* **/simulation**: Interactive What-If scenario controls, real-time API execution, and sensitivity curves.
* **/location/:locationId**: Location deep-dive with risk timeline and explainable alert strings.
* **/about**: Interactive system architecture and zero-fabrication methodology overview.
