"""Original practice curriculum; references are concept guides, not copied exercises."""
from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parents[1]
BASE = {x['id']: x for x in json.loads((ROOT / 'curriculum/original.json').read_text(encoding='utf-8'))}
SOURCES = {
 'cs50': ('Harvard CS50P', 'https://cs50.harvard.edu/python/'),
 'mooc': ('Helsinki Python MOOC', 'https://programming-26.mooc.fi/'),
 'py': ('Python 官方教程', 'https://docs.python.org/3/tutorial/index.html'),
 'flow': ('Python：控制流与函数', 'https://docs.python.org/3/tutorial/controlflow.html'),
 'data': ('Python：数据结构', 'https://docs.python.org/3/tutorial/datastructures.html'),
 'errors': ('Python：异常处理', 'https://docs.python.org/3/tutorial/errors.html'),
 'io': ('Python：输入、输出与文件', 'https://docs.python.org/3/tutorial/inputoutput.html'),
 'classes': ('Python：类与迭代器', 'https://docs.python.org/3/tutorial/classes.html'),
 'csv': ('Python：csv 标准库', 'https://docs.python.org/3/library/csv.html'),
 'json': ('Python：json 标准库', 'https://docs.python.org/3/library/json.html'),
 'torch': ('PyTorch：Learn the Basics', 'https://docs.pytorch.org/tutorials/beginner/basics/intro.html'),
 'tensor': ('PyTorch：Tensors', 'https://docs.pytorch.org/tutorials/beginner/basics/tensorqs_tutorial.html'),
 'grad': ('PyTorch：自动微分', 'https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html'),
 'dataset': ('PyTorch：Dataset 与 DataLoader', 'https://docs.pytorch.org/tutorials/beginner/basics/data_tutorial.html'),
 'model': ('PyTorch：构建神经网络', 'https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html'),
 'optim': ('PyTorch：优化训练循环', 'https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html'),
 'save': ('PyTorch：保存与加载模型', 'https://docs.pytorch.org/tutorials/beginner/basics/saveloadrun_tutorial.html'),
 'arena': ('ARENA：Fundamentals', 'https://learn.arena.education/chapter0_fundamentals/'),
}
CHAPTERS = [
 ('c01','起步与控制流','把输入、条件、循环写顺，建立独立写完整程序的习惯。',['cs50','flow']),
 ('c02','序列与字符串','从索引切片走到窗口、去重和序列补齐。',['data','mooc']),
 ('c03','函数与组合','练返回值、参数、生成器与可变对象语义。',['flow','mooc']),
 ('c04','字典与实验数据','分组、排序、配置合并与模型结果筛选。',['data','cs50']),
 ('c05','文件、异常与测试','真实读取 CSV / JSONL，验证边界并写可重复运行的报告。',['io','errors','csv','json']),
 ('c06','类与数据流水线','用类管理状态，组合小型评估器和实验数据流程。',['classes','mooc']),
 ('c07','张量形状与索引','批量维、布尔索引、gather、padding 和成对距离。',['tensor','arena']),
 ('c08','广播与数值稳定','避免维度碰巧对齐；实现稳定损失与注意力。',['tensor','arena']),
 ('c09','梯度与训练排错','检查梯度累积、计算图断开、数值求导和梯度裁剪。',['grad','arena']),
 ('c10','模型与数据加载','Module、参数注册、Dataset、collate 与评估模式。',['model','dataset']),
 ('c11','训练、评估与恢复','实现训练步骤、正确聚合指标、无梯度评估和 checkpoint。',['optim','save']),
 ('c12','综合实验与挑战','从线性回归到分类训练、指标分析与因果注意力。',['optim','arena']),
]
LESSONS = []

def clean(code):
    return textwrap.dedent(code).strip() + '\n'

def case(expr, expected=None, *, label='变式检查', setup=None, raises=None, tolerance=None):
    item = {'label':label,'expr':expr,'expected':expected}
    if setup: item['setup'] = clean(setup)
    if raises: item['raises'] = raises
    if tolerance is not None: item['tolerance'] = tolerance
    return item

def stdin(text, expected, label='输入输出检查'):
    return {'label':label,'stdin':text,'stdout':True,'expected':expected}

def quiz(question, options, answer, why):
    return {'question':question,'options':options,'answer':answer,'why':why}

def example(title, code, output, explanation):
    return {'title':title,'code':clean(code),'output':output,'explanation':explanation}

def add(id, chapter, title, level, kind, intro, code, notes, task, signature, solution, tests, q, *, examples=None, pitfalls=None, fixtures=None, bug=None, minutes=20):
    ch = CHAPTERS[chapter-1]
    item = dict(id=id, chapter=ch[0],group=ch[1],title=title,level=level,kind=kind,minutes=minutes,
                runtime='torch' if chapter>=7 else 'python',tag=signature.split('(')[0].replace('def ',''),intro=intro,
                example=clean(code),cpp='把已有的编程思路迁移过来；优先理解对象、输入输出约定和边界行为。',
                visual='tensor' if chapter in (7,8,10) else ('gradient' if chapter in (9,11,12) else 'list'),
                quiz=q,task=task,signature=signature,tests=tests,solution=clean(solution),
                hints=[notes[0],notes[1],notes[2]],
                teaching=[{'title':'为什么要学','body':intro},{'title':'把过程拆开','body':notes[0]+' '+notes[1]},{'title':'边界与检查','body':notes[2]}],
                examples=examples or [], pitfalls=pitfalls or [],
                resources=[{'title':SOURCES[k][0],'url':SOURCES[k][1]} for k in ch[3]],
                success='这一关已通过。回想哪些边界让你修改了实现，再尝试不看参考重写。')
    if fixtures: item['fixtures']=fixtures
    if bug: item['bug']=clean(bug)
    LESSONS.append(item)
    return item

def existing(id, chapter, level=1, minutes=15):
    item=BASE[id].copy(); ch=CHAPTERS[chapter-1]
    item.update(chapter=ch[0],group=ch[1],level=level,kind='实现',minutes=minutes,
                resources=[{'title':SOURCES[k][0],'url':SOURCES[k][1]} for k in ch[3]])
    item['teaching']=[{'title':'核心模型','body':item['intro']},{'title':'逐步写出来','body':'先写出输入、输出与变量的含义，再把操作逐句翻译成代码。'+item['cpp']},{'title':'检查与迁移','body':'运行示例验证直觉，再提交测试。通过后换一个输入，解释哪里会变化、哪里保持不变。'}]
    item['examples']=[example('跟踪已有例子',item['example'],'见代码旁注','先按行预测结果，再用「运行示例」验证。注意变量赋值或张量形状如何改变。')]
    item['pitfalls']=['不要把“没有报错”当成结果正确。按照题目的返回值、类型与边界逐项检查。']
    LESSONS.append(item);return item

existing('p1',1,minutes=10)
add('py01',1,'输入不是数值',1,'实现',
 'input() 读到的一律是字符串。要做数值运算，先显式转换；split() 按任意连续空白分开输入，map(int, ...) 把每段转成整数。',
 'text = "  8  3 "\na, b = map(int, text.split())\nprint(a // b, a % b)',
 ['先用 input().split() 得到两段文本，再转为整数。','/ 是浮点除法；// 是向下取整的整除；% 是余数。负数的 // 也向负无穷取整。','输出三个数：和、整除结果、余数。输入保证第二个数非零；不要给 input 写提示词。'],
 '读取一行两个整数 a、b，b 非零。输出 a+b、a//b、a%b，用空格隔开。','完整程序 · input / int / print',
 'a, b = map(int, input().split())\nprint(a+b, a//b, a%b)',
 [stdin('8 3\n','11 2 2','正整数'),stdin('-7 3\n','-4 -3 2','负数整除'),stdin('0 5\n','5 0 0','零与空白'),stdin(' 12   4\n','16 3 0','连续空白')],
 quiz('input() 读入 12 后，直接与整数 3 相加会怎样？',['得到 15','得到 "123"','抛出 TypeError'],2,['必须先转成数值。','字符串拼接也要求两边都是字符串。','对，字符串与整数不能直接相加。']),
 examples=[example('空白与类型','a,b = map(int, " 12  5 ".split())\nprint(a+b)','17','split 自动忽略连续空白；转换后加法才是数值加法。'),example('负数整除','print(-7 // 3, -7 % 3)','-3 2','商向下取整，且 a == (a//b)*b + a%b。')])
add('py02',1,'条件要覆盖边界',1,'实现',
 'if / elif / else 按顺序选择第一个满足条件的分支。把区间边界写清楚，比堆叠条件更重要。比较使用 >=、<、==，赋值使用单个 =。',
 'value = 0\nif value > 0:\n    print("positive")\nelif value == 0:\n    print("zero")\nelse:\n    print("negative")',
 ['先处理不在 0 到 100 范围内的非法输入。','有效分数先判断 >=90，再判断 >=60，最后落入 F。每个分支只输出一个标签。','必须检查 59、60、89、90 这些阈值；区间的等号决定结果。'],
 '读入一个整数分数。若小于 0 或大于 100，输出 INVALID；90–100 输出 A；60–89 输出 P；0–59 输出 F。','完整程序 · if / elif / else',
 '''score = int(input())
if score < 0 or score > 100:
    print('INVALID')
elif score >= 90:
    print('A')
elif score >= 60:
    print('P')
else:
    print('F')''',
 [stdin('90','A','A 的边界'),stdin('89','P','P 的上界'),stdin('60','P','P 的下界'),stdin('59','F','不及格边界'),stdin('-1','INVALID','负数非法'),stdin('101','INVALID','超上限')],
 quiz('把 >=90 的判断放在 >=60 后的 elif 中，会有什么问题？',['90 分先命中 >=60，得不到 A','没有区别','只有 100 分受影响'],0,['对，命中一个分支后不再检查后面的 elif。','分支顺序决定先匹配哪个范围。','所有 >=90 的合法分数都会受影响。']),
 examples=[example('边界刚好相等','score=60\nprint(score >= 60)','True','>= 包含 60。测试不能只挑范围中间的 75。'),example('组合非法条件','score=-1\nprint(score < 0 or score > 100)','True','or 只要求有一边成立。')])
existing('p3',1,minutes=12)
add('py03',1,'range 的终点在哪里',1,'实现',
 'range(start, stop, step) 不包含 stop。循环可以同时筛选与累加；先为累计变量设初值，再逐项更新。空范围不会执行循环体。',
 'total = 0\nfor n in range(1, 5):\n    total += n\nprint(total)  # 10',
 ['读入整数 n，创建 total=0。','range(1, n+1) 才能包含 n；只把偶数加到 total。','n=0 时答案是 0。检查 2 是否计入，不要错写成不包含 n 的范围。'],
 '读入整数 n（0≤n≤10000），输出从 1 到 n（含 n）的所有偶数之和。','完整程序 · range 与累计',
 'n=int(input())\ntotal=0\nfor value in range(1,n+1):\n    if value%2 == 0:\n        total += value\nprint(total)',
 [stdin('0','0','空范围'),stdin('1','0','没有偶数'),stdin('2','2','包含终点'),stdin('8','20','多个偶数'),stdin('100','2550','较长范围')],
 quiz('list(range(2, 7, 2)) 的结果是什么？',['[2,4,6]','[2,4,6,7]','[2,3,4,5,6]'],0,['对，步长为 2，终点 7 不包含。','range 不会额外加上终点。','这对应步长 1。']),
 examples=[example('空范围','print(list(range(1,1)))','[]','起点等于终点时，没有元素。'),example('倒序','print(list(range(5,0,-2)))','[5, 3, 1]','负步长也不包含终点。')])
add('py04',1,'while 也需要退出条件',2,'排错',
 'while 会反复检查条件。循环体必须让状态向终止条件靠近。遇到满足条件的第一条记录时可以 break，但累计值仍然需要处理空输入的语义。',
 'n=3\nwhile n>0:\n    print(n)\n    n -= 1',
 ['输入是一行整数，用 split 与 int 解析。','从左到右累加，遇到第一个负数立即停止；负数本身不计入。','不要用 return 结束顶层程序；可以用 break，或者下标加 while。没有负数时应统计全部。'],
 '读取一行整数，输出第一个负数出现之前的所有数之和。若第一项为负数或输入为空，输出 0。','完整程序 · break 与循环状态',
 'values=list(map(int,input().split()))\ntotal=0\nfor x in values:\n    if x<0:\n        break\n    total += x\nprint(total)',
 [stdin('1 2 -1 100','3','停止后不再累计'),stdin('-2 5','0','第一项就停止'),stdin('0 4 6','10','没有负数'),stdin('\n','0','空输入')],
 quiz('while n > 0 的循环里忘记更新 n，可能发生什么？',['自动减到 0','一直循环，直到被停止','Python 自动报语法错误'],1,['Python 不会替你修改变量。','对，条件可能永远保持为真。','逻辑错误通常可以通过语法检查。']),
 bug='n=3\nwhile n>0:\n    print(n)',examples=[example('break 的作用','for x in [1,-1,9]:\n    if x<0:\n        break\n    print(x)','1','break 退出整个当前循环，而不是只跳过当前项。'),example('continue 的区别','for x in [1,-1,9]:\n    if x<0:\n        continue\n    print(x)','1\n9','continue 只跳过当前项，其后的元素仍然访问。')])

