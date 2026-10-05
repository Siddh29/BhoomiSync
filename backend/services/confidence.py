from backend.config import HIGH_CONFIDENCE, LOW_CONFIDENCE


def classify(score, issues, missing_municipal=False):
    penalties = {'TOPOLOGY_INVALID':12, 'PARCEL_OVERLAP':12, 'DUPLICATE_GEOMETRY':12, 'AREA_MISMATCH':8,
                 'GNSS_DEVIATION':8, 'ATTRIBUTE_MISMATCH':8, 'UNMATCHED_SOURCE':12, 'MULTIPLE_CANDIDATE_MATCH':10}
    confidence = round(max(0, min(100, score - sum(penalties.get(t,0) for t in {i['type'] for i in issues}))),1)
    requires_review = bool(issues) or missing_municipal
    status = 'CONFLICT' if confidence < LOW_CONFIDENCE else 'REVIEW_REQUIRED' if confidence < HIGH_CONFIDENCE or requires_review else 'MATCHED'
    return confidence, status
