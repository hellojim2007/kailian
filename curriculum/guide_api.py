"""Original, executable syntax notes. These are teaching notes, not copied text."""
import textwrap

API = {}

def card(key, title, syntax, body, code, output, source):
    API[key] = dict(key=key, title=title, syntax=syntax, body=body,
                    code=textwrap.dedent(code).strip()+'\n', output=output, source=source)

PY = 'https://docs.python.org/3/tutorial/'
TYPES = 'https://docs.python.org/3/library/stdtypes.html'
TORCH = 'https://docs.pytorch.org/docs/2.10/'

card('values','变量、表达式与输出','name = expression\nprint(value1, value2)',
 '等号先计算右侧，再把结果绑定给左侧名字。变量第一次赋值不用声明类型。数字不加引号，字符串加引号；# 后是注释。print 可以接多个值，默认以一个空格分隔并换行。x += 2 对数值相当于 x = x + 2；它不是数学等式，也不会让其他旧结果自动重算。',
 'x = 12\ny = x + 3\nx += 2\nprint(x, y)\nprint("x", x)', '14 15\nx 14', PY+'introduction.html#numbers')
card('input','从字符串输入得到数值','text = input()\nnumber = int(text)\nparts = text.split()',
 'input() 读入一行并返回 str，不包括末尾换行。int("12") 得到整数 12；float("1.5") 得到小数。输入一行两个数时，先 split 拆成字符串列表，parts[0]读第一项、parts[1]读第二项，再分别转换。后续看到list(map(int,parts))时，它表示逐个转换再收成列表，不是把整个列表一次传给int。题目评测通常不希望input中带提示语。',
 'text = "18 5"\nparts = text.split()\na = int(parts[0])\nb = int(parts[1])\nprint(a + b, a // b, a % b)', '23 3 3', 'https://cs50.harvard.edu/python/notes/0/')
card('arithmetic','除法、取余与比较','a / b   a // b   a % b\na == b   a < b   a <= b',
 '/ 返回真除法结果，整数相除也得到浮点数；// 向负无穷方向取整，不是简单截去小数；% 与 // 满足 a == (a//b)*b + a%b。比较返回 True/False。判断相等是 ==，赋值是 =；本课除数保证非零。',
 'print(9 / 2, 9 // 2, 9 % 2)\nprint(-9 // 2, -9 % 2)\nprint(4 == 4, 4 < 4)', '4.5 4 1\n-5 1\nTrue False', PY+'introduction.html#numbers')
card('branch','分支、布尔与缩进','if condition:\n    ...\nelif other_condition:\n    ...\nelse:\n    ...',
 '冒号后换行并缩进；同一层缩进表示同一个代码块。if/elif/else 只执行第一个成立的分支。and 表示同时成立，or 表示至少一个成立，not 表示取反。可以先排除非法输入，再按阈值从高到低或从低到高判断，避免范围重叠时提前截住。',
 'score = 64\nif score < 0 or score > 100:\n    print("invalid")\nelif score >= 60:\n    print("pass")\nelse:\n    print("fail")', 'pass', PY+'controlflow.html#if-statements')
card('for','遍历与累计','for value in values:\n    total += value',
 'for 直接遍历元素，不要求你自己维护下标。循环变量每轮绑定下一项；循环体统一缩进。累计变量要在循环前初始化，循环后读最终结果。修改循环变量不会自动替换原列表元素。append 是向列表末尾添加一个元素的原地方法，返回 None。',
 'values = [2, 5, 8]\ntotal = 0\nresult = []\nfor value in values:\n    total += value\n    result.append(value * 2)\nprint(total)\nprint(result)\nprint(values)', '15\n[4, 10, 16]\n[2, 5, 8]', PY+'controlflow.html#for-statements')
card('range','range 的三种调用','range(stop)\nrange(start, stop)\nrange(start, stop, step)',
 'start 默认 0，step 默认 1，stop 永不包含。range(2,8,2) 依次给出 2、4、6；step 可为负但不能为 0。它是可迭代对象，用 list(...) 才能直观看到全部值。想包含整数 n，正向循环通常写到 n+1。',
 'print(list(range(4)))\nprint(list(range(2, 9, 2)))\nprint(list(range(5, 0, -2)))', '[0, 1, 2, 3]\n[2, 4, 6, 8]\n[5, 3, 1]', PY+'controlflow.html#the-range-function')
