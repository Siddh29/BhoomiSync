import hashlib
import json
import math
import uuid
from pathlib import Path
from typing import Literal
from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, Query, UploadFile, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from backend.services.city import city_data
from backend.services.survey import survey_data, analyze_geotiff, compare_rasters, CONTEXT
from backend.services.environment import environment
from backend.services.context import site_context, geocode
from backend.services import operations as store
from backend.api.dependencies import editor

router = APIRouter(prefix='/api')


@router.get('/city/wards')
def wards():
    return city_data()['geojson']


@router.get('/city/insights')
def insights():
    return city_data()['insights']


@router.get('/survey')
def survey():
    return survey_data()


@router.get('/environment')
async def weather(lat: float = Query(12.9716, ge=-85, le=85), lon: float = Query(77.5946, ge=-180, le=180), refresh: bool = False):
    return await environment(lat, lon, refresh)


@router.get('/site-context')
async def context(lat: float = Query(12.9716, ge=-85, le=85), lon: float = Query(77.5946, ge=-180, le=180), refresh: bool = False):
    return await site_context(lat, lon, refresh)


@router.get('/places')
async def places(q: str = Query(min_length=2, max_length=80)):
    return await geocode(q)


class Resource(BaseModel):
    name: str = Field(min_length=3,max_length=100)
    category: Literal['equipment','service','training'] = 'equipment'
    provider: str = Field(min_length=2,max_length=100)
    status: Literal['available','reserved'] = 'available'
    description: str = Field(default='',max_length=1000)


@router.get('/resources')
def resources():
    return store.listing('resource')


@router.post('/resources')
def add_resource(body: Resource, actor=Depends(editor)):
    return store.save('resource',body.model_dump(),actor)


@router.put('/resources/{key}')
def update_resource(key: uuid.UUID, body: Resource, actor=Depends(editor)):
    if not store.get('resource',str(key)):
        raise HTTPException(404,'Resource not found')
    return store.save('resource',{**body.model_dump(),'id':str(key)},actor,'updated')


@router.get('/survey/rasters')
def rasters():
    return store.listing('raster')


@router.post('/survey/rasters')
async def raster_upload(role: Literal['ndvi', 'dem', 'ortho'] = Form(...), file: UploadFile = File(...), actor=Depends(editor)):
    if Path(file.filename or '').suffix.lower() not in ('.tif', '.tiff'):
        raise HTTPException(400, 'Upload a georeferenced .tif or .tiff file')
    data = await file.read(40 * 1024 * 1024 + 1)
    if len(data) > 40 * 1024 * 1024:
        raise HTTPException(413, 'Raster limit is 40 MB')
    asset_id = str(uuid.uuid4())
    folder = CONTEXT / 'rasters'
    folder.mkdir(exist_ok=True)
    path = folder / f'{asset_id}.tif'
    path.write_bytes(data)
    try:
        result = analyze_geotiff(path, role, asset_id)
    except Exception as exc:
        path.unlink(missing_ok=True)
        raise HTTPException(400, f'Cannot read this raster: {str(exc)[:200]}')
    return store.save('raster', {**result, 'filename': Path(file.filename).name, 'sha256': hashlib.sha256(data).hexdigest()}, actor)


class RasterComparison(BaseModel):
    baseline: uuid.UUID
    latest: uuid.UUID


@router.post('/survey/compare')
def raster_comparison(body: RasterComparison, actor=Depends(editor)):
    a,b=store.get('raster',str(body.baseline)),store.get('raster',str(body.latest))
    if not a or not b: raise HTTPException(404,'Both uploaded rasters must exist')
    if a['role']!=b['role']: raise HTTPException(400,'Compare rasters with the same interpretation')
    if body.baseline==body.latest: raise HTTPException(400,'Choose two different acquisitions')
    key=str(uuid.uuid4())
    try:
        result=compare_rasters(CONTEXT/'rasters'/f'{body.baseline}.tif',CONTEXT/'rasters'/f'{body.latest}.tif',a['role'],key)
    except Exception as exc:
        raise HTTPException(400,f'Comparison failed: {str(exc)[:180]}')
    return store.save('comparison',{**result,'baseline':a['filename'],'latest':b['filename']},actor)


