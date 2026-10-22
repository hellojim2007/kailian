"""Torch handovers: tensor basics -> a working training loop -> extensions."""
from guide_lessons import guide

guide('t1','tensor reduce','py27 py29',
 '先认识张量的类型和轴，再做归约。暂不要求会优化器、GPU或注意力。',
 'import torch并创建浮点张量，先打印shape确认[B,D]。|每行的特征轴是dim=1，mean后得到[B]。|直接返回Tensor，不能tolist或item后冒充张量结果；这两者只用于观察。',
 '创建[[1.,3.],[5.,7.]]张量，输出其shape列表和逐行均值的tolist，各一行。',
 'import torch\nx=torch.tensor([[1.,3.],[5.,7.]])\nprint(list(x.shape))\nprint(x.mean(1).tolist())', '[2, 2]\n[2.0, 6.0]')
guide('pt01','reshape tensor','t1',
 '先保留batch含义，再合并特征轴；非连续与空批次是同一API的边界，而不是新算法。',
 '输入至少二维，第一轴始终是样本数。|使用flatten(start_dim=1)合并后续轴，不写死图像或特征维数。|分别检查普通、转置、空批次；不把整个张量展成一维。',
 '创建torch.arange(12).reshape(2,2,3)，保留batch轴展平，输出形状列表及第二条样本列表。',
 'import torch\nx=torch.arange(12).reshape(2,2,3)\ny=x.flatten(1)\nprint(list(y.shape))\nprint(y[1].tolist())', '[2, 6]\n[6, 7, 8, 9, 10, 11]')
guide('t2','broadcast reduce','t1 pt01',
 '在推荐路线中先于复杂索引练广播，避免后续一出现[B,1]就只能照抄。',
 '先求x.mean(1,keepdim=True)，明确它的shape是[B,1]。|用x减去该均值张量，结果形状保持[B,D]。|用非方阵验证能运行，再用方阵对照错误版本，不能把不报错当正确。',
 '对[[1.,5.,9.],[2.,4.,6.]]逐行减均值，输出结果tolist。',
 'import torch\nx=torch.tensor([[1.,5.,9.],[2.,4.,6.]])\nmean=x.mean(1,keepdim=True)\nprint((x-mean).tolist())', '[[-4.0, 0.0, 4.0], [-2.0, 0.0, 2.0]]')
guide('pt02','gather tensor','t2',
 '只增加“每行取不同列”这一索引模式，不同时要求完整分类损失。',
 '读取B=logits.shape[0]并构造行索引。|把行索引与labels成对索引，或者先把labels扩成[B,1]再gather。|返回[B]，保留dtype与求导路径；禁止先tolist再重新包装。',
 '从x=[[2.,9.,4.],[8.,3.,5.]]按labels=[2,0]取每行分数，print结果tolist。',
 'import torch\nx=torch.tensor([[2.,9.,4.],[8.,3.,5.]])\nlabels=torch.tensor([2,0])\nprint(x[torch.arange(2),labels].tolist())', '[4.0, 8.0]')
guide('pt03','mask reduce broadcast','pt02',
 '先清除无效位置，再归约有效数据；全空行单独通过安全计数处理。',
 'safe=x.masked_fill(~mask,0)，不要用乘法屏蔽NaN。|每行sum除以mask.sum(1).clamp_min(1)。|两者都得到[B]，全无效行0/1为0；输入不做原地修改。',
 'x=[[2.,99.,4.]]，mask=[[True,False,True]]，忽略无效项后求行均值，print tolist。',
 'import torch\nx=torch.tensor([[2.,99.,4.]])\nmask=torch.tensor([[True,False,True]])\nsafe=x.masked_fill(~mask,0)\nprint((safe.sum(1)/mask.sum(1).clamp_min(1)).tolist())', '[3.0]')
