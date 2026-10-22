"""Corrections and contract regressions from the independent Python content audit.

Loaded by finish.py before examples/quizzes are finalized. Keep original exercise
IDs and original six Python task contracts intact so saved work remains usable.
"""

python_lessons = {item['id']: item for item in LESSONS if item['runtime'] == 'python'}

# Existing lessons previously used a non-output placeholder in the output field.
for ident, output in {
    'p1': '75',
    'p2': '60\n90',
    'p3': '2\n4\n6\n完成',
    'p4': '75',
    'p5': '达标',
    'p6': 'True\nFalse\nTrue',
}.items():
    python_lessons[ident]['examples'][0]['output'] = output
    python_lessons[ident]['examples'][0]['explanation'] = (
        '先按行预测结果，再用「运行示例」核对上方的完整输出。'
        '本例使用自己的数据；编程任务可能使用另一组输入，要分别阅读。'
    )

# "0 is None" produces a SyntaxWarning on supported Python versions. Compare a
# variable to None so the useful is/boolean distinction has no extra stderr.
python_lessons['py10']['examples'][1] = example(
    '零值不是缺失值',
    'value = 0\nprint(value is None, bool(value))',
    'False False',
    '零的真假值是假，但它并不是 None。用 is None 判断缺失值，保留合法的零。',
)

# NaN is neither <0 nor >1. Reject values that fail the positive range test.
probability = python_lessons['py13']
probability['solution'] = clean('''
def mean_probability(xs):
    if not xs or any(not 0 <= x <= 1 for x in xs):
        raise ValueError("invalid probabilities")
    return sum(xs) / len(xs)
''')
probability['task'] = (
    '定义 mean_probability(xs)，xs 是数值列表或元组。只接受非空且所有元素都在 [0,1] '
    '的输入，返回均值；空输入、NaN、正负无穷或元素越界均抛 ValueError。'
)
probability['hints'][1] = (
    '检查所有数都满足 0 <= x <= 1；任意一个不满足就拒绝。'
    '不要只检查 x < 0 or x > 1，因为 NaN 的这两个比较都为 False。'
)
probability['teaching'][1]['body'] = probability['hints'][0] + ' ' + probability['hints'][1]
probability['examples'][0]['code']='xs=[0.2,1.3]\nprint(any(not 0 <= x <= 1 for x in xs))\n'
probability['tests'].extend([
    case('mean_probability([float("nan")])', raises='ValueError', label='NaN 不是合法概率'),
    case('mean_probability([float("inf")])', raises='ValueError', label='正无穷非法'),
    case('mean_probability([float("-inf")])', raises='ValueError', label='负无穷非法'),
    case('mean_probability((0, 1))', 0.5, label='元组也可求均值'),
])

# Say what is returned, rather than leaving readers to infer epoch from tests.
checkpoint = python_lessons['py18']
checkpoint['task'] = (
    '定义 best_checkpoint(records)，记录含 epoch、status，可选 loss。只保留 status 为 ok '
    '且 loss 为有限 int/float（不含 bool）的记录。选择 loss 最小的记录；loss 并列时选择 '
    'epoch 最早的一条，返回这条记录的 epoch。无有效记录返回 None。'
)
checkpoint['hints'][1] = '候选按 (loss,epoch) 升序选择，返回胜出记录的 epoch，而不是 loss 或整个字典。'
checkpoint['teaching'][1]['body'] = checkpoint['hints'][0] + ' ' + checkpoint['hints'][1]
checkpoint['tests'].extend([
    case('best_checkpoint([{"epoch":1,"status":"ok","loss":0.9},{"epoch":5,"status":"ok","loss":0.1}])',
         5, label='先比较 loss，不能只取最早 epoch'),
    case('best_checkpoint([{"epoch":1,"status":"ok","loss":float("inf")},{"epoch":2,"status":"ok","loss":0.4}])',
         2, label='无限值不参与选择'),
    case('best_checkpoint([{"epoch":1,"status":"ok","loss":"0.1"},{"epoch":2,"status":"ok","loss":0.4}])',
         2, label='数值字符串不作指标'),
])

# This is a validation exercise: invalid shape/type must give AssertionError,
# not accidental TypeError from len(row), and a third dimension is not 2-D.
validation = python_lessons['py23']
validation['task'] = (
    '实现 validate_batch(features,labels)。features 与 labels 都必须是列表或元组；'
    'features 的每行也必须是列表或元组，各行等宽，行内元素必须是内置 int/float（不含 bool）。'
    'labels 的长度必须等于行数，且每个标签为非负内置 int（不含 bool）。'
    '合法返回 True，任一条件不满足均抛 AssertionError。两个空序列合法；非空批次允许各行宽度都为 0。'
)
validation['solution'] = clean('''
def validate_batch(features, labels):
    assert isinstance(features, (list, tuple))
    assert isinstance(labels, (list, tuple))
    assert len(features) == len(labels)
    assert all(isinstance(row, (list, tuple)) for row in features)
    if features:
        width = len(features[0])
        assert all(len(row) == width for row in features)
    assert all(type(value) in (int, float) for row in features for value in row)
    assert all(type(label) is int and label >= 0 for label in labels)
    return True
''')
validation['hints'] = [
    '先验证 features、labels 以及每个特征行的容器类型，再调用 len，避免非法结构意外抛出 TypeError。',
    '用 assert 分别检查样本数、等宽行、内置数值特征和非负整数标签；bool 不作为特征数值或标签。',
    '两个空序列合法；[[],[]] 配 [0,1] 也合法。任一约定不满足时抛 AssertionError，而不是返回 False。',
]
validation['teaching'][1]['body'] = validation['hints'][0] + ' ' + validation['hints'][1]
validation['teaching'][2]['body'] = validation['hints'][2]
validation['pitfalls'] = [validation['hints'][2]]
validation['tests'].extend([
    case('validate_batch([1],[0])', raises='AssertionError', label='一维特征必须明确拒绝'),
    case('validate_batch([[[1]]],[0])', raises='AssertionError', label='三维特征不是二维数值批次'),
    case('validate_batch(["a"],[0])', raises='AssertionError', label='字符串不作为特征行'),
    case('validate_batch([[True]],[0])', raises='AssertionError', label='布尔值不作数值特征'),
    case('validate_batch([["1"]],[0])', raises='AssertionError', label='数值字符串不是数值特征'),
    case('validate_batch(None,[])', raises='AssertionError', label='无效顶层容器'),
    case('validate_batch(((1,2.5),(3,4)),(0,1))', True, label='元组与浮点数值合法'),
    case('validate_batch([[],[]],[0,1])', True, label='零宽二维批次合法'),
])

# The original tests never asked for a proper non-empty prefix of the ranking.
python_lessons['py16']['tests'].append(
    case('top_runs([{"name":"b","score":2},{"name":"a","score":2},{"name":"c","score":3}],2)',
         ['c', 'a'], label='确实只取前 k 项')
)

# Additional explicit boundaries from the exercise contracts.
python_lessons['py07']['tests'].append(
    case('moving_average([1,2],-1)', raises='ValueError', label='负窗口也必须拒绝')
)
python_lessons['py20']['fixtures']['invalid.json'] = '{bad json'
python_lessons['py20']['tests'].append(
    case('read_config("invalid.json")', raises='JSONDecodeError', label='保留 JSON 格式错误')
)
