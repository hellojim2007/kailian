"""Independent Python assessments; all tasks and data are original.

No exercise here replaces an existing lesson. Explanations are feedback for
after submission, rather than hints shown during an assessment.
"""
from assessment_common import Bank, check


def program(stdin, expected, label):
    return {'stdout': True, 'stdin': stdin, 'expected': expected, 'label': label}


def build():
    bank = Bank('py')

    # Chapters 1 and 2 precede functions: write standalone programs here.
    items = [
        bank.output('c01-stock', 'c01', '写出这段仓库记录程序的完整标准输出。', r'''
            boxes = 14
            reserved = boxes - 5
            boxes = 3
            reserved += boxes
            print(boxes, reserved)
        ''', '3 12', 'reserved 先保存 9；改变 boxes 不会自动重算它，最后再加 3。', ['p1']),
        bank.output('c01-scan', 'c01', '写出完整标准输出，每个 print 的结果各占一行。', r'''
            total = 0
            for value in range(2, 9, 3):
                total += value
                print(total)
            print("done")
        ''', '2\n7\n15\ndone', 'range 依次产生 2、5、8，不含终点 9；循环外的输出只执行一次。', ['p3', 'py03']),
        bank.choice('c01-input', 'c01', '标准输入是一行 24。运行代码后会输出什么？',
                    ['24 6', '246', '抛出 TypeError'], 1,
                    'input() 得到字符串 "24"，与字符串 "6" 相加是在拼接；int 转换才会做数值加法。',
                    ['py01'], code='value = input()\nprint(value + "6")'),
        bank.choice('c01-branches', 'c01', '这段程序原本想对温度分三级。关于输入温度 35，哪项判断正确？',
                    ['输出 warm，因为首个分支已匹配；hot 分支不会执行',
                     '依次输出 warm 和 hot', '输出 hot，因为后面的条件更严格'], 0,
                    'if/elif 只执行首个成立分支；要优先识别高温，应先判断 >=30。',
                    ['py02'], code='temperature = 35\nif temperature >= 20:\n    print("warm")\nelif temperature >= 30:\n    print("hot")\nelse:\n    print("cold")'),
        bank.coding('c01-fare', 'c01',
                    '标准输入是一行整数 age。age<0 时输出 INVALID；0–5 岁输出 0；6–17 岁输出 8；18 岁及以上输出 15。只输出一个结果，不输出输入提示。',
                    '完整程序 · input / if / print', r'''
            age = int(input())
            if age < 0:
                print('INVALID')
            elif age <= 5:
                print(0)
            elif age <= 17:
                print(8)
            else:
                print(15)
        ''', [program('-1\n', 'INVALID', '负年龄'), program('0\n', '0', '零岁'),
              program('5\n', '0', '免费上界'), program('6\n', '8', '优惠下界'),
              program('17\n', '8', '优惠上界'), program('18\n', '15', '成人下界')],
                    '先排除负值，再按从小到大的上界判断；边界 5/6 和 17/18 决定分支是否完整。', ['py01', 'py02']),
        bank.coding('c01-sentinel', 'c01',
                    '标准输入为一行整数，可为空。把第一个 0 当作结束标记，0 及其后所有数均忽略。输出结束标记之前能被 3 整除的数的个数；负数也按同一整除规则处理。没有 0 时检查整行。',
                    '完整程序 · 循环 / break / 计数', r'''
            values = list(map(int, input().split()))
            count = 0
            for value in values:
                if value == 0:
                    break
                if value % 3 == 0:
                    count += 1
            print(count)
        ''', [program('3 4 6 0 9\n', '2', '标记后不再计数'), program('0 3\n', '0', '首项结束'),
              program('-6 -2 12\n', '2', '负数与没有标记'), program('\n', '0', '空行'),
              program('1 2 4\n', '0', '无匹配')],
                    '先判断标记再计数，才能忽略 0 以及后续项。这里只累计个数，不能把满足条件的数直接求和。', ['p1', 'p3', 'py04']),
    ]
    bank.exam('chapter-c01', 'chapter', '第 1 章 · 输入与控制流验收', ['c01'], 10, items,
              '独立追踪变量与循环，识别分支顺序问题，再写两个完整程序。')

    items = [
        bank.output('c02-copy', 'c02', '写出两行完整输出，注意切片复制的范围。', r'''
            readings = [8, 6, 4, 2]
            tail = readings[1:3]
            tail[0] = 99
            print(readings[-1], readings[0])
            print(tail)
        ''', '2 8\n[99, 4]', '切片新建外层列表；替换 tail 的元素不修改 readings。右边界索引 3 不包含。', ['p2', 'py05']),
        bank.output('c02-tokens', 'c02', '写出完整标准输出。这里没有文件或隐藏输入。', r'''
            text = "  NET\tLab!\nNET  "
            words = text.lower().split()
            print(len(words))
            print(words[1])
        ''', '3\nlab!', '默认 split 处理空格、制表符与换行；lower 不会删除感叹号。', ['py06']),
        bank.choice('c02-mask', 'c02', '长度不同的原序列是 [0,7] 与 [4]。右侧补 0 后，哪一组 mask 正确？',
                    ['[[False,True],[True,False]]', '[[True,True],[True,False]]', '[[True,True],[True,True]]'], 1,
                    'mask 描述原位置是否存在。第一行的 0 是有效数据，第二行末尾的 0 才是 padding。', ['py09']),
        bank.choice('c02-shared', 'c02', '想得到两行彼此独立的结果。下列代码的问题是什么？',
                    ['没有问题，两行独立', '两行共享同一个内部列表，修改任一行都会影响另一行', '整数不能放进二维列表'], 1,
                    '外层乘法复制的是同一行的引用。循环中分别创建每一行，才能避免共享状态。', ['py05', 'py09'],
                    code='rows = [[0, 0]] * 2\nrows[1][0] = 5\nprint(rows)'),
        bank.coding('c02-peak', 'c02',
                    '标准输入共两行：第一行为正整数 k，第二行为整数列表（可以为空）。求任意连续 k 项的最大总和并输出；若项数不足 k，输出 EMPTY。k 保证大于 0。允许简单循环实现，不要求特定复杂度。',
                    '完整程序 · 切片 / 窗口 / 边界', r'''
            k = int(input())
            values = list(map(int, input().split()))
            if len(values) < k:
                print('EMPTY')
            else:
                best = sum(values[:k])
                for start in range(1, len(values) - k + 1):
                    total = sum(values[start:start + k])
                    if total > best:
                        best = total
                print(best)
        ''', [program('2\n4 -3 7 2\n', '9', '最大窗口在末尾'),
              program('2\n-8 -2 -5\n', '-7', '全负值不能用零初始化'),
              program('1\n-3 6 2\n', '6', '单项窗口'), program('3\n1 2\n', 'EMPTY', '长度不足'),
              program('1\n\n', 'EMPTY', '空列表')],
                    '以第一个真实窗口初始化 best，避免全负值时错误地返回 0；起点应包含最后一个完整窗口。', ['p2', 'py05', 'py07']),
        bank.coding('c02-dictionary-order', 'c02',
                    '标准输入为一行文本。按任意空白分词、转为小写，再按首次出现顺序输出不重复的词，用一个空格连接；标点保留。空白行只输出空行。',
                    '完整程序 · 文本清洗 / 保序去重', r'''
            words = input().lower().split()
            seen = set()
            kept = []
            for word in words:
                if word not in seen:
                    seen.add(word)
                    kept.append(word)
            print(' '.join(kept))
        ''', [program('Blue RED blue green RED\n', 'blue red green', '大小写合并且保序'),
              program('  A\tB   a!\n', 'a b a!', '任意空白与保留标点'),
              program('\n', '', '空白输入'), program('模型 模型 Lab\n', '模型 lab', 'Unicode'),
              program('z z z\n', 'z', '全部重复')],
                    '先按同一规则规范化，再检查是否见过。集合负责成员判断，列表保留首次出现的顺序。', ['py06', 'py08']),
    ]
    bank.exam('chapter-c02', 'chapter', '第 2 章 · 序列与文本验收', ['c02'], 10, items,
              '区分副本与共享引用，处理真实零值、窗口边界和文本顺序。')

    items = [
        bank.output('c03-return', 'c03', '写出完整标准输出，包括函数内和函数外的 print。', r'''
            def shipping(items, extra=2):
                print(len(items))
                return sum(items) + extra
            result = shipping([3, 4], extra=0)
            print(result)
        ''', '2\n7', '函数内打印长度 2，但调用表达式得到 return 的 7；显式 extra=0 会覆盖默认值。', ['p4', 'py10']),
        bank.output('c03-default-list', 'c03', '写出两行完整输出。', r'''
            def collect(value, bucket=None):
                if bucket is None:
                    bucket = []
                bucket.append(value)
                return bucket
            saved = []
            print(collect(4, saved))
            print(collect(9), saved)
        ''', '[4]\n[9] [4]', '显式传入 saved 时更新它；没有传入时创建新的列表，因此第二次不会改 saved。', ['py12']),
        bank.choice('c03-generator', 'c03', '执行到 line = stream() 后，哪项描述正确？',
                    ['已经输出 begin，line 是 [2]', '尚未输出 begin，line 是生成器对象', '已输出 begin，line 是整数 2'], 1,
                    '含 yield 的函数调用先创建生成器；函数体在 next 或迭代时才开始执行。', ['py11'],
                    code='def stream():\n    print("begin")\n    yield 2\nline = stream()'),
        bank.choice('c03-invalid-average', 'c03', '函数要求概率全在 [0,1] 且非空。哪种验证能同时拒绝空列表与 NaN？',
                    ['if not values or any(not 0 <= x <= 1 for x in values): raise ValueError()',
                     'if any(x < 0 or x > 1 for x in values): raise ValueError()',
                     'if not sum(values): raise ValueError()'], 0,
                    'NaN 的 <0 与 >1 都为 False；正向区间判断对 NaN 为 False。sum 为零则可能只是全零合法输入。', ['py13']),
        bank.coding('c03-weighted-hits', 'c03',
                    '定义 weighted_accuracy(preds,labels,weights)。三个输入是等长列表，weights 为有限非负数。返回正确预测对应的权重之和 / 总权重；总权重为 0 时返回 0.0。长度不一致抛 ValueError。不得修改输入。',
                    'def weighted_accuracy(preds, labels, weights)', r'''
            def weighted_accuracy(preds, labels, weights):
                if len(preds) != len(labels) or len(labels) != len(weights):
                    raise ValueError('length mismatch')
                total = sum(weights)
                if total == 0:
                    return 0.0
                correct = sum(weight for pred, label, weight in zip(preds, labels, weights) if pred == label)
                return correct / total
        ''', [check('weighted_accuracy([1,0,1],[1,1,1],[1,6,3])', .4, label='按权重而非样本数'),
              check('weighted_accuracy([],[],[])', 0., label='空输入'),
              check('weighted_accuracy([1],[0],[0])', 0., label='零总权重'),
              check('weighted_accuracy([0,1],[0,1],[2,8])', 1., label='全部正确'),
              check('weighted_accuracy([1],[1,0],[1])', raises='ValueError', label='长度不一致')],
                    '分子只累计正确项的权重，分母累计所有权重。先验证长度，避免 zip 静默截断。', ['p4', 'p6', 'py13']),
        bank.coding('c03-budget-stream', 'c03',
                    '定义 within_budget(costs,budget)，返回生成器。costs 是有限非负数列表，budget 为有限数。按原序逐项产出费用，只有累计费用不超过 budget 才产出；遇到首个无法容纳的费用就结束，后续不再跳选。budget<0 在开始迭代时抛 ValueError。不修改 costs。',
                    'def within_budget(costs, budget)', r'''
            def within_budget(costs, budget):
                if budget < 0:
                    raise ValueError('negative budget')
                total = 0
                for cost in costs:
                    if total + cost > budget:
                        break
                    total += cost
                    yield cost
        ''', [check('list(within_budget([2,4,1],5))', [2], label='首个超额后停止'),
              check('list(within_budget([2,3,1],5))', [2,3], label='恰好用尽预算'),
              check('list(within_budget([0,0,1],0))', [0,0], label='零费用也可产出'),
              check('list(within_budget([],0))', [], label='空输入'),
              check('list(within_budget([1],-1))', raises='ValueError', label='负预算'),
              check('isinstance(within_budget([],-1),__import__("types").GeneratorType)', True,
                    label='真正生成器且创建时尚不抛负预算异常')],
                    '累计后是否越界决定能否 yield；遇到无法容纳的费用使用 break，因此不会从后面挑便宜项填空。', ['py10', 'py11', 'py13']),
    ]
    bank.exam('chapter-c03', 'chapter', '第 3 章 · 函数与生成器验收', ['c03'], 10, items,
              '区分打印与返回、显式零值与默认值，独立写有清晰契约的函数。')

    _chapters_04_06(bank)
    _cumulative_and_stage(bank)
    _reviews(bank)
    return bank.result()


