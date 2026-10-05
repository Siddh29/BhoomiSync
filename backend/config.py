import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data'
DEMO_MODE = os.getenv('BHOOMISYNC_DEMO_MODE', 'true').lower() == 'true'
WEIGHTS = {'iou': .45, 'proximity': .20, 'area_similarity': .15, 'shape_similarity': .10, 'attribute_similarity': .10}
HIGH_CONFIDENCE = 85
LOW_CONFIDENCE = 60
CANDIDATE_RADIUS_M = 12
BOUNDARY_LIMIT_M = 2
AREA_LIMIT_PERCENT = 5
GNSS_LIMIT_M = 2
OVERLAP_MIN_SQM = .1
AMBIGUITY_MARGIN = 5
BUILDING_MATCH_IOU = .3
BUILDING_UNCHANGED_IOU = .9
SCHEMA_VERSION = 1
