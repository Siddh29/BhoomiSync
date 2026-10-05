import re
from rapidfuzz.fuzz import ratio

ALIASES = {
    'survey_number': ['survey_number', 'survey_no', 'surveyNumber', 'Survey Number', 'sy_no', 'plot_number'],
    'parcel_id': ['parcel_id', 'parcel_no', 'plot_id'],
    'municipal_property_id': ['municipal_property_id', 'property_id', 'PID', 'municipal_pid'],
    'revenue_record_id': ['revenue_record_id', 'record_id'],
    'owner_name': ['owner_name', 'owner', 'holder'],
    'land_use': ['land_use', 'usage', 'landuse'],
    'recorded_area_sqm': ['recorded_area_sqm', 'recorded_area', 'area_m2'],
}


def normalize(value):
    return re.sub(r'[^a-z0-9]', '', str(value).casefold()) if value is not None else ''


def map_attributes(properties):
    values, mapping, suggestions = {}, {}, {}
    for key, value in properties.items():
        canonical = next((c for c, aliases in ALIASES.items() if normalize(key) in [normalize(a) for a in aliases]), None)
        if canonical:
            mapping[key] = canonical
            if value not in (None, ''):
                values[canonical] = value
        else:
            scores = [(ratio(normalize(key), normalize(alias)), c) for c, aliases in ALIASES.items() for alias in aliases]
            score, candidate = max(scores)
            if score >= 70:
                suggestions[key] = {'suggested_field': candidate, 'similarity': round(score / 100, 3), 'applied': False}
    return values, mapping, suggestions


def attribute_similarity(a, b):
    signals = [ratio(normalize(a[k]), normalize(b[k])) / 100 for k in ('survey_number', 'owner_name', 'land_use') if normalize(a.get(k)) and normalize(b.get(k))]
    return sum(signals) / len(signals) if signals else None
