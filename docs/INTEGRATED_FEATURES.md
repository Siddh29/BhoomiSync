# Integrated feature coverage

All changes and copied assets are inside BhoomiSync. Bengaluru-UrbanScope, Landroid and kv remain intact. The starting project was backed up as `.recovery/before-integration.zip`.

| Source capability | Working implementation | Data / scope |
|---|---|---|
| UrbanScope MapLibre map, fly-to, picking, 2D/3D | City Atlas + Mission Control | 243 DataMeet ward polygons; vector OpenFreeMap street styles, Esri imagery, offline local geometry |
| Value/growth coloring | Spatial index and median-deviation mode | Area/accessibility proxy; no transaction prices or temporal growth claimed |
| K-means clusters | Four deterministic spatial clusters and filter | Standardized log index, deviation, area, distance and local spatial statistic |
| Local significance/hotspots | Exploratory Gi* mode with selected-ward z-score | Eight nearest neighbours plus self; normal approximation, uncorrected p<0.05 |
| Top/bottom rankings, scatter, regression | Searchable ranks, highest/lowest order, Patterns tab | Actual derived metrics; distance is already part of the proxy |
| Gini, Lorenz, shares | Patterns tab | Distribution of the proxy, not measured household wealth |
| Landroid/kv boundary + orthomosaic | Survey Lab, source boundary reprojection, local tile mosaic | EPSG:32643 → WGS84, partial coverage explicitly reported |
| Vegetation/plant zones | RGB zone overlays; calibrated uploaded NDVI zones | RGB greenness differentiated from NDVI |
| Canopy detection, small-crown flags | Threshold/morphology/distance-peak/watershed candidates | Five candidates in imported sample; size outliers not diagnosed disease |
| NDVI, DEM and ortho layers | GeoTIFF upload, reprojection, preview and statistics | User-provided calibrated rasters; missing source DEM is not fabricated |
| Cross-date raster analysis | Baseline/latest uploaded raster comparison | Shared WGS84 grid, valid overlap, change thresholds and exportable preview |
| Historic series and trend projection | Dated CSV explorer; actual saved weather series shortcut | OLS and approximate prediction interval; not an unavailable trained AI model |
| kv weather, moisture and risk indicators | Environment conditions, 30-day history, seven-day provider forecast | Open-Meteo dated responses cached locally; explicit outage state |
| Location selection + comparison | Place search, manual coordinates and two-site comparison | GeoNames via Open-Meteo; gridded weather estimates |
| Soil profile / pH | Soil & access tab; modeled provider values or manual scenario | ISRIC availability shown; no fallback “measured” pH |
| OSM proximity/context | 3 km nearby roads/water/amenities and GeoJSON export | Overpass representative feature centres; no false nearest-distance claim |
| Health/risk/crop rules | Transparent condition components, threshold alerts, crop scenarios | Exploratory rules with visible inputs; no agronomic diagnosis or yield claim |
| Valuation factors | Interactive weighted factor explorer | Hypothetical inputs, no monetary valuation presented as evidence |
| Geofences and alerts | Persistent circle fences, checks and transition stream | Manual coordinates, server-held previous state; no push/GPS claim |
| Document vault and verification | Upload, download, delete, stored hashes and verify | Persistent files + SQLite metadata; byte integrity only |
| Landowner/consultant/admin views | Local officer, analyst and viewer personas | Read-only viewer guards; production Firebase authentication not available |
| English/Tamil support | Translated navigation labels | Navigation translation, not a claim that every paragraph is localized |
| Marketplace / employment sample screens | Local resource exchange + field task board | Equipment/services/training catalog, reservation and assignment progression; no payment or external employment service |
| System insights | Overview, pipeline summary, API health and audit | Counts derive from actual local results and saved actions |
| BhoomiSync core | Six-source ingestion, nine-stage harmonization, source comparison, conflict/change evidence, exports | Original geometry calculations retained; bundled cadastral observations are synthetic |
| SIH recording flow | Mission Control + timed Demo director + print report | Nine-scene four-minute narrative; real actions are performed by the presenter |

## Scope that requires external assets or deployment work

The siblings do not contain usable Firebase credentials, a trained trend model, calibrated DEM/NDVI rasters or historic canopy acquisitions. The integration supplies working upload/analysis paths and explicit unavailable states instead of reporting fallback numbers as measurements. Production identity, official cadastral connectors, legally approved review processes, push notifications and public resource transactions remain deployment work.

The ward dataset is an imported snapshot and is not certified as the current administrative boundary version. OpenFreeMap/OSM and Esri require network access for basemaps; local geometry, imagery, harmonization and saved records work without those basemaps. Weather and other providers use dated caches when available.

## Attribution

- DataMeet Municipal Spatial Data: https://github.com/datameet/Municipal_Spatial_Data/tree/master/Bangalore
- OpenFreeMap / OpenMapTiles / OpenStreetMap: https://openfreemap.org/quick_start/
- Esri World Imagery attribution is displayed on satellite views.
- Open-Meteo and GeoNames are identified on weather/search responses.
- ISRIC SoilGrids and OpenStreetMap/Overpass are identified on optional site context.
- Local orthomosaic tiles and boundary are copied from the user's kv project; capture date and original imagery licensing were not supplied. Confirm the original asset rights before public distribution.
