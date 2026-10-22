"""Independent standard-level Torch assessments; no changes to legacy drills."""
from assessment_common import Bank, check


def build():
    bank = Bank('torch')

    def out(key, chapter, prompt, code, expected, explanation, skills):
        return bank.output(key, chapter, prompt, code, expected, explanation, skills, runtime='torch')

    def choice(key, chapter, prompt, options, answer, explanation, skills, code=None):
        item = bank.choice(key, chapter, prompt, options, answer, explanation, skills, code=code)
        bank.items[-1]['runtime'] = 'torch'
        return item

    def coding(key, chapter, prompt, signature, solution, tests, explanation, skills):
        return bank.coding(key, chapter, prompt, signature, 'import torch\n' + solution,
                           tests, explanation, skills, runtime='torch')

    backward_probe = '''
def _uses_autograd(function,*args):
    with torch.autograd.profiler.profile(use_cpu=True) as trace:
        function(*args)
    return any('autograd::engine::evaluate_function' in event.name for event in trace.function_events)
'''

    c = 'c07'
    q = [
        out('07-o1',c,'写出完整标准输出，每个print占一行。',
            'import torch\nx=torch.arange(24).reshape(2,3,4)\nprint(list(x.flatten(1).shape))\nprint(x[1,:,0].tolist())',
            '[2, 12]\n[12, 16, 20]','批次轴保留为2；第1条样本的三个块分别从12、16、20开始。',['pt01','t1']),
        out('07-o2',c,'零也可能是合法token。写出两行标准输出。',
            'import torch\ntokens=torch.tensor([[0,5,0],[8,0,0]])\nmask=torch.tensor([[True,True,False],[True,False,False]])\nprint(tokens[mask].tolist())\nprint(mask.sum(1).tolist())',
            '[0, 5, 8]\n[2, 1]','布尔索引选取有效位置；token值0不能代替独立mask。',['pt04','pt02']),
        choice('07-m1',c,'传感器矩阵是[天数,传感器数]。要保留每天所有传感器的一个平均值，正确表达式是？',
               ['x.mean(dim=1)','x.mean(dim=0)','x.flatten().mean()'],0,
               'dim=1归约传感器轴，结果长度为天数。dim=0得到每个传感器的跨天均值；全部展平则只剩一个数。',['t1']),
        choice('07-m2',c,'用值0右补齐token序列后，哪种mask构造能同时保留合法的零token？',
               ['tokens != 0','依据每条原序列长度，将前length个位置设True','整行只要出现非零就全部设True'],1,
               '有效性来自原长度，而非token取值。tokens!=0会误删合法零；整行置True又会把padding纳入计算。',['pt04','pt03']),
        coding('07-c1',c,
               '实现 sensor_summary(x,valid)。x是CPU二维浮点张量[B,D]，D>=1，valid是同形bool。有效元素有限，无效元素可为NaN/Inf。返回字典{mean,peak}，两项均为[B]张量：每行有效均值与最大值，全无效行两项均为0；支持B=0，不改输入，mean保留梯度。',
               'def sensor_summary(x, valid)',
               '''def sensor_summary(x,valid):
    counts=valid.sum(1)
    mean=x.masked_fill(~valid,0).sum(1)/counts.clamp_min(1)
    peak=x.masked_fill(~valid,float('-inf')).max(1).values
    peak=torch.where(counts>0,peak,torch.zeros_like(peak))
    return {'mean':mean,'peak':peak}
''',
               [check('sensor_summary(torch.tensor([[2.,8.,99.],[-5.,-2.,7.]]),torch.tensor([[True,True,False],[True,True,False]]))',{'mean':[5,-3.5],'peak':[8,-2]},label='均值与负数最大值'),
                check('sensor_summary(torch.tensor([[float("nan"),float("inf")]]),torch.tensor([[False,False]]))',{'mean':[0],'peak':[0]},label='全无效非有限位置'),
                check('[list(r[k].shape) for k in ("mean","peak")]',[[0],[0]],setup='r=sensor_summary(torch.empty(0,3),torch.empty(0,3,dtype=torch.bool))',label='空批次形状'),
                check('x.grad',[[0.5,0,0.5]],setup='x=torch.tensor([[1.,99.,3.]],requires_grad=True)\nsensor_summary(x,torch.tensor([[True,False,True]]))["mean"].sum().backward()',label='仅有效位置参与梯度')],
               '先按mask替换无效值再归约；最大值必须用-inf屏蔽，不能用0覆盖合法负数。全无效行单独归零。',['t1','pt03']),
        coding('07-c2',c,
               '图像已提取为任意至少二维张量x[B,...]，每条样本展平后有F>=1个特征。centers是[K,F]浮点张量，K>=1，两者CPU、同dtype且有限。实现 assign_prototypes(x,centers)，返回[B] long张量，每条样本分配到平方欧氏距离最近的中心；距离相同取较小中心索引。支持非连续x与空B，不修改输入。',
               'def assign_prototypes(x, centers)',
               '''def assign_prototypes(x,centers):
    flat=x.flatten(1)
    distances=((flat[:,None,:]-centers[None,:,:])**2).sum(-1)
    return distances.argmin(1)
''',
               [check('assign_prototypes(torch.tensor([[[0.,0.]],[[4.,3.]],[[1.,0.]]]),torch.tensor([[0.,0.],[4.,4.]]))',[0,1,0],label='批量原型分配'),
                check('assign_prototypes(torch.tensor([[[1.,1.]]]),torch.tensor([[0.,0.],[2.,2.]]))',[0],label='平局取首索引'),
                check('list(assign_prototypes(torch.empty(0,2,3),torch.ones(2,6)).shape)',[0],label='空批次'),
                check('assign_prototypes(x,c)',[1],setup='x=torch.arange(6.).reshape(1,2,3).transpose(1,2)\nc=torch.tensor([[0.,0.,0.,0.,0.,0.],[0.,3.,1.,4.,2.,5.]])',label='非连续特征顺序'),
                check('result.dtype==torch.long and torch.equal(x,old)',True,setup='x=torch.tensor([[[1.,2.]],[[3.,4.]]]);old=x.clone()\nresult=assign_prototypes(x,torch.zeros(1,2))',label='整数索引且不修改输入')],
               '展平只合并特征维；广播构造成对距离后沿中心轴argmin。argmin天然保留第一个最小值。',['pt01','pt05','pt02'])]
    bank.exam('chapter-c07','chapter','张量形状与索引 · 章末验收',[c],10,q,'闭卷检查批次轴、有效位置和向量化索引，提交后统一讲评。')

    c='c08'
    q=[
        out('08-o1',c,'写出两行标准输出。',
            'import torch\nx=torch.tensor([[2.,4.],[10.,14.]])\nprint((x-x.mean(1)).tolist())\nprint((x-x.mean(1,keepdim=True)).tolist())',
            '[[-1.0, -8.0], [7.0, 2.0]]\n[[-1.0, 1.0], [-2.0, 2.0]]','不保留归约维时，[2]按列广播；[2,1]才对应每行自己的均值。',['t2']),
        out('08-o2',c,'编号特征拆成两头后，写出标准输出。',
            'import torch\nx=torch.arange(8).reshape(1,2,4)\nh=x.reshape(1,2,2,2).permute(0,2,1,3)\nprint(h.sum(-1).tolist())',
            '[[[1, 9], [5, 13]]]','第0头取每个token前两个特征；第1头取后两个，再各自求和。',['pt09']),
        choice('08-m1',c,'输入是[-1200,-1201]的float32张量。直接log(exp(x).sum())得到-inf，根本原因与修复是？',
               ['指数下溢；先减最大值计算再加回最大值','log只支持正整数；先转long','元素顺序错误；先排序'],0,
               '极小指数在float32中下溢为0，log(0)为-inf。logsumexp的平移公式将指数限制在可表示范围；排序和转整数都不能解决。',['pt06','pt07']),
        choice('08-m2',c,'分数scores形状[B,Tq,Tk]，value形状[B,Tk,Dv]。哪种归一化与输出组合正确？',
               ['沿Tq做softmax，输出[B,Tk,Dv]','沿Tk做softmax后乘value，输出[B,Tq,Dv]','沿B做softmax，输出[B,Tq,Tk]'],1,
               '每个query在全部key间分配权重，因此沿最后的Tk轴归一化；乘value时Tk被归约，Dv保留。',['pt10']),
        coding('08-c1',c,
               '实现 smoothed_nll(logits,labels,epsilon)。logits是CPU有限浮点[B,C]、C>=1，labels为合法类别long[B]，0<=epsilon<=1。每条样本损失=(1-epsilon)*目标类负log概率+epsilon*所有C类负log概率的均值，再对B取均值。返回标量张量，不先softmax后log；B=0时返回连接logits计算图的0。',
               'def smoothed_nll(logits, labels, epsilon)',
               '''def smoothed_nll(logits,labels,epsilon):
    if logits.shape[0]==0:
        return logits.sum()*0
    negative_log_probs=torch.logsumexp(logits,-1,keepdim=True)-logits
    target=negative_log_probs[torch.arange(len(labels),device=logits.device),labels]
    return ((1-epsilon)*target+epsilon*negative_log_probs.mean(-1)).mean()
''',
               [check('smoothed_nll(torch.tensor([[0.,1.0986122886681098]],dtype=torch.float64),torch.tensor([1]),0.4).item()',0.5074045301854029,label='非均匀概率的中间平滑系数'),
                check('smoothed_nll(torch.tensor([[1000.,1001.]],dtype=torch.float64),torch.tensor([1]),1.).item()',0.813261687518,label='平滑到均匀目标且稳定'),
                check('torch.allclose(smoothed_nll(x,y,0),torch.nn.functional.cross_entropy(x,y))',True,setup='x=torch.tensor([[1.,-2.,4.],[2.,0.,-1.]])\ny=torch.tensor([2,0])',label='零平滑退化成交叉熵'),
                check('x.grad',[],setup='x=torch.empty(0,3,requires_grad=True)\nsmoothed_nll(x,torch.empty(0,dtype=torch.long),0.2).backward()',label='空批次仍能反向'),
                check('x.grad.sum(1)',[0,0],setup='x=torch.tensor([[1.,2.,0.],[0.,3.,1.]],requires_grad=True)\nsmoothed_nll(x,torch.tensor([0,1]),0.2).backward()',label='梯度保持平移不变性')],
               '用logsumexp减去各类logit得到稳定的负log概率，再混合目标类与均匀目标。空批次的零必须连接输入图。',['pt06','pt07','pt08']),
        coding('08-c2',c,
               '实现 merge_heads(h)，将CPU张量[B,H,T,Dh]恢复为[B,T,H*Dh]，每个token按head编号拼接特征。H>=1、Dh>=1，B或T可以为0；支持非连续输入且保留梯度。',
               'def merge_heads(h)',
               '''def merge_heads(h):
    b,heads,t,width=h.shape
    return h.permute(0,2,1,3).reshape(b,t,heads*width)
''',
               [check('merge_heads(torch.tensor([[[[0,1],[4,5]],[[2,3],[6,7]]]]))',[[[0,1,2,3],[4,5,6,7]]],label='token特征归位'),
                check('list(merge_heads(torch.empty(0,2,3,4)).shape)',[0,3,8],label='空批次'),
                check('list(merge_heads(torch.empty(2,3,0,4)).shape)',[2,0,12],label='空序列'),
                check('x.grad',[[[[1,1],[1,1]],[[1,1],[1,1]]]],setup='x=torch.ones(1,2,2,2,requires_grad=True)\nmerge_heads(x).sum().backward()',label='梯度不中断')],
               '先交换head与token轴，再合并head和头内特征。直接reshape会把不同token的特征混在一起。',['pt09','t2'])]
    bank.exam('chapter-c08','chapter','广播与数值稳定 · 章末验收',[c],10,q,'检查维度语义、稳定损失和注意力的数据流。')

    c='c09'
    q=[
        out('09-o1',c,'写出两行标准输出。',
            'import torch\nx=torch.tensor(3.,requires_grad=True)\nx.square().backward()\n(x.detach()*x).backward()\nprint(x.grad.item())\nx.grad=None\n(2*x).backward()\nprint(x.grad.item())',
            '9.0\n2.0','第一图贡献6，detach分支将其中一个x当常数3，第二图再贡献3；清空后只剩最后的2。',['t3','pt11','pt12']),
        out('09-o2',c,'写出输出；有限差分使用代码中的步长，不把近似当精确导数。',
            'import torch\nx=torch.tensor(1.,dtype=torch.float64,requires_grad=True)\n(x**4).backward()\ne=0.5\nnumerical=((x.detach()+e)**4-(x.detach()-e)**4)/(2*e)\nprint(round(x.grad.item(),3),round(numerical.item(),3))',
            '4.0 5.0','四次函数在1处解析导数为4；eps=0.5的中心差分为5，说明有限步长仍有截断误差。',['pt13']),
        choice('09-m1',c,'两个micro-batch分别含2条和5条样本，每批loss都是mean。要模拟所有7条样本的mean梯度，应怎样反向？',
               ['分别乘2/7和5/7，逐批backward且中途不清梯度','每批loss除以2，逐批清梯度','直接把两个mean相加'],0,
               '整体mean给每条样本相同权重。批次mean需按本批样本数/总数加权，且累积期间保留已算梯度。',['pt15','pt11']),
        choice('09-m2',c,'两组梯度全局L2范数为10，max_norm为5。正确的全局范数裁剪应怎样处理？',
               ['各组分别裁成范数5','所有梯度统一乘约0.5，参数数值本身不动','每个梯度元素截到[-5,5]'],1,
               '全局裁剪将所有参数梯度视为一个向量，用相同系数缩放，保留其方向；逐组归一化与逐元素截断均会改变方向。',['pt14']),
        coding('09-c1',c,
               '实现 weighted_square_gradient(values,weights)。两者是同长有限Python数值列表，可为空。用真实autograd求 sum(weights[i]*x[i]**2) 对x的梯度，返回一维float64张量；不要直接代入解析导数。',
               'def weighted_square_gradient(values, weights)',
               '''def weighted_square_gradient(values,weights):
    x=torch.tensor(values,dtype=torch.float64,requires_grad=True)
    w=torch.tensor(weights,dtype=torch.float64)
    (w*x.square()).sum().backward()
    return x.grad
''',
               [check('weighted_square_gradient([2,-3,0],[0.5,2,9])',[2,-12,0],label='正负值与零'),
                check('weighted_square_gradient([],[])',[],label='空向量'),
                check('str(weighted_square_gradient([1],[2]).dtype)','torch.float64',label='梯度dtype'),
                check('_uses_autograd(weighted_square_gradient,[1.,2.],[3.,4.])',True,setup=backward_probe,label='实际自动微分')],
               '权重参与损失而不作为待求导变量；x必须是需要梯度的叶子。空向量求和仍能连接计算图。',['t3','pt12']),
        coding('09-c2',c,
               '实现 accumulated_l1_grad(batches)。batches是非空list，每项(x,y)为同长一维CPU float32张量，至少总计1条样本，元素有限；单批允许为空。创建w=0的标量叶子，对所有样本的mean绝对误差 abs(w*x-y) 逐批backward累积，返回w梯度的Python float；误差为0时采用PyTorch的abs梯度0。',
               'def accumulated_l1_grad(batches)',
               '''def accumulated_l1_grad(batches):
    w=torch.tensor(0.,requires_grad=True)
    n=sum(x.numel() for x,y in batches)
    for x,y in batches:
        ((w*x-y).abs().sum()/n).backward()
    return w.grad.item()
''',
               [check('accumulated_l1_grad([(torch.tensor([1.,2.,3.]),torch.tensor([1.,1.,1.])),(torch.tensor([4.]),torch.tensor([-1.]))])',-0.5,label='不等批次的L1梯度'),
                check('accumulated_l1_grad([(torch.tensor([-2.,3.]),torch.tensor([1.,0.]))])',1,label='零误差采用零次梯度'),
                check('accumulated_l1_grad([(torch.empty(0),torch.empty(0)),(torch.tensor([2.]),torch.tensor([1.]))])',-2,label='允许一个空micro-batch'),
                check('_uses_autograd(accumulated_l1_grad,[(torch.tensor([1.]),torch.tensor([2.]))])',True,setup=backward_probe,label='真实逐批反向'),
                check('isinstance(accumulated_l1_grad([(torch.ones(1),torch.zeros(1))]),float)',True,label='返回Python浮点数')],
               '各批sum除以同一个总样本数，保证尾批不被过度加权。abs的梯度取决于误差符号，零点按PyTorch约定为0。',['pt11','pt13','pt15'])]
    bank.exam('chapter-c09','chapter','梯度与训练排错 · 章末验收',[c],10,q,'区分函数值、梯度、计算图和累积权重。')

    c='c10'
    q=[
        out('10-o1',c,'仅输出参数数量和形状，不需要知道随机初始化值。',
            'import torch\nclass Bridge(torch.nn.Module):\n    def __init__(self):\n        super().__init__()\n        self.linear=torch.nn.Linear(2,3,bias=False)\n        self.shift=torch.ones(3)\n    def forward(self,x):\n        return self.linear(x)+self.shift\nm=Bridge()\nprint(sum(p.numel() for p in m.parameters()))\nprint(list(m(torch.ones(4,2)).shape))',
            '6\n[4, 3]','普通Tensor属性shift不会自动成为Parameter；Linear无bias，只有2×3个权重，batch维保留。',['t4','pt16']),
        out('10-o2',c,'写出标准输出。',
            'import torch\nsamples=[(torch.tensor([2.,4.]),1)]\nx=torch.stack([p[0] for p in samples])\ny=torch.tensor([p[1] for p in samples],dtype=torch.long)\nprint(list(x.shape),list(y.shape))\nprint(y.dtype==torch.long)',
            '[1, 2] [1]\nTrue','stack增加batch轴；只有一条样本也不能把特征或标签的batch轴squeeze掉。',['pt17','pt18']),
        choice('10-m1',c,'模型含Dropout。验证时已调用model.eval()，还希望不构建计算图，应该再做什么？',
               ['with torch.no_grad(): 包住验证前向','optimizer.zero_grad()就能关闭计算图','把batch大小设1即可'],0,
               'eval控制Dropout等层的行为，no_grad控制运算记录。清梯度和batch大小都不等于关闭梯度记录。',['pt20']),
        choice('10-m2',c,'只训练新分类头：backbone已requires_grad_(False)，但head之前也被冻结。哪一步不可省？',
               ['把整个model.eval()当冻结开关','重新启用head的requires_grad，并把head参数交给优化器','只把head参数复制成普通Tensor'],1,
               '冻结和启用都要显式管理；优化器需要真正注册的参数，普通Tensor副本不再对应模型原参数。',['pt19','t4']),
        coding('10-c1',c,
               '实现 make_regressor(widths)。widths为至少含2个正整数的list，依次表示输入、各隐藏层和输出宽度；返回nn.Module，由相邻Linear组成，除最后一层外每层后接ReLU，所有Linear含bias。widths长度不足2或存在非正维度时抛ValueError。无需验证非整数输入。',
               'def make_regressor(widths)',
               '''def make_regressor(widths):
    if len(widths)<2 or any(w<=0 for w in widths):
        raise ValueError('invalid widths')
    layers=[]
    for i in range(len(widths)-1):
        layers.append(torch.nn.Linear(widths[i],widths[i+1]))
        if i<len(widths)-2:
            layers.append(torch.nn.ReLU())
    return torch.nn.Sequential(*layers)
''',
               [check('m(torch.tensor([[-1.,-1.],[1.,1.]]))',[[0],[6]],setup='m=make_regressor([2,3,1])\nlinears=[v for v in m.modules() if isinstance(v,torch.nn.Linear)]\nwith torch.no_grad():\n    for layer in linears:\n        layer.weight.fill_(1);layer.bias.zero_()',label='隐藏层确实应用非线性'),
                check('sum(p.numel() for p in make_regressor([3,4,2,1]).parameters())',29,label='全部参数已注册'),
                check('sum(isinstance(m,torch.nn.ReLU) for m in make_regressor([2,1]).modules())',0,label='仅输出层不加ReLU'),
                check('make_regressor([3,0,1])',raises='ValueError',label='拒绝非正宽度'),
                check('make_regressor([3])',raises='ValueError',label='拒绝缺少输出宽度')],
               '按相邻维度组装网络，每个隐藏Linear后加ReLU。输出层保持原始数值；使用ModuleList或Sequential等注册层。',['t4','pt16']),
        coding('10-c2',c,
               '实现 WindowDataset(series,window)，继承torch.utils.data.Dataset。series是一维CPU浮点张量，window是正整数；window<=0抛ValueError。样本i为(series[i:i+window],series[i+window])，故长度max(N-window,0)。只接受0<=i<len(ds)的整数索引，越界抛IndexError。构造与返回都隔离存储，不让外部修改污染数据集。',
               'class WindowDataset(torch.utils.data.Dataset)',
               '''class WindowDataset(torch.utils.data.Dataset):
    def __init__(self,series,window):
        if window<=0:
            raise ValueError('positive window required')
        self.series=series.clone()
        self.window=window
    def __len__(self):
        return max(len(self.series)-self.window,0)
    def __getitem__(self,i):
        if i<0 or i>=len(self):
            raise IndexError('sample index out of range')
        return self.series[i:i+self.window].clone(),self.series[i+self.window].clone()
''',
               [check('WindowDataset(torch.tensor([1.,3.,5.,7.]),2)[1]',[[3,5],7],label='窗口与下一时刻目标'),
                check('len(WindowDataset(torch.ones(2),4))',0,label='序列短于窗口'),
                check('ds[0]',[[1,2],3],setup='s=torch.tensor([1.,2.,3.])\nds=WindowDataset(s,2)\ns[0]=99\na,b=ds[0]\na[0]=88\nb.fill_(77)',label='构造与返回均无别名'),
                check('WindowDataset(torch.ones(3),1)[-1]',raises='IndexError',label='接口明确不支持负索引'),
                check('WindowDataset(torch.ones(3),0)',raises='ValueError',label='非法窗口')],
               '先按预测任务定义样本数量和目标偏移，再实现Dataset协议。clone同时保护原输入与取出的样本。',['pt17','pt18'])]
    bank.exam('chapter-c10','chapter','模型与数据加载 · 章末验收',[c],10,q,'在新数据接口中检验参数注册、组批与模式管理。')

    c='c11'
    q=[
        out('11-o1',c,'两批平方误差总和分别为12和16，元素数为3和1。写出输出。',
            'sums=[12,16]\ncounts=[3,1]\nprint(sum(sums)/sum(counts))\nprint(sum(s/n for s,n in zip(sums,counts))/len(sums))',
            '7.0\n10.0','全体元素MSE是28/4=7。等权平均批次mean使尾批16获得与大批同样权重，得到错误的10。',['pt21','pt23']),
        out('11-o2',c,'写出两行标准输出。',
            'import torch,copy\nm=torch.nn.Linear(1,1,bias=False)\nwith torch.no_grad():\n    m.weight.zero_()\nshallow=m.state_dict()\ndeep=copy.deepcopy(m.state_dict())\nwith torch.no_grad():\n    m.weight.add_(3)\nprint(shallow["weight"].tolist())\nprint(deep["weight"].tolist())',
            '[[3.0]]\n[[0.0]]','state_dict中的张量可能共享参数存储；deepcopy才得到不随后续更新改变的内存快照。',['pt24']),
        choice('11-m1',c,'真实标签[1,1,0]，模型全预测0。按本课程零分母返回0的约定，precision、recall、F1分别是？',
               ['0、0、0','1、0、1','NaN、1、NaN'],0,
               '没有预测正例，precision按约定为0；两个真实正例都漏掉，recall为0，TP为0所以F1也为0。',['pt22']),
        choice('11-m2',c,'训练循环先loss=criterion(...).item()，再loss.backward()。最直接的修复是？',
               ['把Python float转成long','保留原张量loss做backward，另用loss.item()记录数值','给optimizer.step()多调用一次'],1,
               'item后的Python数值不带计算图。训练用张量loss与日志用数值可以分别保存；多step不能恢复丢失的图。',['t5','pt25']),
        coding('11-c1',c,
               '实现 evaluate_binary(model,batches)。每批(x,y)的模型输出和y均为一维[B]，y是0/1浮点张量。临时eval并关闭梯度，按全部样本聚合BCEWithLogitsLoss与logit>=0的准确率，返回{loss:Python float,accuracy:Python float}。空数据两项0；成功或异常都恢复原train/eval模式，不更新参数。',
               'def evaluate_binary(model, batches)',
               '''def evaluate_binary(model,batches):
    mode=model.training
    model.eval()
    total=0.0
    correct=0
    count=0
    try:
        with torch.no_grad():
            for x,y in batches:
                logits=model(x)
                total+=torch.nn.functional.binary_cross_entropy_with_logits(logits,y,reduction='sum').item()
                correct+=((logits>=0)==(y==1)).sum().item()
                count+=y.numel()
        return {'loss':total/count if count else 0.0,'accuracy':correct/count if count else 0.0}
    finally:
        model.train(mode)
''',
               [check('evaluate_binary(torch.nn.Identity(),[(torch.zeros(3),torch.tensor([1.,1.,1.])),(torch.zeros(1),torch.tensor([0.]))])',{'loss':0.69314718056,'accuracy':0.75},label='尾批按样本聚合'),
                check('evaluate_binary(torch.nn.Identity(),[])',{'loss':0,'accuracy':0},label='空数据'),
                check('m.training and bool(m.flags) and not any(m.flags)',True,setup='class Probe(torch.nn.Module):\n    def __init__(self):\n        super().__init__();self.flags=[]\n    def forward(self,x):\n        self.flags.append(torch.is_grad_enabled());return x\nm=Probe()\nevaluate_binary(m,[(torch.ones(1,requires_grad=True),torch.ones(1))])',label='前向关闭梯度并恢复模式'),
                check('m.training',False,setup='m=torch.nn.Identity();m.eval()\nevaluate_binary(m,[])',label='原eval保持不变'),
                check('m.training',True,setup='class Broken(torch.nn.Module):\n    def forward(self,x):raise RuntimeError("fail")\nm=Broken()\ntry:evaluate_binary(m,[(torch.ones(1),torch.ones(1))])\nexcept RuntimeError:pass',label='异常仍恢复模式')],
               '累计sum损失和样本数，避免尾批偏差。eval、no_grad与finally恢复模式分别解决层行为、图记录和后续训练状态。',['pt20','pt21','pt22','pt23']),
        coding('11-c2',c,
               '实现 resume_sgd_step(model,optimizer,path,x,y)。path是可信CPU checkpoint，键为model、optimizer、epoch；模型及SGD优化器结构匹配，模型输出与y均为[B,1]。先恢复两种state_dict，切train，清旧梯度，用mean MSE完成一次更新。返回(保存epoch+1,本次更新前MSE的Python float)。加载使用map_location="cpu",weights_only=True。',
               'def resume_sgd_step(model, optimizer, path, x, y)',
               '''def resume_sgd_step(model,optimizer,path,x,y):
    state=torch.load(path,map_location='cpu',weights_only=True)
    model.load_state_dict(state['model'])
    optimizer.load_state_dict(state['optimizer'])
    model.train()
    optimizer.zero_grad()
    loss=((model(x)-y)**2).mean()
    loss.backward()
    optimizer.step()
    return state['epoch']+1,loss.item()
''',
               [check('result',[6,4],setup=_resume_setup(),label='恢复轮数并返回更新前损失'),
                check('m.weight',[[0.1]],setup=_resume_setup(),label='恢复momentum后正确更新'),
                check('o.state[m.weight]["momentum_buffer"]',[[9]],setup=_resume_setup(),label='优化器动量必须恢复'),
                check('m.training and isinstance(result[1],float)',True,setup=_resume_setup(),label='训练模式和Python标量')],
               '续训必须恢复优化器的动量等状态，不只恢复学习率；先清旧梯度再用新损失反向。保存epoch与下一轮编号按题面区分。',['pt24','pt25','t5'])]
    bank.exam('chapter-c11','chapter','训练、评估与恢复 · 章末验收',[c],10,q,'通过指标聚合和真实续训检验训练代码的完整性。')

    c='c12'
    q=[
        out('12-o1',c,'写出两行输出；macro F1包括全部3类，零分母类别记0。',
            'import torch\ncm=torch.tensor([[2,0,0],[1,1,0],[0,0,0]])\ntp=cm.diag().double()\nden=cm.sum(0)+cm.sum(1)\nf1=torch.where(den>0,2*tp/den.clamp_min(1),torch.zeros_like(tp))\nprint(cm.sum(0).tolist())\nprint(round(f1.mean().item(),4))',
            '[3, 1, 0]\n0.4889','列和是各类预测数。逐类F1分别0.8、2/3、0，对三类等权平均约0.4889。',['pt27']),
        out('12-o2',c,'写出因果平均的输出。',
            'import torch\nscores=torch.zeros(3,3,dtype=torch.float64)\nscores=scores.masked_fill(torch.triu(torch.ones(3,3,dtype=torch.bool),1),float("-inf"))\nv=torch.tensor([2.,6.,10.],dtype=torch.float64)\nprint([round(z,2) for z in (scores.softmax(-1)@v).tolist()])',
            '[2.0, 4.0, 6.0]','第i行只在0..i上归一化；零分数使每个可见value等权，因此分别取各前缀均值。',['pt29']),
        choice('12-m1',c,'模型Linear(D,1)输出单logit，标签是0/1浮点数。哪种二分类训练接口最合适？',
               ['先argmax得到整数，再用MSE','BCEWithLogitsLoss直接接收logit与同形标签','先sigmoid再交给BCEWithLogitsLoss'],1,
               'BCEWithLogitsLoss内部做稳定的sigmoid与log计算；重复sigmoid改变损失含义，单logit也没有可供类别argmax的维。',['pt26','t6']),
        choice('12-m2',c,'训练完成后为了报告独立验证表现，应怎样处理验证数据？',
               ['detach后拼回训练集再训练几轮','仅在eval与no_grad下评估，不能参与本次参数更新','只要不调用验证输入.grad，怎样使用都行'],1,
               'detach只能切断输入图，不能阻止验证标签影响模型参数。独立验证要求验证数据不参加训练更新。',['pt30','pt28']),
        coding('12-c1',c,
               '实现 prefix_masked_mean(x,valid)。x形状[B,T,D]、valid为bool[B,T]，CPU浮点，有效位置有限，无效可含NaN/Inf。返回同形张量，第t步仅平均0..t内有效token；此前没有有效token时返回零。支持空B/T，不修改输入并保留有效输入梯度。',
               'def prefix_masked_mean(x, valid)',
               '''def prefix_masked_mean(x,valid):
    total=x.masked_fill(~valid.unsqueeze(-1),0).cumsum(1)
    counts=valid.cumsum(1).unsqueeze(-1).clamp_min(1)
    return total/counts
''',
               [check('prefix_masked_mean(torch.tensor([[[2.],[99.],[6.],[10.]]]),torch.tensor([[True,False,True,True]]))',[[[2],[2],[4],[6]]],label='每步只使用有效前缀'),
                check('prefix_masked_mean(torch.tensor([[[float("nan")],[4.]]]),torch.tensor([[False,True]]))',[[[0],[4]]],label='首个有效token之前为零'),
                check('list(prefix_masked_mean(torch.empty(2,0,3),torch.empty(2,0,dtype=torch.bool)).shape)',[2,0,3],label='空序列'),
                check('x.grad',[[[1.5],[0],[0.5]]],setup='x=torch.tensor([[[2.],[9.],[6.]]],requires_grad=True)\nprefix_masked_mean(x,torch.tensor([[True,False,True]]))[:,-2:].sum().backward()',label='因果累计的输入梯度')],
               '累积和与有效计数必须同步沿序列轴进行；只用前缀信息自然避免未来泄漏，masked_fill屏蔽非有限padding。',['pt28','pt29']),
        coding('12-c2',c,
               '实现 fit_affine(x,y,steps=100,lr=0.1)。x是非空CPU float32[N,D]、D>=1，y为同样本数[N,1] float32，数据有限。创建含bias的Linear(D,1)，权重和bias清零，用全批SGD和mean MSE训练steps次，返回{weight:一维Python列表,bias:Python float}。steps>=0；遵守传入lr，不修改输入。',
               'def fit_affine(x, y, steps=100, lr=0.1)',
               '''def fit_affine(x,y,steps=100,lr=0.1):
    x=x.detach();y=y.detach()
    m=torch.nn.Linear(x.shape[1],1)
    torch.nn.init.zeros_(m.weight)
    torch.nn.init.zeros_(m.bias)
    o=torch.optim.SGD(m.parameters(),lr=lr)
    for _ in range(steps):
        o.zero_grad()
        loss=((m(x)-y)**2).mean()
        loss.backward()
        o.step()
    return {'weight':m.weight.detach().flatten().tolist(),'bias':m.bias.item()}
''',
               [check('fit_affine(torch.tensor([[1.],[2.]]),torch.tensor([[3.],[5.]]),steps=1)',{'weight':[1.3],'bias':0.8},label='一次更新的真实梯度'),
                check('fit_affine(torch.ones(2,3),torch.ones(2,1),steps=0)',{'weight':[0,0,0],'bias':0},label='零步与维度配置'),
                check('fit_affine(torch.ones(2,2),torch.ones(2,1),steps=3,lr=0)',{'weight':[0,0],'bias':0},label='零学习率'),
                check('fit_affine(x,y,steps=180)',{'weight':[2,-1],'bias':0.5},setup='x=torch.tensor([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])\ny=2*x[:,:1]-x[:,1:2]+0.5',tolerance=1e-3,label='学习多特征仿射关系')],
               '从可控多特征目标验证完整优化流程。必须按目标形状[N,1]计算MSE，避免广播成[N,N]。',['t6','pt26','pt30'])]
    bank.exam('chapter-c12','chapter','综合实验与挑战 · 章末验收',[c],10,q,'检查因果信息边界、序列聚合和完整拟合过程。')

    _add_cumulative(bank,out,choice,coding,backward_probe)
    _add_stage(bank,out,choice,coding)
    _add_review(bank,out,choice,coding,backward_probe)
    result=bank.result()
    assert len(result['items'])==68
    assert len(result['exercises'])==25
    return result


