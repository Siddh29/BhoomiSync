# Integrated workspace verification

Verified locally on Windows, 5 October 2026. This is a runnable SIH demonstration prototype, not a certified government land-record system.

## Automated checks

- `npm test`: **26 passed**. Core geometry/matching tests plus real ward data, survey coverage, run-scoped review persistence, document integrity, viewer mutation guards, geofence transitions, field-task validation, GeoTIFF nodata handling, raster comparison, environmental cache behavior, CSV forecasting and resource reservations.
- `npm run build`: successful Vite production build, 1,954 modules. The lazy-loaded MapLibre bundle produces a size warning; it does not prevent building or running.
- `.venv/Scripts/python.exe -m pip check`: no broken requirements. Dependency lock updated for the geospatial/raster packages used by setup.

## Working browser checks

Both the development app on port 5175 and production preview on port 4175 were exercised. Layouts were inspected at 1366x768, 1440x900 and 1920x1080. Full-HD Mission Control has no horizontal page overflow.

| Flow | Observed result |
|---|---|
| Mission / atlas | Real MapLibre basemap, 243 ward polygons, 3D index, ward search/selection, hotspots, four clusters, rankings, regression and Lorenz/Gini views |
| Harmonization | All nine stages completed; 448 observations, 100 master parcels, 86 matched, 14 requiring review, 17 issues, 10 differences; 93.1% mean evidence confidence |
| Parcel comparison | BS-P-00002 shows 71.5% evidence confidence and 3.93 m boundary disagreement; source outlines and linked evidence inspected |
| Survey | Supplied Kallapuram RGB tiles, vegetation zones, five candidate crowns and 71.1% boundary coverage displayed |
| Raster upload / history | Actual RGB GeoTIFF imported and previewed; weather history converted to an elapsed-day regression forecast |
| Environment | Actual dated Open-Meteo data, two-site comparison, optional infrastructure context, explicit unavailable soil state |
| Case / evidence | Review decision saved for the current run; supplied demo note uploaded; SHA-256 verification returned intact |
| Field operations | Geofence initial-inside and exited transitions persisted; verification task moved to in progress; RTK resource reserved |
| Viewer persona | Mutation controls disabled; backend harmonization request returned 403 |
| Export | Browser downloaded a valid GeoJSON FeatureCollection containing 100 parcels; complete evidence bundle and print-ready report returned successfully |
| Demo director | All nine scenes navigated on the final build; timer, minimize and final disabled Next control verified |
| Restart | Completed run, uploaded document, saved geofence, task and resource survived API restart |

Final completed run at handoff: `3bb58ac4ef15`. The app can produce a new identifier when the presenter runs harmonization. Save the review against that new run during recording; older decisions remain in the audit history.

During rebuilding, an already-open production tab briefly referenced a removed lazy chunk. Reloading the completed build resolved it; the subsequent nine-scene traversal produced no new console errors. The API and development server were restarted before final verification.

## Recording kit

- Follow `FOUR_MINUTE_DEMO.md` for the narration and shot timings.
- `demo-kit/field-verification-note.txt` is explicitly labeled demonstration evidence.
- `demo-kit/kallapuram-orthomosaic.tif` is a georeferenced RGB conversion of the supplied tiles, not fabricated NDVI or elevation.
- `demo-kit/screenshots/` contains Mission Control, city atlas, parcel comparison, survey and evidence-vault proof images.

The recording itself has not been generated. Real NDVI/DEM acquisitions, production authentication, official cadastral connectors and deployment credentials remain external inputs. The feature coverage and precise limitations are documented in `INTEGRATED_FEATURES.md`.
