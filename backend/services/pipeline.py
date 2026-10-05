import hashlib
import json
import logging
import time
from collections import Counter
from pathlib import Path
from shapely.geometry import mapping
from backend.config import BOUNDARY_LIMIT_M, AREA_LIMIT_PERCENT, GNSS_LIMIT_M, SCHEMA_VERSION
from backend.core.schemas import Parcel, Issue
from backend.services.ingestion import ROLES, load_source, display_layer
from backend.services.crs import analysis_crs, reproject
from backend.services.attributes import normalize, attribute_similarity
from backend.services.matching import match
from backend.services.topology import overlaps
from backend.services.changes import building_changes
from backend.services.confidence import classify

log = logging.getLogger('BhoomiSync')
STAGES = ['Data Validation', 'CRS Harmonization', 'Attribute Mapping', 'Topology Analysis', 'Spatial Candidate Matching', 'Conflict Detection', 'Change Detection', 'Confidence Scoring', 'Master Layer Generation']


def fingerprint(directory):
    digest = hashlib.sha256(str(SCHEMA_VERSION).encode())
    from backend import config
    digest.update(json.dumps({k:getattr(config,k) for k in dir(config) if k.isupper() and isinstance(getattr(config,k),(int,float,dict))},sort_keys=True).encode())
    for path in sorted(Path(directory).glob('*')):
        if path.suffix in ('.geojson','.csv'):
            digest.update(path.name.encode()); digest.update(path.read_bytes())
    return digest.hexdigest()


