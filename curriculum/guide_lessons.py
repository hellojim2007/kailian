"""72 authored lesson handovers; small programs precede independent tasks."""
import textwrap
GUIDES = {}
def guide(ident, keys, before, reason, steps, prompt, code, expected):
    GUIDES[ident] = dict(apiKeys=keys.split(), requires=before.split(), reason=reason,
        steps=steps.split('|'), warmup=dict(prompt=prompt, code=textwrap.dedent(code).strip()+'\n', expected=expected))

guide('p1','values','',
 '先建立“计算一个表达式、保存结果、输出”的完整程序，不引入循环或函数定义。',
 '写一条赋值保存初值，暂不使用 input。|下一行读取旧值并加上增量，把结果重新赋给同一个名字。|最后 print 变量，而不是把期望答案写成常量；改初值后应仍然成立。',
 '创建 balance=23，增加 7，再输出 balance。写完整程序，只输出结果。',
 'balance = 23\nbalance += 7\nprint(balance)', '30')
guide('py01','list input arithmetic','p1',
 '先把一行字符串拆开，再分别转换数值；不把 map、解包等简写当作已经会的知识。',
 '用 input() 读一行；parts=input().split() 得到两个字符串。|用 a=int(parts[0])、b=int(parts[1]) 分别转换，然后计算三个表达式。|print 的多个实参默认用空格分隔；不要额外输出输入提示。',
 '给定 text="23 4"，分别转成整数，输出它们的和、整除商、余数，用空格分隔。',
 'text = "23 4"\nparts = text.split()\na = int(parts[0])\nb = int(parts[1])\nprint(a+b, a//b, a%b)', '27 5 3')
guide('py02','branch arithmetic','py01',
 '把取值范围翻译成互不遗漏的分支。先用单个值手算，再读取真正输入。',
 '先处理小于0或大于100的非法范围。|有效输入再按90、60这两个下界从高到低检查。|每条路径只输出一次；用59、60、89、90检查边界。',
 '给定 score=90，90及以上输出 high，否则输出 low。写 if/else，不直接打印已知答案。',
 'score = 90\nif score >= 90:\n    print("high")\nelse:\n    print("low")', 'high')
guide('p3','for list','py02',
 '复用已经会的加法，把同一条操作交给每个元素。先理解缩进，再考虑更短写法。',
 '用方括号创建分数列表。|for 的循环变量每轮拿到一个分数；把 print(score+5) 放在缩进中。|在纸上分别写出每一轮的变量值；本题不要求修改列表。',
 '遍历 values=[2,4,7]，每个数乘3后输出，各占一行。',
 'values = [2,4,7]\nfor value in values:\n    print(value*3)', '6\n12\n21')
guide('py03','range for arithmetic','p3',
 '把枚举范围、筛选条件、累计结果拆成三件小事，不要求先想出数学公式。',
 'total=0 放循环前，n=0时它也应有定义。|遍历range(1,n+1)，用value%2==0识别偶数，再累加。|循环后只print一次总和；终点n本身是否需要被检查要明确。',
 '用 range 遍历1到8（包含8），累加其中的偶数并只输出总和。',
 'total=0\nfor value in range(1,9):\n    if value%2==0:\n        total+=value\nprint(total)', '20')
guide('py04','while for input','py03',
 '先写易检查的遍历与结束标记；while是控制状态的工具，不必为了题名强行改掉可读的for。',
 '先把分词得到的字符串逐个int转换，或在遍历时转换。|每轮先检查是否负数，成立立即break，之后才加到total。|没有数据或首项就是负数时，不会发生累计，输出初始0。',
 '对values=[4,6,-2,99]，使用while与索引i累加第一个负数前的数字并输出；需要维护i避免死循环。',
 'values=[4,6,-2,99]\ntotal=0\ni=0\nwhile i<len(values):\n    if values[i]<0:\n        break\n    total+=values[i]\n    i+=1\nprint(total)', '10')
guide('p2','list slice','p3',
 '把“第几个元素”和“索引是多少”分清，后续函数会反复使用len与切片。',
 '先创建列表，再分别读取长度和最后一项。|最后一项可用xs[-1]，不需要把长度减1再手算常量。|本题保证列表非空；空列表索引是另一种需要提前处理的契约。',
 '创建 xs=[9,18,27,36]，第一行输出长度，第二行输出最后一项。',
 'xs=[9,18,27,36]\nprint(len(xs))\nprint(xs[-1])', '4\n36')