guide('pt04','pad tensor slice','pt03 py05',
 '把Python右补齐经验迁移到指定dtype和shape的张量；原零token与补齐零不能混淆。',
 '按原行长求L，分配[B,L] long tokens和bool mask。|逐行把长度n的序列写入tokens[i,:n]，对应mask设True。|空批次保持[0,0]，全空行仍保留B；不要用tokens!=0重建mask。',
 '分配一行宽3的long tokens和bool mask，把原序列[0,8]写入前两位，输出两者tolist。',
 'import torch\ntokens=torch.zeros((1,3),dtype=torch.long)\nmask=torch.zeros((1,3),dtype=torch.bool)\ntokens[0,:2]=torch.tensor([0,8])\nmask[0,:2]=True\nprint(tokens.tolist())\nprint(mask.tolist())', '[[0, 8, 0]]\n[[True, True, False]]')
guide('pt05','broadcast reduce grad','pt15 t2',
 '成对距离是向量化综合回访。先手算一对，再明确[N,M,D]中间量的含义。',
 'x[:,None,:]是[N,1,D]，y[None,:,:]是[1,M,D]。|广播相减得到每对差值[N,M,D]，逐元素平方。|沿最后特征轴sum得到[N,M]；保留Tensor计算图，不额外sqrt。',
 'x=[[0.,0.],[1.,2.]]，y=[[1.,0.]]，用广播求成对平方距离并print tolist。',
 'import torch\nx=torch.tensor([[0.,0.],[1.,2.]])\ny=torch.tensor([[1.,0.]])\nd=((x[:,None,:]-y[None,:,:])**2).sum(-1)\nprint(d.tolist())', '[[1.0], [4.0]]')
guide('pt06','softmax reduce broadcast','pt26 t2',
 '手写数值稳定公式放在已经会训练之后；先理解实际softmax的轴，再理解为什么平移不改变概率。',
 '沿最后一轴取最大值并keepdim。|中心化后exp，再除以同一轴的指数总和。|检查大正数、最后一轴和为1、shape不变及反传；不要调用被本题禁止的softmax。',
 '对[[500.,500.]]按减最大值、exp、除总和手写概率，print tolist，不能直接softmax。',
 'import torch\nx=torch.tensor([[500.,500.]])\nm=x.max(-1,keepdim=True).values\ne=(x-m).exp()\nprint((e/e.sum(-1,keepdim=True)).tolist())', '[[0.5, 0.5]]')
guide('pt07','softmax reduce','pt06',
 '在同一稳定平移技巧上增加log与恢复偏移，避免一次引入完整交叉熵。',
 '先保留最后轴求最大值m，算sum(exp(x-m))。|对和取log后加回m。|只移除被归约的最后轴，不能裸squeeze把其他长度1的轴也删掉。',
 'x=[[100.,100.]]，用m+log(sum(exp(x-m)))计算，print形状列表和保留6位小数的标量值。',
 'import torch\nx=torch.tensor([[100.,100.]])\nm=x.max(-1,keepdim=True).values\ny=(m+(x-m).exp().sum(-1,keepdim=True).log()).squeeze(-1)\nprint(list(y.shape))\nprint(round(y.item(),6))', '[1]\n100.693146')
guide('pt08','maskedloss softmax gather','pt07 pt25 t3',
 '在自动微分与稳定logsumexp都学过后，再实现带忽略标签的损失，消除早期先修倒挂。',
 'valid=labels!=ignore_index；先筛选logits与labels，再按类别索引。|每行损失是logsumexp减去目标类logit，对有效行取mean。|没有有效行时返回logits.sum()*0.0，让零仍能反传；不要把ignore_index直接当索引。',
 '创建requires_grad的[[3.,4.]]，构造与输入相连的标量零，backward后输出零值与输入grad.tolist。',
 'import torch\nx=torch.tensor([[3.,4.]],requires_grad=True)\ny=x.sum()*0.0\ny.backward()\nprint(y.item())\nprint(x.grad.tolist())', '0.0\n[[0.0, 0.0]]')
