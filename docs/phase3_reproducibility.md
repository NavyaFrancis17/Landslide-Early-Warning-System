# Phase 3 Reproducibility & Metadata Protocol

## 1. Provenance & Versioning

* **Environmental Reanalysis Provider**: ECMWF ERA5-Land Reanalysis (via Open-Meteo Archive API)
* **Landslide Source Catalog**: NASA Global Landslide Catalog (`data/raw/Global_Landslide_Catalog_Export.csv`)
* **Pipeline Script**: `build_feature_matrix.py`
* **Output Feature Matrix**: `data/processed/event_environment_features.csv`
* **Metadata Output Directory**: `data/environmental/metadata/`

---

## 2. Configurable Hyperparameters & Constants

* `EARTH_RADIUS_KM`: `6371.0088 km` (WGS84 IUGG Standard)
* `max_spatial_distance_km`: `50.0 km`
* `prediction_cutoff_hours`: `0 hours`
* `history_window_days`: `7 days` (`168 hours`)

---

## 3. Pre-Event Feature Calculation Formulas

1. `precipitation_1h` .. `168h`: $\sum_{k=0}^{\Delta h - 1} \text{precipitation}(t_{\text{event}} - k)$
2. `soil_moisture_layer1_current`: $\text{soil\_moisture\_0\_to\_7cm}(t_{\text{event}})$
3. `soil_moisture_layer1_change_24h`: $\theta_0(t_{\text{event}}) - \theta_0(t_{\text{event}} - 24\text{h})$
4. `soil_moisture_layer1_change_72h`: $\theta_0(t_{\text{event}}) - \theta_0(t_{\text{event}} - 72\text{h})$