existing('p2',2,minutes=10)
add('py05',2,'切片与独立副本',1,'实现',
 '切片 xs[start:stop] 包含 start，不包含 stop。xs[:] 复制外层列表；把新名字直接赋给旧列表只产生别名。返回新列表时要防止意外修改输入。',
 'a=[1,2,3]\nb=a[:]\nb[0]=9\nprint(a)  # [1,2,3]',
 ['长度 n 不为负，xs[:n] 自动处理 n 超过列表长度的情况。','先得到切片，再返回它；n=0 得到空列表。','评测会修改返回值，检查原列表是否还保持不变。浅复制对嵌套对象不保证完全独立。'],
 '定义 take_first(xs,n)，返回前 n 项的新列表，n≥0。不可修改输入；返回列表自身必须与输入独立。','def take_first(xs, n)',
 'def take_first(xs,n):\n    return xs[:n]',
 [case('take_first([1,2,3],2)',[1,2],label='正常切片'),case('take_first([1,2],9)',[1,2],label='超过长度'),case('take_first([1],0)',[],label='零项'),case('xs', [1,2,3],setup='xs=[1,2,3]\nout=take_first(xs,3)\nout.append(9)',label='不能返回输入别名')],
 quiz('b=a 与 b=a[:] 的关键区别是什么？',['两者都深复制','前者共享列表，后者新建外层列表','后者修改会直接改变前者长度'],1,['切片不是深复制。','对，外层容器的身份不同。','新建外层列表后 append 不影响原列表长度。']),
 examples=[example('别名','a=[1,2]\nb=a\nb.append(3)\nprint(a)','[1, 2, 3]','a 与 b 指向同一个列表。'),example('切片的右界','print([10,20,30,40][1:3])','[20, 30]','索引 3 的元素不包含。')])
add('py06',2,'清洗文本与词频输入',1,'实现',
 'strip() 清除两端空白，lower() 统一大小写，split() 按连续空白拆词。字符串不可变，调用方法得到新字符串。清洗顺序应符合明确的数据约定。',
 'text="  PyTorch  IS fun "\nprint(text.lower().split())',
 ['只按空白拆分，不需要去掉标点；先 lower 再 split 就够了。','返回字符串列表，空白文本应返回空列表。','不要使用 split(" ")：它会在连续空格处产生空词，且不覆盖制表符。'],
 '定义 tokenize(text)，按任意空白分词并转成小写。保留标点，不修改其他字符。','def tokenize(text)',
 'def tokenize(text):\n    return text.lower().split()',
 [case('tokenize("  AI   Lab\\tPYTHON ")',['ai','lab','python'],label='空格与制表符'),case('tokenize("\\n \\t")',[],label='全空白'),case('tokenize("Hello, WORLD!")',['hello,','world!'],label='保留标点'),case('tokenize("模型 Python")',['模型','python'],label='Unicode')],
 quiz('为什么此处更适合 text.split()？',['它自动小写','它把连续空白当作分隔，不产生空词','它会删除标点'],1,['小写由 lower 完成。','对，默认 split 处理空白序列。','默认 split 不处理标点。']),
 examples=[example('指定空格的陷阱','print("a  b".split(" "))','[\'a\', \'\', \'b\']','两个空格之间出现空字符串。'),example('默认分隔','print(" A\\tb\\nC ".lower().split())',"['a', 'b', 'c']",'连续空白会被统一处理。')])
add('py07',2,'滑动窗口均值',2,'实现',
 '窗口是序列中的连续片段。长度 n、窗口 k 的完整窗口共有 n-k+1 个。窗口均值可以先切片求和，进一步可维护滑动总和，将复杂度从 O(nk) 降到 O(n)。',
 'xs=[2,4,6,8]\nprint(xs[0:2], xs[1:3])',
 ['k 必须为正，否则 raise ValueError。k 大于长度时没有完整窗口，返回 []。','简单实现逐个取 xs[i:i+k]；进阶实现减去离开的值、加上新进入的值。','输出长度为 max(0,len(xs)-k+1)，不要丢掉最后一个窗口。'],
 '定义 moving_average(xs,k)，返回每个完整连续 k 项窗口的平均值。k≤0 抛出 ValueError；k>len(xs) 返回空列表，不修改输入。','def moving_average(xs, k)',
 '''def moving_average(xs,k):
    if k<=0:
        raise ValueError('k must be positive')
    if k>len(xs):
        return []
    total=sum(xs[:k])
    result=[total/k]
    for i in range(k,len(xs)):
        total += xs[i]-xs[i-k]
        result.append(total/k)
    return result''',
 [case('moving_average([2,4,6,8],2)',[3,5,7],label='多个窗口'),case('moving_average([7],1)',[7],label='单项窗口'),case('moving_average([1,2],3)',[],label='窗口过大'),case('moving_average([],2)',[],label='空序列'),case('moving_average([1],0)',raises='ValueError',label='非法窗口'),case('xs',[1,2,3],setup='xs=[1,2,3]\nmoving_average(xs,2)',label='输入不变')],
 quiz('长度 5 的序列使用大小 3 的完整窗口，有多少个？',['2','3','5'],1,['第一个窗口从索引 0 开始，最后一个从 2 开始。','对，5-3+1=3。','不是每个起点都能容纳一个完整窗口。']),
 examples=[example('观察窗口','xs=[1,3,5]\nfor i in range(len(xs)-1):\n    print(xs[i:i+2])','[1, 3]\n[3, 5]','相邻窗口共享一个元素。'),example('滑动总和','total=1+3\ntotal=total-1+5\nprint(total/2)','4.0','减去离开窗口的 1，加上进入的 5。')],minutes=25)
add('py08',2,'去重但保留顺序',2,'实现',
 'set 支持快速成员判断，但不代表业务所需的输出顺序。想按首次出现顺序去重，需要一个集合负责“见过没有”，一个列表负责保留输出顺序。',
 'seen=set()\nresult=[]\nfor name in ["b","a","b"]:\n    if name not in seen:\n        seen.add(name)\n        result.append(name)\nprint(result)',
 ['创建空 seen 与 result，按输入顺序遍历。','只在元素还没有见过时 append，再加入 seen。','不要 sorted(set(xs))，它会改变顺序。输入元素保证可哈希。'],
 '定义 unique_stable(xs)，保留每个元素的首次出现，返回新列表。输入元素可哈希，不能修改 xs。','def unique_stable(xs)',
 'def unique_stable(xs):\n    seen=set()\n    out=[]\n    for x in xs:\n        if x not in seen:\n            seen.add(x)\n            out.append(x)\n    return out',
 [case('unique_stable([3,1,3,2,1])',[3,1,2],label='保持首次顺序'),case('unique_stable([])',[],label='空序列'),case('unique_stable(["b","a","b"])',['b','a'],label='字符串'),case('unique_stable([2,2,2])',[2],label='全部重复'),case('xs',[3,1,3],setup='xs=[3,1,3]\nunique_stable(xs)',label='不修改输入')],
 quiz('sorted(set([3,1,3,2])) 为什么不符合“首次出现顺序”？',['没有去重','结果变成 [1,2,3]','会抛出异常'],1,['它能去重。','对，排序破坏了原顺序。','整数集合可以正常排序。']),
 examples=[example('集合只负责检查','seen={"x"}\nprint("x" in seen, "y" in seen)','True False','成员判断是集合的职责。'),example('输出顺序由列表负责','out=[]\nout.append("z")\nout.append("a")\nprint(out)',"['z', 'a']",'append 按追加次序保存。')])
add('py09',2,'把变长序列排成批次',3,'挑战',
 '一批序列长度不同，常先补成同样长度，并额外记录有效位置。padding 值本身可能也是合法数据，因此 mask 必须依据原长度构造，不能靠数值是否为零推断。',
 'seq=[4,0]\nwidth=4\npadded=seq+[0]*(width-len(seq))\nmask=[True]*len(seq)+[False]*(width-len(seq))\nprint(padded,mask)',
 ['先计算最大长度，批次为空时最大长度设为 0。','每条序列补零到最大长度；mask 对原元素为 True，补齐位置为 False。','不要用 [[0]*width]*batch 来创建独立行。合法 token 也可能是 0。'],
 '定义 pad_batch(sequences)，返回 (padded,mask)，两者是二维列表。右侧补 0，mask 为布尔值；空批次返回 ([],[])，全空序列保留对应的空行，不修改输入。','def pad_batch(sequences)',
 '''def pad_batch(sequences):
    width=max((len(s) for s in sequences),default=0)
    padded=[]
    masks=[]
    for s in sequences:
        missing=width-len(s)
        padded.append(list(s)+[0]*missing)
        masks.append([True]*len(s)+[False]*missing)
    return padded,masks''',
 [case('pad_batch([[4,0],[2]])',[[[4,0],[2,0]],[[True,True],[True,False]]],label='有效零值'),case('pad_batch([])',[[],[]],label='空批次'),case('pad_batch([[],[]])',[[[],[]],[[],[]]],label='全空行'),case('pad_batch([[],[1,2]])',[[[0,0],[1,2]],[[False,False],[True,True]]],label='空序列混合'),case('seqs',[[1],[2,3]],setup='seqs=[[1],[2,3]]\na,b=pad_batch(seqs)\na[0][0]=99',label='不能修改原序列')],
 quiz('为什么不能用 padded[i][j] != 0 来生成 mask？',['因为布尔值不能组成列表','原始序列里也可能含合法的 0','因为所有序列长度都相等'],1,['布尔值可以放进列表。','对，mask 应由长度而不是数值决定。','变长才是需要补齐的原因。']),
 examples=[example('合法的零','seq=[0,5]\nprint([True]*len(seq))','[True, True]','两个元素都来自原序列，即使其中一个为 0。'),example('共享行的陷阱','rows=[[0]*2]*2\nrows[0][0]=9\nprint(rows)','[[9, 0], [9, 0]]','乘法复制的是行引用；创建独立行应在循环中分别构造。')],minutes=30)

existing('p4',3,minutes=15)
existing('p6',3,2,20)
add('py10',3,'让默认参数可控',1,'实现',
 '默认参数让常见调用更简洁；关键字调用让含义更明确。None 是没有给定值的标记，不能简单用真假判断替代，因为 0 和空列表也可能是合法输入。',
 'def shift(x, amount=1):\n    return x+amount\nprint(shift(3),shift(3,amount=0))',
 ['定义 scale(values,factor=1,bias=0)，逐项计算 x*factor+bias。','参数名必须支持 factor= 与 bias= 这样的关键字调用。','factor=0 是合法值；返回新列表，并允许空输入。'],
 '定义 scale(values,factor=1,bias=0)，返回逐元素线性变换后的新列表，不修改输入。','def scale(values, factor=1, bias=0)',
 'def scale(values,factor=1,bias=0):\n    return [x*factor+bias for x in values]',
 [case('scale([1,2])',[1,2],label='默认参数'),case('scale([1,2],bias=3,factor=2)',[5,7],label='关键字顺序'),case('scale([8,9],factor=0,bias=2)',[2,2],label='合法的零'),case('scale([])',[],label='空列表'),case('xs',[1,2],setup='xs=[1,2]\nscale(xs,2)',label='原列表不变')],
 quiz('调用 scale([1], factor=0) 时，factor 应该是什么？',['默认值 1','0','None'],1,['显式传入会覆盖默认值。','对，0 也是有效的参数。','没有传 None。']),
 examples=[example('默认与覆盖','def f(x,a=2):\n    return x*a\nprint(f(3),f(3,a=0))','6 0','默认值仅在对应参数没有传入时使用。'),example('None 与零','print(0 is None, bool(0))','False False','零的真假值是假，但它并不是 None。')])
add('py11',3,'按需产出小批次',2,'实现',
 'yield 让函数变成生成器：每次迭代才产出一个值，函数可以从暂停处继续。与一次返回所有批次相比，这种接口适合连接后续数据流水线。',
 'def countdown(n):\n    while n>0:\n        yield n\n        n-=1\nprint(list(countdown(3)))',
 ['batch_size 必须为正，否则抛 ValueError。','用 range(0,len(xs),batch_size) 遍历各批次起点，yield xs[i:i+batch_size]。','最后一个不完整批次保留。生成器函数内的错误通常在开始迭代时才触发。'],
 '定义 batches(xs,batch_size)，返回生成器，依次产出连续小批次的新列表，保留最后不足一批的数据。batch_size≤0 时在迭代时抛 ValueError。','def batches(xs, batch_size) · 使用 yield',
 'def batches(xs,batch_size):\n    if batch_size<=0:\n        raise ValueError("positive batch size required")\n    for i in range(0,len(xs),batch_size):\n        yield list(xs[i:i+batch_size])',
 [case('list(batches([1,2,3,4,5],2))',[[1,2],[3,4],[5]],label='保留尾批'),case('list(batches([],3))',[],label='空数据'),case('list(batches([1,2],9))',[[1,2]],label='一小批'),case('iter(g) is g',True,setup='g=batches([1,2],1)',label='真正的迭代器'),case('list(batches([1],0))',raises='ValueError',label='非法大小')],
 quiz('调用生成器函数之后，还没有开始迭代时，通常发生什么？',['立即返回所有批次列表','返回一个生成器对象','自动启动新线程'],1,['生成器按需产出。','对，函数体在迭代时推进。','yield 不等于并发。']),
 examples=[example('暂停与继续','def g():\n    yield 1\n    yield 2\nx=g()\nprint(next(x),next(x))','1 2','每次 next 推进到下一个 yield。'),example('尾批边界','xs=[1,2,3,4,5]\nprint(xs[4:6])','[5]','切片超过右界不会报错。')],minutes=25)
