from shapely import STRtree
from shapely.geometry import mapping
from backend.config import BUILDING_MATCH_IOU, BUILDING_UNCHANGED_IOU
from backend.services.crs import reproject


def building_changes(old, latest, parcels, analysis):
    tree = STRtree([r['geometry'] for r in latest])
    candidates, matched_old, matched_latest, result = [], set(), set(), []
    for i, before in enumerate(old):
        a = before['geometry']
        for j in tree.query(a):
            j = int(j)
            b = latest[j]['geometry']
            iou = a.intersection(b).area / a.union(b).area
            if iou >= BUILDING_MATCH_IOU: candidates.append((iou, i, j))
    parcel_tree = STRtree([p['geometry'] for p in parcels])
    def emit(kind, record, before=None, iou=None):
        geom = record['geometry']
        options = [(geom.intersection(parcels[int(k)]['geometry']).area, int(k)) for k in parcel_tree.query(geom)]
        index = max(options)[1] if options and max(options)[0] > 0 else None
        result.append({'id':f'CHANGE-{len(result)+1:04d}', 'type':kind,
            'parcel_id':parcels[index]['attributes'].get('parcel_id',parcels[index]['id']) if index is not None else None,
            'source_ids':{'current':record['id'], 'previous':before['id'] if before else None},
            'area_sqm':round(geom.area,3), 'iou':round(iou,4) if iou is not None else None,
            'description':kind.replace('_',' ').title() + ' from vector footprint comparison',
            'geometry':mapping(reproject(geom,analysis,'EPSG:4326'))})
    for iou, i, j in sorted(candidates, key=lambda c:(-c[0],c[1],c[2])):
        if i in matched_old or j in matched_latest: continue
        matched_old.add(i); matched_latest.add(j)
        if iou < BUILDING_UNCHANGED_IOU: emit('MODIFIED_BUILDING',latest[j],old[i],iou)
    for j, record in enumerate(latest):
        if j not in matched_latest: emit('NEW_BUILDING',record)
    for i, record in enumerate(old):
        if i not in matched_old: emit('REMOVED_BUILDING',record)
    return result
