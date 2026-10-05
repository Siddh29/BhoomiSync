# SIH video script (2:50)
**0:00–0:15 — Problem.** Dashboard: “Urban land data lives in different agency systems. Boundaries, identifiers and recorded areas often disagree. BhoomiSync turns those observations into a traceable master layer.”

**0:15–0:30 — Sources.** Data Sources: “These six simulated sources exercise real algorithms. Municipal polygons are UTM, cadastral and GNSS are WGS84, revenue is tabular. Metadata and renamed fields are detected.”

**0:30–0:50 — Run.** Reset Demo, Start Intelligent Harmonization: “We validate, reproject, index spatial candidates, map attributes, detect conflicts and compare building epochs. Stage durations come from actual backend processing.” The small pipeline may complete quickly; explain the stages after completion.

**0:50–1:25 — Clean parcel.** Map Review, select BS-P-00001: “97.1% evidence score comes from polygon overlap, a 0.29 m centroid shift and matching attributes. GNSS agreement is measured in metres. Sources remain traceable.” Toggle cadastral/municipal.

**1:25–1:55 — Review evidence.** BS-P-00002: “A 3.93 m deviation lowers the score to 71.5%.” BS-P-00003: “Recorded revenue area differs by 18%; review is required even though spatial matching is strong.” Optionally show repaired BS-P-00010.

**1:55–2:15 — Changes.** Enable Detected changes; select BS-P-00015 then BS-P-00016: “Comparing old and latest building vectors identifies a new and a removed structure. Agency boundary disagreements are separately labeled, since they do not prove a historical change.”

**2:15–2:35 — Master and review.** Conflicts filter CRITICAL, Inspect a parcel: “Conflicts have measured evidence and a recommendation. Cadastral geometry is retained until survey review; no unverified legal boundary is silently substituted.”

**2:35–2:50 — Output.** Export: “Download master GeoJSON, conflict and change CSVs and the computed run summary. This local prototype needs no cloud accounts or keys. It demonstrates explainable harmonization, with human verification for difficult records.”