add('py12',3,'修复悄悄共享的历史',2,'排错',
 '默认参数在函数定义时求值一次。把列表作为默认参数，会让不同调用共享同一个容器。通常用 None 作为默认值，在函数内部为新调用创建列表。',
 'def append_safe(value, history=None):\n    if history is None:\n        history=[]\n    history.append(value)\n    return history',
 ['将默认参数设为 history=None。','只有 history is None 时新建列表；调用者显式传入列表时，应继续向那个列表追加。','不要写 if not history：调用者传入的空列表也应该被原地追加。'],
 '修复 remember(value,history=[]) 的共享默认值问题。无 history 时每次返回独立列表；显式传入列表时向该列表原地追加并返回它。','def remember(value, history=None)',
 'def remember(value,history=None):\n    if history is None:\n        history=[]\n    history.append(value)\n    return history',
 [case('remember(1)',[1],label='首次调用'),case('remember(2)',[2],label='第二次不能共享'),case('history',[3],setup='history=[]\nout=remember(3,history)',label='显式空列表应被更新'),case('out is history',True,setup='history=[5]\nout=remember(6,history)',label='保留容器身份'),case('remember(4,[1,2])',[1,2,4],label='已有历史')],
 quiz('为什么 if not history 不能替代 if history is None？',['空列表也是 False，但它可能由调用者提供','None 的真假值是 True','列表不能参与 if'],0,['对，空列表和未传入是不同情形。','None 的真假值是 False。','列表可以按空与非空判断真假。']),
 bug='def remember(value,history=[]):\n    history.append(value)\n    return history',examples=[example('共享默认参数','def f(x,seen=[]):\n    seen.append(x)\n    return seen\nprint(f(1))\nprint(f(2))','[1]\n[1, 2]','同一个默认列表被重复使用。'),example('身份与值','a=[]\nb=[]\nprint(a==b,a is b)','True False','值相等，不代表是同一个容器。')],minutes=25)
add('py13',3,'把契约写成明确的异常',2,'实现',
 '函数除了定义正常输出，也应明确拒绝哪些输入。raise ValueError 表示类型大体合适但值不在约定范围内；验证应在进行计算前完成。',
 'def positive(x):\n    if x<=0:\n        raise ValueError("x must be positive")\n    return x',
 ['xs 为空时抛 ValueError。','检查所有数是否在 0 到 1 内，任何一个越界都拒绝。','合法输入求平均；0 和 1 都属于合法边界。不要吞掉异常并返回一个看似合法的数。'],
 '定义 mean_probability(xs)，只接受非空且所有元素都在 [0,1] 的数值序列，返回均值；空序列或元素越界抛 ValueError。','def mean_probability(xs)',
 'def mean_probability(xs):\n    if not xs or any(x<0 or x>1 for x in xs):\n        raise ValueError("invalid probabilities")\n    return sum(xs)/len(xs)',
 [case('mean_probability([0,0.5,1])',0.5,label='合法边界'),case('mean_probability([1])',1,label='单元素'),case('mean_probability([])',raises='ValueError',label='空输入'),case('mean_probability([-0.01,0.5])',raises='ValueError',label='小于零'),case('mean_probability([0.5,1.1])',raises='ValueError',label='大于一')],
 quiz('非法概率输入时返回 0，有什么风险？',['0 永远不能是合法结果','调用者无法区分失败和合法的零均值','会自动抛出异常'],1,['全零输入的均值就可以是零。','对，异常让失败与合法结果明确区分。','返回数字不会自动抛异常。']),
 examples=[example('提前验证','xs=[0.2,1.3]\nprint(any(x<0 or x>1 for x in xs))','True','any 只需一个非法元素就为真。'),example('合法边界','print(0 <= 0 <= 1, 0 <= 1 <= 1)','True True','约定 [0,1] 包含两端。')])

existing('p5',4,1,15)
add('py14',4,'用字典统计标签',1,'实现',
 '计数字典用每个标签作为键、出现次数作为值。dict.get(key,0) 为没出现过的标签提供初值。字典保留插入顺序，但计数本身通常不依赖顺序。',
 'counts={}\nfor label in ["cat","dog","cat"]:\n    counts[label]=counts.get(label,0)+1\nprint(counts)',
 ['创建空字典，不要预设全部标签。','对每项使用 counts.get(label,0)+1 更新。','空输入应返回 {}；标签可能是整数或字符串，不能用固定长度数组代替。'],
 '定义 label_counts(labels)，返回每个可哈希标签的出现次数。','def label_counts(labels)',
 'def label_counts(labels):\n    counts={}\n    for label in labels:\n        counts[label]=counts.get(label,0)+1\n    return counts',
 [case('label_counts(["a","b","a"])',{'a':2,'b':1},label='重复标签'),case('label_counts([])',{},label='空标签'),case('label_counts([2,2,7])[2]',2,label='整数键'),case('label_counts(["", ""])',{'':2},label='空字符串也是标签')],
 quiz('counts 中没有键 x，怎样把它的计数初始化为 1？',['counts[x] += 1 总能成功','counts[x] = counts.get(x,0)+1','counts.append(x)'],1,['缺失键会导致 KeyError。','对，get 给未出现的键提供默认值。','字典没有 append。']),
 examples=[example('不存在的键','d={}\nprint(d.get("new",0))','0','get 不会自动把键插入字典。'),example('计数更新','d={"x":2}\nd["x"]=d.get("x",0)+1\nprint(d)',"{'x': 3}",'已有键在原值上加一。')])
add('py15',4,'分组平均不能混在一起',2,'实现',
 '实验记录常按模型分组。每组需要独立的总和与计数，最后才能计算均值。不能把组均值再简单平均来替代所有样本的加权平均。',
 'rows=[{"model":"A","loss":1.0},{"model":"A","loss":3.0}]\ntotal=sum(r["loss"] for r in rows)\nprint(total/len(rows))',
 ['用字典保存每个 model 的 loss 总和与记录数量。','完整遍历后再为每组计算 total/count。','组大小可能不同；不能假设每个模型有相同记录数。空输入返回 {}，不修改记录。'],
 '定义 group_mean(records)，records 每项包含 model 和 loss，返回 {model: 平均loss}。','def group_mean(records)',
 '''def group_mean(records):
    totals={}
    counts={}
    for row in records:
        key=row['model']
        totals[key]=totals.get(key,0)+row['loss']
        counts[key]=counts.get(key,0)+1
    return {key:totals[key]/counts[key] for key in totals}''',
 [case('group_mean([{"model":"A","loss":1},{"model":"B","loss":9},{"model":"A","loss":3}])',{'A':2,'B':9},label='交错分组'),case('group_mean([])',{},label='空记录'),case('group_mean([{"model":"x","loss":0},{"model":"x","loss":0.6}])',{'x':0.3},label='零损失也计数'),case('group_mean([{"model":"solo","loss":2.5}])',{'solo':2.5},label='单次实验')],
 quiz('一组有 1 条记录，另一组有 9 条，整体均值能简单平均两个组均值吗？',['总能','只有各组数量相同时才普遍成立','只要组名不同就可以'],1,['不同组权重不同。','对，整体均值需要按样本数量加权。','组名不影响统计权重。']),
 examples=[example('不同组的权重','print((1*0+3*4)/(1+3))','3.0','一条 0 和三条 4 的整体均值是 3，不是 2。'),example('字典推导式','totals={"A":6};counts={"A":3}\nprint({k:totals[k]/counts[k] for k in totals})',"{'A': 2.0}",'为每个分组单独计算。')],minutes=25)
add('py16',4,'让榜单排序可重复',2,'实现',
 'sorted 返回新列表，key 决定比较值。key 可以返回元组：先比较第一项，相同再比较后面的项。明确的并列规则可以让榜单和实验结果可重复。',
 'rows=[{"name":"b","score":2},{"name":"a","score":2}]\nprint(sorted(rows,key=lambda r:(-r["score"],r["name"])))',
 ['用 key 返回 (-score,name)，这样得分降序、名称升序。','再提取前 k 条的 name。k=0 返回 []，k 大于记录数时返回全部。','sorted 不改输入；list.sort 会原地排序。不要只按 score 排，忽略并列规则。'],
 '定义 top_runs(records,k)，记录包含 name、score，按 score 降序、name 升序返回前 k 个名称；k≥0，不能修改 records。','def top_runs(records, k)',
 'def top_runs(records,k):\n    ranked=sorted(records,key=lambda r:(-r["score"],r["name"]))\n    return [r["name"] for r in ranked[:k]]',
 [case('top_runs([{"name":"b","score":2},{"name":"a","score":2},{"name":"c","score":3}],3)',['c','a','b'],label='并列规则'),case('top_runs([],2)',[],label='无记录'),case('top_runs([{"name":"x","score":0}],0)',[],label='取零项'),case('rows',[{'name':'z','score':1},{'name':'a','score':2}],setup='rows=[{"name":"z","score":1},{"name":"a","score":2}]\ntop_runs(rows,2)',label='原顺序不变')],
 quiz('key=lambda r:(-r["score"],r["name"]) 中为什么把 score 取负？',['让默认升序变成分数降序','避免浮点误差','把负分变成无效值'],0,['对，越大的原分数对应越小的负数。','取负不能解决浮点误差。','负分仍然可以按同一规则排序。']),
 examples=[example('元组排序','print(sorted([(2,"b"),(2,"a"),(1,"z")]))',"[(1, 'z'), (2, 'a'), (2, 'b')]",'先看数值，再看字符串。'),example('排序副本','xs=[3,1]\nys=sorted(xs)\nprint(xs,ys)','[3, 1] [1, 3]','原列表保持不变。')],minutes=25)
add('py17',4,'合并配置但别共享内部状态',3,'挑战',
 '配置通常有默认值与用户覆盖值。这里要求递归合并嵌套字典：双方都是字典才继续深入，否则覆盖值替换默认值。返回结果必须独立，防止修改新配置污染旧配置。',
 'import copy\na={"train":{"lr":0.1}}\nb=copy.deepcopy(a)\nb["train"]["lr"]=0.2\nprint(a)',
 ['先 deepcopy 默认配置，避免共享嵌套列表和字典。','遍历覆盖项；双方都是 dict 时递归合并，否则 deepcopy 覆盖值。','不要只做浅 copy。即使覆盖列表，也要复制它，结果不能与任一输入共享可变对象。'],
 '定义 merge_config(defaults,overrides)，递归合并嵌套字典，覆盖值优先，返回完全独立的可变结构。输入由字典、列表及基本值组成，不含循环引用。','def merge_config(defaults, overrides)',
 '''import copy
def merge_config(defaults,overrides):
    result=copy.deepcopy(defaults)
    for key,value in overrides.items():
        if key in result and isinstance(result[key],dict) and isinstance(value,dict):
            result[key]=merge_config(result[key],value)
        else:
            result[key]=copy.deepcopy(value)
    return result''',
 [case('merge_config({"train":{"lr":0.1,"epochs":5}},{"train":{"lr":0.2}})',{'train':{'lr':0.2,'epochs':5}},label='递归覆盖'),case('merge_config({"a":1},{"a":None,"b":2})',{'a':None,'b':2},label='None 也可覆盖'),case('a',{'x':[1]},setup='a={"x":[1]}\nr=merge_config(a,{})\nr["x"].append(2)',label='默认值独立'),case('b',{'x':[9]},setup='b={"x":[9]}\nr=merge_config({},b)\nr["x"].append(2)',label='覆盖值独立'),case('merge_config({"a":{"x":1}},{"a":3})',{'a':3},label='非字典替换')],
 quiz('dict.copy() 为什么不够满足本题？',['它不复制键','它只复制外层，内层列表仍共享','它总会改变值的类型'],1,['copy 会保留键。','对，嵌套可变对象还指向原对象。','浅复制不会自动改变类型。']),
 examples=[example('浅复制仍共享','a={"x":[1]}\nb=a.copy()\nb["x"].append(2)\nprint(a)',"{'x': [1, 2]}",'外层不同，内部列表相同。'),example('深复制隔离','import copy\na={"x":[1]}\nb=copy.deepcopy(a)\nb["x"].append(2)\nprint(a)',"{'x': [1]}",'深复制使嵌套容器相互独立。')],minutes=30)
