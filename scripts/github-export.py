"""Produce a reviewed source tree for the connected GitHub API (no credentials)."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--chunk', type=int)
args = parser.parse_args()
names = subprocess.check_output(
    ['git', '-c', 'core.quotepath=false', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
    cwd=ROOT).decode('utf-8').split('\0')
selected = sorted({name for name in names if name and not name.startswith(('.openai/', '.runtime/', 'dist/server/', 'dist/.openai/'))})
if args.chunk is None:
    print(json.dumps({'count':len(selected),'chunks':(len(selected)+9)//10,'files':selected},ensure_ascii=False))
else:
    rows=[]
    for name in selected[args.chunk*10:(args.chunk+1)*10]:
        path=ROOT/name
        if path.is_symlink() or not path.is_file():
            raise RuntimeError('Only regular source files may be mirrored')
        content=path.read_text(encoding='utf-8')
        rows.append({'path':name,'mode':'100644','type':'blob','content':content})
    print(json.dumps(rows,ensure_ascii=False))
