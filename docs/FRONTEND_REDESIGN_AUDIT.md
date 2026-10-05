# Frontend redesign audit

Inspected 2026-10-05 before changing implementation. Backend frozen; SHA256 baseline captured for all 21 Python/requirements source files. Existing production build succeeds (MapLibre chunk-size warning). Current Map Review inspected live and against docs/map-review.jpg.

## Existing pages and components
App.jsx owns six conditional pages (Dashboard, Data Sources, Harmonization, Map Review, Conflicts, Export), fetch/state orchestration and upload form. MapView.jsx lazily imports MapLibre; ParcelDetails.jsx renders evidence; RunProgress.jsx renders real stage timings. api/client.js centralizes the API prefix and errors. styles.css is one dense global stylesheet.

## Working functionality and state dependencies
Health sets demo mode. Datasets/status load before completed results. Summary, parcels, conflicts, changes and eight layer FeatureCollections load together. Parcel ID joins map selection to inspector. A 250 ms status poll refreshes completed results. Reset clears results; run executes the existing API. Conflicts have search/severity filters and Inspect navigation. Uploads remain available outside demo mode. Four export attachment links work.

## API dependencies
GET /health, /datasets, /harmonization/status, /results/summary, /results/parcels, /results/conflicts, /results/changes, /layers/{name}. POST /harmonization/run, /demo/reset and /datasets/upload. GET /export/{filename}. These are relative to the existing /api client prefix. No new endpoint or schema is needed. No timestamps or approval/resolution persistence are supplied: the redesign must not fabricate those.

## UX and visual problems
The 224px sidebar, large heading and full-width green notice consume working space. Map has fixed 690px height and creates browser scrolling; inspector also scrolls. Saturated status fills make the unchanged synthetic grid look like a board game. Layer controls are ungrouped floating checkboxes, no fit/selection comparison tools. Large selector is detached from map tools. Inspector has one long undifferentiated definition list; source IDs and recommendations are hard to scan. Dashboard and source cards fragment parallel information and waste space. Icons are mixed Unicode. App.jsx mixes state, layout and all pages.

## Preserve
api/client.js endpoint configuration/error semantics; backend data flow and selection by parcel_id; MapLibre ESM worker integration, style readiness guard, WGS84 local geometry, hover/click handlers and lazy load. Source values, repair provenance, confidence, warnings, conflict/change output and original download routes.

## Rewrite
Application shell and all page presentation; map composition, grouped layers, toolbar and selector; inspector hierarchy; stage display; global styles. Separate fetch orchestration from presentation. All working interactions must remain.

## New frontend architecture
app/ owns shell/sidebar/workspace bar. hooks/useWorkspace.js owns existing calls and actual run progress. pages/ owns six focused screens. features/map/ owns canvas, toolbar, grouped layer manager and inspector. features/datasets/ owns uploads. components/ supplies status, section and empty-state primitives. styles/tokens.css and globals.css define one system. api/client.js stays intact; api/presentation.js formats existing values without recomputing GIS evidence.

Map Review is the default workstation: full viewport beneath a 52px workspace bar and 42px context toolbar; 200px navigation and 344px independently scrolling inspector. Neutral low-opacity polygons, semantic strokes, clear selection and dashed municipal reference. Local coordinate graticule is presentation-only, derived from displayed extent; no invented roads, imagery or changed parcel coordinates. No fake review approval buttons or resolved statuses.
