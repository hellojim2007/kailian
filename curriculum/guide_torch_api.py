"""PyTorch syntax notes paired with deterministic, real CPU examples."""
from guide_api import card, TORCH

card('tensor','创建 Tensor：数值、dtype 与 shape','import torch\nx = torch.tensor(data, dtype=torch.float32)\nx.shape; x.dtype; x.ndim',
 'Tensor 是带类型和维度的数组。整数列表默认推断为整数，mean 与可训练参数通常需要浮点张量。shape 的每项是对应轴的长度，ndim 是轴数，numel() 是总元素数。tolist() 转 Python 列表；item() 只适用于恰好一个元素的张量。device 是存储位置，本课程先在 CPU 学习。',
 'import torch\nx = torch.tensor([[1., 2., 3.], [4., 5., 6.]])\nprint(list(x.shape), x.ndim, x.numel())\nprint(x.dtype == torch.float32)\nprint(x[0].tolist())', '[2, 3] 2 6\nTrue\n[1.0, 2.0, 3.0]', 'https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html')
card('reduce','归约：sum、mean、dim、keepdim','x.mean(dim=1, keepdim=True)\nx.sum(dim=-1)',
 'dim 指要被归约掉的轴，不是要保留的轴。对 [B,D]，mean(1) 沿每行特征求均值，返回 [B]；mean(0) 返回 [D]。keepdim=True 把被归约的轴保留为长度 1，便于广播。dim=-1 表示最后一轴。没有 dim 则对所有元素归约成标量。',
 'import torch\nx = torch.tensor([[2., 6.], [4., 12.]])\nprint(x.mean(1).tolist())\nprint(x.mean(0).tolist())\nprint(list(x.mean(1, keepdim=True).shape))', '[4.0, 8.0]\n[3.0, 9.0]\n[2, 1]', TORCH+'generated/torch.mean.html')
card('reshape','展平、reshape 与非连续张量','x.flatten(start_dim=1)\nx.reshape(new_shape)\nx.transpose(dim0, dim1)',
 'flatten(1) 合并第 1 轴起的所有特征轴，保留 batch 轴。reshape 改变形状但保持逻辑元素顺序，必要时复制；view 对步长有更严格要求，不能假定转置后也能 view。转置交换轴，可能使存储非连续。空批次用 flatten(1) 可避免 reshape(0,-1) 的不明确推断。',
 'import torch\nx = torch.arange(12).reshape(2, 2, 3)\ny = x.transpose(1, 2)\nprint(list(y.shape), y.is_contiguous())\nprint(y.flatten(1).tolist())', '[2, 3, 2] False\n[[0, 3, 1, 4, 2, 5], [6, 9, 7, 10, 8, 11]]', TORCH+'generated/torch.flatten.html')
card('broadcast','广播：对齐尾轴，长度相同或为 1','x - row_mean\nx[:, None, :]\ny[None, :, :]',
 '广播从最右一轴开始对齐；每对长度相等或其中一侧为 1 才能匹配。缺少的前导轴视为 1。[B,D] 减 [B,1] 表示每行减一个均值；减 [B] 会把 B 对齐到 D，方阵时可能能运行却算错。None 或 unsqueeze 插入长度为 1 的轴，不是填入数值。',
 'import torch\nx = torch.tensor([[2., 4.], [10., 14.]])\nprint((x - x.mean(1)).tolist())\nprint((x - x.mean(1, keepdim=True)).tolist())\nprint(list(x[:, None, :].shape))', '[[-1.0, -8.0], [7.0, 2.0]]\n[[-1.0, 1.0], [-2.0, 2.0]]\n[2, 1, 2]', TORCH+'notes/broadcasting.html')
