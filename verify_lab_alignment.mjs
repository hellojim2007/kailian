import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {lessonLabs,renderLessonLab,bindLessonLab} from './dist/labs.js';
import {PYTHON_LAB_META,renderPythonLab,bindPythonLab} from './dist/labs-python.js';
import {torchLabMetadata,renderTorchLabById,bindTorchLabById} from './dist/labs-torch.js';

const [lessons,course,manifest]=await Promise.all(['dist/lessons.json','dist/course.json','curriculum/lab-alignment.json'].map(async path=>JSON.parse(await readFile(path,'utf8'))));
const expectedIds=['p1','p2','p3','p4','p5','p6','t1','t2','t3','t4','t5','t6'];
const metadata={...PYTHON_LAB_META,...Object.fromEntries(torchLabMetadata.map(value=>[value.id,value]))};
assert.equal(lessons.length,72);assert.equal(new Set(lessons.map(l=>l.id)).size,72);assert.equal(course.chapters.length,12);
assert.equal(manifest.lessons.length,72);assert.deepEqual(manifest.lessons.map(x=>x.lessonId),lessons.map(x=>x.id));
assert.equal(new Set(manifest.lessons.map(x=>x.objective)).size,72,'objectives are lesson-specific audit entries, not one generic sentence');
assert.deepEqual(Object.keys(lessonLabs).sort(),[...expectedIds].sort(),'only twelve explicitly registered labs');
assert.deepEqual(Object.keys(metadata).sort(),[...expectedIds].sort());
assert.equal(Object.keys(PYTHON_LAB_META).length,6);assert.equal(torchLabMetadata.length,6);
assert.equal(new Set(Object.values(metadata).map(x=>x.widgetId)).size,12,'every registered interaction has a distinct widget identity');

