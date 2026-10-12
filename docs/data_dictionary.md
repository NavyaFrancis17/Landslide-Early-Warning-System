# Data Dictionary — Sample Environmental Data Schema

> **DISCLAIMER**:
> **SYNTHETIC DEMONSTRATION DATA — NOT REAL OBSERVATION DATA**
> This data schema and accompanying synthetic sample dataset are created exclusively for software pipeline architecture validation in Phase 1. They do not represent physical sensor readings or actual geographic locations.

---

## Field Specifications

| Field Name | Category | Expected Type | Unit / Format | Description | Unit Dependence Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `date` | Historical / Temporal | String (ISO 8601) | `YYYY-MM-DD` | Date of environmental observation. | Standard calendar format. |
| `location_id` | Metadata / Spatial | String | Identifier string | Unique identifier for a specific geographic monitoring location/zone. | Schema-dependent string identifier. |
| `latitude` | Spatial | Float | Decimal degrees (°N/S) | WGS84 latitude coordinate of monitoring station. | Standard geographic coordinate. |
| `longitude` | Spatial | Float | Decimal degrees (°E/W) | WGS84 longitude coordinate of monitoring station. | Standard geographic coordinate. |
| `rainfall_1d` | Environmental | Float | Millimeters (mm) | Total accumulated precipitation measured over 24 hours. | *Depends on deployment dataset resolution (e.g., mm/day vs mm/hr aggregated).* |
| `soil_moisture` | Environmental | Float | Percentage (%) | Volumetric soil water content. | *Depends on sensor calibration (volumetric water content % vs degree of saturation).* |
| `temperature` | Environmental | Float | Degrees Celsius (°C) | Ambient surface air temperature. | *Depends on sensor unit calibration (°C vs K vs °F).* |
| `humidity` | Environmental | Float | Percentage (%) | Relative atmospheric humidity. | Percentage relative humidity (0–100%). |
| `elevation` | Physical / Spatial | Float | Meters (m) | Terrain elevation above mean sea level. | *Depends on DEM source (e.g., SRTM / NASADEM in meters).* |
| `slope` | Physical / Spatial | Float | Degrees (°) | Terrain slope inclination angle. | Calculated from DEM elevation gradient in degrees (0–90°). |
| `landslide_event` | Event Indicator | Integer / Boolean | `0` or `1` | Binary flag indicating historical recorded occurrence of a landslide event on this date at this location (`1` = Event, `0` = No Event). | Ground-truth historical label. |

---

## Summary of Field Categorization

1. **Temporal & Spatial Metadata**: `date`, `location_id`, `latitude`, `longitude`, `elevation`, `slope`
2. **Dynamic Environmental Measurements**: `rainfall_1d`, `soil_moisture`, `temperature`, `humidity`
3. **Historical Event Record**: `landslide_event`