def _chapters_04_06(bank):
    items = [
        bank.output('c04-counts', 'c04', '写出完整标准输出。字典的键顺序按首次插入顺序保留。', r'''
            counts = {}
            for label in ['dog', 'cat', 'dog', 'bird', 'cat']:
                counts[label] = counts.get(label, 0) + 1
            print(list(counts))
            print(counts['cat'])
        ''', "['dog', 'cat', 'bird']\n2", '已有键更新不会重新插入；cat 出现两次。', ['py14']),
        bank.output('c04-config', 'c04', '写出完整标准输出。', r'''
            import copy
            original = {'tags': ['fast'], 'limit': 0}
            shallow = original.copy()
            deep = copy.deepcopy(original)
            shallow['tags'].append('cpu')
            deep['tags'].append('gpu')
            print(original['tags'])
            print(original.get('limit', 8))
        ''', "['fast', 'cpu']\n0", '浅复制与 original 共享内部 tags；deep 中的追加不影响 original。get 保留显式的零。', ['py17', 'p5']),
        bank.choice('c04-weighting', 'c04', '模型 A 的两条 loss 是 0 和 4，模型 B 的一条 loss 是 10。三条记录的整体均值是多少？',
                    ['6，因为两个模型均值是 2 和 10', '14/3，因为每条记录应有相同权重', '7，因为只需最大与最小值'], 1,
                    '两个组的样本数不同，不能等权平均组均值；总和 14 除以总记录数 3 才是整体均值。', ['py15']),
        bank.choice('c04-checkpoint', 'c04', '下面候选中，按有限 loss 最小、并列 epoch 最早的规则应返回哪个 epoch？',
                    ['1', '4', '6'], 1,
                    'epoch=1 的 NaN 应先过滤；剩下两条 loss 相同，所以取较早的 epoch=4。', ['py16', 'py18'],
                    code='records = [\n    {"epoch": 1, "loss": float("nan")},\n    {"epoch": 6, "loss": 0.2},\n    {"epoch": 4, "loss": 0.2},\n]'),
        bank.coding('c04-team-counts', 'c04',
                    '定义 team_counts(events)。events 是字典列表，每项有字符串 team 和 status，status 保证为 ok 或 failed。返回 {team:{ok:成功数,failed:失败数}}，每个出现的 team 都保留这两个键，即使其中一个计数为 0。空输入返回 {}，不得修改 events。',
                    'def team_counts(events)', r'''
            def team_counts(events):
                result = {}
                for event in events:
                    team = event['team']
                    if team not in result:
                        result[team] = {'ok': 0, 'failed': 0}
                    result[team][event['status']] += 1
                return result
        ''', [check('team_counts([{"team":"red","status":"ok"},{"team":"blue","status":"failed"},{"team":"red","status":"ok"}])',
                     {'red':{'ok':2,'failed':0},'blue':{'ok':0,'failed':1}}, label='交错分组且保留零计数'),
              check('team_counts([])', {}, label='空记录'),
              check('team_counts([{"team":"","status":"failed"}])', {'':{'ok':0,'failed':1}}, label='空字符串也是合法组名'),
              check('events', [{'team':'x','status':'ok'}], setup='events=[{"team":"x","status":"ok"}]\nteam_counts(events)', label='不改输入')],
                    '为每个 team 单独创建计数器；两个状态都设初值，才能区分没有该状态与遗漏该字段。', ['p5', 'py14', 'py15']),
        bank.coding('c04-qualified-ranking', 'c04',
                    '定义 qualified_teams(records,min_count)。每条记录含字符串 team 和有限数值 score；min_count 为正整数。按 team 分组，保留记录数至少 min_count 的组，按组平均 score 降序、team 升序返回组名列表。不得修改 records。',
                    'def qualified_teams(records, min_count)', r'''
            def qualified_teams(records, min_count):
                totals = {}
                counts = {}
                for record in records:
                    team = record['team']
                    totals[team] = totals.get(team, 0) + record['score']
                    counts[team] = counts.get(team, 0) + 1
                eligible = [team for team in totals if counts[team] >= min_count]
                return sorted(eligible, key=lambda team: (-totals[team] / counts[team], team))
        ''', [check('qualified_teams([{"team":"b","score":2},{"team":"a","score":3},{"team":"b","score":4},{"team":"c","score":99}],2)',
                     ['b'], label='数量门槛先筛选'),
              check('qualified_teams([{"team":"b","score":2},{"team":"a","score":2},{"team":"c","score":3}],1)',
                     ['c','a','b'], label='均分降序并列名字升序'),
              check('qualified_teams([],1)', [], label='空输入'),
              check('qualified_teams([{"team":"x","score":0}],2)', [], label='全组不合格'),
              check('qualified_teams([{"team":"a","score":0},{"team":"a","score":6},{"team":"b","score":4}],1)',
                     ['b','a'], label='按均值而非总分排序'),
              check('rows', [{'team':'z','score':1},{'team':'a','score':8}],
                    setup='rows=[{"team":"z","score":1},{"team":"a","score":8}]\nqualified_teams(rows,1)', label='不原地排序或修改记录')],
                    '先累计每组总分与次数，再筛记录数，最后用均值排序；直接按总分排序会偏向记录多的组。', ['py14', 'py15', 'py16']),
    ]
    bank.exam('chapter-c04', 'chapter', '第 4 章 · 字典与实验数据验收', ['c04'], 10, items,
              '检查嵌套副本、指标有效性与分组权重，并实现完整的分组榜单。')

    items = [
        bank.output('c05-csv', 'c05', '写出完整标准输出。CSV 数据直接写在代码中。', r'''
            import csv
            import io
            text = 'name,score\n"north,lab",4\nsouth,6\n'
            rows = list(csv.DictReader(io.StringIO(text)))
            print(len(rows), rows[0]['name'])
            print(sum(float(row['score']) for row in rows))
        ''', '2 north,lab\n10.0', '引号中的逗号属于 name 字段；DictReader 的数值字段仍是字符串，需要显式转成数值。', ['py21']),
        bank.output('c05-json-structure', 'c05', '写出两行完整输出。所有 JSON 数据均在代码中给出。', r'''
            import json
            records = []
            invalid = 0
            for line in ['{"ok":true}', 'null', '{oops}', '   ']:
                if not line.strip():
                    continue
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    invalid += 1
                    continue
                if isinstance(value, dict):
                    records.append(value)
                else:
                    invalid += 1
            print(len(records), invalid)
            print(records[0]['ok'])
        ''', '1 2\nTrue', 'null 是合法 JSON，但不是字典记录；坏 JSON 也计为无效，空白行不计。JSON 的 true 解析为 Python True。', ['py22', 'py24']),
        bank.choice('c05-json-api', 'c05', '变量 raw 是字符串 \'{"rate":0}\'。怎样正确解析，并在 rate 缺失时默认使用 2，同时保留合法的 0？',
                    ['json.load(raw).get("rate",2)', 'json.loads(raw).get("rate",2)', 'json.loads(raw).get("rate") or 2'], 1,
                    'loads 接受字符串；load 接受文件对象。get 的默认值只在键缺失时使用，or 会错误替换合法零值。', ['py20']),
        bank.choice('c05-exception', 'c05', '这个转换函数为什么不适合作为严格解析器？',
                    ['它不能捕获 ValueError', '它把程序自身的 NameError 也当作输入错误吞掉了', 'float 只能转换整数'], 1,
                    'ratio 未定义会抛 NameError，却被 except Exception 吞掉。应只捕获预期转换错误，让程序错误暴露。', ['py19', 'py23'],
                    code='def parse(text):\n    try:\n        return float(text) * ratio\n    except Exception:\n        return None'),
        bank.coding('c05-csv-to-json', 'c05',
                    '定义 export_passes(input_path,output_path,minimum)。输入为 UTF-8 CSV，列名 name、score；score 保证是有限数值字符串。按原序收集 score>=minimum 的 name，返回名称列表，并以 UTF-8 JSON 数组覆盖写入 output_path。只有表头时返回并写入 []。文件或解析错误保持抛出。',
                    'def export_passes(input_path, output_path, minimum)', r'''
            import csv
            import json
            def export_passes(input_path, output_path, minimum):
                with open(input_path, encoding='utf-8', newline='') as stream:
                    result = [row['name'] for row in csv.DictReader(stream) if float(row['score']) >= minimum]
                with open(output_path, 'w', encoding='utf-8') as stream:
                    json.dump(result, stream, ensure_ascii=False)
                return result
        ''', [check('export_passes("teams.csv","selected.json",3)', ['北,区','south'], label='带逗号名称与相等阈值'),
              check('__import__("json").loads(open("selected.json",encoding="utf-8").read())', ['北,区','south'],
                    setup='export_passes("teams.csv","selected.json",3)', label='真正写入 JSON 数组'),
              check('export_passes("empty.csv","selected.json",0)', [], label='只有表头'),
              check('__import__("json").loads(open("selected.json",encoding="utf-8").read())', [],
                    setup='export_passes("teams.csv","selected.json",3)\nexport_passes("empty.csv","selected.json",0)', label='重复运行覆盖旧结果'),
              check('export_passes("missing.csv","selected.json",0)', raises='FileNotFoundError', label='缺文件不吞错')],
                    'CSV 解析负责引号语义，数值转换负责阈值。输出是一份完整 JSON 数组，重复运行必须使用覆盖写。',
                    ['py20', 'py21', 'py24'], fixtures={'teams.csv':'name,score\n"北,区",3\nwest,2.5\nsouth,4\n','empty.csv':'name,score\n'}),
        bank.coding('c05-number-log', 'c05',
                    '定义 sum_number_log(path)，读取 UTF-8 文本。空白行忽略；其余每行尝试转为 float，只接受有限数值。返回 (有效数值之和,无效非空行数)。无法转换、NaN、正负无穷均计为无效；文件不存在时保留 FileNotFoundError。空有效集总和为 0.0。',
                    'def sum_number_log(path)', r'''
            import math
            def sum_number_log(path):
                total = 0.0
                invalid = 0
                with open(path, encoding='utf-8') as stream:
                    for line in stream:
                        text = line.strip()
                        if not text:
                            continue
                        try:
                            value = float(text)
                        except ValueError:
                            invalid += 1
                            continue
                        if not math.isfinite(value):
                            invalid += 1
                        else:
                            total += value
                return total, invalid
        ''', [check('sum_number_log("mixed.txt")', [2.5,3], label='空白、格式错与非有限值'),
              check('sum_number_log("blank.txt")', [0.,0], label='全空白'),
              check('sum_number_log("zeros.txt")', [0.,0], label='合法零和负数不拒绝'),
              check('sum_number_log("missing.txt")', raises='FileNotFoundError', label='缺文件保持异常')],
                    '先跳过空白，再捕获 float 转换的 ValueError；解析成功后还要用 isfinite 排除 NaN 与无穷大。',
                    ['py19', 'py22', 'py23'], fixtures={'mixed.txt':' 1.5 \n\noops\n-2\nnan\n3\ninf\n','blank.txt':'\n \t\n','zeros.txt':'0\n-2\n2\n'}),
    ]
    bank.exam('chapter-c05', 'chapter', '第 5 章 · 文件与错误处理验收', ['c05'], 10, items,
              '用明确的文件格式与异常边界处理数据，验证返回结果及实际写出的文件。')

    items = [
        bank.output('c06-protocol', 'c06', '写出完整标准输出。', r'''
            class Shelf:
                def __init__(self, values):
                    self.values = list(values)
                def __len__(self):
                    return len(self.values)
                def __getitem__(self, index):
                    return self.values[index] * 10
            source = [2, 4]
            shelf = Shelf(source)
            source.append(8)
            print(len(shelf), shelf[-1])
        ''', '2 40', '构造时复制外层列表，所以 source 追加不改变长度；负索引通过 __getitem__ 保留。', ['py27']),
        bank.output('c06-compose', 'c06', '写出完整标准输出。', r'''
            class Pipeline:
                def __init__(self, functions):
                    self.functions = list(functions)
                def __call__(self, value):
                    for function in self.functions:
                        value = function(value)
                    return value
            operations = [lambda x: x - 1, lambda x: x * 3]
            pipeline = Pipeline(operations)
            operations.append(lambda x: x + 100)
            print(pipeline(5))
        ''', '12', '构造时复制变换列表，外部追加不生效；原顺序是先减 1、再乘 3。', ['py29']),
        bank.choice('c06-aggregation', 'c06', '两个批次分别有 2 个和 6 个样本，正确率是 1.0 与 0.5。整体正确率应如何累计？',
                    ['(1.0+0.5)/2 = 0.75', '(2*1.0+6*0.5)/8 = 0.625', '(1.0+0.5)/8 = 0.1875'], 1,
                    '可合并状态是正确数与样本数；两个批次分别正确 2 和 3 个，总共 5/8。', ['py25', 'py26']),
        bank.choice('c06-early-stop', 'c06', '某 early stopping 的 best=0.50、min_delta=0.04、bad=1、patience=2。新 loss=0.47，采用严格 loss<best-min_delta 才改善的规则。这一步应怎样更新？',
                    ['best 改为 0.47，bad 清零，继续', 'best 保留 0.50，bad 变 2，停止', 'best 保留 0.50，bad 仍为 1，继续'], 1,
                    '0.47 并不小于 0.46，改善幅度不足，等待计数应增加到 2。', ['py28']),
        bank.coding('c06-recent-mean', 'c06',
                    '定义 RecentMean(size)。size 为正整数，否则抛 ValueError。支持 add(value)、compute()、reset()：只保留最近 size 个有限数值；compute 返回它们的均值，空状态返回 0.0；reset 清空。实例相互独立。',
                    'class RecentMean(size)', r'''
            class RecentMean:
                def __init__(self, size):
                    if type(size) is not int or size <= 0:
                        raise ValueError('positive integer size required')
                    self.size = size
                    self.values = []
                def add(self, value):
                    self.values.append(value)
                    if len(self.values) > self.size:
                        self.values.pop(0)
                def compute(self):
                    return sum(self.values) / len(self.values) if self.values else 0.0
                def reset(self):
                    self.values = []
        ''', [check('RecentMean(2).compute()', 0., label='空状态'),
              check('meter.compute()', 7., setup='meter=RecentMean(2)\nfor value in [2,6,8]:\n    meter.add(value)', label='只取最近两项'),
              check('meter.compute()', 0., setup='meter=RecentMean(1)\nmeter.add(5)\nmeter.reset()', label='重置'),
              check('second.compute()', 0., setup='first=RecentMean(2)\nsecond=RecentMean(2)\nfirst.add(7)', label='独立实例'),
              check('RecentMean(0)', raises='ValueError', label='拒绝零窗口'),
              check('RecentMean(True)', raises='ValueError', label='布尔值不作大小')],
                    '窗口满后移除最旧项，保证统计的是最近数据；实例状态要在 __init__ 中分别创建。', ['py25', 'py27']),
        bank.coding('c06-transform-dataset', 'c06',
                    '定义 TransformedDataset(rows,transform)。rows 是二维数值列表，元素为不可变数值；transform 是接受一行列表并返回一个结果的函数。构造时复制每一行。支持 len(ds)、ds[i]（包括负索引）：每次把该行的新副本交给 transform，再返回变换结果。输入修改或 transform 原地修改行，都不能污染内部数据。索引越界保留 IndexError。',
                    'class TransformedDataset(rows, transform)', r'''
            class TransformedDataset:
                def __init__(self, rows, transform):
                    self.rows = [list(row) for row in rows]
                    self.transform = transform
                def __len__(self):
                    return len(self.rows)
                def __getitem__(self, index):
                    return self.transform(list(self.rows[index]))
        ''', [check('len(TransformedDataset([[1],[2]],sum))', 2, label='长度协议'),
              check('TransformedDataset([[1,2],[3,4]],sum)[-1]', 7, label='负索引与变换'),
              check('ds[0]', [1,2,9], setup='rows=[[1,2]]\ndef extend(row):\n    row.append(9)\n    return row\nds=TransformedDataset(rows,extend)\nrows[0][0]=88\nds[0]', label='构造及每次访问都隔离'),
              check('TransformedDataset([],sum)[0]', raises='IndexError', label='越界'),
              check('ds[0]', 5, setup='ds=TransformedDataset([[2,3]],sum)', label='独立调用')],
                    '构造时复制保护输入隔离；取出时再复制，保护内部数据不被有副作用的 transform 修改。', ['py27', 'py29', 'py30']),
    ]
    bank.exam('chapter-c06', 'chapter', '第 6 章 · 类与数据流水线验收', ['c06'], 10, items,
              '检查对象协议、加权统计、提前停止规则，并实现有独立状态的数据组件。')


