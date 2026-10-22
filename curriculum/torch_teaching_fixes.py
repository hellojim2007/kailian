"""Lesson-by-lesson semantic review, applied after legacy examples are assembled.

This changes teaching prose only: exercise IDs, contracts, executable examples,
quiz answers, grading tests and reference implementations remain intact.
"""

_TORCH_TEACHING = {
    't1': (
        '把输入x的两维标成[B,D]：B条样本、每条D个特征。row_means只沿dim=1取mean，返回[B]张量；例如[[1,3],[2,6]]得到[2,4]。dim=0会改成每列的跨样本均值，和本题接口不同。',
        '分别检查多行、多特征与D=1。D=1时每行均值就是那一行唯一的数；返回值仍须是torch.Tensor，不能用tolist或print替代return。'),
    'pt01': (
        '先把x.shape[0]认作批次轴，只合并第1维及后面的特征。flatten(start_dim=1)把[B,C,H,W]变成[B,C*H*W]；二维[B,D]输入不再改变形状。',
        '用转置后的非连续张量检查元素顺序，再检查B=0仍得到[0,特征数]。view要求合适的存储布局，view(B,-1)在空批次上也可能无法推断维度；不要把batch一起展平。'),
    'pt02': (
        'logits是[B,C]，labels是[B]。创建与logits同设备的行号arange(B)，和labels逐项配对索引，得到每条样本自己的目标类别分数，结果为[B]。',
        '用不同样本选择不同类别检查配对语义，再检查单样本和B=0。logits[:,labels]会让所有行选择同一组列，形成[B,B]，并非本题目标；返回结果应保留dtype和输入梯度。'),
    'pt03': (
        '先用x.masked_fill(~mask,0)将无效位置替换为0，再沿dim=1求和。分母必须是mask.sum(1)的有效数量，clamp_min(1)只保护全无效行；不能用完整特征宽度作分母。',
        '有效数为0的行应得到0；有效数值本身为0仍要计数。无效位置允许NaN/Inf，乘mask无法排除它们，因为NaN*0与Inf*0仍是NaN。还要检查空批次、不修改x、以及有效位置的梯度。'),
    'pt04': (
        '由序列数得到B，由最大原长度得到T，分别创建long类型tokens[B,T]和bool类型mask[B,T]。每条原序列写入前length个位置，同时将这段mask设True，右侧保留补齐零。',
        '空批次明确返回[0,0]；B条全空序列应保持[B,0]。零token可以是合法数据，所以mask依据原长度建立，不能使用tokens!=0；两项的dtype也必须分别检查。'),
    'pt05': (
        'x[:,None,:]是[N,1,D]，y[None,:,:]是[1,M,D]。相减广播成[N,M,D]，逐特征平方后只沿最后一维求和，得到任意两条样本之间的平方距离[N,M]。',
        '用N和M不同、相同向量距离为0、以及N=0或M=0检查shape。题目要求平方距离，不开根号；全部运算保留为张量，才能保留dtype、device和梯度。'),
    't2': (
        '先计算row_mean=x.mean(dim=1,keepdim=True)，其shape为[B,1]，再返回x-row_mean。长度1的特征轴会扩展到D，每一行都减去本行均值，输出仍为[B,D]。',
        '先用[[1,3],[2,6]]核对结果[[-1,1],[-2,2]]，再用B和D不同的输入检查。省略keepdim可能报广播错误；当B=D时也可能无报错却按列算错。D=1时每行结果应为0，不原地修改输入。'),
    'pt06': (
        '沿最后一维取最大值m并keepdim=True，计算z=x-m，再令e=exp(z)，最后e/e.sum(-1,keepdim=True)。同一行的公共指数因子在分子分母抵消，所以概率不因平移改变。',
        '输入有限且最后一维非空。用1000级正数、负大数、相同值、单类别和三维张量核对稳定性与shape；结果应保留梯度。本题练习手写公式，不直接调用现成softmax。'),
    'pt07': (
        '计算m=x.max(-1,keepdim=True).values，再求m+log(sum(exp(x-m)))。中间归约保留维度以便广播；最后只squeeze(-1)，使输出恰好删除原来的最后一维。',
        '输入有限且最后一维非空。一维输入归约成标量张量，[1,D]输入则得到[1]；无参数squeeze会把batch=1也删掉。用正负大数检查稳定性，并把减去的最大值加回来。'),
    'pt08': (
        '先建立valid=labels!=ignore_index并过滤行，再用有效标签选取目标logit。每行交叉熵是logsumexp(有效logits)-目标logit，最后只对有效行取mean；不能先拿-100作类别索引。',
        '全部忽略或空批次时，有限logits的sum()*0提供与输入图连接的零；这不是修复模型NaN的办法。检查混合有效/忽略标签、只按有效行平均、以及零损失仍可反向。本题不直接调用现成cross_entropy。'),
    'pt09': (
        '把[B,T,D]先reshape为[B,T,H,D/H]，此时每个token的特征仍在一起；再permute(0,2,1,3)交换token与head轴，得到[B,H,T,D/H]。',
        '先拒绝H<=0或D不能整除H。用arange编号检查每个token在各head中拿到哪段特征，再测试非连续输入。直接reshape(B,H,T,D/H)只有shape看起来相同，元素的语义归属可能已经错位。'),
    'pt10': (
        '计算q@k.transpose(-1,-2)/sqrt(D)，分数shape为[B,Tq,Tk]。沿最后的key轴做softmax，为每个query分配一组key权重；再乘v[B,Tk,Dv]，得到[B,Tq,Dv]。',
        '测试Tq和Tk不同、Dv和D不同的情况，避免各维碰巧相同掩盖错误。零分数时输出应是全部value的均值；改变query应影响权重，并保持计算图。本题不调用现成注意力函数。'),
    't3': (
        '主示例与第一概念题先用y=x²说明求导：x=3时函数值9、梯度6。完整代码题改为y=x²+3x，因此导数为2x+3；创建浮点叶子x，构造该损失，backward后返回x.grad.item()。',
        '明确区分函数值、梯度和所选函数：完整题x=2时函数值10、梯度7；不能照搬x²的梯度4。每次调用新建叶子，检查0与负输入；不要先把损失item()成Python数值再求导。'),
    'pt11': (
        '对同一叶子x，先由新图计算x²并backward，再由另一份新图计算3x并backward，记录累计的2x+3。随后将x.grad置None或清零，重新前向x²并backward，记录仅2x的梯度。',
        '返回两个Python数值，顺序是累计梯度、清空后的梯度。x=0能区分3和0，负数检查符号。两份独立图可以分别反向；包含已释放中间量的旧图不能直接重复backward，清梯度也不会重建旧图。'),
    'pt12': (
        '把数值列表构造成float64、requires_grad=True的叶子x，直接用x.square().sum()形成损失再backward。如果逐项组合已有标量张量，用stack保留关系，而不是torch.tensor重新包装。',
        '返回x.grad这个一维张量，而非Python列表；空列表也应给空梯度张量。检查正负值与0，并实际调用autograd，不能直接写出2*x冒充求导过程。item只用于报告，不用于重建损失。'),
    'pt13': (
        '固定同一个函数f(x)=x³+2x²-4x：一条路线用float64叶子和backward取得autograd梯度；另一条路线在x.detach()的前后两点求[f(x+eps)-f(x-eps)]/(2eps)。',
        '返回(autograd梯度,中心差分梯度)两个Python数值，数值近似必须使用传入的正eps。检查正数、0、负数和普通小数；步长过小会放大相消误差，不能简单认为越小越准，也不能两项都代解析公式。'),
    'pt14': (
        '收集所有非None的参数梯度，把它们的平方和相加后开方得到全局L2范数。按min(1,max_norm/(原范数+1e-6))求一个共同系数，在no_grad中原地乘到每份grad。',
        '返回裁剪前的Python范数，参数值本身不变。范数小于上限时不能放大梯度；max_norm=0应清成零，没有梯度时返回0。不要逐元素截断或分别归一化每个参数，也不调用现成clip_grad_norm_。'),
    'pt15': (
        '本题每批x和y是一维、逐样本对应。w从0开始，先统计所有批次的总样本数；每批计算sum((w*x-y)²)/总数再backward，中途不清w.grad。',
        '最终返回w.grad.item()。用3条和1条的不等批次检查权重；再把同一数据换一种拆批方式，梯度应一致。把每批mean简单除以批次数只适用于等大批次，不能替代本题整体mean。'),
    't4': (
        '定义继承nn.Module的TinyModel，在__init__先super().__init__()，再把nn.Linear(3,2)存成实例属性；forward只调用这个层。输入[B,3]映射为[B,2]，batch轴不变。',
        'weight形状[2,3]有6个数，bias形状[2]有2个数，共8个注册参数；batch大小改变不会改变参数数。检查单样本仍为[1,2]，调用model(x)的结果能参与求导；普通Tensor属性不等于Parameter。'),
    'pt16': (
        'make_mlp按传入维度组装Linear(in_dim,hidden)→ReLU→Linear(hidden,classes)，两层均含bias并注册在返回的nn.Module中。forward结果为原始logits，不在最后额外softmax。',
        '检查不同in_dim/hidden/classes以及batch=1的输出维。参数总数应为in_dim*hidden+hidden+hidden*classes+classes；分类交叉熵处理logits的稳定归一化，argmax或先softmax都会改变训练接口。'),
    'pt17': (
        'FeatureDataset先验证x与y的首维样本数一致，再分别clone保存。__len__返回样本数，__getitem__(i)返回本条特征与标签各自的clone；Dataset负责单条取样，DataLoader负责组批与打乱。',
        '长度不一致抛ValueError。构造后修改原x/y，以及修改取出的特征/标签，都不能污染内部数据；只保存引用或只在构造时clone仍不够。取单条样本与完整batch的shape也要区分。'),
    'pt18': (
        'collate_samples接收一组(等长一维特征,整数标签)。将特征用torch.stack新增batch轴，标签用torch.tensor(...,dtype=torch.long)汇成[B]；返回(特征[B,D],标签[B])。',
        '空样本列表抛ValueError。B=1时仍需[1,D]与[1]，不能随意squeeze；组批结果应有独立存储，修改batch不能影响输入特征。cat只拼已有轴，不会自动形成所需batch轴。'),
    'pt19': (
        '遍历model.backbone.parameters()把requires_grad设False，遍历model.head.parameters()把requires_grad设True，然后返回head参数的list供优化器使用；包含之前已冻结的head也必须重新启用。',
        '同时核对主体全部冻结、head全部可求导，以及返回的是原head参数而非Tensor副本。eval只改变Dropout等层行为，不自动冻结参数；优化器接收哪些参数也必须单独管理。'),
    'pt20': (
        '预测前保存was_training=model.training，再model.eval()，在with torch.no_grad()里调用model(x)。使用try/finally，使返回输出或前向抛错后都执行model.train(was_training)。',
        '用Dropout检查eval行为，用requires_grad输入检查前向是否真的关闭图记录，再分别验证原train和原eval能恢复。只有x.grad为None并不能证明没有建图；finally也要覆盖模型抛异常的路径。'),
    't5': (
        'update_weight(start)创建需要梯度的浮点标量w，交给SGD(lr=0.1)。按zero_grad→计算(w-3)²→backward→step执行一次；backward给出2(w-3)，step才按w-=0.1*grad修改参数。',
        '从0开始应更新到0.6，从5开始到4.6，已经在3则保持3。返回更新后的w.item()，不是更新前loss或梯度；若把此步骤放入循环，每次独立更新都要防止旧梯度意外累积。'),
    'pt21': (
        'epoch_mse保存原模式，eval+no_grad遍历(x,y)，累计所有预测误差的平方sum和y.numel()。最后总平方误差/总目标元素数，而不是先算每批mean再对批次平均。',
        '用尾批大小不同的数据检查加权；没有目标元素时返回Python 0.0。预测与y须按同一目标形状对应，避免广播扩大误差矩阵。成功和异常都在finally恢复原模式，不进行backward或参数更新。'),
    'pt22': (
        '以logits>=0判为正类，以labels==1作真实正类，利用布尔交集统计TP、FP、FN。转成Python计数后分别算precision=TP/(TP+FP)、recall=TP/(TP+FN)、F1=2TP/(2TP+FP+FN)。',
        '每个指标单独保护零分母并按本题返回0；空输入同样不产生NaN。检查logit恰为0时属于正类，以及没有预测正例、没有真实正例等情况；三种指标不能用accuracy代替。'),
    'pt23': (
        'evaluate_classifier在eval+no_grad下用logits[B,C]和long标签[B]求交叉熵sum，累计argmax(1)预测正确数和样本数；最终用总样本数分别平均loss与accuracy。',
        '空数据两项为Python 0；尾批大小不同时仍按每条样本同权聚合。不要先argmax再算交叉熵，不要在验证时反向或step；保存原模式并在finally恢复，前向期间确实要关闭梯度记录。'),
    'pt24': (
        'save_checkpoint用torch.save保存model.state_dict()、optimizer.state_dict()与epoch三个键。load_checkpoint按CPU和weights_only=True加载，分别恢复模型与优化器状态，再返回保存的epoch。',
        '保存后先改模型参数或优化器学习率，再加载检查恢复；动量等状态也属于优化器而非模型。返回的是保存轮数，不擅自加1。磁盘保存已写入快照；若只在内存缓存最佳state_dict，需要deepcopy隔离后续更新。'),
    'pt25': (
        'train_step先model.train()，再optimizer.zero_grad()，用原始分类logits与long标签计算交叉熵张量loss，接着backward和step。最后返回Python loss值供日志使用。',
        '预先放入旧梯度也应被清掉，原eval模型需切回train。可以另存metric=loss.item()用于日志，但不能用loss=loss.item()覆盖仍要反向的张量；item无需机械地等到backward后，关键是保留loss的图。'),
    't6': (
        '按题面创建一维x=[-2,-1,0,1,2]与同形y=2*x+1，w、b均为需要梯度的零标量。SGD学习率0.1，循环100次，每次清梯度、算mean((w*x+b-y)²)、backward再step。',
        '返回训练后的(w.item(),b.item())，应分别接近2和1，而不是只确认没报错。预测与目标必须同形，不能混用[N]和[N,1]造成[N,N]广播。代码里step前的loss与交互中更新后参数的当前loss属于相邻两组参数，要分清记录时点。'),
    'pt26': (
        '创建Linear(D,1).to(x)匹配特征dtype，权重与bias清零。每轮将输出squeeze(-1)成[B]，目标y转到x.dtype，直接用BCEWithLogitsLoss，按给定lr完成SGD；把每轮更新前的loss.item()存入列表。',
        '返回一维Python weight列表、数值bias和长度等于steps的losses。float32/float64输入都需匹配模型与标签；steps=0保留零参数及空曲线，lr=0不更新。单logit不先sigmoid，也不先argmax，检查损失确实下降。'),
    'pt27': (
        '用targets*C+preds编码每条配对，bincount(minlength=C*C)后reshape为[C,C]，行是真实类、列是预测类。TP取对角线，FP取列和减TP，FN取行和减TP。',
        '逐类F1=2TP/(2TP+FP+FN)，零分母记0，再对全部C类等权mean；未出现类也按约定占一个位置。空样本仍返回完整C×C零矩阵，结果矩阵转Python二维列表，不把macro改成按样本数加权。'),
    'pt28': (
        '把mask[B,T]用unsqueeze(-1)变为[B,T,1]，用masked_fill屏蔽无效特征，再沿dim=1求和得到[B,D]。分母用mask.sum(1,keepdim=True)得到[B,1]，clamp_min(1)后与分子广播相除。',
        '全无效句和T=0都返回[B,D]零向量，B=0仍保留特征维。有效位置保证有限，无效NaN/Inf必须用替换而非乘零排除；不修改输入，并让有效位置继续参与梯度。'),
    'pt29': (
        '先按q@k.transpose(-1,-2)/sqrt(D)形成[B,T,T]分数。创建diagonal=1的严格上三角bool mask，将未来key的分数填为-inf，再沿最后key轴softmax并乘v。',
        '当前token本身仍可见，不能连对角线也遮掉。改动未来value时，前面输出应完全不受影响；仅在softmax后把未来权重置0会破坏剩余权重归一化。本题手写实现，不直接调用现成因果注意力。'),
    'pt30': (
        '创建零初始化Linear(D,2)，只用train_x/train_y按给定epochs与lr完成SGD和交叉熵训练。训练后切eval，在no_grad下分别求训练损失、独立验证损失与验证accuracy，返回model和三个Python指标。',
        '返回model保持eval。验证数据不能参与反向、step或拼回训练；detach验证输入并不能阻止其标签影响模型参数。检查已知合成规则能学到，再在同一训练集下改动验证标签，确认训练后参数不随验证标签改变。'),
}