guide('p4','function mean','p2',
 '推荐路线把这一课提前，先系统学会def、调用和return，再写切片与文本函数。',
 '先写def mean(values):及缩进的函数体；参数来自调用者。|把sum、len和除法分成有名字的中间变量，再return结果。|用print(mean([...] ))在函数外自测；这里保证输入非空，不自行改变接口。',
 '定义double(value)，返回value的两倍。在函数外依次输出double(6)和double(-2)。',
 'def double(value):\n    return value*2\nprint(double(6))\nprint(double(-2))', '12\n-4')
guide('py05','function slice','p4 p2',
 '在已经会写函数后，只增加切片和外层副本这两个知识点。',
 '函数头的xs、n由调用者提供，不再input。|先用xs[:n]取得结果，再return；不需要自己写边界裁剪循环。|通过修改返回列表检查原列表没有被改动；只要求外层独立，不要求深复制。',
 '定义tail(xs)，返回xs[1:]。用[3,6,9]调用，把返回列表首项改成100，分别输出原列表和结果。',
 'def tail(xs):\n    return xs[1:]\na=[3,6,9]\nb=tail(a)\nb[0]=100\nprint(a)\nprint(b)', '[3, 6, 9]\n[100, 9]')
guide('py06','string split chain function','p4 py05',
 '先分别练会方法的调用方式和返回类型，再组合为一个文本函数。本课只统一大小写、按空白分词，不删除标点。',
 '先在函数外写lowered=text.lower()，观察得到新字符串、原text仍不变。|再写words=lowered.split()，观察返回列表；用制表符、连续空格和全空白分别验证。|把两步移入def tokenize(text):，最后return words；熟练后才改成链式表达式。|不要增加未要求的去标点规则。默认split已经忽略两端空白，因此strip可用于理解，但不是这里的必要步骤。',
 '定义words(text)：先转小写，再按任意空白分词，返回列表。用"  GREEN\\tTea!  "（含制表符）调用并print返回值。',
 'def words(text):\n    lowered=text.lower()\n    result=lowered.split()\n    return result\nprint(words("  GREEN\tTea!  "))', "['green', 'tea!']")
guide('py07','slice range mean raise','py05 p4 py13',
 '这是进阶回访：同时维护窗口边界和异常规则。先会单个切片均值，再枚举所有完整窗口。',
 '先排除k<=0并raise；k大于长度时没有窗口。|一个窗口是xs[start:start+k]，合法start从0到len(xs)-k。|每轮计算该窗口均值并append；不要把相邻窗口的元素平均混在一起。',
 '给定xs=[2,4,8,10]、k=2，依次输出每个完整窗口的和，各占一行。',
 'xs=[2,4,8,10]\nk=2\nfor start in range(len(xs)-k+1):\n    print(sum(xs[start:start+k]))', '6\n12\n18')
guide('py08','set for','py05',
 '引入集合只解决“是否见过”，输出顺序仍交给列表维护。',
 '在循环前创建seen=set()、result=[]。|仅在value不属于seen时，同时add到集合并append到结果。|返回result，不直接返回集合，也不排序；不能修改输入列表。',
 '对[3,1,3,2,1]用集合和列表保留首次出现顺序，输出结果列表。',
 'seen=set()\nresult=[]\nfor value in [3,1,3,2,1]:\n    if value not in seen:\n        seen.add(value)\n        result.append(value)\nprint(result)', '[3, 1, 2]')
guide('py09','nested tuplezip comprehension','py07 py08',
 '这是序列综合回访：把原长度、补充值和有效性分开；不要求首次接触列表时就实现二维批处理。',
 '先算每行原长度，再求最大长度；空批次明确返回两个空列表。|每次循环创建新的补齐行和mask行，原长度范围为True，补齐范围为False。|合法零token也必须被标为True；最后返回二元元组而不是只返回补齐数据。',
 '给定rows=[[0,2],[3]]，右补到宽度2，分别输出补齐列表与按原长度生成的mask。',
 'rows=[[0,2],[3]]\npadded=[]\nmasks=[]\nfor row in rows:\n    padded.append(row[:]+[0]*(2-len(row)))\n    masks.append([True]*len(row)+[False]*(2-len(row)))\nprint(padded)\nprint(masks)', '[[0, 2], [3, 0]]\n[[True, True], [True, False]]')