def _resume_setup():
    return '''
m=torch.nn.Linear(1,1,bias=False)
with torch.no_grad():m.weight.fill_(1)
o=torch.optim.SGD(m.parameters(),lr=0.1,momentum=0.5)
o.state[m.weight]['momentum_buffer']=torch.tensor([[2.]])
torch.save({'model':m.state_dict(),'optimizer':o.state_dict(),'epoch':5},'resume.pt')
with torch.no_grad():m.weight.fill_(9)
m.weight.grad=torch.tensor([[100.]])
o.param_groups[0]['lr']=9
m.eval()
result=resume_sgd_step(m,o,'resume.pt',torch.tensor([[2.]]),torch.tensor([[0.]]))
'''


def _add_cumulative(bank,out,choice,coding,backward_probe):
    c='c09'
    q=[
        out('cum09-o1',c,'写出两行标准输出。',
            'groups={}\nfor name,value in [("b",2),("a",0),("b",6)]:\n    groups.setdefault(name,[]).append(value)\ncopy_of_b=groups["b"][:]\ncopy_of_b.append(10)\nprint(list(groups))\nprint(groups["b"],copy_of_b)',
            "['b', 'a']\n[2, 6] [2, 6, 10]",'字典保留首次插入顺序；切片建立新列表，追加不会修改原分组。',['p2','p5','py14','py15']),
        out('cum09-o2',c,'写出标准输出。',
            'import torch\nx=torch.tensor([[1.,5.,9.],[3.,6.,9.]])\nlabels=torch.tensor([2,0])\nselected=x[torch.arange(2),labels]\nprint(selected.tolist())\nprint((selected-x.mean(1)).tolist())',
            '[9.0, 3.0]\n[4.0, -3.0]',
            '行列索引逐项配对，目标分数为9与3；减去对应行均值5与6，得到4和-3。',['t1','pt02','t2']),
        choice('cum09-m1',c,'程序用float("nan")读入一个损失记录，随后按loss最小挑checkpoint。哪项处理最可靠？',
               ['先判断math.isfinite(loss)，无效记录不进入排序','NaN总比所有数大，可以直接min','先把所有loss转int'],0,
               'NaN不满足通常的全序比较，且int(NaN)会报错。应在进入最优选择前检查有限性。',['py18','py19','py13']),
        choice('cum09-m2',c,'已得到多个需要梯度的标量loss，怎样合成总损失并保留回到各输入的图？',
               ['torch.tensor(losses).sum()','torch.stack(losses).sum()','sum(v.item() for v in losses)'],1,
               'stack是可微组合操作；重新构造torch.tensor会重新包装数值，item则直接转Python数值，均会丢失原图关系。',['p4','pt12','pt11']),
        coding('cum09-c1',c,
               '实现 pack_events(rows)。rows是字典list，每项含sample字符串与features有限数值list；非空时所有features具有相同正长度D。按sample首次出现顺序分组，将各组特征逐维求均值，返回(keys,means)，keys为字符串list，means为float32[G,D]张量。空rows返回([],float32[0,0]张量)，不修改输入。',
               'def pack_events(rows)',
               '''def pack_events(rows):
    if not rows:return [],torch.empty(0,0,dtype=torch.float32)
    groups={}
    for row in rows:
        groups.setdefault(row['sample'],[]).append(row['features'])
    keys=list(groups)
    means=torch.stack([torch.tensor(groups[k],dtype=torch.float32).mean(0) for k in keys])
    return keys,means
''',
               [check('pack_events([{"sample":"b","features":[2,4]},{"sample":"a","features":[0,8]},{"sample":"b","features":[6,10]}])',[['b','a'],[[4,7],[0,8]]],label='稳定分组与逐维均值'),
                check('list(pack_events([])[1].shape)',[0,0],label='空记录形状'),
                check('pack_events([{"sample":"x","features":[0]}])',[['x'],[[0]]],label='合法零特征'),
                check('rows==old',True,setup='import copy\nrows=[{"sample":"x","features":[1,2]}]\nold=copy.deepcopy(rows)\npack_events(rows)',label='不污染原记录')],
               '先用Python字典维护组与顺序，再把同组矩阵转成张量沿样本轴平均。组大小不应被误当特征维。',['py14','py15','p5','t1']),
        coding('cum09-c2',c,
               '实现 batch_linear_gradient(batches,initial)。initial是有限CPU float32[D]，D>=1；batches为非空list，每项X[B,D]和y[B]为有限CPU float32，总样本数大于0，允许某批B=0。以initial的副本为需梯度叶子，对整体mean((X@w-y)**2)逐批backward，返回[D]梯度张量；不修改initial或其已有.grad。',
               'def batch_linear_gradient(batches, initial)',
               '''def batch_linear_gradient(batches,initial):
    w=initial.detach().clone().requires_grad_(True)
    n=sum(y.numel() for x,y in batches)
    for x,y in batches:
        ((x@w-y).square().sum()/n).backward()
    return w.grad
''',
               [check('batch_linear_gradient([(torch.tensor([[1.,0.],[0.,2.]]),torch.tensor([2.,-2.])),(torch.tensor([[1.,1.]]),torch.tensor([0.]))],torch.zeros(2))',[-4/3,8/3],label='不同批大小与向量参数'),
                check('batch_linear_gradient([(torch.empty(0,2),torch.empty(0)),(torch.tensor([[1.,2.]]),torch.tensor([0.]))],torch.tensor([1.,1.]))',[6,12],label='非零初值与空批'),
                check('initial.grad',[9],setup='initial=torch.tensor([2.],requires_grad=True)\ninitial.grad=torch.tensor([9.])\nbatch_linear_gradient([(torch.tensor([[1.]]),torch.tensor([1.]))],initial)',label='原参数梯度不受污染'),
                check('_uses_autograd(batch_linear_gradient,[(torch.ones(1,1),torch.zeros(1))],torch.zeros(1))',True,setup=backward_probe,label='真实反向传播')],
               '参数副本切断外部历史图；各批sum除以全部样本数后累积，矩阵乘法将梯度送回向量参数。',['pt01','pt11','pt12','pt15'])]
    bank.exam('cumulative-09','cumulative','累计验收 · Python 到自动微分',[f'c{i:02d}' for i in range(1,10)],25,q,'把Python分组、数据校验与张量梯度放在新任务中综合检查。')

    c='c12'
    q=[
        out('cum12-o1',c,'写出标准输出。',
            'class Meter:\n    def __init__(self):self.total=0;self.n=0\n    def update(self,value,n):self.total+=value*n;self.n+=n\nm=Meter()\nm.update(2,3)\nm.update(10,1)\nprint(m.total,m.n,m.total/m.n)',
            '16 4 4.0','状态类累计的是加权总和与真实数量，(2×3+10×1)/4=4。',['py25','pt21']),
        out('cum12-o2',c,'写出标准输出。',
            'import torch\nm=torch.nn.Dropout(1.0)\nx=torch.ones(2,requires_grad=True)\nold=m.training\nm.eval()\nwith torch.no_grad():y=m(x)*2\nm.train(old)\nprint(m.training,y.requires_grad,y.tolist())',
            'True False [2.0, 2.0]','eval让Dropout成为恒等映射；后续乘法在no_grad中不建图，最后恢复原train模式。',['pt19','pt20']),
        choice('cum12-m1',c,'Adam模型续训时只恢复model.state_dict，优化器使用全新状态。即使学习率相同，最可能发生什么？',
               ['一定逐步复现原训练轨迹','丢失动量等优化器状态，更新轨迹可能改变','模型所有参数会自动变成零'],1,
               'Adam的历史一阶、二阶估计属于优化器状态。恢复模型权重不等于恢复完整优化过程。',['pt24','pt25']),
        choice('cum12-m2',c,'要比较两种模型的独立验证表现，哪种标准化流程正确？',
               ['用训练集计算均值/尺度，原样应用到验证集','训练与验证拼在一起拟合标准化参数','分别标准化验证集以使其均值必为0'],0,
               '预处理参数也属于从数据学习的状态，应仅由训练数据确定。单独重拟合验证统计会改变模型实际看到的坐标。',['py30','pt30']),
        coding('cum12-c1',c,
               '实现 balanced_sample_weights(labels)。labels是CPU一维long张量，类别编号为非负整数且不要求连续。返回同长float32张量，每个样本权重=其类别出现次数的倒数。空输入返回形状[0] float32，不修改labels。',
               'def balanced_sample_weights(labels)',
               '''def balanced_sample_weights(labels):
    if labels.numel()==0:return torch.empty(0,dtype=torch.float32)
    _,inverse,counts=torch.unique(labels,return_inverse=True,return_counts=True)
    return 1/counts[inverse].float()
''',
               [check('balanced_sample_weights(torch.tensor([0,0,1]))',[0.5,0.5,1],label='类频率倒数'),
                check('balanced_sample_weights(torch.tensor([9,5,9,5,9]))',[1/3,0.5,1/3,0.5,1/3],label='不连续类别保留样本顺序'),
                check('[list(balanced_sample_weights(torch.empty(0,dtype=torch.long)).shape),str(balanced_sample_weights(torch.empty(0,dtype=torch.long)).dtype)]',[[0],'torch.float32'],label='空输入与dtype'),
                check('x',[2,2,7],setup='x=torch.tensor([2,2,7])\nbalanced_sample_weights(x)',label='不修改标签')],
               '统计类别频率后再映射回原样本位置；不能直接按类别排序输出权重，否则会丢失样本对应关系。',['py14','p5','pt02','pt18']),
        coding('cum12-c2',c,
               '实现 evaluate_masked_tokens(model,batches)。每项x[B,T,D]、y[B,T]，model输出有限logits[B,T,C]，C>=1；y为long，有效标签合法，-100为忽略项。eval+no_grad下按全部有效token聚合交叉熵和准确率，返回{loss:float,accuracy:float,count:int}；没有有效token时loss/accuracy均0。成功或异常均恢复原模式，不更新参数。',
               'def evaluate_masked_tokens(model, batches)',
               '''def evaluate_masked_tokens(model,batches):
    mode=model.training
    model.eval()
    total=0.0;correct=0;count=0
    try:
        with torch.no_grad():
            for x,y in batches:
                logits=model(x)
                valid=y!=-100
                selected=logits[valid]
                labels=y[valid]
                if labels.numel():
                    total+=torch.nn.functional.cross_entropy(selected,labels,reduction='sum').item()
                    correct+=(selected.argmax(-1)==labels).sum().item()
                    count+=labels.numel()
        return {'loss':total/count if count else 0.0,'accuracy':correct/count if count else 0.0,'count':count}
    finally:
        model.train(mode)
''',
               [check('evaluate_masked_tokens(torch.nn.Identity(),[(torch.zeros(1,3,2),torch.tensor([[0,0,-100]])),(torch.zeros(1,1,2),torch.tensor([[1]]))])',{'loss':0.69314718056,'accuracy':2/3,'count':3},label='按有效token聚合'),
                check('evaluate_masked_tokens(torch.nn.Identity(),[(torch.ones(1,2,3),torch.tensor([[-100,-100]]))])',{'loss':0,'accuracy':0,'count':0},label='全忽略'),
                check('evaluate_masked_tokens(torch.nn.Identity(),[])',{'loss':0,'accuracy':0,'count':0},label='空数据'),
                check('m.training and bool(m.flags) and not any(m.flags)',True,setup='class Probe(torch.nn.Module):\n    def __init__(self):super().__init__();self.flags=[]\n    def forward(self,x):self.flags.append(torch.is_grad_enabled());return x\nm=Probe()\nevaluate_masked_tokens(m,[(torch.zeros(1,1,2,requires_grad=True),torch.tensor([[0]]))])',label='真实关闭前向图并恢复模式')],
               '先按二维mask选出有效token，将[B,T,C]化为[有效数,C]。分母是有效token总数，既不是batch数也不是序列数。',['pt08','pt18','pt20','pt23','pt28'])]
    bank.exam('cumulative-12','cumulative','累计验收 · 从数据到独立评估',[f'c{i:02d}' for i in range(1,13)],25,q,'结合Python状态管理、采样权重和带padding的真实评估循环。')


