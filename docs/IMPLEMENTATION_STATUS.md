# Implementation status
| Feature | Status | Evidence / scope |
|---|---|---|
| Phase 0 source audit | DONE | Source modules inspected before application code |
| Phase 1 architecture/data model/migration map | DONE | Actual simplified module boundaries documented |
| Phase 2 FastAPI skeleton/config/logging | DONE | Live health and OpenAPI |
| Phase 3 deterministic demo sources | DONE | Six generated files; reproducibility test |
| Phase 4 ingestion, CRS and indexed matching | DONE | Known projected area/shift, STRtree and one-to-one tests |
| Phase 4 topology checks | DONE | Validity, overlap, duplicates, slivers; warnings |
| Automatic topology correction | PARTIAL | make_valid with originals retained, review required |
| Coverage gaps | TODO | Requires authoritative coverage AOI |
| Phase 5 attributes/conflicts/confidence/changes/master | DONE | Evidence thresholds and tested scenarios |
| Phase 6 result and layer APIs | DONE | Typed responses, unknown ID handling and run/status |
| Phase 7/8 frontend integration | DONE | Six screens, map selection/toggles, evidence and filters |
| Phase 9 exports | DONE | Four generated files; endpoint tests and browser download |
| Phase 10 tests and stabilization | DONE | 14 backend tests; production build; zero npm audit vulnerabilities |
| Phase 11 documentation/demo script | DONE | README, architecture, algorithm/limitations and 2:50 script |
| Custom uploads | DONE | GeoJSON/CSV only; explicit CRS; isolated non-demo raw files |
| Raster support | PARTIAL | Metadata adapter; optional Rasterio dependency, tiles deferred |
| Advanced trained ML | NOT REQUIRED | Explainable deterministic heuristics instead |
| Utility/DSM/DTM/drone processing | NOT REQUIRED FOR DEMO | Future integration |
| PostGIS/OGC/distributed workers | FUTURE | Repository boundary exists, no required services |

Demo-only components: generated grid and source observations. Computation, API, persistence, UI and exports are real. No final score is hard-coded. See ACCEPTANCE.md for executed checks and remaining warnings.