card('gather','按每行不同的列索引取值','rows = torch.arange(batch)\nscores = logits[rows, labels]\nlogits.gather(1, labels[:, None]).squeeze(1)',
 'logits[rows,labels] 把两个等长索引逐对匹配：第 i 行取 labels[i] 列，不是取一个矩形子表。labels 必须是合法整数索引，通常 dtype=torch.long。gather 的 index 与输入具有相同轴数，因此需先把 [B] 变成 [B,1]，随后 squeeze(1) 仅移除指定的单例轴。',
 'import torch\nx = torch.tensor([[1., 8., 3.], [9., 2., 4.]])\nlabels = torch.tensor([1, 0])\nrows = torch.arange(x.shape[0])\nprint(x[rows, labels].tolist())\nprint(x.gather(1, labels[:, None]).squeeze(1).tolist())', '[8.0, 9.0]\n[8.0, 9.0]', TORCH+'generated/torch.gather.html')
card('mask','bool mask、替换与安全分母','safe = x.masked_fill(~mask, 0)\ncounts = mask.sum(dim=1).clamp_min(1)',
 'mask 的 True 表示有效。~mask 取反；masked_fill 返回新张量，把选中位置替换成给定值。不要用 x*mask 屏蔽非有限值，因为 NaN*0 仍是 NaN。clamp_min(1) 将计数下限设为 1，使全无效行的 0/1 安全返回 0。mask 的来源是数据约定，不一定是 x!=0。',
 'import torch\nx = torch.tensor([[2., float("nan"), 6.], [9., 8., 7.]])\nmask = torch.tensor([[True, False, True], [False, False, False]])\nsafe = x.masked_fill(~mask, 0)\ncounts = mask.sum(1).clamp_min(1)\nprint((safe.sum(1) / counts).tolist())', '[4.0, 0.0]', TORCH+'generated/torch.Tensor.masked_fill.html')
card('pad','张量分配、切片赋值与 dtype','tokens = torch.zeros((batch, width), dtype=torch.long)\nmask = torch.zeros((batch, width), dtype=torch.bool)',
 'torch.zeros 先分配正确形状和类型；每行仅把原序列区间写入 tokens[i,:length]，再将同一区间 mask 设 True。原 token 为 0 时仍然有效。不要先创建浮点 tokens 再假定它能作类别索引；empty 批次、全空行的形状也应保持接口约定。',
 'import torch\ntokens = torch.zeros((2, 3), dtype=torch.long)\nmask = torch.zeros((2, 3), dtype=torch.bool)\ntokens[0, :2] = torch.tensor([0, 5])\nmask[0, :2] = True\nprint(tokens.tolist())\nprint(mask.tolist())', '[[0, 5, 0], [0, 0, 0]]\n[[True, True, False], [False, False, False]]', TORCH+'generated/torch.zeros.html')
card('grad','requires_grad、backward 与 .grad','x = torch.tensor(value, requires_grad=True)\ny = expression(x)\ny.backward()\nx.grad',
 '浮点叶子 x 开启 requires_grad 后，相关运算会建立计算图。标量 y.backward() 把 y 对叶子的导数累加到 .grad；不是返回一个梯度数值。调用前 x.grad 通常是 None。item() 只用于最终读数，不能提前替换还需要求导的 Tensor。非标量输出可先 sum 再反传。',
 'import torch\nx = torch.tensor(4., requires_grad=True)\nprint(x.grad)\ny = x * x + 2 * x\ny.backward()\nprint(y.item(), x.grad.item())', 'None\n24.0 10.0', 'https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html')
card('gradclear','累积、清空与重建计算图','x.grad = None\noptimizer.zero_grad()\nnew_loss = expression(x)',
 '不同 backward 的梯度会累加，适合有意进行 micro-batch 累积，却容易导致普通训练时误加历史梯度。设置 .grad=None 或优化器 zero_grad 都可清理相关状态。第一次 backward 后通常不能再次直接穿过同一张已释放的图；重新计算 loss 会建立新图。不要为普通训练随意添加 retain_graph=True。',
 'import torch\nx = torch.tensor(2., requires_grad=True)\n(x * 3).backward()\n(x * x).backward()\nprint(x.grad.item())\nx.grad = None\n(x * x).backward()\nprint(x.grad.item())', '7.0\n4.0', 'https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html')
