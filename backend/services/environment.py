"""Observed weather and explicit, reproducible environmental indicators. No random fallback."""
import json
import math
from datetime import datetime, timezone
from pathlib import Path
import httpx

CACHE = Path(__file__).resolve().parents[1] / 'data' / 'context' / 'weather'


def now():
    return datetime.now(timezone.utc).isoformat()


async def environment(lat, lon, refresh=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f'{lat:.3f}_{lon:.3f}.json'
    cached = json.loads(path.read_text()) if path.exists() else None
    age = (datetime.now(timezone.utc) - datetime.fromisoformat(cached['fetched_at'])).total_seconds() if cached else math.inf
    if cached and age < 3600 and not refresh:
        return {**cached, 'delivery': 'cached', 'cache_age_seconds': round(age)}
    params = {'latitude': lat, 'longitude': lon, 'current': 'temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m,weather_code',
              'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,et0_fao_evapotranspiration',
              'hourly': 'soil_moisture_0_to_1cm', 'past_days': 30, 'forecast_days': 7, 'timezone': 'Asia/Kolkata'}
    try:
        async with httpx.AsyncClient(timeout=18) as client:
            response = await client.get('https://api.open-meteo.com/v1/forecast', params=params)
            response.raise_for_status()
        raw = response.json()
        today = raw['current']['time'][:10]
        daily = [{key: values[i] for key, values in raw['daily'].items()} for i in range(len(raw['daily']['time']))]
        history = [r for r in daily if r['time'] < today]
        forecast = [r for r in daily if r['time'] >= today]
        hourly = raw.get('hourly', {})
        pairs = [(t, v) for t, v in zip(hourly.get('time', []), hourly.get('soil_moisture_0_to_1cm', [])) if t <= raw['current']['time'] and v is not None]
        moisture = pairs[-1][1] * 100 if pairs else None
        rain = sum(r['precipitation_sum'] or 0 for r in history)
        temp = raw['current']['temperature_2m']
        # Scenario thresholds, not a trained crop, yield, price, or legal-risk model.
        components = [{'name': 'Thermal comfort', 'value': round(max(0, 100 - abs(temp - 26) * 5)), 'weight': 35},
                      {'name': 'Recent rainfall', 'value': round(min(100, rain / 100 * 100)), 'weight': 35}]
        if moisture is not None:
            components.append({'name': 'Surface moisture', 'value': round(min(100, moisture / 35 * 100)), 'weight': 30})
        score = round(sum(x['value'] * x['weight'] for x in components) / sum(x['weight'] for x in components))
        risks = []
        if rain < 30 and (moisture is None or moisture < 20):
            risks.append({'level': 'high', 'title': 'Dry conditions', 'detail': '30-day rain below 30 mm with low or unavailable surface moisture.'})
        if temp > 32:
            risks.append({'level': 'medium', 'title': 'Heat exposure', 'detail': 'Current air temperature exceeds the 32 °C scenario threshold.'})
        if any((r['precipitation_sum'] or 0) > 40 for r in forecast):
            risks.append({'level': 'medium', 'title': 'Heavy rain outlook', 'detail': 'At least one forecast day exceeds 40 mm; inspect drainage.'})
        crops = [{'name': 'Millets', 'reason': 'Low-rainfall scenario'}] if rain < 80 else [{'name': 'Maize', 'reason': 'Moderate rainfall scenario'}]
        if rain > 100 and temp > 25:
            crops.append({'name': 'Rice', 'reason': 'Warm, wet scenario; irrigation and soil suitability still need checking'})
        result = {'latitude': lat, 'longitude': lon, 'fetched_at': now(), 'delivery': 'live', 'available': True,
                  'current': raw['current'], 'units': raw['current_units'], 'history': history, 'forecast': forecast,
                  'rain_30d_mm': round(rain, 1), 'soil_moisture_percent': round(moisture, 1) if moisture is not None else None,
                  'score': score, 'components': components, 'risks': risks, 'crop_scenarios': crops,
                  'provenance': 'Open-Meteo gridded weather/model estimates; surface soil layer 0–1 cm. Not an on-site sensor.',
                  'method': 'Transparent temperature/rainfall/moisture scenario index. No NDVI, soil pH, crop yield or land price inferred.'}
        path.write_text(json.dumps(result), encoding='utf-8')
        return result
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        if cached:
            return {**cached, 'delivery': 'offline cache', 'cache_age_seconds': round(age), 'warning': 'Weather refresh unavailable; showing the dated saved response.'}
        return {'available': False, 'latitude': lat, 'longitude': lon, 'fetched_at': now(), 'delivery': 'unavailable',
                'warning': 'Weather provider is unavailable. No observations have been fabricated.'}
