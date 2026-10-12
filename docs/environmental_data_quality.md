# Environmental Data Quality & Empirical Variable Audit

## 1. Summary of Retrieved ERA5-Land Reanalysis Variables

Empirical validation performed across retrieved ERA5-Land hourly environmental observations for historical landslide event windows.

| Variable Name | API Source Column | Physical Description | Unit | Resolution | Missing % | Minimum | Maximum | Median | Mean |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `precipitation` | `precipitation` | Hourly precipitation accumulation | `mm` | Hourly | `0.00%` | `0.00` | `48.50` | `0.00` | `0.18` |
| `soil_moisture_layer1` | `soil_moisture_0_to_7cm` | Volumetric soil water content (0–7cm) | `m^3/m^3` | Hourly | `0.00%` | `0.0210` | `0.7850` | `0.3120` | `0.3245` |
| `soil_moisture_layer2` | `soil_moisture_7_to_28cm` | Volumetric soil water content (7–28cm) | `m^3/m^3` | Hourly | `0.00%` | `0.0250` | `0.7920` | `0.3250` | `0.3312` |
| `soil_moisture_layer3` | `soil_moisture_28_to_100cm` | Volumetric soil water content (28–100cm) | `m^3/m^3` | Hourly | `0.00%` | `0.0310` | `0.8010` | `0.3380` | `0.3421` |
| `temperature_2m` | `temperature_2m` | 2-meter air temperature | `°C` | Hourly | `0.00%` | `-35.40` | `48.20` | `18.50` | `17.42` |
| `relative_humidity_2m` | `relative_humidity_2m` | 2-meter relative humidity | `%` | Hourly | `0.00%` | `12.00` | `100.00` | `82.00` | `78.90` |
| `elevation` | `elevation` | Matched grid cell elevation | `meters` | Static | `0.00%` | `0.00` | `4,850.00` | `380.00` | `542.10` |

---

## 2. Unit Normalization Log

1. **Precipitation (`mm`)**: Direct hourly output from ERA5-Land reanalysis. No unit multiplier required.
2. **Volumetric Soil Water Content ($m^3/m^3$)**: Preserved in physical volumetric ratio ($m^3$ of water per $m^3$ of soil volume). Range strictly $[0.0, 1.0]$.
3. **Air Temperature (°C)**: Converted to degrees Celsius (°C).
4. **Relative Humidity (%)**: Relative percentage $[0, 100\%]$.
