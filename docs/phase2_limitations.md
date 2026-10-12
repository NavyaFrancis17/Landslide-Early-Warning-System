# Dataset Limitations & Research Scope Report — Phase 2

## 1. Executive Summary

This document provides a scientific evaluation of the primary dataset (`data/raw/Global_Landslide_Catalog_Export.csv`). While the NASA Global Landslide Catalog provides a global historical record of real-world landslide occurrences, it has significant empirical limitations that must be addressed before training predictive models or conducting lead-time experiments.

---

## 2. Identified Empirical Limitations

### A. Incomplete & Ambiguous Event Dates
* **Metrics**: Out of `11,033` records, only `4,395` (`39.83%`) possess standardized, fully parseable `event_date` values (`YYYY-MM-DD`). The remaining `6,638` records (`60.17%`) contain incomplete strings (missing exact day or year) or ambiguous formatting.
* **Impact**: Temporal sequence analysis and lead-time evaluation must be restricted to the subset of records with valid parsed dates (`data/processed/landslide_events_temporal.csv`).

---

### B. Absence of Continuous Environmental Telemetry
* **Missing Variables**: The raw catalog does **NOT** contain:
  1. Continuous daily rainfall values (mm/day)
  2. Volumetric soil moisture percentages (%)
  3. Terrain slope gradient (°)
  4. Topographic elevation above sea level (m)
  5. Land cover classification
* **Trigger Category vs. Numerical Data**: The dataset records categorical triggers (e.g. `landslide_trigger` = `rain`), but lacks continuous numerical weather observations.

---

### C. Event-Only Bias (Absence of Non-Event Negative Controls)
* **Dataset Characteristic**: The catalog is an **incident catalog**. It exclusively contains positive landslide events ($y=1$). It does not contain daily non-event background streams ($y=0$).
* **Impact**: Early-warning systems require training on both event and non-event days to compute false-alarm rates, precision-recall curves, and ROC metrics.

---

### D. Multi-Day Lead-Time Experiment Feasibility Assessment

> **SCIENTIFIC CONCLUSION ON LEAD-TIME EXPERIMENTS**:
>
> **The current raw NASA Global Landslide Catalog dataset ALONE CANNOT support a true multi-day lead-time forecasting experiment.**
>
> Reason: A multi-day lead-time experiment requires antecedent environmental time series (e.g., precipitation 1 to 7 days prior to event date) across both event and non-event baseline windows. The raw catalog records only the event occurrence day without prior daily weather streams.

---

## 3. Required External Dataset Integrations for Phase 3+

To build a location-adaptive, temporal early-warning system in subsequent phases, the following external datasets will be integrated via spatial-temporal joins (`latitude`, `longitude`, `event_date`):

1. **NASA GPM IMERG / ERA5 Precipitation Reanalysis**: To retrieve continuous daily 1-day, 3-day, 7-day, and 14-day antecedent accumulated rainfall (mm).
2. **ERA5-Land Volumetric Soil Moisture**: To retrieve daily antecedent soil saturation (%).
3. **NASA SRTM / NASADEM Global Elevation Model**: To extract continuous slope inclination (°) and elevation (m).
