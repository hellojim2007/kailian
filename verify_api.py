"""End-to-end smoke checks against the user's running loopback learning server."""
import json
from pathlib import Path
import urllib.request

ROOT=Path(__file__).resolve().parent
from catalog import load_catalog
catalogue=load_catalog(ROOT/'dist')

with urllib.request.urlopen('http://127.0.0.1:8766/api/health',timeout=5) as response:
    health=json.load(response)
assert health['runtime']=='native' and health['exerciseCount']==len(catalogue)
ids=['py13','pt12','t5','pt26']
for runtime in ['python','torch']:
    item=next((x for x in catalogue if x['id'].startswith('ax-') and x['runtime']==runtime),None)
    if item:ids.append(item['id'])
for ident in ids:
    exercise=next(x for x in catalogue if x['id']==ident)
    request=urllib.request.Request('http://127.0.0.1:8766/api/run',
        data=json.dumps({'lesson':ident,'code':exercise['solution'],'action':'submit'}).encode('utf-8'),
        headers={'Content-Type':'application/json','Origin':'http://127.0.0.1:8766'})
    with urllib.request.urlopen(request,timeout=35) as response:
        result=json.load(response)
    assert result['ok'],(ident,result)
    print('PASS HTTP',ident,len(result['tests']),flush=True)