card('detach','复制数据与保留计算图不是一回事','y = x.clone()\nz = x.detach()\n# avoid torch.tensor(existing_tensor) on a differentiable path',
 'clone 创建数据副本并保留与输入的求导关系；detach 断开梯度但通常共享存储。detach().clone() 同时断图和复制，适合数据快照。把已有张量重新 torch.tensor(...) 包装会产生新叶子，原路径断开。想返回梯度时要对原叶子读取 .grad，而不是对新包装的值求导后冒充结果。',
 'import torch\nx = torch.tensor([2., 3.], requires_grad=True)\ny = x.clone()\nz = x.detach()\nprint(y.requires_grad, z.requires_grad)\n(y * y).sum().backward()\nprint(x.grad.tolist())', 'True False\n[4.0, 6.0]', TORCH+'generated/torch.clone.html')
card('sgd','SGD 一步：清零、前向、反传、更新','optimizer.zero_grad()\nloss = ...\nloss.backward()\noptimizer.step()',
 'SGD 接收参数的可迭代对象和学习率 lr。backward 只计算梯度，不改参数；step 按 w -= lr*grad 更新。每轮应先清空上一轮梯度，再重新计算 loss。item 适合记录更新后的参数或损失。这里四步先按顺序写清楚，不必先封装复杂框架。',
 'import torch\nw = torch.tensor(1., requires_grad=True)\noptimizer = torch.optim.SGD([w], lr=0.1)\noptimizer.zero_grad()\nloss = (w - 4) ** 2\nloss.backward()\noptimizer.step()\nprint(round(w.item(), 3))', '1.6', 'https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html')
card('mse','前向、损失与训练循环','pred = w * x + b\nloss = ((pred - target) ** 2).mean()',
 '预测、目标必须具有相同含义与形状；[N,1] 与 [N] 相减可能广播成 [N,N]。平方误差先逐元素计算，再平均成标量 loss。w 和 b 必须都交给优化器；训练若干轮后再返回参数。检查损失趋势，不能只看循环是否运行。',
 'import torch\nx = torch.tensor([-1., 0., 1.])\ntarget = 3 * x + 2\nw = torch.tensor(0., requires_grad=True)\nb = torch.tensor(0., requires_grad=True)\nloss = ((w * x + b - target) ** 2).mean()\nloss.backward()\nprint(loss.item())\nprint(w.grad.item(), b.grad.item())', '10.0\n-4.0 -4.0', 'https://d2l.ai/chapter_linear-regression/linear-regression.html')
card('module','nn.Module、super 与 Linear','class Model(torch.nn.Module):\n    def __init__(self):\n        super().__init__()\n        self.linear = torch.nn.Linear(in_dim, out_dim)\n    def forward(self, x):\n        return self.linear(x)',
 '继承 Module 并先调用 super 初始化，再把层放在实例属性中，才能正确注册子模块。nn.Linear(D,C) 的权重形状是 [C,D]，可选 bias 为 [C]；输入 [...,D] 输出 [...,C]。使用 model(x) 调用，框架会进入 forward。普通 Tensor 属性不是自动注册的可训练 Parameter。',
 'import torch\nlayer = torch.nn.Linear(3, 2)\nprint(list(layer.weight.shape), list(layer.bias.shape))\nprint(list(layer(torch.ones(4, 3)).shape))\nprint(sum(p.numel() for p in layer.parameters()))', '[2, 3] [2]\n[4, 2]\n8', 'https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html')
card('sequential','Sequential、ReLU 与参数数','torch.nn.Sequential(\n    torch.nn.Linear(D, H),\n    torch.nn.ReLU(),\n    torch.nn.Linear(H, C))',
 'Sequential 按给定顺序传递张量。第一层把最后一维 D 变为 H，ReLU 把负值置 0，不改变形状且没有可训练参数；第二层 H 变 C。两层都带 bias 时，参数总数是 D*H+H+H*C+C。分类输出通常是原始 logits，不在模型末尾提前 softmax。',
 'import torch\nmodel = torch.nn.Sequential(torch.nn.Linear(2, 3), torch.nn.ReLU(), torch.nn.Linear(3, 2))\nprint(list(model(torch.ones(5, 2)).shape))\nprint(sum(p.numel() for p in model.parameters()))\nprint(torch.nn.ReLU()(torch.tensor([-2., 0., 3.])).tolist())', '[5, 2]\n17\n[0.0, 0.0, 3.0]', TORCH+'generated/torch.nn.Sequential.html')