@router.post('/survey/trends')
async def trends(file: UploadFile = File(...)):
    import csv,io
    from datetime import date,timedelta
    import numpy as np
    raw=await file.read(1024*1024+1)
    if len(raw)>1024*1024: raise HTTPException(413,'Time series limit is 1 MB')
    try:
        rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
        points=sorted((date.fromisoformat(r['date']),float(r['value'])) for r in rows)
        if not 4<=len(points)<=1000 or not all(math.isfinite(v) for _,v in points): raise ValueError('Provide 4–1000 finite observations')
        if len({d for d,_ in points})!=len(points): raise ValueError('Dates must be unique')
        x=np.array([(d-points[0][0]).days for d,_ in points],dtype=float);y=np.array([v for _,v in points])
        slope,intercept=np.polyfit(x,y,1);pred=slope*x+intercept
        residual=float(np.sqrt(np.sum((y-pred)**2)/(len(y)-2)))
        r2=1-float(np.sum((y-pred)**2))/float(np.sum((y-y.mean())**2)) if np.std(y)>0 else 1
        forecasts=[]
        for days in [7,30,90]:
            nx=x[-1]+days;mean=float(slope*nx+intercept);spread=1.96*residual*math.sqrt(1+1/len(x)+(nx-x.mean())**2/max(float(np.sum((x-x.mean())**2)),1))
            forecasts.append({'date':(points[-1][0]+timedelta(days=days)).isoformat(),'value':round(mean,4),'lower':round(mean-spread,4),'upper':round(mean+spread,4)})
        return {'filename':Path(file.filename or 'series.csv').name,'observations':[{'date':d.isoformat(),'value':v} for d,v in points],'slope_per_day':round(float(slope),6),'r2':round(r2,4),'forecast':forecasts,'method':'Ordinary least squares on elapsed days; approximate normal 95% prediction intervals. Exploratory extrapolation, not a trained AI model. Values keep the units of your CSV.'}
    except (ValueError,KeyError,UnicodeError,TypeError) as exc:
        raise HTTPException(400,f'CSV needs date (YYYY-MM-DD) and numeric value columns: {exc}')


@router.get('/survey/rasters/{asset_id}/image')
def raster_image(asset_id: uuid.UUID):
    path = CONTEXT / 'rasters' / f'{asset_id}.png'
    if not path.exists():
        raise HTTPException(404, 'Raster not found')
    return FileResponse(path, media_type='image/png')


class Review(BaseModel):
    parcel_id: str = Field(min_length=1, max_length=100)
    run_id: str = Field(min_length=1, max_length=100)
    status: Literal['investigating', 'field_check', 'accepted', 'rejected']
    note: str = Field(min_length=5, max_length=3000)


@router.get('/reviews')
def reviews():
    return store.listing('review')


@router.post('/reviews')
def review(body: Review, actor=Depends(editor)):
    # This records a human decision. It never overwrites pipeline evidence.
    return store.save('review', {**body.model_dump(), 'id': f'{body.run_id}:{body.parcel_id}', 'actor': actor}, actor, 'decision')


@router.get('/documents')
def documents():
    return store.listing('document')


@router.post('/documents')
async def document_upload(file: UploadFile = File(...), parcel_id: str = Form('workspace'), actor=Depends(editor)):
    filename = Path((file.filename or 'document').replace('\\', '/')).name
    suffix = Path(filename).suffix.lower()
    if suffix not in ('.pdf', '.png', '.jpg', '.jpeg', '.txt', '.csv', '.json', '.geojson'):
        raise HTTPException(400, 'Supported evidence: PDF, PNG, JPG, TXT, CSV, JSON, GeoJSON')
    data = await file.read(15 * 1024 * 1024 + 1)
    if not data or len(data) > 15 * 1024 * 1024:
        raise HTTPException(400, 'Evidence must be non-empty and at most 15 MB')
    key = str(uuid.uuid4())
    folder = store.ROOT / 'documents'
    folder.mkdir(parents=True, exist_ok=True)
    (folder / key).write_bytes(data)
    return store.save('document', {'id': key, 'filename': filename, 'parcel_id': parcel_id[:100], 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'actor': actor}, actor)


@router.get('/documents/{key}/download')
def download(key: uuid.UUID):
    record = store.get('document', str(key))
    if not record:
        raise HTTPException(404, 'Document not found')
    return FileResponse(store.ROOT / 'documents' / str(key), filename=record['filename'], media_type='application/octet-stream')


