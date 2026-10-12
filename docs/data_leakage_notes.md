# Data Leakage Prevention Framework & Field Audit

> **CRITICAL ACADEMIC INTEGRITY DIRECTIVE**:
> Data leakage occurs when information unavailable at prediction time is inadvertently included as an input feature during machine learning model training. In landslide early-warning systems, using post-event metrics or event-outcome fields as model predictors artificially inflates model metrics while rendering the system unusable for real-time forecasting.

---

## 1. Categorization of Dataset Fields

### Category A: Pre-Event / Causative Features (Valid Predictive Inputs)
These variables represent physical, spatial, or location-baseline characteristics known prior to event occurrence:
* `latitude` & `longitude` (Geographic monitoring location)
* `country_name` & `country_code` & `admin_division_name` (Regional administrative boundaries)
* `admin_division_population` (Zone population metric)
* `location_accuracy` (Spatial radius precision label)
* `landslide_setting` (Geological/topographic environment setting, e.g. `steep_slope`, `above_road`)
* `event_year`, `event_month`, `event_day`, `event_day_of_year`, `season` (Derived temporal calendar attributes)

---

### Category B: Event Outcome & Severity Targets (Strictly Excluded from Predictive Inputs)
These fields represent consequences or observed severity resulting from the event. **Using these as input features constitutes catastrophic target leakage**:
* `landslide_size` (`small`, `medium`, `large`, `catastrophic` — known only after occurrence)
* `fatality_count` (Casualty metric recorded post-disaster)
* `injury_count` (Casualty metric recorded post-disaster)
* `event_title` & `event_description` (Narrative summaries written post-event)

---

### Category C: Post-Event Metadata & Administrative Artifacts (Strictly Excluded)
These fields are system logging timestamps and administrative references generated after report submission:
* `submitted_date` (Date report was filed in database)
* `created_date` (Database record insertion timestamp)
* `last_edited_date` (Database edit timestamp)
* `event_import_id` & `event_import_source` (Database import tags)
* `source_name` & `source_link` & `photo_link` (News/bulletin citations)

---

### Category D: Primary Target Variable
* `landslide_category` (Classification of landslide type: `landslide`, `mudslide`, `debris_flow`, `rock_fall`).

---

## 2. Mandatory Rules for Phase 3+ Model Pipeline Construction

1. **Feature Matrix Selection**: When assembling feature matrices ($X$), **only Category A features** (plus external continuous meteorology/terrain rasters added in future phases) may be selected.
2. **Target Vector Selection**: Target labels ($y$) must be constructed from `landslide_category` (or binary event flags).
3. **Automated Leakage Check**: Unit tests in Phase 2 (`tests/test_temporal_features.py`) strictly assert that `landslide_size`, `fatality_count`, `injury_count`, `submitted_date`, `created_date`, and `last_edited_date` are absent from model input feature lists.
