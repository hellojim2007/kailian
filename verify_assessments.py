"""Validate the exam bank's answers, independence, coverage and executable tasks."""
import ast
from collections import Counter
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'dist'))
from grade import grade

bank=json.loads((ROOT/'dist/exams.json').read_text(encoding='utf-8'))
items={x['id']:x for x in bank['items']}
exercises={x['id']:x for x in bank['exercises']}
lessons=json.loads((ROOT/'dist/lessons.json').read_text(encoding='utf-8'))
assert len(bank['exams'])==18
assert Counter(e['kind'] for e in bank['exams'])=={'chapter':12,'cumulative':4,'stage':2}
assert sum(e['minutes'] for e in bank['exams'])==310
assert len(items)==len(bank['items'])
assert len(exercises)==len(bank['exercises'])
used=[i for exam in bank['exams'] for i in exam['itemIds']]
assert len(used)==len(set(used))
assert not set(used)&set(bank['reviewItems'])
assert len(bank['reviewItems'])==24
assert all(Counter(items[i]['chapter'] for i in bank['reviewItems'])[f'c{n:02}']==2 for n in range(1,13))
for exam in bank['exams']:
    selected=[items[i] for i in exam['itemIds']]
    assert sum(x['kind']=='code' for x in selected)>=(3 if exam['kind']=='stage' else 2),exam['id']
    assert any(x['kind']=='output' for x in selected),exam['id']
    if exam['kind']=='chapter':
        expected=set(bank['chapterLessons'][exam['chapters'][0]])
        covered={skill for x in selected for skill in x['skills']}
        assert expected<=covered,(exam['id'],'missing skills',expected-covered)

failures=[]
output_count=0
for item in items.values():
    assert item['prompt'] and item['explanation'] and item['skills'],item['id']
    assert 0<item['points']<=10
    if item['kind']=='choice':
        assert len(set(item['options']))==len(item['options'])
        assert 0<=item['answer']<len(item['options'])
    elif item['kind']=='output':
        exercise={'id':item['id'],'tests':[{'stdout':True,'label':'stdout','expected':''}]}
        result=grade({'lesson':item['id'],'code':item['code'],'action':'run','stdin':''},[exercise])
        output_count+=1
        if not result['ok'] or result['stdout'].strip()!=item['expectedStdout'].strip():
            failures.append((item['id'],'output answer',item['expectedStdout'],result))
    elif item['kind']=='code':
        assert item['exerciseId'] in exercises,item['id']
    else:
        raise AssertionError(item['kind'])

case_count=0
for exercise in exercises.values():
    assert len(exercise['tests'])>=3,exercise['id']
    assert exercise['task'] and exercise['signature']
    result=grade({'lesson':exercise['id'],'code':exercise['solution'],'action':'submit'},list(exercises.values()))
    case_count+=len(exercise['tests'])
    if not result['ok']:failures.append((exercise['id'],'reference',result))
    # A deliberately blank function/program must not earn full credit.
    tree=ast.parse(exercise['solution'])
    for node in ast.walk(tree):
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)):
            node.body=[ast.Return(value=ast.Constant(value=None))]
    wrong=ast.unparse(tree) if any(isinstance(x,ast.FunctionDef) for x in ast.walk(tree)) else 'print(0)'
    result=grade({'lesson':exercise['id'],'code':wrong,'action':'submit'},list(exercises.values()))
    if result['ok']:failures.append((exercise['id'],'empty implementation incorrectly accepted'))

assert not set(exercises)&{x['id'] for x in lessons}
print(f"18 independent papers / {len(items)} new questions / {len(exercises)} coding tasks / {case_count} checks / {output_count} exact output answers")
print('FAILURES',json.dumps(failures,ensure_ascii=False))
assert not failures
