# Environmental Dataset Source & Metadata Specification

## 1. Primary Environmental Dataset Identification

* **Dataset Name**: ERA5-Land Hourly Reanalysis
* **Provider / Origin**: European Centre for Medium-Range Weather Forecasts (ECMWF) / Copernicus Climate Change Service (C3S)
* **Access Platform / Archive API**: Open-Meteo ERA5 Reanalysis Archive (`https://archive-api.open-meteo.com/v1/archive`)
* **Data Type**: Gridded Land Surface Reanalysis (Atmospheric & Land Hydro-meteorology)
* **Spatial Resolution**: `0.1° x 0.1°` (approximately `11 km x 11 km` grid cell spacing at the Equator)
* **Temporal Resolution**: Hourly (`1-hour` intervals)
* **Coverage Period**: `1940-01-01` to `Present`
* **Geographic Extent**: Global Land Surface Coverage (`90°N` to `90°S`, `180°W` to `180°E`)
* **Licensing & Attribution Requirements**:
  * Copernicus Climate Change Service (C3S) Open Data License
  * Attribution Statement: *"Contains modified Copernicus Climate Change Service information [2026]. Neither the European Commission nor ECMWF is responsible for any use that may be made of the information."*

---

## 2. Variables Audited & Extracted

| Framework Variable | API Column Name | Physical Meaning | Source Unit | Conversion Applied | Output Feature Unit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Precipitation** | `precipitation` | Hourly accumulated rainfall | `mm/hr` | *None (Preserved)* | `mm` |
| **Soil Moisture (Layer 1)** | `soil_moisture_0_to_7cm` | Volumetric soil water content (0–7 cm depth) | `m^3/m^3` | *None (Preserved)* | `m^3/m^3` |
| **Soil Moisture (Layer 2)** | `soil_moisture_7_to_28cm` | Volumetric soil water content (7–28 cm depth) | `m^3/m^3` | *None (Preserved)* | `m^3/m^3` |
| **Soil Moisture (Layer 3)** | `soil_moisture_28_to_100cm` | Volumetric soil water content (28–100 cm depth) | `m^3/m^3` | *None (Preserved)* | `m^3/m^3` |
| **Air Temperature** | `temperature_2m` | Ambient 2-meter air temperature | `°C` | *None (Preserved)* | `°C` |
| **Relative Humidity** | `relative_humidity_2m` | 2-meter relative humidity | `%` | *None (Preserved)* | `%` |
| **Surface Elevation** | `elevation` | Topographic grid elevation above sea level | `meters` | *None (Preserved)* | `meters` |

---

## 3. Data Ingestion & Authentication Mechanism

* **API Endpoints**: Public HTTPS API (`https://archive-api.open-meteo.com/v1/archive`)
* **Credential Requirements**: Publicly accessible open data service. No API keys required for research usage.
* **Security Rule**: In compliance with security standards, any custom token or private proxy setting is loaded strictly via environment variables (`ERA5_API_KEY`, `OPENMETEO_PROXY`) and is never committed to code repositories.
