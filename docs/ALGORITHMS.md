# Algorithms
All algorithms are deterministic heuristics, not trained AI models or measured prediction accuracy.

CRS: cache PyProj always_xy transforms. Select UTM zone from the first cadastral parcel's WGS84 centroid. All area/distance calculations occur in projected metres. Suitable for a compact Bengaluru extent; wide/global datasets need an extent-aware projection policy. Original geometry and source CRS remain in provenance; display/export use EPSG:4326. Missing CRS is rejected with a visible warning; optional rejected sources are skipped, while cadastral input is mandatory.

Attribute mapping: normalized field aliases map automatically. Unrecognized fields get RapidFuzz suggestions above .70 without applying them. Survey joins remove punctuation/whitespace and case; missing identifiers never join to each other. Revenue area must be finite and positive. Duplicate revenue joins create review evidence.

Spatial candidates: municipal STRtree queried by cadastral polygon buffered 12 m. Plausible candidates intersect or have centroid separation <=12 m. Compute IoU = intersection/union, area ratio = min/max, centroid distance and boundary Hausdorff distance. Proximity and shape signals use exp(-distance/5). Attribute similarity averages available survey, owner and land-use normalized fuzzy ratios. No absent attribute gets a fabricated value.

Matching: weights IoU .45, proximity .20, area .15, shape .10, attributes .10; renormalize available weights. Globally order candidate pairs by score and enforce one-to-one greedy assignment; reject scores below 30. Candidate score margin below 5 forces ambiguity review. This is not the optimal assignment solution and cannot resolve splits/merges.

Topology: make_valid only on invalid/empty observations; retain original geometry and operations. Non-polygon output is excluded from parcel roles. Detect positive overlaps above .1 m² with STRtree, exact duplicate geometry and slivers below 1 m². Repair and overlap issues force review. No automatic neighbor boundary adjustment. Roads/spacing are not labeled gaps without an authoritative coverage AOI.

Conflicts: Hausdorff distance >2 m, revenue area difference >5% relative to cadastral area, attribute similarity <.8, GNSS distance to cadastral boundary >2 m, overlaps, invalid repairs, ambiguity and unmatched observations. GNSS joins survey IDs; without IDs, nearest polygon within 2 m is associated and recorded. GNSS distance measures boundary agreement, not certified instrument accuracy.

Confidence: weighted score minus unique issue penalties (invalid/overlap/duplicate 12, area/GNSS/attribute 8, unmatched 12, ambiguity 10), clipped 0–100. >=85 with no issue = MATCHED; 60–85 or any issue = REVIEW_REQUIRED; <60 = CONFLICT. Thresholds are configured. Master geometry always remains cadastral; only accepted evidence marks auto_harmonized. This score is not a calibrated probability.

Changes: old/latest footprint candidates are indexed and greedily assigned by descending IoU >=.3; matched IoU <.9 = MODIFIED_BUILDING, unmatched latest = NEW_BUILDING, unmatched old = REMOVED_BUILDING. Missing epoch skips change detection, avoiding false removals. Largest footprint/parcel intersection assigns the parcel. Cadastral/municipal boundary differences are labeled PARCEL_BOUNDARY_DISAGREEMENT; dates do not establish temporal parcel change.

Dashboard: input_features counts all original observations (including CSV rows); matched counts accepted master parcels; needs_review includes review and low confidence; conflicts counts records, so several may refer to one parcel; changes includes three building changes plus boundary disagreements; success_rate = matched/all cadastral parcels. A master record being generated does not imply its legal accuracy.
