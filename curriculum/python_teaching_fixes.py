"""Small, lesson-specific teaching bridges from the 36-lesson semantic review.

Load after python_audit_fixes.py and before finish.py's final per-lesson loop.
Task IDs, original six task contracts, worked-example answers and quizzes stay
unchanged. The file defines text/code; it does not execute teaching examples.
"""
python_teaching = {lesson['id']: lesson for lesson in LESSONS if lesson['runtime'] == 'python'}

for ident, steps, boundary in [
    ('p1',
     '按顺序跟踪 score：先保存初值，再用旧值计算 score + 5，最后把新值写回同一个名字。讲解代码用初值 70；编程任务用初值 75，两段程序需要分别计算。',
     'print(score) 显示执行到这一行时保存的值。试着把初值换成 0，观察加 5 的规则是否保持一致。'),
    ('p2',
     '先创建 scores 列表。len(scores) 统计元素数量；scores[0] 读第一项，scores[-1] 读最后一项。主示例修改的是 scores[1]，不会连带修改最后一项。',
     '编程任务要求两次 print：第一行是长度，第二行是最后一个分数。长度 3 不代表存在索引 3，正索引只到 2。'),
    ('p3',
     'for score in scores: 每轮把下一项赋给 score，缩进中的 print(score + 5) 计算并显示本轮结果。这个表达式不会把 scores 原列表的元素改掉。',
     '任务要逐项输出 65、80、95，各占一行。把 print 移出循环只会在循环结束后执行一次；要根据缩进判断属于哪一层。'),
    ('p4',
     '前面的切片题已经使用过 def 和 return，这里把函数调用系统串起来：参数 values 接收列表，sum(values) 得总和，len(values) 得数量，除法计算均值。',
     '本题保证 values 非空。mean 的返回值要能赋给 y 并参与后续计算；只在函数里 print 均值，会让 y 得到 None。'),
    ('p5',
     '先在函数里设 count=0，再逐条访问 record["loss"]。只有 loss < threshold 才把 count 加 1，循环结束后 return count，而不是返回最后一条的判断。',
     '这里是严格小于：loss 与 threshold 相等不计入。空 records 没有循环项，初始的 0 就是结果；model 等其他字段不参与计数。'),
    ('p6',
     'for pred, label in zip(preds, labels): 每轮取相同位置的一对数。用 pred == label 判断是否相等，把 True 对应的次数累计到 correct，再除以总样本数。',
     '本题保证两列表等长；双空时提前 return 0.0，避免除以零。第二个例题故意给不同长度，只演示 zip 会截断，不把它当作本题的合法输入。'),
]:
    item = python_teaching[ident]
    item['teaching'][1]['body'] = steps
    item['teaching'][2]['body'] = boundary

python_teaching['p4']['cpp'] = 'def add_bonus(score): 定义函数；这里不写返回值类型。任务需要把结果交给调用者，因此函数体应显式 return。'

# A learner first encounters an independently authored function in chapter 2.
first_function = python_teaching['py05']
first_function['teaching'] = [
    {'title': '第一次从空白写函数', 'body':
     '这一关第一次要求你自己定义函数。def take_first(xs, n): 是函数头，xs 和 n 是调用者传入的参数；冒号后换行，函数体统一缩进 4 个空格。只定义函数不会自动调用它。'},
    {'title': '用切片创建外层副本', 'body':
     'xs[:n] 取前 n 项并新建外层列表；n 超过长度时取到末尾，n=0 时得到空列表。把 b=xs 直接赋给另一个名字只会产生别名。'},
    {'title': '返回值与显示结果', 'body':
     '函数体用 return 把新列表交给调用者；result = take_first(xs, n) 会接住它。print 只负责显示，不能代替 return。本题评测会传入参数，不需要你再用 input 读取。后面的函数章节会系统讲参数、生成器和状态。'},
    {'title': '独立到哪一层', 'body':
     '评测会向返回列表追加元素，确认原列表长度不变；只要求外层列表独立。切片不是递归深复制，内部如果仍是可变对象，需要在后续复制章节进一步处理。'},
]
first_function['example'] = clean('''
def copy_prefix(values, count):
    return values[:count]

original = [10, 20, 30]
copied = copy_prefix(original, 2)
copied[0] = 99
print(original)
print(copied)
''')

