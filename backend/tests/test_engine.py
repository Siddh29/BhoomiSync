import pytest
from shapely.geometry import box, Polygon
from shapely.affinity import translate
from backend.services.crs import reproject, analysis_crs
from backend.services.matching import geometry_metrics, weighted_score, match
from backend.services.topology import repair, overlaps
from backend.services.attributes import normalize, map_attributes, attribute_similarity
from backend.services.confidence import classify


def record(id,geometry,survey='SY-1'):
    return {'id':id,'geometry':geometry,'attributes':{'survey_number':survey}}


def test_crs_roundtrip_and_metric_area():
    p=box(550000,1430000,550030,1430030)
    wgs=reproject(p,'EPSG:32643','EPSG:4326')
    result=reproject(wgs,'EPSG:4326',analysis_crs(wgs))
    assert result.area==pytest.approx(900,abs=1e-5)
    assert result.hausdorff_distance(p)<1e-5


def test_known_geometry_metrics():
    a=box(0,0,10,10); b=translate(a,xoff=2)
    m=geometry_metrics(a,b)
    assert m['iou']==pytest.approx(80/120)
    assert m['centroid_distance_m']==2
    assert m['boundary_distance_m']==2
    assert m['area_similarity']==1
    assert geometry_metrics(a,box(0,0,20,10))['area_similarity']==.5


def test_missing_signals_renormalized():
    assert weighted_score({'iou':1,'attribute_similarity':None})==100
    assert weighted_score({})==0


def test_index_matching_one_to_one():
    base=[record('a',box(0,0,10,10)),record('b',box(20,0,30,10),'SY-2')]
    source=[record('s2',box(20.2,0,30.2,10),'SY-2'),record('s1',box(.2,0,10.2,10)),record('orphan',box(200,0,210,10))]
    assigned,unmatched=match(base,source)
    assert assigned[0]['index']==1 and assigned[1]['index']==0
    assert unmatched==[2]
    assert len({v['index'] for v in assigned.values()})==len(assigned)


def test_repair_and_overlap():
    invalid=Polygon([(0,0),(10,10),(0,10),(10,0),(0,0)])
    fixed,ops=repair(invalid)
    assert fixed.is_valid and fixed.area==50 and ops[0]['operation']=='make_valid'
    assert not invalid.is_valid
    hits=overlaps([box(0,0,10,10),box(9,0,19,10),box(50,0,60,10)])
    assert len(hits)==1 and hits[0][2]==10


def test_attribute_normalization_and_suggestions():
    attrs,mapping,suggestions=map_attributes({'Survey Number':' sy-001 ','PID':'M1','recored_area':200})
    assert attrs['survey_number']==' sy-001 '
    assert mapping['PID']=='municipal_property_id'
    assert normalize('SY-001')==normalize(' sy 001 ')
    assert attribute_similarity(attrs,{'survey_number':'SY001'})==1
    assert attribute_similarity({},attrs) is None
    assert 'recored_area' not in attrs
    assert suggestions['recored_area']['applied'] is False


def test_confidence_forces_review():
    assert classify(95,[])[1]=='MATCHED'
    assert classify(95,[{'type':'AREA_MISMATCH'}])==(87,'REVIEW_REQUIRED')
    assert classify(0,[{'type':'UNMATCHED_SOURCE'}],True)[1]=='CONFLICT'
