import asyncio
import io
import json
from datetime import datetime, timezone
import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.api.intelligence import router
from backend.services import operations as store
from backend.services.city import city_data, gini
from backend.services.survey import survey_data, analyze_geotiff


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(store, 'ROOT', tmp_path / 'operations')
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_real_ward_geometry_and_stable_partition():
    result = city_data()
    features = result['geojson']['features']
    assert len(features) == 243
    assert sum(c['count'] for c in result['insights']['clusters']) == 243
    assert len({f['properties']['ward_id'] for f in features}) == 243
    assert 650 < result['insights']['area_km2'] < 800
    assert all(f['properties']['area_km2'] > 0 for f in features)
    assert all(-180 <= f['properties']['longitude'] <= 180 for f in features)
    assert result['insights']['lorenz'][0] == 0
    assert result['insights']['lorenz'][-1] == pytest.approx(1)
    assert gini([5, 5, 5]) == pytest.approx(0)
    assert gini([0, 0, 10]) == pytest.approx(2 / 3)


def test_survey_reports_partial_coverage_and_candidate_bounds():
    data = survey_data()
    assert 60 < data['coverage_percent'] < 90
    assert 7000 < data['area_sqm'] < 8000
    assert data['canopy_count'] == len(data['canopies']['features'])
    assert sum(z['percent'] for z in data['zones']) == pytest.approx(100, abs=.05)
    west, south, east, north = data['bounds']
    for f in data['canopies']['features']:
        lon, lat = f['geometry']['coordinates']
        assert west <= lon <= east and south <= lat <= north


def test_review_updates_preserve_audit_and_run_scope(client):
    body = {'parcel_id': 'BS-P-00002', 'run_id': 'run-one', 'status': 'field_check', 'note': 'Check the shifted northern boundary.'}
    assert client.post('/api/reviews', json=body).status_code == 200
    assert client.post('/api/reviews', json={**body, 'status': 'accepted', 'note': 'Field verification completed and documented.'}).status_code == 200
    assert len(client.get('/api/reviews').json()) == 1
    assert len(client.get('/api/audit').json()) == 2
    assert client.post('/api/reviews', json={**body, 'run_id': 'run-two'}).status_code == 200
    assert len(client.get('/api/reviews').json()) == 2


def test_viewer_cannot_mutate_operations(client):
    response = client.post('/api/tasks', headers={'X-Workspace-Role': 'viewer'}, json={'title': 'Verify boundary', 'assignee': 'Team A'})
    assert response.status_code == 403
    assert client.get('/api/tasks').json() == []


def test_document_roundtrip_and_tamper_detection(client):
    data = b'Demo survey evidence, not an official record.'
    r = client.post('/api/documents', files={'file': ('../../evidence.txt', data, 'text/plain')}, data={'parcel_id': 'BS-P-00002'})
    assert r.status_code == 200
    doc = r.json()
    assert doc['filename'] == 'evidence.txt'
    assert client.get(f"/api/documents/{doc['id']}/download").content == data
    assert client.get(f"/api/documents/{doc['id']}/verify").json()['intact'] is True
    (store.ROOT / 'documents' / doc['id']).write_bytes(b'changed')
    assert client.get(f"/api/documents/{doc['id']}/verify").json()['intact'] is False
    assert client.post('/api/documents', files={'file': ('payload.html', b'<script/>')}).status_code == 400


def test_geofence_state_is_server_tracked_and_persistent(client):
    fence = client.post('/api/geofences', json={'name': 'Test perimeter', 'latitude': 12.97, 'longitude': 77.59, 'radius_m': 100}).json()
    path = f"/api/geofences/{fence['id']}/check"
    assert client.post(path, json={'latitude': 12.97, 'longitude': 77.59}).json()['event'] == 'initial'
    assert client.post(path, json={'latitude': 12.97, 'longitude': 77.59}).json()['event'] == 'unchanged'
    outside = client.post(path, json={'latitude': 12.972, 'longitude': 77.59}).json()
    assert outside['event'] == 'exited' and 220 < outside['distance_m'] < 225
    assert client.post(path, json={'latitude': 12.97, 'longitude': 77.59}).json()['event'] == 'entered'
    assert len(client.get('/api/alerts').json()) == 3
    assert store.get('geofence', fence['id'])['inside'] is True


def test_task_moves_and_invalid_status(client):
    body = {'title': 'Verify survey point', 'assignee': 'Team Alpha', 'category': 'verification'}
    task = client.post('/api/tasks', json=body).json()
    assert client.put('/api/tasks/' + task['id'], json={**body, 'status': 'done'}).json()['status'] == 'done'
    assert client.put('/api/tasks/' + task['id'], json={**body, 'status': 'invented'}).status_code == 422


