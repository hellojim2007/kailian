import assert from 'node:assert/strict';
import fs from 'node:fs';
import {
  cleanAssessmentProgress,scoreAssessment,selectReviewItems,getReviewSchedule,
  getAssessmentEvidence,createAssessmentCenter,
} from './dist/assessments.js';

const DAY=86400000,T0=Date.parse('2026-01-01T00:00:00.000Z');
const iso=offset=>new Date(T0+offset).toISOString();
const tests=[];
const test=(title,fn)=>tests.push({title,fn});
const freeze=value=>{if(value&&typeof value==='object'){Object.freeze(value);Object.values(value).forEach(freeze);}return value;};
const row=(id='first',overrides={})=>({id,examId:'c01-exam',mode:'independent',startedAt:iso(0),updatedAt:iso(DAY),submittedAt:iso(DAY),durationMs:600000,elapsedMs:600000,assistance:'independent',answers:{q:{choice:1,confidence:'sure'}},itemIds:['q'],results:{q:{points:2,maxPoints:2,passed:true}},skills:{p1:{points:2,maxPoints:2}},...overrides});

test('exports import without browser globals',()=>{
  assert.equal(typeof createAssessmentCenter,'function');
  for(const fn of [cleanAssessmentProgress,scoreAssessment,selectReviewItems,getReviewSchedule,getAssessmentEvidence])assert.equal(typeof fn,'function');
});
test('sanitize missing/malformed input and bound enums, text, dates, counts',()=>{
  assert.deepEqual(cleanAssessmentProgress(null),{version:1,drafts:{},attempts:[]});
  const raw={version:1,drafts:{draft:row('draft',{mode:'invented',assistance:'invented',elapsedMs:-50,startedAt:iso(0),updatedAt:'bad',answers:{q:{choice:99,confidence:'invented',code:'x'.repeat(17000),output:'z'.repeat(25000),stdin:'0'.repeat(5000)}}}),badDate:row('badDate',{startedAt:'2026-02-30T00:00:00Z'})},attempts:[row('bad-submit',{submittedAt:'2025-12-30T00:00:00Z'}),row('bad-id',{examId:'<script>'})]};
  const clean=cleanAssessmentProgress(raw),a=clean.drafts.draft.answers.q;
  assert.equal(clean.drafts.draft.mode,'independent');assert.equal(clean.drafts.draft.assistance,'independent');assert.equal(clean.drafts.draft.elapsedMs,0);assert.equal(clean.drafts.draft.updatedAt,iso(0));
  assert.equal(a.code.length,16000);assert.equal(a.output.length,24000);assert.equal(a.stdin.length,4000);assert.equal(a.confidence,'unsure');assert.equal(a.choice,undefined);
  assert.equal(clean.drafts.badDate,undefined);assert.equal(clean.attempts.length,0);
});
test('prototype keys are rejected throughout stored data and scoring',()=>{
  const raw=JSON.parse('{"version":1,"drafts":{"__proto__":{"examId":"x","startedAt":"2026-01-01T00:00:00Z"},"constructor":{},"prototype":{}},"attempts":[]}');
  assert.deepEqual(cleanAssessmentProgress(raw).drafts,{});assert.equal({}.polluted,undefined);
  const record=row();record.skills=JSON.parse('{"__proto__":{"points":2,"maxPoints":2},"constructor":{},"prototype":{},"p1":{"points":2,"maxPoints":2}}');
  assert.deepEqual(Object.keys(cleanAssessmentProgress({attempts:[record]}).attempts[0].skills),['p1']);
  assert.equal(Object.keys(scoreAssessment([{id:'__proto__',kind:'choice',points:2,answer:0,skills:['constructor']}],{}).results).length,0);
});
test('sanitization is idempotent, does not mutate inputs, and recalculates totals',()=>{
  const raw=freeze({version:1,drafts:{draft:row('draft',{submittedAt:undefined,answers:{q:{choice:0,confidence:'guess'}}})},attempts:[row('first',{score:999,maxScore:999,percent:999,results:{q:{points:1,maxPoints:2,passed:true}}})]});
  const clean=cleanAssessmentProgress(raw);
  assert.equal(clean.attempts[0].score,1);assert.equal(clean.attempts[0].percent,50);assert.equal(clean.attempts[0].results.q.passed,false);
  assert.deepEqual(cleanAssessmentProgress(clean),clean);assert.equal(raw.attempts[0].score,999);
});
test('duplicate immutable IDs and already-submitted stale drafts do not duplicate history',()=>{
  const r=row('same');
  const clean=cleanAssessmentProgress({drafts:{same:r},attempts:[r,{...r,results:{q:{points:0,maxPoints:2}}}]});
  assert.equal(clean.attempts.length,1);assert.equal(clean.attempts[0].percent,100);assert.equal(clean.drafts.same,undefined);
});
test('docs first -> independent same-paper retest cannot become first independent evidence',()=>{
  const clean=cleanAssessmentProgress({drafts:{waiting:row('waiting')},attempts:[row('second',{submittedAt:iso(2*DAY)}),row('first',{assistance:'docs'})]});
  assert.deepEqual(clean.attempts.map(r=>[r.id,r.mode,r.assistance]),[['first','independent','docs'],['second','retest','independent']]);
  assert.equal(clean.attempts.filter(r=>r.mode==='independent'&&r.assistance==='independent').length,0);
  assert.equal(clean.drafts.waiting.mode,'retest');assert.deepEqual(cleanAssessmentProgress(clean),clean);
  assert.equal(getAssessmentEvidence(row('pre-opened'),clean.attempts,T0+3*DAY).mode,'retest');
});
test('first independent and correction parent/answers/marks remain distinct',()=>{
  const initial=row('first'),correction=row('fix',{mode:'correction',parentId:'first',submittedAt:iso(2*DAY),answers:{q:{choice:0,confidence:'unsure'}},results:{q:{points:0,maxPoints:2}}});
  const clean=cleanAssessmentProgress({attempts:[initial,correction]});
  assert.equal(clean.attempts[0].mode,'independent');assert.equal(clean.attempts[1].mode,'correction');assert.equal(clean.attempts[1].parentId,'first');
  clean.attempts[1].answers.q.choice=9;assert.equal(clean.attempts[0].answers.q.choice,1);assert.equal(initial.answers.q.choice,1);
  assert.equal(clean.attempts[0].percent,100);
});
const paper=[{id:'choice',kind:'choice',points:2,options:['A','B'],answer:1,skills:['p1']},{id:'output',kind:'output',points:3,expectedStdout:'75\n',skills:['p1']},{id:'code',kind:'code',points:5,skills:['p2']}];
test('partial check ratio, distinct skill aggregation, and CRLF output scoring',()=>{
  const graded=scoreAssessment(paper,{choice:{choice:1},output:{output:'75\r\n'}},{code:{tests:[{passed:true,label:'one'},{passed:false,label:'two',expected:3,actual:4}]}});
  assert.equal(graded.score,7.5);assert.equal(graded.maxScore,10);assert.equal(graded.percent,75);assert.equal(graded.results.code.passed,false);
  assert.deepEqual(graded.skills.p1,{points:5,maxPoints:5});assert.equal(graded.results.code.checks[1].expected,'3');
});
test('blank code and genuine student errors get zero, not all-or-nothing code partial credit',()=>{
  const blank=scoreAssessment(paper,{});assert.equal(blank.results.code.points,0);assert.equal(blank.results.choice.points,0);assert.equal(blank.results.output.points,0);
  const bad=scoreAssessment([paper[2]],{},{code:{tests:[],error:{type:'SyntaxError',message:'bad code'}}});assert.equal(bad.percent,0);assert.equal(bad.results.code.error.type,'SyntaxError');
});
test('review dates are anchored to first formal exam, with exact 1/3/7 due boundaries',()=>{
  const progress={attempts:[row('first',{assistance:'ai'})]};
  const schedule=getReviewSchedule(progress,[1,3,7],T0+2*DAY);
  assert.deepEqual(schedule.map(s=>s.dueAt),[iso(2*DAY),iso(4*DAY),iso(8*DAY)]);assert.deepEqual(schedule.map(s=>s.due),[true,false,false]);
  assert.deepEqual(getReviewSchedule({attempts:[]}),[]);
});
test('review evidence requires 24h independent gap; all-seen/mixed items are not novel transfer',()=>{
  const prior=[row('first')],review=row('review',{examId:'review-pool',mode:'review',itemIds:['r1','r2']});
  assert.equal(getAssessmentEvidence(review,prior,T0+2*DAY-1).retentionEvidence,false);
  assert.equal(getAssessmentEvidence(review,prior,T0+2*DAY).delayEvidence,true);
  assert.equal(getAssessmentEvidence({...review,assistance:'docs'},prior,T0+4*DAY).delayEvidence,false);
  const seen=[...prior,row('earlier-review',{mode:'review',examId:'review-pool',itemIds:['r1'],submittedAt:iso(2*DAY)})];
  const mixed=getAssessmentEvidence(review,seen,T0+3*DAY);assert.equal(mixed.retentionEvidence,true);assert.equal(mixed.delayEvidence,false);assert.deepEqual(mixed.seenBefore,['r1']);
  const correction=row('correction',{mode:'correction',submittedAt:iso(3*DAY-1)});assert.equal(getAssessmentEvidence(review,[...prior,correction],T0+3*DAY).retentionEvidence,false);
});
test('import cannot invent delayed mastery with flags or hide previously seen items',()=>{
  const reviewed=row('review',{mode:'review',examId:'review-pool',itemIds:['q'],submittedAt:iso(3*DAY),seenBefore:[],retentionEvidence:true,delayEvidence:true});
  const clean=cleanAssessmentProgress({attempts:[row(),reviewed]});
  assert.deepEqual(clean.attempts[1].seenBefore,['q']);assert.equal(clean.attempts[1].delayEvidence,false);assert.equal(clean.attempts[1].retentionEvidence,true);
  const early=cleanAssessmentProgress({attempts:[row(),{...reviewed,submittedAt:iso(DAY+1000),itemIds:['r1']}]});assert.equal(early.attempts[1].retentionEvidence,false);assert.equal(early.attempts[1].delayEvidence,false);
  assert.deepEqual(cleanAssessmentProgress(clean),clean);
});
test('review schedule marks due completed step, while ordinary early review does not consume it',()=>{
  const first=row(),review=row('review',{mode:'review',examId:'review-pool',submittedAt:iso(2*DAY),itemIds:['r1'],reviewStep:1});
  const p=cleanAssessmentProgress({attempts:[first,review]});assert.equal(getReviewSchedule(p,[1,3,7],T0+2*DAY)[0].done,true);
  const early=cleanAssessmentProgress({attempts:[first,{...review,reviewStep:undefined,submittedAt:iso(DAY+1000)}]});assert.equal(getReviewSchedule(early,[1,3,7],T0+2*DAY)[0].done,false);
  const prematureStep=cleanAssessmentProgress({attempts:[first,{...review,reviewStep:7}]});assert.equal(getReviewSchedule(prematureStep,[1,3,7],T0+8*DAY)[2].done,false);
});
test('review selection is separate, learned/chapter filtered, max 4, weak confident errors first',()=>{
  const data={reviewItems:['r1','r2','r3','r4','r5'],items:[{id:'q',chapter:'c01',skills:['p1']},{id:'weak',chapter:'c02',skills:['p2']},...Array.from({length:5},(_,n)=>({id:'r'+(n+1),chapter:n===1?'c02':'c01',skills:[n===1?'p2':'p1']}))],exams:[{id:'c01-exam',chapters:['c01','c02']}]};
  const p={attempts:[row('first',{answers:{q:{confidence:'guess'},weak:{confidence:'sure'}},results:{q:{points:0,maxPoints:2},weak:{points:0,maxPoints:2}}})]};
  const selected=selectReviewItems(data,p,{now:T0+5*DAY});assert.equal(selected.length,4);assert.equal(selected[0],'r2');assert(!selected.includes('q'));
  assert(!selectReviewItems(data,{attempts:[]},{learnedChapters:['c01']}).includes('r2'));assert.equal(selectReviewItems(data,{attempts:[]}).length,4);
  const seen={attempts:[{...p.attempts[0],itemIds:['r2'],submittedAt:iso(DAY)}]};assert.equal(selectReviewItems(data,seen,{now:T0+5*DAY})[0],'r2');
});
test('real course data supports every exam and reference-result shape',()=>{
  if(!fs.existsSync('dist/exams.json'))return;
  const data=JSON.parse(fs.readFileSync('dist/exams.json','utf8'));
  for(const exam of data.exams){const items=exam.itemIds.map(id=>data.items.find(i=>i.id===id));assert(items.every(Boolean));assert(scoreAssessment(items).maxScore>0);}
  const picks=selectReviewItems(data,{attempts:[]});assert(picks.length>0&&picks.length<=4);assert(picks.every(id=>data.reviewItems.includes(id)));
});

