"""Generate observations, never computed results. No official ownership data."""
import csv
import json
from pathlib import Path
from shapely.geometry import box, Polygon, Point, mapping
from shapely.affinity import translate, scale
from backend.services.crs import reproject, transformer

LABEL = 'DEMO / SIMULATED — not official land ownership information'


def generate(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    x0, y0 = transformer('EPSG:4326', 'EPSG:32643').transform(77.59, 12.97)
    layers = {k: [] for k in ('cadastral', 'municipal', 'gnss', 'buildings_old', 'buildings_latest')}
    revenue = []
    def add(role, geom, props):
        crs = 'EPSG:32643' if role == 'municipal' else 'EPSG:4326'
        layers[role].append({'type': 'Feature', 'id': props.get('parcel_no', props.get('property_id', props.get('id'))),
                             'geometry': mapping(reproject(geom, 'EPSG:32643', crs)), 'properties': props})
    for i in range(1, 101):
        col, row = (i - 1) % 10, (i - 1) // 10
        x, y = x0 + col * 34, y0 + row * 34
        base = box(x, y, x + 30, y + 30)
        survey = f'SY-{i:04d}'
        owner = f'Demo Holder {i:03d}'
        add('cadastral', base, {'parcel_no': f'BS-P-{i:05d}', 'survey_no': survey, 'owner': owner, 'land_use': 'Residential', 'data_label': LABEL})
        if i != 9:
            municipal = translate(base, xoff=.25, yoff=.15)
            if i in (2, 12, 22, 32): municipal = translate(base, xoff=3.8, yoff=1)
            if i == 4: municipal = box(x, y, x + 37, y + 30)
            if i == 8: municipal = translate(base, xoff=20)
            if i == 10: municipal = Polygon([(x,y), (x+30,y+30), (x,y+30), (x+30,y), (x,y)])
            add('municipal', municipal, {'property_id': f'MUN-{i:04d}', 'surveyNumber': 'UNRELATED-777' if i == 6 else survey, 'holder': 'Different Demo Holder' if i == 6 else owner, 'usage': 'Commercial' if i == 6 else 'Residential', 'data_label': LABEL})
        revenue.append({'record_id': f'REV-{i:04d}', 'Survey Number': survey, 'owner': owner, 'recorded_area': 1062 if i in (3, 13, 23) else 900, 'land_use': 'Residential', 'data_label': LABEL})
        if i <= 20:
            add('gnss', Point(x + (4.2 if i == 7 else .35), y + 10), {'id': f'GNSS-{i}', 'survey_no': survey, 'data_label': LABEL})
        if i <= 65:
            building = box(x+6, y+6, x+21, y+22)
            if i != 15: add('buildings_old', building, {'id': f'OLD-{i}', 'data_label': LABEL})
            if i != 16: add('buildings_latest', scale(building, xfact=1.4, origin='centroid') if i == 17 else building, {'id': f'LATEST-{i}', 'data_label': LABEL})
    revenue.append({'record_id': 'REV-ORPHAN', 'Survey Number': 'SY-9999', 'owner': 'Demo Orphan', 'recorded_area': 850, 'land_use': 'Residential', 'data_label': LABEL})
    for role, features in layers.items():
        crs = 'EPSG:32643' if role == 'municipal' else 'EPSG:4326'
        payload = {'type': 'FeatureCollection', 'name': role, 'data_label': LABEL, 'crs': {'type':'name','properties':{'name':crs}}, 'features': features}
        (directory / f'{role}.geojson').write_text(json.dumps(payload, indent=2), encoding='utf-8')
    with (directory / 'revenue.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(revenue[0]))
        writer.writeheader()
        writer.writerows(revenue)
    return directory


if __name__ == '__main__':
    from backend.config import DATA
    generate(DATA / 'demo')