assert len(_TORCH_TEACHING) == 36
_torch_reviewed = []
for _lesson in LESSONS:
    if _lesson['runtime'] != 'torch':
        continue
    _operations, _boundaries = _TORCH_TEACHING[_lesson['id']]
    _first = dict(_lesson['teaching'][0])
    _lesson['teaching'] = [
        _first,
        {'title':'按本题接口写实现','body':_operations},
        {'title':'用本题的边界核对','body':_boundaries},
    ]
    _torch_reviewed.append(_lesson['id'])
assert len(_torch_reviewed) == 36

_torch_by_id = {lesson['id']:lesson for lesson in LESSONS if lesson['runtime']=='torch'}
_torch_by_id['pt06']['intro'] = '直接对大logits取exp可能溢出。每行先减去最大值不会改变softmax，因为分子分母的公共指数因子会抵消。中心化后的最大logit为0，其余不大于0，所以取exp后最大值为1。'
_torch_by_id['pt06']['teaching'][0]['body'] = _torch_by_id['pt06']['intro']
_torch_by_id['pt03']['hints'][0] = '先用x.masked_fill(~mask,0)替换无效位置，再逐行求和；分母是每行True的数量。不能用乘mask排除NaN/Inf。'
_torch_by_id['pt26']['hints'][1] = '完整batch训练steps轮，预测squeeze(-1)，目标转为x.dtype；每轮记录更新前loss.item()，再backward和step。'
_torch_by_id['pt08']['teaching'].insert(1, {
    'title':'最小先导：同一张计算图里的零',
    'body':'训练中的logits原本通过张量运算连接着模型参数。loss.backward()沿这条运算关系计算参数梯度；本节先知道这一点即可。logits.sum()*0虽然数值为0，仍保留到logits的连接；单独torch.tensor(0.)通常不需要梯度，也不连接logits，不能让梯度沿它回到模型。第9章会系统讲requires_grad、计算图和backward；这里先用“保留运算连接”的写法处理全部忽略的批次。',
})

_torch_by_id['t1']['examples'][0]['explanation'] = '输入是两条样本、每条两个特征。沿dim=1分别计算(1+3)/2与(2+6)/2，得到张量[2,4]，shape为[2]；dim=0则是另一种跨样本归约。'
_torch_by_id['t3']['examples'][0]['explanation'] = '本例只对y=x²求导：x=3时函数值为9、梯度为6。完整代码题用y=x²+3x，同在x=3时函数值为18、梯度为9；必须先确认正在求导的是哪一个函数。'
_torch_by_id['t4']['examples'][1]['title'] = '普通Tensor属性不是可训练参数'
_torch_by_id['t4']['examples'][1]['explanation'] = 'self.w只是普通Tensor，不会自动出现在parameters()里。保存nn.Linear等子模块会注册其Parameter；这里区分的是普通张量属性与可训练参数，并不是说Module没有其他注册机制。'
_torch_by_id['t6']['examples'][0]['explanation'] = '此例用[N,1]特征和同形标签演示形状检查。完整代码题使用一维x、y；两种表示都可描述数据，但不要混用[N]与[N,1]相减，否则会意外广播成[N,N]。'