add('py18',4,'选出最好的有效 checkpoint',3,'综合',
 '实验可能失败或记录缺失。选择 checkpoint 时，先过滤无效记录，再应用完整的排序规则。不要让坏数据在最终排名时悄悄变成零分或更优分数。',
 'import math\nprint(math.isfinite(0.3),math.isfinite(float("nan")))',
 ['只接受 status=="ok" 且 loss 是有限数值的记录；缺少 loss 视为无效。','候选按 (loss,epoch) 升序选择，loss 相同时取更早的 epoch。','没有候选返回 None。有效的零损失不能被 if loss 误过滤。'],
 '定义 best_checkpoint(records)，记录含 epoch、status，可选 loss。只保留 status 为 ok 且 loss 为有限 int/float（不含 bool）的记录，返回最小 loss、并列最早 epoch；无有效记录返回 None。','def best_checkpoint(records)',
 '''import math
def best_checkpoint(records):
    valid=[]
    for row in records:
        value=row.get('loss')
        if row.get('status')=='ok' and type(value) in (int,float) and math.isfinite(value):
            valid.append(row)
    if not valid:
        return None
    return min(valid,key=lambda r:(r['loss'],r['epoch']))['epoch']''',
 [case('best_checkpoint([{"epoch":3,"status":"ok","loss":0.2},{"epoch":1,"status":"ok","loss":0.2}])',1,label='并列取早'),case('best_checkpoint([{"epoch":1,"status":"failed","loss":0},{"epoch":2,"status":"ok","loss":0.5}])',2,label='失败实验不能入选'),case('best_checkpoint([{"epoch":1,"status":"ok","loss":float("nan")},{"epoch":2,"status":"ok","loss":0}])',2,label='NaN 与合法零'),case('best_checkpoint([{"epoch":1,"status":"ok"}])',None,label='缺失指标'),case('best_checkpoint([])',None,label='空记录'),case('best_checkpoint([{"epoch":1,"status":"ok","loss":False}])',None,label='布尔值不是指标')],
 quiz('float("nan") 为什么需要显式过滤？',['它等于 0','它不是有限的有效指标，普通比较不能表达正常排名','它不能存入字典'],1,['NaN 不等于 0。','对，使用 isfinite 排除 NaN 与无穷大。','字典可以保存 NaN，但不代表它是有效数据。']),
 examples=[example('NaN 的比较','x=float("nan")\nprint(x==x, x<0, x>0)','False False False','不能期待 NaN 像普通数那样参与排名。'),example('并列规则','rows=[(0.3,5),(0.3,2)]\nprint(min(rows))','(0.3, 2)','loss 相同后比较 epoch。')],minutes=30)

add('py19',5,'只处理你预料到的错误',1,'实现',
 'try / except 用来处理可能失败的转换。只捕获预期异常，才能保留其他程序错误的线索。解析配置中的概率时，还应过滤 NaN、无穷大和越界值。',
 'try:\n    value=float("oops")\nexcept ValueError:\n    value=None\nprint(value)',
 ['先 float(text.strip())；只对 ValueError 做回退。','转换成功后用 math.isfinite 和 0<=value<=1 检查合法性。','无效字符串、非有限值与越界值都返回 None；合法零应返回 0.0。'],
 '定义 parse_probability(text)，text 是字符串。合法的 [0,1] 有限浮点值返回 float，其余返回 None。','def parse_probability(text)',
 'import math\ndef parse_probability(text):\n    try:\n        value=float(text.strip())\n    except ValueError:\n        return None\n    return value if math.isfinite(value) and 0<=value<=1 else None',
 [case('parse_probability(" 0.25 ")',0.25,label='空白'),case('parse_probability("0")',0,label='合法零'),case('parse_probability("1")',1,label='合法一'),case('parse_probability("nan")',None,label='NaN'),case('parse_probability("1.2")',None,label='越界'),case('parse_probability("oops")',None,label='格式错误'),case('parse_probability("")',None,label='空文本')],
 quiz('为什么通常不写 except Exception: return None？',['因为 Python 不允许','它还会吞掉名字拼错等非预期程序错误','因为它只能捕获 ValueError'],1,['语法允许，但范围太宽。','对，只处理预期转换错误更易排错。','Exception 范围远大于 ValueError。']),
 examples=[example('预期转换错误','try:\n    print(float("not-a-number"))\nexcept ValueError:\n    print("格式无效")','格式无效','失败是输入不符合转换规则。'),example('能解析不等于合法','import math\nx=float("inf")\nprint(math.isfinite(x))','False','解析成功后仍要做值域检查。')])
add('py20',5,'真正读取一份 JSON 文件',1,'实现',
 'with open(...) 在代码块结束时关闭文件。json.load 从文件读取，json.loads 从字符串读取。encoding="utf-8" 让包含中文的配置跨平台保持一致。',
 'import json\ntext=\'{"lr": 0.1, "name": "实验"}\'\nconfig=json.loads(text)\nprint(config["lr"])',
 ['用 with open(path,encoding="utf-8") as f 获取文件。','json.load(f) 得到字典后，读取 name 与 lr。','缺少 lr 时使用默认值 0.001；显式的 lr=0 不能被默认值替换。文件错误与 JSON 格式错误保持抛出。'],
 '定义 read_config(path)，从 UTF-8 JSON 文件读取配置，返回 {"name":配置的name,"lr":配置lr或默认0.001}。name 保证存在。不要吞掉文件或 JSON 错误。','def read_config(path)',
 'import json\ndef read_config(path):\n    with open(path,encoding="utf-8") as f:\n        config=json.load(f)\n    return {"name":config["name"],"lr":config.get("lr",0.001)}',
 [case('read_config("config.json")',{'name':'实验甲','lr':0.2},label='中文与数值'),case('read_config("default.json")',{'name':'baseline','lr':0.001},label='默认值'),case('read_config("zero.json")',{'name':'zero','lr':0},label='显式零'),case('read_config("missing.json")',raises='FileNotFoundError',label='保留缺文件错误')],
 quiz('json.load 与 json.loads 的区别是什么？',['前者读文件对象，后者读字符串','前者只支持整数','没有区别'],0,['对，注意最后的 s。','JSON 文件和字符串都支持多种值。','输入接口不同。']),
 fixtures={'config.json':'{"name":"实验甲","lr":0.2}','default.json':'{"name":"baseline"}','zero.json':'{"name":"zero","lr":0}'},
 examples=[example('文本解析','import json\nprint(json.loads(\'{"epochs": 3}\')["epochs"])','3','这里输入是字符串，所以使用 loads。'),example('合法默认值','config={"lr":0}\nprint(config.get("lr",0.001))','0','get 只在键缺失时采用默认值。')])
add('py21',5,'CSV 不能直接按逗号切',2,'实现',
 'CSV 字段可以用引号包含逗号。逐行 split(",") 会破坏这种结构。csv.DictReader 按列名组织每行；数字字段读出时仍是字符串，使用前需要转换。',
 'import csv,io\ntext=\'name,loss\\n"run,a",0.2\\n\'\nprint(list(csv.DictReader(io.StringIO(text))))',
 ['with open(path,newline="",encoding="utf-8") 打开 CSV。','用 csv.DictReader 读取行，把 loss 转成 float 后求平均。','只有表头时返回 None。引号内的逗号属于字段内容。'],
 '定义 csv_mean_loss(path)，文件列名包含 name、loss，loss 为合法数值字符串。返回平均 loss，没有数据行返回 None。','def csv_mean_loss(path)',
 'import csv\ndef csv_mean_loss(path):\n    with open(path,newline="",encoding="utf-8") as f:\n        values=[float(row["loss"]) for row in csv.DictReader(f)]\n    return sum(values)/len(values) if values else None',
 [case('csv_mean_loss("runs.csv")',0.3,label='带引号的逗号'),case('csv_mean_loss("empty.csv")',None,label='只有表头'),case('csv_mean_loss("single.csv")',0,label='零损失')],
 quiz('"run,a",0.2 这一行有多少个 CSV 字段？',['2','3','4'],0,['对，引号里的逗号不分隔列。','直接 split 会错误得到三段。','此行只有两列。']),
 fixtures={'runs.csv':'name,loss\n"run,a",0.2\nrun_b,0.4\n','empty.csv':'name,loss\n','single.csv':'name,loss\none,0\n'},
 examples=[example('引号中的逗号','import csv,io\nprint(next(csv.reader(io.StringIO(\'"x,y",2\\n\'))))',"['x,y', '2']",'csv.reader 知道引号语义。'),example('数字转换','row={"loss":"0.25"}\nprint(float(row["loss"])*2)','0.5','解析 CSV 后还要转换数值字段。')],minutes=25)
add('py22',5,'逐行解析不完美的日志',2,'实现',
 'JSONL 一行一个 JSON 值，适合增量日志。空行可以跳过，坏行应有可见的统计。这里要求每个有效行必须是字典，所以语法正确的数组也应计为无效记录。',
 'import json\nfor line in [\'{"loss":0.2}\',"broken"]:\n    try:\n        print(json.loads(line))\n    except json.JSONDecodeError:\n        print("坏行")',
 ['按行读取并 strip，空行不计入任何一边。','捕获 json.JSONDecodeError，非字典的合法 JSON 也计入 rejected。','返回 (records,rejected)，不要因为第一行错误就放弃整个文件。'],
 '定义 read_jsonl(path)，读取 UTF-8 JSONL，忽略空行，收集字典记录，并统计坏 JSON 或非字典行。返回 (记录列表,无效行数)。','def read_jsonl(path)',
 '''import json
def read_jsonl(path):
    records=[]
    rejected=0
    with open(path,encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                value=json.loads(line)
            except json.JSONDecodeError:
                rejected+=1
                continue
            if isinstance(value,dict):
                records.append(value)
            else:
                rejected+=1
    return records,rejected''',
 [case('read_jsonl("mixed.jsonl")',[[{'loss':0.2},{'name':'甲'}],2],label='坏行、数组与空行'),case('read_jsonl("blank.jsonl")',[[],0],label='全空白'),case('read_jsonl("scalar.jsonl")',[[],3],label='标量均无效')],
 quiz('某行是 [1,2]，它属于哪类？',['坏 JSON','合法 JSON，但不符合本题的记录结构','字典记录'],1,['JSON 数组语法合法。','对，语法有效不代表结构符合数据约定。','Python 中解析为 list。']),
 fixtures={'mixed.jsonl':'{"loss":0.2}\n\nbroken\n[1,2]\n{"name":"甲"}\n','blank.jsonl':'\n  \n','scalar.jsonl':'null\n3\n"text"\n'},
 examples=[example('语法与结构','import json\nx=json.loads("[1,2]")\nprint(isinstance(x,dict))','False','解析成功后还需要验证结构。'),example('空白行','print(bool("  \\n".strip()))','False','strip 后为空，所以可以跳过。')],minutes=25)
add('py23',5,'把数据约定变成断言',2,'排错',
 '测试不是只选一个正常样例。批次数据至少要检查样本数量一致、每行特征宽度相同，以及标签范围。assert 能让违反约定的地方尽早暴露，正式接口也可用显式异常。',
 'features=[[1,2],[3,4]]\nlabels=[0,1]\nassert len(features)==len(labels)\nprint("长度一致")',
 ['定义 validate_batch(features,labels)，合法时返回 True。','用 assert 检查样本数一致；非空时每行宽度等于首行；标签必须是非负 int，不能接受 bool。','两个空列表合法。任一约定不满足时必须抛 AssertionError，而不是返回 False。'],
 '实现 validate_batch(features,labels)。验证数量一致、二维特征行等宽、标签为非负整数（不含bool）。合法返回 True，非法抛 AssertionError。','def validate_batch(features, labels)',
 'def validate_batch(features,labels):\n    assert len(features)==len(labels)\n    if features:\n        assert all(len(row)==len(features[0]) for row in features)\n    assert all(type(x) is int and x>=0 for x in labels)\n    return True',
 [case('validate_batch([[1,2],[3,4]],[0,1])',True,label='合法数据'),case('validate_batch([],[])',True,label='空批次'),case('validate_batch([[1]],[0,1])',raises='AssertionError',label='数量不一致'),case('validate_batch([[1],[2,3]],[0,1])',raises='AssertionError',label='不规则特征'),case('validate_batch([[1]],[-1])',raises='AssertionError',label='负标签'),case('validate_batch([[1]],[True])',raises='AssertionError',label='bool 不作类别编号')],
 quiz('只检查 len(features)==len(labels) 是否足够？',['足够，说明所有行都一样宽','不够，还可能存在不规则行或非法标签','足够，只要不报语法错误'],1,['样本数量与特征维度是不同约定。','对，需要独立验证各项不变量。','语法通过不保证数据有效。']),
 bug='def validate_batch(features,labels):\n    return len(features)==len(labels)',
 examples=[example('数量相同但维度错误','x=[[1],[2,3]]\ny=[0,1]\nprint(len(x)==len(y))','True','这个正常结果会掩盖特征维度问题。'),example('bool 是特殊整数','print(isinstance(True,int),type(True) is int)','True False','精确类型检查可排除布尔标签。')],minutes=25)