let failures=0;
for(const {title,fn}of tests){try{fn();console.log('PASS',title);}catch(error){failures++;console.error('FAIL',title,error.stack);}}
if(fs.existsSync('dist/exams.json')){
  const data=JSON.parse(fs.readFileSync('dist/exams.json','utf8')),exerciseMap=new Map(data.exercises.map(e=>[e.id,e]));
  const realistic=data.exams.map((exam,index)=>{
    const answers={},codeResults={};for(const id of exam.itemIds){const item=data.items.find(i=>i.id===id);answers[id]={confidence:'sure'};if(item.kind==='choice')answers[id].choice=item.answer;else if(item.kind==='output')answers[id].output=item.expectedStdout;else{const ex=exerciseMap.get(item.exerciseId);answers[id].code=ex.solution;codeResults[id]={stdout:'',tests:ex.tests.map(t=>({passed:true,label:t.label,input:t.stdin??t.expr??'',actual:t.expected,expected:t.expected}))};}}
    return row('sim-'+index,{examId:exam.id,itemIds:exam.itemIds,answers,submittedAt:iso((index+1)*DAY),...scoreAssessment(exam.itemIds.map(id=>data.items.find(i=>i.id===id)),answers,codeResults)});
  });
  const p=cleanAssessmentProgress({attempts:realistic}),bytes=Buffer.byteLength(JSON.stringify(p),'utf8');console.log(`SIZE 18-paper reference-answer simulation: ${bytes} UTF-8 bytes (${(bytes/1024).toFixed(1)} KiB); field caps are not a global byte cap.`);
}
console.log(`${tests.length-failures}/${tests.length} assessment state regressions passed.`);
if(failures)process.exitCode=1;