guide('py10','default for comprehension','p4 py05',
 '先用普通循环写清逐元素变换，再认识默认参数与等价推导式；不要求一步背出最短代码。',
 '函数头列出factor=1、bias=0，省略时才用默认值。|创建新结果列表，依次append(value*factor+bias)。|用位置参数、关键字参数、factor=0三个调用核查规则。',
 '定义shift(xs, amount=1)，返回每项加amount的新列表。输出shift([2,5])与shift([2,5],amount=3)。',
 'def shift(xs,amount=1):\n    result=[]\n    for value in xs:\n        result.append(value+amount)\n    return result\nprint(shift([2,5]))\nprint(shift([2,5],amount=3))', '[3, 6]\n[5, 8]')
guide('p6','tuplezip function mean','p4 py10',
 '先把一对样本比较清楚，再把多对比较累计为比例；不需要复杂可视化才能理解这个计数过程。',
 '双空时提前return 0.0，避免零分母。|for pred,label in zip(...)解包配对，用相等判断累计正确次数。|循环后除以总样本数；两列表等长是本题保证，不把zip截断当成额外功能。',
 '遍历preds=[1,0,0,1]与labels=[1,1,0,1]，输出正确数和总数，用空格隔开。',
 'preds=[1,0,0,1]\nlabels=[1,1,0,1]\ncorrect=0\nfor pred,label in zip(preds,labels):\n    if pred==label:\n        correct+=1\nprint(correct,len(labels))', '3 4')
guide('py11','generator slice range raise','py09 py13',
 '这是惰性执行回访：除了分批，还需要理解函数体何时开始运行。',
 '检查batch_size后，按range(0,len(xs),batch_size)生成每批起点。|每轮yield一个xs[start:start+batch_size]的新列表。|保留末尾不足一批；用list(batches(...))消费并检查异常发生在迭代时。',
 '定义parts()，用yield依次产出[1,2]和[3]。创建生成器g，连续两次print(list(g))。',
 'def parts():\n    yield [1,2]\n    yield [3]\ng=parts()\nprint(list(g))\nprint(list(g))', '[[1, 2], [3]]\n[]')
guide('py12','none default list','py10 py05',
 '复习默认参数，但这次关注可变对象的生命周期；有意原地修改与意外共享要分开。',
 '把默认值改为None，用is None判断未提供。|仅在未提供时新建列表；显式传入的空列表也必须沿用。|append后return同一个列表，分别测试两次省略参数和一次显式列表调用。',
 '定义collect(x, history=None)，按本课规则追加并返回。输出collect(5)、collect(8)，各一行。',
 'def collect(x,history=None):\n    if history is None:\n        history=[]\n    history.append(x)\n    return history\nprint(collect(5))\nprint(collect(8))', '[5]\n[8]')
guide('py13','raise finite mean','py19 p4',
 '推荐路线先练异常捕获，再要求主动拒绝非法输入；不能只检查普通负数而漏掉NaN。',
 '空输入先raise ValueError。|逐项检查0<=value<=1是否成立，取反处理非法值；NaN不会满足合法区间。|通过全部检查后才求均值；不要遇到非法值就返回None，那是另一类接口。',
 '定义valid(x)，若x不满足0<=x<=1则raise ValueError，否则return x。打印valid(0.5)，再捕获valid(2)的ValueError并输出bad。',
 'def valid(x):\n    if not 0<=x<=1:\n        raise ValueError("range")\n    return x\nprint(valid(0.5))\ntry:\n    valid(2)\nexcept ValueError:\n    print("bad")', '0.5\nbad')
guide('p5','dict for branch','p6',
 '第一次把每条记录作为字典读取。先练d[key]，再把字段判断放入循环。',
 'records是一组字典，不是字典本身；循环变量每次是一条记录。|读取record["loss"]，严格小于threshold才计数。|count在循环外初始化，结束后return；空列表自然返回0。',
 'records=[{"loss":0.2},{"loss":0.5},{"loss":0.8}]，统计loss严格小于0.5的记录数并print。',
 'records=[{"loss":0.2},{"loss":0.5},{"loss":0.8}]\ncount=0\nfor record in records:\n    if record["loss"]<0.5:\n        count+=1\nprint(count)', '1')
