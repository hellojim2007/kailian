"""Self-contained stdout quizzes. Run the displayed code when auditing answers.

Every distractor is authored for the particular example, rather than inferred
from a hidden submission test. Example stdout is verified by the course audit.
"""
import io
import tokenize


# correct explanation, wrong stdout 1, explanation 1, wrong stdout 2, explanation 2
TRACE_CHOICES = {
    'p1': ('先算 70+5，再把 75 赋给 score；print 只输出更新后的值。', '70', '第二次赋值会覆盖原值，score 不再是 70。', '80', '这段代码的初值是 70，所以是 70+5；编程任务中的初值 75 属于另一段程序。'),
    'py01': ('split 分出 12 和 5，int 将它们变成整数，相加得 17。', '125', 'map(int, ...) 已把两段文本转换成整数，这里执行数值加法。', '12 5', 'print 的参数是 a+b，而不是分别打印 a 和 b。'),
    'py02': ('>= 包含等号，所以 60>=60 的结果是 True。', 'False', '只有 > 才排除相等；代码使用的是 >=。', '60', 'print 打印比较表达式的布尔结果，不是 score 本身。'),
    'p3': ('循环逐行输出 2、4、6；循环外的 print 再输出一次“完成”。', '2\n完成\n4\n完成\n6\n完成', '最后一个 print 没有缩进，不在循环体内。', '1\n2\n3\n完成', '循环打印 value*2，不是原始 value。'),
    'py03': ('range 不包含终点；起点与终点同为 1 时，没有任何元素。', '[1]', 'range 的右端点不包含，起点等于终点时范围为空。', '[0]', '这里显式把起点设为 1，并没有使用 range(1) 的写法。'),
    'py04': ('先输出 1；遇到 -1 时 break 结束整个循环，9 不再处理。', '1\n9', '这是把 break 当作 continue 了；break 会终止整个循环。', '1\n-1\n9', 'print 位于负数检查之后，负数不会被打印。'),
    'p2': ('索引 0 取到 60；更新的是中间元素，最后的 90 没有改变。', '60\n80', 'scores[1] 是第二个元素，而 scores[-1] 是第三个元素。', '75\n90', 'Python 从索引 0 开始，scores[0] 是 60。'),
    'py05': ('b=a 让两个名字指向同一个列表，所以 b.append 也能从 a 观察到。', '[1, 2]', 'b=a 没有创建副本；若要独立的外层列表可以用 a[:]。', '[1, 2, [3]]', 'append 的参数是整数 3，不是列表 [3]。'),
    'py06': ('显式按单个空格分隔时，两个连续空格之间保留一个空字符串。', "['a', 'b']", '默认 split() 会合并空白；这里传入了明确的分隔符 " "。', "['a  b']", '字符串中确实存在指定的空格分隔符，因此会发生分割。'),
    'py07': ('两个完整窗口依次是索引 0:2 和 1:3；切片包含左端、不含右端。', '[1, 3]\n[3, 5]\n[5]', 'range(len(xs)-1) 只生成 0、1，末尾不完整的窗口不会打印。', '[1]\n[3]', '切片 i:i+2 最多取两个元素，不是只取索引 i。'),
    'py08': ('集合里有 x 而没有 y，两个成员测试分别得到 True 和 False。', 'True True', 'in 检查指定值是否存在，不是只检查集合是否非空。', 'False True', '集合的唯一元素是 x，两个判断的真假顺序不能颠倒。'),
    'py09': ('这里只按序列长度创建两个 True；合法元素 0 也对应有效位置。', '[False, True]', 'mask 依据原始长度，而不是对每个数值做 bool 转换。', '[True]', 'len(seq) 是 2，所以列表乘法会重复 True 两次。'),
    'p4': ('函数返回 70+5=75，返回值赋给 result，再由 print 输出。', '70', '调用后执行了函数里的 +5，参数不会直接作为最终结果返回。', 'None', '函数明确使用 return 返回一个数，并非只在函数体里 print。'),
    'p6': ('三对预测与标签依次是相等、不相等、相等；每对各打印一行。', 'True\nTrue\nTrue', '第二对是 0 与 1，它们不相等。', 'True\nFalse', 'zip 的两边都长为 3，因此共有三轮迭代。'),
    'py10': ('第一次使用默认 a=2 得 6；第二次显式 a=0 覆盖默认值，结果为 0。', '6 6', '显式传入 0 是合法参数，不会被默认值 2 替换。', '3 0', '默认 a 是 2，第一次调用返回 3*2。'),
    'py11': ('两次 next 推进同一个生成器，依次得到 1、2，print 在一行输出。', '1 1', '生成器会记住暂停位置；第二次 next 从第二个 yield 继续。', '1\n2', '这里只有一次 print，两个参数默认用一个空格分隔。'),
    'py12': ('默认列表只创建一次；两次调用依次把 1、2 追加到同一列表。', '[1]\n[2]', '这种结果需要每次创建独立列表；代码中的默认列表被复用。', '[1, 2]\n[1, 2]', '第一次 print 立刻输出当时的 [1]，不会被后一次修改追溯改写。'),
    'py13': ('1.3 超出 [0,1]，所以生成器中至少一个条件为真，any 返回 True。', 'False', '0.2 合法并不能抵消 1.3 非法；any 只需一项为真。', '[False, True]', 'any 会把逐项判断汇总为一个布尔值，不返回布尔列表。'),
    'p5': ('loss 是 0.25，小于 0.5，因此执行分支并输出“达标”。', 'MLP', '条件检查 loss，分支里的 print 打印固定文本“达标”，没有打印 model。', '0.25', 'print 的参数不是 loss 数值，而是字符串“达标”。'),
    'py14': ('new 不在字典中，get 返回显式提供的默认值 0。', 'None', '只有没有提供默认值时，缺失键的 get 才返回 None。', '抛出 KeyError', 'get 为缺失键提供默认值，不同于直接用 d["new"] 索引。'),
    'py15': ('分子是按数量加权的总和 12，分母总数是 4，结果为 3.0。', '2.0', '简单平均 0 和 4 忽略两组样本数分别为 1 和 3。', '12.0', '12 是加权总和，还需要除以总样本数 4。'),
    'py16': ('元组先比较第一项，同为 2 时再按第二项排序，因此 a 在 b 前。', "[(1, 'z'), (2, 'b'), (2, 'a')]", '第一项相等时，Python 还会比较后续项，不会直接保留原来的 b、a 顺序。', "[(2, 'a'), (2, 'b'), (1, 'z')]", '元组先按第一项比较；不能先按字母把 z 排到最后。'),
    'py17': ('dict.copy 只复制外层字典，内层列表仍然共享，原字典可观察到追加的 2。', "{'x': [1]}", '浅复制没有复制嵌套列表；要隔离它应使用深复制。', "{'x': [2]}", 'append 是在已有列表末尾追加，不是替换原来的元素 1。'),
    'py18': ('NaN 与自身的相等比较以及与 0 的有序比较都为 False。', 'True False False', 'NaN 的特殊性质之一就是不等于自身。', 'False False True', 'NaN 既不小于 0，也不大于 0；它不是正无穷。'),
    'py19': ('float 无法解析该文本而抛出 ValueError，匹配的 except 输出“格式无效”。', 'nan', 'not-a-number 不是 float 所接受的特殊字符串 nan。', '抛出未捕获的 ValueError', '这段程序明确用 except ValueError 捕获并处理了转换异常。'),
    'py20': ('loads 把 JSON 文本解析成字典，再通过 epochs 键取到整数 3。', "{'epochs': 3}", '代码在解析后又索引了 epochs，打印的是该值而不是整个字典。', 'epochs', '方括号里的字符串是键名，用于查找值，并非最终打印内容。'),
    'py21': ('CSV 的引号保护内部逗号，所以第一列是 x,y，第二列为字符串 2。', "['x', 'y', '2']", 'csv.reader 遵守引号规则，不会把引号内部的逗号再分列。', "['x,y', 2]", 'csv.reader 默认返回文本字段，不会自动把数字文本转成整数。'),
    'py22': ('JSON 数组解析为 Python list，因此不是 dict。', 'True', 'JSON 也支持数组，不是所有合法 JSON 都会解析成字典。', '抛出 JSONDecodeError', '[1,2] 是合法 JSON 数组；这里不是语法错误。'),
    'py23': ('外层 x 有两行，y 有两个标签，所以长度比较为 True；这不代表行宽有效。', 'False', 'len(x) 只数外层行数，不会因为两行宽度不同而改变。', '抛出 ValueError', '普通列表允许不规则的内层列表；这段代码没有显式验证行宽或抛异常。'),
    'py24': ('列表长度是 2；浮点加法的机器表示使均值打印为 0.30000000000000004；最小值为 0.2。', '2 0.6 0.2', '0.6 接近总和，代码还除以长度 2 来计算均值。', '2 0.30000000000000004 0.4', 'min 返回最小值 0.2，0.4 是最大值。'),
    'py25': ('self.x 在每次构造实例时新建，修改 a.x 不影响 b.x。', '[1]', '这是把实例属性误当成所有实例共享的类属性了。', '[[], [1]]', 'b.x 是单个列表；构造其他实例不会自动向它插入元素。'),
    'py26': ('第一行把两个批次比例等权平均为 0.5；第二行按总样本数得到 0.75。', '0.75\n0.75', '第一行确实写的是按批次平均，它不会自动改成按样本数加权。', '0.5\n0.5', '第二行的分母是总样本数 4，正确数为 3，因此是 0.75。'),
    'py27': ('内置 len 调用实例的 __len__，该方法明确返回 2。', '0', 'len 采用类定义的协议返回值，不是统计实例当前有几个属性。', '抛出 TypeError', 'Tiny 已实现合法的 __len__ 方法，因此支持 len(Tiny())。'),
    'py28': ('0.4 比上一轮 0.5 小，却比历史最好 0.3 大，所以两个比较为 True、False。', 'True True', '改善上一轮并不代表超过历史最好值。', 'False True', '请分别对照两个比较右边的值：0.4<0.5 成立，0.4<0.3 不成立。'),
    'py29': ('乘法优先于加法：3*2+1=7，而括号使另一式先算 3+1，再乘 2 得 8。', '8 8', '第一个表达式没有括号，不能先计算 3+1。', '7 7', '第二个表达式有括号，先加 1 再乘 2，所以不同于第一个。'),
    'py30': ('a 在集合中、b 不在集合中，成员测试分别得到 True、False。', 'True True', '非空集合不代表包含所有值；b 不属于这个集合。', 'False True', '成员测试按实际元素判断，不会因集合无序而交换结果。'),
    't1': ('张量形状为 [2,2]；沿 dim=1 求均值得到每行的 2、4。', 'torch.Size([2, 2])\ntensor([1.5000, 4.5000])', '1.5、4.5 是沿 dim=0 求列均值的结果，代码归约的是 dim=1。', 'torch.Size([2, 2])\ntensor(3.)', '全局均值需要不指定 dim；这里保留每行一个均值。'),
    'pt01': ('从维度 1 开始展平保留 batch=2，并把 3*4 合并成 12。', '[24]', '只有全部 flatten 才会把 batch 也合并；flatten(1) 保留第 0 维。', '[2, 3, 4]', 'flatten(1) 会合并第 1 维及其后所有维度，形状不会保持三维。'),
    'pt02': ('两个索引张量逐项配对，取 x[0,2]=2 和 x[1,0]=3。', 'tensor([[2, 0],\n        [5, 3]])', '这是对每行选择相同两列的结果；两个高级索引会按位置配对。', 'tensor([0, 5])', '代码指定的列索引依次是 2、0，不是 0、2。'),
    'pt03': ('布尔值按 1、0、1 计数，沿 dim=1 求和得到长度为 1 的张量 [2]。', 'tensor([3])', 'False 不计入有效位置数，不能直接用这一行的总长度。', 'tensor([1, 0, 1])', '代码还执行了 sum(1)，已经将列维归约为一个计数。'),
    'pt04': ('torch.long 是 torch.int64 的别名，所以 dtype 打印为 torch.int64。', 'torch.float32', '这里显式指定 long，不使用浮点 dtype。', 'torch.bool', 'token 索引采用整数类型；布尔类型通常用于 mask。'),
    'pt05': ('None 在中间插入一个长度为 1 的新轴，[2,3] 变成 [2,1,3]。', '[1, 2, 3]', 'None 位于第二个索引位置，不是最前面。', '[2, 3, 1]', '这是在最后一轴之后插入新轴的形状，不是 x[:,None,:]。'),
    't2': ('每行各减去本行均值 2、4；keepdim=True 让均值沿列正确广播。', '[[-1.0, -1.0], [0.0, 2.0]]', '这是错误地移除 keepdim 后，长度为 2 的均值向列轴对齐的结果。', '[[-0.5, -1.5], [0.5, 1.5]]', '这是按列减均值；代码的 dim=1 指定按行归约。'),
    'pt06': ('默认 float32 无法表示 exp(1000) 的巨大有限值，结果溢出为 inf。', '1000.0', 'exp 不是恒等函数，数学值为 e 的 1000 次方。', '1.0', 'exp(0) 才是 1；只有先减去最大值等平移操作后才可能得到 0。'),
    'pt07': ('无参数 squeeze 删除两个长度为 1 的轴，得到标量形状 []；squeeze(-1) 只删最后一轴。', '[1] [1]', '无参数 squeeze 会删除所有长度为 1 的轴，并不只删除一个。', '[] []', '指定 -1 时只删除最后一轴，原来的第 0 维仍保留。'),
    'pt08': ('loss 与 x 的图仍相连；常数乘 0 的导数为 0，因此得到两个零梯度。', 'None', 'x 参与了可微运算并执行 backward，即使导数为零也会生成 grad。', 'tensor([1., 1.])', 'sum 的导数原本为 1，但后续乘 0 也必须计入链式法则。'),
    'pt09': ('转置交换轴与元素位置，reshape 按原有线性顺序重新分组，两份结果不同。', '[[0, 1], [2, 3], [4, 5]]\n[[0, 1], [2, 3], [4, 5]]', '第一行使用转置，不是 reshape；它把原来的列变成行。', '[[0, 3], [1, 4], [2, 5]]\n[[0, 3], [1, 4], [2, 5]]', 'reshape 只按已有元素顺序分组，不会自动执行转置的轴交换。'),
    'pt10': ('softmax 沿最后一轴将这一行归一化，随后对该轴求和得到 1。', 'tensor([6.])', '6 是原始得分的总和；softmax 已经把它们变成总和为 1 的概率。', 'tensor([3.])', '类别数为 3 不代表概率总和为 3；每行归一化后的总和是 1。'),
    't3': ('x² 在 x=3 处的导数是 2x=6，item 将梯度标量取为 Python 浮点数。', '9.0', '9 是函数值 y，不是梯度 dy/dx。', '3.0', '求导时幂次 2 会成为系数，不能直接把 x 当作梯度。'),
    'pt11': ('两个独立前向图分别贡献 3 和 4，未清空 grad 时相加得 7。', '4.0', '第二次 backward 不会自动覆盖旧梯度，默认采用累加。', '3.0', '第二次反向同样会贡献梯度 4，不能忽略它。'),
    'pt12': ('stack 保留计算图，sum 后是 x+2x，对 x 的导数为 3。', '6.0', '6 是 x=2 时 y 的函数值，不是导数。', '1.0', '两个分支都依赖 x，第二项 2x 的导数也要计入。'),
    'pt13': ('中心差分近似 x² 在 x=2 处的导数 4；浮点舍入使这次打印值略小于 4。', '2.0', 'x² 的导数是 2x，而不是 x；在 x=2 时应接近 4。', '0.0', 'x+e 与 x-e 是不同的浮点数，差商不会因为对称取点就变成 0。'),
    'pt14': ('计算平方和 9+16，再开平方，得到全局 L2 范数 5.0。', '7.0', '7 是绝对值之和，对应 L1 范数，不是代码中的平方和开根。', '25.0', '25 只是平方和，代码中的 **0.5 还会开平方。'),
    'pt15': ('两批各含 3、1 项，总数为 4，样本权重分别是 0.75 和 0.25。', '0.5 0.5', '两个批次的样本数不同，不能简单分成相同权重。', '3.0 1.0', '代码分别除以总样本数 4，输出比例而非原始计数。'),
    't4': ('Linear(3,2) 把每个样本的 3 维特征变成 2 维；输入 batch=1 保持不变。', '[3, 2]', '3 是输入特征数，并不是输入的样本数。', '[2, 1]', 'Linear 不会把 batch 轴与输出特征轴互换。'),
    'pt16': ('权重有 2*3=6 个，默认 bias 还有 2 个，因此参数总数是 8。', '6', 'nn.Linear 默认 bias=True，还需要把两个偏置参数算进去。', '5', '权重矩阵的元素数量是输入数乘输出数，不是把两者相加。'),
    'pt17': ('clone 创建独立存储，修改 b 不会改变 a，所以 a.item() 仍为 1.0。', '9.0', '只有共享存储时才会连带改变 a；clone 在这里创建了副本。', '[1.0]', 'item 取出单个 Python 标量，结果不是列表。'),
    'pt18': ('stack 即使只有一个输入，也会新增一个轴，把 [3] 变成 [1,3]。', '[3]', 'stack 新建轴，不会因为输入只有一个而省略 batch 轴。', '[3, 1]', '默认 dim=0，在最前面插入新轴，而不是最后面。'),
    'pt19': ('eval 调整层的训练/评估行为，不会修改参数 requires_grad，因此仍为 True。', 'False', '切换评估模式不会冻结参数；冻结需要单独关闭 requires_grad。', '抛出 AttributeError', 'Linear 确实有 weight 参数，参数支持 requires_grad 属性。'),
    'pt20': ('评估模式下 Dropout 是恒等映射，哪怕 p=1.0 也会原样返回输入。', 'tensor([0., 0.])', '全部置零发生在该层的训练模式；代码已调用 eval。', 'tensor([2., 2.])', '评估模式不会额外放大输入，而是直接保持原值。'),
    't5': ('loss=(w-3)² 在 w=0 的梯度为 -6，SGD 更新 w=0-0.1*(-6)=0.6。', '-0.6', '梯度为负，更新公式是减去梯度，所以参数会向正方向移动。', '0.0', 'backward 之后确实调用了 optimizer.step，参数已经更新。'),
    'pt21': ('按样本数加权的总误差是 3*1+1*9=12，除以 4 项得到 3.0。', '5.0', '5 是两个批次均值的简单平均，忽略了批次大小 3 与 1。', '12.0', '12 是误差总和，最终还要除以全部样本数 4。'),
    'pt22': ('p 和 y 同时为 True 的只有第一个位置，所以真阳性数量为 1。', '2', '2 是预测正例数；第二个预测正例的真实标签为 False。', '3', '& 是逐项逻辑与，不是统计任意一边为 True 的位置数。'),
    'pt23': ('argmax(1) 返回每行最大值的列索引：第一行是 1，第二行是 0。', 'tensor([3., 5.])', 'argmax 返回索引，不返回最大数值本身。', 'tensor([0, 1])', '第一行 3 在列 1，第二行 5 在列 0，注意索引从 0 开始。'),
    'pt24': ('Linear 的状态字典含 weight 和 bias，sorted 按键名排序后 bias 在前。', "['weight', 'bias']", '代码显式使用 sorted，键名按字母顺序排序。', "['bias', 'grad', 'weight']", '参数梯度不自动成为 state_dict 的独立状态项。'),
    'pt25': ('标量浮点张量的 item() 返回 Python float，因此类型名是 float。', 'Tensor', 'item 已经取出 Python 数值，结果不再是 torch.Tensor。', 'int', '张量由 2. 这个浮点字面量构造，取出的 Python 数值也是浮点类型。'),
    't6': ('逐行计算 y=2x+1 得 3、5、7，x 和 y 都保持三条样本、每条一个特征的 [3,1]。', '[[3.0], [5.0], [7.0]]\n[3, 1] [3]', '逐元素运算保持输入形状，y 不会自动移除最后的长度 1 维。', '[[2.0], [4.0], [6.0]]\n[3, 1] [3, 1]', '表达式还加了偏置 1，不能只计算 2*x。'),
    'pt26': ('sigmoid(0)=1/(1+exp(0))=1/2，输出 0.5。', '0.0', 'sigmoid 不是恒等函数；logit 为 0 对应概率 0.5。', '1.0', '有限的零输入对应中间概率，而不是饱和到 1。'),
    'pt27': ('逐项计算 0*3+2=2、1*3+0=3，得到配对的一维编码。', '[6, 1]', '乘数 3 作用在前一个张量，而不是后一个张量。', '[2, 1]', '第二对还有真实类编码 1*3，不能只把两个类别编号直接相加。'),
    'pt28': ('在末尾添加长度为 1 的轴，[2,3] 变成 [2,3,1]，便于沿特征轴广播。', '[1, 2, 3]', 'unsqueeze(-1) 把新轴放在最后，不是最前面。', '[2, 3]', 'unsqueeze 会增加维数，不会原样保留二维形状。'),
    'pt29': ('diagonal=1 保留严格上三角，所以主对角线及其下方均为 0。', 'tensor([[1., 1., 1.],\n        [0., 1., 1.],\n        [0., 0., 1.]])', '这是包含主对角线的上三角；代码传入 1，排除了主对角线。', 'tensor([[0., 0., 0.],\n        [1., 0., 0.],\n        [1., 1., 0.]])', 'triu 保留上三角，而不是下三角。'),
    'pt30': ('正数比较先得到 False、False、True、True，long 将它们转成整数 0、0、1、1。', 'tensor([False, False,  True,  True])', '比较后还调用了 long，最终输出是整数张量，不是布尔张量。', 'tensor([1, 1, 0, 0])', '条件是 x>0，只有后面的 1、2 满足，不能反转真假。'),
}