card('while','while、break 与 continue','while condition:\n    ...\n    if stop:\n        break',
 'while 每轮执行前检查条件；循环体必须改变相关状态，否则可能永不结束。break 退出当前最内层循环；continue 跳过本轮余下语句。处理结束标记时，应先检查标记再把数值加入累计，避免误计标记本身。',
 'i = 0\ntotal = 0\nvalues = [4, 2, -1, 9]\nwhile i < len(values):\n    if values[i] < 0:\n        break\n    total += values[i]\n    i += 1\nprint(total)', '6', PY+'controlflow.html#break-and-continue-statements')
card('list','列表、长度与索引','xs = [a, b, c]\nlen(xs)\nxs[index]',
 '列表有顺序、可修改。长度为 n 时，正索引是 0 到 n-1；-1 是最后一项，-n 是第一项。xs[i] 读取元素，xs[i] = value 替换该位置；空列表没有最后一项，索引越界会抛 IndexError。len 是函数，写 len(xs)，不是 xs.len()。',
 'xs = [14, 28, 42]\nprint(len(xs), xs[0], xs[-1])\nxs[1] = 7\nprint(xs)', '3 14 42\n[14, 7, 42]', PY+'introduction.html#lists')
card('function','先定义，再调用，再接返回值','def function_name(parameter):\n    return expression\nresult = function_name(argument)',
 'def 是定义，括号内是形参，调用时传入的是实参。定义函数不会自动执行函数体；调用才执行。return 把值交给调用者，并立刻结束本次调用；没有 return 时结果是 None。函数题由评测调用你的函数，不需要额外 input。可先用 print(function_name(...)) 自测，但函数内部不能只 print 代替返回。',
 'def triple(number):\n    result = number * 3\n    return result\n\na = triple(4)\nprint(a)\nprint(triple(0))', '12\n0', PY+'controlflow.html#defining-functions')
card('mean','sum、len 与空输入','total = sum(values)\ncount = len(values)\nmean = total / count',
 'sum 把数值可迭代对象求和，空输入的和为 0；len 得元素个数。均值要除以元素数，而不是固定常数。空输入时 count=0，不能直接相除：是返回默认值还是抛异常，必须由本题契约决定。不要把所有函数都统一写成空时返回 0。',
 'values = [3, 7, 8]\nprint(sum(values), len(values))\nprint(sum(values) / len(values))\nprint(sum([]))', '18 3\n6.0\n0', 'https://docs.python.org/3/library/functions.html#sum')
card('slice','切片、边界与副本','xs[start:stop:step]\nxs[:n]\nxs[:]',
 '切片包含 start、不包含 stop；省略 start 从头取，省略 stop 到末尾。切片越过边界会自动截断，与单个索引不同。列表切片创建新的外层列表；b=xs 只创建别名。嵌套列表的内层仍可能共享，之后需要 deepcopy。',
 'xs = [2, 4, 6, 8]\na = xs[:2]\na[0] = 99\nprint(xs)\nprint(a)\nprint(xs[1:20:2], xs[:0])', '[2, 4, 6, 8]\n[99, 4]\n[4, 8] []', PY+'introduction.html#lists')
card('string','方法调用、lower 与字符串不变性','new_text = text.lower()\ntrimmed = text.strip()',
 '点左侧是对象，点右侧是这个对象的方法；括号表示实际调用。lower() 无必填参数，返回小写后的新字符串；不会改变原 text。strip() 只清除两端空白，不清除中间空白。两者都不负责删除标点。repr(value)把字符串边界与空白转义显示出来，便于观察，不是清洗操作。先用几个有名字的中间变量，把每一步的类型和值写清楚，再读链式写法。',
 'text = "  HeLLo, LAB!  "\nsmall = text.lower()\ntrimmed = small.strip()\nprint(repr(text))\nprint(repr(small))\nprint(repr(trimmed))', "'  HeLLo, LAB!  '\n'  hello, lab!  '\n'hello, lab!'", TYPES+'#str.lower')
card('split','split() 与 split(" ") 是不同规则','words = text.split()\nfields = text.split(sep, maxsplit)',
 '不传 sep 的 split() 按连续空白分组，支持空格、制表符 \t、换行 \n，忽略两端空白，不产生空词；返回 list[str]。显式 split(" ") 只认单个空格，每个分隔符都会切一次，因此连续空格会产生空字符串，也不切制表符。可选 maxsplit 限制最多切几次，结果最多多一段。空白字符串的默认 split() 返回 []。',
 'text = "  RED\tBLUE  "\nprint(text.split())\nprint(text.split(" "))\nprint("x:y:z".split(":", 1))\nprint("   ".split())', "['RED', 'BLUE']\n['', '', 'RED\\tBLUE', '', '']\n['x', 'y:z']\n[]", TYPES+'#str.split')
