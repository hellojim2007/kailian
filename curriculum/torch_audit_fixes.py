"""Corrections and behavioral checks found by the independent Torch audit.

Executed by finish.py after all lessons exist, before its import/quiz pass.
"""

_torch_lessons = {item['id']: item for item in LESSONS}


def _torch_add_test(lesson_id, *checks):
    _torch_lessons[lesson_id]['tests'].extend(checks)


# A false mask means that the value is excluded, even if padding contains NaN
# or infinity. Multiplication by zero would still propagate these values.
for _id, _function, _body in [
    ('pt03', 'masked_row_mean',
     'return x.masked_fill(~mask,0).sum(1)/mask.sum(1).clamp_min(1)'),
    ('pt28', 'masked_pool',
     'return x.masked_fill(~mask.unsqueeze(-1),0).sum(1)/mask.sum(1,keepdim=True).clamp_min(1)'),
]:
    _item = _torch_lessons[_id]
    _item['solution'] = clean(f'def {_function}(x,mask):\n    {_body}')
    _item['task'] += ' mask=False 的元素完全忽略，包括其中的 NaN/Inf；有效位置保证是有限浮点数。'
    _item['teaching'][1]['body'] += ' 用 masked_fill 将无效位置替换为0；不能仅乘mask，因为 NaN*0 和 Inf*0 仍是 NaN。'
    _item['hints'][0] += ' 使用 x.masked_fill(~mask,0)；句向量输入需要先给mask增加特征维。'

_torch_lessons['pt28']['hints'][0] = 'mask.unsqueeze(-1) 变为 [B,T,1]，用 x.masked_fill(~mask.unsqueeze(-1),0) 后沿序列维求和。'
_torch_lessons['pt03']['example'] = _torch_lessons['pt03']['example'].replace('(x*mask).sum(1)', 'x.masked_fill(~mask,0).sum(1)')
_torch_lessons['pt28']['example'] = _torch_lessons['pt28']['example'].replace('(x*mask.unsqueeze(-1))', 'x.masked_fill(~mask.unsqueeze(-1),0)')
_torch_add_test('pt03',
    case('masked_row_mean(torch.tensor([[2.,float("nan")],[float("inf"),3.],[float("nan"),float("-inf")]]),torch.tensor([[True,False],[False,True],[False,False]]))',
         [2,3,0],label='无效位置的非有限值不传播'),
    case('x.grad',[[1,0]],setup='x=torch.tensor([[2.,float("nan")]],requires_grad=True)\nmasked_row_mean(x,torch.tensor([[True,False]])).sum().backward()',label='被屏蔽位置梯度为零'))
_torch_add_test('pt28',
    case('masked_pool(torch.tensor([[[2.,3.],[float("nan"),float("inf")]],[[float("nan"),float("-inf")],[4.,6.]]]),torch.tensor([[True,False],[False,True]]))',
         [[2,3],[4,6]],label='池化排除无效NaN与Inf'),
    case('masked_pool(torch.tensor([[[float("nan"),float("inf")]]]),torch.tensor([[False]]))',[[0,0]],label='非有限padding的全空句'))

# These manual max-based formulas teach stable finite, nonempty reductions.
# Their input domains should say this explicitly rather than imply support for
# zero-width reductions or infinite logits.
for _id in ('pt06','pt07'):
    _item = _torch_lessons[_id]
    _item['task'] += ' 输入至少一维，最后一维长度大于0；其他维可以为0，所有输入元素有限。'
    _item['teaching'][2]['body'] += ' 最后一维非空且元素有限，这是本题手写公式的输入约定。'

# Observe the autograd engine rather than patching a public function: a valid
# solution may import backward under an alias before the test starts.
_backward_probe = '''
def _audit_used_backward(function, args):
    with torch.autograd.profiler.profile(use_cpu=True) as trace:
        function(*args)
    return any("autograd::engine::evaluate_function" in event.name
               for event in trace.function_events)
'''
_torch_add_test('pt12',case('_audit_used_backward(square_grad,([1.,2.],))',True,setup=_backward_probe,label='真实执行反向传播'))
_torch_add_test('pt13',
    case('check_gradient(2,eps=0.1)',[16,16.01],tolerance=1e-8,label='中心差分遵守传入eps'),
    case('_audit_used_backward(check_gradient,(1.234,))',True,setup=_backward_probe,label='自动微分不以解析公式代替'))

_torch_add_test('pt14',
    case('p.grad',[0.2],setup='p=torch.nn.Parameter(torch.tensor([1.]));p.grad=torch.tensor([0.2])\nclip_gradients([p],1)',label='小梯度不能被放大'),
    case('p.grad',[0,0],setup='p=torch.nn.Parameter(torch.tensor([1.,2.]));p.grad=torch.tensor([3.,4.])\nclip_gradients([p],0)',label='最大范数为零'),
    case('norm==0 and torch.equal(p.grad,torch.zeros(2))',True,setup='p=torch.nn.Parameter(torch.ones(2));p.grad=torch.zeros(2)\nnorm=clip_gradients([p],1)',label='已有零梯度保持为零'))

