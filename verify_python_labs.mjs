import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {assignmentTrace,indexTrace,loopTrace,meanTrace,parseMeanInput,countGoodTrace,accuracyTrace,
 pythonLabs,PYTHON_LAB_META,renderPythonLab,bindPythonLab} from './dist/labs-python.js';

assert.deepEqual(Object.keys(pythonLabs),['p1','p2','p3','p4','p5','p6']);
assert.equal(renderPythonLab('py05'),'');
assert.equal(renderPythonLab('unknown'),'');
assert.equal(bindPythonLab('unknown',null),false);
for(const id of ['constructor','toString','__proto__']){assert.equal(renderPythonLab(id),'');assert.equal(bindPythonLab(id,null),false);}
for(const id of Object.keys(pythonLabs)){
 const html=pythonLabs[id].render();
 assert.match(html,new RegExp(`id="lab-${id}"`));
 assert.match(html,new RegExp(`data-python-lab="${id}"`));
 assert.equal(PYTHON_LAB_META[id].widgetId,`lab-${id}`);
 assert.doesNotMatch(html,/id="(?:list-note|score-slider|tensor-grid)"/);
 assert.equal(pythonLabs[id].bind(null),false);
}
assert.match(renderPythonLab('p6'),/zip\(preds, labels\)/);
assert.match(renderPythonLab('p6'),/correct \/ len\(labels\)/);
assert.match(renderPythonLab('p5'),/record\[&quot;loss&quot;\] &lt; threshold/);
assert.match(renderPythonLab('p4'),/return sum\(values\) \/ len\(values\)/);
assert.match(renderPythonLab('p3'),/print\(score \+ 5\)/);

assert.deepEqual(assignmentTrace(70,0),{base:70,stage:0,value:null,stdout:''});
assert.equal(assignmentTrace(70,1).value,70);
assert.equal(assignmentTrace(70,2).value,75);
assert.equal(assignmentTrace(70,2).stdout,'');
assert.equal(assignmentTrace(70,3).stdout,'75');
assert.equal(assignmentTrace(75,3).stdout,'80');
assert.equal(indexTrace([60,75,90],-1).value,90);
assert.equal(indexTrace([60,75,90],-3).value,60);
assert.equal(indexTrace([60,75,90],3).error,'IndexError');
assert.equal(indexTrace([],0).error,'IndexError');
assert.deepEqual(loopTrace([60,75,90],2).outputs,[65,80]);
assert.equal(loopTrace([60,75,90],3).stdout,'65\n80\n95');
assert.equal(loopTrace([0,-5,10],3).stdout,'5\n0\n15');
assert.equal(meanTrace([2,4],'return').stdout,'调用结果: 3.0');
assert.equal(meanTrace([2,4],'print').stdout,'3.0\n调用结果: None');
assert.equal(meanTrace([-3,0,6]).returned,1);
assert.throws(()=>meanTrace([]),RangeError);
assert.deepEqual(parseMeanInput(' -3, 0，6 '),{ok:true,values:[-3,0,6]});
for(const text of ['', '<img src=x onerror=alert(1)>','1,2,','Infinity','1.5','999'])assert.equal(parseMeanInput(text).ok,false,text);
assert.equal(countGoodTrace([{model:'a',loss:.25},{model:'b',loss:.5},{model:'c',loss:.75}],.5).count,1);
assert.equal(countGoodTrace([{model:'a',loss:0}],0).count,0);
assert.equal(countGoodTrace([],1).count,0);
assert.deepEqual(accuracyTrace([1,0,1],[1,1,1]).rows.map(row=>row.correct),[true,false,true]);
assert.equal(accuracyTrace([1,0,1],[1,1,1]).accuracy,2/3);
assert.equal(accuracyTrace([],[]).accuracy,0);
assert.equal(accuracyTrace([0],[0]).accuracy,1);
assert.equal(accuracyTrace([0],[1]).accuracy,0);
assert.throws(()=>accuracyTrace([1],[]),RangeError);
assert.throws(()=>accuracyTrace([true],[1]),TypeError);