card('chain','链式调用：先看每一步返回什么','lowered = text.lower()\nwords = lowered.split()\n# equivalent: text.lower().split()',
 '方法从左到右执行。lower 的结果仍是字符串，所以可以继续调用字符串 split；split 的结果是列表，因此不能继续 .lower()。text.lower().split() 是两步计算的简写，不是一个必须背下来的新函数。读不顺时就拆成中间变量；这种写法同样正确。',
 'text = "  Orange\tPEAR!  "\nlowered = text.lower()\nwords = lowered.split()\nprint(repr(lowered))\nprint(words)\nprint(text.lower().split() == words)', "'  orange\\tpear!  '\n['orange', 'pear!']\nTrue", 'https://cs50.harvard.edu/python/notes/0/')
card('tuplezip','配对、解包与 zip','for left, right in zip(xs, ys):\n    ...\nreturn first, second',
 'zip 按相同位置配对；循环头的两个名字把这一对拆开。默认在较短一侧结束，不替你验证等长。return a,b 返回一个二元元组，调用者可写 x,y=f() 解包。计数时 True/False 可参与整数计算，但先写明确 if 更容易检查。',
 'xs = [2, 4, 6]\nys = [2, 0, 6]\ncorrect = 0\nfor left, right in zip(xs, ys):\n    if left == right:\n        correct += 1\nprint(correct, len(xs))\nprint(list(zip([1, 2], [8])))', '2 3\n[(1, 8)]', 'https://docs.python.org/3/library/functions.html#zip')
card('default','默认参数与关键字参数','def transform(x, factor=2, bias=0):\n    ...\ntransform(3, bias=1)',
 '调用者省略参数才使用默认值；传入 0 仍是明确的实参。位置实参按顺序配对，关键字实参按名字配对。默认值在函数定义时求值一次，因此列表默认值会跨调用共享。普通数值默认值不涉及这个共享修改问题。',
 'def shift(x, amount=2, bias=0):\n    return x * amount + bias\nprint(shift(3))\nprint(shift(3, bias=4))\nprint(shift(3, 0, 4))', '6\n10\n4', PY+'controlflow.html#default-argument-values')
card('comprehension','先会循环，再读推导式','result = [expression for item in values if condition]',
 '推导式是新建列表的简写：先从 for 读取每项，再按可选 if 过滤，最后计算左侧 expression。它不是必须使用的解法；先写 result=[]、for、append 完全可以。多层循环或状态累计时，普通循环往往更容易读。',
 'values = [1, 2, 3, 4]\nresult = []\nfor value in values:\n    if value % 2 == 0:\n        result.append(value * 10)\nprint(result)\nprint([v * 10 for v in values if v % 2 == 0])', '[20, 40]\n[20, 40]', PY+'datastructures.html#list-comprehensions')
card('set','成员判断与保序去重','seen = set()\nif item not in seen:\n    seen.add(item)',
 'set 存放互不重复的可哈希元素，用 in / not in 判断成员，用 add 添加。空集合必须写 set()，{} 是空字典。集合不能用下标访问，也不承诺原始插入顺序；所以保序去重需要列表负责顺序、集合负责见过与否。普通列表不可哈希，不能直接放入集合。',
 'seen = set()\nresult = []\nfor value in ["b", "a", "b", "c"]:\n    if value not in seen:\n        seen.add(value)\n        result.append(value)\nprint(result)', "['b', 'a', 'c']", PY+'datastructures.html#sets')
card('nested','二维列表、最大长度与独立行','rows = [[...], [...]]\nwidth = max(lengths, default=0)',
 '二维列表是“列表里装列表”。len(rows) 是行数，len(rows[i]) 是第 i 行长度。max(...,default=0) 为无元素时指定结果；不是把 0 与所有元素一起比较。每轮创建新行，避免 [[0]*width]*batch 让各行共享同一列表。mask 表示原长度，不应由元素值是不是 0 推断。',
 'rows = [[0, 7], [4], []]\nwidth = max((len(row) for row in rows), default=0)\npadded = []\nfor row in rows:\n    padded.append(row[:] + [0] * (width - len(row)))\nprint(width)\nprint(padded)', '2\n[[0, 7], [4, 0], [0, 0]]', PY+'datastructures.html#nested-list-comprehensions')