add('py24',5,'综合：生成可重跑的实验报告',3,'综合',
 '报告脚本把读取、清洗、分组统计和写出连接起来。先规定有效记录，再对同一批有效数据计算指标。输出文件用覆盖写入，重复运行不应偷偷追加上一份结果。',
 'import json\nreport={"A":{"count":2,"mean_loss":0.3}}\ntext=json.dumps(report,ensure_ascii=False)\nprint(json.loads(text)==report)',
 ['逐行解析 JSONL，跳过坏 JSON、非字典、status 非 ok、model 非字符串、loss 非有限数值或 bool 的记录。','为每个 model 维护 count、sum、min，最后产生 count、mean_loss、best_loss。','用 json.dump 覆盖写入 output_path，同时返回相同字典；空有效集写 {}。'],
 '定义 build_report(input_path,output_path)。读取 JSONL，只保留 status==ok、model 为字符串、loss 为有限数值且不含bool的记录。返回并写入 {model:{count,mean_loss,best_loss}}。坏行跳过，输出覆盖写。','def build_report(input_path, output_path)',
 '''import json,math
def build_report(input_path,output_path):
    groups={}
    with open(input_path,encoding='utf-8') as f:
        for line in f:
            try:
                row=json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row,dict):
                continue
            loss=row.get('loss')
            if row.get('status')!='ok' or not isinstance(row.get('model'),str) or type(loss) not in (int,float) or not math.isfinite(loss):
                continue
            groups.setdefault(row['model'],[]).append(loss)
    result={k:{'count':len(v),'mean_loss':sum(v)/len(v),'best_loss':min(v)} for k,v in groups.items()}
    with open(output_path,'w',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False)
    return result''',
 [case('build_report("logs.jsonl","out.json")',{'A':{'count':2,'mean_loss':0.3,'best_loss':0.2},'B':{'count':1,'mean_loss':0.8,'best_loss':0.8}},label='分组报告'),case('__import__("json").loads(open("out.json",encoding="utf-8").read())==report',True,setup='report=build_report("logs.jsonl","out.json")',label='文件与返回值一致'),case('build_report("empty.jsonl","out.json")',{},label='覆盖为空报告'),case('list(__import__("json").loads(open("out.json").read()).keys())',[],setup='build_report("empty.jsonl","out.json")',label='不能追加旧结果')],
 quiz('为什么第二次运行不能用追加模式 a 写 JSON 报告？',['追加会自动合并字典','会拼接多个 JSON 对象，通常不再是一份合法报告','追加模式不存在'],1,['文件不会替你合并结构。','对，完整报告通常应覆盖写成一个对象。','a 是合法模式，但不符合本题语义。']),
 fixtures={'logs.jsonl':'{"model":"A","loss":0.2,"status":"ok"}\n{"model":"A","loss":0.4,"status":"ok"}\nbroken\n{"model":"A","loss":0,"status":"failed"}\n{"model":"B","loss":0.8,"status":"ok"}\n{"model":"A","loss":false,"status":"ok"}\n','empty.jsonl':'bad\n[]\n'},
 examples=[example('统计约定','values=[0.2,0.4]\nprint(len(values),sum(values)/len(values),min(values))','2 0.30000000000000004 0.2','浮点均值按容差检查，不要求字符串完全一致。'),example('往返校验','import json\nobj={"x":0.2}\nprint(json.loads(json.dumps(obj))==obj)','True','写出后再读回，是检查报告格式的一种方式。')],minutes=35)

add('py25',6,'用类维护加权均值',1,'实现',
 '类把状态与更新方法放在一起。__init__ 初始化实例自己的计数与总和，self 指向当前实例。加权均值应累计 value×n，最后除以累计样本数。',
 'class Counter:\n    def __init__(self):\n        self.count=0\n    def update(self,n):\n        self.count+=n',
 ['实现 AverageMeter，__init__ 与 reset 把 total、count 清零。','update(value,n=1) 累加 value*n 与 n；n=0 不改变统计。','compute() 在 count=0 时返回 0.0，否则返回 total/count。不同实例不能共享状态。'],
 '定义 AverageMeter 类，支持 update(value,n=1)、compute()、reset()。输入 n 为非负整数，compute 返回加权均值，空状态返回 0.0。','class AverageMeter',
 'class AverageMeter:\n    def __init__(self):\n        self.reset()\n    def reset(self):\n        self.total=0.0\n        self.count=0\n    def update(self,value,n=1):\n        self.total+=value*n\n        self.count+=n\n    def compute(self):\n        return self.total/self.count if self.count else 0.0',
 [case('AverageMeter().compute()',0,label='空状态'),case('m.compute()',2.5,setup='m=AverageMeter()\nm.update(1,1)\nm.update(3,3)',label='不等批次权重'),case('m.compute()',0,setup='m=AverageMeter()\nm.update(7)\nm.reset()',label='重置'),case('b.compute()',0,setup='a=AverageMeter()\nb=AverageMeter()\na.update(99)',label='实例相互独立'),case('m.compute()',2,setup='m=AverageMeter()\nm.update(2)\nm.update(999,0)',label='零权重')],
 quiz('一个批次均值为 1、含 1 项，另一个均值为 3、含 3 项，整体均值是多少？',['2','2.5','4'],1,['不能忽略批次大小。','对，(1×1+3×3)/4=2.5。','总样本数是 4，均值不是 4。']),
 examples=[example('实例状态','class Box:\n    def __init__(self):\n        self.x=[]\na=Box();b=Box()\na.x.append(1)\nprint(b.x)','[]','在初始化方法中创建列表，每个实例各自拥有。'),example('加权求和','print((1*1+3*3)/(1+3))','2.5','先恢复每批总和，再合并。')],minutes=25)
add('py26',6,'累计分类结果而非累计比例',2,'实现',
 '分类准确率的可合并状态是“正确数、总数”，而不是每批准确率列表。将状态封装成类后，可以分多次 update，最后统一 compute。',
 'correct=2\ntotal=3\ncorrect += 1\ntotal += 1\nprint(correct/total)',
 ['实现 AccuracyMeter，每次 update(preds,labels) 先验证长度相同，否则抛 ValueError。','累计相同位置预测相等的数量与本批样本数。','空批次不改变结果；compute 在没有样本时返回 0.0。'],
 '定义 AccuracyMeter，支持 update(preds,labels)、compute()。多次更新等价于拼接全部样本后计算，长度不一致抛 ValueError。','class AccuracyMeter',
 'class AccuracyMeter:\n    def __init__(self):\n        self.correct=0\n        self.total=0\n    def update(self,preds,labels):\n        if len(preds)!=len(labels):\n            raise ValueError("length mismatch")\n        self.correct+=sum(a==b for a,b in zip(preds,labels))\n        self.total+=len(labels)\n    def compute(self):\n        return self.correct/self.total if self.total else 0.0',
 [case('AccuracyMeter().compute()',0,label='无样本'),case('m.compute()',0.75,setup='m=AccuracyMeter()\nm.update([1,0,1],[1,1,1])\nm.update([0],[0])',label='不等长批次'),case('m.update([0],[0,1])',raises='ValueError',setup='m=AccuracyMeter()',label='拒绝长度不一致'),case('m.compute()',1,setup='m=AccuracyMeter()\nm.update([1],[1])\nm.update([],[])',label='空批次无影响')],
 quiz('两批大小不同，直接平均它们的准确率，通常会怎样？',['一定等于整体准确率','可能错误，应该按样本数累计','总会变成零'],1,['小批次不能获得与大批次相同权重。','对，累计正确数与总数即可。','错误不一定是零。']),
 examples=[example('批次比例平均的偏差','print((0/1+3/3)/2)\nprint((0+3)/(1+3))','0.5\n0.75','两种结果不同，后一种按样本统计。'),example('长度要先检查','print(list(zip([1,2],[1])))','[(1, 1)]','zip 会静默截断，不能替代长度验证。')],minutes=25)
add('py27',6,'实现一个可索引数据集',2,'实现',
 '定义 __len__ 与 __getitem__ 后，对象可以支持 len(ds) 与 ds[i]。这种“协议”让数据容器与使用方解耦，也是后续 PyTorch Dataset 的基础。',
 'class Numbers:\n    def __len__(self):\n        return 3\n    def __getitem__(self,i):\n        return [10,20,30][i]\nprint(Numbers()[1])',
 ['构造时验证 features、labels 数量一致，保存每个特征行的副本。','__getitem__ 返回 (一行特征的新列表,标签)，支持列表的负索引语义。','索引越界保留 IndexError；修改输入或返回的行，不能污染内部数据。'],
 '定义 ListDataset(features,labels)，支持 len(ds)、ds[i]。数据长度不一致抛 ValueError；构造与取出时均复制特征行。标签为基本值。','class ListDataset',
 'class ListDataset:\n    def __init__(self,features,labels):\n        if len(features)!=len(labels):\n            raise ValueError("length mismatch")\n        self.features=[list(row) for row in features]\n        self.labels=list(labels)\n    def __len__(self):\n        return len(self.labels)\n    def __getitem__(self,i):\n        return list(self.features[i]),self.labels[i]',
 [case('len(ListDataset([[1],[2]],[0,1]))',2,label='长度协议'),case('ListDataset([[1],[2]],[0,1])[-1]',[[2],1],label='负索引'),case('ListDataset([],[])[0]',raises='IndexError',label='越界'),case('ListDataset([[1]],[])',raises='ValueError',label='构造长度检查'),case('ds[0]',[[1,2],0],setup='xs=[[1,2]]\nds=ListDataset(xs,[0])\nxs[0][0]=99\na,b=ds[0]\na[0]=88',label='输入输出都隔离')],
 quiz('ds[i] 会调用哪个方法？',['__len__','__getitem__','forward'],1,['len(ds) 才调用它。','对，索引协议调用 __getitem__。','forward 用于神经网络的前向计算。']),
 examples=[example('长度协议','class Tiny:\n    def __len__(self):\n        return 2\nprint(len(Tiny()))','2','内置函数会调用协议方法。'),example('列表负索引','print([10,20,30][-1])','30','本题把相同的语义保留给数据集。')],minutes=25)
add('py28',6,'实现提前停止状态机',3,'挑战',
 'Early stopping 持续观察验证指标，而不是只比较相邻两轮。这里记录历史最好 loss；改善幅度必须严格大于 min_delta，才清零等待计数。',
 'best=0.5\nnew=0.48\nmin_delta=0.03\nprint(new < best-min_delta)',
 ['构造 EarlyStop(patience,min_delta=0)，要求 patience≥1、min_delta≥0，否则抛 ValueError。','第一次观测建立 best。此后仅 loss < best-min_delta 算改善，更新 best 并清零坏轮数。','连续未改善轮数达到 patience 后 step 返回 True。相等不算改善；历史最好值不是上一轮的值。'],
 '定义 EarlyStop，支持 step(loss)→bool。按上述历史最优与严格改善规则决定是否停止。输入 loss 为有限数，patience 为整数。','class EarlyStop(patience, min_delta=0)',
 'class EarlyStop:\n    def __init__(self,patience,min_delta=0):\n        if patience<1 or min_delta<0:\n            raise ValueError("invalid settings")\n        self.patience=patience\n        self.min_delta=min_delta\n        self.best=None\n        self.bad=0\n    def step(self,loss):\n        if self.best is None or loss < self.best-self.min_delta:\n            self.best=loss\n            self.bad=0\n        else:\n            self.bad+=1\n        return self.bad>=self.patience',
 [case('[e.step(x) for x in [1,0.8,0.9,0.85]]',[False,False,False,True],setup='e=EarlyStop(2)',label='历史最优'),case('[e.step(x) for x in [1,1,0.5,0.5]]',[False,False,False,False],setup='e=EarlyStop(2)',label='改善清零'),case('[e.step(x) for x in [1,0.9]]',[False,True],setup='e=EarlyStop(1,min_delta=0.2)',label='改善幅度不足'),case('EarlyStop(0)',raises='ValueError',label='非法 patience'),case('EarlyStop(1,-0.1)',raises='ValueError',label='非法 delta')],
 quiz('验证 loss 从 0.3 变 0.5，再变 0.4，最后一轮一定算改善吗？',['算，因为比上一轮更低','不算，仍然比历史最好 0.3 差','只看训练 loss'],1,['比较基准是历史最优。','对，要与 best 比。','提前停止通常观察独立验证指标。']),
 examples=[example('对比历史而非相邻','best=0.3\nprevious=0.5\ncurrent=0.4\nprint(current<previous,current<best)','True False','相邻改善不等于突破历史最好。'),example('计数达到阈值','bad=2\npatience=2\nprint(bad>=patience)','True','达到阈值这一轮就可以停止。')],minutes=30)
