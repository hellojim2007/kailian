"""Local learning app. Uses the existing Python and real CPU PyTorch."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
from catalog import load_catalog

ROOT = Path(__file__).resolve().parent
DIST = ROOT / 'dist'
PORT = 8766


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def log_message(self, fmt, *args):
        pass

    def send_json(self, data, status=200):
        raw = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if urlsplit(self.path).path == '/api/health':
            catalogue=load_catalog(DIST)
            self.send_json({'ok': True, 'runtime': 'native', 'torch': True, 'python': sys.version.split()[0],
                            'exerciseCount':len(catalogue),
                            'contentRevision':json.loads((DIST/'course.json').read_text(encoding='utf-8')).get('contentRevision')})
        else:
            super().do_GET()

    def do_POST(self):
        if self.path != '/api/run':
            self.send_json({'error': 'Not found'}, 404)
            return
        origin = self.headers.get('Origin')
        if origin and origin not in (f'http://127.0.0.1:{PORT}', f'http://localhost:{PORT}'):
            self.send_json({'error': 'Origin rejected'}, 403)
            return
        try:
            size = int(self.headers.get('Content-Length', 0))
            if not 0 < size <= 24000:
                raise ValueError('请求过长或为空。')
            request = json.loads(self.rfile.read(size))
            if request.get('lesson') not in {lesson['id'] for lesson in load_catalog(DIST)}:
                raise ValueError('找不到这一关。')
            if not isinstance(request.get('code'), str) or len(request['code']) > 16000:
                raise ValueError('代码长度超出限制。')
            if request.get('action') not in ('run', 'submit'):
                raise ValueError('未知操作。')
            # PyTorch's optimizer/cache initialization calls getpass.getuser().
            # Windows has no pwd module, so preserve its normal username field.
            allowed_env = {key: value for key, value in os.environ.items() if key.upper() in {'SYSTEMROOT', 'WINDIR', 'PATH', 'TEMP', 'TMP', 'USERPROFILE', 'USERNAME', 'LOCALAPPDATA', 'APPDATA'}}
            allowed_env.update({'PYTHONIOENCODING': 'utf-8', 'OMP_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1'})
            with tempfile.TemporaryDirectory(prefix='python-gym-') as scratch:
                proc = subprocess.run([sys.executable, '-X', 'utf8', '-I', str(ROOT / 'runner.py')], input=json.dumps(request), text=True, encoding='utf-8', capture_output=True, timeout=25, cwd=scratch, env=allowed_env)
            if proc.returncode:
                self.send_json({'ok': False, 'error': {'type': 'RuntimeError', 'message': proc.stderr[-1200:] or '执行进程退出，请重试。', 'guide': '检查代码是否导致进程退出。'}, 'tests': [], 'stdout': ''})
                return
            self.send_json(json.loads(proc.stdout))
        except subprocess.TimeoutExpired:
            self.send_json({'ok': False, 'error': {'type': 'TimeoutError', 'message': '本次运行超过 25 秒，已停止。', 'guide': '检查是否存在无限循环，或先减少循环次数。'}, 'tests': [], 'stdout': ''})
        except Exception as error:
            self.send_json({'error': {'type': type(error).__name__, 'message': str(error)}, 'ok': False}, 400)


if __name__ == '__main__':
    print(f'Python Gym ready: http://127.0.0.1:{PORT}', flush=True)
    ThreadingHTTPServer(('127.0.0.1', PORT), Handler).serve_forever()
