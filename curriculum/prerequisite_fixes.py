"""Apply after finish.py's default per-lesson prerequisites, before JSON output.

This is a learning-path repair and a bounded reference audit, not a claim that a
complete skill dependency graph has been validated. Inline primer text is owned
by the separate Python/Torch teaching audits.
"""

PREREQUISITE_OVERRIDES = {
    'py05': [
        '已学起步与控制流、p2 列表索引',
        '先读本节函数接口先导：def、形参、缩进与 return；p4 稍后系统练习函数',
    ],
    'pt08': [
        '已学张量形状与索引、pt07 数值稳定的 logsumexp',
        '先读本节最小计算图先导：与输入相连的零和独立常量；t3 稍后系统练习自动微分',
    ],
}

SECTION_RESOURCE_OVERRIDES = {
    'p1': [
        ('Python 官方：数值、变量与赋值', 'https://docs.python.org/3/tutorial/introduction.html#numbers'),
    ],
    'p2': [
        ('Python 官方：列表、索引与切片', 'https://docs.python.org/3/tutorial/introduction.html#lists'),
    ],
    'p3': [
        ('Python 官方：for 语句', 'https://docs.python.org/3/tutorial/controlflow.html#for-statements'),
    ],
    'p4': [
        ('Python 官方：定义函数与返回值', 'https://docs.python.org/3/tutorial/controlflow.html#defining-functions'),
    ],
    'p5': [
        ('Python 官方：字典', 'https://docs.python.org/3/tutorial/datastructures.html#dictionaries'),
    ],
    'p6': [
        ('Python 官方：zip 按位置配对', 'https://docs.python.org/3/library/functions.html#zip'),
    ],
    't1': [
        ('PyTorch 2.10 官方：torch.mean 的 dim 与输出形状', 'https://docs.pytorch.org/docs/2.10/generated/torch.mean.html#torch.mean'),
    ],
    't2': [
        ('PyTorch 2.10 官方：广播的一般规则', 'https://docs.pytorch.org/docs/2.10/notes/broadcasting.html#general-semantics'),
        ('PyTorch 2.10 官方：torch.mean 与 keepdim', 'https://docs.pytorch.org/docs/2.10/generated/torch.mean.html#torch.mean'),
    ],
    't3': [
        ('PyTorch 官方教程：计算梯度', 'https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html#computing-gradients'),
    ],
    't4': [
        ('PyTorch 官方教程：nn.Linear', 'https://docs.pytorch.org/tutorials/beginner/basics/buildmodel_tutorial.html#nn-linear'),
    ],
    't5': [
        ('PyTorch 官方教程：优化器与更新步骤', 'https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html#optimizer'),
    ],
    't6': [
        ('PyTorch 官方教程：训练与评估循环', 'https://docs.pytorch.org/tutorials/beginner/basics/optimization_tutorial.html#full-implementation'),
    ],
    'py05': [
        ('Python 官方：定义函数与返回值（本节先导）', 'https://docs.python.org/3/tutorial/controlflow.html#defining-functions'),
        ('Python 官方：列表切片与浅复制', 'https://docs.python.org/3/tutorial/introduction.html#lists'),
    ],
    'pt08': [
        ('PyTorch 官方教程：张量、函数与计算图（本节先导）', 'https://docs.pytorch.org/tutorials/beginner/basics/autogradqs_tutorial.html#tensors-functions-and-computational-graph'),
    ],
}

COURSE_INDEX_URLS = {
    'https://cs50.harvard.edu/python/',
    'https://programming-26.mooc.fi/',
    'https://learn.arena.education/chapter0_fundamentals/',
}

def apply_learning_path_references(lessons):
    for item in lessons:
        lesson_id = item['id']
        if lesson_id in PREREQUISITE_OVERRIDES:
            item['prerequisites'] = list(PREREQUISITE_OVERRIDES[lesson_id])
        item['prerequisiteAuditScope'] = (
            'inline-primer-path-repair' if lesson_id in PREREQUISITE_OVERRIDES
            else 'chapter-path-hint-not-complete-skill-graph'
        )
        original = [dict(resource) for resource in item['resources']]
        for resource in original:
            if resource['url'] in COURSE_INDEX_URLS:
                resource['scope'] = 'course-index'
                if '课程目录' not in resource['title']:
                    resource['title'] += ' · 课程目录（延伸）'
            else:
                resource['scope'] = 'chapter-reference'
        if lesson_id in SECTION_RESOURCE_OVERRIDES:
            item['resources'] = [
                {'title': title, 'url': url, 'scope': 'official-section'}
                for title, url in SECTION_RESOURCE_OVERRIDES[lesson_id]
            ] + [resource for resource in original if resource['scope'] == 'course-index']
            item['resourceAuditScope'] = 'specific-official-sections-plus-labelled-course-index'
        else:
            item['resources'] = original
            item['resourceAuditScope'] = 'chapter-reference-category-only-not-every-claim'

apply_learning_path_references(LESSONS)
