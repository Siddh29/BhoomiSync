"""Measured RGB survey analysis adapted from Landroid and kv; no synthetic NDVI."""
import json
import math
from functools import lru_cache
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import shape, mapping, Polygon
from shapely.ops import transform
from pyproj import Transformer

ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / 'frontend' / 'public' / 'survey'
CONTEXT = ROOT / 'backend' / 'data' / 'context'


def tile_lon(x, z):
    return x / 2 ** z * 360 - 180


def tile_lat(y, z):
    return math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / 2 ** z))))


def lon_pixel(lon, z):
    return (lon + 180) / 360 * 2 ** z * 256


def lat_pixel(lat, z):
    return (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * 2 ** z * 256


def canopy_segments(rgb, valid):
    """Excess-green mask and distance-transform watershed; candidate crowns, not verified trees."""
    r, g, b = rgb.astype(float).transpose(2, 0, 1)
    gcc = np.divide(g, r + g + b, out=np.zeros_like(g), where=(r + g + b) > 0)
    mask = np.uint8((g > r * 1.07) & (g > b * 1.05) & (gcc > .355) & valid) * 255
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    distance = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
    if not distance.max():
        return gcc, mask, []
    peaks = np.uint8((distance == cv2.dilate(distance, np.ones((7, 7), np.uint8))) & (distance > 1.8))
    _, markers = cv2.connectedComponents(peaks)
    markers = markers + 1
    markers[(opening > 0) & (peaks == 0)] = 0
    cv2.watershed(cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR), markers)
    crowns = []
    for label in range(2, int(markers.max()) + 1):
        region = (markers == label) & (mask > 0)
        yy, xx = np.where(region)
        if 8 <= len(xx) <= 5000:
            crowns.append({'x': float(xx.mean()), 'y': float(yy.mean()), 'pixels': len(xx)})
    return gcc, mask, crowns


