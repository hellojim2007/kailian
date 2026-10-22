let ready;
async function init() {
  self.postMessage({ type: 'status', message: '首次加载 Python 运行时…' });
  const { loadPyodide } = await import('https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs');
  const py = await loadPyodide();
  const [grader, lessons, exams] = await Promise.all([fetch('grade.py').then(r => r.text()), fetch('lessons.json').then(r => r.text()),fetch('exams.json').then(r=>{if(!r.ok)throw new Error('考核题库加载失败，请刷新页面');return r.json();})]);
  py.runPython(grader);
  py.globals.set('_lessons_json', JSON.stringify([...JSON.parse(lessons),...(exams.exercises||[])]));
  py.runPython('_lessons = json.loads(_lessons_json)');
  self.postMessage({ type: 'ready' });
  return py;
}
self.onmessage = async ({data}) => {
  try {
    ready ??= init();
    const py = await ready;
    if (data.type === 'init') return;
    py.globals.set('_request_json', JSON.stringify(data));
    const result = py.runPython('json.dumps(grade(json.loads(_request_json), _lessons), ensure_ascii=False)');
    self.postMessage({ type: 'result', id: data.id, result: JSON.parse(result) });
  } catch (error) {
    ready = undefined;
    self.postMessage({type: 'fatal', id: data.id, message: error.message});
  }
};