def without_comments(code):
    """Remove COMMENT tokens, preserving # characters within strings."""
    tokens = tokenize.generate_tokens(io.StringIO(code).readline)
    return tokenize.untokenize([
        token._replace(string='') if token.type == tokenize.COMMENT else token
        for token in tokens
    ]).strip() + '\n'


def trace_quiz(item):
    example = item['examples'][0]
    expected = example['output'].strip()
    correct_why, wrong1, why1, wrong2, why2 = TRACE_CHOICES[item['id']]
    options = [expected, wrong1, wrong2]
    why = [correct_why, why1, why2]
    assert expected and len(set(options)) == 3, (item['id'], options)
    offset = sum(map(ord, item['id'])) % len(options)
    return {
        'question': '在全新的 Python 进程中运行下面这段完整代码，标准输出是什么？（多行输出按原换行显示。）',
        'code': without_comments(example['code']),
        'options': options[offset:] + options[:offset],
        'answer': (-offset) % len(options),
        'why': why[offset:] + why[:offset],
        'expectedStdout': expected,
        'revision': 2,
    }


def audit_first_quiz(item):
    """Clarify concept prompts and retain a map from every old choice index.

    The fixed lesson ordering gives exactly 24 correct answers in each position.
    It does not depend on a user's progress or on the order this function runs.
    """
    original = item['quiz']
    q = dict(original, options=list(original['options']), why=list(original['why']))
    if item['id'] == 'pt05':
        q['question'] = '浮点张量 x 的形状为 [N,D]，y 的形状为 [M,D]。执行 x[:,None,:] - y[None,:,:] 后，差张量的形状是什么？'
        q['why'][0] = '对。x[:,None,:] 为 [N,1,D]，y[None,:,:] 为 [1,M,D]，广播后是 [N,M,D]。'
    elif item['id'] == 'pt25':
        q['question'] = '已有 loss 是可求导的标量张量。以下哪种写法既能记录 Python 数值，又保留随后反向传播所需的 loss？'
        q['options'] = [
            'loss = loss.item(); loss.backward()',
            'metric = loss.item(); loss.backward()',
            'metric = loss.detach(); metric.backward()',
        ]
        q['why'] = [
            'item 返回 Python 数值；把它重新赋给 loss 后，loss 不再有 backward 方法。',
            '对。metric 保存 Python 数值，原 loss 张量仍然保留计算图。记录 item 可以在反向之前或之后，关键是不要用它替换训练用的 loss。',
            'detach 返回脱离原计算图的张量，不能通过 metric.backward() 向原图反向传播。',
        ]
    elif item['id'] == 'py06':
        q['question'] = '需要按任意连续空白分词，并且不保留空词时，为什么适合 text.split()？'
    elif item['id'] == 'pt02':
        q['question'] = 'logits 是形状 [2,C] 的二维张量，labels 是包含两个合法列索引的 long 张量。logits[:, labels] 的结果形状是什么？'
    elif item['id'] == 't3':
        q['question'] = 'x 是值为 3 的浮点叶张量，requires_grad=True 且旧梯度为空。令 y=x²，执行 y.backward() 后，x.grad 是多少？'
    desired_answer = list(TRACE_CHOICES).index(item['id']) % 3
    count = len(q['options'])
    assert count == 3 and len(q['why']) == count
    shift = (q['answer'] - desired_answer) % count
    q['options'] = q['options'][shift:] + q['options'][:shift]
    q['why'] = q['why'][shift:] + q['why'][:shift]
    q['answer'] = desired_answer
    q['previousAnswerMap'] = [(index-shift) % count for index in range(count)]
    q['revision'] = 2
    return q