guide('pt09','matmul reshape','pt05 pt08',
 '拆多头只改变轴的组织，不改变token顺序。把每一步shape写在变量旁再实现。',
 '检查H>0且D能整除H，算Dh=D//H。|reshape为[B,T,H,Dh]，此时token仍在第二轴。|permute(0,2,1,3)得到[B,H,T,Dh]；不能直接reshape到目标形状。',
 'x=torch.arange(8).reshape(1,2,4)，拆H=2为[1,2,2,2]并换轴，输出第0个head的tolist。',
 'import torch\nx=torch.arange(8).reshape(1,2,4)\ny=x.reshape(1,2,2,2).permute(0,2,1,3)\nprint(y[0,0].tolist())', '[[0, 1], [4, 5]]')
guide('pt10','matmul attention softmax','pt09 pt06',
 '先把单头注意力分成分数、权重、加权和三步；这里没有因果mask。',
 'q与转置后的k矩阵乘得到[B,Tq,Tk]，除以sqrt(D)。|沿最后的key轴计算稳定softmax。|权重乘v得到[B,Tq,Dv]；Tq和Tk不必相等。',
 '给定weights=[[[0.25,0.75]]]，v=[[[2.],[6.]]]，用矩阵乘法输出加权结果tolist。',
 'import torch\nweights=torch.tensor([[[0.25,0.75]]])\nv=torch.tensor([[[2.],[6.]]])\nprint((weights@v).tolist())', '[[[5.0]]]')
guide('t3','grad tensor','pt04',
 '先在一个浮点标量上走通自动微分，再写模型；手算导数只用来核对。',
 'x=torch.tensor(float(value),requires_grad=True)，确保是浮点叶子。|用x构造x*x+3*x并backward。|读取x.grad.item()作为返回值；不要返回y、x或backward的None结果。',
 '创建x=3.0需要梯度，计算y=x*x+2*x，backward后输出x的Python梯度数值。',
 'import torch\nx=torch.tensor(3.,requires_grad=True)\ny=x*x+2*x\ny.backward()\nprint(x.grad.item())', '8.0')
guide('pt11','gradclear grad','t3',
 '用两次独立前向观察.grad的累计，再清空重算，避免直接背zero_grad顺序。',
 '按任务每次重新计算表达式并backward，第一次累计结束后保存Python数值。|设置x.grad=None后，再对新计算的x*x反传。|返回两阶段读数；不要让后一次清空改变先前已记录的结果。',
 'x=2.0，先对3*x反传，再对4*x反传；输出累计梯度。清空后对x*x反传，再输出梯度。',
 'import torch\nx=torch.tensor(2.,requires_grad=True)\n(x*3).backward()\n(x*4).backward()\nprint(x.grad.item())\nx.grad=None\n(x*x).backward()\nprint(x.grad.item())', '7.0\n4.0')
guide('pt12','detach grad','pt11',
 '排错先找计算图从哪一步断开，不能只写出一个数值上看似正确的梯度公式。',
 '由输入数值列表创建一次浮点叶子x。|保持x*x等Tensor运算，不用torch.tensor包已有计算结果，不提前item。|sum成标量并backward，再返回原x.grad。',
 'x=[1.,4.]需要梯度，clone后求平方和并反传，print原x.grad.tolist。',
 'import torch\nx=torch.tensor([1.,4.],requires_grad=True)\ny=x.clone()\n(y*y).sum().backward()\nprint(x.grad.tolist())', '[2.0, 8.0]')
guide('pt13','grad arithmetic','t6 pt12',
 '数值差分是验证工具，不是自动微分的替代实现；把同一多项式在两条计算路径中比较。',
 '一条路径使用float64叶子构造多项式并backward。|另一条用普通数值计算(f(v+eps)-f(v-eps))/(2*eps)。|返回(autograd梯度,中心差分梯度)两个Python数值，不增加第三项；eps太小也有浮点舍入问题。',
 '对f(x)=x*x，在x=3、eps=0.001用中心差分计算导数，print round(derivative,6)。',
 'x=3.0\neps=0.001\ndef f(value):\n    return value*value\nderivative=(f(x+eps)-f(x-eps))/(2*eps)\nprint(round(derivative,6))', '6.0')