def run_pipeline(directory, callback=lambda stage:None):
    start = time.perf_counter()
    stages = []
    def stage(index):
        name = STAGES[index]
        log.info('[BhoomiSync] %s',name)
        callback({'name':name,'status':'RUNNING','index':index,'total':len(STAGES)})
        return time.perf_counter()
    def done(index, tick):
        record = {'name':STAGES[index], 'status':'DONE', 'index':index,'duration_ms':round((time.perf_counter()-tick)*1000,2),'total':len(STAGES)}
        stages.append(record); callback(record)
    directory = Path(directory)
    tick = stage(0)
    initial, _ = load_source(directory/'cadastral.geojson','cadastral')
    if not initial: raise ValueError('A non-empty cadastral polygon layer is required')
    done(0,tick)
    tick = stage(1)
    analysis = analysis_crs(reproject(initial[0]['geometry'], initial[0]['source_crs'],'EPSG:4326'))
    data, metadata = {}, []
    for role in ROLES:
        try:
            records, meta = load_source(directory / (f'{role}.csv' if role == 'revenue' else f'{role}.geojson'),role,analysis)
        except (ValueError, TypeError, KeyError) as exc:
            if role == 'cadastral': raise
            records, meta = [], {'id':role,'name':role.replace('_',' ').title(),'status':'REJECTED','feature_count':0,'valid_geometry_count':0,'crs':None,'warnings':[str(exc)]}
        data[role] = records; metadata.append(meta)
    base, municipal = data['cadastral'], data['municipal']
    if len({p['id'] for p in base}) != len(base): raise ValueError('Duplicate cadastral IDs must be corrected before building master records')
    done(1,tick)
    tick = stage(2)
    revenue_index, gnss_index = {}, {}
    for r in data['revenue']:
        key = normalize(r['attributes'].get('survey_number'))
        if key: revenue_index.setdefault(key,[]).append(r)
    for r in data['gnss']:
        key = normalize(r['attributes'].get('survey_number'))
        if key: gnss_index.setdefault(key,[]).append(r)
        else:
            distances = [(r['geometry'].distance(p['geometry']),i) for i,p in enumerate(base)]
            if distances:
                distance, i = min(distances)
                if distance <= GNSS_LIMIT_M:
                    key = normalize(base[i]['attributes'].get('survey_number'))
                    gnss_index.setdefault(key,[]).append(r)
                    r['association'] = 'NEAREST_WITHIN_2M'
    done(2,tick)
    tick = stage(3)
    overlap_records = [('cadastral',v) for v in overlaps([r['geometry'] for r in base])] + [('municipal',v) for v in overlaps([r['geometry'] for r in municipal])]
    done(3,tick)
    tick = stage(4)
    assigned, unmatched_municipal = match(base,municipal)
    municipal_to_base = {v['index']:i for i,v in assigned.items()}
    done(4,tick)
    tick = stage(5)
    issues, issues_by_parcel = [], {i:[] for i in range(len(base))}
    def issue(index, kind, description, sources, metrics=None, severity='WARNING'):
        parcel_id = base[index]['attributes'].get('parcel_id',base[index]['id']) if index is not None else None
        record = Issue(id=f'ISSUE-{len(issues)+1:04d}',parcel_id=parcel_id,type=kind,severity=severity,description=description,
            sources=sources,metrics=metrics or {},recommended_action='Verify against source survey; retain cadastral master pending review').model_dump()
        issues.append(record)
        if index is not None: issues_by_parcel[index].append(record)
    used_revenue, observations = set(), {}
    for i,p in enumerate(base):
        attrs = p['attributes']; key = normalize(attrs.get('survey_number'))
        revenue_options = revenue_index.get(key,[])
        revenue = revenue_options[0] if revenue_options else None
        if revenue: used_revenue.add(revenue['id'])
        if len(revenue_options)>1: issue(i,'MULTIPLE_CANDIDATE_MATCH','Duplicate revenue survey join', ['revenue'],{'record_ids':[r['id'] for r in revenue_options]})
        obs = assigned.get(i); mun = municipal[obs['index']] if obs else None
        for source, record in [('cadastral',p),('municipal',mun)]:
            if record and record['repairs']: issue(i,'TOPOLOGY_INVALID',f'{source} required geometry repair', [source],{'repairs':record['repairs']},'CRITICAL')
            if record and record['geometry'].area < 1: issue(i,'EXTREME_SLIVER',f'{source} area below 1 square metre', [source],{'area_sqm':record['geometry'].area})
        if not obs: issue(i,'UNMATCHED_SOURCE','No municipal match', ['municipal'])
        else:
            metrics = obs['metrics']
            if metrics['boundary_distance_m'] > BOUNDARY_LIMIT_M: issue(i,'BOUNDARY_MISMATCH','Municipal boundary disagrees with cadastral survey',['cadastral','municipal'],{'boundary_distance_m':round(metrics['boundary_distance_m'],3)})
            if metrics.get('attribute_similarity') is not None and metrics['attribute_similarity'] < .8: issue(i,'ATTRIBUTE_MISMATCH','Survey/owner/land-use attributes disagree',['cadastral','municipal'],{'attribute_similarity':round(metrics['attribute_similarity'],3)})
            if obs['ambiguous']: issue(i,'MULTIPLE_CANDIDATE_MATCH','Competing spatial candidate scores',['municipal'],{'candidates':obs['candidates']})
        difference = None
        if not revenue: issue(i,'UNMATCHED_SOURCE','No revenue record joined by normalized survey number',['revenue'])
        elif revenue['attributes'].get('recorded_area_sqm') is not None:
            area = revenue['attributes']['recorded_area_sqm']; difference = abs(area-p['geometry'].area)/p['geometry'].area*100
            if difference > AREA_LIMIT_PERCENT: issue(i,'AREA_MISMATCH','Revenue recorded area differs from projected cadastral area',['revenue','cadastral'],{'recorded_area_sqm':area,'calculated_area_sqm':round(p['geometry'].area,3),'difference_percent':round(difference,3)})
        else: issue(i,'MISSING_ATTRIBUTE','Revenue recorded area unavailable',['revenue'])
        ground = gnss_index.get(key,[])
        deviation = max((g['geometry'].distance(p['geometry'].boundary) for g in ground),default=None)
        if deviation is not None and deviation > GNSS_LIMIT_M: issue(i,'GNSS_DEVIATION','Survey point deviates from cadastral boundary',['gnss','cadastral'],{'deviation_m':round(deviation,3)})
        observations[i] = (obs,mun,revenue,ground,difference,deviation)
    for source,(a,b,area,duplicate) in overlap_records:
        for idx in (a,b):
            i = idx if source == 'cadastral' else municipal_to_base.get(idx)
            issue(i,'DUPLICATE_GEOMETRY' if duplicate else 'PARCEL_OVERLAP',f'{source} observations overlap by {area:.2f} square metres',[source],{'source_ids':[(base if source=='cadastral' else municipal)[k]['id'] for k in (a,b)],'overlap_sqm':round(area,3)},'CRITICAL')
    for j in unmatched_municipal: issue(None,'UNMATCHED_SOURCE',f'Municipal record {municipal[j]["id"]} has no assigned parcel',['municipal'],{'source_id':municipal[j]['id']})
    for r in data['revenue']:
        if r['id'] not in used_revenue: issue(None,'UNMATCHED_SOURCE',f'Revenue record {r["id"]} has no joined parcel',['revenue'],{'source_id':r['id']})
    done(5,tick)
    tick = stage(6)
    warnings = [f'{m["id"]}: {w}' for m in metadata for w in m.get('warnings',[])]
    if data['buildings_old'] and data['buildings_latest']:
        changes = building_changes(data['buildings_old'],data['buildings_latest'],base,analysis)
    else:
        changes = []; warnings.append('Building change detection skipped: both non-empty epochs required')
    for i,(obs,mun,_,_,_,_) in observations.items():
        if obs and obs['metrics']['boundary_distance_m'] > BOUNDARY_LIMIT_M:
            changes.append({'id':f'CHANGE-{len(changes)+1:04d}','type':'PARCEL_BOUNDARY_DISAGREEMENT','parcel_id':base[i]['attributes'].get('parcel_id',base[i]['id']),
                'description':'Cross-source boundary disagreement; temporal change is unverified', 'iou':round(obs['metrics']['iou'],4),
                'area_difference_percent':round((1-obs['metrics']['area_similarity'])*100,3),
                'geometry':mapping(reproject(mun['geometry'],analysis,'EPSG:4326'))})
    done(6,tick)
    tick = stage(7)
    parcels = []
    for i,p in enumerate(base):
        attrs = p['attributes']; pid = attrs.get('parcel_id',p['id'])
        obs,mun,rev,ground,diff,deviation = observations[i]
        confidence,status = classify(obs['score'] if obs else 0,issues_by_parcel[i],not obs)
        metrics = {k:round(v,4) if v is not None else None for k,v in obs['metrics'].items()} if obs else {k:None for k in ('iou','centroid_distance_m','boundary_distance_m','area_similarity','attribute_similarity')}
        metrics.update({'match_score':round(obs['score'],3) if obs else None,'recorded_area_difference_percent':round(diff,3) if diff is not None else None,'gnss_deviation_m':round(deviation,3) if deviation is not None else None})
        source_ids = {'cadastral':p['id']}
        if mun: source_ids['municipal'] = mun['id']
        if rev: source_ids['revenue'] = rev['id']
        if ground: source_ids['gnss'] = ','.join(g['id'] for g in ground)
        parcel_changes = [c for c in changes if c['parcel_id']==pid]
        if any('BUILDING' in c['type'] for c in parcel_changes): source_ids['buildings'] = 'epoch comparison'
        explanation = [f'Polygon IoU {metrics["iou"]:.3f}',f'Centroid deviation {metrics["centroid_distance_m"]:.3f} m',f'Boundary Hausdorff distance {metrics["boundary_distance_m"]:.3f} m',f'Weighted match score {metrics["match_score"]:.2f}%'] if obs else ['No plausible municipal observation; confidence cannot be established']
        if diff is not None: explanation.append(f'Revenue area difference {diff:.2f}%')
        if deviation is not None: explanation.append(f'GNSS boundary deviation {deviation:.2f} m')
        explanation += [f'Review evidence: {r["description"]}' for r in issues_by_parcel[i]]
        for r in issues_by_parcel[i]: r['confidence']=confidence
        parcel = Parcel(parcel_id=pid,survey_number=attrs.get('survey_number'),municipal_property_id=mun['attributes'].get('municipal_property_id') if mun else None,
            revenue_record_id=rev['id'] if rev else None,owner_name=attrs.get('owner_name'),land_use=attrs.get('land_use'),recorded_area_sqm=rev['attributes'].get('recorded_area_sqm') if rev else None,
            geometry=mapping(reproject(p['geometry'],analysis,'EPSG:4326')),area_sqm=round(p['geometry'].area,3),perimeter_m=round(p['geometry'].length,3),metrics=metrics,
            source_ids=source_ids,source_count=len(source_ids),confidence=confidence,overall_confidence=confidence,status=status,
            topology='REVIEW' if any(r['type'] in ('TOPOLOGY_INVALID','PARCEL_OVERLAP','DUPLICATE_GEOMETRY') for r in issues_by_parcel[i]) else 'VALID',
            conflicts=issues_by_parcel[i],changes=parcel_changes,explanation=explanation,recommendation='Auto-harmonization accepted; cadastral geometry retained' if status=='MATCHED' else 'Human survey verification required; cadastral geometry retained',
            auto_harmonized=status=='MATCHED',review_required=status!='MATCHED',
            metadata={'analysis_crs':analysis,'master_geometry_policy':'CADASTRAL_RETAINED','original_geometry':p['original_geometry'],
                      'municipal_original_geometry':mun['original_geometry'] if mun else None,'municipal_original_crs':mun['source_crs'] if mun else None,
                      'repair_operations':p['repairs']+(mun['repairs'] if mun else []),'candidate_scores':obs['candidates'] if obs else [],
                      'source_properties':{k:v['raw_properties'] for k,v in [('cadastral',p),('municipal',mun),('revenue',rev)] if v}}).model_dump()
        parcels.append(parcel)
    done(7,tick)
    tick = stage(8)
    layers = {role:display_layer(records,analysis) for role,records in data.items() if role!='revenue'}
    layers['harmonized']={'type':'FeatureCollection','features':[{'type':'Feature','id':p['parcel_id'],'geometry':p['geometry'],'properties':{k:v for k,v in p.items() if k not in ('geometry','metadata')}} for p in parcels]}
    layers['conflicts']={'type':'FeatureCollection','features':[f for f in layers['harmonized']['features'] if f['properties']['conflicts']]}
    layers['changes']={'type':'FeatureCollection','features':[{'type':'Feature','geometry':c['geometry'],'properties':{k:v for k,v in c.items() if k!='geometry'}} for c in changes]}
    counts = Counter(p['status'] for p in parcels)
    summary = {'datasets':len([m for m in metadata if m['status']!='MISSING']),'input_features':sum(m['feature_count'] for m in metadata),
        'harmonized_parcels':len(parcels),'matched':counts['MATCHED'],'review_required':counts['REVIEW_REQUIRED'],'low_confidence':counts['CONFLICT'],
        'needs_review':sum(p['review_required'] for p in parcels),'conflicts':len(issues),'conflict_parcels':sum(bool(p['conflicts']) for p in parcels),
        'changes':len(changes),'average_confidence':round(sum(p['confidence'] for p in parcels)/len(parcels),1),
        'success_rate':round(100*counts['MATCHED']/len(parcels),1),'analysis_crs':analysis,'data_label':'DEMO / SIMULATED' if all(m.get('data_label')=='DEMO / SIMULATED' for m in metadata if m['status']!='MISSING') else 'USER PROVIDED / UNVERIFIED',
        'warnings':warnings,'duration_ms':round((time.perf_counter()-start)*1000,2),'confidence_note':'Explainable heuristic evidence score, not a calibrated probability'}
    done(8,tick)
    return {'summary':summary,'datasets':metadata,'parcels':parcels,'conflicts':issues,'changes':changes,'layers':layers,'stages':stages,'fingerprint':fingerprint(directory)}
