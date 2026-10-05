# Frontend redesign verification

## Delivered interface

Map Review is the default screen. A 200 px navigation rail, 54 px workspace bar and 46 px map context bar frame a full-height map with a 344 px parcel inspector. The inspector owns its scroll; the desktop body does not scroll. Grouped layers, source comparison, parcel search/previous/next, zoom, fit, focus and reset operate on the real MapLibre map. Thin semantic boundaries and neutral fills preserve the supplied geometries. The grid is still synthetic; no roads, satellite imagery or survey context were invented.

The other five screens use compact tables, aligned fields and separators: source registry with mappings pane; a measured nine-stage pipeline; overview with one metrics strip, source health and review queue; searchable and filtered conflict register; export artifact table and real run metadata. Segoe UI, Lucide, four-pixel corners, tabular numerals and shared tokens replace the previous card system.

## Changed files and components

- Rewritten: `frontend/src/App.jsx`, `frontend/src/main.jsx`, `frontend/src/components/RunProgress.jsx`.
- New shell: `frontend/src/app/{AppShell,Sidebar,WorkspaceBar}.jsx`.
- New pages: `frontend/src/pages/{Overview,Sources,Harmonization,MapReview,Conflicts,Export}.jsx`.
- New map components: `frontend/src/features/map/{MapCanvas,MapToolbar,LayerManager,ParcelSelector,ParcelInspector}.jsx`, `layers.js`.
- New support: `frontend/src/hooks/useWorkspace.js`, `frontend/src/api/presentation.js`, `frontend/src/features/datasets/UploadForm.jsx`, `frontend/src/components/{StatusIndicator,SectionHeader,EmptyState}.jsx`.
- New styling: `frontend/src/styles/{tokens,globals}.css`.
- Removed unused predecessors: `frontend/src/styles.css`, `frontend/src/components/{MapView,ParcelDetails}.jsx`.
- Dependency: `frontend/package.json` and root `package-lock.json` add Lucide React.
- Documentation: `FRONTEND_REDESIGN_AUDIT.md`, `DESIGN_SYSTEM.md`, this report, and seven verification screenshots in this directory.

Preserved without changes: API request client, Vite proxy and ESM worker configuration, React/MapLibre stack, all endpoint contracts, dataset roles, upload multipart contract, all four export routes. Existing screen behavior was carried into the new components. No backend components were rewritten.

## Verification evidence

The baseline build passed before work. The final `npm run build` also passes. Vite retains its MapLibre chunk-size warning (approximately 1.06 MB before gzip); the map renderer and worker remain separate lazy-loaded assets.

Development server: `127.0.0.1:5175`. Built production preview: `127.0.0.1:4175`. Both load and display the backend snapshot. Clean verification tabs report no console warnings or errors. Installation-time Vite dependency refresh and map hot-refresh errors occurred during implementation; a clean reload and guarded map effects resolved them before verification.

| Flow | Observed result |
|---|---|
| All six screens | Loaded real source/result data and operational empty states |
| Run Harmonization | Disabled run/reset while active; polled real stage progress; completed and refreshed snapshot |
| Reset demo | Cleared the completed snapshot; production displayed “No completed master layer”; a subsequent run restored results |
| Direct map click | Clicked visible parcel 00003; search field, outline and inspector changed to 00003 |
| Parcel search and next | Selected 00002 by ID; next selected 00003 and corresponding revenue area evidence |
| Evidence / Records / Provenance | Measured fields, canonical/source records, candidate score and raw provenance disclosure verified |
| Layers / comparison | Reference, GNSS, previous-building and change overlays toggled; master layer hidden/restored; comparison enabled source boundaries |
| Map tools | Zoom in/out, fit all, focus selected, reset view changed the live map |
| Conflict search | Search for 00002 returned one issue with its 3.93 m boundary measurement |
| Severity filter | Critical filter returned three of seventeen issues |
| Conflict row | Opened Map Review with 00002 selected; focus reached zoom 20 |
| Source registry | Six measured roles; municipal warning; correct source-to-canonical field direction |
| Custom upload | Separate temporary data directory and unmodified backend modules on 8002; UI on 5176 uploaded bundled cadastral GeoJSON using the file chooser; registry changed from Missing to Ready with 100 valid polygons and EPSG:4326 |
| Export | Production UI downloaded master GeoJSON; all four production proxy export URLs returned HTTP 200 with nonempty files |

The custom upload check used disposable runtime data, without switching the main server's mode or editing demo files. No user records were uploaded. The temporary servers were stopped after verification.

## Desktop map layout

Measured actual rendered DOM dimensions, rather than inferring them from a resized screenshot:

| Viewport | Body height / scroll height | Map canvas | Inspector |
|---|---|---|---|
| 1366 × 768 | 768 / 768 | 822 × 668 | 344 px allocated width |
| 1440 × 900 | 900 / 900 | 896 × 800 | Own scroll region 553 px tall, content 915 px |
| 1920 × 1080 | 1080 / 1080 | 1376 × 980 | Fixed width; remaining width goes to map |

Screenshots: `redesign-map-review-1366.png`, `redesign-map-review-1440.png`, `redesign-map-review-1920.png`, `redesign-sources.png`, `redesign-conflicts.png`, `redesign-pipeline.png`, `redesign-overview.png`.

## Backend freeze

Backend files changed: **NONE**. All 21 Python/dependency files under `backend` match their pre-redesign SHA-256 hashes, including routes, schemas, algorithms, fixture generator and tests. UI run/reset naturally changed runtime snapshots and generated outputs through existing endpoints. Source datasets still produce 100 parcels, 86 matched, 14 needing review, 17 conflict records, 10 changes and 93.1% mean evidence confidence.

## Remaining limits

- Offline neutral coordinate backdrop; geographic context requires real basemap data. Synthetic parcel geometry is deliberately unchanged.
- No approval, resolution, legal verification or invented timestamps: those actions/metadata are absent from the frozen backend.
- Upload retains current backend GeoJSON/CSV support and explicit CRS requirements. One GeoJSON ingest was exercised through the UI; all other upload roles retain the same request contract but were not individually uploaded.
- Compact desktop is the verified target. Narrow layouts collapse navigation and overlay the inspector; touch-device UX has not received equivalent acceptance testing.
- Navigation is local UI state; browser history/deep links and cross-tab synchronization are not provided. Reload to refresh a snapshot changed in another tab.
- Eight layers remain available; the selected parcel highlight intentionally stays visible when the master layer is hidden so the current inspection remains legible.

### Follow-up identity pass

Added `frontend/src/styles/identity.css`; refined `app/Sidebar.jsx` and loaded the identity styles in `main.jsx`. `pages/MapReview.jsx` adds the daylight/night control and actual snapshot counts; `features/map/MapCanvas.jsx` applies corresponding semantic paint values. Geometry, data contracts and backend source remain unchanged (21 hashes verified again).

Verified night/day switching, municipal visibility, parcel 00002 evidence, fit-all and overview rendering. At 1366 × 768 the body remains 768 px high with no overflow, and the map remains 822 × 668. Clean console during these checks. Production build passes with the existing MapLibre size warning. Preview: `identity-night-map.png`. The previous screenshots document the earlier visual pass.
