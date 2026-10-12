# Feature Inventory & Column Classification Table

All 31 columns in `data/raw/Global_Landslide_Catalog_Export.csv` are categorized and audited below based on NASA dataset documentation and scientific suitability for machine learning (Phase 3+).

---

## Column Inventory Table

| Column Name | Category | Data Type | Missing % | Use for ML Modeling? | Use for Temporal Analysis? | Excluded? | Reason for Exclusion / Usage Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `event_id` | Identifier | `int64` | `0.00%` | **NO** | **NO** | **EXCLUDE** | Primary key identifier; non-predictive. |
| `event_date` | Temporal | `object` | `0.00%` | **NO** | **YES** | **TRANSFORM** | Parsed into `event_datetime`, `event_year`, `event_month`, `event_day`, `event_day_of_year`, `season`. |
| `event_time` | Temporal | `float64` | `100.00%` | **NO** | **NO** | **EXCLUDE** | 100% missing values across all records. |
| `event_title` | Descriptive Metadata | `object` | `0.00%` | **NO** | **NO** | **EXCLUDE** | Free-text headline; non-predictive narrative. |
| `event_description` | Descriptive Metadata | `object` | `7.81%` | **NO** | **NO** | **EXCLUDE** | Unstructured free-text description. |
| `source_name` | Metadata | `object` | `0.00%` | **NO** | **NO** | **EXCLUDE** | Reporting agency name; administrative metadata. |
| `source_link` | Metadata | `object` | `7.67%` | **NO** | **NO** | **EXCLUDE** | Web URL reference link. |
| `location_description` | Location Info | `object` | `0.92%` | **NO** | **NO** | **EXCLUDE** | Unstructured place name string. |
| `location_accuracy` | Spatial Metadata | `object` | `0.02%` | **YES** | **NO** | **RETAIN** | Spatial confidence radius (`exact`, `1km`, `5km`, `10km`, `unknown`). Useful for filtering high-precision subset. |
| `landslide_category` | Event Info | `object` | `0.01%` | **TARGET/LABEL** | **YES** | **RETAIN** | Landslide classification (`landslide`, `mudslide`, `debris_flow`, `rock_fall`). |
| `landslide_trigger` | Environmental / Cause | `object` | `0.21%` | **YES** | **YES** | **RETAIN** | Event trigger category (`rain`, `downpour`, `monsoon`, `continuous_rain`, `earthquake`). |
| `landslide_size` | Event Outcome | `object` | `0.08%` | **NO (LEAKAGE)**| **NO** | **EXCLUDE FROM INPUTS** | Outcome severity scale (`small`, `medium`, `large`, `catastrophic`). Target/severity label only; cause data leakage if used as input. |
| `landslide_setting` | Geological / Setting | `object` | `0.63%` | **YES** | **NO** | **RETAIN** | Site setting (`mine`, `above_road`, `steep_slope`, `urban`, `unknown`). |
| `fatality_count` | Event Outcome | `float64` | `12.55%` | **NO (LEAKAGE)**| **NO** | **EXCLUDE FROM INPUTS** | Post-event casualty metric; causes severe target leakage. |
| `injury_count` | Event Outcome | `float64` | `51.43%` | **NO (LEAKAGE)**| **NO** | **EXCLUDE FROM INPUTS** | Post-event casualty metric; causes severe target leakage. |
| `storm_name` | Environmental | `object` | `94.77%` | **NO** | **NO** | **EXCLUDE** | High missingness (94.8%); named tropical storms. |
| `photo_link` | Metadata | `object` | `86.44%` | **NO** | **NO** | **EXCLUDE** | URL to photo artifact; non-predictive. |
| `notes` | Descriptive Metadata | `object` | `97.13%` | **NO** | **NO** | **EXCLUDE** | High missingness (97.1%); free-text notes. |
| `event_import_source` | Metadata | `object` | `14.17%` | **NO** | **NO** | **EXCLUDE** | System ingestion tag (`glc`, `nasa_coolr`). |
| `event_import_id` | Metadata | `float64` | `14.16%` | **NO** | **NO** | **EXCLUDE** | Ingestion database identifier. |
| `country_name` | Location Info | `object` | `14.16%` | **YES** | **NO** | **RETAIN** | Country name for regional stratification. |
| `country_code` | Location Info | `object` | `14.18%` | **YES** | **NO** | **RETAIN** | ISO 2-letter country code. |
| `admin_division_name` | Location Info | `object` | `14.84%` | **YES** | **NO** | **RETAIN** | State / province division name. |
| `admin_division_population` | Location / Demographics | `float64` | `14.16%` | **YES** | **NO** | **RETAIN** | Numerical population density indicator of administrative zone. |
| `gazeteer_closest_point` | Location Info | `object` | `14.17%` | **NO** | **NO** | **EXCLUDE** | Gazetteer landmark name. |
| `gazeteer_distance` | Location Info | `float64` | `14.16%` | **YES** | **NO** | **RETAIN** | Distance in km to gazetteer landmark. |
| `submitted_date` | Metadata | `object` | `0.09%` | **NO** | **NO** | **EXCLUDE (LEAKAGE)**| Date report submitted to database; post-event administrative timestamp. |
| `created_date` | Metadata | `object` | `0.01%` | **NO** | **NO** | **EXCLUDE (LEAKAGE)**| Database creation timestamp; post-event administrative timestamp. |
| `last_edited_date` | Metadata | `object` | `0.00%` | **NO** | **NO** | **EXCLUDE (LEAKAGE)**| Database edit timestamp; post-event administrative timestamp. |
| `longitude` | Geographic | `float64` | `0.00%` | **YES** | **YES** | **RETAIN** | Spatial longitude coordinate in decimal degrees. |
| `latitude` | Geographic | `float64` | `0.00%` | **YES** | **YES** | **RETAIN** | Spatial latitude coordinate in decimal degrees. |