def _add_stage(bank,out,choice,coding):
    c='c12'
    q=[
        out('stage-o1',c,'写出标准输出。',
            'rows=[{"x":0,"y":1},{"x":2,"y":5},{"y":7}]\nvalid=[r for r in rows if "x" in r and "y" in r]\nprint(len(valid),sum(r["y"] for r in valid))\nprint([r["x"] for r in valid])',
            '2 6\n[0, 2]','检查键是否存在能保留合法的0；if r.get("x")会误删这条数据。',['p5','py13','py19','py24']),
        out('stage-o2',c,'一次SGD更新后写出输出。',
            'import torch\nm=torch.nn.Linear(1,1)\nwith torch.no_grad():\n    m.weight.zero_();m.bias.zero_()\no=torch.optim.SGD(m.parameters(),lr=0.1)\nx=torch.tensor([[1.],[2.]])\ny=torch.tensor([[3.],[5.]])\no.zero_grad()\nloss=(m(x)-y).square().mean()\nloss.backward();o.step()\nprint(round(loss.item(),2),round(m.weight.item(),2),round(m.bias.item(),2))',
            '17.0 1.3 0.8','初始MSE=(9+25)/2=17，权重梯度-13、bias梯度-8，学习率0.1对应参数1.3和0.8。',['t5','t6','pt25']),
        choice('stage-m1',c,'下面哪项最能证明验证样本没有参与参数训练？',
               ['验证输入的.grad是None','同一训练集与超参数下，改动验证标签不会改变训练后的模型参数','程序调用过detach'],1,
               '输入无.grad或被detach并不能阻止验证标签参与loss更新参数；训练结果对验证标签保持不变才检查了数据边界。',['py30','pt30']),
        choice('stage-m2',c,'模型仍是train模式，但评估前向已放入no_grad。包含Dropout的验证指标为何仍可能不可靠？',
               ['no_grad会随机修改模型权重','Dropout仍按训练行为丢弃激活，还需要eval','no_grad只对long张量有效'],1,
               '图记录与层行为是独立开关。no_grad不把Dropout切换到评估行为，验证通常同时使用eval与no_grad。',['pt19','pt20','pt23']),
        choice('stage-m3',c,'最后一批只有1条样本，其余批有8条。记录一轮mean loss时最稳妥的做法是？',
               ['所有批的mean直接平均','累计每批sum loss，最后除全部样本数','丢掉最后一批的loss'],1,
               'sum再除总数让每条样本权重相同。批次mean直接平均会放大尾批；丢弃则不能报告全部数据表现。',['py25','pt15','pt21']),
        coding('stage-c1',c,
               '实现 prepare_regression(rows,feature_names)。rows是dict列表；feature_names是非空且不重复的字符串列表。只保留所有指定特征及target均存在、类型为int/float（排除bool）且有限的记录，其他记录跳过。按原行顺序与feature_names顺序返回float32张量(x[N,D],y[N,1])；空结果仍保留D。不修改输入，不转换数值字符串。',
               'def prepare_regression(rows, feature_names)',
               '''def prepare_regression(rows,feature_names):
    import math
    xs=[];ys=[]
    keys=list(feature_names)+['target']
    for row in rows:
        if all(k in row and type(row[k]) in (int,float) and math.isfinite(row[k]) for k in keys):
            xs.append([row[k] for k in feature_names])
            ys.append([row['target']])
    return torch.tensor(xs,dtype=torch.float32).reshape(-1,len(feature_names)),torch.tensor(ys,dtype=torch.float32).reshape(-1,1)
''',
               [check('prepare_regression([{"a":0,"b":2,"target":1},{"a":"3","b":4,"target":5},{"a":7,"target":9},{"a":2,"b":4,"target":float("nan")}],["b","a"])',[[[2,0]],[[1]]],label='过滤坏记录并保留零和特征顺序'),
                check('[list(t.shape) for t in prepare_regression([],["a","b","c"])]',[[0,3],[0,1]],label='空结果形状'),
                check('prepare_regression([{"a":True,"target":2},{"a":float("inf"),"target":3},{"a":2.5,"target":4}],["a"])',[[[2.5]],[[4]]],label='拒绝bool与非有限值'),
                check('rows==old',True,setup='import copy\nrows=[{"a":1,"target":2}]\nold=copy.deepcopy(rows)\nprepare_regression(rows,["a"])',label='不修改源记录'),
                check('all(t.dtype==torch.float32 for t in prepare_regression([{"a":1,"target":2}],["a"]))',True,label='统一训练dtype')],
               '字段存在性、类型和有限性分开检查，合法零值不能用真值过滤。先固定列顺序，再显式保留空张量的二维形状。',['py13','py19','py24','pt01','pt17']),
        coding('stage-c2',c,
               '实现 fit_standardized_regressor(x,y,steps=100,lr=0.1)。x为非空有限CPU float32[N,D]、D>=1，y为float32[N,1]。仅由x拟合逐列mean与总体std(unbiased=False)，scale=std.clamp_min(1e-6)。标准化后，用零初始化含bias的Linear(D,1)和SGD训练steps次mean MSE；记录每次更新前loss.item()。返回{model,mean:[D]张量,scale:[D]张量,losses:Python float列表}。steps>=0；不改输入。',
               'def fit_standardized_regressor(x, y, steps=100, lr=0.1)',
               '''def fit_standardized_regressor(x,y,steps=100,lr=0.1):
    x=x.detach();y=y.detach()
    mean=x.mean(0)
    scale=x.std(0,unbiased=False).clamp_min(1e-6)
    features=(x-mean)/scale
    model=torch.nn.Linear(x.shape[1],1)
    torch.nn.init.zeros_(model.weight);torch.nn.init.zeros_(model.bias)
    optimizer=torch.optim.SGD(model.parameters(),lr=lr)
    losses=[]
    for _ in range(steps):
        optimizer.zero_grad()
        loss=(model(features)-y).square().mean()
        losses.append(loss.item())
        loss.backward();optimizer.step()
    return {'model':model,'mean':mean,'scale':scale,'losses':losses}
''',
               [check('[r["mean"],r["scale"],r["losses"]]',[[2,5],[1,1e-6],[]],setup='r=fit_standardized_regressor(torch.tensor([[1.,5.],[3.,5.]]),torch.tensor([[0.],[1.]]),steps=0)',tolerance=1e-8,label='训练统计与常数列保护'),
                check('[r["model"].weight,r["model"].bias,r["losses"]]',[[[0.4]],[0],[4]],setup='r=fit_standardized_regressor(torch.tensor([[-1.],[1.]]),torch.tensor([[-2.],[2.]]),steps=1)',label='一次标准化SGD更新'),
                check('len(r["losses"])==60 and r["losses"][-1]<0.001',True,setup='x=torch.tensor([[-1.,-1.],[-1.,1.],[1.,-1.],[1.,1.]])\ny=2*x[:,:1]-x[:,1:2]+0.5\nr=fit_standardized_regressor(x,y,steps=60)',label='完整多特征训练'),
                check('r["model"].weight',[[0]],setup='r=fit_standardized_regressor(torch.tensor([[-1.],[1.]]),torch.tensor([[-2.],[2.]]),steps=2,lr=0)',label='尊重学习率'),
                check('torch.equal(x,old) and all(isinstance(v,float) for v in r["losses"])',True,setup='x=torch.tensor([[1.],[3.]])\nold=x.clone()\nr=fit_standardized_regressor(x,torch.tensor([[2.],[4.]]),steps=2)',label='输入不变且日志为Python数值')],
               '预处理状态与模型一起返回，供验证阶段复用。总体std适用于本题约定，常数列需保护；训练图、日志值和参数更新各司其职。',['t1','t2','t5','t6','pt16','pt25','pt30']),
        coding('stage-c3',c,
               '实现 evaluate_saved_regressor(bundle,x,y)。bundle含model、训练集拟合的mean[D]与scale[D]>0；模型输出[N,1]。x是CPU有限float32[N,D]，y为float32[N,1]。只能复用bundle统计做标准化，临时eval+no_grad评估，返回{mse:Python float,mae:Python float,count:Python int}，count=N；空N两项误差0。成功或异常均恢复原模式，不更新参数或修改输入。',
               'def evaluate_saved_regressor(bundle, x, y)',
               '''def evaluate_saved_regressor(bundle,x,y):
    model=bundle['model'];mode=model.training
    model.eval()
    try:
        with torch.no_grad():
            if len(x)==0:return {'mse':0.0,'mae':0.0,'count':0}
            residual=model((x-bundle['mean'])/bundle['scale'])-y
            return {'mse':residual.square().mean().item(),'mae':residual.abs().mean().item(),'count':len(x)}
    finally:
        model.train(mode)
''',
               [check('evaluate_saved_regressor({"model":torch.nn.Identity(),"mean":torch.tensor([10.]),"scale":torch.tensor([2.])},torch.tensor([[12.],[16.]]),torch.tensor([[0.],[1.]]))',{'mse':2.5,'mae':1.5,'count':2},label='只复用训练统计'),
                check('evaluate_saved_regressor({"model":torch.nn.Identity(),"mean":torch.zeros(1),"scale":torch.ones(1)},torch.empty(0,1),torch.empty(0,1))',{'mse':0,'mae':0,'count':0},label='空验证集'),
                check('m.training and bool(m.flags) and not any(m.flags)',True,setup='class Probe(torch.nn.Module):\n    def __init__(self):super().__init__();self.flags=[]\n    def forward(self,x):self.flags.append(torch.is_grad_enabled());return x\nm=Probe()\nevaluate_saved_regressor({"model":m,"mean":torch.zeros(1),"scale":torch.ones(1)},torch.ones(1,1,requires_grad=True),torch.zeros(1,1))',label='评估前向无图并恢复原模式'),
                check('m.training',False,setup='m=torch.nn.Identity();m.eval()\nevaluate_saved_regressor({"model":m,"mean":torch.zeros(1),"scale":torch.ones(1)},torch.ones(1,1),torch.zeros(1,1))',label='原eval状态不变'),
                check('m.training',True,setup='class Broken(torch.nn.Module):\n    def forward(self,x):raise RuntimeError("fail")\nm=Broken()\ntry:evaluate_saved_regressor({"model":m,"mean":torch.zeros(1),"scale":torch.ones(1)},torch.ones(1,1),torch.zeros(1,1))\nexcept RuntimeError:pass',label='异常恢复状态')],
               '验证数据必须使用训练坐标系。eval与no_grad分别控制层和图，finally避免验证失败后遗留错误模式；按全部目标元素计算误差。',['pt20','pt21','pt23','pt30'])]
    bank.exam('stage-torch','stage','阶段验收 · 完整数据、训练与评估',[f'c{i:02d}' for i in range(1,13)],45,q,'独立完成记录清洗、训练统计、真实SGD和无泄漏验证；交卷后统一查看讲评。')


