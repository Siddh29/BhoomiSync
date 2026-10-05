# ""c: four-minute SIH26013 recording

Open http://127.0.0.1:5175. Use a 1920×1080 or 1440×900 browser window at 100% zoom. Leave the terminal running. Start on **Mission Control**, with the **Officer / editor** persona and English navigation.

Rehearse once with **Demo director** in the sidebar. Start its timer and use **Next scene**. **Alt+Right / Alt+Left** move between scenes; **Escape** closes the director. Minimize it for recording, or close it and follow the timings below. The timer guides you; it does not simulate actions.

## Before pressing Record

1. Visit Mission Control, City Atlas, Map Review and Survey Lab once to load the map assets. Return to Mission Control.
2. Confirm the top bar says **Complete** and Map Review contains **100 parcels**. Run Harmonization if needed. Do not press Reset demo during recording.
3. Keep `docs/demo-kit/field-verification-note.txt` available in the file picker. It is explicitly demonstration evidence.
4. In Case Desk, use **BS-P-00002**, **Request field verification**, and this short note: `DEMO REVIEW: Verify the 3.93 m municipal boundary disagreement using an RTK survey. Retain cadastral geometry pending officer review.`
5. Check that the laptop is plugged in and silence unrelated notifications. Use your normal screen recorder; a recorded video has not been generated automatically.

## Shot-by-shot run

| Time | On-screen action | Suggested narration |
|---|---|---|
| 0:00–0:20 | Mission Control, show the 3D Bengaluru hero | “Different agencies describe the same land in different coordinate systems and schemas. BhoomiSync combines those observations into one explainable workspace for SIH26013: automated integration and intelligent harmonization of urban land records.” |
| 0:20–0:45 | City Atlas → Hotspots → Clusters; click a ward or search Whitefield | “We begin with real geography: 243 imported Bengaluru ward boundaries, rendered in MapLibre. We can inspect spatial clusters and local concentration patterns. These colors are clearly labeled calculated indicators, so the system never presents a proxy as an official land price.” |
| 0:45–1:05 | Sources; select municipal row and show EPSG:32643 plus field mappings | “Our land-record demonstration has six source roles: cadastral, municipal, revenue, GNSS and two building epochs. The registry exposes format, coordinate reference system, quality and mappings. These parcel records are synthetic fixtures; all the calculations you see are performed on their geometry.” |
| 1:05–1:30 | Click Run Harmonization; show nine completed stages and summary | “The engine validates inputs, reprojects geometry, normalizes attributes, checks topology, finds spatial candidates, detects conflicts and changes, and scores the evidence. The result is 100 master parcels from 448 observations: 86 matched, 14 requiring review and 17 measurable issues.” |
| 1:30–2:05 | Map Review → Find parcel `BS-P-00002` → Source comparison → focus selection → evidence tab | “For this parcel, the municipal boundary disagrees with the cadastral survey by 3.93 metres. The confidence drops to 71.5 percent. We can compare the actual source outlines and inspect overlap, centroid distance, GNSS evidence and the reason for review. The system retains the cadastral geometry and asks for human survey verification.” |
| 2:05–2:35 | Survey Lab → Vegetation zones → canopy toggle | “We also integrated the survey capabilities of Landroid and kv. This separate Kallapuram sample has real local RGB imagery, a reprojected survey boundary, vegetation zones and five candidate crowns. The interface reports 71.1 percent imagery coverage. RGB greenness is explicitly distinguished from NDVI; calibrated NDVI and elevation GeoTIFFs can be uploaded and compared.” |
| 2:35–3:20 | Case Desk → BS-P-00002 → save note → Evidence vault → Attach note → Verify → Audit timeline | “The officer turns evidence into a recorded decision. We request a field check and preserve the reasoning against this run. A supporting file is stored with a SHA-256 hash, and the Verify action checks its byte integrity. The audit timeline records who acted and when. These records survive a reload, connecting analysis to accountability.” |
| 3:20–3:45 | Field Ops → existing demo geofence → Test inside → Test outside, OR task board → move assignment | “Field operations close the loop. A saved geofence detects transitions using server-held state, and the field team can progress a verification assignment. The prototype uses manual test coordinates and local personas, with no claim of background GPS or production authentication.” |
| 3:45–4:00 | Exports → Download harmonized GeoJSON; show Complete evidence bundle / report | “Finally, we deliver interoperable GeoJSON, conflict and change reports, plus a complete evidence bundle. BhoomiSync combines the three projects into one traceable workflow: integrate, investigate, verify and act—while keeping the evidence and its limitations visible.” |

The timings are a target, not an enforced recording limit. At a moderate speaking pace this narration fits about four minutes; rehearse and shorten transitions rather than rushing the evidence scene.

## If you need to cut 20 seconds

Skip the file upload during recording and show the already uploaded note and its Verify action. Skip resource exchange, soil context, forecast scenarios and raster uploads in the primary film; they remain available for questions. Keep the 3.93 m conflict, saved decision and export scenes.

## Claims to keep precise

- “Explainable evidence confidence” is a heuristic, not a measured prediction accuracy.
- City geometry is real imported data; ward heights are a visualized proxy, not physical buildings or terrain.
- Bengaluru land records and the Kallapuram imagery are distinct study areas.
- Candidate crowns require field validation. The source projects supplied no calibrated DEM or historic NDVI dataset.
- Hash checks show file integrity, not legal ownership or authenticity.
- No selection or winning outcome is guaranteed by the software or this recording.