def test_geotiff_nodata_and_calibration(tmp_path, monkeypatch):
    import rasterio
    from rasterio.transform import from_origin
    import backend.services.survey as module
    monkeypatch.setattr(module, 'CONTEXT', tmp_path)
    path = tmp_path / 'ndvi.tif'
    data = np.full((20, 20), .6, dtype='float32')
    data[:5] = -9999
    with rasterio.open(path, 'w', driver='GTiff', width=20, height=20, count=1, dtype='float32', crs='EPSG:4326', transform=from_origin(77.3, 10.4, .00001, .00001), nodata=-9999) as dst:
        dst.write(data, 1)
    result = analyze_geotiff(path, 'ndvi', 'test')
    assert result['stats']['mean'] == pytest.approx(.6, abs=.002)
    assert result['valid_percent'] == pytest.approx(75)
    assert (tmp_path / 'rasters/test.png').exists()
    with rasterio.open(path, 'r+') as dst:
        dst.write(np.full((20, 20), 40, dtype='float32'), 1)
    with pytest.raises(ValueError, match='calibrated'):
        analyze_geotiff(path, 'ndvi', 'invalid')


def test_weather_failure_never_fabricates_data(tmp_path, monkeypatch):
    import backend.services.environment as module
    import httpx
    monkeypatch.setattr(module, 'CACHE', tmp_path)
    class FailedClient:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def get(self, *args, **kwargs): raise httpx.ConnectError('offline')
    monkeypatch.setattr(module.httpx, 'AsyncClient', FailedClient)
    result = asyncio.run(module.environment(12, 77))
    assert result['available'] is False
    assert 'score' not in result and 'current' not in result
    cached = {'available': True, 'fetched_at': datetime.now(timezone.utc).isoformat(), 'current': {'temperature_2m': 24}, 'delivery': 'live'}
    (tmp_path / '12.000_77.000.json').write_text(json.dumps(cached))
    result = asyncio.run(module.environment(12, 77, refresh=True))
    assert result['delivery'] == 'offline cache'
    assert result['current']['temperature_2m'] == 24


def test_raster_comparison_resamples_real_overlap(tmp_path, monkeypatch):
    import rasterio
    from rasterio.transform import from_origin
    import backend.services.survey as module
    monkeypatch.setattr(module, 'CONTEXT', tmp_path)
    before, after = tmp_path / 'before.tif', tmp_path / 'after.tif'
    for path, value in [(before, .3), (after, .6)]:
        with rasterio.open(path,'w',driver='GTiff',width=20,height=20,count=1,dtype='float32',crs='EPSG:4326',transform=from_origin(77.3,10.4,.00001,.00001),nodata=-9999) as dst:
            dst.write(np.full((20,20),value,dtype='float32'),1)
    result=module.compare_rasters(before,after,'ndvi','difference')
    assert result['mean_delta']==pytest.approx(.3,abs=.001)
    assert result['increase_percent']==100
    assert result['decrease_percent']==0
    assert result['overlap_percent']==100


def test_dated_series_respects_elapsed_days_and_rejects_duplicates(client):
    csv=b'date,value\n2026-01-01,1\n2026-01-03,3\n2026-01-06,6\n2026-01-11,11\n'
    response=client.post('/api/survey/trends',files={'file':('series.csv',csv,'text/csv')})
    assert response.status_code==200
    result=response.json()
    assert result['slope_per_day']==pytest.approx(1)
    assert result['r2']==pytest.approx(1)
    assert result['forecast'][0]['value']==pytest.approx(18)
    invalid=b'date,value\n2026-01-01,1\n2026-01-01,2\n2026-01-03,3\n2026-01-04,4'
    assert client.post('/api/survey/trends',files={'file':('duplicate.csv',invalid)}).status_code==400


def test_local_resource_reservation_is_saved_and_guarded(client):
    body={'name':'RTK GNSS survey kit','provider':'Field unit','category':'equipment'}
    resource=client.post('/api/resources',json=body).json()
    assert client.put('/api/resources/'+resource['id'],json={**body,'status':'reserved'}).json()['status']=='reserved'
    assert client.get('/api/resources').json()[0]['status']=='reserved'
    assert client.put('/api/resources/'+resource['id'],json={**body,'status':'available'},headers={'X-Workspace-Role':'viewer'}).status_code==403