def _add_review(bank,out,choice,coding,backward_probe):
    review=[]
    c='c07'
    review.append(out('r07-o',c,'写出两行标准输出。',
        'import torch\nx=torch.arange(12).reshape(2,2,3).transpose(1,2)\nprint(list(x.shape))\nprint(x.flatten(1)[0].tolist())',
        '[2, 3, 2]\n[0, 3, 1, 4, 2, 5]','转置改变逻辑轴顺序；flatten按当前张量的逻辑顺序合并特征，非连续不等于顺序丢失。',['pt01','pt05']))
    review.append(coding('r07-c',c,
        '实现 length_mask(lengths,max_len)。lengths为整数list，0<=每个长度<=max_len，max_len>=0。返回CPU bool[B,max_len]张量，每行前length个位置True，其余False；支持空list与max_len=0。',
        'def length_mask(lengths, max_len)',
        '''def length_mask(lengths,max_len):
    return torch.arange(max_len)[None,:]<torch.tensor(lengths,dtype=torch.long)[:,None]
''',
        [check('length_mask([0,2,3],3)',[[False,False,False],[True,True,False],[True,True,True]],label='不同长度'),
         check('list(length_mask([],4).shape)',[0,4],label='空批次'),
         check('list(length_mask([0,0],0).shape)',[2,0],label='零长度上限'),
         check('str(length_mask([1],1).dtype)','torch.bool',label='bool类型')],
        '比较位置编号和各行长度，通过[B,1]与[1,T]广播一次构造所有有效位。',['pt04','t2']))
    c='c08'
    review.append(out('r08-o',c,'写出标准输出。',
        'import torch\nx=torch.tensor([[1000.,1000.],[-1000.,-1000.]],dtype=torch.float64)\nz=x-x.max(-1,keepdim=True).values\np=z.exp()/z.exp().sum(-1,keepdim=True)\nprint(p.tolist())',
        '[[0.5, 0.5], [0.5, 0.5]]','大数与负大数都先平移到0；相同logit的概率相等，不受公共偏移影响。',['pt06','pt07']))
    review.append(coding('r08-c',c,
        '实现 weighted_values(scores,values)。scores是有限CPU浮点[B,K]、values为同dtype[B,K,D]，K,D>=1。沿K对scores做稳定softmax，再对value加权，返回[B,D]；支持B=0且保留两输入的梯度。不修改输入。',
        'def weighted_values(scores, values)',
        '''def weighted_values(scores,values):
    return (scores.softmax(-1).unsqueeze(-1)*values).sum(1)
''',
        [check('weighted_values(torch.zeros(1,3),torch.tensor([[[1.,2.],[3.,4.],[8.,9.]]]))',[[4,5]],label='均匀权重'),
         check('weighted_values(torch.tensor([[1000.,1000.]]),torch.tensor([[[2.],[6.]]]))',[[4]],label='大数稳定性'),
         check('list(weighted_values(torch.empty(0,2),torch.empty(0,2,3)).shape)',[0,3],label='空批次'),
         check('values.grad',[[[0.5],[0.5]]],setup='scores=torch.zeros(1,2,requires_grad=True)\nvalues=torch.tensor([[[2.],[6.]]],requires_grad=True)\nweighted_values(scores,values).sum().backward()',label='value梯度'),
         check('scores.grad',[[-1,1]],setup='scores=torch.zeros(1,2,requires_grad=True)\nvalues=torch.tensor([[[2.],[6.]]])\nweighted_values(scores,values).sum().backward()',label='score梯度也必须连通')],
        'softmax沿候选K轴分配权重，unsqueeze使同一权重作用到该候选的全部特征，然后沿K归约。',['pt06','pt10','t2']))
    c='c09'
    review.append(out('r09-o',c,'写出标准输出。',
        'import torch\nx=torch.tensor(2.,requires_grad=True)\na=x*3\nb=x.detach()*5\n(a+b).backward()\nprint((a+b).item(),x.grad.item())',
        '16.0 3.0','detach分支仍贡献函数值10，但不贡献回到x的梯度；可微分支只贡献3。',['pt12','t3']))
    review.append(coding('r09-c',c,
        '实现 grad_wrt_input(matrix,x)。matrix为有限CPU float64[M,D]，x为float64[D]，D>=1、M>=0。用真实autograd计算 sum((matrix@x)**2) 对x的梯度并返回[D]张量。不得修改x、matrix或x已有.grad；允许x本来requires_grad=True。',
        'def grad_wrt_input(matrix, x)',
        '''def grad_wrt_input(matrix,x):
    leaf=x.detach().clone().requires_grad_(True)
    loss=(matrix@leaf).square().sum()
    return torch.autograd.grad(loss,leaf)[0]
''',
        [check('grad_wrt_input(torch.tensor([[1.,2.],[0.,3.]],dtype=torch.float64),torch.tensor([1.,2.],dtype=torch.float64))',[10,56],label='矩阵复合函数的梯度'),
         check('grad_wrt_input(torch.empty(0,2,dtype=torch.float64),torch.ones(2,dtype=torch.float64))',[0,0],label='无输出行'),
         check('x.grad',[7,8],setup='x=torch.tensor([1.,2.],dtype=torch.float64,requires_grad=True)\nx.grad=torch.tensor([7.,8.],dtype=torch.float64)\ngrad_wrt_input(torch.eye(2,dtype=torch.float64),x)',label='外部梯度不受污染'),
         check('str(grad_wrt_input(torch.eye(1,dtype=torch.float64),torch.ones(1,dtype=torch.float64)).dtype)','torch.float64',label='保留双精度'),
         check('_uses_autograd(grad_wrt_input,torch.eye(2,dtype=torch.float64),torch.ones(2,dtype=torch.float64))',True,setup=backward_probe,label='真实自动微分')],
        '在独立叶子副本上求导，避免累积到调用者已有.grad；矩阵乘法的反向传播会合并所有输出行贡献。',['pt12','pt13','pt15']))
    c='c10'
    review.append(choice('r10-m',c,'collate_fn仅收到一条一维特征向量样本（向量长度D）。输出batch应该怎样组织？',
        ['特征[D]、标签标量','特征[1,D]、标签[1]，保留batch轴','无论如何squeeze所有长度1的维'],1,
        '单样本仍是一个batch。删除batch轴会让模型输入和指标代码在尾批大小1时突然改变含义。',['pt17','pt18']))
    review.append(coding('r10-c',c,
        '实现 PairedClassifier(left_dim,right_dim,classes)，继承nn.Module。参数均为正整数；模型含一个带bias的Linear(left_dim+right_dim,classes)。forward(left,right)按最后一维拼接两个同batch的二维浮点特征，返回原始logits[B,classes]。支持B=0，参数注册，保留左右输入梯度。',
        'class PairedClassifier(torch.nn.Module)',
        '''class PairedClassifier(torch.nn.Module):
    def __init__(self,left_dim,right_dim,classes):
        super().__init__()
        self.projection=torch.nn.Linear(left_dim+right_dim,classes)
    def forward(self,left,right):
        return self.projection(torch.cat([left,right],dim=-1))
''',
        [check('list(PairedClassifier(2,3,4)(torch.ones(1,2),torch.ones(1,3)).shape)',[1,4],label='单样本保持batch轴'),
         check('sum(p.numel() for p in PairedClassifier(2,3,4).parameters())',24,label='参数注册'),
         check('list(PairedClassifier(1,2,3)(torch.empty(0,1),torch.empty(0,2)).shape)',[0,3],label='空batch'),
         check('left.grad is not None and right.grad is not None',True,setup='m=PairedClassifier(2,1,2)\nleft=torch.ones(2,2,requires_grad=True)\nright=torch.ones(2,1,requires_grad=True)\nm(left,right).sum().backward()',label='两路特征梯度'),
         check('m(torch.tensor([[2.,3.]]),torch.tensor([[4.]]))',[[432]],setup='m=PairedClassifier(2,1,1)\nprojection=next(v for v in m.modules() if isinstance(v,torch.nn.Linear))\nwith torch.no_grad():\n    projection.weight.copy_(torch.tensor([[1.,10.,100.]]));projection.bias.zero_()',label='左右特征拼接顺序')],
        'cat合并已有的特征轴，而stack会额外新增一轴。将Linear保存为Module属性才能注册其参数。',['t4','pt16','pt18']))
    c='c11'
    review.append(out('r11-o',c,'阈值是logit>=0为正类，写出TP、FP、FN。',
        'import torch\nlogits=torch.tensor([0.,-1.,2.,3.])\ny=torch.tensor([1,1,0,1])\np=logits>=0\nt=y==1\nprint((p&t).sum().item(),(p&~t).sum().item(),(~p&t).sum().item())',
        '2 1 1','零logit也预测正类；第0和3条为TP，第2条为FP，第1条为FN。',['pt22','pt23']))
    review.append(coding('r11-c',c,
        '实现 snapshot_train_state(model,optimizer,epoch)，返回键model、optimizer、epoch的字典，前两项分别是对应state_dict的独立深拷贝。此处不写磁盘；以后修改模型参数、优化器学习率或动量张量，均不能改变该快照。epoch是Python int。',
        'def snapshot_train_state(model, optimizer, epoch)',
        '''def snapshot_train_state(model,optimizer,epoch):
    import copy
    return {'model':copy.deepcopy(model.state_dict()),'optimizer':copy.deepcopy(optimizer.state_dict()),'epoch':epoch}
''',
        [check('s["epoch"]',8,setup='m=torch.nn.Linear(1,1);o=torch.optim.SGD(m.parameters(),lr=0.2)\ns=snapshot_train_state(m,o,8)',label='轮数保留'),
         check('s["model"]["weight"]',[[1]],setup='m=torch.nn.Linear(1,1,bias=False)\nwith torch.no_grad():m.weight.fill_(1)\no=torch.optim.SGD(m.parameters(),lr=0.2)\ns=snapshot_train_state(m,o,1)\nwith torch.no_grad():m.weight.fill_(9)',label='模型参数深拷贝'),
         check('s["optimizer"]["param_groups"][0]["lr"]',0.2,setup='m=torch.nn.Linear(1,1);o=torch.optim.SGD(m.parameters(),lr=0.2)\ns=snapshot_train_state(m,o,1)\no.param_groups[0]["lr"]=9',label='优化器容器独立'),
         check('next(iter(s["optimizer"]["state"].values()))["momentum_buffer"]',[[2]],setup='m=torch.nn.Linear(1,1,bias=False);o=torch.optim.SGD(m.parameters(),lr=0.2,momentum=0.9)\no.state[m.weight]["momentum_buffer"]=torch.tensor([[2.]])\ns=snapshot_train_state(m,o,1)\no.state[m.weight]["momentum_buffer"].fill_(9)',label='动量张量深拷贝')],
        '内存里的最佳训练状态必须递归复制容器和张量。只复制外层dict，或直接保存state_dict引用，都不足以隔离后续更新。',['pt24','pt25','py17']))
    c='c12'
    review.append(out('r12-o',c,'写出标准输出。',
        'import torch\nx=torch.tensor([[[2.],[8.],[20.]]])\nmask=torch.tensor([[False,True,True]])\ntotal=x.masked_fill(~mask.unsqueeze(-1),0).cumsum(1)\ncount=mask.cumsum(1).unsqueeze(-1).clamp_min(1)\nprint((total/count).flatten().tolist())',
        '[0.0, 8.0, 14.0]','无有效前缀返回0；随后分别平均[8]和[8,20]，未来值20不能影响第1步。',['pt28','pt29']))
    review.append(coding('r12-c',c,
        '实现 masked_class_counts(logits,labels,valid)。logits为有限CPU浮点[B,T,C]、C>=1，labels为long[B,T]，valid为同形bool；有效标签在[0,C)，无效标签可为-100。返回long[C,C]混淆矩阵，行是真实类、列是argmax预测类（平局选首类）。忽略所有无效位置，支持空B/T，不修改输入。',
        'def masked_class_counts(logits, labels, valid)',
        '''def masked_class_counts(logits,labels,valid):
    c=logits.shape[-1]
    truth=labels[valid]
    preds=logits.argmax(-1)[valid]
    return torch.bincount(truth*c+preds,minlength=c*c).reshape(c,c)
''',
        [check('masked_class_counts(torch.tensor([[[0.,2.],[3.,0.],[8.,0.]]]),torch.tensor([[1,1,-100]]),torch.tensor([[True,True,False]]))',[[0,0],[1,1]],label='行真实列预测且忽略padding'),
         check('masked_class_counts(torch.zeros(1,2,3),torch.tensor([[-100,-100]]),torch.zeros(1,2,dtype=torch.bool))',[[0,0,0],[0,0,0],[0,0,0]],label='全部忽略'),
         check('masked_class_counts(torch.empty(0,2,2),torch.empty(0,2,dtype=torch.long),torch.empty(0,2,dtype=torch.bool))',[[0,0],[0,0]],label='空批次'),
         check('masked_class_counts(torch.zeros(1,1,2),torch.tensor([[1]]),torch.ones(1,1,dtype=torch.bool))',[[0,0],[1,0]],label='平局预测首类'),
         check('str(masked_class_counts(torch.empty(2,0,3),torch.empty(2,0,dtype=torch.long),torch.empty(2,0,dtype=torch.bool)).dtype)','torch.int64',label='空序列与整数计数类型')],
        '先过滤无效位置再用真实类*C+预测类编码计数，避免-100进入索引。minlength保证未出现类别仍保留完整矩阵。',['pt27','pt28','pt30']))
    bank.review(*review)
