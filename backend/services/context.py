"""Optional external context with explicit availability and a dated cache."""
import asyncio
import json
import math
from pathlib import Path
import httpx
from backend.services.operations import timestamp

CACHE = Path(__file__).resolve().parents[1] / 'data' / 'context' / 'site_context'


async def site_context(lat, lon, refresh=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f'{lat:.3f}_{lon:.3f}.json'
    if path.exists() and not refresh:
        return {**json.loads(path.read_text()), 'delivery': 'saved snapshot'}
    async def soil():
        try:
            async with httpx.AsyncClient(timeout=7) as client:
                r = await client.get('https://rest.isric.org/soilgrids/v2.0/properties/query', params={'lon': lon, 'lat': lat, 'property': ['phh2o', 'soc', 'clay', 'sand', 'silt'], 'depth': '0-5cm', 'value': 'mean'})
                r.raise_for_status()
            values = {}
            for layer in r.json().get('properties', {}).get('layers', []):
                raw = layer.get('depths', [{}])[0].get('values', {}).get('mean')
                if raw is not None:
                    values[layer['name']] = raw / 10
            return {'available': bool(values), 'values': values, 'source': 'ISRIC SoilGrids 0–5 cm modeled mean; pH, SOC g/kg, texture %'}
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return {'available': False, 'values': {}, 'source': 'ISRIC SoilGrids', 'note': 'Soil provider unavailable. Upload or enter a laboratory result instead of substituting defaults.'}
    async def infrastructure():
        try:
            query = f'[out:json][timeout:12];(way["highway"~"^(motorway|trunk|primary|secondary|tertiary)$"](around:3000,{lat},{lon});way["natural"="water"](around:3000,{lat},{lon});node["amenity"~"^(hospital|school)$"](around:3000,{lat},{lon}););out center tags;'
            async with httpx.AsyncClient(timeout=16) as client:
                r = await client.post('https://overpass-api.de/api/interpreter', data={'data': query}, headers={'User-Agent': 'BhoomiSync-SIH-Prototype/2.0'})
                r.raise_for_status()
            features=[]
            for e in r.json().get('elements', []):
                center=e.get('center', e)
                if 'lat' not in center or 'lon' not in center: continue
                tags=e.get('tags', {})
                features.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [center['lon'], center['lat']]}, 'properties': {'name': tags.get('name','Unnamed feature'), 'kind': tags.get('highway') or tags.get('amenity') or 'water', 'osm_id': str(e['id'])}})
            return {'available': True, 'count': len(features), 'roads': sum('highway' in e.get('tags',{}) for e in r.json().get('elements',[])), 'water': sum(e.get('tags',{}).get('natural')=='water' for e in r.json().get('elements',[])), 'amenities': sum('amenity' in e.get('tags',{}) for e in r.json().get('elements',[])), 'features': {'type':'FeatureCollection','features':features}, 'source':'OpenStreetMap / Overpass, 3 km search radius. Way centres are representative points, not nearest-boundary distances.'}
        except (httpx.HTTPError, ValueError, KeyError, TypeError):
            return {'available': False, 'source':'OpenStreetMap / Overpass', 'note':'Infrastructure provider unavailable. Absence of a response does not mean absence of infrastructure.'}
    soils, infra = await asyncio.gather(soil(), infrastructure())
    result={'latitude':lat,'longitude':lon,'soil':soils,'infrastructure':infra,'fetched_at':timestamp(),'delivery':'provider response'}
    if path.exists() and not soils['available'] and not infra['available']:
        return {**json.loads(path.read_text()),'delivery':'offline cache'}
    path.write_text(json.dumps(result),encoding='utf-8')
    return result


async def geocode(query):
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r=await client.get('https://geocoding-api.open-meteo.com/v1/search',params={'name':query,'count':5,'language':'en','format':'json'})
            r.raise_for_status()
        return {'results':[{'name':p['name'],'latitude':p['latitude'],'longitude':p['longitude'],'region':', '.join(filter(None,[p.get('admin1'),p.get('country')]))} for p in r.json().get('results',[])], 'source':'GeoNames via Open-Meteo'}
    except (httpx.HTTPError, ValueError, KeyError):
        return {'results':[],'warning':'Place search unavailable; coordinates can be entered directly.'}
