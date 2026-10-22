"""Execute every new printed answer; validate route order against actual units."""
import json
from pathlib import Path
import sys
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'dist'))
from grade import grade
lessons=json.loads((root/'dist/lessons.json').read_text(encoding='utf-8'))
course=json.loads((root/'dist/course.json').read_text(encoding='utf-8'))
route=course['studyRoute']['lessonIds']
assert len(route)==72 and len(set(route))==72
assert set(route)=={l['id'] for l in lessons}
by_id={l['id']:l for l in lessons}
seen=set();cards={};failures=[]
for ident in route:
    l=by_id[ident];g=l['guide']
    assert g['position']==route.index(ident)+1
    assert set(g['requires'])<=seen,(ident,g['requires'])
    assert len(g['steps'])>=3 and g['reason'] and g['warmup']['prompt']
    assert g['contract'] and all(isinstance(s,str) and s for s in g['contract'])
    assert g['warmup']['code'].strip() and g['warmup']['expected'].strip()
    result=grade({'lesson':ident,'code':g['warmup']['code'],'action':'run','stdin':''},lessons)
    if not result.get('ok') or result.get('stdout','').strip()!=g['warmup']['expected'].strip():
        failures.append((ident,'warmup',g['warmup']['expected'],result))
    for card in g['cards']:
        assert card['body'] and card['syntax'] and card['source'].startswith('https://')
        assert card['firstLessonId'] in seen|{ident},(ident,card['key'])
        if card['key'] not in cards:
            cards[card['key']]=card
            result=grade({'lesson':ident,'code':card['code'],'action':'run','stdin':''},lessons)
            if not result.get('ok') or result.get('stdout','').strip()!=card['output'].strip():
                failures.append((ident,card['key'],card['output'],result))
    seen.add(ident)
assert sum(l['guide']['track']=='core' for l in lessons)==53
assert sum(l['guide']['track']=='extension' for l in lessons)==19
assert route.index('p4')<route.index('py05')<route.index('py06')
assert route.index('t3')<route.index('t5')<route.index('t6')<route.index('t4')
assert route.index('pt26')<route.index('pt06')<route.index('pt08')<route.index('pt10')
assert not any(l['guide']['labEnabled'] for l in lessons if l['runtime']=='python')
assert sum(l['guide']['labEnabled'] for l in lessons)==5
assert {'string','split','chain','function'}<={c['key'] for c in by_id['py06']['guide']['cards']}
print(f"{len(cards)} unique API examples / 72 warmup reference outputs / 72 explicit route handovers")
print('FAILURES',json.dumps(failures,ensure_ascii=False))
assert not failures