guide('py14','dict for','p5',
 '从一个计数器扩展到“每个标签一个计数器”；关键是第一次出现时的默认值。',
 'result={}创建空字典。|每轮用result.get(label,0)+1计算该标签新次数。|返回字典，不返回只包含计数的列表；空输入对应空字典。',
 '对["x","y","x","x"]统计次数，输出结果字典。',
 'counts={}\nfor label in ["x","y","x","x"]:\n    counts[label]=counts.get(label,0)+1\nprint(counts)', "{'x': 3, 'y': 1}")
guide('py15','group dict mean','py14',
 '复用标签计数，再增加每组总和；先用两张普通字典，不急着引入复杂容器。',
 '每条记录取model、loss，为该组分别累计总和与次数。|第二次遍历组名，计算各自total/count。|返回新结果字典；不同组数量不同时也要各除各的次数。',
 '对[("a",2),("b",8),("a",6)]分别累计每组总和，print总和字典，暂时不求均值。',
 'totals={}\nfor name,value in [("a",2),("b",8),("a",6)]:\n    totals[name]=totals.get(name,0)+value\nprint(totals)', "{'a': 8, 'b': 8}")
guide('py16','sort function slice','py15',
 '先用def写排序键，再学习lambda简写；重点是双关键字与平局规则。',
 '定义key函数返回(-score,name)，分别控制降序和升序。|sorted新建排序列表，随后[:k]截取并提取name。|k=0要返回[]，原records不能排序修改；同分时必须按name确定顺序。',
 '给定rows=[("z",2),("a",2),("m",3)]，用sorted按分数降序、名称升序，print完整排序列表。',
 'rows=[("z",2),("a",2),("m",3)]\ndef order(row):\n    return (-row[1],row[0])\nprint(sorted(rows,key=order))', "[('m', 3), ('a', 2), ('z', 2)]")
guide('py17','copy dict function','py24 py12',
 '递归与深复制放在进阶回访；先区分合并规则与独立存储，再处理嵌套。',
 '先深复制默认配置，避免改原输入。|覆盖某键时，仅当双方值都是字典才递归合并，否则整体替换为覆盖值的深副本。|新增覆盖键也需要复制；通过修改结果内层列表检查两份输入均不受影响。',
 '用deepcopy复制cfg={"sizes":[2,4]}，向副本的sizes追加8，分别输出原配置和副本。',
 'import copy\ncfg={"sizes":[2,4]}\nout=copy.deepcopy(cfg)\nout["sizes"].append(8)\nprint(cfg)\nprint(out)', "{'sizes': [2, 4]}\n{'sizes': [2, 4, 8]}")
guide('py18','finite sort dict','py17 py19',
 '这是筛选与排序的综合回访：合法性检查先于取最小值。',
 'status必须为ok；loss字段存在，类型恰为int或float且有限。|在有效记录里比较(loss,epoch)，先最小loss，再最早epoch。|无有效项返回None；返回的是epoch而不是记录对象或loss。',
 '从values=[True,0.2,float("inf"),0.0]筛选非bool的有限int/float，print筛选列表。',
 'import math\nvalues=[True,0.2,float("inf"),0.0]\nvalid=[]\nfor value in values:\n    if type(value) in (int,float) and math.isfinite(value):\n        valid.append(value)\nprint(valid)', '[0.2, 0.0]')
guide('py19','except finite function','py16',
 '先练最常见的ValueError捕获，区分“解析失败”与“解析成功但业务值非法”。',
 'try里仅做float(text)转换，except ValueError返回None。|转换后检查有限性与[0,1]区间，非法返回None。|正常时返回float；不要用except把自己代码的任意错误都掩盖。',
 '遍历["0.25","oops"]，能float转换则print数值，捕获ValueError时print bad。',
 'for text in ["0.25","oops"]:\n    try:\n        value=float(text)\n    except ValueError:\n        print("bad")\n    else:\n        print(value)', '0.25\nbad')
