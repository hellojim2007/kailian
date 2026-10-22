"""Checks the actual lesson solutions, feedback, and grading boundary cases."""
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'dist'))
from grade import grade

lessons = json.loads((root / 'dist' / 'lessons.json').read_text(encoding='utf-8'))
for lesson in lessons:
    result = grade({'lesson': lesson['id'], 'code': lesson['solution'], 'action': 'submit'}, lessons)
    assert result['ok'], (lesson['id'], result)
    print(f"PASS {lesson['id']}: {len(result['tests'])} cases")

wrong = grade({'lesson': 'p4', 'code': 'def mean(values):\n    print(sum(values) / len(values))', 'action': 'submit'}, lessons)
assert not wrong['ok'] and all(not item['passed'] for item in wrong['tests'])
syntax = grade({'lesson': 'p3', 'code': 'for x in [1,2]\n    print(x)', 'action': 'submit'}, lessons)
assert syntax['error']['type'] == 'SyntaxError' and syntax['error']['line'] == 1
undefined = grade({'lesson': 'p4', 'code': 'def meann(values):\n    return 1', 'action': 'submit'}, lessons)
assert not undefined['ok'] and undefined['tests'][0]['error']['type'] == 'NameError'
partial = grade({'lesson': 'p6', 'code': 'def accuracy(preds, labels):\n    return 0', 'action': 'submit'}, lessons)
assert not partial['ok'] and any(item['passed'] for item in partial['tests'])
run = grade({'lesson': 'p1', 'code': 'print(123)', 'action': 'run'}, lessons)
assert run['ok'] and run['stdout'].strip() == '123' and not run['tests']
print('PASS wrong-return / syntax-location / missing-function / partial-credit / run-only')
