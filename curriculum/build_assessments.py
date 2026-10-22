"""Build the additional exam bank without altering any of the 72 lessons."""
import json
from pathlib import Path
from assess_python import build as python_bank
from assess_torch import build as torch_bank

ROOT=Path(__file__).resolve().parents[1]
lessons=json.loads((ROOT/'dist/lessons.json').read_text(encoding='utf-8'))
data={'version':1,'additionalMinutes':310,'exams':[],'items':[],'exercises':[],'reviewItems':[],
      'chapterLessons':{ch:[l['id'] for l in lessons if l['chapter']==ch] for ch in sorted({l['chapter'] for l in lessons})},
      'skillTitles':{l['id']:l['title'] for l in lessons},
      'policy':{'reviewDays':[1,3,7], 'suggestedPassPercent':80,
                'note':'原有练习全部保留。考核与讲评额外约4–6小时；复习间隔是可调整的学习安排，等待时间不计学习工时。'}}
for bank in [python_bank(),torch_bank()]:
    for key in ['exams','items','exercises','reviewItems']: data[key].extend(bank[key])
items={x['id']:x for x in data['items']}
assert len(items)==len(data['items'])
assert len(data['exams'])==18
assert sum(x['kind']=='chapter' for x in data['exams'])==12
assert sum(x['kind']=='cumulative' for x in data['exams'])==4
assert sum(x['kind']=='stage' for x in data['exams'])==2
assert all(all(i in items for i in e['itemIds']) for e in data['exams'])
assert all(i in items for i in data['reviewItems'])
assert len({i for e in data['exams'] for i in e['itemIds']})==sum(len(e['itemIds']) for e in data['exams']), 'Exams must use distinct questions'
assert not set(data['reviewItems']) & {i for e in data['exams'] for i in e['itemIds']}, 'Delayed reviews need separate items'
data['exams'].sort(key=lambda e:(max(int(c[1:]) for c in e['chapters']),{'chapter':0,'cumulative':1,'stage':2}[e['kind']]))
(ROOT/'dist/exams.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"Built {len(data['exams'])} exams, {len(items)} new questions, {len(data['exercises'])} coding tasks and {len(data['reviewItems'])} separate review questions")
