import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {renderLearningGuide,bindLearningGuide,routeOverview,routeNext,cleanWarmups,checkWarmupResult,warmupMismatchHint} from './dist/learning.js';
const lessons=JSON.parse(await readFile('dist/lessons.json','utf8')),course=JSON.parse(await readFile('dist/course.json','utf8'));
const ids=lessons.map(l=>l.id),route=course.studyRoute.lessonIds;
assert.equal(route.length,72);assert.equal(new Set(route).size,72);
assert.equal(course.studyRoute.phases.filter(p=>p.track==='core').flatMap(p=>p.lessonIds).length,53);
for(let n=0;n<route.length;n++)assert.equal(routeNext(route[n],course.studyRoute,lessons)?.id,route[n+1]);
assert.equal(routeNext('p2',course.studyRoute,lessons).id,'p4');assert.equal(routeNext('t5',course.studyRoute,lessons).id,'t6');
for(const lesson of lessons){
 const html=renderLearningGuide(lesson,{lessons});
 assert.ok(html.includes('warmup-editor'));assert.ok(html.includes('最终要独立实现'));
 assert.equal((html.match(/class="syntax-card"/g)||[]).length,lesson.guide.cards.length);
 assert.ok(html.includes('热身通过不自动计入正式通关'));assert.doesNotMatch(html,/<script/);
 for(const pre of lesson.guide.requires)assert.ok(route.indexOf(pre)<route.indexOf(lesson.id));
}
const malicious=structuredClone(lessons[0]);malicious.guide.reason='<img src=x onerror=alert(1)>';
assert.ok(renderLearningGuide(malicious,{lessons}).includes('&lt;img'));assert.doesNotMatch(renderLearningGuide(malicious,{lessons}),/<img/);
const clean=cleanWarmups(JSON.parse('{"py06":{"draft":"safe","passed":true,"viewed":true},"__proto__":{"draft":"bad"},"unknown":{"draft":"bad"}}'),ids);
assert.deepEqual(clean,{py06:{draft:'safe',passed:true,viewed:true}});
assert.deepEqual(cleanWarmups(clean,ids),clean);assert.equal(cleanWarmups({p1:{draft:'a'.repeat(14000),passed:1}},ids).p1.draft.length,12000);
assert.ok(checkWarmupResult({ok:true,stdout:'1\r\n2\n'},'1\n2'));
assert.ok(!checkWarmupResult({ok:false,stdout:'1'},'1'));assert.ok(!checkWarmupResult({ok:true,error:{},stdout:'1'},'1'));
assert.ok(!checkWarmupResult({ok:true,stdout:'RED'},'red'));
const tokenLesson=lessons.find(l=>l.id==='py06');assert.match(warmupMismatchHint(tokenLesson,{stdout:"['GREEN', 'Tea!']"}),/split不会转小写/);assert.match(warmupMismatchHint(tokenLesson,{stdout:''}),/函数外调用/);
const overview=routeOverview(course,lessons,{p1:true});assert.match(overview,/data-guide-lesson="py01"/);assert.match(overview,/19 节进阶/);

// Exercise actual event callbacks with a tiny DOM surface; transport is injected.
function fixture(runCode){
 let row={draft:'print(1)',passed:false,viewed:false};
 const nodes={'#warmup-editor':{value:row.draft},'[data-warmup-run]':{disabled:false},'[data-warmup-solution]':{},'#warmup-solution':{hidden:true},'#warmup-feedback':{textContent:'',classList:{toggle(){}}}};
 const root={querySelector:key=>nodes[key]??null,querySelectorAll:()=>[]};
 const lesson=structuredClone(lessons[0]);lesson.guide.warmup.expected='1';
 bindLearningGuide(root,{lesson,getWarmup:()=>row,saveWarmup:value=>row=value,runCode,navigate(){}});
 return {nodes,get row(){return row;}};
}
let test=fixture(async()=>({ok:true,stdout:'1\n'}));await test.nodes['[data-warmup-run]'].onclick();assert.equal(test.row.passed,true);
test.nodes['#warmup-editor'].value='print(2)';test.nodes['#warmup-editor'].oninput();assert.equal(test.row.passed,false);
test.nodes['[data-warmup-solution]'].onclick();assert.equal(test.row.viewed,true);assert.equal(test.nodes['#warmup-solution'].hidden,false);
test=fixture(async()=>{throw new Error('offline');});await test.nodes['[data-warmup-run]'].onclick();assert.equal(test.nodes['[data-warmup-run]'].disabled,false);assert.equal(test.nodes['#warmup-feedback'].textContent,'offline');
let resolve;test=fixture(()=>new Promise(r=>resolve=r));const running=test.nodes['[data-warmup-run]'].onclick();test.nodes['#warmup-editor'].value='new draft';test.nodes['#warmup-editor'].oninput();resolve({ok:true,stdout:'1'});await running;assert.equal(test.row.draft,'new draft');assert.equal(test.row.passed,false);
const app=await readFile('dist/app.js','utf8');assert.match(app,/if\(state!==owner\)return/,'old account event completions cannot write into a new account');assert.match(app,/warmups:cleanWarmups/);assert.match(app,/routeNext\(l.id,course.studyRoute,lessons\)/);
console.log('PASS 72 guides and dependency route; escaped teaching HTML; isolated, bounded warmup drafts; reference flags, execution failure and edit-during-run preservation.');
