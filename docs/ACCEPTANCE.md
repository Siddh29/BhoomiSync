# Executed acceptance checks
Verified 2026-10-05 on Windows, Python 3.12.4 / Node 22.12.0. Only BhoomiSync application files were created/edited. Sibling projects were read for audit only.

- `npm install`: completed; dependencies subsequently upgraded to Vite 6.4.3 / MapLibre 6.12.0 to resolve registry audit findings.
- `npm run setup`: executed successfully; cross-platform bootstrap uses verified requirements.lock.txt and regenerates fixtures. Initial .venv creation and dependency installation also completed.
- `npm run dev`: started FastAPI on loopback 8001 and Vite on 5175. Fresh startup computed observations; subsequent restart loaded the SQLite snapshot.
- `npm test`: 14 passed. One upstream Starlette TestClient deprecation warning about httpx remains; tests execute correctly.
- `npm run build`: production build succeeds. Map renderer is lazy loaded. MapLibre chunk exceeds 500 kB; this is an existing bundler size warning, not a compilation failure.
- `npm audit`: zero vulnerabilities after dependency updates.
- Backend tests: exact CRS roundtrip/900 m² area, analytic IoU and 2 m shift, area ratio, missing signal renormalization, one-to-one candidates, alias normalization and suggestions, bow-tie repair, overlaps, conflict thresholds, deterministic pipeline, six source roles, all required demo scenarios, optional source errors, reset/rerun/cache, upload validation and attachment responses.
- Live summary endpoint: six sources, 448 observations, 100 parcels, 86 matched, 10 review status, 4 low-confidence status, 14 needing review in total, 17 conflict records, 10 differences, 93.1% mean confidence.
- Browser: dashboard values populated from API; reset cleared results; Start Intelligent Harmonization reported actual stages and completed; map rendered locally; click selected BS-P-00002 with 71.5% confidence/3.93 m shift and tooltip; source/change/GNSS toggles reflected their checked state; BS-P-00015/16 displayed new/removed building; conflict search AREA_MISMATCH returned three measured 18% discrepancies; GeoJSON export downloaded successfully.
- API tests verify all four exports and inspect nonempty GeoJSON/CSV output. Exports live in backend/data/exports.
- Browser source comparison screenshot saved as docs/map-review.jpg. Narrow and desktop layouts inspected. No network basemap is needed.
- Production preview at port 4175: API proxy returned completed results and the bundled module worker rendered local parcel/building layers successfully.

Not claimed: optional Rasterio metadata extraction against a real GeoTIFF, raster tiles, trained model accuracy, legal cadastral adjudication or production deployment. See LIMITATIONS.md.