card('dataset','Dataset 协议与独立存储','class Data(torch.utils.data.Dataset):\n    def __len__(self): ...\n    def __getitem__(self, i): ...',
 'Dataset 管一条样本的索引访问，DataLoader 管把样本组成批次。初始化时 clone 保护外部输入，取出时再 clone 保护内部数据；detach().clone() 适用于数据副本而不是模型中间计算。标签索引通常为 long。DataLoader(dataset,batch_size=...,shuffle=...) 返回可迭代批次，不要在 Dataset.__getitem__ 里自己组整批。',
 'import torch\nfrom torch.utils.data import TensorDataset, DataLoader\ndata = TensorDataset(torch.tensor([[1.], [2.], [3.]]), torch.tensor([0, 1, 0]))\nloader = DataLoader(data, batch_size=2, shuffle=False)\nfor x, y in loader:\n    print(list(x.shape), y.tolist())', '[2, 1] [0, 1]\n[1, 1] [0]', 'https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html')
card('stack','stack、cat 与 collate_fn','torch.stack(tensors, dim=0)\ntorch.tensor(labels, dtype=torch.long)',
 'stack 把相同形状的张量沿新轴叠成批次：[D] 的多条样本变为 [B,D]；cat 沿已有轴拼接，不会自动创建 batch 轴。collate_fn 接收一批样本组成的列表，不是一个索引；先分别收集特征和标签，再 stack 与构造标签张量。变长样本必须另定 padding 规则。',
 'import torch\nxs = [torch.tensor([1., 2.]), torch.tensor([3., 4.])]\nprint(torch.stack(xs).tolist())\nprint(list(torch.stack(xs).shape))\nprint(torch.cat(xs).tolist())', '[[1.0, 2.0], [3.0, 4.0]]\n[2, 2]\n[1.0, 2.0, 3.0, 4.0]', TORCH+'generated/torch.stack.html')
card('mode','train/eval 与 no_grad 各管什么','old_mode = model.training\nmodel.eval()\nwith torch.no_grad():\n    prediction = model(x)\nmodel.train(old_mode)',
 'eval 改变 Dropout、BatchNorm 等层的行为，不等于关闭求导。no_grad 关闭块内梯度记录，不等于切换 eval。对通用预测函数，应先记录原模式，用 try/finally 恢复，保证前向出错时也不污染后续训练。普通训练里不要把 loss 的计算放在 no_grad 中。',
 'import torch\nmodel = torch.nn.Linear(2, 1)\nold = model.training\nmodel.eval()\nwith torch.no_grad():\n    out = model(torch.ones(1, 2))\nprint(model.training, out.requires_grad)\nmodel.train(old)\nprint(model.training)', 'False False\nTrue', 'https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html')
card('classification','分类 logits、标签与交叉熵','loss = torch.nn.functional.cross_entropy(logits, labels, reduction="mean")\npred = logits.argmax(dim=1)',
 '多分类logits是[B,C]原始分数，labels是[B] long类别索引，不是浮点one-hot。cross_entropy内部包含稳定log-softmax，不先softmax。reduction="mean"默认返回批次均值标量，"sum"返回总和，"none"返回每条样本的损失[B]。argmax(1)取每行预测类。训练用Tensor loss反传，仅记录时item()转Python数值。',
 'import torch\nlogits = torch.tensor([[0., 0.], [0., 0.]])\nlabels = torch.tensor([0, 1])\nloss = torch.nn.functional.cross_entropy(logits, labels)\nprint(round(loss.item(), 6))\nprint(logits.argmax(1).tolist())', '0.693147\n[0, 0]', TORCH+'generated/torch.nn.CrossEntropyLoss.html')