card('generator','yield、生成器与惰性执行','def pieces(...):\n    yield value\nlist(pieces(...))',
 '函数中出现 yield，这个函数调用返回生成器；函数体要等迭代才真正执行。yield 产出一个值并暂停，下次迭代从暂停处继续；return 结束迭代，不再产出值。因而参数校验写在生成器体内时，异常会在迭代时出现。用 list(g) 可以消费生成器，但同一个生成器消费后不会自动回到开头。',
 'def two_parts():\n    yield [1, 2]\n    yield [3]\ng = two_parts()\nprint(list(g))\nprint(list(g))', '[[1, 2], [3]]\n[]', PY+'classes.html#generators')
card('none','None 哨兵与可变默认值','def remember(value, history=None):\n    if history is None:\n        history = []',
 'None 表示没有提供对象，判断用 is None。不要写 if not history 来区分“未提供”与“传入空列表”，因为空列表也是假。显式传入列表时是否允许原地修改，要服从函数契约；创建新列表与返回原列表是不同接口。',
 'def add(value, history=None):\n    if history is None:\n        history = []\n    history.append(value)\n    return history\na = []\nprint(add(1), add(2))\nprint(add(3, a), a)', '[1] [2]\n[3] [3]', PY+'controlflow.html#default-argument-values')
card('raise','主动校验与异常','if invalid:\n    raise ValueError("reason")',
 'raise 主动中止正常流程，调用者可以捕获。ValueError 常用于类型大体正确但取值不合法。多个非法条件用 or 联结，也可逐项检查。NaN 与普通比较不同，0 <= value <= 1 对 NaN 为 False；先想清楚合法条件，再用 not 取反，比只写 value<0 or value>1 更稳。',
 'def require_positive(n):\n    if n <= 0:\n        raise ValueError("positive required")\n    return n\ntry:\n    require_positive(0)\nexcept ValueError as error:\n    print(type(error).__name__)\nprint(require_positive(2))', 'ValueError\n2', PY+'errors.html#raising-exceptions')
card('dict','字典的键、取值与遍历','row = {"loss": 0.4}\nrow["loss"]\nrow.get("score", default)',
 '字典把键映射到值。d[key] 在键不存在时抛 KeyError；get 只有缺键时才使用默认值，合法的 0、False、None 不会被替换。for key in d 遍历键，for key,value in d.items() 同时取键值。记录列表要先取一条记录，再取其中字段。',
 'row = {"loss": 0, "name": "run-a"}\nprint(row["name"], row.get("loss", 9))\nprint(row.get("score", 9))\ncounts = {}\nfor label in ["cat", "dog", "cat"]:\n    counts[label] = counts.get(label, 0) + 1\nprint(counts)', "run-a 0\n9\n{'cat': 2, 'dog': 1}", PY+'datastructures.html#dictionaries')
card('group','分组累计与字典推导式','totals[key] += value\ncounts[key] += 1\nresult[key] = totals[key] / counts[key]',
 '先为每个组分别存总和与次数，不能把所有组的损失一起平均。第一次遇见某组时先建立默认状态。items() 可同时得到键和值。字典推导式 {k: expression for k in keys} 是新建字典的简写，也可以先用普通循环逐项赋值。',
 'totals = {}\ncounts = {}\nfor name, loss in [("a", 2), ("b", 9), ("a", 4)]:\n    totals[name] = totals.get(name, 0) + loss\n    counts[name] = counts.get(name, 0) + 1\nresult = {}\nfor name in totals:\n    result[name] = totals[name] / counts[name]\nprint(result)', "{'a': 3.0, 'b': 9.0}", PY+'datastructures.html#dictionaries')
card('sort','sorted、key、元组与 lambda','sorted(records, key=key_function)\nlambda row: (-row["score"], row["name"])',
 'sorted 返回新列表，不修改输入；list.sort() 会原地修改并返回 None。key 接一个函数对象，排序时对每条元素调用它。元组先比第一项，平局再比第二项；数值前加负号可以把该项降序。lambda row: expression 等价于一个只有 return expression 的小函数；先用 def 写 key 更易懂。',
 'rows = [("z", 8), ("a", 8), ("b", 9)]\ndef order(row):\n    return (-row[1], row[0])\nprint(sorted(rows, key=order))\nprint(rows)', "[('b', 9), ('a', 8), ('z', 8)]\n[('z', 8), ('a', 8), ('b', 9)]", 'https://docs.python.org/3/howto/sorting.html')
