# Migration map
| Target feature | Source repo/file | Decision | Target | Changes |
|---|---|---|---|---|
| Map selection | Bengaluru-UrbanScope/frontend/src/App.jsx | ADAPT concept | frontend/src/components/MapView.jsx | Native MapLibre, flat parcels, local style |
| Persistence | Bengaluru-UrbanScope/backend/main.py | ADAPT concept | backend/storage/repository.py | Snapshot repository rather than ward SQL |
| Overlay controls | kv/src/components/Map/MapWrapper.tsx | ADAPT concept | frontend/src/components/MapView.jsx | React state, no globals |
| CRS cache | Landroid/backend/routers/tiles.py | ADAPT concept | backend/services/crs.py | Analysis and display transforms |
| Raster metadata | Landroid/backend/utils/raster.py | ADAPT pattern | backend/services/ingestion.py | Local metadata only, optional dependency |
| Engine/data | None | REIMPLEMENT | backend/services and backend/demo | New parcel-specific code |

No source code or source datasets are copied. Source repositories remain read-only.
