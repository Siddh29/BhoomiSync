import json
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Depends
from fastapi.responses import FileResponse
from backend.core.schemas import RunRequest, Parcel, Issue
from backend.services.export import EXPORTS
from backend.services.ingestion import ROLES, load_source, raster_metadata

from backend.api.dependencies import editor

router = APIRouter(prefix='/api')


def manager(request): return request.app.state.manager


def result(request):
    value = manager(request).result
    if value is None: raise HTTPException(409,'No completed run. Load sources and run harmonization.')
    return value


@router.get('/health')
def health(request:Request):
    return {'status':'ok','service':'BhoomiSync','demo_mode':manager(request).demo_mode}


@router.get('/datasets')
def datasets(request:Request):
    m = manager(request)
    metadata=[]
    analysis=m.result['summary']['analysis_crs'] if m.result else None
    for role in ROLES:
        try: metadata.append(load_source(m.input/(f'{role}.csv' if role=='revenue' else f'{role}.geojson'),role,analysis)[1])
        except (ValueError,TypeError,KeyError) as exc:
            metadata.append({'id':role,'name':role.replace('_',' ').title(),'status':'REJECTED','feature_count':0,'crs':None,'warnings':[str(exc)]})
    return metadata


@router.post('/datasets/upload', dependencies=[Depends(editor)])
async def upload(request:Request, file:UploadFile=File(...), role:str=Form(...), crs:str|None=Form(None)):
    m=manager(request)
    if role not in ROLES: raise HTTPException(422,'Unsupported source role')
    if m.demo_mode: raise HTTPException(409,'Uploads require BHOOMISYNC_DEMO_MODE=false to preserve bundled demo inputs')
    expected='.csv' if role=='revenue' else '.geojson'
    if Path(file.filename or '').suffix.lower()!=expected: raise HTTPException(422,f'{role} requires {expected}')
    content=await file.read(10*1024*1024+1)
    if len(content)>10*1024*1024: raise HTTPException(413,'Upload limit is 10 MB')
    with m.lock:
        if m.state['status']=='RUNNING': raise HTTPException(409,'Cannot replace observations during a run')
        temp=m.input/f'{role}.upload{expected}'
        try:
            temp.write_bytes(content)
            if expected=='.geojson' and crs:
                payload=json.loads(content)
                payload['crs']={'type':'name','properties':{'name':crs}}
                temp.write_text(json.dumps(payload),encoding='utf-8')
            records,metadata=load_source(temp,role,explicit_crs=crs)
            if not records: raise ValueError('No usable observations')
            temp.replace(m.input/f'{role}{expected}')
            m.result=None; m.repo.clear()
            m.state={'status':'IDLE','stages':[],'progress':0,'error':None}
            return metadata
        except (ValueError,KeyError,TypeError) as exc: raise HTTPException(422,str(exc)) from exc
        finally: temp.unlink(missing_ok=True)


@router.get('/datasets/raster-metadata')
def raster(request:Request):
    return raster_metadata(manager(request).input/'optional.tif')


@router.post('/demo/load', dependencies=[Depends(editor)])
def load_demo(request:Request):
    m=manager(request)
    if not m.demo_mode: raise HTTPException(409,'Demo mode disabled')
    return {'datasets':datasets(request),'status':m.state}


@router.post('/demo/reset', dependencies=[Depends(editor)])
def reset(request:Request):
    try: return manager(request).reset()
    except (RuntimeError,ValueError) as exc: raise HTTPException(409,str(exc)) from exc


@router.post('/harmonization/run', dependencies=[Depends(editor)])
def run(request:Request,body:RunRequest=RunRequest()):
    try: return manager(request).start(body.force)
    except RuntimeError as exc: raise HTTPException(409,str(exc)) from exc


@router.get('/harmonization/status')
def status(request:Request):
    m=manager(request)
    with m.lock: return m.state.copy()


@router.get('/results/summary')
def summary(request:Request): return {**result(request)['summary'],'run_id':result(request)['run_id']}


@router.get('/results/parcels',response_model=list[Parcel])
def parcels(request:Request): return result(request)['parcels']


@router.get('/results/parcels/{parcel_id}',response_model=Parcel)
def parcel(parcel_id:str,request:Request):
    p=next((p for p in result(request)['parcels'] if p['parcel_id']==parcel_id),None)
    if p is None: raise HTTPException(404,'Unknown parcel')
    return p


@router.get('/results/conflicts',response_model=list[Issue])
def conflicts(request:Request): return result(request)['conflicts']


@router.get('/results/changes')
def changes(request:Request): return result(request)['changes']


@router.get('/layers/{layer_name}')
def layer(layer_name:str,request:Request):
    value=result(request)['layers'].get(layer_name)
    if value is None: raise HTTPException(404,'Unknown layer')
    return value


@router.get('/export/{filename}')
def export(filename:str,request:Request):
    result(request)
    actual=EXPORTS.get(filename)
    if not actual: raise HTTPException(404,'Unknown export')
    path=manager(request).data/'exports'/actual
    return FileResponse(path,filename=actual,media_type='text/csv' if filename.endswith('.csv') else 'application/json')
