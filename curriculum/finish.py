# Keep the original lesson IDs: browser drafts and completed exercises survive.
exec((ROOT/'curriculum/models.py').read_text(encoding='utf-8'),globals())
exec((ROOT/'curriculum/training.py').read_text(encoding='utf-8'),globals())
exec((ROOT/'curriculum/projects.py').read_text(encoding='utf-8'),globals())
exec((ROOT/'curriculum/python_audit_fixes.py').read_text(encoding='utf-8'),globals())
exec((ROOT/'curriculum/python_teaching_fixes.py').read_text(encoding='utf-8'),globals())
exec((ROOT/'curriculum/torch_audit_fixes.py').read_text(encoding='utf-8'),globals())
exec((ROOT/'curriculum/trace_quizzes.py').read_text(encoding='utf-8'),globals())

EXTRA = {
 'p1':example('赋值会覆盖旧值','x=4\ny=x+1\nx=9\nprint(x,y)','9 5','y保存当时计算出的5，之后修改x不会自动重新计算y。'),
 'p2':example('负索引和切片','xs=[10,20,30]\nprint(xs[-1],xs[:2])','30 [10, 20]','-1从最后开始计数，切片不包含右边界。'),
 'p3':example('循环外只执行一次','for x in [1,2]:\n    print(x)\nprint("end")','1\n2\nend','最后一行没有缩进，不属于循环体。'),
 'p4':example('print不是return','def f(x):\n    print(x)\nresult=f(3)\nprint(result)','3\nNone','函数没有return，调用结果就是None。'),
 'p5':example('缺失键与默认值','row={"loss":0}\nprint(row.get("loss",9),row.get("score",9))','0 9','只有缺少键才使用默认值，合法零值保留。'),
 'p6':example('zip会按较短一侧结束','print(list(zip([1,2,3],[1])))','[(1, 1)]','这也是生产接口应检查预测和标签长度的原因。'),
 't1':example('dim与keepdim','x=torch.ones(2,3)\nprint(list(x.mean(1).shape),list(x.mean(1,keepdim=True).shape))','[2] [2, 1]','两种结果值相似，但对后续广播有不同影响。'),
 't2':example('方形张量也会静默算错','x=torch.tensor([[1.,3.],[2.,6.]])\nprint((x-x.mean(1)).tolist())\nprint((x-x.mean(1,keepdim=True)).tolist())','[[-1.0, -1.0], [0.0, 2.0]]\n[[-1.0, 1.0], [-2.0, 2.0]]','B与D碰巧相同时，错误广播甚至不会报错。'),
 't3':example('backward会累加梯度','x=torch.tensor(2.,requires_grad=True)\n(x*3).backward()\n(x*4).backward()\nprint(x.grad.item())','7.0','想单独求一次梯度，应先清空旧的.grad。'),
 't4':example('只有Parameter会自动注册','class M(torch.nn.Module):\n    def __init__(self):\n        super().__init__()\n        self.w=torch.ones(2)\nprint(list(M().parameters()))','[]','普通张量属性不是自动注册的可训练参数。'),
 't5':example('backward本身不更新值','x=torch.tensor(2.,requires_grad=True)\n(x*x).backward()\nprint(x.item(),x.grad.item())','2.0 4.0','求导后x仍为2，优化器step才会更新它。'),
 't6':example('模型误差怎样定义','x=torch.tensor([1.,2.])\ny=2*x+1\npred=torch.zeros_like(y)\nprint(((pred-y)**2).mean().item())','17.0','初始预测为0时损失较大，训练应让它下降。'),
}
for item in LESSONS:
    if item['id']=='t2':
        item['example']=item['example'].rstrip()+'\nprint(y.tolist())\n'
        item['examples'][0]=example('保留行维，再做中心化',item['example'],'[[-1.0, 1.0], [-2.0, 2.0]]','每行均值分别为2和4。keepdim=True保留[B,1]，减法沿每行的特征维广播。')
    if item['id']=='t4':
        item['example']=item['example'].rstrip()+'\nm=MyModel()\nprint(list(m(torch.ones(1,3)).shape))\n'
        item['examples'][0]=example('实例化后调用模型',item['example'],'[1, 2]','输入一条样本、三个特征；Linear(3,2)将最后一维映射为两个输出，保留样本维。')
    if item['id']=='t1':
        item['examples'][0]['output']='torch.Size([2, 2])\ntensor([2., 4.])'
    if item['id']=='t3':
        item['examples'][0]['output']='6.0'
    if item['id']=='pt13':
        item['examples'][0]['code']='x=2.;e=0.001\nprint(round(((x+e)**2-(x-e)**2)/(2*e),6))\n'
        item['examples'][0]['output']='4.0'
        item['examples'][0]['explanation']='中心差分近似2x；浮点计算可能有微小误差，这里将打印结果舍入到小数点后六位。'
    if item['id']=='pt29':
        item['examples'][0]['output']='tensor([[0., 1., 1.],\n        [0., 0., 1.],\n        [0., 0., 0.]])'
    if item['id']=='t5':
        complete=example('一次完整的参数更新','w=torch.tensor(0.,requires_grad=True)\noptimizer=torch.optim.SGD([w],lr=0.1)\noptimizer.zero_grad()\nloss=(w-3)**2\nloss.backward()\noptimizer.step()\nprint(round(w.item(),2))','0.6','梯度为 -6，SGD 按 w -= 0.1 * grad 更新，所以参数从 0 变成 0.6。zero_grad、backward、step 各负责不同一步。')
        item['example']=complete['code']
        item['examples'][0]=complete
    if item['id']=='t6':
        item['examples'][0]=example('先构造可检查的数据','x=torch.tensor([[1.],[2.],[3.]])\ny=2*x+1\nprint(y.tolist())\nprint(list(x.shape),list(y.shape))','[[3.0], [5.0], [7.0]]\n[3, 1] [3, 1]','三条样本、每条一个特征；标签也保留 [N,1]，防止预测与标签意外广播成 [N,N]。')
    if item['id'] in EXTRA:
        item['examples'].append(EXTRA[item['id']])
    if item['runtime']=='torch':
        item['solution']='import torch\n'+item['solution']
        item['example']='import torch\n'+item['example']
        for ex in item['examples']:
            ex['code']='import torch\n'+ex['code']
    if not item['pitfalls']:
        item['pitfalls']=[item['hints'][-1]]
    item['quiz']=audit_first_quiz(item)
    probe=trace_quiz(item)
    item['quizzes']=[item['quiz'],probe]
    item['goals']=[item['tag'], '独立实现与边界测试', '解释一次失败的原因']
    item['prerequisites']=[] if item['chapter']=='c01' else [CHAPTERS[int(item['chapter'][1:])-2][1]]
    for i,test in enumerate(item['tests']):
        test['sample']=i<2
    item['estimatedMinutes']=item['minutes']