add('py29',6,'把小函数组合成处理流水线',2,'实现',
 '函数可以像其他对象一样存入列表并被依次调用。Compose 把 f、g 组合成 g(f(x))；顺序通常不能交换。构造时复制函数列表，避免外部追加影响已创建的流程。',
 'def twice(x):\n    return x*2\ndef plus_one(x):\n    return x+1\nprint(plus_one(twice(3)))',
 ['类 Compose 接收 transforms，保存 list(transforms)。','实现 __call__(self,x)，按顺序将每个 transform 的输出交给下一个。','空流水线返回原值；不要反转顺序，不要修改调用者传入的 transforms 列表。'],
 '定义 Compose(transforms)，对象可调用，依次执行全部变换。构造时复制函数列表，空列表表示恒等变换。','class Compose · __call__',
 'class Compose:\n    def __init__(self,transforms):\n        self.transforms=list(transforms)\n    def __call__(self,x):\n        for transform in self.transforms:\n            x=transform(x)\n        return x',
 [case('Compose([lambda x:x*2,lambda x:x+1])(3)',7,label='顺序不可逆'),case('Compose([])(8)',8,label='空流水线'),case('Compose([str,lambda s:s.upper()])("hello")','HELLO',label='类型可以变化'),case('pipeline(3)',6,setup='funcs=[lambda x:x*2]\npipeline=Compose(funcs)\nfuncs.append(lambda x:x+10)',label='构造列表独立')],
 quiz('先 ×2 再 +1，与先 +1 再 ×2，一般相同吗？',['总相同','通常不同，执行顺序是接口的一部分','Python 自动按数值排序函数'],1,['可用 x=3 验证结果 7 与 8。','对，组合顺序有意义。','函数不会被自动重排。']),
 examples=[example('顺序对比','x=3\nprint(x*2+1,(x+1)*2)','7 8','输出不同，顺序不能随意更换。'),example('函数也是值','functions=[len,str]\nprint(functions[0]([1,2]))','2','取出函数后可以正常调用。')],minutes=25)
add('py30',6,'综合：按组划分，防止数据泄漏',3,'综合',
 '同一用户、文档或实验组的样本若同时出现在训练与验证集，会造成泄漏。按 group_id 划分可保持组隔离；同时应拒绝重复 sample_id，并让输出副本独立于原记录。',
 'validation_groups={"user_b"}\nrow={"sample_id":"s1","group_id":"user_b"}\nprint(row["group_id"] in validation_groups)',
 ['先检查全部 sample_id 是否唯一，重复则抛 ValueError。','group_id 在 val_groups 中的放入验证集，其余放训练集，保持各自原始相对顺序。','记录可能含嵌套列表，返回 deepcopy 副本。不能修改原数据，也不能把同一组拆到两侧。'],
 '定义 split_by_group(records,val_groups)，每项包含 sample_id、group_id。返回 (train,val)；重复 sample_id 抛 ValueError；保持组隔离、原序和深复制。','def split_by_group(records, val_groups)',
 'import copy\ndef split_by_group(records,val_groups):\n    seen=set()\n    train=[]\n    val=[]\n    for row in records:\n        if row["sample_id"] in seen:\n            raise ValueError("duplicate sample_id")\n        seen.add(row["sample_id"])\n        (val if row["group_id"] in val_groups else train).append(copy.deepcopy(row))\n    return train,val',
 [case('split_by_group([{"sample_id":1,"group_id":"a"},{"sample_id":2,"group_id":"b"},{"sample_id":3,"group_id":"a"}],{"a"})',[[{'sample_id':2,'group_id':'b'}],[{'sample_id':1,'group_id':'a'},{'sample_id':3,'group_id':'a'}]],label='整组隔离与保序'),case('split_by_group([],set())',[[],[]],label='空集'),case('split_by_group([{"sample_id":1,"group_id":"a"},{"sample_id":1,"group_id":"b"}],set())',raises='ValueError',label='跨组重复也拒绝'),case('rows',[{'sample_id':1,'group_id':'a','x':[1]}],setup='rows=[{"sample_id":1,"group_id":"a","x":[1]}]\na,b=split_by_group(rows,set())\na[0]["x"].append(9)',label='嵌套数据隔离')],
 quiz('为什么不能只随机打散同一用户的所有片段后逐条划分？',['随机划分必然报错','同一用户的信息可能同时进入训练与验证','会让列表无法排序'],1,['程序能运行并不代表划分合理。','对，组内相关样本可能造成泄漏。','排序能力不受影响。']),
 examples=[example('集合查找组归属','groups={"a","c"}\nprint("a" in groups,"b" in groups)','True False','同一 group_id 的判断始终一致。'),example('标识重复检查','ids=["s1","s2","s1"]\nprint(len(ids)==len(set(ids)))','False','数量不同说明存在重复标识。')],minutes=40)

existing('t1',7,1,15)
add('pt01',7,'展平特征，保留样本维',1,'实现',
 '图像批次通常是 [B,C,H,W]。送入线性层前把特征轴合并成 C×H×W，同时保留 B。非连续张量不能总用 view；flatten 或 reshape 会按需要处理存储布局。',
 'x=torch.arange(12).reshape(2,2,3)\nprint(x.flatten(start_dim=1).shape)',
 ['只合并第 1 维及之后的特征维，不能把 batch 一起展平。','flatten(start_dim=1) 直接表达这个目标。','检查转置后非连续输入与 B=0 的空批次，不要依赖 view(B,-1) 碰巧成功。'],
 '定义 flatten_features(x)，x 至少二维，返回形状 [B,其余维乘积] 的张量，支持非连续输入与空批次。','def flatten_features(x)',
 'def flatten_features(x):\n    return x.flatten(start_dim=1)',
 [case('list(flatten_features(torch.ones(2,3,4)).shape)',[2,12],label='保留 batch'),case('flatten_features(torch.arange(12).reshape(2,2,3).transpose(1,2))',[[0,3,1,4,2,5],[6,9,7,10,8,11]],label='非连续输入'),case('list(flatten_features(torch.zeros(0,3,2)).shape)',[0,6],label='空批次'),case('flatten_features(torch.tensor([[1.,2.]]))',[[1,2]],label='已是二维')],
 quiz('把 [8,3,4,4] 全部 flatten() 会丢失什么？',['数值精度','每条样本的边界，batch 也被合并','所有梯度'],1,['展平不要求降低精度。','对，通常应从 start_dim=1 开始。','展平本身可保留梯度。']),
 examples=[example('保留第零维','x=torch.ones(2,3,4)\nprint(list(x.flatten(1).shape))','[2, 12]','每条样本的 12 个特征放到一起。'),example('检查连续性','x=torch.ones(2,3,4).transpose(1,2)\nprint(x.is_contiguous())','False','形状改变不一定意味着数据已重新连续排列。')])
add('pt02',7,'取出每条样本的目标分数',2,'实现',
 'logits 的形状 [B,C]，labels 的形状 [B]。需要为每条样本读取它自己对应的类别，而不是让同一组列应用到全部行。成对高级索引可以同时提供行号与列号。',
 'x=torch.tensor([[1.,4.],[7.,2.]])\nrows=torch.arange(2)\nprint(x[rows,torch.tensor([1,0])])',
 ['行号使用 torch.arange(B,device=logits.device)。','列号使用 labels，让行号和列号逐项配对。','B=0 返回形状 [0]；不能用 logits[:,labels]，那会产生二维交叉选择。'],
 '定义 target_scores(logits,labels)，从二维浮点 logits 中取每条样本 labels 指定的类别分数，返回一维张量，保留输入 dtype 和梯度。','def target_scores(logits, labels)',
 'def target_scores(logits,labels):\n    return logits[torch.arange(logits.shape[0],device=logits.device),labels]',
 [case('target_scores(torch.tensor([[1.,4.],[7.,2.]]),torch.tensor([1,0]))',[4,7],label='逐行选择'),case('list(target_scores(torch.empty(0,3),torch.empty(0,dtype=torch.long)).shape)',[0],label='空批次'),case('target_scores(torch.tensor([[8.,9.,1.]]),torch.tensor([2]))',[1],label='单样本'),case('target_scores(torch.ones(2,3,requires_grad=True),torch.tensor([0,2])).requires_grad',True,label='保留梯度')],
 quiz('logits[:, labels] 对 B=2、labels 长度为2时通常得到什么形状？',['[2]','[2,2]','标量'],1,['它不是逐行配对。','对，所有行都取同样的两列。','仍然包含行和列两个维度。']),
 examples=[example('配对索引','x=torch.arange(6).reshape(2,3)\nprint(x[torch.tensor([0,1]),torch.tensor([2,0])])','tensor([2, 3])','分别取第0行第2列和第1行第0列。'),example('交叉选择','x=torch.zeros(2,3)\nprint(list(x[:,torch.tensor([2,0])].shape))','[2, 2]','同样列号应用到全部行。')],minutes=25)
add('pt03',7,'只平均有效位置',2,'实现',
 'mask 表示哪些位置有效。求均值时先把无效值排除，再除以有效数量。把无效位置置零却仍按完整长度求均值，会使短序列受到额外惩罚。',
 'x=torch.tensor([[2.,8.,100.]])\nmask=torch.tensor([[True,True,False]])\nprint((x*mask).sum(1)/mask.sum(1))',
 ['分子为每行 x*mask 的和，分母为每行 True 的数量。','把分母 clamp_min(1)，全无效行的分子为0，最终返回0。','不能除以特征总数；全无效行不允许 NaN，输出应保留梯度。'],
 '定义 masked_row_mean(x,mask)，两者形状 [B,D]、mask 为bool。返回每行有效位置的均值；全无效行返回0，不修改输入。','def masked_row_mean(x, mask)',
 'def masked_row_mean(x,mask):\n    return (x*mask).sum(dim=1)/mask.sum(dim=1).clamp_min(1)',
 [case('masked_row_mean(torch.tensor([[2.,8.,100.],[4.,9.,2.]]),torch.tensor([[True,True,False],[False,False,False]]))',[5,0],label='不等有效长度'),case('masked_row_mean(torch.tensor([[0.,2.]]),torch.tensor([[True,True]]))',[1],label='有效零'),case('list(masked_row_mean(torch.empty(0,3),torch.empty(0,3,dtype=torch.bool)).shape)',[0],label='空批次'),case('masked_row_mean(torch.ones(2,3,requires_grad=True),torch.ones(2,3,dtype=torch.bool)).requires_grad',True,label='梯度保留')],
 quiz('一行 [2,8,0,0] 只有前两项有效，均值是多少？',['2.5','5','10'],1,['2.5 错把 padding 也计入分母。','对，(2+8)/2=5。','10 是总和。']),
 examples=[example('分母要数有效项','mask=torch.tensor([[True,False,True]])\nprint(mask.sum(1))','tensor([2])','布尔 True 的计数即有效样本数。'),example('零分母保护','counts=torch.tensor([0,2])\nprint(counts.clamp_min(1))','tensor([1, 2])','全无效行的分子为0，0/1仍为0。')],minutes=25)
add('pt04',7,'构造张量版 padding 与 mask',2,'实现',
 '将变长 token 列表变成张量，需要同时固定形状和 dtype。token 编号使用 torch.long，mask 使用 torch.bool；空行和空批次也需要明确的二维形状。',
 'out=torch.zeros((2,3),dtype=torch.long)\nout[0,:2]=torch.tensor([4,0])\nprint(out)',
 ['先计算 B 和最大长度 T，创建 [B,T] 的 long 零张量和 bool 假张量。','逐行把原序列写入前 length 个位置，对应 mask 设 True。','空批次是 [0,0]，两个空序列是 [2,0]；不能根据 token 是否为0构造mask。'],
 '定义 tensor_pad(sequences)，返回 (tokens,mask)，右补0；tokens 为long，mask为bool。支持空批次、空行和合法零token。','def tensor_pad(sequences)',
 'def tensor_pad(sequences):\n    b=len(sequences)\n    t=max((len(s) for s in sequences),default=0)\n    tokens=torch.zeros((b,t),dtype=torch.long)\n    mask=torch.zeros((b,t),dtype=torch.bool)\n    for i,s in enumerate(sequences):\n        tokens[i,:len(s)]=torch.tensor(s,dtype=torch.long)\n        mask[i,:len(s)]=True\n    return tokens,mask',
 [case('tensor_pad([[0,2],[3]])',[[[0,2],[3,0]],[[True,True],[True,False]]],label='合法零与补齐'),case('[list(t.shape) for t in tensor_pad([])]',[[0,0],[0,0]],label='空批次形状'),case('[list(t.shape) for t in tensor_pad([[],[]])]',[[2,0],[2,0]],label='全空序列'),case('[str(t.dtype) for t in tensor_pad([[1]])]',['torch.int64','torch.bool'],label='正确 dtype')],
 quiz('token 编号通常使用哪种 dtype？',['float32','long / int64','bool'],1,['浮点通常用于连续特征。','对，离散索引常用整型long。','bool 用于有效位置标记。']),
 examples=[example('不同用途不同类型','print(torch.tensor([1,2],dtype=torch.long).dtype)','torch.int64','索引类型明确。'),example('空行也有形状','print(list(torch.zeros((2,0)).shape))','[2, 0]','有两条样本，每条暂时没有 token。')],minutes=25)
