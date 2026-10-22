import json
from pathlib import Path
import sys

root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'dist'))
from grade import grade,execute
lessons=json.loads((root/'dist/lessons.json').read_text(encoding='utf-8'))
failed=[]
for lesson in lessons:
    main=grade({'lesson':lesson['id'],'code':lesson['example'],'action':'run','stdin':''},lessons)
    if not main['ok']:
        failed.append((lesson['id'],'main example',main.get('error')))
    for index,ex in enumerate(lesson['examples']):
        result=grade({'lesson':lesson['id'],'code':ex['code'],'action':'run','stdin':''},lessons)
        if not result['ok']:
            failed.append((lesson['id'],index,result.get('error')))
        elif result['stdout'].strip()!=ex['output'].strip():
            failed.append((lesson['id'],index,'Displayed output does not match execution',ex['output'],result['stdout']))
    for index,q in enumerate(lesson['quizzes']):
        assert len(set(q['options']))==len(q['options']),lesson['id']
        if 'expectedStdout' in q:
            result=grade({'lesson':lesson['id'],'code':q['code'],'action':'run','stdin':''},lessons)
            if not result['ok'] or result['stdout'].strip()!=q['expectedStdout'] or q['options'][q['answer']]!=q['expectedStdout']:
                failed.append((lesson['id'],f'quiz {index}','Code / output / answer mismatch',result))
            assert q['code'].strip()!='标准输出' and 'contract' not in q
print('72 main examples / 144 displayed outputs / 72 executable prediction answers; failures:',failed)

bad_implementations={
 'py01':'a,b=input().split()\nprint(a+b,0,0)',
 'py05':'def take_first(xs,n):\n    return xs',
 'py09':'def pad_batch(sequences):\n    w=max(map(len,sequences),default=0)\n    rows=[s+[0]*(w-len(s)) for s in sequences]\n    return rows,[[x!=0 for x in s] for s in rows]',
 'py12':'def remember(value,history=[]):\n    history.append(value)\n    return history',
 'py17':'def merge_config(defaults,overrides):\n    result=defaults.copy()\n    result.update(overrides)\n    return result',
 'pt06':'import torch\ndef stable_softmax(x):\n    e=x.exp()\n    return e/e.sum(-1,keepdim=True)',
 'pt15':'import torch\ndef accumulated_mse_grad(batches):\n    w=torch.tensor(0.,requires_grad=True)\n    for x,y in batches:\n        (((w*x-y)**2).mean()/len(batches)).backward()\n    return w.grad.item()',
 'pt20':'import torch\ndef predict(model,x):\n    model.eval()\n    return model(x)',
 'pt29':'import torch\ndef causal_attention(q,k,v):\n    return torch.softmax(q@k.transpose(-1,-2)/(q.shape[-1]**0.5),-1)@v',
}
for id,code in bad_implementations.items():
    result=grade({'lesson':id,'code':code,'action':'submit'},lessons)
    assert not result['ok'],id
print('PASS nine realistic incorrect implementations rejected')
counterexamples=json.loads((root/'curriculum/counterexamples.json').read_text(encoding='utf-8'))
for item in counterexamples:
    result=grade({'lesson':item['lesson'],'code':item['code'],'action':'submit'},lessons)
    assert not result['ok'],(item['lesson'],item['reason'])
print('PASS',len(counterexamples),'previously accepted incorrect implementations now rejected')
for lesson in lessons:
    assert lesson['resources'] and len(lesson['quizzes'])==2
    assert all(len(q['options'])==len(q['why']) and 0<=q['answer']<len(q['options']) for q in lesson['quizzes'])
old=json.loads((root/'curriculum/original.json').read_text(encoding='utf-8'))
assert all(next(x for x in lessons if x['id']==o['id'])['task']==o['task'] for o in old)
print('PASS source links / quiz schema / all 12 original exercise contracts retained')
if failed:
    raise SystemExit(1)
