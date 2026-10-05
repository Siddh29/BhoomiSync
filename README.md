# BhoomiSync

Local prototype for **SIH26013: Automated Integration and Intelligent Harmonization of Multi-source Geospatial Data for Urban Land Record Management**.

BhoomiSync aligns heterogeneous parcel observations, computes spatial and attribute matches, flags conflicts, compares building epochs and produces a traceable master cadastral layer. The parcel records are explicitly simulated; calculations run on their geometry. The integrated atlas uses real ward geometry, the survey uses the supplied imagery, and external environmental data carries its provenance. No government ownership information or evaluation accuracy is claimed.

## Setup and run
Prerequisites: Python 3.12+ with pip and Node.js 22.12+ with npm on Windows, macOS or Linux. From a terminal in the cloned repository:
```powershell
npm ci
npm run setup
npm run dev
```
Open http://127.0.0.1:5175. API docs: http://127.0.0.1:8001/docs. Keep the terminal running. Ctrl+C stops both processes. No API keys or database services are required. Street/satellite basemaps and external weather/soil/infrastructure providers use the internet; local ward geometry, survey imagery, harmonization and saved records remain available offline. Python packages live in this project's `.venv`; setup never touches sibling repositories.

The commands are the same in PowerShell, Command Prompt, macOS Terminal and Linux shells. `npm ci` installs the checked-in lockfile; `npm run setup` creates a project-local Python environment, installs the pinned geospatial dependencies and generates the deterministic parcel fixtures. On Debian/Ubuntu, install Python development and virtual-environment support first if they are missing (`python3-venv`). Use a fresh clone or run `npm run setup` again after changing the Python lockfile.

`npm run setup` creates the virtual environment, installs backend dependencies and generates six demo source files. Startup computes a run or loads an input-fingerprinted SQLite snapshot. Root `npm run dev` starts FastAPI and Vite together. `npm run reset-demo` resets a running server; the UI also has Reset Demo. Start Intelligent Harmonization genuinely runs the pipeline again.

## Integrated land intelligence studio (v2)

The workspace now combines Bengaluru-UrbanScope, Landroid and kv in BhoomiSync: a 3D city atlas with 243 real ward polygons, spatial clusters and exploratory hotspots; local survey imagery, RGB zones and candidate crowns; calibrated GeoTIFF upload and cross-acquisition analysis; weather history, site comparison and location search; soil/infrastructure context; saved case decisions, document hashes, audit events, field tasks, geofences and a local resource catalog.

Start on **Mission Control**. The **Demo director** guides nine scenes with a timer. For the four-minute SIH recording, use [docs/FOUR_MINUTE_DEMO.md](docs/FOUR_MINUTE_DEMO.md). The uploaded sample note is in [docs/demo-kit/field-verification-note.txt](docs/demo-kit/field-verification-note.txt). Full capability coverage and data limits are in [docs/INTEGRATED_FEATURES.md](docs/INTEGRATED_FEATURES.md).

Street maps use OpenFreeMap vector styles with attribution; satellite maps use Esri. DataMeet ward geometry is an imported snapshot. Bengaluru cadastral records remain explicitly synthetic, and Kallapuram is a separate real-imagery study area. Missing calibrated DEM, historical NDVI and trained model files are not replaced by invented results. Local officer/analyst/viewer personas demonstrate roles rather than production authentication.

## Features and stack
Python/FastAPI/Pydantic; SQLite snapshots; Shapely STRtree and geometry repair; PyProj projected calculations; RapidFuzz normalized attribute evidence. React/Vite and native MapLibre offer offline vector map layers, hover, picking, selected outlines and source toggles. Reports download from local endpoints. Rules and thresholds live in `backend/config.py`.

Dashboard metrics derive from the completed run. The bundled grid contains 100 parcels, shifted municipal polygons, an invalid polygon, overlaps, revenue area disagreement, an orphan record, GNSS deviation, and new/removed/modified buildings. Confidence is an explainable heuristic evidence index. Master geometry retains the cadastral source; observations and repair provenance remain inspectable.

## Structure
```
backend/api/          REST endpoints and validated uploads
backend/core/         Pydantic contracts
backend/demo/         deterministic fixture generator
backend/services/     ingestion, CRS, attributes, topology, matching,
                      pipeline, changes, confidence, exports and run manager
backend/storage/      repository interface and SQLite implementation
backend/tests/        geometry, pipeline and API acceptance tests
backend/data/demo/    generated source observations
backend/data/exports/ current completed run reports
frontend/src/         dashboard, map review, source cards, conflicts and exports
scripts/              cross-platform setup, backend and demo reset
docs/                 audit, design, algorithm and demo documentation
```

## Demo
Dashboard → Data Sources → Start Intelligent Harmonization → Map Review → select a clean and a review parcel → Conflicts → Export. See [DEMO.md](DEMO.md) and [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md).

## Custom observations
Demo mode defaults to true. For isolated user uploads stop the server and run:
```powershell
$env:BHOOMISYNC_DEMO_MODE='false'
npm run dev
```
Data Sources then exposes an upload form. Supply cadastral GeoJSON first, municipal GeoJSON and revenue CSV, optionally GNSS and both building epochs. Explicit source CRS is required (GeoJSON declared CRS or upload CRS); no blind CRS inference. Uploads up to 10 MB replace a role in `backend/data/raw`. Required cadastral geometry must contain unique IDs and usable polygons. Aliases are documented in `services/attributes.py`. Unsupported formats (Shapefile/GPKG) require conversion to GeoJSON. Optional bad sources are reported as rejected. No authentication is implemented: both servers bind loopback for local prototype use.

`.env.example` documents shell variables; the backend intentionally does not auto-load `.env`. Vite API prefix defaults to `/api`; its target uses `BHOOMISYNC_API_URL`. If changing `BHOOMISYNC_PORT`, also set `BHOOMISYNC_API_URL` to the matching loopback URL.

## Validation
```powershell
npm test
npm run build
```
Production build writes `frontend/dist`; `npm run preview --workspace frontend` serves it on port 4175 with the API proxy (backend still required). Backend tests cover CRS/units, known IoU and shifts, one-to-one matching, missing signals, attributes, repair, overlaps, demo determinism, building changes, missing sources, uploads, caching, reruns and export responses.

## API
Health/datasets, demo load/reset, run/status, result summary/parcels/conflicts/changes, layers and export downloads under `/api`. See [docs/API_CONTRACT.md](docs/API_CONTRACT.md). All counters are computed. Source audit and adaptation decisions: [docs/SOURCE_AUDIT.md](docs/SOURCE_AUDIT.md).

## Limitations
No legal adjudication, calibrated ML, global assignment optimizer, Shapefile/GPKG loader, raster tiles, utility network harmonization, area-of-interest gap checks or PostGIS. Raster metadata is optional and requires Rasterio. Geometry repair forces review. See [docs/LIMITATIONS.md](docs/LIMITATIONS.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
