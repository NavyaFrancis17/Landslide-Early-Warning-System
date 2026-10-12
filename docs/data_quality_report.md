# Data Quality Audit Report — NASA Global Landslide Catalog

## 1. Executive Summary

This report documents the empirical data quality audit conducted on the raw NASA Global Landslide Catalog dataset (`data/raw/Global_Landslide_Catalog_Export.csv`). All metrics presented below are computed directly from the source dataset.

---

## 2. Dataset Key Metrics

* **Total Dataset Rows**: `11,033`
* **Total Dataset Columns**: `31`
* **Full Row Duplicates**: `0`
* **Duplicate Event Identifiers (`event_id`)**: `0`
* **Total Recorded Landslide Events**: `11,033`
* **Unique Geographic Coordinates (Lat/Lon Pairs)**: `10,895`
* **Unique Named Location Descriptions**: `10,700`

---

## 3. Temporal Coverage & Date Parsing Audit

* **Raw Date Field**: `event_date` (String object)
* **Successfully Parsed Event Dates**: `11,033` / `11,033` (`100.0%`)
* **Invalid / Unparseable / Missing Date Records**: `0` (`0.0%`)
* **Minimum Event Date**: `1988-11-07`
* **Maximum Event Date**: `2017-09-11`

> **Temporal Data Quality Note**:
> The `event_date` column in the raw export contains heterogeneous string formats (e.g. `08-01-2008 00:00` vs `11/20/2017 03:17:00 PM`). Using a multi-format mixed parser (`format="mixed"`), all 11,033 event date records were cleanly converted into standardized ISO datetimes and extracted into `data/processed/landslide_events_clean.csv` and `data/processed/landslide_events_temporal.csv`.

---

## 4. Geographic Coordinate Validation

* **Latitude Field**: `latitude` (Float64)
* **Longitude Field**: `longitude` (Float64)
* **Missing Latitude Values**: `0` (`0.0%`)
* **Missing Longitude Values**: `0` (`0.0%`)
* **Out-of-Range Latitudes (outside [-90°, +90°])**: `0` (`0.0%`)
* **Out-of-Range Longitudes (outside [-180°, +180°])**: `0` (`0.0%`)
* **Observed Latitude Range**: `[-46.7725°, +72.6333°]`
* **Observed Longitude Range**: `[-179.9807°, +179.9912°]`
* **Valid Spatial Coordinate Records**: `11,033` (`100.0%`)

---

## 5. Column-by-Column Missing Value Audit (All 31 Columns)

| Column Name | Data Type | Missing Count | Missing Percentage |
| :--- | :--- | :--- | :--- |
| `source_name` | `object` | `0` | `0.00%` |
| `source_link` | `object` | `846` | `7.67%` |
| `event_id` | `int64` | `0` | `0.00%` |
| `event_date` | `object` | `0` | `0.00%` |
| `event_time` | `float64` | `11,033` | `100.00%` |
| `event_title` | `object` | `0` | `0.00%` |
| `event_description` | `object` | `862` | `7.81%` |
| `location_description` | `object` | `102` | `0.92%` |
| `location_accuracy` | `object` | `2` | `0.02%` |
| `landslide_category` | `object` | `1` | `0.01%` |
| `landslide_trigger` | `object` | `23` | `0.21%` |
| `landslide_size` | `object` | `9` | `0.08%` |
| `landslide_setting` | `object` | `69` | `0.63%` |
| `fatality_count` | `float64` | `1,385` | `12.55%` |
| `injury_count` | `float64` | `5,674` | `51.43%` |
| `storm_name` | `object` | `10,456` | `94.77%` |
| `photo_link` | `object` | `9,537` | `86.44%` |
| `notes` | `object` | `10,716` | `97.13%` |
| `event_import_source` | `object` | `1,563` | `14.17%` |
| `event_import_id` | `float64` | `1,562` | `14.16%` |
| `country_name` | `object` | `1,562` | `14.16%` |
| `country_code` | `object` | `1,564` | `14.18%` |
| `admin_division_name` | `object` | `1,637` | `14.84%` |
| `admin_division_population` | `float64` | `1,562` | `14.16%` |
| `gazeteer_closest_point` | `object` | `1,563` | `14.17%` |
| `gazeteer_distance` | `float64` | `1,562` | `14.16%` |
| `submitted_date` | `object` | `10` | `0.09%` |
| `created_date` | `object` | `1` | `0.01%` |
| `last_edited_date` | `object` | `0` | `0.00%` |
| `longitude` | `float64` | `0` | `0.00%` |
| `latitude` | `float64` | `0` | `0.00%` |

---

## 6. Numerical Columns Summary Statistics

| Column Name | Minimum | Maximum | Mean | Median | Std Dev |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | `1.00` | `11,221.00` | `5,598.95` | `5,601.00` | `3,249.23` |
| `fatality_count` | `0.00` | `5,000.00` | `3.22` | `0.00` | `59.89` |
| `injury_count` | `0.00` | `374.00` | `0.75` | `0.00` | `8.46` |
| `admin_division_population` | `0.00` | `12,691,836.00` | `157,760.05` | `14,640.00` | `829,734.54` |
| `gazeteer_distance` | `0.00` | `215.45` | `11.87` | `7.05` | `15.60` |
| `longitude` | `-179.9807` | `+179.9912` | `2.5224` | `18.5991` | `100.9069` |
| `latitude` | `-46.7725` | `+72.6333` | `25.8821` | `27.8761` | `20.4208` |