card('copy','别名、浅复制与深复制','import copy\nindependent = copy.deepcopy(original)',
 '赋值不复制。列表切片或 dict.copy 只复制外层容器，内层可变对象仍共享。deepcopy 递归复制内部可变结构。本课程的配置与记录不含循环引用；递归合并时先识别双方都是字典的情况，再把更小的子字典交给同一函数。一个分支返回基本值时就停止递归。',
 'import copy\noriginal = {"dims": [2, 3]}\nshallow = original.copy()\ndeep = copy.deepcopy(original)\nshallow["dims"].append(4)\nprint(original)\nprint(deep)', "{'dims': [2, 3, 4]}\n{'dims': [2, 3]}", 'https://docs.python.org/3/library/copy.html')
card('finite','类型检查、bool 与有限数','import math\ntype(value) in (int, float)\nmath.isfinite(value)',
 'bool 是 int 的子类，因此 isinstance(True,int) 为真；若契约排除布尔值，可用 type(value) in (int,float)。math.isfinite 排除 NaN 和正负无穷。先检查类型，再做有限性或范围判断，避免把字符串交给数值函数。筛选、比较、返回是三个独立步骤；返回 epoch 不等于返回整条记录。',
 'import math\nfor value in [True, 0, 0.5, float("nan"), float("inf")]:\n    valid = type(value) in (int, float) and math.isfinite(value)\n    print(valid)', 'False\nTrue\nTrue\nFalse\nFalse', 'https://docs.python.org/3/library/math.html#math.isfinite')
card('except','只捕获预期异常','try:\n    value = float(text)\nexcept ValueError:\n    return None',
 'try 中正常执行的结果继续流向后面；仅发生指定异常时才进入 except。可选else块只在try没有异常时执行。不要为了让测试过关而使用裸 except 吞掉所有错误。float 可以接受两端空白，但也会接受 "nan" 和 "inf"，因此转换成功还不代表数值有效，需要另做有限性与范围判断。',
 'import math\nfor text in [" 0.4 ", "oops", "nan"]:\n    try:\n        value = float(text)\n    except ValueError:\n        print("bad text")\n        continue\n    print(math.isfinite(value))', 'True\nbad text\nFalse', PY+'errors.html#handling-exceptions')
card('filejson','with open、UTF-8 与 JSON','with open(path, "r", encoding="utf-8") as handle:\n    data = json.load(handle)',
 '先 import json。open 的第一个参数是路径，"r" 读取、"w" 覆盖写；with 块结束自动关闭文件，包括异常退出。json.load 读文件对象，json.loads 读字符串；json.dump 写文件对象，json.dumps 返回字符串。JSON 中 null/true 会变为 Python None/True；字典 get 可提供缺键默认值。',
 'import json\ntext = \'{"name":"demo","active":true}\'\ndata = json.loads(text)\nprint(data["name"], data["active"])\nprint(data.get("lr", 0.002))\nprint(json.dumps({"loss": 0.5}, sort_keys=True))', 'demo True\n0.002\n{"loss": 0.5}', PY+'inputoutput.html#saving-structured-data-with-json')
card('csv','CSV 解析与 DictReader','import csv\nrows = csv.DictReader(handle)',
 'CSV 字段中可以包含引号包住的逗号，不能用 split(",") 代替解析器。DictReader 用表头作字典键，每一行的普通字段仍是字符串，需要 float 转换。读取文件时用 encoding="utf-8", newline=""。没有数据行与平均值为 0 是不同情况。',
 'import csv\nimport io\nhandle = io.StringIO(\'name,loss\\n"blue, large",0.4\\nred,0.6\\n\')\nrows = list(csv.DictReader(handle))\nprint(rows[0]["name"])\nprint(sum(float(row["loss"]) for row in rows) / len(rows))', 'blue, large\n0.5', 'https://docs.python.org/3/library/csv.html')
