from shapely import make_valid, STRtree
from shapely.geometry import MultiPolygon
from shapely.validation import explain_validity
from backend.config import OVERLAP_MIN_SQM


def repair(geometry):
    if geometry.is_valid and not geometry.is_empty:
        return geometry, []
    reason = explain_validity(geometry)
    fixed = make_valid(geometry)
    if fixed.geom_type == 'GeometryCollection':
        pieces = [g for g in fixed.geoms if g.geom_type in ('Polygon', 'MultiPolygon') and g.area > 0]
        polygons = [p for g in pieces for p in (g.geoms if g.geom_type == 'MultiPolygon' else [g])]
        fixed = MultiPolygon(polygons) if polygons else fixed
    return fixed, [{'operation': 'make_valid', 'reason': reason, 'valid_after': fixed.is_valid, 'output_type': fixed.geom_type}]


def overlaps(geometries):
    tree = STRtree(geometries)
    results = []
    for i, geom in enumerate(geometries):
        for j in tree.query(geom, predicate='intersects'):
            j = int(j)
            if j <= i:
                continue
            area = geom.intersection(geometries[j]).area
            if area > OVERLAP_MIN_SQM:
                results.append((i, j, area, geom.equals(geometries[j])))
    return results
