# Primary Project Dataset Source Information & Variables Audit

## 1. Dataset Identification & Provenance

* **Dataset Name**: Global Landslide Catalog (GLC)
* **Kaggle Equivalent**: `nasa/landslide-catalog` / `global-landslide-catalog`
* **Original Publisher / Provider**: NASA Goddard Space Flight Center (NASA Open Data Portal & Cooperative Open Online Landslide Repository — COOLR)
* **Primary Scientific Citation**:
  > Kirschbaum, D. B., Adler, R., Hong, Y., Hill, S., & Lerner-Lam, A. (2010). A global landslide catalog for hazard applications: method, results, and limitations. *Natural Hazards*, 52(3), 561–575.
* **Local Raw File Location**: `data/raw/Global_Landslide_Catalog_Export.csv`
* **File Format**: Unmodified CSV (Comma-Separated Values, UTF-8)
* **File Size**: ~8.02 MB

---

## 2. Dataset Overview & Content

The NASA Global Landslide Catalog (GLC) is the primary real-world empirical dataset selected for this research project. It tracks rainfall-triggered and environmental landslide events reported globally across multiple continents.

### Inspected Raw Schema (31 Columns)
1. `source_name` (string): Source reporting organization or publication.
2. `source_link` (string): URL link to original news report or geological bulletin.
3. `event_id` (integer): Unique numeric identifier for the landslide event record.
4. `event_date` (string/datetime): Date and timestamp of landslide occurrence (`MM/DD/YYYY` or `DD-MM-YYYY HH:MM`).
5. `event_time` (string): Approximate local time of event occurrence.
6. `event_title` (string): Title or short summary of the event location.
7. `event_description` (string): Detailed textual narrative describing event circumstances.
8. `location_description` (string): Named geographic location (village, county, province).
9. `location_accuracy` (string): Precision radius of coordinates (e.g., `exact`, `1km`, `5km`, `10km`, `unknown`).
10. `landslide_category` (string): Classification (e.g., `landslide`, `mudslide`, `debris_flow`, `rock_fall`, `complex`).
11. `landslide_trigger` (string): Trigger cause (e.g., `rain`, `downpour`, `monsoon`, `tropical_cyclone`, `continuous_rain`, `earthquake`).
12. `landslide_size` (string): Qualitative size scale (`small`, `medium`, `large`, `very_large`, `catastrophic`).
13. `landslide_setting` (string): Environmental setting (`mine`, `above_road`, `steep_slope`, `urban`, `unknown`).
14. `fatality_count` (float): Number of recorded fatalities.
15. `injury_count` (float): Number of recorded injuries.
16. `storm_name` (string): Associated tropical cyclone or named storm.
17. `photo_link` (string): URL link to event photograph.
18. `notes` (string): Additional observer notes.
19. `event_import_source` (string): Import system provenance flag.
20. `event_import_id` (float): Import system record identifier.
21. `country_name` (string): Country name.
22. `country_code` (string): ISO 2-letter country code.
23. `admin_division_name` (string): State, province, or primary administrative division.
24. `admin_division_population` (float): Estimated population of nearest administrative division.
25. `gazeteer_closest_point` (string): Nearest named gazetteer landmark.
26. `gazeteer_distance` (float): Distance in kilometers to closest gazetteer landmark.
27. `submitted_date` (string): Date report was submitted to NASA catalog.
28. `created_date` (string): System creation timestamp.
29. `last_edited_date` (string): System last edited timestamp.
30. `longitude` (float): WGS84 longitude coordinate in decimal degrees.
31. `latitude` (float): WGS84 latitude coordinate in decimal degrees.

---

## 3. Project Variable Availability Matrix

In compliance with project scientific rules, variables are strictly audited against actual inspected columns without fabrication or artificial renaming:

| Required Framework Variable | Status in Raw Dataset | Available Column Name(s) | Description & Notes |
| :--- | :--- | :--- | :--- |
| **Landslide Event Flag / Label** | **AVAILABLE** | `event_id`, `landslide_category` | All records represent confirmed historical landslide events (`landslide_category` indicates type). |
| **Date / Time Information** | **AVAILABLE** | `event_date`, `event_time` | Date of occurrence available for temporal indexing. |
| **Geographic Location** | **AVAILABLE** | `latitude`, `longitude`, `country_name`, `admin_division_name` | Coordinates enable location-adaptive spatial modeling. |
| **Landslide Trigger Classification** | **AVAILABLE** | `landslide_trigger`, `storm_name` | Categorical trigger flags (`rain`, `monsoon`, `downpour`). |
| **Continuous Daily Precipitation (mm)** | **UNAVAILABLE DIRECTLY** | *None in raw CSV* | Raw dataset lists trigger category (`rain`), but not numerical daily precipitation values (mm/day). |
| **Continuous Soil Moisture (%)** | **UNAVAILABLE DIRECTLY** | *None in raw CSV* | Volumetric soil moisture sensor readings are not included in raw event catalog. |
| **Terrain Slope Angle (°) & Elevation (m)** | **UNAVAILABLE DIRECTLY** | *None in raw CSV* | Raw dataset contains spatial coordinates (`lat`/`lon`), but not DEM slope/elevation channels directly. |

---

## 4. Temporal Limitations & Strategy for Later Phases

> **REPORT ON DATASET TEMPORAL LIMITATION FOR LEAD-TIME EVALUATION**:
>
> 1. **Event-Only Bias**: The raw NASA Global Landslide Catalog is an **event catalog** containing positive landslide occurrences. It does **not** record continuous 365-day/year background non-event time series (days where no landslide occurred).
> 2. **Lack of Continuous Telemetry**: The raw file records the occurrence date, but does not provide continuous antecedent rainfall or soil moisture telemetry leading up to the event date.
> 3. **Integration Strategy for Subsequent Phases**: To construct the temporal early-warning framework, evaluate lead times, and compute false-alarm rates in future phases:
>    * Spatial-temporal joins will be performed using `latitude`, `longitude`, and `event_date` to link event records with continuous meteorological reanalysis streams (such as NASA GPM IMERG precipitation and ERA5 soil moisture) and DEM terrain data (SRTM / NASADEM).
>    * Processed feature matrices will be written strictly to `data/processed/`.
