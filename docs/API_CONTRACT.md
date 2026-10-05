# API contract
Loopback API on port 8001, OpenAPI at /docs. JSON responses; errors have `detail` and HTTP status. Typed Parcel/Issue contracts in `backend/core/schemas.py`.

| Method | Path | Result |
|---|---|---|
| GET | /api/health | service and demo mode |
| GET | /api/datasets | live metadata, field mappings, CRS transforms and warnings |
| POST | /api/datasets/upload | multipart file, role, optional explicit crs; custom mode only |
| GET | /api/datasets/raster-metadata | optional local optional.tif metadata or warning |
| POST | /api/demo/load | source metadata and current status |
| POST | /api/demo/reset | regenerate fixtures and clear completed result |
| POST | /api/harmonization/run | `{ "force": true }`, start actual background run |
| GET | /api/harmonization/status | IDLE/RUNNING/COMPLETED/FAILED, stages, measured durations, error |
| GET | /api/results/summary | computed counters, analysis CRS, warnings and run ID |
| GET | /api/results/parcels | typed canonical parcels |
| GET | /api/results/parcels/{parcel_id} | evidence, conflicts, changes, provenance |
| GET | /api/results/conflicts | conflict records (unassigned parcel_id may be null) |
| GET | /api/results/changes | vector changes and cross-source boundary disagreements |
| GET | /api/layers/{layer_name} | WGS84 FeatureCollection |
| GET | /api/export/harmonized.geojson | harmonized_parcels.geojson attachment |
| GET | /api/export/conflicts.csv | conflicts.csv attachment |
| GET | /api/export/changes.csv | change_report.csv attachment |
| GET | /api/export/summary.json | run_summary.json attachment |

Layers: cadastral, municipal, harmonized, buildings_old, buildings_latest, gnss, conflicts, changes. Unknown parcel/layer/export =404. No completed run or blocked mutation =409. Invalid upload =422; oversize =413. Source replacement invalidates the cache. During rerun readers retain the preceding completed snapshot. Single-worker local service only.