def _cumulative_and_stage(bank):
    items = [
        bank.output('cum03-references', 'c03', '写出完整标准输出，分别跟踪原列表、切片和函数返回值。', r'''
            def append_total(values):
                values.append(sum(values))
                return values[-1]
            source = [2, 5]
            copied = source[:]
            result = append_total(copied)
            print(source)
            print(copied, result)
        ''', '[2, 5]\n[2, 5, 7] 7', '函数修改了 copied，返回新增的总和 7；source 与 copied 的外层容器独立。', ['p1', 'py05', 'p4']),
        bank.output('cum03-lazy', 'c03', '写出完整标准输出，包含生成器执行时的打印。', r'''
            def scaled(values, factor=2):
                for value in values:
                    print('take', value)
                    yield value * factor
            stream = scaled([3, 1], factor=0)
            print('ready')
            print(next(stream))
            print(list(stream))
        ''', 'ready\ntake 3\n0\ntake 1\n[0]', '创建生成器时不执行循环；next 消费第一项，list 消费余项。factor=0 是有效的显式参数。', ['p3', 'py10', 'py11']),
        bank.choice('cum03-default-bug', 'c03', '这段函数中最关键的错误及正确修复是什么？',
                    ['默认 history 只在定义时创建一次；用 None 默认值并在函数内新建列表',
                     'append 不能用于函数参数；改成 print(value)',
                     'return 会导致共享；删掉 return 即可'], 0,
                    '共享来自可变默认对象；删掉 return 不会改变共享状态。None 哨兵能把未传入与显式空列表区分开。',
                    ['py12', 'p4'], code='def archive(value, history=[]):\n    history.append(value)\n    return history'),
        bank.choice('cum03-window-boundary', 'c03', '列表 xs 长度是 4，想检查每个连续 2 项窗口。哪一种起点循环完整且不越界？',
                    ['range(len(xs)-2)', 'range(len(xs)-2+1)', 'range(len(xs)+1)'], 1,
                    '合法起点为 0、1、2，共 4-2+1 个；少加 1 会漏最后窗口。', ['py03', 'py07']),
        bank.coding('cum03-target-runs', 'c03',
                    '定义 target_runs(values,target)，values 为整数列表。按原序返回每一段连续等于 target 的区间长度；非 target 元素分隔区间。不记录长度 0 的区间，不修改输入。例：[1,1,2,1] 对 target=1 返回 [2,1]。',
                    'def target_runs(values, target)', r'''
            def target_runs(values, target):
                result = []
                length = 0
                for value in values:
                    if value == target:
                        length += 1
                    elif length:
                        result.append(length)
                        length = 0
                if length:
                    result.append(length)
                return result
        ''', [check('target_runs([4,4,1,4,2,4,4,4],4)', [2,1,3], label='多段与尾段'),
              check('target_runs([],0)', [], label='空列表'),
              check('target_runs([2,2],1)', [], label='没有目标'),
              check('target_runs([0,0,0],0)', [3], label='目标为零'),
              check('values', [1,1,2], setup='values=[1,1,2]\ntarget_runs(values,1)', label='不修改输入')],
                    '遇到非目标时结算当前段；循环结束后还要结算尾段。不能把所有目标元素的数量当成一段。', ['py02', 'p3', 'py05', 'p4']),
        bank.coding('cum03-chunk-totals', 'c03',
                    '定义 chunk_totals(values,size=2)，返回生成器，依次产出每个连续非重叠批次的总和；最后不足 size 项的批次也保留。values 是有限数值列表，size 必须是正整数（不含 bool），非法时在迭代开始抛 ValueError。不修改 values。',
                    'def chunk_totals(values, size=2)', r'''
            def chunk_totals(values, size=2):
                if type(size) is not int or size <= 0:
                    raise ValueError('positive integer size required')
                for start in range(0, len(values), size):
                    yield sum(values[start:start + size])
        ''', [check('list(chunk_totals([3,5,7,9,2]))', [8,16,2], label='默认大小与尾批'),
              check('list(chunk_totals([2,-2,3],size=3))', [3], label='显式大小'),
              check('list(chunk_totals([],4))', [], label='空列表'),
              check('list(chunk_totals([1],0))', raises='ValueError', label='零大小非法'),
              check('list(chunk_totals([1],True))', raises='ValueError', label='布尔值非法'),
              check('isinstance(chunk_totals([],0),__import__("types").GeneratorType)', True,
                    label='真正生成器且创建时尚不触发参数异常')],
                    '非重叠起点以 size 为步长；yield 产出聚合后的数值，切片自动保留最后不足一批的部分。', ['py03', 'py05', 'p4', 'py10', 'py11', 'py13']),
    ]
    bank.exam('cumulative-03', 'cumulative', '累计测验 · Python 前三章', ['c01','c02','c03'], 25, items,
              '交错检查控制流、序列副本、函数参数和惰性迭代，不依赖原练习的固定数据。')

    items = [
        bank.output('cum06-json-groups', 'c06', '写出完整标准输出，数据均在代码中。', r'''
            import json
            totals = {}
            for line in ['{"team":"b","value":2}', '{"team":"a","value":0}', '{"team":"b","value":3}']:
                row = json.loads(line)
                key = row['team']
                totals[key] = totals.get(key, 0) + row['value']
            print(sorted(totals.items()))
        ''', "[('a', 0), ('b', 5)]", '按字典键分组累加后，sorted 对 (键,值) 元组排序；零值记录应保留。', ['py14', 'py16', 'py20']),
        bank.output('cum06-instance-state', 'c06', '写出两行完整输出。', r'''
            class Counter:
                def __init__(self):
                    self.values = []
                def add(self, value):
                    self.values.append(value)
                def total(self):
                    return sum(self.values)
            first = Counter()
            second = Counter()
            first.add(3)
            first.add(-1)
            print(first.total())
            print(second.total())
        ''', '2\n0', '每次构造都创建新的列表；first 的两次更新不会影响 second。sum([]) 为 0。', ['p4', 'py25']),
        bank.choice('cum06-leakage', 'c06', '同一病人的多条记录高度相关，计划用验证集评估对新病人的效果。哪种划分最符合目标？',
                    ['逐条随机划分所有记录，不记录病人标识', '先按病人标识分组，同一病人的全部记录只进入一侧',
                     '把每位病人的第一条放训练，其余放验证'], 1,
                    '目标是新病人泛化，同一病人的相关记录应保持组隔离；逐条随机或按条数拆分都会让病人信息跨两侧。', ['py30']),
        bank.choice('cum06-mutation', 'c06', '一个数据集构造函数保存 self.rows=list(rows)。输入 rows=[[1,2]]。哪项风险仍然存在？',
                    ['外层列表仍是同一个对象', '内层行仍共享，调用者修改 rows[0][0] 会污染内部数据',
                     '数值 1 会变成字符串'], 1,
                    'list(rows) 只复制外层；复制每行才能隔离二维数值数据。存在更深层可变结构时还需考虑深复制。', ['py17', 'py27']),
        bank.coding('cum06-counter-diff', 'c06',
                    '定义 counter_diff(before,after)。两者为 {字符串:非负整数} 字典。返回包含双方所有键的新字典，每键对应 {before:旧计数,after:新计数,delta:新减旧}。任一侧缺键按 0 处理，显式零值保留；不得修改输入。返回字典的键顺序无要求。',
                    'def counter_diff(before, after)', r'''
            def counter_diff(before, after):
                result = {}
                for key in set(before) | set(after):
                    old = before.get(key, 0)
                    new = after.get(key, 0)
                    result[key] = {'before': old, 'after': new, 'delta': new - old}
                return result
        ''', [check('counter_diff({"a":3,"b":0},{"a":1,"c":5})',
                     {'a':{'before':3,'after':1,'delta':-2},'b':{'before':0,'after':0,'delta':0},'c':{'before':0,'after':5,'delta':5}}, label='新增删除与零值'),
              check('counter_diff({},{})', {}, label='双方为空'),
              check('counter_diff({"x":2},{"x":2})', {'x':{'before':2,'after':2,'delta':0}}, label='计数无变化'),
              check('[before,after]', [{'x':1},{'y':2}], setup='before={"x":1}\nafter={"y":2}\nr=counter_diff(before,after)\nr["x"]["before"]=99', label='输入独立')],
                    '键集合是并集，缺失项通过 get 补零；每个结果记录重新创建，避免与输入共享可变状态。', ['py08', 'py14', 'py17']),
        bank.coding('cum06-latest-log', 'c06',
                    '定义 read_latest_metrics(path)，读取 UTF-8 JSONL。有效行必须是字典，run 为字符串，metric 为有限的内置 int/float 且不含 bool。空白行忽略；坏 JSON、非字典或字段不合约的非空行计为无效。返回 (按 run 保留最后一次有效 metric 的字典,无效行数)。无效行不得覆盖此前有效值。文件错误保持抛出。',
                    'def read_latest_metrics(path)', r'''
            import json
            import math
            def read_latest_metrics(path):
                latest = {}
                invalid = 0
                with open(path, encoding='utf-8') as stream:
                    for line in stream:
                        if not line.strip():
                            continue
                        try:
                            row = json.loads(line)
                        except json.JSONDecodeError:
                            invalid += 1
                            continue
                        if not isinstance(row, dict):
                            invalid += 1
                            continue
                        value = row.get('metric')
                        valid_number = type(value) is int or (type(value) is float and math.isfinite(value))
                        if not isinstance(row.get('run'), str) or not valid_number:
                            invalid += 1
                            continue
                        latest[row['run']] = value
                return latest, invalid
        ''', [check('read_latest_metrics("latest.jsonl")', [{'a':.3,'b':0},3], label='最后有效值与坏行统计'),
              check('read_latest_metrics("empty.jsonl")', [{},0], label='空白文件'),
              check('read_latest_metrics("bad.jsonl")', [{},3], label='非法字段与非有限指标'),
              check('read_latest_metrics("missing.jsonl")', raises='FileNotFoundError', label='缺文件')],
                    '先确认结构与字段有效，再替换该 run 的旧值。bool 是 int 的子类，精确类型检查才能把它排除。',
                    ['py14', 'py18', 'py19', 'py22', 'py23'], fixtures={
                        'latest.jsonl':'{"run":"a","metric":1}\n{"run":"b","metric":0}\n{"run":"a","metric":0.3}\n{"run":"a","metric":true}\nbroken\n[]\n\n',
                        'empty.jsonl':' \n\t\n',
                        'bad.jsonl':'{"run":2,"metric":1}\n{"run":"x","metric":NaN}\n{"run":"x"}\n'}),
    ]
    bank.exam('cumulative-06', 'cumulative', '累计测验 · Python 六章联考',
              ['c01','c02','c03','c04','c05','c06'], 25, items,
              '把结构验证、字典聚合、真实文件和对象状态放在同一份卷中复用。')

    items = [
        bank.output('stage-return-alias', 'c06', '写出完整标准输出。', r'''
            def update(values, increment=1):
                copied = values[:]
                for index in range(len(copied)):
                    copied[index] += increment
                return copied
            original = [1, 4]
            result = update(original, increment=0)
            result.append(8)
            print(original)
            print(result)
        ''', '[1, 4]\n[1, 4, 8]', '传入零不会使用默认增量；函数返回外层副本，追加结果不改原列表。', ['p1', 'py03', 'py05', 'py10']),
        bank.output('stage-stable-ranking', 'c06', '写出完整标准输出。', r'''
            scores = {'beta': [2, 4], 'alpha': [3], 'gamma': [1, 5]}
            names = sorted(scores, key=lambda name: (-sum(scores[name]) / len(scores[name]), name))
            print(names)
            print([len(scores[name]) for name in names])
        ''', "['alpha', 'beta', 'gamma']\n[1, 2, 2]", '三组均值都为 3，所以按名称升序；第二行的组大小不应影响并列规则。', ['py15', 'py16']),
        bank.choice('stage-config-isolation', 'c06', '配置包含任意深度的字典与列表，且无循环引用。新实验配置修改后必须完全不影响默认配置。哪项足够？',
                    ['new = defaults', 'new = defaults.copy()', 'new = copy.deepcopy(defaults)'], 2,
                    '赋值共享全部对象，浅复制只分离外层；deepcopy 才能隔离这里任意深度的可变对象。', ['py05', 'py17']),
        bank.choice('stage-exception-scope', 'c06', '函数需要：缺文件时抛 FileNotFoundError，JSON 格式错时抛 JSONDecodeError，合法但缺 lr 时用默认值。哪个方案符合？',
                    ['用 with open + json.load，再用 config.get("lr",默认值)，不捕获这两个错误',
                     'except Exception 后返回默认配置', '对 JSON 字符串调用 dict(text)'], 0,
                    '缺失键的默认值与读取失败是不同情形；只用 get 处理缺字段，不吞掉文件和格式错误。', ['py19', 'py20', 'py23']),
        bank.choice('stage-validation-boundary', 'c06', '同一文档切成多个片段后训练分类器，验证集要评估对新文档的效果。哪项最可靠？',
                    ['只确认训练与验证列表不是同一个对象', '按 document_id 分组划分，拒绝重复 sample_id，并复制输出记录',
                     '把原列表浅复制两次，再独立打乱'], 1,
                    '对象不同不代表信息独立；需要组隔离、样本唯一性和数据副本隔离共同保证划分契约。', ['py17', 'py27', 'py30']),
        bank.coding('stage-session-summary', 'c06',
                    '定义 session_summary(events)。每项是 {session:字符串,value:有限数值}。按 session 首次出现顺序返回列表，每项为 {session,count,total,last}：记录数、数值总和、该 session 最后一次的 value。空输入返回 []；不得修改或复用输入字典。',
                    'def session_summary(events)', r'''
            def session_summary(events):
                summaries = {}
                for event in events:
                    key = event['session']
                    if key not in summaries:
                        summaries[key] = {'session': key, 'count': 0, 'total': 0, 'last': event['value']}
                    row = summaries[key]
                    row['count'] += 1
                    row['total'] += event['value']
                    row['last'] = event['value']
                return list(summaries.values())
        ''', [check('session_summary([{"session":"b","value":2},{"session":"a","value":0},{"session":"b","value":-1}])',
                     [{'session':'b','count':2,'total':1,'last':-1},{'session':'a','count':1,'total':0,'last':0}], label='交错分组、首次顺序与最后值'),
              check('session_summary([])', [], label='空事件'),
              check('session_summary([{"session":"","value":0}])', [{'session':'','count':1,'total':0,'last':0}], label='空名称和零值合法'),
              check('events', [{'session':'x','value':2}], setup='events=[{"session":"x","value":2}]\nr=session_summary(events)\nr[0]["total"]=99', label='返回记录不复用输入')],
                    '字典保存首次插入顺序；每组状态分别累计 count、total，并在每次事件时替换 last。', ['py06', 'py14', 'py15', 'py17']),
        bank.coding('stage-prediction-ledger', 'c06',
                    '定义 PredictionLedger，支持 add(preds,labels)、report()、reset()。add 的两个输入是列表，长度须一致，所有元素须为内置整数 0 或 1（不含 bool），否则抛 ValueError 且不改变已有统计。report 返回新的 {count,correct,accuracy} 字典；无样本 accuracy=0.0。多次 add 等价于拼接样本；reset 清空；实例独立。',
                    'class PredictionLedger', r'''
            class PredictionLedger:
                def __init__(self):
                    self.reset()
                def add(self, preds, labels):
                    if len(preds) != len(labels):
                        raise ValueError('length mismatch')
                    if any(type(value) is not int or value not in (0, 1) for value in preds + labels):
                        raise ValueError('binary integers required')
                    self.count += len(labels)
                    self.correct += sum(pred == label for pred, label in zip(preds, labels))
                def report(self):
                    return {'count': self.count, 'correct': self.correct,
                            'accuracy': self.correct / self.count if self.count else 0.0}
                def reset(self):
                    self.count = 0
                    self.correct = 0
        ''', [check('PredictionLedger().report()', {'count':0,'correct':0,'accuracy':0.}, label='空账本'),
              check('ledger.report()', {'count':4,'correct':3,'accuracy':.75},
                    setup='ledger=PredictionLedger()\nledger.add([1,0,1],[1,1,1])\nledger.add([0],[0])', label='不等批次按样本累计'),
              check('ledger.add([1],[1,0])', raises='ValueError', setup='ledger=PredictionLedger()', label='拒绝长度不一致'),
              check('ledger.add([True],[1])', raises='ValueError', setup='ledger=PredictionLedger()', label='拒绝 bool'),
              check('ledger.report()', {'count':1,'correct':1,'accuracy':1.}, setup='ledger=PredictionLedger()\nledger.add([1],[1])\ntry:\n    ledger.add([1,2],[1,0])\nexcept ValueError:\n    pass', label='失败更新不污染已有统计'),
              check('ledger.report()', {'count':0,'correct':0,'accuracy':0.}, setup='ledger=PredictionLedger()\nledger.add([1],[1])\nledger.reset()', label='重置'),
              check('ledger.report()', {'count':1,'correct':1,'accuracy':1.},
                    setup='ledger=PredictionLedger()\nledger.add([1],[1])\nsnapshot=ledger.report()\nsnapshot["count"]=99', label='返回报告副本'),
              check('second.report()', {'count':0,'correct':0,'accuracy':0.},
                    setup='first=PredictionLedger()\nsecond=PredictionLedger()\nfirst.add([1],[1])', label='实例状态独立')],
                    '先完整验证批次，再改计数，才能保证失败操作不留下部分状态。全局准确率用累计正确数除以累计样本数。', ['p6', 'py13', 'py23', 'py25', 'py26']),
        bank.coding('stage-team-export', 'c06',
                    '定义 export_team_totals(input_path,output_path)。读取 UTF-8 CSV，列 team、amount；team 作为字符串原样使用，amount 保证是有限数值字符串。按 team 累加 amount，返回 {team:总额}，并将同一字典以 UTF-8 JSON 覆盖写入 output_path。空数据写 {}；重复执行不追加；文件错误保持抛出。',
                    'def export_team_totals(input_path, output_path)', r'''
            import csv
            import json
            def export_team_totals(input_path, output_path):
                totals = {}
                with open(input_path, encoding='utf-8', newline='') as stream:
                    for row in csv.DictReader(stream):
                        team = row['team']
                        totals[team] = totals.get(team, 0) + float(row['amount'])
                with open(output_path, 'w', encoding='utf-8') as stream:
                    json.dump(totals, stream, ensure_ascii=False)
                return totals
        ''', [check('export_team_totals("amounts.csv","totals.json")', {'北,组':1.5,'south':0.}, label='带逗号组名、负值与零'),
              check('__import__("json").loads(open("totals.json",encoding="utf-8").read())', {'北,组':1.5,'south':0.},
                    setup='export_team_totals("amounts.csv","totals.json")', label='实际 JSON 与返回一致'),
              check('export_team_totals("empty.csv","totals.json")', {}, label='空数据'),
              check('__import__("json").loads(open("totals.json",encoding="utf-8").read())', {},
                    setup='export_team_totals("amounts.csv","totals.json")\nexport_team_totals("empty.csv","totals.json")', label='覆盖旧输出'),
              check('export_team_totals("missing.csv","totals.json")', raises='FileNotFoundError', label='保留文件异常')],
                    'CSV 的字段引用规则交给 DictReader；每组单独累加，再一次性覆盖写出完整 JSON 对象。', ['py14', 'py15', 'py20', 'py21', 'py24'],
                    fixtures={'amounts.csv':'team,amount\n"北,组",2.5\nsouth,0\n"北,组",-1\n','empty.csv':'team,amount\n'}),
    ]
    bank.exam('stage-python', 'stage', 'Python 阶段考核 · 独立实验脚本',
              ['c01','c02','c03','c04','c05','c06'], 45, items,
              '在新情境中独立追踪语义、判断实现边界，并完成聚合函数、状态组件与真实文件转换。')


