"""UrbanScope-derived ward analytics. Real boundaries; explicitly synthetic value proxy."""
import json
import math
from functools import lru_cache
from pathlib import Path
import numpy as np
from pyproj import Geod, Transformer
from shapely.geometry import shape, mapping
from shapely.ops import transform
from shapely import make_valid

CONTEXT = Path(__file__).resolve().parents[1] / 'data' / 'context'
GEOD = Geod(ellps='WGS84')
TO_METRES = Transformer.from_crs(4326, 32643, always_xy=True).transform
TO_GEO = Transformer.from_crs(32643, 4326, always_xy=True).transform


def gini(values):
    values = np.sort(np.asarray(values, dtype=float))
    if not len(values) or values.sum() <= 0:
        return 0.0
    n = len(values)
    return float((2 * np.sum(np.arange(1, n + 1) * values) / (n * values.sum())) - (n + 1) / n)


def cluster(matrix, k=4):
    """Deterministic k-means, standardized inputs, no model-download dependency."""
    std = matrix.std(axis=0)
    data = (matrix - matrix.mean(axis=0)) / np.where(std > 1e-9, std, 1)
    rng = np.random.default_rng(42)
    centers = [data[rng.integers(len(data))]]
    for _ in range(k - 1):
        dist = np.min(((data[:, None] - np.array(centers)[None]) ** 2).sum(axis=2), axis=1)
        centers.append(data[int(np.argmax(dist))])
    centers = np.array(centers)
    labels = np.zeros(len(data), dtype=int)
    for _ in range(100):
        next_labels = np.argmin(((data[:, None] - centers[None]) ** 2).sum(axis=2), axis=1)
        if np.array_equal(labels, next_labels) and _ > 0:
            break
        labels = next_labels
        for i in range(k):
            if np.any(labels == i):
                centers[i] = data[labels == i].mean(axis=0)
    return labels


@lru_cache(maxsize=1)
def city_data():
    raw = json.loads((CONTEXT / 'bbmp.geojson').read_text(encoding='utf-8'))
    rows, geometries, centroids = [], [], []
    for index, feature in enumerate(raw['features']):
        geom = make_valid(shape(feature['geometry']))
        projected = transform(TO_METRES, geom)
        center = transform(TO_GEO, projected.centroid)
        props = feature['properties']
        _, _, distance = GEOD.inv(77.5913, 12.9797, center.x, center.y)
        rows.append({'ward_id': str(props.get('KGISWardID', index)), 'ward_no': str(props.get('KGISWardNo', index + 1)),
                     'name': props.get('KGISWardName', f'Ward {index + 1}'),
                     'area_km2': projected.area / 1e6, 'distance_km': distance / 1000,
                     'longitude': center.x, 'latitude': center.y})
        geometries.append(mapping(geom.simplify(.000025, preserve_topology=True)))
        centroids.append([projected.centroid.x, projected.centroid.y])
    areas = np.array([r['area_km2'] for r in rows])
    distances = np.array([r['distance_km'] for r in rows])
    values = np.clip(55000 * (np.median(areas) / areas) ** .45 / (1 + .06 * distances), 12000, 160000)
    deviation = (values - np.median(values)) / np.median(values)
    zscores = (values - values.mean()) / max(values.std(), 1)
    # Binary eight-nearest-neighbour Gi* including self; normal approximation.
    xy = np.asarray(centroids)
    neighbours = np.argsort(((xy[:, None] - xy[None]) ** 2).sum(axis=2), axis=1)[:, :9]
    n = len(values)
    local_z = np.array([(values[ids].sum() - values.mean() * len(ids)) /
                        (values.std() * math.sqrt((n * len(ids) - len(ids) ** 2) / (n - 1))) for ids in neighbours])
    labels = cluster(np.column_stack([np.log(values), deviation, areas, distances, local_z]))
    order = sorted(set(labels), key=lambda c: float(values[labels == c].mean()), reverse=True)
    names = ['Compact central', 'Established urban', 'Mixed transition', 'Outer extensive']
    label_map = {int(c): i for i, c in enumerate(order)}
    features = []
    for i, (row, geometry) in enumerate(zip(rows, geometries)):
        p = math.erfc(abs(float(local_z[i])) / math.sqrt(2))
        c = label_map[int(labels[i])]
        row.update(value_proxy=round(float(values[i]), 2), deviation=round(float(deviation[i]), 4),
                   zscore=round(float(zscores[i]), 3), cluster=c, cluster_name=names[c],
                   gi_z=round(float(local_z[i]), 3), gi_p=round(p, 5),
                   significance='hotspot' if p < .05 and local_z[i] > 0 else 'coldspot' if p < .05 else 'neutral',
                   extrusion_m=round(math.sqrt(float(values[i])) * 10, 1))
        features.append({'type': 'Feature', 'id': i, 'properties': row, 'geometry': geometry})
    slope, intercept = np.polyfit(distances, values, 1)
    correlation = float(np.corrcoef(distances, values)[0, 1])
    sorted_values = np.sort(values)
    lorenz = [0.0] + (np.cumsum(sorted_values) / sorted_values.sum()).tolist()
    clusters = [{'id': c, 'name': name, 'count': sum(r['cluster'] == c for r in rows),
                 'mean_proxy': round(float(np.mean([r['value_proxy'] for r in rows if r['cluster'] == c])), 2)}
                for c, name in enumerate(names)]
    insights = {'count': n, 'area_km2': round(float(areas.sum()), 2), 'gini': round(gini(values), 4),
                'hotspots': sum(r['significance'] == 'hotspot' for r in rows),
                'coldspots': sum(r['significance'] == 'coldspot' for r in rows),
                'proxy_median': round(float(np.median(values)), 2),
                'top_decile_share': round(float(sorted_values[-math.ceil(n * .1):].sum() / values.sum()), 4),
                'bottom_half_share': round(float(sorted_values[:n // 2].sum() / values.sum()), 4),
                'regression': {'slope': float(slope), 'intercept': float(intercept), 'r2': correlation ** 2, 'correlation': correlation},
                'lorenz': lorenz, 'clusters': clusters,
                'ranking': sorted(rows, key=lambda r: r['value_proxy'], reverse=True),
                'provenance': {'geometry': 'DataMeet Municipal Spatial Data / Bengaluru wards',
                               'url': 'https://github.com/datameet/Municipal_Spatial_Data/tree/master/Bangalore',
                               'metric': 'UrbanScope area/accessibility proxy; not official land prices or observed growth',
                               'significance': 'Gi* normal approximation, binary 8-neighbour weights plus self; exploratory, uncorrected p<0.05',
                               'snapshot_note': 'Imported ward snapshot; not a claim about current administrative boundaries'}}
    return {'geojson': {'type': 'FeatureCollection', 'features': features}, 'insights': insights}