const chapterPositions=new Map(course.chapters.map((chapter,index)=>[chapter.title,index]));
const domIds=new Set();let rendered=0,omitted=0;
for(let index=0;index<lessons.length;index++){
  const lesson=lessons[index],entry=manifest.lessons[index],chapter=course.chapters.find(c=>c.id===lesson.chapter);
  assert.equal(entry.ordinal,index+1);assert.equal(entry.title,lesson.title);assert.equal(entry.chapter,lesson.chapter);assert.ok(entry.objective.length>=10);
  assert.ok(chapter,lesson.id+' belongs to a known chapter');assert.equal(lesson.group,chapter.title);assert.ok(chapter.lessons.includes(lesson.id));
  for(const hint of lesson.prerequisites||[])if(chapterPositions.has(hint))assert.ok(chapterPositions.get(hint)<chapterPositions.get(chapter.title),lesson.id+' named chapter path points backwards');
  const html=renderLessonLab(lesson.id);
  if(entry.widgetId===null){
    omitted++;assert.equal(html,'',lesson.id+' must not inherit a generic widget from visual='+lesson.visual);assert.equal(entry.domId,null);
    assert.equal(renderPythonLab(lesson.id),'');assert.equal(renderTorchLabById(lesson.id),'');
  }else{
    rendered++;assert.ok(metadata[lesson.id]);assert.equal(metadata[lesson.id].widgetId,entry.widgetId);
    assert.equal(typeof lessonLabs[lesson.id].render,'function');assert.equal(typeof lessonLabs[lesson.id].bind,'function');
    assert.ok(html.startsWith('<section '),lesson.id+' must render its own section');assert.match(html,/class="lesson-lab"/);
    assert.doesNotMatch(html,/\bdata-lesson\s*=/,lesson.id+' lab markup must not masquerade as a navigation target');
    const sectionId=html.match(/^<section\b[^>]*\bid="([^"]+)"/)?.[1];assert.equal(sectionId,entry.domId);assert.ok(!domIds.has(sectionId));domIds.add(sectionId);
    assert.ok(html.includes(`data-lab="${lesson.id}"`));
    const ids=[...html.matchAll(/(?:^|\s)id="([^"]+)"/g)].map(match=>match[1]);assert.equal(new Set(ids).size,ids.length,lesson.id+' has no duplicate DOM ids');
    for(const match of html.matchAll(/\b(?:for|aria-controls)="([^"]+)"/g))for(const target of match[1].split(/\s+/))assert.ok(ids.includes(target),lesson.id+' internal control anchor '+target+' resolves in its own lab');
    for(const match of html.matchAll(/url\(#([^)]+)\)/g))assert.ok(ids.includes(match[1]),lesson.id+' SVG local reference resolves');
  }
  assert.doesNotThrow(()=>bindLessonLab(lesson.id,null),lesson.id+' absent lab host on quiz/mission tabs is harmless');
  assert.equal(lesson.prerequisiteAuditScope,entry.prerequisiteAuditScope,lesson.id+' exposes the honest path-audit scope');
  assert.equal(lesson.resourceAuditScope,entry.resourceAuditScope,lesson.id+' exposes the honest reference-audit scope');
  assert.deepEqual(lesson.prerequisites,entry.learningPathHints,lesson.id+' follows its reviewed path hint declaration');
  assert.deepEqual(lesson.resources.map(r=>({url:r.url,scope:r.scope})),entry.resources,lesson.id+' resource categories and targets match its reviewed declaration');
  for(const resource of lesson.resources){
    const url=new URL(resource.url);assert.equal(url.protocol,'https:');assert.ok(['docs.python.org','docs.pytorch.org','cs50.harvard.edu','programming-26.mooc.fi','learn.arena.education'].includes(url.hostname),lesson.id+' official or original course source');
    assert.equal(url.username,'');assert.equal(url.password,'');
    if(resource.scope==='course-index')assert.match(resource.title,/课程目录/,'course homepages are not labelled as a specific matching section');
  }
  if(entry.widgetId||['py05','pt08'].includes(lesson.id))assert.ok(lesson.resources.some(r=>r.scope==='official-section'&&new URL(r.url).hash),lesson.id+' links its audited official section');
}
assert.equal(rendered,12);assert.equal(omitted,60);
assert.deepEqual(course.chapters.flatMap(c=>c.lessons),lessons.map(l=>l.id));for(const chapter of course.chapters)assert.equal(chapter.lessons.length,6);
assert.equal(lessons[13].id,'p6','the reported lesson 14 remains zip/accuracy');assert.match(lessons[13].task,/accuracy/);assert.match(manifest.lessons[13].objective,/zip/);
const p5=lessons.find(l=>l.id==='p5');assert.match(p5.task,/字典/);assert.match(p5.task,/严格/);assert.equal(metadata.p5.widgetId,'lab-p5');
assert.match(lessons.find(l=>l.id==='py05').prerequisites.join(' '),/def.*return/);
assert.match(lessons.find(l=>l.id==='pt08').prerequisites.join(' '),/计算图/);

for(const id of ['unknown','p0','p7','t7','py99','pt99','values','list','tensor','gradient','constructor','toString','__proto__',null,undefined]){
  assert.equal(renderLessonLab(id),'','central renderer has no unregistered fallback: '+id);
  assert.equal(renderPythonLab(id),'');assert.equal(renderTorchLabById(id),'');
  assert.equal(bindPythonLab(id,null),false);assert.equal(bindTorchLabById(id,null),false);
  assert.doesNotThrow(()=>bindLessonLab(id,null));
}

for(const path of ['dist/app.js','curriculum/ui-v2.js']){
  const source=await readFile(path,'utf8');
  for(const forbidden of [/function\s+widget\s*\(/,/widget\s*\(\s*l\.visual\s*\)/,/function\s+tensorCells\s*\(/,/function\s+renderContentBase\s*\(/,/score-slider|gradient-slider|tensor-caption|list-note/])assert.doesNotMatch(source,forbidden,path+' no legacy generic widget/render/bind path');
  const fn=source.match(/function\s+conceptWidget\s*\(l\)\s*\{[^}]*\}/)?.[0];assert.ok(fn,path+' explicit concept renderer');assert.doesNotMatch(fn,/visual|fallback/);assert.match(fn,/renderLessonLab\(l\.id\)/);
  const concept=Function('renderLessonLab',fn+';return conceptWidget;')(renderLessonLab);
  for(const lesson of lessons)assert.equal(concept(lesson),renderLessonLab(lesson.id),path+' runtime concept mapping '+lesson.id);
  assert.match(source,/bindLessonLab\(lesson\(\)\.id,\s*\$\('#lesson-content'\)\)/,path+' binds the same current lesson');
}
const index=await readFile('dist/index.html','utf8');assert.match(index,/labs-python\.css/);assert.match(index,/labs-torch\.css/);
const appSource=await readFile('dist/app.js','utf8');
assert.match(appSource,/querySelectorAll\(['"]button\.lesson-nav\[data-lesson\]['"]\)/,'navigation events are limited to actual sidebar lesson buttons');
assert.doesNotMatch(appSource,/querySelectorAll\(['"]\[data-lesson\]['"]\)/,'no global data-lesson listener can intercept lab child clicks');
console.log('PASS 72 ordered lesson/objective mappings; 12 unique lesson labs, 60 intentional omissions; unknown/prototype IDs empty; no old visual fallback in app or rebuild fragment; chapter/path/reference metadata aligned.');
console.log('Scope: this verifies declarations and render wiring, not every pedagogy claim, live browser behavior, or a complete skill dependency graph.');