guide('py20','filejson dict','py13 py19',
 '先分清JSON字符串和文件对象。文件读取范式单独教，不让临时测试文件的搭建掩盖核心API。',
 'import json，使用with open(path,encoding="utf-8")取得文件对象。|json.load(handle)解析为字典，读取必需name和带默认值的lr。|构造只包含规定两个字段的新字典并返回；本题不吞文件或JSON错误。',
 '用json.loads读取字符串{\"name\":\"trial\"}，输出name与缺失lr的默认值0.001，用空格隔开。',
 'import json\ncfg=json.loads(\'{"name":"trial"}\')\nprint(cfg["name"],cfg.get("lr",0.001))', 'trial 0.001')
guide('py21','csv filejson mean','py20',
 '已有文件读取经验后，只增加CSV格式与字段转换；先用内存文件观察引号规则。',
 '用with open(path,newline="",encoding="utf-8")读取，交给csv.DictReader。|逐行把row["loss"]转float并累计，同时统计行数。|有数据返回均值，没数据返回None；带逗号的名称不应影响列对应。',
 '使用csv.DictReader和io.StringIO读取文本name,loss换行"red,blue",0.7换行。print第一行name字段。',
 'import csv\nimport io\nrows=csv.DictReader(io.StringIO(\'name,loss\\n"red,blue",0.7\\n\'))\nfor row in rows:\n    print(row["name"])', 'red,blue')
guide('py22','jsonl except dict','py20 py21',
 '把错误处理范围缩小到每一行，让一行坏日志不会丢掉所有好记录。',
 '每行先strip判断是否空白，空白直接continue。|对这一行json.loads，格式错误累计bad并继续。|成功后再判定是否字典；合格append，否则也累计bad，最后返回二元组。',
 '对lines=[\'{"ok":true}\',"bad","[]"]逐行json.loads，成功时print类型名称，格式失败时print bad。',
 'import json\nfor line in [\'{"ok":true}\',"bad","[]"]:\n    try:\n        value=json.loads(line)\n    except json.JSONDecodeError:\n        print("bad")\n    else:\n        print(type(value).__name__)', 'dict\nbad\nlist')
guide('py23','assert finite nested','py22 py13',
 '先学每一条结构断言的安全顺序，再组成完整数据契约；不把布尔值偷当整数标签。',
 '验证外层是列表/元组，且行数等于标签数。|逐行验证容器与等宽，再逐元素验证内置数值类型并排除bool。|逐标签验证内置int且非负；通过后return True，空结构按任务约定处理。',
 '定义check_labels(xs)，断言每项type是int且>=0，合法返回True。输出check_labels([0,2])，再捕获[True]的AssertionError输出bad。',
 'def check_labels(xs):\n    for x in xs:\n        assert type(x) is int and x>=0\n    return True\nprint(check_labels([0,2]))\ntry:\n    check_labels([True])\nexcept AssertionError:\n    print("bad")', 'True\nbad')
guide('py24','jsonl group finite filejson','py23 py15',
 '这是Python主线的小型项目。先跑通读取、过滤、统计三个独立步骤，再接文件输出。',
 '按JSONL规则逐行解析，坏行与不符合字段要求的记录跳过。|按model累计count、total_loss和best_loss，最后算mean_loss。|with open(output_path,"w",encoding="utf-8")和json.dump覆盖写；同时return同一份报告结果。',
 'records=[{"model":"a","loss":2.0},{"model":"a","loss":4.0}]，用循环统计count与total，print次数和均值。',
 'records=[{"model":"a","loss":2.0},{"model":"a","loss":4.0}]\ncount=0\ntotal=0.0\nfor row in records:\n    count+=1\n    total+=row["loss"]\nprint(count,total/count)', '2 3.0')
guide('py25','class weighted','py23 p4',
 '第一次独立写类，先把对象初始化、方法调用与跨调用状态逐项讲清；加权统计不是新数学。',
 '在__init__里初始化total和count，reset也恢复这两个状态。|update(value,n)累加value*n和n，不能每次覆盖历史总量。|compute根据count返回0.0或total/count；用两个实例验证不共享状态。',
 '定义Count类：初始化n=0，add(value)把value累加到self.n。创建对象依次add(2)、add(5)，print对象n。',
 'class Count:\n    def __init__(self):\n        self.n=0\n    def add(self,value):\n        self.n+=value\nc=Count()\nc.add(2)\nc.add(5)\nprint(c.n)', '7')