guide('pt14','norm gradclear','pt13 t5',
 '先看一个3-4-5范数例子，再把相同缩放因子应用于所有参数梯度。',
 '收集grad不是None的参数，累计平方和开根号。|按指定系数min(1,max_norm/(原范数+1e-6))，在no_grad中把所有有效grad乘同一比例。|零梯度和空集合要安全处理；返回裁剪前范数，而不是裁剪后值。',
 '梯度向量[6.,8.]范数为10。裁剪到上限5，print原范数与裁剪后tolist，各一行。',
 'import torch\ng=torch.tensor([6.,8.])\nnorm=g.square().sum().sqrt()\nscale=min(1.0,5.0/norm.item())\nprint(norm.item())\nprint((g*scale).tolist())', '10.0\n[3.0, 4.0]')
guide('pt15','weighted gradclear mse','pt14 pt21',
 '把Python加权平均知识迁移到梯度。分批方案可以变，总体目标函数必须保持不变。',
 '先统计全部样本总数。|每批平方误差求sum，再除同一个总数并backward；循环中不清空梯度。|返回w.grad.item；不等批次时各批mean除批次数会改变每个样本的权重。',
 '两个micro-batch的mean loss是2与10、样本数3与1，按样本权重计算整体mean，print结果。',
 'means=[2.0,10.0]\nsizes=[3,1]\nprint(sum(m*n for m,n in zip(means,sizes))/sum(sizes))', '4.0')
guide('t4','module class','t6 py25',
 '先训练过手写参数，再学习Module如何组织这些参数，理解框架替你管理了什么。',
 '继承nn.Module，在__init__首部super().__init__。|把nn.Linear(3,2)赋给self的属性。|forward中调用该层并return；在外部用model(x)验证[B,3]变为[B,2]。',
 '创建nn.Linear(4,2)，输出weight.shape列表及参数总数量，各一行。',
 'import torch\nlayer=torch.nn.Linear(4,2)\nprint(list(layer.weight.shape))\nprint(sum(p.numel() for p in layer.parameters()))', '[2, 4]\n10')
guide('pt16','sequential module','t4',
 '在单层模型上只增加隐藏层和非线性，把shape和参数数算清楚。',
 '顺序放Linear(in_dim,hidden)、ReLU、Linear(hidden,classes)。|每层默认带bias，不能漏算或意外关闭。|返回模型对象，不返回其一次计算输出；输入batch数改变时仍应成立。',
 '创建Linear(2,4)→ReLU→Linear(4,1)，输出零输入[3,2]的输出shape列表和参数总数。',
 'import torch\nm=torch.nn.Sequential(torch.nn.Linear(2,4),torch.nn.ReLU(),torch.nn.Linear(4,1))\nprint(list(m(torch.zeros(3,2)).shape))\nprint(sum(p.numel() for p in m.parameters()))', '[3, 1]\n17')
guide('pt17','dataset detach protocol','pt16 py27',
 '用已经学过的Python索引协议，增加Tensor副本、dtype和数据接口要求。',
 '构造检查样本数一致，分别clone保存特征和标签。|__len__返回第一轴样本数；__getitem__返回本题规定的特征/标签副本。|检查构造后改外部输入、取出后改样本都不应污染Dataset。',
 'x=[[1.,2.]]，创建data=x.detach().clone()；把x[0,0]改99，print data.tolist。',
 'import torch\nx=torch.tensor([[1.,2.]])\ndata=x.detach().clone()\nx[0,0]=99\nprint(data.tolist())', '[[1.0, 2.0]]')