add('pt05',7,'向量化成对平方距离',3,'挑战',
 'x 为 [N,D]、y 为 [M,D] 时，想比较任意两条向量，可以扩出 x 的列轴与 y 的行轴，广播到 [N,M,D]，沿最后一维求和。注意本题要平方距离，不开根号。',
 'x=torch.tensor([[0.,0.],[1.,0.]])\ny=torch.tensor([[1.,1.]])\nprint(((x[:,None,:]-y[None,:,:])**2).sum(-1))',
 ['x[:,None,:] 是 [N,1,D]，y[None,:,:] 是 [1,M,D]。','差的平方沿 dim=-1 求和得到 [N,M]，不要沿样本轴求和。','支持 N 或 M 为0；不要转为 Python 列表，以便保留dtype、device和梯度。'],
 '定义 pairwise_sqdist(x,y)，返回形状 [N,M] 的成对欧氏距离平方，输入特征宽度一致，支持空样本维并保留梯度。','def pairwise_sqdist(x, y)',
 'def pairwise_sqdist(x,y):\n    return ((x[:,None,:]-y[None,:,:])**2).sum(dim=-1)',
 [case('pairwise_sqdist(torch.tensor([[0.,0.],[1.,0.]]),torch.tensor([[1.,1.],[0.,0.]]))',[[2,0],[1,1]],label='非方形语义'),case('list(pairwise_sqdist(torch.empty(0,3),torch.ones(2,3)).shape)',[0,2],label='空 x'),case('list(pairwise_sqdist(torch.ones(2,3),torch.empty(0,3)).shape)',[2,0],label='空 y'),case('pairwise_sqdist(torch.tensor([[2.,-1.]]),torch.tensor([[2.,-1.]]))',[[0]],label='相同向量'),case('pairwise_sqdist(torch.ones(2,3,requires_grad=True),torch.zeros(4,3)).requires_grad',True,label='保留计算图')],
 quiz('广播后的差张量形状是什么？',['[N,M,D]','[N,D]','[M,N]'],0,['对，每一对样本都有D个差值。','这还没有比较全部 y。','特征维在求和前仍然存在。']),
 examples=[example('添加维度','x=torch.zeros(2,3)\nprint(list(x[:,None,:].shape))','[2, 1, 3]','中间的1将扩展成另一组样本数。'),example('平方与距离','d=torch.tensor([3.,4.])\nprint((d*d).sum().item())','25.0','距离是5，平方距离是25。')],minutes=30)

existing('t2',8,1,15)
add('pt06',8,'数值稳定的 softmax',2,'实现',
 '直接对大 logits 取 exp 可能溢出。每行先减去最大值不会改变 softmax，因为分子分母同时乘同一常数；最大指数变成0，其余不大于0。',
 'x=torch.tensor([[1000.,1001.]])\nz=x-x.max(dim=-1,keepdim=True).values\nprint(z.exp())',
 ['沿最后一维取最大值，keepdim=True 方便广播。','对中心化值取 exp，再除以沿最后一维的总和。','不能直接调用 torch.softmax 或 F.softmax；检查大数、负数、相同值与三维输入。'],
 '定义 stable_softmax(x)，对任意至少一维的有限浮点张量沿最后一维实现稳定softmax。不能调用现成softmax；保持形状和梯度。','def stable_softmax(x)',
 'def stable_softmax(x):\n    z=x-x.max(dim=-1,keepdim=True).values\n    values=z.exp()\n    return values/values.sum(dim=-1,keepdim=True)',
 [case('stable_softmax(torch.tensor([[1000.,1000.],[-1000.,-1000.]]))',[[0.5,0.5],[0.5,0.5]],label='大数稳定性'),case('torch.allclose(stable_softmax(x),torch.softmax(x,-1))',True,setup='torch.manual_seed(1)\nx=torch.randn(2,3,4)',label='三维变式'),case('stable_softmax(torch.tensor([9.]))',[1],label='单类别'),case('stable_softmax(torch.ones(2,3,requires_grad=True)).requires_grad',True,label='保留梯度')],
 quiz('为什么每行减去最大值不会改变 softmax？',['它们的排序没变就足够','分子分母的公共指数因子会抵消','因为最大值总是0'],1,['排序相同不保证概率相同。','对，公共乘法因子可以约掉。','原最大值不一定是0。']),
 examples=[example('直接指数溢出','print(torch.exp(torch.tensor(1000.)).item())','inf','float32 无法表示这么大的指数值。'),example('平移后的指数','print(torch.exp(torch.tensor([1000.,1001.])-1001))','tensor([0.3679, 1.0000])','先减去最大值，把数值带回可表示范围。')],minutes=25)
add('pt07',8,'稳定计算 logsumexp',2,'实现',
 'log(sum(exp(x))) 也会先溢出。把最大值 m 提出来，可写成 m+log(sum(exp(x-m)))。本题输出沿最后一维归约后的形状，不保留该维。',
 'x=torch.tensor([1000.,1000.])\nm=x.max()\nprint((m+(x-m).exp().sum().log()).item())',
 ['先沿最后一维取最大值，暂时保留维度以便相减。','对中心化值 exp、sum、log，再加回 m。','最后 squeeze(-1) 只去掉被归约的那一维；不能用无参数 squeeze 误删batch维。'],
 '定义 stable_logsumexp(x)，输入为有限浮点数，不用现成 logsumexp，沿最后一维返回稳定结果。','def stable_logsumexp(x)',
 'def stable_logsumexp(x):\n    m=x.max(dim=-1,keepdim=True).values\n    return (m+(x-m).exp().sum(-1,keepdim=True).log()).squeeze(-1)',
 [case('stable_logsumexp(torch.tensor([[1000.,1000.]]))',[1000.693147],tolerance=1e-5,label='大数'),case('torch.allclose(stable_logsumexp(x),torch.logsumexp(x,-1))',True,setup='torch.manual_seed(2)\nx=torch.randn(2,3,4)',label='多维输入'),case('list(stable_logsumexp(torch.ones(1,2)).shape)',[1],label='保留单样本维'),case('stable_logsumexp(torch.tensor([-1000.]))',-1000,label='单元素')],
 quiz('对形状 [1,4] 的输入归约最后一维，为什么不能随意 squeeze()？',['可能把batch大小为1的维也删掉','squeeze 不能用于浮点张量','一定会改变数值'],0,['对，使用 squeeze(-1) 精确控制。','squeeze 与数值类型无关。','它改变形状，不会改变元素数值。']),
 examples=[example('指定被删除的维','x=torch.ones(1,1)\nprint(list(x.squeeze().shape),list(x.squeeze(-1).shape))','[] [1]','省略dim会删掉所有长度为1的维。'),example('加回最大值','x=torch.tensor([2.,2.])\nm=x.max()\nprint(round((m+(x-m).exp().sum().log()).item(),4))','2.6931','减去再加回，确保表达式等价。')],minutes=25)
add('pt08',8,'忽略 padding 的交叉熵',3,'挑战',
 '分类交叉熵可写成 logsumexp(logits)-目标类别logit。忽略标签时，应只在有效样本上求平均。全部被忽略也要返回与输入计算图相连的零，才能安全 backward。',
 'logits=torch.tensor([[1.,2.]])\nlabel=torch.tensor([1])\nloss=torch.logsumexp(logits,dim=1)-logits[torch.arange(1),label]\nprint(loss)',
 ['先取 labels!=ignore_index 的有效行，再进行目标索引。','用 torch.logsumexp 减目标logit，再对有效行求mean。','全无效时返回 logits.sum()*0。不要对 -100 直接做类别索引；不要调用现成 cross_entropy。'],
 '定义 masked_ce(logits,labels,ignore_index=-100)，输入 [B,C] 与 [B]，返回有效行平均交叉熵标量。全部忽略或空批次返回保留计算图的0。','def masked_ce(logits, labels, ignore_index=-100)',
 'def masked_ce(logits,labels,ignore_index=-100):\n    valid=labels!=ignore_index\n    if not valid.any():\n        return logits.sum()*0\n    x=logits[valid]\n    y=labels[valid]\n    return (torch.logsumexp(x,1)-x[torch.arange(len(y),device=x.device),y]).mean()',
 [case('masked_ce(torch.tensor([[0.,0.],[1000.,1000.]]),torch.tensor([0,-100])).item()',0.69314718,label='只平均有效行'),case('masked_ce(torch.randn(2,3,requires_grad=True),torch.tensor([-100,-100])).requires_grad',True,label='全忽略保留梯度'),case('x.grad',[[0,0],[0,0]],setup='x=torch.randn(2,2,requires_grad=True)\nmasked_ce(x,torch.tensor([-100,-100])).backward()',label='全忽略仍可反向'),case('torch.allclose(masked_ce(x,y),torch.nn.functional.cross_entropy(x,y))',True,setup='torch.manual_seed(3)\nx=torch.randn(4,3)\ny=torch.tensor([0,2,1,0])',label='与可信实现对照'),case('masked_ce(torch.empty(0,3),torch.empty(0,dtype=torch.long)).item()',0,label='空批次')],
 quiz('直接返回 torch.tensor(0.)，为什么可能导致训练报错？',['它太小','它通常不连接原计算图，也不需要梯度','所有零张量都不能求导'],1,['数值大小不是问题。','对，loss.backward 需要有效的计算图。','与输入相连的零可以求导。']),
 examples=[example('相连的零','x=torch.ones(2,requires_grad=True)\nloss=x.sum()*0\nloss.backward()\nprint(x.grad)','tensor([0., 0.])','值为零，但依旧连接x。'),example('先过滤再索引','labels=torch.tensor([1,-100])\nprint(labels[labels!=-100])','tensor([1])','无效负索引不会进入目标选择。')],minutes=35)
add('pt09',8,'拆分多头时别打乱 token',2,'实现',
 '多头注意力常把 [B,T,D] 变为 [B,H,T,D/H]。reshape 负责拆分特征维，permute 负责交换 head 与 token 轴。只做reshape会保持元素顺序，却不等于轴交换。',
 'x=torch.arange(8).reshape(1,2,4)\ny=x.reshape(1,2,2,2).permute(0,2,1,3)\nprint(y)',
 ['验证 heads 为正且 D 能整除 heads，不满足抛ValueError。','先 reshape(B,T,H,D/H)，再 permute(0,2,1,3)。','支持非连续输入；用可追踪编号检查每个token的特征是否仍然成组。'],
 '定义 split_heads(x,heads)，把 [B,T,D] 转成 [B,H,T,D/H]，维度不合法抛 ValueError。','def split_heads(x, heads)',
 'def split_heads(x,heads):\n    b,t,d=x.shape\n    if heads<=0 or d%heads:\n        raise ValueError("invalid head count")\n    return x.reshape(b,t,heads,d//heads).permute(0,2,1,3)',
 [case('split_heads(torch.arange(8).reshape(1,2,4),2)',[[[[0,1],[4,5]],[[2,3],[6,7]]]],label='数值顺序'),case('list(split_heads(torch.zeros(2,3,8),4).shape)',[2,4,3,2],label='输出形状'),case('split_heads(torch.zeros(1,2,3),2)',raises='ValueError',label='不能整除'),case('split_heads(torch.zeros(1,2,4),0)',raises='ValueError',label='非法head数')],
 quiz('reshape(B,H,T,D/H) 能直接替代拆维再 permute 吗？',['总能，形状相同就行','不能，元素对应的语义轴可能被打乱','只在B大于1时报错'],1,['形状相同不代表元素归属相同。','对，用编号张量能暴露这种静默错误。','错误可能不报异常。']),
 examples=[example('轴交换不是重排形状','x=torch.arange(6).reshape(2,3)\nprint(x.T.tolist())\nprint(x.reshape(3,2).tolist())','[[0, 3], [1, 4], [2, 5]]\n[[0, 1], [2, 3], [4, 5]]','转置与reshape的结果不同。'),example('head宽度','d=12;heads=3\nprint(d//heads)','4','每个头拥有4个特征。')],minutes=25)
