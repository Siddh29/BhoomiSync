# SIH26013 integrated workspace

The user's latest request expands the earlier frontend-only boundary. Work remains inside BhoomiSync; Bengaluru-UrbanScope, Landroid and kv are read-only references. A recovery archive is saved under `.recovery/before-integration.zip`.

## Source audit and integration map

| Source | Implemented capability found | Integrated destination |
|---|---|---|
| Bengaluru-UrbanScope | MapLibre basemap, tilted/extruded wards, growth proxy, clusters, significance, rank lists, regression, Gini/inequality | City Atlas and mission landing view |
| Landroid | Raster overlays, boundary handling, green-index watershed canopy detection, zones, health, valuation factors, trends | Survey Lab and Environmental Intelligence |
| Landroid | Documents, geofence checks, role-oriented views | Records & Review and Field Operations, persisted in SQLite |
| Landroid | English/Tamil navigation, account views | Local demo personas and translated navigation |
| Landroid | Marketplace and employment screens contain sample UI | Local resource/task board, explicitly demo records; no transaction or job application claims |
| kv | Orthomosaic tiles and EPSG:32643 boundary | Copied sample survey assets, reprojected boundary with provenance |
| kv | Weather, moisture, pH, risks, crop rules, charts, two-location comparison | Environmental Intelligence with actual cached API values, input provenance and explicit unavailable signals |
| BhoomiSync | Six-source harmonization, matching, confidence, conflict/change detection and exports | Preserved core pipeline, map investigation, sources and exports |

## Data findings

- UrbanScope has source code but no local processed ward dataset. Its DataMeet URL fallback returns 243 ward features; this snapshot is imported with attribution. Ward value/growth is a synthetic morphology/accessibility proxy, not transaction data or observed temporal growth.
- Landroid's `data` directory contains only `.gitkeep`. Its raster/NDVI/DEM and trained model files are missing. Do not report its fallback numbers as measurements.
- kv contains ten real orthomosaic tiles (zooms 12–18), six very small DEM tiles and a UTM LineString boundary. The boundary must be reprojected before display. Missing elevation metadata means its tiny DEM tiles cannot support an elevation claim.
- kv estimates an NDVI-like number from weather and seeds random time series. The integrated product must not label this as measured NDVI. RGB vegetation is explicitly identified as RGB; true NDVI requires red/NIR raster bands or a supplied NDVI raster.
- Landroid's document store is in memory and geofences rely on client-supplied prior state. The integrated version uses persistent records and server-held per-rule transitions.
- Firebase sign-in requires deployment credentials. Local demo personas are visibly labeled and must not be described as production identity verification.

## Four-minute narrative

City context → six-source ingestion → real harmonization → boundary disagreement investigation → imagery/canopy evidence → reviewer decision and audit trail → export. Environmental analysis and field operations provide depth without distracting from land-record harmonization. Presentation mode guides this sequence with a timer and keyboard navigation.

## Completion checks

Build and core regression tests; dedicated tests for imported city statistics, image geometry/coverage, rules/persistence and document paths; browser checks for all new pages, actual tile rendering, geofence transition, review persistence, downloads and the complete presentation sequence. Document any remaining gaps precisely.
