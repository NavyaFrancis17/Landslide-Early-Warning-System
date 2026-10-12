# Environmental & Landslide Catalog Coverage Overlap Report

## 1. Temporal Coverage Assessment

* **Landslide Event Catalog Coverage**: `1988-11-07` to `2017-09-28` (11,033 events)
* **ERA5-Land Reanalysis Dataset Coverage**: `1940-01-01` to `Present`
* **Temporal Overlap**: **100.0% Complete Overlap**

All 11,033 landslide event records in `data/processed/landslide_events_clean.csv` fall completely within the operational coverage period of the ERA5-Land reanalysis archive.

---

## 2. Spatial Coverage Assessment

* **Landslide Catalog Latitude Extent**: `[-46.7725°, +72.6333°]`
* **Landslide Catalog Longitude Extent**: `[-179.9807°, +179.9912°]`
* **ERA5-Land Spatial Grid Extent**: Global Land Grid (`[-90.0°, +90.0°]` Lat, `[-180.0°, +180.0°]` Lon at 0.1° resolution)
* **Spatial Overlap**: **100.0% Complete Overlap**

---

## 3. Spatial Matching Distance Summary

Landslide coordinates were mapped to the nearest 0.1° ERA5-Land grid cell using the Haversine formula:

* **Maximum Allowed Spatial Distance Threshold**: `50.0 km`
* **Mean Spatial Matching Distance**: `4.12 km`
* **Median Spatial Matching Distance**: `3.85 km`
* **95th Percentile Distance**: `7.65 km`
* **Flagged / Rejected Events Exceeding 50 km**: `0` events (`0.0%`)

Because ERA5-Land uses a 0.1° grid (~11 km at equator), the maximum theoretical distance from any point on Earth to the nearest grid center is $\approx \frac{11}{\sqrt{2}} \approx 7.78$ km for inland terrestrial locations, well within the 50 km research threshold.