add('pt10',8,'手写缩放点积注意力',3,'挑战',
 '注意力先计算每个query与全部key的匹配分数，除以 sqrt(D)，沿key轴归一化，再加权求value。key长度与query长度可以不同，value特征宽度也可以不同。',
 'q=torch.ones(1,2,3)\nk=torch.ones(1,4,3)\nprint(list((q@k.transpose(-1,-2)).shape))',
 ['分数是 q@k.transpose(-1,-2)/sqrt(D)，形状 [B,Tq,Tk]。','softmax 必须沿最后的key维，再与 v 相乘。','检查 Tq≠Tk 与 Dv≠D 的情况，不能依赖全部维度恰好相同。'],
 '定义 attention(q,k,v)，输入 [B,Tq,D]、[B,Tk,D]、[B,Tk,Dv]，返回 [B,Tq,Dv]。手写缩放、softmax和矩阵乘法，不调用现成注意力函数。','def attention(q, k, v)',
 'def attention(q,k,v):\n    scores=q@k.transpose(-1,-2)/(q.shape[-1]**0.5)\n    return torch.softmax(scores,dim=-1)@v',
 [case('attention(torch.zeros(1,2,3),torch.ones(1,4,3),torch.tensor([[[1.,2.],[3.,4.],[5.,6.],[7.,8.]]]))',[[[4,5],[4,5]]],label='均匀注意力与异维'),case('torch.allclose(attention(q,k,v),torch.nn.functional.scaled_dot_product_attention(q,k,v),atol=1e-5)',True,setup='torch.manual_seed(4)\nq=torch.randn(2,3,4)\nk=torch.randn(2,5,4)\nv=torch.randn(2,5,6)',label='非方形对照'),case('attention(q,k,v).requires_grad',True,setup='q=torch.randn(1,2,3,requires_grad=True)\nk=torch.randn(1,4,3)\nv=torch.randn(1,4,2)',label='梯度连通')],
 quiz('softmax 为什么必须沿 key 轴？',['要为每个query在全部key之间分配权重','因为batch轴必须求和为1','因为value维度必须等于key长度'],0,['对，每个query对应一份key权重分布。','不同样本之间不应互相归一化。','Dv 与 key 长度可以不同。']),
 examples=[example('权重和为1','s=torch.tensor([[1.,2.,3.]])\nprint(torch.softmax(s,-1).sum(-1))','tensor([1.])','每个query的一组key权重归一化。'),example('批量矩阵乘法','a=torch.ones(2,3,4);b=torch.ones(2,4,5)\nprint(list((a@b).shape))','[2, 3, 5]','相同batch中的矩阵分别相乘。')],minutes=35)

existing('t3',9,1,15)
add('pt11',9,'区分累积与清空梯度',2,'排错',
 'backward 把新梯度加到叶子张量的 .grad 中，而不是覆盖。两份独立前向图可以先后反向，得到梯度总和；要比较单独一次的梯度，必须清空旧值并重新前向。',
 'x=torch.tensor(2.,requires_grad=True)\n(x**2).backward()\n(3*x).backward()\nprint(x.grad)',
 ['创建浮点叶子x；先对x² backward，再对3x的独立新图 backward，记录累计梯度。','将 x.grad 置为 None 或清零，再重新计算 x² 并 backward。','返回累计梯度与清空后的梯度。不要对已经释放的同一图反复 backward。'],
 '定义 gradient_stages(value)，完成上述步骤，返回 (累计梯度,清空后仅x²的梯度)，均为Python数值。','def gradient_stages(value)',
 'def gradient_stages(value):\n    x=torch.tensor(float(value),requires_grad=True)\n    (x**2).backward()\n    (3*x).backward()\n    accumulated=x.grad.item()\n    x.grad=None\n    (x**2).backward()\n    return accumulated,x.grad.item()',
 [case('gradient_stages(2)',[7,4],label='正确累计'),case('gradient_stages(0)',[3,0],label='零点'),case('gradient_stages(-2)',[-1,-4],label='负梯度')],
 quiz('连续两次对独立前向图 backward，不清空.grad，会怎样？',['第二次覆盖第一次','梯度相加','总会报图已释放'],1,['默认是累加。','对，梯度累积可用于大batch模拟，但也容易误用。','独立新图可分别反向，重复旧图才有释放问题。']),
 bug='x=torch.tensor(2.,requires_grad=True)\ny=x**2\ny.backward()\ny.backward()',examples=[example('梯度相加','x=torch.tensor(2.,requires_grad=True)\n(x*3).backward()\n(x*4).backward()\nprint(x.grad.item())','7.0','两份图的贡献加在一起。'),example('清空后重新前向','x=torch.tensor(2.,requires_grad=True)\n(x*3).backward()\nx.grad=None\n(x*4).backward()\nprint(x.grad.item())','4.0','清空状态后只剩本次贡献。')],minutes=25)
add('pt12',9,'修复被重新包装断开的图',2,'排错',
 'torch.tensor(existing_tensor) 会复制数据并建立新张量，原来的计算图关系不会保留。用 stack 合并现有标量张量，或者直接保留张量运算，才会让梯度回到原输入。',
 'x=torch.tensor([1.,2.],requires_grad=True)\ny=(x*x).sum()\ny.backward()\nprint(x.grad)',
 ['求 sum(x_i²) 时直接使用 x.square().sum()。','如果逐项生成标量张量，应使用 torch.stack 而不是 torch.tensor(list_of_tensors)。','返回一维张量的梯度值，不能只手写解析导数，必须通过 backward 得到。'],
 '定义 square_grad(values)，values为数值列表，用真实 autograd 计算 sum(x²) 对 x 的梯度，返回梯度张量。修复下面重新包装张量的错误。','def square_grad(values)',
 'def square_grad(values):\n    x=torch.tensor(values,dtype=torch.float64,requires_grad=True)\n    loss=x.square().sum()\n    loss.backward()\n    return x.grad',
 [case('square_grad([1,2,-3])',[2,4,-6],label='梯度正确'),case('square_grad([0])',[0],label='零梯度'),case('square_grad([])',[],label='空向量'),case('isinstance(square_grad([1]),torch.Tensor)',True,label='返回梯度张量')],
 quiz('把张量列表交给 torch.tensor(...) 后，原图通常会怎样？',['始终保留','数据被重新包装，原图关系可能断开','自动调用 backward'],1,['这不是保留图的组合方式。','对，需要 stack 等可微张量运算。','构造张量不等于反向传播。']),
 bug='def square_grad(values):\n    x=torch.tensor(values,dtype=torch.float32,requires_grad=True)\n    loss=torch.tensor([v*v for v in x]).sum()\n    loss.backward()\n    return x.grad',examples=[example('stack 保留关系','x=torch.tensor(2.,requires_grad=True)\ny=torch.stack([x,x*2]).sum()\ny.backward()\nprint(x.grad.item())','3.0','两个分支的梯度都回到x。'),example('item 用于报告，不用于损失图','x=torch.tensor(2.,requires_grad=True)\nprint(type(x.item()).__name__)','float','转成Python数值后，不再携带计算图。')],minutes=25)
add('pt13',9,'用有限差分核对 autograd',2,'实现',
 '中心差分 [f(x+eps)-f(x-eps)]/(2eps) 可以近似导数。它适合核对自定义损失，不用于替代高效的反向传播。float64 能减少小步长下的相消误差。',
 'x=torch.tensor(1.2,dtype=torch.float64)\neps=1e-5\nf=lambda z:z**3\nprint(((f(x+eps)-f(x-eps))/(2*eps)).item())',
 ['函数固定为 f(x)=x³+2x²-4x。用float64、requires_grad=True计算精确autograd梯度。','另用中心差分和传入的正eps估计导数。','返回 (autograd梯度,数值梯度)，两者均为Python数值，不能直接代入解析公式。'],
 '定义 check_gradient(value,eps=1e-5)，核对多项式 x³+2x²-4x 的自动微分与中心差分。','def check_gradient(value, eps=1e-5)',
 'def check_gradient(value,eps=1e-5):\n    x=torch.tensor(float(value),dtype=torch.float64,requires_grad=True)\n    f=lambda z:z**3+2*z**2-4*z\n    f(x).backward()\n    numerical=((f(x.detach()+eps)-f(x.detach()-eps))/(2*eps)).item()\n    return x.grad.item(),numerical',
 [case('check_gradient(2)',[16,16],label='正数'),case('check_gradient(0)',[-4,-4],label='原点'),case('check_gradient(-1)',[-5,-5],label='负数'),case('abs(a-b)<1e-5',True,setup='a,b=check_gradient(1.234)',label='一般浮点值')],
 quiz('有限差分的 eps 越小一定越准确吗？',['一定','不一定，太小会增加浮点相消误差','eps 必须等于1'],1,['浮点精度有限。','对，需要在近似误差与舍入误差间取平衡。','通常使用更小步长。']),
 examples=[example('前后两点','x=2.;e=0.001\nprint(((x+e)**2-(x-e)**2)/(2*e))','约4.0','对x²的中心差分接近2x。'),example('选择更高精度','x=torch.tensor(1.2,dtype=torch.float64)\nprint(x.dtype)','torch.float64','检查梯度时可以用双精度降低误差。')],minutes=25)
add('pt14',9,'按全局范数裁剪梯度',3,'挑战',
 '全局范数把全部参数梯度当成一个长向量，先计算L2范数，再统一缩放。逐个元素截断或逐个参数各自归一化，都不是相同操作。没有梯度的参数应跳过。',
 'grads=[torch.tensor([3.]),torch.tensor([4.])]\nnorm=torch.sqrt(sum((g*g).sum() for g in grads))\nprint(norm.item())',
 ['先收集 grad is not None 的梯度，计算合并L2范数。','系数 min(1,max_norm/(total_norm+1e-6))；用 no_grad 原地乘到所有有效grad。','返回裁剪前范数。max_norm≥0；没有梯度时返回0，不修改参数值。不能调用现成 clip_grad_norm_。'],
 '定义 clip_gradients(parameters,max_norm)，实现上述全局范数裁剪并返回裁剪前Python范数。','def clip_gradients(parameters, max_norm)',
 'def clip_gradients(parameters,max_norm):\n    grads=[p.grad for p in parameters if p.grad is not None]\n    if not grads:\n        return 0.0\n    total=torch.sqrt(sum((g*g).sum() for g in grads))\n    scale=min(1.0,max_norm/(total.item()+1e-6))\n    with torch.no_grad():\n        for g in grads:\n            g.mul_(scale)\n    return total.item()',
 [case('norm',5,setup='a=torch.nn.Parameter(torch.tensor([1.]));b=torch.nn.Parameter(torch.tensor([2.]))\na.grad=torch.tensor([3.]);b.grad=torch.tensor([4.])\nnorm=clip_gradients([a,b],1)',label='返回原范数'),case('[a.grad.item(),b.grad.item()]',[0.6,0.8],setup='a=torch.nn.Parameter(torch.tensor([1.]));b=torch.nn.Parameter(torch.tensor([2.]))\na.grad=torch.tensor([3.]);b.grad=torch.tensor([4.])\nclip_gradients([a,b],1)',label='统一缩放'),case('clip_gradients([torch.nn.Parameter(torch.ones(2))],1)',0,label='没有梯度'),case('p.item()',7,setup='p=torch.nn.Parameter(torch.tensor(7.));p.grad=torch.tensor(9.)\nclip_gradients([p],1)',label='不能修改参数')],
 quiz('梯度分别为3和4，全局L2范数是多少？',['7','5','4'],1,['7是绝对值之和。','对，sqrt(3²+4²)=5。','4只是最大单项。']),
 examples=[example('全局与逐项区别','print((3**2+4**2)**0.5)','5.0','全部参数的梯度共同参与范数。'),example('原地改梯度','g=torch.tensor([3.,4.])\ng.mul_(0.2)\nprint(g)','tensor([0.6000, 0.8000])','两个分量按相同比例缩小。')],minutes=30)
add('pt15',9,'梯度累积也要按样本数加权',3,'排错',
 '多个micro-batch模拟一个大batch时，若每批使用mean loss，应该乘以本批样本数/总样本数后再backward。简单除以批次数，只在所有批次同样大时才等价。',
 'sizes=[3,1]\nweights=[n/sum(sizes) for n in sizes]\nprint(weights)',
 ['w为从0开始的浮点叶子。每批预测w*x，均方误差先求sum，再除全部样本总数。','遍历micro-batch累计梯度，中途不能清空；至少包含一个样本。','返回w.grad.item()。测试包含不等批次大小，不能对各批均值简单平均。'],
 '定义 accumulated_mse_grad(batches)，每项为 (x_tensor,y_tensor)，一维且非空。对整体 MSE 在 w=0、pred=w*x 处计算梯度，使用逐批 backward 累积。','def accumulated_mse_grad(batches)',
 'def accumulated_mse_grad(batches):\n    w=torch.tensor(0.,requires_grad=True)\n    total=sum(x.numel() for x,y in batches)\n    for x,y in batches:\n        loss=((w*x-y)**2).sum()/total\n        loss.backward()\n    return w.grad.item()',
 [case('accumulated_mse_grad([(torch.tensor([1.,1.,1.]),torch.zeros(3)),(torch.tensor([2.]),torch.tensor([4.]))])',-4,label='不等批次大小'),case('accumulated_mse_grad([(torch.tensor([1.,2.]),torch.tensor([2.,4.]))])',-10,label='单批对照'),case('accumulated_mse_grad([(torch.tensor([1.]),torch.tensor([2.])),(torch.tensor([2.]),torch.tensor([4.]))])',-10,label='不同拆分结果相同')],
 quiz('3项和1项的两个micro-batch，其mean loss权重应该是？',['各1/2','3/4和1/4','各1'],1,['批次大小不相同。','对，要对应每个样本相同权重。','这样总权重变成2。']),
 bug='for x,y in batches:\n    loss=((w*x-y)**2).mean()/len(batches)\n    loss.backward()',examples=[example('按样本数分配','print(3/(3+1),1/(3+1))','0.75 0.25','小批次不应被过度加权。'),example('sum形式更直接','errors=torch.tensor([1.,9.])\nprint(errors.sum()/2)','tensor(5.)','每批总和最终除总样本数。')],minutes=30)

exec((ROOT/'curriculum/finish.py').read_text(encoding='utf-8'),globals())
