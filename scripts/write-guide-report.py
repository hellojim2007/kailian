"""Refresh the route table without rechecking external links or changing notes."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
lessons=json.loads((root/'dist/lessons.json').read_text(encoding='utf-8'))
course=json.loads((root/'dist/course.json').read_text(encoding='utf-8'))
by_id={l['id']:l for l in lessons}
report=root/'CURRICULUM_REDESIGN.md'
body=report.read_text(encoding='utf-8').split('\n<!-- GUIDE TABLE -->')[0]
rows=['\n<!-- GUIDE TABLE -->','|路线步|稳定题号|课节|阶段|先修ID|本节用法卡|','|---:|---|---|---|---|---|']
for n,ident in enumerate(course['studyRoute']['lessonIds'],1):
    l=by_id[ident];g=l['guide']
    rows.append(f"|{n}|{ident}|{l['title']}|{'入门' if g['track']=='core' else '回访'}|{', '.join(g['requires']) or '无'}|{'、'.join(c['title'] for c in g['cards'])}|")
report.write_text(body+'\n'.join(rows)+'\n',encoding='utf-8')
print('Updated 72-row teaching route table')