card('jsonl','逐行 JSON 与错误位置','for line in handle:\n    if not line.strip():\n        continue\n    value = json.loads(line)',
 'JSONL 是每行一个独立 JSON 值。空行可以先跳过；一行坏 JSON 应只跳过这一行，而不是丢掉整个文件。解析成功的列表、数字也是合法 JSON，却未必符合“记录必须是字典”的业务约定。json.JSONDecodeError 只捕获格式错误；是否跳过其他类型要另行判断。',
 'import json\nlines = [\'{"x":1}\', "", "oops", "[1,2]"]\nrecords = []\nbad = 0\nfor line in lines:\n    if not line.strip():\n        continue\n    try:\n        value = json.loads(line)\n    except json.JSONDecodeError:\n        bad += 1\n        continue\n    if isinstance(value, dict):\n        records.append(value)\n    else:\n        bad += 1\nprint(records, bad)', "[{'x': 1}] 2", 'https://docs.python.org/3/library/json.html')
card('assert','断言、结构与逐层验证','assert condition, "reason"\nisinstance(value, (list, tuple))',
 'assert 条件为假时抛 AssertionError。先检查外层类型，才可以安全地 len 或遍历；再检查行类型、行宽、元素类型、标签长度与取值。这里按题目要求练习断言；生产接口的必要校验通常应显式 raise，因为 Python 优化模式可移除 assert。两空序列是否允许也要读契约。',
 'def require_pair(values):\n    assert isinstance(values, (list, tuple))\n    assert len(values) == 2\n    return True\nprint(require_pair([3, 4]))\ntry:\n    require_pair([3])\nexcept AssertionError:\n    print("invalid shape")', 'True\ninvalid shape', PY+'errors.html#raising-exceptions')
card('class','类、实例、self 与初始化','class Counter:\n    def __init__(self):\n        self.count = 0\n    def update(self):\n        self.count += 1',
 'class 定义一种对象；Counter() 创建实例并调用 __init__ 初始化。self 是当前实例，调用 obj.update() 时 Python 自动把 obj 传给方法的第一个参数。需要跨调用保留的状态放 self.xxx，不是每次方法里都重新设局部变量。每个实例应有独立状态。',
 'class Counter:\n    def __init__(self):\n        self.count = 0\n    def update(self, n=1):\n        self.count += n\na = Counter()\nb = Counter()\na.update(3)\nprint(a.count, b.count)', '3 0', PY+'classes.html#class-objects')
card('weighted','累计总量而非平均比例','weighted_total += value * count\nsamples += count\nmean = weighted_total / samples',
 '如果 value 是本批均值，必须乘上本批数量再累计。不同批次大小时，直接平均各批均值或准确率会给小批次过高权重。空状态的行为由接口决定。reset 需要重置分子和分母，不能只重置显示值。',
 'means = [2.0, 10.0]\nsizes = [3, 1]\ntotal = 0.0\ncount = 0\nfor mean, size in zip(means, sizes):\n    total += mean * size\n    count += size\nprint(total / count)\nprint(sum(means) / len(means))', '4.0\n6.0', 'https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html')
card('protocol','特殊方法与可调用对象','def __len__(self): ...\ndef __getitem__(self, index): ...\ndef __call__(self, value): ...',
 'len(obj) 调用 __len__；obj[i] 调用 __getitem__；obj(value) 调用 __call__。这些方法仍要显式 return。构造时复制输入与取出时复制数据解决不同的共享风险。函数也能放入列表并依次调用，Compose 保存的是函数对象，不是每个函数提前执行的结果。',
 'class Doubler:\n    def __call__(self, value):\n        return value * 2\nclass TinyData:\n    def __len__(self):\n        return 2\n    def __getitem__(self, index):\n        return [5, 9][index]\nprint(Doubler()(6))\ndata = TinyData()\nprint(len(data), data[1])', '12\n2 9', 'https://docs.python.org/3/reference/datamodel.html#special-method-names')
card('state','把历史规则写成状态机','best, bad_count, patience\nif significant_improvement:\n    bad_count = 0\nelse:\n    bad_count += 1',
 '先明确状态、输入和一次step后的输出。本题best表示上一次显著改善的基准：min_delta>0时，小幅下降不更新它，等待次数仍增加；只有loss<best-min_delta才更新best并清零等待。min_delta=0时才退化为逐次记录严格下降的历史最小值。先手算短序列，再写类。',
 'best = None\nbad = 0\nmin_delta = 0.1\nfor loss in [1.0, 0.95, 0.89]:\n    if best is None or loss < best - min_delta:\n        best = loss\n        bad = 0\n    else:\n        bad += 1\n    print(best, bad)', '1.0 0\n1.0 1\n0.89 0', PY+'classes.html#instance-objects')
