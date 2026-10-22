"""A dependency-ordered entry route and a separate advanced return route.

Topic chapter membership and all historical IDs remain stable. The route is a
recommendation, never an access lock. Exams still cover the full topic chapter.
"""
import copy
import json
from pathlib import Path
from guide_api import API
import guide_torch_api
from guide_lessons import GUIDES
import guide_torch_lessons
from guide_contracts import CONTRACTS

PHASES = [
 ('python-core','Python 入门主线','先会语法、函数与数据处理，再组合文件与类。',
  'p1 py01 py02 p3 py03 py04 p2 p4 py05 py06 py10 p6 py08 py12 p5 py14 py15 py16 py19 py13 py20 py21 py22 py23 py25 py26 py27 py29 py24'),
 ('torch-core','PyTorch 入门主线','先走通真实求导和训练，再组织模型、数据与评估。',
  't1 pt01 t2 pt02 pt03 pt04 t3 pt11 pt12 t5 t6 t4 pt16 pt17 pt18 pt20 pt21 pt22 pt23 pt24 pt25 pt26 pt27 pt30'),
 ('python-plus','Python 进阶回访','窗口、二维组批、生成器、递归和状态机。',
  'py07 py09 py11 py17 py18 py28 py30'),
 ('torch-plus','PyTorch 进阶回访','稳定损失、梯度工程、向量化与注意力。',
  'pt06 pt07 pt08 pt13 pt14 pt15 pt19 pt05 pt28 pt09 pt10 pt29'),
]
RETAINED_LABS = {'t1','t2','t3','t5','t6'}

def apply_pedagogy(lessons):
    by_id = {l['id']:l for l in lessons}
    route = [i for _,_,_,ids in PHASES for i in ids.split()]
    assert len(route)==72 and set(route)==set(by_id)==set(GUIDES)
    seen=set()
    first_api={}
    phases=[]
    for ident,title,description,ids in PHASES:
        selected=ids.split()
        phases.append(dict(id=ident,title=title,description=description,lessonIds=selected,
                           track='core' if ident.endswith('core') else 'extension'))
        for lesson_id in selected:
            item=by_id[lesson_id]
            authored=copy.deepcopy(GUIDES[lesson_id])
            assert set(authored['requires'])<=seen,(lesson_id,'untaught prerequisite',set(authored['requires'])-seen)
            assert all(key in API for key in authored['apiKeys'])
            authored['cards']=[]
            for key in authored.pop('apiKeys'):
                first_api.setdefault(key,lesson_id)
                card=copy.deepcopy(API[key])
                card['firstLessonId']=first_api[key]
                card['newHere']=first_api[key]==lesson_id
                authored['cards'].append(card)
            authored['phase']=ident
            authored['track']='core' if ident.endswith('core') else 'extension'
            authored['position']=route.index(lesson_id)+1
            authored['labEnabled']=lesson_id in RETAINED_LABS
            authored['contract']=CONTRACTS.get(lesson_id,[item['task']])
            item['guide']=authored
            # Topic chapters are retained for existing exam/record compatibility.
            # The UI uses these exact lesson prerequisites, not a generic previous chapter.
            item['prerequisites']=[by_id[i]['title'] for i in authored['requires']]
            item['prerequisiteAuditScope']='authored-lesson-route-with-inline-api-not-exhaustive-code-proof'
            item['resources']=[r for r in item['resources'] if r.get('scope')!='course-index']
            for card in authored['cards']:
                if not any(r['url']==card['source'] for r in item['resources']):
                    item['resources'].append(dict(title=card['title']+' · 用法参考',url=card['source'],scope='api-reference'))
            # Old teaching text is retained as authoring history, not the main explanation.
            if lesson_id=='p4':
                item['cpp']='参数不用写类型；函数体缩进，调用返回值由 return 决定。'
            seen.add(lesson_id)
    # The existing manually authored objectives stay intact; update wiring and
    # current reference/path declarations reproducibly after the new guide pass.
    path=Path(__file__).resolve().parent/'lab-alignment.json'
    audit=json.loads(path.read_text(encoding='utf-8'))
    audit['version']=2
    audit['scope']='5 optional Tensor/gradient/training labs; 67 units taught with executable syntax examples, warmups and full tasks.'
    for entry in audit['lessons']:
        l=by_id[entry['lessonId']]
        for key in ('prerequisites','prerequisiteAuditScope','resourceAuditScope'):
            entry['learningPathHints' if key=='prerequisites' else key]=l[key]
        entry['resources']=[dict(url=r['url'],scope=r['scope']) for r in l['resources']]
        if l['id'] not in RETAINED_LABS:
            entry['widgetId']=None
            entry['domId']=None
    path.write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(version=1,phases=phases,lessonIds=route,coreCount=53,extensionCount=19,
        note='推荐顺序按具体先修关系组织；左侧章节仍按知识主题归档。章节编号是稳定的题目索引，不代表必须按编号学习。先完成53节入门主线，再回访19节进阶；所有内容都可自由打开。',
        budget='入门主线约20–30小时；19节进阶另计，按需回访。全量专题考核额外约4–6小时。')