guide('pt18','stack dataset tuplezip','pt17',
 '先用两个同长样本练stack，再编写接收样本列表的collate函数。',
 '从samples分别收集一维特征和整数标签。|torch.stack(features)得到[B,D]；torch.tensor(labels,dtype=long)得到[B]。|不要cat成[B*D]，也不要把标签作浮点特征堆叠；空samples必须抛ValueError。',
 'samples=[(tensor([1.,2.]),0),(tensor([3.,4.]),1)]，分别组批，输出特征shape列表和标签tolist。',
 'import torch\nsamples=[(torch.tensor([1.,2.]),0),(torch.tensor([3.,4.]),1)]\nx=torch.stack([row[0] for row in samples])\ny=torch.tensor([row[1] for row in samples],dtype=torch.long)\nprint(list(x.shape))\nprint(y.tolist())', '[2, 2]\n[0, 1]')
guide('pt19','freeze module mode','pt26 pt18',
 '这是训练范围管理的进阶回访：参数是否求导、优化器持有哪些参数、模型模式需要分别考虑。',
 '对backbone所有parameters调用requires_grad_(False)。|对head全部parameters启用求导，保留真实参数对象。|返回list(model.head.parameters())；不克隆、不返回全模型参数。',
 '创建两个Linear组成的Sequential，冻结第0层，print全部参数的requires_grad列表。',
 'import torch\nm=torch.nn.Sequential(torch.nn.Linear(2,2),torch.nn.Linear(2,1))\nfor p in m[0].parameters():\n    p.requires_grad_(False)\nprint([p.requires_grad for p in m.parameters()])', '[False, False, True, True]')
guide('pt20','mode module','pt18',
 '预测函数要避免悄悄改变下一次训练的行为，先教模式与梯度两条独立控制线。',
 '记录原model.training，切换eval。|try中配合no_grad前向并return。|finally中model.train(old_mode)，即使前向抛异常也恢复。',
 '创建Linear(1,1)，记录原模式，eval+no_grad计算一次，print输出requires_grad，再恢复并print model.training。',
 'import torch\nm=torch.nn.Linear(1,1)\nold=m.training\nm.eval()\nwith torch.no_grad():\n    out=m(torch.ones(1,1))\nprint(out.requires_grad)\nm.train(old)\nprint(m.training)', 'False\nTrue')
guide('t5','sgd gradclear','pt12',
 '推荐路线把这一步放在Module之前，用一个标量完整走通优化流程。',
 '创建浮点叶子w，交给SGD([w],lr=0.1)。|按清梯度、计算新loss、backward、step四步执行一次。|更新后return w.item；用手算w-0.1*2*(w-3)对照，但正式实现使用真实SGD。',
 'w从2.0开始，loss=(w-5)**2，SGD学习率0.1更新一次，print round(w.item(),3)。',
 'import torch\nw=torch.tensor(2.,requires_grad=True)\nopt=torch.optim.SGD([w],lr=0.1)\nopt.zero_grad()\nloss=(w-5)**2\nloss.backward()\nopt.step()\nprint(round(w.item(),3))', '2.6')
guide('t6','mse sgd','t5',
 '先训练两个手写参数拟合直线，再学分类训练。每轮操作与上一课完全一致，只增加数据和重复。',
 '创建给定x和y，w、b都从0浮点叶子开始。|SGD必须同时持有w与b；100轮中每轮重新前向并清梯度。|循环后返回两个Python数值；检查它们接近2和1，不直接返回正确常量。',
 'x=[-1.,0.,1.]，target=2*x+1，w=b=0时计算MSE，print round(loss.item(),6)。',
 'import torch\nx=torch.tensor([-1.,0.,1.])\ntarget=2*x+1\nw=torch.tensor(0.)\nb=torch.tensor(0.)\nloss=((w*x+b-target)**2).mean()\nprint(round(loss.item(),6))', '3.666667')