@lru_cache(maxsize=1)
def survey_data():
    original = json.loads((CONTEXT / 'survey_boundary_original.geojson').read_text())
    line = original['features'][0]['geometry']['coordinates']
    projected = Polygon([(c[0], c[1]) for c in line])
    to_geo = Transformer.from_crs(32643, 4326, always_xy=True).transform
    polygon = transform(to_geo, projected)
    z = 18
    files = list((ASSETS / 'ortho_tiles' / str(z)).glob('*/*.png'))
    xs, ys = [int(p.parent.name) for p in files], [int(p.stem) for p in files]
    x0, y0 = min(xs), min(ys)
    width, height = (max(xs) - x0 + 1) * 256, (max(ys) - y0 + 1) * 256
    mosaic = Image.new('RGBA', (width, height))
    for p in files:
        mosaic.paste(Image.open(p).convert('RGBA'), ((int(p.parent.name) - x0) * 256, (int(p.stem) - y0) * 256))
    array = np.asarray(mosaic)
    # Scope analytical results to the actual boundary, not the whole tile rectangle.
    area_mask = Image.new('L', (width, height))
    points = [(lon_pixel(x, z) - x0 * 256, lat_pixel(y, z) - y0 * 256) for x, y in polygon.exterior.coords]
    ImageDraw.Draw(area_mask).polygon(points, fill=255)
    valid = (array[:, :, 3] > 0) & (np.asarray(area_mask) > 0)
    gcc, mask, crowns = canopy_segments(array[:, :, :3], valid)
    center = polygon.centroid
    gsd = 156543.03392804097 * math.cos(math.radians(center.y)) / 2 ** z
    median_area = float(np.median([c['pixels'] for c in crowns])) if crowns else 0
    features = []
    for i, crown in enumerate(crowns):
        lon = tile_lon(x0 + crown['x'] / 256, z)
        lat = tile_lat(y0 + crown['y'] / 256, z)
        features.append({'type': 'Feature', 'properties': {'id': f'CROWN-{i + 1:03}', 'area_sqm': round(crown['pixels'] * gsd ** 2, 2),
                          'small_crown': crown['pixels'] < median_area * .5}, 'geometry': {'type': 'Point', 'coordinates': [lon, lat]}})
    values = gcc[valid]
    zone_bounds = [(0, .32), (.32, .355), (.355, .4), (.4, 1.01)]
    colors = [(170, 137, 107), (224, 184, 99), (115, 191, 128), (29, 116, 94)]
    names = ['Bare / low greenness', 'Mixed cover', 'Green vegetation', 'High greenness']
    zone_image = np.zeros((height, width, 4), dtype=np.uint8)
    zones = []
    for (low, high), color, name in zip(zone_bounds, colors, names):
        selected = (gcc >= low) & (gcc < high) & valid
        zone_image[selected] = [*color, 195]
        zones.append({'name': name, 'percent': round(100 * int(selected.sum()) / max(1, len(values)), 2), 'color': '#%02x%02x%02x' % color})
    ASSETS.mkdir(exist_ok=True)
    mosaic.save(ASSETS / 'mosaic.png')
    Image.fromarray(zone_image).save(ASSETS / 'zones.png')
    vegetation = np.zeros_like(zone_image)
    vegetation[mask > 0] = [68, 224, 160, 190]
    Image.fromarray(vegetation).save(ASSETS / 'vegetation.png')
    coords = [[tile_lon(x0, z), tile_lat(y0, z)], [tile_lon(max(xs) + 1, z), tile_lat(y0, z)],
              [tile_lon(max(xs) + 1, z), tile_lat(max(ys) + 1, z)], [tile_lon(x0, z), tile_lat(max(ys) + 1, z)]]
    boundary = {'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'name': 'Kallapuram survey'}, 'geometry': mapping(polygon)}]}
    return {'id': 'kallapuram', 'name': 'Kallapuram field survey', 'boundary': boundary,
            'center': [center.x, center.y], 'bounds': list(polygon.bounds), 'image_coordinates': coords,
            'area_sqm': round(projected.area, 2), 'perimeter_m': round(projected.length, 2),
            'area_acres': round(projected.area / 4046.8564224, 3), 'source_crs': 'EPSG:32643', 'display_crs': 'EPSG:4326',
            'gsd_m': round(gsd, 3), 'valid_pixels': int(valid.sum()), 'coverage_percent': round(min(100, float(valid.sum() * gsd * gsd / projected.area * 100)), 1),
            'vegetation_percent': round(100 * np.count_nonzero(mask) / max(1, int(valid.sum())), 1),
            'mean_gcc': round(float(values.mean()), 4) if len(values) else None, 'zones': zones,
            'canopies': {'type': 'FeatureCollection', 'features': features}, 'canopy_count': len(features),
            'small_canopies': sum(f['properties']['small_crown'] for f in features),
            'density_per_acre': round(len(features) / (projected.area / 4046.8564224), 1),
            'provenance': {'imagery': 'Local orthomosaic tiles imported from kv; capture date not supplied',
                           'boundary': 'kv boundary reprojected from declared EPSG:32643; closed LineString interpreted as survey polygon',
                           'method': 'RGB green-chromatic coordinate + excess-green threshold + watershed candidate crowns (Landroid/kv)',
                           'limitations': 'RGB greenness is not NDVI. Small crowns are size outliers, not a diagnosis of tree stress. No calibrated DEM or historical imagery supplied.'}}


def analyze_geotiff(path, role, asset_id):
    import rasterio
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    with rasterio.open(path) as source:
        if source.crs is None:
            raise ValueError('GeoTIFF must declare its CRS')
        with WarpedVRT(source, crs='EPSG:4326') as raster:
            factor = min(1, 1024 / max(raster.width, raster.height))
            w, h = max(1, int(raster.width * factor)), max(1, int(raster.height * factor))
            indexes = list(range(1, min(3, raster.count) + 1)) if role == 'ortho' else [1]
            data = raster.read(indexes=indexes, out_shape=(len(indexes), h, w), out_dtype='float32', masked=True, resampling=Resampling.average)
            bounds = raster.bounds
        source_crs = str(source.crs)
    valid = ~np.ma.getmaskarray(data[0]) & np.isfinite(data[0].filled(np.nan))
    values = np.asarray(data[0].filled(0), dtype=float)
    if not valid.any():
        raise ValueError('No valid pixels in the supplied raster')
    if role == 'ndvi' and (values[valid].min() < -1.01 or values[valid].max() > 1.01):
        raise ValueError('NDVI raster must contain calibrated values between -1 and 1')
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    stats = {'min': round(float(values[valid].min()), 3), 'max': round(float(values[valid].max()), 3), 'mean': round(float(values[valid].mean()), 3)}
    zones = []
    if role == 'ortho':
        if data.shape[0] < 3:
            raise ValueError('Orthomosaic needs at least three RGB bands')
        rgb = np.asarray(data[:3].filled(0)).transpose(1, 2, 0)
        if rgb.max() > 255:
            rgb = rgb / max(1, np.percentile(rgb, 99)) * 255
        rgba[:, :, :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    else:
        cuts = [-1.01, .2, .4, .6, 1.01] if role == 'ndvi' else np.linspace(stats['min'] - .001, stats['max'] + .001, 5)
        colors = [(180, 121, 91), (235, 185, 76), (104, 189, 138), (28, 114, 108)]
        for i, color in enumerate(colors):
            mask = (values >= cuts[i]) & (values < cuts[i + 1]) & valid
            rgba[mask, :3] = color
            zones.append({'name': ['Bare / stressed', 'Sparse', 'Healthy', 'Dense'][i] if role == 'ndvi' else f'Band {i+1}',
                          'percent': round(float(mask.sum() / valid.sum() * 100), 2), 'color': '#%02x%02x%02x' % color})
    rgba[valid, 3] = 230
    dest = CONTEXT / 'rasters'
    dest.mkdir(exist_ok=True)
    Image.fromarray(rgba).save(dest / f'{asset_id}.png')
    return {'id': asset_id, 'role': role, 'source_crs': source_crs, 'stats': stats, 'zones': zones,
            'valid_percent': round(float(valid.mean() * 100), 1), 'image_url': f'/api/survey/rasters/{asset_id}/image',
            'image_coordinates': [[bounds.left, bounds.top], [bounds.right, bounds.top], [bounds.right, bounds.bottom], [bounds.left, bounds.bottom]],
            'note': ('RGB preview; listed statistics describe the first (red) band. Resampled to at most 1024 pixels.' if role == 'ortho'
                     else 'Calibrated NDVI preview; listed statistics describe valid index pixels.' if role == 'ndvi'
                     else 'Elevation preview resampled to at most 1024 pixels; units follow the supplied raster metadata.')}


def compare_rasters(before_path, after_path, role, result_id):
    """Compare real co-registered valid pixels, resampling both to one WGS84 grid."""
    import rasterio
    from rasterio.vrt import WarpedVRT
    from rasterio.enums import Resampling
    with rasterio.open(before_path) as source:
        with WarpedVRT(source, crs='EPSG:4326') as first:
            factor=min(1,768/max(first.width,first.height))
            w,h=max(1,int(first.width*factor)),max(1,int(first.height*factor))
            transform=first.transform @ first.transform.scale(first.width/w,first.height/h)
            indexes=[1,2,3] if role=='ortho' else [1]
            a=first.read(indexes=indexes,out_shape=(len(indexes),h,w),out_dtype='float32',masked=True,resampling=Resampling.average)
            bounds=first.bounds
        with rasterio.open(after_path) as other:
            with WarpedVRT(other,crs='EPSG:4326',transform=transform,width=w,height=h,resampling=Resampling.average,nodata=float('nan')) as second:
                b=second.read(indexes=indexes,out_dtype='float32',masked=True)
    valid=~np.ma.getmaskarray(a).any(axis=0)&~np.ma.getmaskarray(b).any(axis=0)&np.isfinite(a.filled(np.nan)).all(axis=0)&np.isfinite(b.filled(np.nan)).all(axis=0)
    if not valid.any(): raise ValueError('The rasters have no overlapping valid pixels')
    av=a.filled(0);bv=b.filled(0)
    if role=='ortho':
        av=av[1]/np.maximum(av.sum(axis=0),1e-6);bv=bv[1]/np.maximum(bv.sum(axis=0),1e-6);threshold=.03;unit='RGB greenness'
    else:
        av,bv=av[0],bv[0];threshold=.1 if role=='ndvi' else .5;unit='NDVI' if role=='ndvi' else 'elevation raster units'
    delta=bv-av
    rgba=np.zeros((h,w,4),dtype=np.uint8)
    rgba[valid]=[172,193,183,110]
    rgba[valid&(delta>threshold)]=[110,215,168,230]
    rgba[valid&(delta<-threshold)]=[232,145,109,230]
    dest=CONTEXT/'rasters';dest.mkdir(exist_ok=True)
    Image.fromarray(rgba).save(dest/f'{result_id}.png')
    return {'id':result_id,'role':role,'image_url':f'/api/survey/rasters/{result_id}/image',
            'image_coordinates':[[bounds.left,bounds.top],[bounds.right,bounds.top],[bounds.right,bounds.bottom],[bounds.left,bounds.bottom]],
            'valid_pixels':int(valid.sum()),'overlap_percent':round(float(valid.mean()*100),1),
            'mean_delta':round(float(delta[valid].mean()),4),
            'increase_percent':round(float((valid&(delta>threshold)).sum()/valid.sum()*100),2),
            'decrease_percent':round(float((valid&(delta<-threshold)).sum()/valid.sum()*100),2),
            'threshold':threshold,'unit':unit,
            'note':'Latest minus baseline on overlapping valid pixels. Changes can reflect acquisition conditions or registration error; they are not legal encroachment or biological diagnoses.'}
