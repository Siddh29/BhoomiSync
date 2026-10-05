import csv
import json
import time
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.api.routes import router
from backend.demo.generate_demo_data import generate
from backend.services.pipeline import run_pipeline, fingerprint
from backend.services.ingestion import load_source
from backend.services.run_manager import RunManager
from backend.services.export import write_exports


@pytest.fixture
def demo(tmp_path):
    return generate(tmp_path/'demo')


def test_end_to_end_and_reproducibility(demo):
    a=run_pipeline(demo); b=run_pipeline(demo)
    assert a['parcels']==b['parcels']
    assert len(a['parcels'])==100
    assert a['summary']['analysis_crs']=='EPSG:32643'
    assert a['summary']['matched']>0 and a['summary']['needs_review']>0
    assert a['summary']['input_features']==448
    by={p['parcel_id']:p for p in a['parcels']}
    assert by['BS-P-00001']['status']=='MATCHED'
    assert by['BS-P-00002']['metrics']['centroid_distance_m']==pytest.approx((3.8**2+1)**.5,abs=.001)
    assert by['BS-P-00003']['metrics']['recorded_area_difference_percent']==pytest.approx(18,abs=.001)
    expected={'BOUNDARY_MISMATCH','AREA_MISMATCH','ATTRIBUTE_MISMATCH','PARCEL_OVERLAP','UNMATCHED_SOURCE','GNSS_DEVIATION','TOPOLOGY_INVALID'}
    assert expected.issubset({c['type'] for c in a['conflicts']})
    assert {'NEW_BUILDING','REMOVED_BUILDING','MODIFIED_BUILDING'}.issubset({c['type'] for c in a['changes']})
    assert by['BS-P-00010']['metadata']['repair_operations']
    assert by['BS-P-00007']['metrics']['gnss_deviation_m']==pytest.approx(4.2,abs=.001)
    write_exports(a,demo.parent/'exports')
    assert json.loads((demo.parent/'exports/harmonized_parcels.geojson').read_text())['features']
    with (demo.parent/'exports/conflicts.csv').open(encoding='utf-8-sig',newline='') as f:
        assert len(list(csv.DictReader(f)))==a['summary']['conflicts']


def test_missing_crs_rejected(demo):
    path=demo/'municipal.geojson'; payload=json.loads(path.read_text());payload.pop('crs');path.write_text(json.dumps(payload))
    with pytest.raises(ValueError,match='CRS missing'): load_source(path,'municipal')


def test_optional_missing_layers_and_absent_csv_field(demo):
    (demo/'buildings_latest.geojson').unlink()
    (demo/'gnss.geojson').unlink()
    revenue=demo/'revenue.csv'
    revenue.write_text('record_id,owner\nR1,Demo\n',encoding='utf-8')
    output=run_pipeline(demo)
    assert len(output['parcels'])==100
    assert output['summary']['warnings']
    assert not any(c['type']=='REMOVED_BUILDING' for c in output['changes'])


def test_optional_source_without_crs_warns_and_continues(demo):
    path=demo/'municipal.geojson';payload=json.loads(path.read_text());payload.pop('crs');path.write_text(json.dumps(payload))
    output=run_pipeline(demo)
    assert len(output['parcels'])==100
    assert any('CRS missing' in warning for warning in output['summary']['warnings'])
    assert all(p['review_required'] for p in output['parcels'])


def test_fixture_regeneration_identical(demo):
    before=fingerprint(demo);generate(demo)
    assert before==fingerprint(demo)


def test_api_reset_run_export_and_cache(tmp_path):
    app=FastAPI();app.include_router(router)
    m=RunManager(tmp_path);m.initialize();app.state.manager=m
    with TestClient(app) as client:
        for path in ['/api/health','/api/datasets','/api/results/summary','/api/results/parcels','/api/results/conflicts','/api/results/changes','/api/layers/harmonized','/api/results/parcels/BS-P-00001']:
            response=client.get(path);assert response.status_code==200,(path,response.text)
        assert client.get('/api/results/parcels/unknown').status_code==404
        for filename in ['harmonized.geojson','conflicts.csv','changes.csv','summary.json']:
            r=client.get('/api/export/'+filename);assert r.status_code==200 and r.headers.get('content-disposition')
        assert client.post('/api/demo/reset').status_code==200
        assert client.get('/api/results/summary').status_code==409
        assert client.post('/api/harmonization/run',json={'force':True}).status_code==200
        deadline=time.monotonic()+15
        while client.get('/api/harmonization/status').json()['status']=='RUNNING' and time.monotonic()<deadline: time.sleep(.02)
        assert client.get('/api/harmonization/status').json()['status']=='COMPLETED'
        assert client.get('/api/results/summary').json()['matched']>0
        cached=RunManager(tmp_path);cached.initialize()
        assert cached.state['cached'] is True


def test_upload_validation_and_non_demo_ingestion(tmp_path,demo):
    app=FastAPI();app.include_router(router);m=RunManager(tmp_path/'custom',demo_mode=False);m.initialize();app.state.manager=m
    with TestClient(app) as client:
        bad=client.post('/api/datasets/upload',data={'role':'cadastral'},files={'file':('cadastral.geojson',b'{}')})
        assert bad.status_code==422
        assert client.post('/api/demo/reset').status_code==409
        for role in ('cadastral','municipal','revenue','gnss','buildings_old','buildings_latest'):
            suffix='.csv' if role=='revenue' else '.geojson'
            response=client.post('/api/datasets/upload',data={'role':role},files={'file':(role+suffix,(demo/(role+suffix)).read_bytes())})
            assert response.status_code==200,response.text
        m.execute()
        assert m.state['status']=='COMPLETED'
        assert client.get('/api/results/summary').json()['harmonized_parcels']==100