card('binary','二分类 logits 与 BCEWithLogits','loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, targets)\npred = logits >= 0',
 '二分类可用单个logit：正数偏向正类，0对应概率0.5。BCEWithLogits接原始logit，内部含稳定sigmoid，目标是同形浮点0/1。Linear(D,1)输出[B,1]，squeeze(-1)得[B]；不裸squeeze以免删掉B=1的样本轴。模型.to(x)匹配输入x的device与浮点dtype；y.to(dtype=x.dtype)转换目标类型。两个logit的分类器则使用交叉熵，别混用接口。',
 'import torch\nlogits = torch.tensor([-2., 0., 2.])\nlabels = torch.tensor([0., 1., 1.])\nprint((logits >= 0).tolist())\nprint(round(torch.nn.functional.binary_cross_entropy_with_logits(logits, labels).item(), 6))', '[False, True, True]\n0.315668', TORCH+'generated/torch.nn.BCEWithLogitsLoss.html')
card('metrics','precision、recall、F1 与分母','precision = TP / (TP + FP)\nrecall = TP / (TP + FN)\nf1 = 2 * precision * recall / (precision + recall)',
 'TP 是预测正且真实正，FP 是预测正但真实负，FN 是预测负但真实正。先统计整数数量，再按约定处理零分母。混淆矩阵本课约定行为真实类别、列为预测类别；每类计算一次 F1 后平均是 macro F1，不等于先平均 precision/recall 再代入公式。',
 'tp, fp, fn = 3, 1, 2\np = tp / (tp + fp)\nr = tp / (tp + fn)\nf1 = 2 * p * r / (p + r)\nprint(round(p, 3), round(r, 3), round(f1, 3))', '0.75 0.6 0.667', 'https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall')
card('checkpoint','state_dict、保存与加载','torch.save({"model": model.state_dict(), ...}, path)\nmodel.load_state_dict(saved["model"])',
 'state_dict是命名参数和buffer的映射；优化器也有自己的状态。checkpoint同时记录epoch和两种状态。用torch.load(path,map_location="cpu",weights_only=True)读取本题状态文件，再分别load_state_dict恢复。内存中长期保存最佳参数时要deepcopy，不能把仍会变化的引用当快照。只加载自己信任的文件，本课程测试文件由本机生成。',
 'import torch\nimport copy\nmodel = torch.nn.Linear(2, 1)\nsaved = copy.deepcopy(model.state_dict())\nprint(sorted(saved))\nprint(list(saved["weight"].shape))', "['bias', 'weight']\n[1, 2]", 'https://docs.pytorch.org/tutorials/beginner/basics/saveloadrun_tutorial.html')
card('softmax','稳定 softmax 与 logsumexp','m = x.max(dim=-1, keepdim=True).values\ne = (x - m).exp()\nprob = e / e.sum(-1, keepdim=True)',
 '先减去最后一维最大 logit，再 exp：中心化最大 logit 是 0，对应最大指数是 1。概率与原 softmax 等价，同时避免大正数 exp 溢出。max(dim) 返回 values 和 indices，不能把整个返回对象参与减法。logsumexp = m + log(sum(exp(x-m)))，最后按接口移除归约轴；本课假设输入有限且最后一轴非空。',
 'import torch\nx = torch.tensor([[1000., 1000.], [-1000., -1000.]])\nm = x.max(-1, keepdim=True).values\ne = (x - m).exp()\np = e / e.sum(-1, keepdim=True)\nprint(p.tolist())\nprint(p.sum(-1).tolist())', '[[0.5, 0.5], [0.5, 0.5]]\n[1.0, 1.0]', 'https://d2l.ai/chapter_multilayer-perceptrons/numerical-stability-and-init.html')
card('maskedloss','先过滤，再索引；空时返回连图的零','valid = labels != ignore_index\nloss = logits.sum() * 0.0',
 'ignore_index 是跳过样本的标记，不是合法类别编号。先筛选有效行，再做类别索引。全部被忽略时，torch.tensor(0.) 是与输入断开的常量，可能无法反传；logits.sum()*0 保留图。不要对每个批次 loss 均值简单平均，应按有效样本数聚合。',
 'import torch\nx = torch.tensor([[1., 2.]], requires_grad=True)\nzero = x.sum() * 0.0\nzero.backward()\nprint(zero.item(), zero.requires_grad)\nprint(x.grad.tolist())', '0.0 True\n[[0.0, 0.0]]', TORCH+'generated/torch.nn.functional.cross_entropy.html')