// Bind against a minimal scoped event host: exercise actual module callbacks,
// including repeated binds, remounts and p6 empty/toggle transitions.
class Host {
 constructor(id){this.id=id;this.innerHTML='';this.events=new Map();this.inputValue='';}
 contains(target){return target.owner===this;}
 addEventListener(type,fn){const list=this.events.get(type)||[];list.push(fn);this.events.set(type,list);}
 querySelector(selector){return selector==='[data-plab-input="values"]'?{value:this.inputValue}:null;}
 fire(type,dataset,value=''){
  const element={owner:this,dataset,value,closest(){return this;}};
  for(const fn of this.events.get(type)||[])fn({type,target:element});
 }
}
for(const id of Object.keys(pythonLabs)){
 const host=new Host(`lab-${id}`);assert.equal(pythonLabs[id].bind(host),true);assert.equal(pythonLabs[id].bind(host),true);
 assert.equal(host.events.get('click').length,1,'binding is idempotent for '+id);
 if(id==='p1'){host.fire('click',{plabAction:'example'});for(let i=0;i<3;i++)host.fire('click',{plabAction:'step'});assert.match(host.innerHTML,/<pre>75<\/pre>/);}
 if(id==='p2'){host.fire('click',{plabAction:'index',index:'-3'});assert.match(host.innerHTML,/scores\[0\] 和 scores\[-3\]/);}
 if(id==='p3'){host.fire('click',{plabAction:'original'});host.fire('click',{plabAction:'next'});assert.match(host.innerHTML,/<pre>65<\/pre>/);host.fire('click',{plabAction:'all'});assert.match(host.innerHTML,/<pre>65\n80\n95<\/pre>/);}
 if(id==='p4'){host.inputValue='0, 6';host.fire('click',{plabAction:'apply'});host.fire('click',{plabAction:'print'});assert.match(host.innerHTML,/<pre>3.0\n调用结果: None<\/pre>/);host.inputValue='<script>alert(1)</script>';host.fire('click',{plabAction:'apply'});assert.doesNotMatch(host.innerHTML,/<script>/);}
 if(id==='p5'){host.fire('click',{plabAction:'original'});host.fire('input',{plabInput:'threshold'},'25');assert.match(host.innerHTML,/恰好相等，不计入/);assert.match(host.innerHTML,/<pre>0<\/pre>/);host.fire('click',{plabAction:'empty'});assert.match(host.innerHTML,/records 是空列表/);}
 if(id==='p6'){
  host.fire('click',{plabAction:'reset'});host.fire('click',{plabAction:'toggle',field:'preds',index:'1'});assert.match(host.innerHTML,/<pre>1.0<\/pre>/);
  host.fire('click',{plabAction:'wrong'});assert.match(host.innerHTML,/<pre>0.0<\/pre>/);
  host.fire('click',{plabAction:'empty'});assert.match(host.innerHTML,/zip\(\[\], \[\]\)/);assert.match(host.innerHTML,/不进行 0\/0 除法/);
  host.fire('click',{plabAction:'add'});assert.match(host.innerHTML,/preds = \[0\]/);assert.match(host.innerHTML,/labels = \[1\]/);
 }
}

// Independent real Python oracle, batched into one subprocess. No student code
// or filesystem mutation is involved.
const cases=[];
for(let base=0;base<=100;base+=5)for(let stage=0;stage<=3;stage++)cases.push({kind:'assignment',base,stage});
for(let index=-5;index<=5;index++)cases.push({kind:'index',values:[60,75,90],index});
for(const values of [[60,75,90],[0,-5,10],[]])for(let steps=0;steps<=values.length;steps++)cases.push({kind:'loop',values,steps});
for(const values of [[2,4],[7],[-3,0,6],[0,0],[-1,-2,-4]])for(const mode of ['return','print'])cases.push({kind:'mean',values,mode});
for(let threshold=0;threshold<=100;threshold+=5)cases.push({kind:'count',threshold:threshold/100,losses:[.25,.5,.75]});
for(let length=0;length<=4;length++)for(let code=0;code<4**length;code++){
 let remaining=code,preds=[],labels=[];for(let i=0;i<length;i++){preds.push(remaining%2);labels.push(Math.floor(remaining/2)%2);remaining=Math.floor(remaining/4);}cases.push({kind:'accuracy',preds,labels});
}
const oracle=String.raw`
import contextlib,io,json,sys
result=[]
for case in json.load(sys.stdin):
 kind=case['kind']
 if kind=='assignment':
  code='score = '+str(case['base'])+'\nscore = score + 5\nprint(score)'
  capture=io.StringIO();namespace={}
  with contextlib.redirect_stdout(capture):exec('\n'.join(code.splitlines()[:case['stage']]),namespace)
  result.append({'value':namespace.get('score'),'stdout':capture.getvalue().strip()})
 elif kind=='index':
  try:result.append({'ok':True,'value':case['values'][case['index']]})
  except IndexError:result.append({'ok':False,'value':None})
 elif kind=='loop':result.append('\n'.join(str(score+5) for score in case['values'][:case['steps']]))
 elif kind=='mean':
  average=sum(case['values'])/len(case['values'])
  result.append('调用结果: '+str(average) if case['mode']=='return' else str(average)+'\n调用结果: None')
 elif kind=='count':result.append(sum(loss<case['threshold'] for loss in case['losses']))
 elif kind=='accuracy':
  correct=sum(pred==label for pred,label in zip(case['preds'],case['labels']))
  result.append(correct/len(case['labels']) if case['labels'] else 0.0)
print(json.dumps(result,ensure_ascii=True))
`;
const proc=spawnSync(process.env.PYTHON||'python',['-X','utf8','-c',oracle],{input:JSON.stringify(cases),encoding:'utf8',maxBuffer:2*1024*1024});
assert.equal(proc.status,0,proc.stderr||proc.error?.message);
const expected=JSON.parse(proc.stdout);
for(let i=0;i<cases.length;i++){
 const c=cases[i],want=expected[i];let actual;
 if(c.kind==='assignment'){const trace=assignmentTrace(c.base,c.stage);actual={value:trace.value,stdout:trace.stdout};}
 if(c.kind==='index'){const trace=indexTrace(c.values,c.index);actual={ok:trace.ok,value:trace.value};}
 if(c.kind==='loop')actual=loopTrace(c.values,c.steps).stdout;
 if(c.kind==='mean')actual=meanTrace(c.values,c.mode).stdout;
 if(c.kind==='count')actual=countGoodTrace(c.losses.map((loss,index)=>({model:String(index),loss})),c.threshold).count;
 if(c.kind==='accuracy')actual=accuracyTrace(c.preds,c.labels).accuracy;
 assert.deepEqual(actual,want,JSON.stringify(c));
}
console.log(`PASS six dedicated Python labs; scoped event callbacks, defaults, empty/boundary cases and ${cases.length} real Python oracle cases`);
