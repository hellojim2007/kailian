"""Independent Python curriculum audit. Does not modify the application or progress."""
import contextlib
import copy
import io
import json
import math
import os
from pathlib import Path
import random
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'dist'))
from grade import execute, grade

LESSONS = [x for x in json.loads((ROOT / 'dist/lessons.json').read_text(encoding='utf-8')) if x['runtime'] == 'python']
BY_ID = {x['id']: x for x in LESSONS}
RNG = random.Random(491827)
checks = 0
issues = []


def check(value, expected, label):
    global checks
    checks += 1
    if isinstance(expected, float):
        good = math.isclose(value, expected, rel_tol=1e-10, abs_tol=1e-10)
    else:
        good = value == expected
    if not good:
        issues.append((label, repr(value), repr(expected)))


def raises(call, error, label):
    global checks
    checks += 1
    try:
        value = call()
    except Exception as exc:
        if not isinstance(exc, error):
            issues.append((label, type(exc).__name__, error.__name__))
    else:
        issues.append((label, repr(value), error.__name__))


for lesson in LESSONS:
    ident = lesson['id']
    previous = Path.cwd()
    with tempfile.TemporaryDirectory() as folder:
        os.chdir(folder)
        for name, content in lesson.get('fixtures', {}).items():
            Path(name).write_text(content, encoding='utf-8')
        if ident in {'p1', 'p2', 'p3'}:
            check(execute(lesson['solution'])[1].strip(), {'p1':'80','p2':'3\n90','p3':'65\n80\n95'}[ident], ident)
        elif ident.startswith('py') and int(ident[2:]) <= 4:
            for _ in range(60):
                if ident == 'py01':
                    a,b=RNG.randint(-100,100),RNG.choice([x for x in range(-10,11) if x])
                    inp=f'{a}  {b}\n';expected=f'{a+b} {a//b} {a%b}'
                elif ident == 'py02':
                    score=RNG.randint(-20,120);inp=str(score)
                    expected='INVALID' if score not in range(101) else ('A' if score>=90 else 'P' if score>=60 else 'F')
                elif ident == 'py03':
                    n=RNG.randint(0,100);inp=str(n);expected=str((n//2)*(n//2+1))
                else:
                    xs=[RNG.randint(-2,9) for _ in range(RNG.randint(0,15))];inp=' '.join(map(str,xs))+'\n'
                    cutoff=next((i for i,x in enumerate(xs) if x<0),len(xs));expected=str(sum(xs[:cutoff]))
                check(execute(lesson['solution'], inp)[1].strip(), expected, ident)
        else:
            ns={};exec(lesson['solution'],ns)
            for _ in range(40):
                xs=[RNG.randint(-5,10) for _ in range(RNG.randint(0,12))]
                if ident == 'p4':
                    ys=xs or [1];check(ns['mean'](ys),sum(ys)/len(ys),ident)
                elif ident == 'p5':
                    rows=[{'loss':x/10} for x in xs];check(ns['count_good'](rows,.3),len([r for r in rows if r['loss']<.3]),ident)
                elif ident == 'p6':
                    ys=[RNG.randrange(3) for _ in xs];check(ns['accuracy'](xs,ys),len([i for i in range(len(xs)) if xs[i]==ys[i]])/len(xs) if xs else 0.,ident)
                elif ident == 'py05':
                    n=RNG.randrange(20);before=xs[:];r=ns['take_first'](xs,n);check(r,before[:n],ident);check(r is xs,False,ident+' identity');r.append(88);check(xs,before,ident+' mutation')
                elif ident == 'py06':
                    check(ns['tokenize']('  A\tB\n中文,  ! '),['a','b','中文,','!'],ident)
                elif ident == 'py07':
                    k=RNG.randint(1,15);check(ns['moving_average'](xs,k),[sum(xs[i:i+k])/k for i in range(max(0,len(xs)-k+1))],ident)
                elif ident == 'py08':
                    expected=[]
                    for x in xs:
                        if x not in expected:expected.append(x)
                    check(ns['unique_stable'](xs),expected,ident)
                elif ident == 'py09':
                    seqs=[xs[:RNG.randrange(len(xs)+1)] for _ in range(RNG.randrange(5))];width=max(map(len,seqs),default=0)
                    r=ns['pad_batch'](seqs);check(r,([s+[0]*(width-len(s)) for s in seqs],[[i<len(s) for i in range(width)] for s in seqs]),ident)
                elif ident == 'py10':
                    a,b=RNG.randint(-2,2),RNG.randint(-2,2);check(ns['scale'](xs,bias=b,factor=a),[x*a+b for x in xs],ident)
                elif ident == 'py11':
                    k=RNG.randint(1,9);g=ns['batches'](xs,k);check(iter(g) is g,True,ident+' iterator');check(list(g),[xs[i:i+k] for i in range(0,len(xs),k)],ident)
                elif ident == 'py12':
                    a=ns['remember'](1);b=ns['remember'](2);check(a,[1],ident);check(b,[2],ident);check(ns['remember'](9,xs) is xs,True,ident+' identity')
                elif ident == 'py13':
                    ys=[RNG.random() for _ in range(5)];check(ns['mean_probability'](ys),sum(ys)/len(ys),ident)
                elif ident == 'py14':
                    check(ns['label_counts'](xs),{x:xs.count(x) for x in set(xs)},ident)
                elif ident == 'py15':
                    rows=[{'model':str(x%3),'loss':x} for x in xs];groups={k:[r['loss'] for r in rows if r['model']==k] for k in {r['model'] for r in rows}}
                    check(ns['group_mean'](rows),{k:sum(v)/len(v) for k,v in groups.items()},ident)
                elif ident == 'py16':
                    rows=[{'name':str(i),'score':x} for i,x in enumerate(xs)];k=RNG.randint(0,20);check(ns['top_runs'](rows,k),[r['name'] for r in sorted(rows,key=lambda r:(-r['score'],r['name']))[:k]],ident)
                elif ident == 'py17':
                    a={'x':{'lr':1,'v':xs[:]}};b={'x':{'lr':2},'y':[3]};r=ns['merge_config'](a,b);check(r,{'x':{'lr':2,'v':xs},'y':[3]},ident);r['x']['v'].append(88);check(a['x']['v'],xs,ident+' deep copy')
                elif ident == 'py18':
                    rows=[{'epoch':i,'loss':x,'status':'ok' if i%2 else 'failed'} for i,x in enumerate(xs)];v=[r for r in rows if r['status']=='ok'];expected=min(v,key=lambda r:(r['loss'],r['epoch']))['epoch'] if v else None;check(ns['best_checkpoint'](rows),expected,ident)
                elif ident == 'py19':
                    val=RNG.uniform(-1,2);check(ns['parse_probability'](str(val)),val if 0<=val<=1 else None,ident)
                elif ident == 'py20':
                    Path('case.json').write_text(json.dumps({'name':'自测','lr':0}),encoding='utf-8');check(ns['read_config']('case.json'),{'name':'自测','lr':0},ident)
                elif ident == 'py21':
                    import csv
                    with open('case.csv','w',encoding='utf-8',newline='') as f:
                        w=csv.writer(f);w.writerow(['name','loss']);w.writerows([['x,y',x] for x in xs])
                    check(ns['csv_mean_loss']('case.csv'),sum(xs)/len(xs) if xs else None,ident)
                elif ident == 'py22':
                    Path('case.jsonl').write_text('{"a":1}\nbroken\n[1]\n\n0\n',encoding='utf-8');check(ns['read_jsonl']('case.jsonl'),([{'a':1}],3),ident)
                elif ident == 'py23':
                    check(ns['validate_batch']([[1,2]]*len(xs),[0]*len(xs)),True,ident)
                elif ident == 'py24':
                    Path('case.jsonl').write_text('\n'.join(json.dumps({'status':'ok','model':'m','loss':x}) for x in xs),encoding='utf-8');expected={'m':{'count':len(xs),'mean_loss':sum(xs)/len(xs),'best_loss':min(xs)}} if xs else {};check(ns['build_report']('case.jsonl','result.json'),expected,ident);check(json.loads(Path('result.json').read_text(encoding='utf-8')),expected,ident+' file')
                elif ident == 'py25':
                    meter=ns['AverageMeter']();weights=[RNG.randint(0,4) for _ in xs]
                    for x,w in zip(xs,weights):meter.update(x,w)
                    check(meter.compute(),sum(x*w for x,w in zip(xs,weights))/sum(weights) if sum(weights) else 0.,ident)
                elif ident == 'py26':
                    meter=ns['AccuracyMeter']();ys=[RNG.randrange(3) for _ in xs]
                    for a,b in zip(xs,ys):meter.update([a],[b])
                    check(meter.compute(),sum(a==b for a,b in zip(xs,ys))/len(xs) if xs else 0.,ident)
                elif ident == 'py27':
                    features=[[x] for x in xs];labels=[0]*len(xs);ds=ns['ListDataset'](features,labels);check(len(ds),len(xs),ident)
                    if xs:
                        value=ds[-1];check(value,([xs[-1]],0),ident);value[0].append(99);check(ds[-1],([xs[-1]],0),ident+' independent')
                elif ident == 'py28':
                    e=ns['EarlyStop'](2,.1);best=None;bad=0
                    for x in xs:
                        if best is None or x<best-.1:best=x;bad=0
                        else:bad+=1
                        check(e.step(x),bad>=2,ident)
                elif ident == 'py29':
                    check(ns['Compose']([lambda x:x+1,lambda x:x*2])(3),8,ident)
                elif ident == 'py30':
                    rows=[{'sample_id':i,'group_id':x%3,'nested':[x]} for i,x in enumerate(xs)];r=ns['split_by_group'](rows,{1});check(r,([x for x in rows if x['group_id']!=1],[x for x in rows if x['group_id']==1]),ident)
        os.chdir(previous)

ns={};exec(BY_ID['py13']['solution'],ns);raises(lambda:ns['mean_probability']([float('nan')]),ValueError,'py13 NaN in probability range')
ns={};exec(BY_ID['py23']['solution'],ns);raises(lambda:ns['validate_batch']([1],[0]),AssertionError,'py23 1-D feature structure')
print(json.dumps({'reviewed_python_lessons':len(LESSONS),'independent_checks':checks,'issues':issues},ensure_ascii=False,indent=2))

if issues:
    raise SystemExit(1)
