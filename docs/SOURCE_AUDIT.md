# Source Repository Audit

Audit performed 2026-10-05, before implementation. All sources remain read-only. No application code has been copied. Paths below were verified on disk and important modules read.

## Bengaluru-UrbanScope
- Stack: React 18, Vite 5, deck.gl 9, react-map-gl/MapLibre; FastAPI, SQLite, PyProj, NumPy and statistical packages.
- Relevant files: `frontend/src/App.jsx` (GeoJsonLayer, hover/click and selected outline), `frontend/package.json`, `backend/main.py` (SQLite and cached GeoJSON), `backend/pipeline/build_dataset.py` (ward ingestion), `backend/scripts/setup.mjs`, `frontend/scripts/perf-benchmark.mjs`.
- Reusable modules: map selection and source/result layer concepts; local API and cached artifact architecture.
- Not relevant: property value, Gini, regression, ward clustering, 3D elevation animation.
- Risks: monolithic map tightly coupled to ward analytics; network download for base wards; ward polygons are not cadastral parcels. No verified multi-source parcel fixtures.
- Proposed adaptation: `frontend/src/App.jsx` interaction concept into `frontend/src/components/MapView.jsx`; `backend/main.py` local persistence concept into `backend/storage/repository.py`. Reimplement both rather than copying coupled code.

## kv
- Stack: root React 18/Vite/TypeScript/Leaflet, FastAPI/OpenCV raster API. Nested `krishi-map` is Next 16/React 19/Leaflet, not a separate source repo.
- Relevant files: `src/components/Map/MapWrapper.tsx`, `src/services/dataService.ts`, `api/index.py`, `src/pages/Dashboard.tsx`, `krishi-map/src/components/Map/MapWrapper.tsx`, `krishi-map/package.json`.
- Reusable modules: explicit independent overlay toggles and local tile fallback design.
- Not relevant: Open-Meteo/SoilGrids, agricultural health, vegetation contour tree counts, crop/weather charts.
- Risks: dashboard uses global window callback; root map centers Chennai; remote APIs undermine offline demo; incompatible nested React version. `krishi-map/AGENTS.md` applies only inside that untouched subtree.
- Data inventory: `public/boundary.geojson`, nested boundary copies, local tile directories. Boundary outlines and imagery do not provide related municipal/revenue/GNSS parcel observations.
- Proposed adaptation: toggle behavior from `src/components/Map/MapWrapper.tsx` into `frontend/src/components/MapView.jsx`; no direct source copying.

## Landroid
- Stack: FastAPI/Pydantic, Rasterio, Shapely, PyProj, NumPy/OpenCV; Flutter mobile and Firebase-related screens.
- Relevant files: `backend/main.py`, `backend/models/schemas.py`, `backend/utils/raster.py`, `backend/utils/geo.py`, `backend/utils/confidence.py`, `backend/routers/tiles.py`, `backend/tests/test_canopy.py`, `backend/services/parcel_registry.py`.
- Reusable modules: lifespan setup, typed API contracts, bounded raster reads, cached always_xy Transformers, explicit signal penalties and synthetic algorithm tests.
- Not relevant: NDVI/canopy, valuation, soil/rainfall, agricultural dashboards, mobile auth.
- Risks: geo helpers approximate geographic area and first rings; unsuitable for cadastral metric calculations. Tile router couples to parcel registry, NDVI colormaps and URL geometry fetching. Raster dependencies are heavy; no need to migrate full server.
- Data inventory: `mobile/assets/data/parcel.geojson` is a standalone parcel, not a multi-source urban dataset; data directory contains `.gitkeep`.
- Proposed adaptation: Transformer caching concept from `backend/routers/tiles.py` into `backend/services/crs.py`; Rasterio metadata pattern from `backend/utils/raster.py` into `backend/services/ingestion.py`; Pydantic and test concepts reimplemented.

## Final Reuse Decision
| Feature | Decision | Reason |
|---|---|---|
| Map interactions | ADAPT concepts | Fresh small MapLibre component; remove ward/agricultural coupling |
| Local persistence and API | ADAPT concepts | SQLite snapshot repository and FastAPI lifespan |
| Raster metadata | ADAPT pattern | Optional Rasterio; tiles deferred |
| CRS, indexing, matching, topology | REIMPLEMENT | New projected metric engine and STRtree |
| Attribute mapping, conflicts, confidence, changes | REIMPLEMENT | Parcel-specific explainable rules |
| Demo source data | REIMPLEMENT | Deterministic synthetic parcels, explicitly labeled |
| Existing analytics, mobile, cloud auth | IGNORE | Outside scope |
| Direct source code reuse | NONE | No independently suitable module without domain coupling |
