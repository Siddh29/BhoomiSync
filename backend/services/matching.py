import math
from shapely import STRtree
from backend.config import WEIGHTS, CANDIDATE_RADIUS_M, AMBIGUITY_MARGIN
from backend.services.attributes import attribute_similarity


def geometry_metrics(a, b):
    union = a.union(b).area
    centroid = a.centroid.distance(b.centroid)
    boundary = a.boundary.hausdorff_distance(b.boundary)
    return {'iou': a.intersection(b).area / union if union else 0,
            'centroid_distance_m': centroid, 'boundary_distance_m': boundary,
            'area_similarity': min(a.area, b.area) / max(a.area, b.area) if max(a.area, b.area) else 0,
            'proximity': math.exp(-centroid / 5), 'shape_similarity': math.exp(-boundary / 5)}


def weighted_score(metrics):
    available = [(metrics[k], w) for k, w in WEIGHTS.items() if metrics.get(k) is not None]
    return 100 * sum(v * w for v, w in available) / sum(w for _, w in available) if available else 0


def match(base, municipal):
    tree = STRtree([r['geometry'] for r in municipal])
    ranked, candidates = [], {}
    for i, parcel in enumerate(base):
        options = []
        for j in tree.query(parcel['geometry'].buffer(CANDIDATE_RADIUS_M)):
            j = int(j)
            m = geometry_metrics(parcel['geometry'], municipal[j]['geometry'])
            m['attribute_similarity'] = attribute_similarity(parcel['attributes'], municipal[j]['attributes'])
            score = weighted_score(m)
            if m['iou'] > 0 or m['centroid_distance_m'] <= CANDIDATE_RADIUS_M:
                options.append((score, j, m))
                ranked.append((score, i, j, m))
        candidates[i] = sorted(options, key=lambda x: (-x[0], x[1]))
    assigned, used = {}, set()
    for score, i, j, metrics in sorted(ranked, key=lambda x: (-x[0], x[1], x[2])):
        if i in assigned or j in used or score < 30:
            continue
        options = candidates[i]
        ambiguous = len(options) > 1 and options[0][0] - options[1][0] < AMBIGUITY_MARGIN
        assigned[i] = {'index': j, 'score': score, 'metrics': metrics, 'ambiguous': ambiguous,
                       'candidates': [{'source_id': municipal[k]['id'], 'score': round(s, 3)} for s, k, _ in options]}
        used.add(j)
    return assigned, [j for j in range(len(municipal)) if j not in used]