guide('py26','class weighted tuplezip','py25 p6',
 '把函数版accuracy变成可多批累计的对象；复用正确数和样本数，不累计批次比例。',
 '初始化correct和total。|update先检查两列表等长，再配对统计；累计到self属性中。|compute对总正确数除总样本数；小批次与大批次应按样本数自然加权。',
 '两批(correct,total)分别为(1,1)、(1,3)，累计整数后输出整体准确率。',
 'correct=0\ntotal=0\nfor c,n in [(1,1),(1,3)]:\n    correct+=c\n    total+=n\nprint(correct/total)', '0.5')
guide('py27','protocol class slice','py25 py05',
 '先在普通Python对象里练好len和索引协议，再迁移到PyTorch Dataset。',
 '构造时检查长度一致，并逐行复制features。|__len__返回样本数量，__getitem__返回(特征行副本,标签)。|构造复制与取出复制缺一不可；本题元素是不可变数值，行切片足够。',
 '定义PairData类，__len__返回2，__getitem__(i)从[10,20]读取。print len(obj)和obj[1]。',
 'class PairData:\n    def __len__(self):\n        return 2\n    def __getitem__(self,i):\n        return [10,20][i]\nobj=PairData()\nprint(len(obj),obj[1])', '2 20')
guide('py28','state class','py25 py18',
 '提前停止是进阶状态题。先手算显著改善基准best、等待次数；min_delta>0时，这个best不等于每步都更新的最小loss。',
 '构造时验证patience>=1、min_delta>=0，非法抛ValueError；第一次输入建立best并清零等待。|仅loss<best-min_delta才更新best并清零bad_count；小幅下降达不到门槛时不更新best。|未显著改善就累计bad_count，达到patience后返回True。先用min_delta=0理解严格下降，再测试正min_delta。',
 '依次观察[1.0,0.8,0.9]，只在比历史best严格更小时更新best，并在每步print best。',
 'best=None\nfor loss in [1.0,0.8,0.9]:\n    if best is None or loss<best:\n        best=loss\n    print(best)', '1.0\n0.8\n0.8')
guide('py29','protocol function class','py27 py10',
 '函数可以像数值一样放入列表；可调用对象只是在已有类上增加__call__协议。',
 '构造时复制transforms外层列表，不提前执行变换。|__call__接收初值，按顺序把上一次结果交给下一个函数。|循环后返回最终值；无函数时返回原值，不能擅自排序函数列表。',
 '定义add1与double，把函数放入列表并按此顺序应用到3，print最终值。',
 'def add1(x):\n    return x+1\ndef double(x):\n    return x*2\nvalue=3\nfor function in [add1,double]:\n    value=function(value)\nprint(value)', '8')
guide('py30','set copy dict','py17 py24',
 '这是数据工程综合回访。组隔离、重复ID、顺序和深复制是四个可分别测试的规则。',
 'val_groups转集合用于成员判断；seen记录已经出现的sample_id。|重复ID先raise；根据group_id是否在验证组中分配整条记录。|按输入顺序append深副本，返回(train,val)，不要随机拆同一个组。',
 '记录[("a",1),("b",2),("c",1)]按group=1分到val，其余train，保持顺序并分别输出名称列表。',
 'train=[]\nval=[]\nfor name,group in [("a",1),("b",2),("c",1)]:\n    if group==1:\n        val.append(name)\n    else:\n        train.append(name)\nprint(train)\nprint(val)', "['b']\n['a', 'c']")

GUIDES['py06']['trace']=[
 dict(statement='text = "  PyTHon\\tLAB!  "',value="'  PyTHon\\tLAB!  '",kind='str',explanation='输入是一整段字符串；\\t表示一个制表符，不是两个词之间固定只有一个空格。'),
 dict(statement='lowered = text.lower()',value="'  python\\tlab!  '",kind='str',explanation='只改变字母大小写。两端空白、制表符与感叹号都还在；原text不变。'),
 dict(statement='words = lowered.split()',value="['python', 'lab!']",kind='list[str]',explanation='默认split识别任意连续空白，切成两个字符串并收在列表里，标点保留。'),
 dict(statement='return words',value="['python', 'lab!']",kind='list[str]',explanation='把列表交给函数调用者；只有外部print调用结果时才出现标准输出。'),
]
