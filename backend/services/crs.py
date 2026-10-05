from functools import lru_cache
from pyproj import CRS, Transformer
from shapely.ops import transform


@lru_cache(maxsize=32)
def transformer(source, target):
    return Transformer.from_crs(source, target, always_xy=True)


def reproject(geometry, source, target):
    if CRS(source) == CRS(target):
        return geometry
    return transform(transformer(source, target).transform, geometry)


def analysis_crs(geometry_wgs84):
    c = geometry_wgs84.centroid
    if not (-180 <= c.x <= 180 and -80 <= c.y <= 84):
        raise ValueError('Input outside supported UTM latitude/longitude range')
    zone = min(60, max(1, int((c.x + 180) // 6) + 1))
    return f'EPSG:{32600 + zone if c.y >= 0 else 32700 + zone}'