_torch_add_test('pt18',case('x',[1,2],setup='x=torch.tensor([1.,2.])\nbatch,labels=collate_samples([(x,1)])\nbatch[0,0]=99',label='单样本组批不共享输入存储'))

_torch_add_test('pt20',case('m.training',True,setup='''
class _AuditFailingModel(torch.nn.Module):
    def forward(self,x):
        raise RuntimeError("intentional forward failure")
m=_AuditFailingModel()
m.train()
try:
    predict(m,torch.ones(1,2))
except RuntimeError:
    pass
''',label='前向异常后仍恢复原模式'))

_grad_probe = '''
class _AuditGradientMode(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.flags=[]
    def forward(self,x):
        self.flags.append(torch.is_grad_enabled())
        return x
'''
_torch_add_test('pt21',case('bool(m.flags) and not any(m.flags)',True,setup=_grad_probe+'''
m=_AuditGradientMode()
epoch_mse(m,[(torch.ones(2,requires_grad=True),torch.ones(2))])
''',label='MSE前向时关闭梯度记录'))
_torch_add_test('pt23',case('bool(m.flags) and not any(m.flags)',True,setup=_grad_probe+'''
m=_AuditGradientMode()
evaluate_classifier(m,[(torch.zeros(2,2,requires_grad=True),torch.tensor([0,1]))])
''',label='分类评估前向时关闭梯度记录'))

_torch_add_test('pt25',case('isinstance(loss,float)',True,setup='m=torch.nn.Linear(1,2)\no=torch.optim.SGD(m.parameters(),lr=0.1)\nloss=train_step(m,o,torch.ones(1,1),torch.tensor([0]))',label='返回Python浮点损失'))
_torch_lessons['pt25']['example'] = clean('''
m=torch.nn.Linear(1,2,bias=False)
torch.nn.init.zeros_(m.weight)
optimizer=torch.optim.SGD(m.parameters(),lr=0.1)
x=torch.ones(1,1)
labels=torch.tensor([0])
optimizer.zero_grad()
loss=torch.nn.functional.cross_entropy(m(x),labels)
loss.backward()
optimizer.step()
print(round(loss.item(),4))
print(m.weight.detach().tolist())
''')

# A CPU floating tensor can be float32 or float64. Match the model and targets
# to the actual input instead of silently assuming the default float32.
_item = _torch_lessons['pt26']
_item['solution'] = _item['solution'].replace('m=torch.nn.Linear(x.shape[1],1)', 'm=torch.nn.Linear(x.shape[1],1).to(x)').replace('y.float()', 'y.to(dtype=x.dtype)')
_item['task'] += ' x 为二维、y 为一维，样本数和特征数均大于0；支持CPU float32/float64特征，模型与目标转换到x.dtype；steps为非负整数。'
_item['teaching'][1]['body'] += ' Linear(...).to(x) 匹配特征的设备与dtype；目标用 y.to(dtype=x.dtype)，避免 Double/Float 不匹配。'
_item['hints'][0] += ' 用 Linear(...).to(x) 匹配输入dtype。'
_torch_add_test('pt26',
    case('r["weight"]==[0.] and r["bias"]==0.0 and len(r["losses"])==3',True,setup='r=fit_binary(torch.tensor([[-1.],[1.]]),torch.tensor([0,1]),steps=3,lr=0)',label='尊重传入的零学习率'),
    case('r["weight"]==[0.,0.] and r["bias"]==0.0 and r["losses"]==[]',True,setup='r=fit_binary(torch.ones(2,2),torch.tensor([0,1]),steps=0)',label='零训练步保留初始化'),
    case('len(r["losses"])==2 and all(torch.isfinite(torch.tensor(r["losses"])))',True,setup='r=fit_binary(torch.tensor([[-1.],[1.]],dtype=torch.float64),torch.tensor([0,1]),steps=2)',label='双精度输入可训练'))

# Contrast the returned parameters against an independent run that sees only
# the training data. Detaching validation inputs does not make it legitimate
# to concatenate them into training.
_torch_add_test('pt30',case('torch.allclose(r["model"].weight,control.weight,atol=1e-6,rtol=1e-6) and torch.allclose(r["model"].bias,control.bias,atol=1e-6,rtol=1e-6)',True,setup='''
tx=torch.tensor([[-2.],[-0.5],[1.5],[3.]])
ty=torch.tensor([0,0,1,1])
vx=torch.tensor([[-6.],[6.]])
vy=torch.tensor([1,0])
control=torch.nn.Linear(1,2)
torch.nn.init.zeros_(control.weight)
torch.nn.init.zeros_(control.bias)
control_optimizer=torch.optim.SGD(control.parameters(),lr=0.35)
for _ in range(8):
    control_optimizer.zero_grad()
    control_loss=torch.nn.functional.cross_entropy(control(tx),ty)
    control_loss.backward()
    control_optimizer.step()
r=train_classifier(tx,ty,vx,vy,epochs=8,lr=0.35)
''',label='验证标签不能影响训练参数'))

_torch_lessons['t6']['example'] += '\nprint(y.tolist())\n'
