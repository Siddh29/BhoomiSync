# Demo data
**This dataset is generated for prototype demonstration and does not represent official land ownership information.** All holder names are synthetic.

`python -m backend.demo.generate_demo_data` produces byte-identical observations each time. No random values or final scores are stored. Origin: 77.59 E, 12.97 N, transformed to EPSG:32643. 10x10 grid, 30 m square parcels, 34 m spacing.

| Source | Count | CRS | Construction |
|---|---|---|---|
| cadastral | 100 | EPSG:4326 | projected base polygons transformed for display |
| municipal | 99 | EPSG:32643 | .25/.15 m shift by default; parcel 9 absent |
| revenue | 101 | no geometry | 100 exact survey joins and one orphan |
| GNSS | 20 | EPSG:4326 | points .35 m inside west boundary, parcel 7 at 4.2 m |
| buildings_old | 64 | EPSG:4326 | buildings on parcels 1–65 except parcel 15 |
| buildings_latest | 64 | EPSG:4326 | buildings on parcels 1–65 except parcel 16; parcel 17 enlarged |

Parcel 2/12/22/32 municipal shift 3.8/1 m; parcel 4 enlarged to 37 m width creates neighboring overlap; parcel 8 shifts 20 m, creating a missing/ambiguous assignment scenario; parcel 10 is a bow-tie polygon requiring repair. Parcel 6 attributes differ. Revenue areas for 3/13/23 are 1062 vs 900 m². Building footprints are 15x16 m; latest footprint 17 has 1.4x width. The absence of parcel 9 does not necessarily leave master 9 unmatched because geometric candidates can disagree with explicit source numbering; provenance exposes the actual assignment.

Grid spacing represents unmodeled roads/space and is not automatically classified as cadastral gaps. These controlled scenarios exercise genuine algorithms. Existing source repo outlines were unsuitable for multi-source parcel evidence and were not copied.
