import assert from 'node:assert/strict';
import fs from 'node:fs';
import {cleanAssessmentProgress} from './dist/assessments.js';

const source=fs.readFileSync(new URL('./dist/app.js',import.meta.url),'utf8');
const lessons=JSON.parse(fs.readFileSync(new URL('./dist/lessons.json',import.meta.url),'utf8'));
const body=source.slice(source.indexOf('function syncQuizRevisions('),source.indexOf('async function importProgress('));
const clean=new Function('lessons','cleanAssessmentProgress',body+';return cleanProgress;')(lessons,cleanAssessmentProgress);
const old=clean({version:1,current:'p4',drafts:{p4:'def mean(xs):\n    return sum(xs)/len(xs)'},passed:{p1:true},quiz:{p4:true},answers:{p4:1}});
assert.equal(old.current,'p4');assert.equal(old.passed.p1,true);assert.equal(old.quiz.p4,true);assert.equal(old.answers.p4,lessons.find(l=>l.id==='p4').quiz.previousAnswerMap[1]);assert.match(old.drafts.p4,/return/);
const newer=clean({version:2,current:'py01',drafts:{py01:'print(1)',unknown:'bad'},passed:{py01:true,unknown:true},quiz:{'py01:1':true},answers:{'py01:1':2,'p1:1':99},quizRevisions:{'py01:1':2},inputs:{py01:'8 3'},stats:{py01:{attempts:3,failures:2,reference:true}}});
assert.equal(newer.quiz['py01:1'],true);assert.equal(newer.answers['py01:1'],2);assert.equal(newer.inputs.py01,'8 3');assert.equal(newer.stats.py01.failures,2);assert.equal(newer.stats.py01.reference,true);assert.equal(newer.drafts.unknown,undefined);assert.equal(newer.passed.unknown,undefined);assert.equal(newer.answers['p1:1'],undefined);
assert.throws(()=>clean({version:9,drafts:{},passed:{}}));
const superseded=clean({version:2,current:'p1',drafts:{p1:'print(80)'},passed:{p1:true},quiz:{p1:true,'p1:1':true},answers:{p1:1,'p1:1':1}});
assert.equal(superseded.quiz.p1,true);assert.equal(superseded.answers.p1,lessons[0].quiz.answer);assert.equal(superseded.quiz['p1:1'],undefined);assert.equal(superseded.answers['p1:1'],undefined);assert.equal(superseded.passed.p1,true);assert.equal(superseded.drafts.p1,'print(80)');
assert.deepEqual(clean({version:2,...superseded}),superseded);
console.log('PASS old concepts remapped / revised predictions reset / current quizzes retained / drafts / programming history / repeat import');
