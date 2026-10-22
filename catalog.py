"""Shared catalogue for the local runner and HTTP request validation."""
import json
from pathlib import Path


def load_catalog(directory):
    root=Path(directory)
    lessons=json.loads((root/'lessons.json').read_text(encoding='utf-8'))
    exams=root/'exams.json'
    if exams.exists():
        lessons.extend(json.loads(exams.read_text(encoding='utf-8')).get('exercises',[]))
    ids=[lesson['id'] for lesson in lessons]
    if len(ids)!=len(set(ids)):
        raise ValueError('Duplicate exercise ID in course catalogue')
    return lessons
