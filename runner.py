from pathlib import Path
import json
import sys

root = Path(__file__).resolve().parent / 'dist'
sys.path.insert(0, str(root))
sys.path.insert(0, str(root.parent))
from grade import grade
from catalog import load_catalog

lessons = load_catalog(root)
request = json.loads(sys.stdin.read())
print(json.dumps(grade(request, lessons), ensure_ascii=True))