guide('pt21','weighted mse mode','pt20 t6',
 '整个epoch的MSE要给每个目标元素相同权重；不是把每批loss读数直接平均。',
 '记录原模式，eval与no_grad遍历。|每批误差平方求sum累加，并用target.numel累计元素总数。|结束后总和除总元素数，空集合返回0，finally恢复模式。',
 '两批误差分别为[1.,3.,2.]、[4.]，累计平方和除总元素数，print整体MSE。',
 'import torch\nbatches=[torch.tensor([1.,3.,2.]),torch.tensor([4.])]\ntotal=0.0\ncount=0\nfor error in batches:\n    total+=error.square().sum().item()\n    count+=error.numel()\nprint(total/count)', '7.5')
guide('pt22','binary metrics','pt21',
 '先从logit符号得到预测，再由布尔条件数出TP/FP/FN，不让指标公式和张量API一起成为跳步。',
 'pred=logits>=0，labels按真实正负理解。|用&组合布尔条件并sum得到TP、FP、FN。|各零分母按题目返回0，最后返回Python数值字典；logit=0要算正类。',
 'logits=[-1.,0.,2.]、labels=[0,0,1]，输出预测布尔列表，再输出TP和FP数量（同一行）。',
 'import torch\nlogits=torch.tensor([-1.,0.,2.])\nlabels=torch.tensor([0,0,1])\npred=logits>=0\ntp=(pred&(labels==1)).sum().item()\nfp=(pred&(labels==0)).sum().item()\nprint(pred.tolist())\nprint(tp,fp)', '[False, True, True]\n1 1')
guide('pt23','classification mode weighted','pt22 pt20',
 '先独立认识cross_entropy的输入约定，再合并评估模式、损失加权与准确率。',
 'eval与no_grad下，对每批logits计算交叉熵总量与正确数。|按全体样本数聚合loss与accuracy，不能按批次平均。|空数据给约定默认值，恢复原模式；不要在验证中调用optimizer.step。',
 'logits=[[1.,3.],[4.,2.]]、labels=[1,0]，用argmax得到类别，print预测列表与正确数。',
 'import torch\nlogits=torch.tensor([[1.,3.],[4.,2.]])\nlabels=torch.tensor([1,0])\npred=logits.argmax(1)\nprint(pred.tolist())\nprint((pred==labels).sum().item())', '[1, 0]\n2')
guide('pt24','checkpoint module','pt23',
 '先区分模型对象、当前状态字典和独立快照，再练磁盘保存恢复。',
 '把模型state_dict、优化器state_dict、epoch放到规定键中torch.save。|load时指定CPU，分别load_state_dict到已有模型和优化器。|返回保存的epoch；路径和键名属于接口，不自行改名。',
 '创建Linear(3,1)，deepcopy其state_dict，print排序后的键列表和weight.shape列表。',
 'import torch\nimport copy\nm=torch.nn.Linear(3,1)\nsnapshot=copy.deepcopy(m.state_dict())\nprint(sorted(snapshot))\nprint(list(snapshot["weight"].shape))', "['bias', 'weight']\n[1, 3]")
guide('pt25','classification sgd module','pt24',
 '已经会单步SGD与分类损失后，把它们合成可复用的分类训练函数。',
 'model.train()启用训练模式，optimizer.zero_grad。|计算logits与cross_entropy，用Tensor loss.backward并step。|最后return loss.item供记录；不能提前把loss变成Python数再反传。',
 '创建全零logits形状[2,2]并requires_grad=True、labels=[0,1]，交叉熵backward后print梯度shape和loss保留6位。',
 'import torch\nlogits=torch.zeros(2,2,requires_grad=True)\nlabels=torch.tensor([0,1])\nloss=torch.nn.functional.cross_entropy(logits,labels)\nloss.backward()\nprint(list(logits.grad.shape))\nprint(round(loss.item(),6))', '[2, 2]\n0.693147')
