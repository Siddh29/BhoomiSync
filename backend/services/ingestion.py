import csv
import json
import math
from pathlib import Path
from pyproj import CRS
from shapely.geometry import shape, mapping
from backend.services.attributes import map_attributes
from backend.services.crs import reproject
from backend.services.topology import repair

ROLES = ('cadastral', 'municipal', 'revenue', 'gnss', 'buildings_old', 'buildings_latest')


def load_source(path, role, target_crs=None, explicit_crs=None):
    path = Path(path)
    warnings, records, mappings, suggestions = [], [], {}, {}
    if not path.exists():
        return [], {'id': role, 'name': role.replace('_',' ').title(), 'status': 'MISSING', 'warnings': ['Optional source unavailable'], 'feature_count': 0, 'format': path.suffix, 'crs': None, 'valid_geometry_count': 0}
    if path.suffix.lower() == '.csv':
        with path.open(encoding='utf-8-sig', newline='') as f:
            raw = list(csv.DictReader(f))
        crs, valid, bounds, types = None, 0, None, []
        for i, props in enumerate(raw):
            attrs, m, s = map_attributes(props)
            mappings.update(m); suggestions.update(s)
            value = attrs.get('recorded_area_sqm')
            if value is not None:
                try:
                    value = float(value)
                    if not math.isfinite(value) or value <= 0: raise ValueError()
                    attrs['recorded_area_sqm'] = value
                except (ValueError, TypeError):
                    attrs.pop('recorded_area_sqm', None)
                    warnings.append(f'Row {i+1}: invalid recorded area omitted')
            if not attrs.get('survey_number'): warnings.append(f'Row {i+1}: survey number absent; cannot join')
            records.append({'id': str(attrs.get('revenue_record_id', i)), 'attributes': attrs, 'raw_properties': props})
    else:
        payload = json.loads(path.read_text(encoding='utf-8-sig'))
        if payload.get('type') != 'FeatureCollection': raise ValueError('GeoJSON FeatureCollection required')
        raw = payload.get('features', [])
        crs = explicit_crs or payload.get('crs', {}).get('properties', {}).get('name')
        if not crs:
            raise ValueError(f'{path.name}: CRS missing. Supply explicit CRS; no coordinate guessing is performed.')
        try:
            crs = CRS(crs).to_string()
        except Exception as exc:
            raise ValueError(f'{path.name}: invalid CRS declaration: {crs}') from exc
        valid, types, all_bounds = 0, set(), []
        for i, feature in enumerate(raw):
            try:
                geom = shape(feature['geometry'])
                if geom.is_empty or not all(math.isfinite(v) for v in geom.bounds): raise ValueError('Empty or non-finite geometry')
                types.add(geom.geom_type); all_bounds.append(geom.bounds)
                valid += int(geom.is_valid)
                props = feature.get('properties') or {}
                attrs, m, s = map_attributes(props)
                mappings.update(m); suggestions.update(s)
                projected = reproject(geom, crs, target_crs) if target_crs else geom
                fixed, operations = repair(projected)
                expected = ('Point', 'MultiPoint') if role == 'gnss' else ('Polygon', 'MultiPolygon')
                if fixed.geom_type not in expected or fixed.is_empty or (role != 'gnss' and fixed.area <= 0):
                    raise ValueError(f'Expected {expected}, got {fixed.geom_type}')
                if operations: warnings.append(f'Feature {i}: geometry repaired; human review required')
                records.append({'id': str(feature.get('id') or attrs.get('parcel_id') or attrs.get('municipal_property_id') or props.get('id') or i),
                    'geometry': fixed, 'original_geometry': feature['geometry'], 'attributes': attrs,
                    'raw_properties': props, 'repairs': operations, 'source_crs': crs})
            except (ValueError, TypeError, KeyError) as exc:
                warnings.append(f'Feature {i} skipped: {exc}')
        bounds = [min(b[0] for b in all_bounds), min(b[1] for b in all_bounds), max(b[2] for b in all_bounds), max(b[3] for b in all_bounds)] if all_bounds else None
        types = sorted(types)
    return records, {'id':role, 'name':role.replace('_',' ').title(), 'source_type':role, 'format':path.suffix.lstrip('.').upper(),
        'crs':crs, 'analysis_crs':target_crs, 'transformation':f'{crs} -> {target_crs}' if crs and target_crs else None,
        'feature_count':len(raw), 'loaded_count':len(records), 'valid_geometry_count':valid, 'bounds':bounds,
        'geometry_types':types, 'field_mapping':mappings, 'mapping_suggestions':suggestions, 'warnings':warnings,
        'status':'WARNING' if warnings else 'READY', 'quality_indicator':round(100*valid/len(raw),1) if raw and crs else None,
        'data_label': 'PROTOTYPE / NON-OFFICIAL DATASET' if any(any(tag in str(r.get('raw_properties',{}).get('data_label','')).upper() for tag in ('DEMO', 'PROTOTYPE', 'SYNTHETIC')) for r in records) else 'USER PROVIDED / UNVERIFIED'}


def display_layer(records, analysis):
    return {'type':'FeatureCollection', 'features':[{'type':'Feature', 'geometry':mapping(reproject(r['geometry'], analysis, 'EPSG:4326')),
        'properties':{'source_id':r['id'], **r['attributes']}} for r in records if 'geometry' in r]}


def raster_metadata(path):
    try:
        import rasterio
        with rasterio.open(path) as src:
            return {'crs':str(src.crs), 'bounds':list(src.bounds), 'width':src.width, 'height':src.height, 'bands':src.count, 'resolution':list(src.res), 'nodata':src.nodata}
    except ImportError:
        return {'status':'UNAVAILABLE', 'warning':'Optional rasterio is not installed; vector processing remains available'}
    except Exception as exc:
        return {'status':'WARNING', 'warning':str(exc)}
