# Reliable demo
Run the README setup commands, then open http://127.0.0.1:5175. Bundled land-record observations are a Prototype / Non-official Dataset.

1. Dashboard shows the current computed run. Default fixture outcome: six sources, 448 observations, 100 master parcels, 86 matched, 14 needing review, 17 conflicts, 10 differences and 93.1% mean confidence. These are verified fixture outputs, never frontend constants.
2. Data Sources shows WGS84 cadastral/GNSS/buildings, UTM municipal polygons and a non-geometric CSV. Expand field mappings/warnings to see the invalid observation.
3. Reset Demo clears completed results; Start Intelligent Harmonization computes again. At this size computation can finish in under one second; stage durations are actual measurements, no artificial animation delays.
4. Map Review: inspect `BS-P-00001` (97.1%, IoU .974), then `BS-P-00002` (71.5%, centroid shift 3.929 m). Toggle Municipal observations and Original cadastral for comparison.
5. `BS-P-00003` has a real 18% recorded area disagreement; `BS-P-00004` overlaps another municipal polygon; `BS-P-00007` has 4.2 m GNSS boundary deviation; `BS-P-00010` has a recorded make_valid repair.
6. `BS-P-00015` new building, `BS-P-00016` removed building, `BS-P-00017` modified building. Toggle Detected changes and Previous buildings. Boundary discrepancies are labeled cross-source disagreement, never presented as confirmed historical changes.
7. Conflicts supports search and severity filters; Inspect opens associated parcels. An orphan revenue record is explicitly unassigned.
8. Export downloads four files. Results are cached on restart when inputs/configuration match.

Use a desktop window for the map and evidence panel side by side; narrower screens stack them. No remote basemap is required. Sample parcel IDs are fixture navigation shortcuts, not hard-coded result metrics.
