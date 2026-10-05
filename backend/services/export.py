import csv
import json
from pathlib import Path

EXPORTS = {'harmonized.geojson':'harmonized_parcels.geojson','conflicts.csv':'conflicts.csv',
           'changes.csv':'change_report.csv','summary.json':'run_summary.json'}


def write_exports(result,directory):
    directory = Path(directory); directory.mkdir(parents=True,exist_ok=True)
    (directory/'harmonized_parcels.geojson').write_text(json.dumps(result['layers']['harmonized'],indent=2,allow_nan=False),encoding='utf-8')
    (directory/'run_summary.json').write_text(json.dumps({'run_id':result.get('run_id'),'fingerprint':result['fingerprint'],**result['summary'],'stages':result['stages']},indent=2),encoding='utf-8')
    for key,filename,fields in [('conflicts','conflicts.csv',['id','parcel_id','type','severity','confidence','description','sources','metrics','recommended_action']),
                               ('changes','change_report.csv',['id','parcel_id','type','description','area_sqm','iou','source_ids','area_difference_percent'])]:
        with (directory/filename).open('w',newline='',encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f,fieldnames=fields); writer.writeheader()
            for row in result[key]:
                sanitized = {}
                for field in fields:
                    value = row.get(field)
                    if isinstance(value,(dict,list)): value=json.dumps(value)
                    if isinstance(value,str) and value.startswith(('=','+','-','@')): value="'"+value
                    sanitized[field]=value
                writer.writerow(sanitized)