# Introduce shorthand where it first appears; a normal loop remains valid.
python_teaching['py10']['teaching'].append({'title':'先用普通循环，再读简写', 'body':
 '可以先创建 result=[]，循环每个 value，把 value*factor+bias 追加到 result，最后 return result。参考实现中的 [value*factor+bias for value in values] 是列表推导式，表达的是同一过程，不是必须背下来的特殊解法。'})
python_teaching['py15']['teaching'].append({'title':'读懂字典推导式', 'body':
 '示例中的 {k: totals[k]/counts[k] for k in totals} 是字典推导式：遍历每个分组 k，把该组均值作为结果字典的值。也可以用普通 for 循环逐项写 result[k]=totals[k]/counts[k]；两种写法都要使用该组自己的次数。'})
python_teaching['py16']['teaching'].append({'title':'lambda 在排序中做什么', 'body':
 'lambda r: (-r["score"], r["name"]) 是一个只含表达式的小函数：接收一条 r，返回用于比较的元组。它等价于定义一个普通 sort_key(r) 并 return 这个元组；把函数本身传给 key，不是提前调用它得到一个排序结果。'})
python_teaching['py17']['teaching'].append({'title':'递归只发生在双方都是字典时', 'body':
 '递归就是函数在更小的一层配置上调用自己。对某个键，默认值与覆盖值同时是字典才继续合并；只要其中一边不是字典，就用覆盖值的深副本替换，这也是递归停止继续深入的条件。'})

# The file lesson's headline should be demonstrated by a real, self-contained
# read. The temporary directory is setup for this example, not a student task.
python_teaching['py20']['example'] = clean('''
import json
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "sample.json"
    path.write_text('{"name":"示例实验","lr":0.1}', encoding="utf-8")
    with open(path, encoding="utf-8") as stream:
        config = json.load(stream)
    print(config["name"], config.get("lr", 0.001))
''')
python_teaching['py20']['teaching'].append({'title':'文件读取与文本解析分两步理解', 'body':
 '上方先在自动清理的临时目录创建演示文件，再用 with open 和 json.load 真正读取它；临时目录仅用于让例子安全、自足。题目附件由运行器提供，你只需读取传入的 path。下面的 loads 小例题单独演示已有 JSON 文本的解析，不代表文件读取已经发生。'})

python_teaching['py25']['example'] = clean('''
class WeightedTracker:
    def __init__(self):
        self.total = 0.0
        self.count = 0

    def update(self, value, n):
        self.total += value * n
        self.count += n

    def compute(self):
        return self.total / self.count if self.count else 0.0

meter = WeightedTracker()
meter.update(1, 1)
meter.update(3, 3)
print(meter.compute())
''')
python_teaching['py25']['teaching'].append({'title':'实例怎样调用方法', 'body':
 'meter=WeightedTracker() 会创建实例并调用 __init__；meter.update(1,1) 调用时，Python 自动把 meter 作为 self，所以不用再手动传 self。两次更新累计总和 10、样本数 4，compute 返回 2.5。任务还需实现 reset，把同一实例恢复到空状态。'})

python_teaching['py27']['task'] = (
 '定义 ListDataset(features,labels)，features 为二维数值列表，行元素是不可变数值；labels 的元素为基本值。'
 '支持 len(ds)、ds[i]。数据长度不一致抛 ValueError；构造与取出时均复制特征行。'
)
python_teaching['py27']['teaching'].append({'title':'复制契约的范围', 'body':
 '本题每行只含不可变数值，因此复制外层特征列表和每一行就足够。若行内还有嵌套可变列表，浅复制不能保证完全隔离，那是上一章深复制问题的扩展，不是本题输入。'})

python_teaching['py28']['intro'] = (
 'Early stopping 持续观察验证指标，而不是只比较相邻两轮。这里维护用于判断显著改善的 best 基准；'
 '只有 loss < best-min_delta 时才更新 best 并清零等待计数。'
)
python_teaching['py28']['teaching'][0]['body'] = python_teaching['py28']['intro']
python_teaching['py28']['teaching'].append({'title':'best 的精确含义', 'body':
 '当 min_delta>0，某次很小的下降不会更新 best，之后仍与上次达到显著改善门槛的基准比较。min_delta=0 时，best 才逐次记录严格下降后的历史最小值；不要把两个定义混用。'})