exec((ROOT/'curriculum/torch_teaching_fixes.py').read_text(encoding='utf-8'),globals())
exec((ROOT/'curriculum/prerequisite_fixes.py').read_text(encoding='utf-8'),globals())

# Keep independent examples self-contained without duplicate import noise.
def deduplicate_torch_import(code):
    while code.startswith('import torch\nimport torch\n'):
        code=code[len('import torch\n'):]
    return code
for item in LESSONS:
    item['example']=deduplicate_torch_import(item['example'])
    for worked in item['examples']:
        worked['code']=deduplicate_torch_import(worked['code'])

# Explicit learning contracts for manual implementations. They are teaching
# checks, not a security boundary: aliases can still be used deliberately.
for id,forbidden in {'pt06':['softmax'],'pt07':['logsumexp'],'pt08':['cross_entropy'],'pt14':['clip_grad_norm_'],'pt10':['scaled_dot_product_attention'],'pt29':['scaled_dot_product_attention']}.items():
    next(x for x in LESSONS if x['id']==id)['forbiddenCalls']=forbidden

assert len(LESSONS)==72, len(LESSONS)
assert len({x['id'] for x in LESSONS})==72
assert all(len(x['examples'])>=2 and len(x['quizzes'])==2 for x in LESSONS)
chapters=[]
for id,title,description,resources in CHAPTERS:
    selected=[x for x in LESSONS if x['chapter']==id]
    assert len(selected)==6,(id,len(selected))
    chapters.append({'id':id,'title':title,'description':description,'minutes':sum(x['minutes'] for x in selected),'resources':[{'title':SOURCES[k][0],'url':SOURCES[k][1]} for k in resources],'lessons':[x['id'] for x in selected]})
from pedagogy import apply_pedagogy
study_route=apply_pedagogy(LESSONS)
course={'version':4,'contentRevision':'2026-10-22-guided-course','title':'Python × PyTorch 实验编程','budget':'主线 20–30 小时＋进阶回访','studyRoute':study_route,'notes':'讲解、例题与练习为原创。学习顺序参考CS50P与Helsinki MOOC，API语义核对Python/PyTorch官方文档，数值稳定与训练递进参考D2L；不是对应机构的官方课程或原题镜像。','chapters':chapters,'sources':[{'key':k,'title':v[0],'url':v[1]} for k,v in SOURCES.items()] + [{'key':'d2l','title':'Dive into Deep Learning · 数据、求导与训练递进','url':'https://d2l.ai/'}]}
(ROOT/'dist/lessons.json').write_text(json.dumps(LESSONS,ensure_ascii=False,indent=2),encoding='utf-8')
(ROOT/'dist/course.json').write_text(json.dumps(course,ensure_ascii=False,indent=2),encoding='utf-8')
print(f"Built {len(LESSONS)} coding exercises, {sum(len(x['tests']) for x in LESSONS)} checks, 144 quizzes, 144 worked examples; suggested {sum(x['minutes'] for x in LESSONS)/60:.1f}h")
