"""Shared grader for native Python and browser Python (Pyodide)."""
import contextlib
import io
import json
import math
import traceback
import ast
import os
from pathlib import Path
import tempfile


def plain(value):
    if hasattr(value, 'detach'):
        value = value.detach().cpu().tolist()
    if isinstance(value, (tuple, list)):
        return [plain(item) for item in value]
    if isinstance(value, dict):
        return {key: plain(item) for key, item in value.items()}
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    return value


def same(actual, expected, tolerance=1e-5):
    if isinstance(expected, bool):
        return isinstance(actual, bool) and actual == expected
    if isinstance(expected, (int, float)):
        return isinstance(actual, (int, float)) and not isinstance(actual, bool) and math.isclose(actual, expected, rel_tol=tolerance, abs_tol=tolerance)
    if isinstance(expected, dict):
        return isinstance(actual, dict) and actual.keys() == expected.keys() and all(same(actual[k], v, tolerance) for k, v in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(same(a, b, tolerance) for a, b in zip(actual, expected))
    return actual == expected


def error_info(error):
    line = getattr(error, 'lineno', None)
    for frame in traceback.extract_tb(error.__traceback__):
        if frame.filename == '<你的代码>':
            line = frame.lineno
    guides = {
        'SyntaxError': '检查冒号、括号和引号是否配对。',
        'IndentationError': '代码块统一缩进 4 个空格，避免混用 Tab。',
        'NameError': '检查变量或函数名有没有拼错，以及是否先定义再使用。',
        'TypeError': '检查传入的值、返回值与函数参数是否符合题意。',
        'IndexError': '列表从 0 开始索引；最大正索引比长度小 1。',
        'KeyError': '检查字典中是否存在这个键，以及键的拼写。',
        'RuntimeError': '检查张量的 shape、dtype，以及是否需要梯度。',
    }
    name = type(error).__name__
    return {'type': name, 'line': line, 'message': str(error)[:1400], 'guide': guides.get(name, '先看报错位置，再检查这一行使用的变量和输入。')}


def execute(code, stdin_text=''):
    output = io.StringIO()
    stream = io.StringIO(stdin_text)
    def read_input(prompt=''):
        if prompt:
            print(prompt, end='')
        line = stream.readline()
        if line == '':
            raise EOFError('标准输入已读完；可在编辑器下方填写测试输入。')
        return line.rstrip('\r\n')
    namespace = {'__name__': '__main__', 'input': read_input}
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
        exec(compile(code, '<你的代码>', 'exec'), namespace)
    return namespace, output.getvalue()[:12000]


def _grade(request, lesson):
    code = request.get('code', '')
    result = {'ok': False, 'stdout': '', 'tests': []}
    try:
        tree = ast.parse(code)
        forbidden = lesson.get('forbiddenCalls', []) if request.get('action') == 'submit' else []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else (node.func.id if isinstance(node.func, ast.Name) else '')
                if name in forbidden:
                    raise ValueError(f'这一题练习手写实现，不能直接调用 {name}。请查看左侧的推导与提示。')
        if request.get('action') == 'run':
            sample_input = request.get('stdin', lesson['tests'][0].get('stdin', ''))
            namespace, result['stdout'] = execute(code, sample_input)
            result['ok'] = True
            return result
        program = all(test.get('stdout') for test in lesson['tests'])
        if not program:
            namespace, result['stdout'] = execute(code)
        for test in lesson['tests']:
            record = {'label': test['label'], 'expected': ('抛出 '+test['raises']) if test.get('raises') else test.get('expected'), 'input': test.get('stdin', test.get('expr', '程序标准输出'))}
            try:
                if program:
                    _, stdout = execute(code, test.get('stdin', ''))
                    result['stdout'] = stdout
                    actual = stdout.strip()
                else:
                    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                        if test.get('setup'):
                            exec(test['setup'], namespace)
                        actual = plain(eval(test['expr'], namespace))
                record.update(actual=actual, passed=not test.get('raises') and same(actual, test.get('expected'), test.get('tolerance', 1e-5)))
                if test.get('raises'):
                    record['feedback'] = '应当拒绝这个输入，但函数正常返回了。'
            except Exception as error:
                expected_exception = test.get('raises')
                if expected_exception and any(cls.__name__ == expected_exception for cls in type(error).__mro__):
                    record.update(passed=True, actual='抛出 '+type(error).__name__)
                else:
                    record.update(passed=False, error=error_info(error))
            result['tests'].append(record)
        result['ok'] = bool(result['tests']) and all(test['passed'] for test in result['tests'])
    except Exception as error:
        result['error'] = error_info(error)
    return result


def grade(request, lessons):
    lesson = next(item for item in lessons if item['id'] == request['lesson'])
    previous = Path.cwd()
    with tempfile.TemporaryDirectory(prefix='kaillian-exercise-') as directory:
        try:
            os.chdir(directory)
            for name, content in lesson.get('fixtures', {}).items():
                target = Path(name)
                if target.is_absolute() or '..' in target.parts:
                    raise ValueError('非法练习附件路径')
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding='utf-8')
            return _grade(request, lesson)
        finally:
            os.chdir(previous)