def _reviews(bank):
    bank.review(
        bank.output('review-c01-control', 'c01', '写出完整标准输出。', r'''
            count = 0
            for number in [5, 2, 8, 0, 7]:
                if number == 0:
                    break
                if number >= 5:
                    count += 1
            print(count)
        ''', '2', '只检查 0 之前的 5、2、8，其中 5 与 8 达到阈值；后面的 7 不参与。', ['p1', 'py02', 'p3', 'py04']),
        bank.coding('review-c01-duration', 'c01',
                    '标准输入是一行非负整数 seconds。把它换算为完整分钟数和剩余秒数，用一个空格分隔输出。例如 125 秒输出 2 5。只输出数字，不输出单位或提示。',
                    '完整程序 · 数值转换 / // / %', r'''
            seconds = int(input())
            print(seconds // 60, seconds % 60)
        ''', [program('125\n', '2 5', '跨多分钟'), program('0\n', '0 0', '零秒'),
              program('59\n', '0 59', '不足一分钟'), program('60\n', '1 0', '恰好一分钟')],
                    '整除得到完整分钟，余数得到不足一分钟的秒数，两者满足 seconds=minutes*60+remainder。', ['py01']),
        bank.output('review-c02-inner-copy', 'c02', '写出完整标准输出。', r'''
            rows = [[1], [2]]
            copied = rows[:]
            copied[0].append(9)
            copied.append([3])
            print(len(rows))
            print(rows[0])
        ''', '2\n[1, 9]', '外层切片隔离了 append 行操作，但原有内层列表仍共享，所以第一行变化。', ['p2', 'py05', 'py09']),
        bank.coding('review-c02-differences', 'c02',
                    '标准输入为一行整数，可为空。按原序输出每对相邻数的“后项减前项”，用一个空格分隔。少于两个数时输出空行。不得额外输出列表括号。',
                    '完整程序 · 相邻位置 / 空边界', r'''
            values = list(map(int, input().split()))
            result = []
            for index in range(1, len(values)):
                result.append(str(values[index] - values[index - 1]))
            print(' '.join(result))
        ''', [program('3 8 6 6\n', '5 -2 0', '正负与零差'),
              program('9\n', '', '单项'), program('\n', '', '空行'),
              program('-4 -1\n', '3', '负输入')],
                    '第一个合法后项索引是 1；每对相邻数只产出一个差，所以输出项数比输入少 1。', ['p2', 'py05', 'py07']),
        bank.choice('review-c03-none', 'c03', '函数默认 items=None；调用者显式传入 [] 时，函数要原地更新这个空列表。应如何判断需要新建容器？',
                    ['if not items', 'if items is None', 'if len(items)==0'], 1,
                    '只有 None 表示未提供。空列表虽然为假，仍是调用者主动提供并希望更新的容器。', ['py10', 'py12']),
        bank.coding('review-c03-clamp', 'c03',
                    '定义 clamp_values(values,low=0,high=1)，把每个有限数值限制到闭区间 [low,high]，返回新列表。low、high 为有限数值；low>high 抛 ValueError。不得修改 values；low==high 合法。',
                    'def clamp_values(values, low=0, high=1)', r'''
            def clamp_values(values, low=0, high=1):
                if low > high:
                    raise ValueError('invalid interval')
                return [max(low, min(value, high)) for value in values]
        ''', [check('clamp_values([-2,.4,3])', [0,.4,1], label='默认区间'),
              check('clamp_values([-3,0,5],low=-1,high=2)', [-1,0,2], label='关键字参数'),
              check('clamp_values([1,2],2,2)', [2,2], label='零宽区间'),
              check('clamp_values([],2,1)', raises='ValueError', label='空输入也验证区间'),
              check('xs', [-1,2], setup='xs=[-1,2]\nout=clamp_values(xs)\nout.append(9)', label='不修改或复用输入')],
                    '先验证区间，再逐项做截断；返回新列表，空数据也不能跳过非法参数检查。', ['p4', 'py10', 'py13']),
        bank.output('review-c04-get', 'c04', '写出完整标准输出。', r'''
            settings = {'retry': 0, 'mode': None}
            print(settings.get('retry', 3))
            print(settings.get('mode', 'auto'))
            print(settings.get('timeout', 9))
        ''', '0\nNone\n9', 'get 只在键不存在时使用默认值；已存在的 0 和 None 都原样保留。', ['p5', 'py17']),
        bank.coding('review-c04-required-key', 'c04',
                    '定义 first_missing(config,required)，config 为字典，required 为字符串列表。按 required 的顺序返回第一个不存在于 config 的键；所有键都存在时返回 None。值为 None、0 或空字符串都算存在；不得修改输入。',
                    'def first_missing(config, required)', r'''
            def first_missing(config, required):
                for key in required:
                    if key not in config:
                        return key
                return None
        ''', [check('first_missing({"x":0},["x","y","z"])', 'y', label='首个缺失键'),
              check('first_missing({"x":None,"y":""},["x","y"])', None, label='空值也算存在'),
              check('first_missing({},[])', None, label='没有必需键'),
              check('first_missing({},["b","a"])', 'b', label='按要求顺序而非排序')],
                    '成员判断检查键是否存在；不能用 config.get(key) 的真假值区分缺失与合法空值。', ['p5', 'py14']),
        bank.choice('review-c05-json-value', 'c05', '一份按行读取的日志依次含空白行、[1,2]、{"ok":true}、broken；约定只接受 JSON 字典，空白忽略。有效记录数和无效行数分别是多少？',
                    ['1 和 2', '2 和 1', '1 和 3'], 0,
                    '数组是合法 JSON 但不符合记录结构，broken 是坏 JSON，两者都计无效；空白行不计。', ['py20', 'py22', 'py23']),
        bank.coding('review-c05-enabled', 'c05',
                    '定义 load_enabled_names(path)。文件是 UTF-8 JSON 数组，每项保证是字典，含字符串 name，可选 enabled。仅当 enabled 的值恰好为布尔 True 时保留 name，按原序返回列表；缺失、False、数字 1 都不保留。文件和 JSON 格式错误保持抛出。',
                    'def load_enabled_names(path)', r'''
            import json
            def load_enabled_names(path):
                with open(path, encoding='utf-8') as stream:
                    rows = json.load(stream)
                return [row['name'] for row in rows if row.get('enabled') is True]
        ''', [check('load_enabled_names("flags.json")', ['b','e'], label='精确布尔状态与原序'),
              check('load_enabled_names("empty.json")', [], label='空数组'),
              check('load_enabled_names("missing.json")', raises='FileNotFoundError', label='缺文件'),
              check('load_enabled_names("invalid.json")', raises='JSONDecodeError', label='坏 JSON')],
                    '本题要求的是恰好 True，用 is True 区分布尔开关与数值 1，不能仅凭真假值筛选。', ['py20', 'py23'],
                    fixtures={'flags.json':'[{"name":"a","enabled":1},{"name":"b","enabled":true},{"name":"c"},{"name":"d","enabled":false},{"name":"e","enabled":true}]',
                              'empty.json':'[]','invalid.json':'{broken'}),
        bank.output('review-c06-shared-argument', 'c06', '写出完整标准输出。', r'''
            class Bag:
                def __init__(self, values):
                    self.values = list(values)
                def take(self):
                    return self.values[:]
            bag = Bag([7, 8])
            first = bag.take()
            first.append(9)
            print(bag.take())
        ''', '[7, 8]', 'take 每次返回外层副本；这些行内元素是不可变整数，调用者追加不会改变内部列表。', ['py25', 'py27']),
        bank.coding('review-c06-range', 'c06',
                    '定义 RunningRange，支持 add(value)、bounds()、reset()。value 为有限数值；bounds 返回目前所有输入的 (最小值,最大值)，空状态返回 None。reset 清空；实例独立。',
                    'class RunningRange', r'''
            class RunningRange:
                def __init__(self):
                    self.reset()
                def add(self, value):
                    if self.minimum is None:
                        self.minimum = value
                        self.maximum = value
                    else:
                        self.minimum = min(self.minimum, value)
                        self.maximum = max(self.maximum, value)
                def bounds(self):
                    if self.minimum is None:
                        return None
                    return self.minimum, self.maximum
                def reset(self):
                    self.minimum = None
                    self.maximum = None
        ''', [check('RunningRange().bounds()', None, label='空状态'),
              check('state.bounds()', [-4,7], setup='state=RunningRange()\nfor value in [2,7,-4,0]:\n    state.add(value)', label='正负值与完整范围'),
              check('state.bounds()', [0,0], setup='state=RunningRange()\nstate.add(0)', label='零作为首值'),
              check('state.bounds()', None, setup='state=RunningRange()\nstate.add(4)\nstate.reset()', label='重置'),
              check('second.bounds()', None, setup='first=RunningRange()\nsecond=RunningRange()\nfirst.add(9)', label='实例独立')],
                    '空状态使用 None，不能把零当成未初始化；之后分别维护全局最小值和最大值。', ['py25', 'py26', 'py28']),
    )