card('norm','全局范数、缩放与 no_grad','norm = sqrt(sum(grad.square().sum() for grad in grads))\nscale = min(1, max_norm / norm)',
 '全局范数把所有参数梯度拼成一个长向量后求 L2 范数，不是逐参数各裁一次。先记录原范数，再统一缩放；小梯度不应放大。跳过 grad is None 的参数，原范数为零时避免除零。原地改梯度通常放在 no_grad 下执行；返回裁剪前的 Python 数值。',
 'import torch\ngrads = [torch.tensor([3.]), torch.tensor([4.])]\nnorm = torch.sqrt(sum((g * g).sum() for g in grads))\nscale = min(1.0, 2.0 / norm.item())\nprint(norm.item())\nprint([round((g * scale).item(), 3) for g in grads])', '5.0\n[1.2, 1.6]', TORCH+'generated/torch.nn.utils.clip_grad_norm_.html')
card('freeze','参数列表、冻结与训练范围','for p in model.backbone.parameters():\n    p.requires_grad_(False)',
 'parameters() 返回可迭代参数对象；requires_grad_(False) 原地关闭该参数的求导标记，True 则启用。冻结参数与 eval 改变层模式是不同操作。若任务要求返回 head 的全部参数，不能返回整个 model 参数列表，也不能返回参数的 clone；优化器要更新真实 Parameter。',
 'import torch\nmodel = torch.nn.Sequential(torch.nn.Linear(2, 3), torch.nn.Linear(3, 1))\nfor p in model[0].parameters():\n    p.requires_grad_(False)\nprint([p.requires_grad for p in model.parameters()])', '[False, False, True, True]', TORCH+'notes/autograd.html')
card('matmul','矩阵乘法、换轴与成对运算','scores = q @ k.transpose(-2, -1)\nheads = x.reshape(B, T, H, Dh).permute(0, 2, 1, 3)',
 '@ 是矩阵乘法，不是逐元素相乘 *；最后两个轴的内侧长度必须匹配，前面的 batch 轴可广播。permute 给出新轴的顺序，不改变各元素含义；reshape 只分拆/合并轴，不能代替换轴。拆 head 时先把 D 拆成 H 和 Dh，再把 H 换到 T 前，否则 token 与特征会错配。',
 'import torch\nq = torch.tensor([[[1., 0.], [0., 1.]]])\nk = torch.tensor([[[2., 3.], [4., 5.], [6., 7.]]])\nscores = q @ k.transpose(-2, -1)\nprint(list(scores.shape))\nprint(scores.tolist())', '[1, 2, 3]\n[[[2.0, 4.0, 6.0], [3.0, 5.0, 7.0]]]', TORCH+'generated/torch.matmul.html')
card('attention','缩放、沿 key 归一化与因果 mask','scores = (q @ k.transpose(-2,-1)) / sqrt(D)\nweights = softmax(scores, dim=-1)\noutput = weights @ v',
 '每个 query 对所有 key 给出权重，所以 softmax 沿最后的 key 轴，权重之和为 1。缩放用 query/key 的特征宽 D，不是 token 数。因果注意力把未来位置 j>i 的 score 替换为 -inf 后再 softmax；仅仅把分数设为 0 仍可能获得概率。先做单头，再拆多头，不在入门第一轮要求手写注意力。',
 'import torch\nscores = torch.zeros(1, 3, 3)\nfuture = torch.ones(3, 3, dtype=torch.bool).triu(1)\nweights = scores.masked_fill(future, float("-inf")).softmax(-1)\nprint(weights[0, 0].tolist())\nprint(weights[0, 1].tolist())', '[1.0, 0.0, 0.0]\n[0.5, 0.5, 0.0]', 'https://d2l.ai/chapter_attention-mechanisms-and-transformers/attention-scoring-functions.html')