@router.get('/documents/{key}/verify')
def verify(key: uuid.UUID):
    record = store.get('document', str(key))
    if not record:
        raise HTTPException(404, 'Document not found')
    path = store.ROOT / 'documents' / str(key)
    actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
    return {'id': str(key), 'intact': actual == record['sha256'], 'expected_sha256': record['sha256'], 'actual_sha256': actual,
            'scope': 'Verifies byte integrity since upload; does not establish legal authenticity.'}


@router.delete('/documents/{key}')
def remove_document(key: uuid.UUID, actor=Depends(editor)):
    if not store.get('document', str(key)):
        raise HTTPException(404, 'Document not found')
    store.delete('document', str(key), actor)
    (store.ROOT / 'documents' / str(key)).unlink(missing_ok=True)
    return {'deleted': True}


class Fence(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    latitude: float = Field(ge=-85, le=85)
    longitude: float = Field(ge=-180, le=180)
    radius_m: float = Field(ge=5, le=50000)


class Position(BaseModel):
    latitude: float = Field(ge=-85, le=85)
    longitude: float = Field(ge=-180, le=180)


@router.get('/geofences')
def fences():
    return store.listing('geofence')


@router.post('/geofences')
def create_fence(body: Fence, actor=Depends(editor)):
    return store.save('geofence', {**body.model_dump(), 'inside': None}, actor)


@router.delete('/geofences/{key}')
def delete_fence(key: uuid.UUID, actor=Depends(editor)):
    if not store.get('geofence', str(key)):
        raise HTTPException(404, 'Geofence not found')
    store.delete('geofence', str(key), actor)
    return {'deleted': True}


@router.post('/geofences/{key}/check')
def check_fence(key: uuid.UUID, body: Position, actor=Depends(editor)):
    f = store.get('geofence', str(key))
    if not f:
        raise HTTPException(404, 'Geofence not found')
    a, b = math.radians(f['latitude']), math.radians(body.latitude)
    dlat, dlon = b - a, math.radians(body.longitude - f['longitude'])
    distance = 6371000 * 2 * math.asin(min(1, math.sqrt(math.sin(dlat / 2)**2 + math.cos(a) * math.cos(b) * math.sin(dlon / 2)**2)))
    inside = distance <= f['radius_m']
    event = 'initial' if f['inside'] is None else 'entered' if inside and not f['inside'] else 'exited' if not inside and f['inside'] else 'unchanged'
    result = {'geofence_id': str(key), 'name': f['name'], 'inside': inside, 'distance_m': round(distance, 1), 'event': event, **body.model_dump(), 'mode': 'manual test point'}
    store.save('geofence', {**f, 'inside': inside, 'last_check': result}, actor, 'checked')
    if event != 'unchanged':
        store.save('alert', result, actor, event)
    return result


@router.get('/alerts')
def alerts():
    return store.listing('alert')


class Task(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    assignee: str = Field(min_length=2, max_length=80)
    category: Literal['survey', 'verification', 'canopy', 'maintenance'] = 'survey'
    status: Literal['open', 'in_progress', 'done'] = 'open'
    parcel_id: str = Field(default='', max_length=100)


@router.get('/tasks')
def tasks():
    return store.listing('task')


@router.post('/tasks')
def add_task(body: Task, actor=Depends(editor)):
    return store.save('task', body.model_dump(), actor)


@router.put('/tasks/{key}')
def edit_task(key: uuid.UUID, body: Task, actor=Depends(editor)):
    if not store.get('task', str(key)):
        raise HTTPException(404, 'Task not found')
    return store.save('task', {**body.model_dump(), 'id': str(key)}, actor, 'updated')


@router.get('/audit')
def audit():
    return store.audit()


@router.get('/evidence-bundle')
def evidence(request: Request):
    manager=getattr(request.app.state,'manager',None)
    result=manager.result if manager else None
    body = {'generated_at': store.timestamp(), 'product': 'BhoomiSync SIH26013 prototype', 'reviews': store.listing('review'),
            'documents': store.listing('document'), 'tasks': store.listing('task'), 'geofences': store.listing('geofence'),
            'resources':store.listing('resource'),'rasters':store.listing('raster'),'comparisons':store.listing('comparison'),
            'harmonization':result,'audit': store.audit(), 'city_provenance': city_data()['insights']['provenance'], 'survey_provenance': survey_data()['provenance']}
    return Response(json.dumps(body, indent=2), media_type='application/json', headers={'Content-Disposition': 'attachment; filename="bhoomisync-evidence.json"'})


@router.get('/report')
def report(request:Request):
    from html import escape
    result=getattr(request.app.state,'manager',None)
    result=result.result if result else None
    if not result: raise HTTPException(409,'Run harmonization before generating a report')
    summary=result['summary'];run_id=result['run_id']
    decisions=[r for r in store.listing('review') if r['run_id']==run_id]
    rows=''.join(f"<tr><td>{escape(r['parcel_id'])}</td><td>{escape(r['status'].replace('_',' '))}</td><td>{escape(r['note'])}</td><td>{escape(r['actor'])}</td></tr>" for r in decisions)
    metrics=''.join(f'<article><span>{label}</span><strong>{summary[key]}</strong></article>' for label,key in [('Master parcels','harmonized_parcels'),('Matched','matched'),('Needs review','needs_review'),('Conflicts','conflicts')])
    content=f'''<!doctype html><html lang="en"><meta charset="utf-8"><title>BhoomiSync evidence report</title><style>body{{font:14px system-ui;color:#244339;max-width:980px;margin:50px auto;padding:0 28px}}header{{border-bottom:2px solid #719d77;padding-bottom:25px}}h1{{font-size:40px;font-weight:400;letter-spacing:-1px}}small,footer{{color:#829481;font-size:11px}}.metrics{{display:flex;gap:50px;margin:35px 0}}article span{{display:block;font-size:11px;color:#879a80}}article strong{{font-size:35px;font-weight:400}}table{{width:100%;border-collapse:collapse;font-size:12px}}td,th{{text-align:left;padding:12px;border-bottom:1px solid #dfe8da;vertical-align:top}}h2{{font-size:22px;font-weight:500;margin-top:32px}}p{{line-height:1.8}}.note{{background:#f1f5eb;padding:18px}}button{{background:#2b5846;color:white;padding:10px 18px;border:0;border-radius:4px;cursor:pointer}}@media print{{body{{margin:0;max-width:none}}button{{display:none}}}}</style><header><small>BHOOMISYNC / SIH26013 / EVIDENCE REPORT</small><h1>From records to accountable decisions.</h1><p>Run {escape(run_id)} · Generated {escape(store.timestamp())}</p><button onclick="window.print()">Print / save as PDF</button></header><div class="metrics">{metrics}</div><h2>Harmonization evidence</h2><p>{summary['input_features']} source observations across {summary['datasets']} roles. Mean heuristic evidence confidence: {summary['average_confidence']}%. Analysis CRS: {escape(summary['analysis_crs'])}. Cadastral boundaries are retained pending human survey review.</p><p class="note">Bundled parcel records are synthetic demonstration fixtures. Confidence is an explainable evidence index, not a calibrated probability. This report is not a legal ownership certificate.</p><h2>Recorded decisions for this run</h2><table><thead><tr><th>Parcel</th><th>Outcome</th><th>Recorded reasoning</th><th>Actor</th></tr></thead><tbody>{rows or '<tr><td colspan="4">No decisions recorded for this run.</td></tr>'}</tbody></table><h2>Spatial and survey context</h2><p>243 DataMeet Bengaluru ward polygons support exploratory clustering and Gi* analysis. The morphology/accessibility index is not an official price or observed growth metric. Kallapuram is a separate survey site: {survey_data()['area_acres']} acres, {survey_data()['coverage_percent']}% coverage by the imported RGB imagery. Image-derived crowns require field validation.</p><h2>Provenance and accountability</h2><p>{len(store.listing('document'))} uploaded evidence files retain SHA-256 hashes. {len(decisions)} reviewer decisions are attached to this run. The local database retains an append-only application event history; it is not a tamper-proof legal ledger. Local personas demonstrate workflow roles and require real authentication before deployment.</p><footer>Supporting machine-readable records are available in the evidence bundle, harmonized GeoJSON, conflicts CSV and change report. © BhoomiSync prototype.</footer></html>'''
    return Response(content,media_type='text/html')