guide('pt26','binary sgd module','pt25',
 '从已会的多分类训练迁移到单logit二分类，只改变模型输出、目标dtype和损失API。',
 '构造CPU线性层并转换到x.dtype，按任务规则零初始化。|每步squeeze(-1)得到[B]，标签也转同dtype，用BCEWithLogits反传更新。|记录每步Python loss，按任务返回参数和曲线；steps=0时也保留正确初值结构。',
 'logits=torch.zeros(3)，targets=[0.,1.,1.]，用BCEWithLogits计算loss并print保留6位小数。',
 'import torch\nlogits=torch.zeros(3)\ntargets=torch.tensor([0.,1.,1.])\nloss=torch.nn.functional.binary_cross_entropy_with_logits(logits,targets)\nprint(round(loss.item(),6))', '0.693147')
guide('pt27','metrics tensor nested','pt26',
 '先给矩阵轴定义明确含义，再从每类TP/FP/FN算macro F1；与二分类指标形成递进。',
 '创建classes×classes的独立整数行列表。|每对(target,pred)更新confusion[target][pred]。|逐类从对角、列和、行和算F1，零分母按约定处理，再对所有classes平均。',
 'preds=[1,0,1]、targets=[0,0,1]、classes=2，构造行真实列预测的混淆矩阵并print。',
 'preds=[1,0,1]\ntargets=[0,0,1]\nmatrix=[[0,0],[0,0]]\nfor pred,target in zip(preds,targets):\n    matrix[target][pred]+=1\nprint(matrix)', '[[1, 1], [0, 1]]')
guide('pt28','mask broadcast reduce','pt05 pt03',
 '进阶池化复用已掌握mask与广播，只增加token轴和每token特征向量。',
 'mask由[B,T]扩成[B,T,1]，沿特征轴广播。|替换无效token的全部特征，再沿T轴求和得到[B,D]。|有效token数保持[B,1]并clamp_min，保证全无效句返回零且忽略NaN/Inf。',
 'x=[[[1.,3.],[99.,99.],[5.,7.]]]，mask=[[True,False,True]]，输出有效token均值tolist。',
 'import torch\nx=torch.tensor([[[1.,3.],[99.,99.],[5.,7.]]])\nmask=torch.tensor([[True,False,True]])\nsafe=x.masked_fill(~mask[:,:,None],0)\ncount=mask.sum(1,keepdim=True).clamp_min(1)\nprint((safe.sum(1)/count).tolist())', '[[3.0, 5.0]]')
guide('pt29','attention matmul mask','pt10 pt28',
 '最后才给注意力加入未来遮罩；先验证“改变未来v不影响过去输出”这一因果性质。',
 '与单头注意力相同地构造scaled scores。|triu(1)创建严格上三角未来mask，在softmax前填-inf。|沿key轴归一化后乘v，检查对角线可见、第一token只看自己以及梯度仍保留。',
 '创建3×3全零分数，严格上三角填-inf再softmax，print前两行权重tolist。',
 'import torch\nscores=torch.zeros(3,3)\nfuture=torch.ones(3,3,dtype=torch.bool).triu(1)\nweights=scores.masked_fill(future,float("-inf")).softmax(-1)\nprint(weights[:2].tolist())', '[[1.0, 0.0, 0.0], [0.5, 0.5, 0.0]]')
guide('pt30','classification binary sgd mode','pt27 pt26',
 '结业任务用两个logit表示两个类别：Linear(D,2)+交叉熵，与上一课的单logit+BCE接口不同。验证数据不能参加更新。',
 '创建零初始化Linear(D,2)，用SGD与交叉熵仅在训练集更新epochs轮。|训练完成后eval+no_grad，分别计算训练loss、验证loss和验证accuracy；不要求每轮历史曲线。|返回model及三个Python指标，model保持eval；验证标签变化不应影响训练后的参数。',
 'logits=[[-2.,0.],[1.,2.],[0.,1.]]、targets=[1,1,0]，按每行argmax预测，print准确率保留6位；不要更新参数。',
 'import torch\nlogits=torch.tensor([[-2.,0.],[1.,2.],[0.,1.]])\ntargets=torch.tensor([1,1,0])\naccuracy=(logits.argmax(1)==targets).float().mean()\nprint(round(accuracy.item(),6))', '0.666667')
