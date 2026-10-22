import {createAssessmentCenter,cleanAssessmentProgress} from './assessments.js';
import {createProgressSync} from './sync.js';
import {renderLessonLab,bindLessonLab} from './labs.js';

const $ = (selector, root = document) => root.querySelector(selector);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const icon = (name, size=14) => {
  const paths = {arrow:'<path d="M4 8h9M9 4l4 4-4 4"/>',play:'<path d="m5 3 8 5-8 5z"/>',check:'<path d="m3 8 3 3 7-7"/>',clock:'<circle cx="8" cy="8" r="5.5"/><path d="M8 4.5V8l2.5 1.5"/>',book:'<path d="M8 3v11M2 3c3-1 4 0 6 1 2-1 3-2 6-1v9c-3-1-4 0-6 1-2-1-3-2-6-1z"/>',code:'<path d="m5 4-4 4 4 4m6-8 4 4-4 4M9 2 7 14"/>',hint:'<path d="M6 12h4m-4 2h4M5 9c-4-5 2-9 5-6 3 2 1 5 0 6l-.5 1h-3z"/>',reset:'<path d="M3 6a5 5 0 1 1-.3 3M3 2v4h4"/>',download:'<path d="M8 1v9M4 6l4 4 4-4M2 11v3h12v-3"/>',upload:'<path d="M8 11V2M4 6l4-4 4 4M2 11v3h12v-3"/>',menu:'<path d="M2 4h12M2 8h12M2 12h12"/>',leaf:'<path d="M13 2c-8-1-13 8-7 10 6 2 7-5 7-10ZM4 13l6-7"/>',close:'<path d="m4 4 8 8m0-8-8 8"/>',spark:'<path d="m8 1 1.8 5.2L15 8l-5.2 1.8L8 15l-1.8-5.2L1 8l5.2-1.8Z"/>'};
  return `<svg width="${size}" height="${size}" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${paths[name] || paths.code}</svg>`;
};
let lessons = [], currentTab='learn', activeConsole='result', hintCount={}, outputs={}, busy=false, native=false, runtimeState='正在连接运行环境', worker, workerReady=false, timerEnd=0, toastTimer;
let state={current:'p1',drafts:{},quiz:{},passed:{},answers:{},stats:{},inputs:{},quizRevisions:{}};
try { state={...state,...JSON.parse(localStorage.getItem('kaillian-v1') || '{}')}; } catch {}
state.assessments=cleanAssessmentProgress(state.assessments);
let assessmentCenter,assessmentPromise,progressSync;
async function openAssessments(){
 try{
  assessmentPromise??=createAssessmentCenter({getProgress:()=>state,saveProgress:save,toast,
   getRuntime:()=>({native,ready:native||workerReady}),
   runCode:async request=>{
    if(!native)return browserRun(request);
    const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request),signal:AbortSignal.timeout(30000)});
    const result=await response.json();if(!response.ok)throw new Error(result.error?.message||'运行服务未能接受请求');return result;
   }}).catch(error=>{assessmentPromise=undefined;throw error;});
  assessmentCenter=await assessmentPromise;assessmentCenter.open();
 }catch(error){toast('考核中心暂时未加载：'+error.message);}
}
const lesson = () => lessons.find(item => item.id === state.current) || lessons[0];
const starter = '# 从这里开始，写出完整代码。\n';
const draft = id => Object.hasOwn(state.drafts,id) ? state.drafts[id] : starter;
const passedCount = () => lessons.filter(item=>state.passed[item.id]).length;
const xp = () => lessons.reduce((n,item)=>n+(item.quizzes||[item.quiz]).reduce((sum,_,i)=>sum+(state.quiz[i?item.id+':'+i:item.id]?15:0),0)+(state.passed[item.id]?35:0),0);
function save(){if(progressSync){progressSync.changed();return;}try {localStorage.setItem('kaillian-v1',JSON.stringify({...state,version:2}));} catch {toast('浏览器未允许保存，请导出进度备份。');} }
function toast(message, bonus=''){clearTimeout(toastTimer);$('#toast')?.remove();document.body.insertAdjacentHTML('beforeend',`<div class="toast" id="toast" role="status">${esc(message)}${bonus?`<strong>${esc(bonus)}</strong>`:''}</div>`);toastTimer=setTimeout(()=>$('#toast')?.remove(),3200);}
function celebrate(){const colors=['#bde299','#b6a0ec','#e5ce87','#a6c8b1'];const box=document.createElement('div');box.className='celebrate';for(let i=0;i<24;i++){const bit=document.createElement('i');bit.className='confetti';bit.style.cssText=`left:${15+Math.random()*75}%;background:${colors[i%4]};animation-delay:${Math.random()*.4}s;transform:rotate(${Math.random()*180}deg)`;box.append(bit);}document.body.append(box);setTimeout(()=>box.remove(),2200);}
function snippet(text){return `<div class="snippet"><pre>${esc(text)}</pre></div>`;}
function renderNavBase(){
  let group='';let groupIndex=0;
  return lessons.map((item,index)=>{let heading='';if(item.group!==group){group=item.group;heading=`<div class="group-title"><span>0${++groupIndex}</span>${esc(group)}</div>`;}return `${heading}<button class="lesson-nav ${item.id===state.current?'active':''} ${state.passed[item.id]?'done':''}" data-lesson="${item.id}" aria-current="${item.id===state.current?'step':'false'}"><span class="nav-number">${state.passed[item.id]?'✓':String(index+1).padStart(2,'0')}</span><span>${esc(item.title)}</span>${item.id===state.current?'<i class="nav-dot"></i>':''}</button>`;}).join('');
}
function renderBase(){
 const l=lesson(), index=lessons.indexOf(l), count=passedCount();
 $('#app').innerHTML=`<div class="app-shell"><aside class="sidebar" id="sidebar"><a class="brand" href="#" aria-label="开练，返回当前学习"><span class="brand-mark">&gt;_</span><span><span class="brand-name">开练</span><small>SMALL STEPS. REAL CODE.</small></span></a><div class="journey"><div class="eyebrow">YOUR LEARNING PATH</div><div class="journey-row"><span>从看懂，到写出</span><b>${count} / ${lessons.length}</b></div><div class="track"><span style="width:${count/lessons.length*100}%"></span></div></div><nav class="nav-scroll" aria-label="学习关卡">${renderNav()}</nav><div class="side-foot"><div class="profile"><span class="avatar">you</span><span><b>每次，向前一点</b><small>${xp()} XP · ${count===lessons.length?'第一轮已通关':count<6?'Python 探索者':'张量探索者'}</small></span></div><button class="text-button icon-button" id="settings">${icon('reset',12)} 学习设置与进度</button></div></aside><main class="main"><header class="topbar"><div class="breadcrumb"><button class="mobile-toggle" id="mobile-toggle" aria-label="展开学习路线">${icon('menu',17)}</button>LEARNING LAB <span>/ ${esc(l.group)}</span></div><div class="top-actions"><div class="runtime ${native||workerReady?'ready':''}" id="runtime-status"><i></i><span>${esc(runtimeState)}</span></div><button class="icon-button" id="export" title="导出学习进度">${icon('download')}<span class="label">导出进度</span></button></div></header><section class="hero"><div class="hero-copy"><span class="sprint-label"><i></i> 一个小目标，一次真进步</span><h1>把「看懂」变成「写出」。</h1><p>先学一点，动手试试。每次尝试，都有回音。</p><div class="hero-path"><b>PYTHON</b><span>────</span><span>TENSORS</span><span>────</span><span>PYTORCH</span></div></div><div class="hero-art" aria-hidden="true"><div class="art-grid"></div><div class="code-tile">[ ]</div><div class="code-tile">∇</div></div></section><div class="study-strip"><div class="strip-left"><span>${icon('book',13)} 第 <strong>${String(index+1).padStart(2,'0')}</strong> / ${lessons.length} 关</span><span>${icon('clock',13)} 约 <strong>${l.minutes} 分钟</strong></span><span>${icon('leaf',13)} 跟着自己的节奏</span></div><button class="timer-btn" id="timer">${icon('clock',12)}<span>开启 15 分钟专注</span></button></div><div class="workspace"><section class="panel lesson-panel"><div class="panel-label"><span>${icon('book',13)} 今日微课</span><span class="pill">${l.runtime==='torch'?'PYTORCH':'PYTHON'}</span></div><div class="lesson-header"><h2>${esc(l.title)}</h2><div class="lesson-meta">${esc(l.tag)} <span>·</span> ${state.passed[l.id]?'已完成，随时重练':'由浅入深，即学即练'}</div></div><div class="tabs" role="tablist" aria-label="学习步骤">${[['learn','学一点'],['quiz','预测一下'],['mission','动手写']].map(([key,label],i)=>`<button class="tab ${currentTab===key?'active':''}" role="tab" aria-selected="${currentTab===key}" data-tab="${key}"><span class="num">${key==='quiz'&&quizComplete(l)?'✓':i+1}</span>${label}</button>`).join('')}</div><div class="lesson-content" id="lesson-content"></div></section><div class="right-column"><section class="editor-panel" aria-label="Python 代码编辑器"><div class="editor-toolbar"><div class="editor-file"><span class="file-icon">⌁</span> practice.py</div><div class="editor-language"><span>${l.runtime==='torch'?'Python · torch':'Python'}</span><div class="editor-dots"><i></i><i></i><i></i></div></div></div><div class="editor-region"><div class="line-numbers" id="line-numbers" aria-hidden="true">1</div><textarea class="code-editor" id="editor" aria-label="在这里编写完整的 Python 代码" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" placeholder="# 从空白开始，试着写几行…"></textarea></div><div class="editor-footer"><div class="editor-tools"><button class="dark-tool" id="hint">${icon('hint',13)} 提示</button><button class="dark-tool" id="rewrite">${icon('reset',12)} 重写</button></div><div class="editor-footer-right"><button class="run-btn" id="run" ${busy?'disabled':''}>${icon('play',12)}运行</button><button class="submit-btn" id="submit" ${busy?'disabled':''}>${icon('check',13)}提交判题</button></div></div><div class="shortcut">Ctrl / ⌘ + Enter 运行 <span style="float:right" id="save-status">草稿自动保存</span></div></section><section class="panel console-panel"><div class="console-heading"><b id="console-title">${icon('code',13)} 运行与反馈</b><span id="console-meta">READY WHEN YOU ARE</span></div><div class="console-body" id="console-body" aria-live="polite"></div></section></div></div><footer class="bottom-note"><span>${icon('check',11)} 进度保存在当前浏览器 · 可导出备份</span><span>允许查文档 · 鼓励试错 · 随时快进</span></footer></main></div><input type="file" id="import-file" accept="application/json,.json" class="hidden">`;
 $('#editor').value=draft(l.id);updateLines();renderContent();renderConsole();bind();updateTimer();
}
function bindContentBase(){
 document.querySelectorAll('[data-go-tab]').forEach(button=>button.onclick=()=>switchTab(button.dataset.goTab));
 const focus=$('#focus-editor');if(focus)focus.onclick=()=>{$('#editor').focus();$('#editor').scrollIntoView({behavior:'smooth',block:'center'});};
}
function switchTab(tab){currentTab=tab;render();}
function bind(){
 document.querySelectorAll('button.lesson-nav[data-lesson]').forEach(b=>b.onclick=()=>navigate(b.dataset.lesson));
 document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>switchTab(b.dataset.tab));
 $('#editor').addEventListener('input',()=>{state.drafts[state.current]=$('#editor').value;save();updateLines();$('#save-status').textContent='已保存';});
 $('#editor').addEventListener('scroll',()=>{$('#line-numbers').scrollTop=$('#editor').scrollTop;});
 $('#editor').addEventListener('keydown',e=>{
   const el=e.target;
   if(e.key==='Tab'){e.preventDefault();const start=el.selectionStart,end=el.selectionEnd;el.setRangeText('    ',start,end,'end');el.dispatchEvent(new Event('input'));}
   if(e.key==='Enter'&&!e.ctrlKey&&!e.metaKey){e.preventDefault();const before=el.value.slice(0,el.selectionStart),line=before.split('\n').at(-1),indent=(line.match(/^\s*/)?.[0]||'')+(line.trimEnd().endsWith(':')?'    ':'');el.setRangeText('\n'+indent,el.selectionStart,el.selectionEnd,'end');el.dispatchEvent(new Event('input'));}
   if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();run('run');}
   if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();save();toast('草稿已保存');}
 });
 $('#run').onclick=()=>run('run');$('#submit').onclick=()=>run('submit');
 $('#hint').onclick=()=>{activeConsole='hints';hintCount[state.current]=Math.max(1,hintCount[state.current]||0);renderConsole();};
 $('#rewrite').onclick=()=>modal('从空白再写一次？','当前关卡的代码会清空，已获得的通关记录保留。',()=>{state.drafts[state.current]=starter;save();render();},'清空草稿');
 $('#export').onclick=exportProgress;$('#settings').onclick=settings;
 $('#mobile-toggle').onclick=()=>$('#sidebar').classList.toggle('open');
 $('#timer').onclick=()=>{timerEnd=timerEnd?0:Date.now()+15*60*1000;updateTimer();if(timerEnd)toast('专注时间开始。到时可以继续，不会中断代码。');};
 $('#import-file').onchange=importProgress;
 $('.brand').onclick=e=>{e.preventDefault();navigate(state.current);};
}
function navigate(id){navExpanded.add(lessons.find(x=>x.id===id)?.chapter);state.current=id;currentTab='learn';activeConsole='result';save();render();window.scrollTo({top:0,behavior:'smooth'});}
function updateLines(){const ed=$('#editor');if(ed)$('#line-numbers').textContent=Array.from({length:Math.max(12,ed.value.split('\n').length)},(_,i)=>i+1).join('\n');}
function format(value){
 const repr=v=>v===null?'None':typeof v==='boolean'?(v?'True':'False'):typeof v==='string'?JSON.stringify(v):Array.isArray(v)?'['+v.map(repr).join(', ')+']':typeof v==='object'?'{'+Object.entries(v).map(([k,x])=>repr(k)+': '+repr(x)).join(', ')+'}':String(v);
 return typeof value==='string'?value:repr(value);
}
function renderConsoleBase(){
 const l=lesson(),node=$('#console-body');if(!node)return;
 if(activeConsole==='hints'){
   const count=hintCount[l.id]||1;
   $('#console-title').innerHTML=`${icon('hint',13)} 一次只看一步`;
   $('#console-meta').textContent=`HINT ${Math.min(count,3)} / 3`;
   node.innerHTML=l.hints.slice(0,count).map((hint,i)=>`<div class="hint-card"><b>HINT 0${i+1}</b>${esc(hint)}</div>`).join('')+`<div class="hint-actions">${count<3?'<button class="button outline" id="next-hint">再给一点提示</button>':'<button class="button outline" id="show-solution">查看参考实现</button>'}<button class="button" id="back-result">返回运行结果</button></div><div id="solution-slot"></div>`;
   if($('#next-hint'))$('#next-hint').onclick=()=>{hintCount[l.id]=count+1;renderConsole();};
   if($('#show-solution'))$('#show-solution').onclick=()=>{$('#solution-slot').innerHTML=`<div class="reference"><p>看懂后，关掉参考，重新写一遍。参考实现不会替你通关。</p><pre>${esc(l.solution)}</pre></div>`;$('#show-solution').disabled=true;};
   $('#back-result').onclick=()=>{activeConsole='result';renderConsole();};return;
 }
 $('#console-title').innerHTML=`${icon('code',13)} 运行与反馈`;
 const result=outputs[l.id];
 if(!result){$('#console-meta').textContent='READY WHEN YOU ARE';node.innerHTML=`<div class="empty-state"><div class="empty-icon">${icon('play',15)}</div><p>写几行，让想法跑起来。<br><small>运行看输出，提交看测试。卡住时，提示就在旁边。</small></p></div>`;return;}
 if(result.loading){$('#console-meta').textContent='RUNNING';node.innerHTML=`<div class="empty-state"><span class="spinner"></span><p>${esc(result.message||'正在运行你的代码…')}<br><small>代码在独立进程中执行，界面可以继续操作。</small></p></div>`;return;}
 $('#console-meta').textContent=result.elapsed?`${result.elapsed}s · ${native?'NATIVE PYTHON':'BROWSER PYTHON'}`:'FEEDBACK';
 if(result.bridge){node.innerHTML=`<div class="bridge-note">这关需要真实 PyTorch。本机学习台已提供完整运行环境。<br>请先启动项目里的「启动学习台.ps1」，然后打开本机版。<br><a class="button outline" href="http://127.0.0.1:8766" target="_blank" rel="noopener">打开本机版 ${icon('arrow',12)}</a><br>进度可用页面右上角导出，再到本机版导入。</div>`;return;}
 let html='';
 if(result.error)html+=errorBlock(result.error);
 if(result.tests?.length){const passed=result.tests.filter(t=>t.passed).length;html+=`<div class="judge-heading"><b class="verdict ${result.ok?'':'fail'}">${icon(result.ok?'check':'code',14)} ${result.ok?'ACCEPTED':'再试一次'}</b><span class="judge-sub">${passed} / ${result.tests.length} tests passed</span></div>${result.tests.map((test,i)=>`<details class="case ${test.passed?'':'fail'}" ${!test.passed?'open':''}><summary><span>${test.passed?'✓':'○'} ${esc(test.label)}</span><span>${test.passed?'通过':'查看反馈'}</span></summary><div class="case-detail">输入：${esc(test.input)}\n期望：${esc(format(test.expected))}\n${test.error?`错误：${esc(test.error.message)}\n${esc(test.error.guide)}`:`实际：${esc(format(test.actual))}`}</div></details>`).join('')}`;if(result.ok){const next=lessons[lessons.indexOf(l)+1];html+=`<div class="success-note">${esc(l.success)}</div>${next?`<button class="button primary next-btn" id="next-lesson">下一关 · ${esc(next.title)} ${icon('arrow',13)}</button>`:`<div class="all-complete">这轮最后一关已完成。你可以回看薄弱处，或导出这次学习的全部代码。</div>`}`;}}
 if(result.stdout)html+=`<div class="mini-label">标准输出</div><pre class="stdout">${esc(result.stdout)}</pre>`;
 if(!result.error&&!result.tests?.length&&!result.stdout)html=`<div class="empty-state"><div class="empty-icon">${icon('check',15)}</div><p>代码运行完成，没有输出。<br><small>函数题可以点「提交判题」，用不同输入检查返回值。</small></p></div>`;
 node.innerHTML=html;
 if($('#next-lesson'))$('#next-lesson').onclick=()=>navigate(lessons[lessons.indexOf(l)+1].id);
}
function errorBlock(error){return `<div class="error-box"><b>${esc(error.type||'执行错误')}${error.line?` · 第 ${error.line} 行`:''}</b><pre>${esc(error.message)}</pre>${esc(error.guide||'请重试，或点提示看看这一关的思路。')}</div>`;}
let requestId=0;const pending=new Map();
function setRuntime(message,ready=false){runtimeState=message;const el=$('#runtime-status');if(el){el.classList.toggle('ready',ready);el.innerHTML=`<i></i><span>${esc(message)}</span>`;}}
function startWorker(){workerReady=false;worker=new Worker('python-worker.js',{type:'module'});worker.onmessage=({data})=>{
 if(data.type==='ready'){workerReady=true;setRuntime('Python 已就绪',true);}
 if(data.type==='status')setRuntime(data.message);
 if(data.type==='result'){const p=pending.get(data.id);if(p){clearTimeout(p.timer);pending.delete(data.id);p.resolve(data.result);}}
 if(data.type==='fatal'){setRuntime('运行环境加载失败，可重试');for(const [id,p]of pending){clearTimeout(p.timer);p.reject(new Error(data.message));pending.delete(id);}worker.terminate();worker=undefined;}
};worker.onerror=()=>{setRuntime('浏览器运行环境连接失败');for(const [id,p]of pending){clearTimeout(p.timer);p.reject(new Error('Python 运行环境未能加载。请检查网络后重试，或使用本机版。'));pending.delete(id);}worker?.terminate();worker=undefined;};worker.postMessage({type:'init'});}
async function connectRuntime(){
 try {const response=await fetch('/api/health',{signal:AbortSignal.timeout(1800)});const health=await response.json();if(health.runtime==='native'){native=true;setRuntime('Python + PyTorch 已就绪',true);return;}}catch{}
 startWorker();
}
function browserRun(request){if(!worker)startWorker();return new Promise((resolve,reject)=>{const id=++requestId;const timer=setTimeout(()=>{worker?.terminate();worker=undefined;workerReady=false;setRuntime('运行已停止，点击运行可重试');for(const [pid,p] of pending){clearTimeout(p.timer);p.reject(new Error('运行超时。检查循环是否终止；首次加载也可能需要更好的网络连接。'));pending.delete(pid);}},workerReady?12000:90000);pending.set(id,{resolve,reject,timer});worker.postMessage({...request,id});});}
async function run(action){
 if(busy)return;const l=lesson(),code=$('#editor').value;state.drafts[l.id]=code;save();activeConsole='result';
 if(!code.split('\n').some(line=>line.trim()&&!line.trim().startsWith('#'))){toast('先写一两行试试；左边「动手写」里有完整任务。');switchTab('mission');return;}
 if(l.runtime==='torch'&&!native){outputs[l.id]={bridge:true};renderConsole();return;}
 busy=true;outputs[l.id]={loading:true,message:l.runtime==='torch'?'正在启动真实 PyTorch，首次运行稍等几秒…':workerReady||native?'正在执行并检查…':'正在加载 Python，首次使用稍等片刻…'};renderConsole();$('#run').disabled=true;$('#submit').disabled=true;const started=performance.now();
 try{const request={lesson:l.id,code,action,stdin:state.inputs?.[l.id]??l.tests[0].stdin??''}; if(action==='submit'){state.stats??={};state.stats[l.id]??={attempts:0,failures:0};state.stats[l.id].attempts++;save();}let result;
   if(native){const response=await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request),signal:AbortSignal.timeout(30000)});result=await response.json();}
   else result=await browserRun(request);
   result.elapsed=((performance.now()-started)/1000).toFixed(2);outputs[l.id]=result;if(action==='submit'&&!result.ok){state.stats[l.id].failures++;save();}
   if(action==='submit'&&result.ok&&!state.passed[l.id]){state.passed[l.id]=true;save();toast('通过了！这是你亲手写出的进步。','+35 XP');celebrate();}
 }catch(error){outputs[l.id]={ok:false,error:{type:'运行提示',message:error.message,guide:native?'本机服务可能已停止，请重新启动学习台。':'可点击运行重试；也可以打开本机版学习。'}};}
 finally{busy=false;render();}
}
function updateTimer(){const button=$('#timer');if(!button)return;if(!timerEnd){button.classList.remove('running');button.innerHTML=`${icon('clock',12)}<span>开启 15 分钟专注</span>`;return;}const remain=Math.max(0,Math.ceil((timerEnd-Date.now())/1000));if(!remain){timerEnd=0;toast('15 分钟到了。休息一下，或者继续当前这题。');return updateTimer();}button.classList.add('running');button.innerHTML=`${icon('clock',12)}<span>${String(Math.floor(remain/60)).padStart(2,'0')}:${String(remain%60).padStart(2,'0')} · 点击结束</span>`;}
setInterval(updateTimer,1000);
function modal(title,body,action,label='确定'){document.querySelector('.modal-overlay')?.remove();document.body.insertAdjacentHTML('beforeend',`<div class="modal-overlay" id="modal-overlay"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title"><h3 id="modal-title">${esc(title)}</h3><p>${esc(body)}</p><div class="modal-actions"><button class="button outline" id="modal-cancel">取消</button><button class="button primary" id="modal-confirm">${esc(label)}</button></div></section></div>`);const close=()=>$('#modal-overlay')?.remove();$('#modal-cancel').onclick=close;$('#modal-confirm').onclick=()=>{close();action();};$('#modal-overlay').onclick=e=>{if(e.target.id==='modal-overlay')close();};$('#modal-cancel').focus();}
function exportProgress(){const blob=new Blob([JSON.stringify({version:2,exportedAt:new Date().toISOString(),...state},null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const anchor=document.createElement('a');anchor.href=url;anchor.download='开练-学习进度.json';anchor.click();setTimeout(()=>URL.revokeObjectURL(url),1500);toast('已导出进度和代码草稿');}
function settings(){document.body.insertAdjacentHTML('beforeend',`<div class="modal-overlay" id="modal-overlay"><section class="modal" role="dialog" aria-modal="true" aria-labelledby="settings-title"><h3 id="settings-title">带着进度继续学</h3><p>草稿、预测题和通关状态保存在当前浏览器。换设备或在网页版与本机版之间切换时，用导出 / 导入继续。</p><div class="modal-actions" style="flex-wrap:wrap"><button class="button outline" id="import-trigger">${icon('upload')}导入进度</button><button class="button outline" id="reset-progress">重新开始</button><button class="button primary" id="close-settings">完成</button></div></section></div>`);$('#close-settings').onclick=()=>$('#modal-overlay').remove();$('#import-trigger').onclick=()=>{$('#modal-overlay').remove();$('#import-file').click();};$('#reset-progress').onclick=()=>modal('确定清空当前学习空间？','这会清空当前空间的代码草稿、预测答案、通关与考核记录。若已登录账号，清空结果还会同步到云端，影响其他设备。请先导出进度备份。',()=>{state={current:'p1',drafts:{},quiz:{},passed:{},answers:{}};outputs={};hintCount={};currentTab='learn';save();render();toast('已重置，可以重新出发');},'清空记录');}
function syncQuizRevisions(progress){
 progress.quizRevisions??={};progress.quiz??={};progress.answers??={};let reset=0;
 for(const l of lessons)(l.quizzes||[l.quiz]).forEach((q,i)=>{
  const key=i?l.id+':'+i:l.id,revision=q.revision??1,previous=progress.quizRevisions[key]??1;
  if(previous!==revision){
   if(previous===1&&Array.isArray(q.previousAnswerMap)){
    const old=progress.answers[key];if(Number.isInteger(old))progress.answers[key]=q.previousAnswerMap[old];
   }else{
    if(progress.quiz[key]||progress.answers[key]!==undefined)reset++;
    delete progress.quiz[key];delete progress.answers[key];
   }
  }
  progress.quizRevisions[key]=revision;
 });
 return reset;
}
function cleanProgress(data){
 if(![1,2].includes(data?.version)||!data.drafts||!data.passed)throw new Error('格式不匹配');
 const clean={current:lessons.some(l=>l.id===data.current)?data.current:'p1',drafts:{},quiz:{},passed:{},answers:{},stats:{},inputs:{},quizRevisions:{},assessments:cleanAssessmentProgress(data.assessments)};
 for(const l of lessons){
  if(typeof data.drafts[l.id]==='string')clean.drafts[l.id]=data.drafts[l.id].slice(0,16000);
  if(data.passed[l.id]===true)clean.passed[l.id]=true;
  if(typeof data.inputs?.[l.id]==='string')clean.inputs[l.id]=data.inputs[l.id].slice(0,4000);
  (l.quizzes||[l.quiz]).forEach((q,i)=>{const key=i?l.id+':'+i:l.id,a=data.answers?.[key];if(data.quiz?.[key]===true)clean.quiz[key]=true;if(Number.isInteger(a)&&a>=0&&a<q.options.length)clean.answers[key]=a;clean.quizRevisions[key]=data.quizRevisions?.[key]??1;});
  const s=data.stats?.[l.id];if(s&&typeof s==='object')clean.stats[l.id]={attempts:Math.max(0,Math.min(1e6,Number(s.attempts)||0)),failures:Math.max(0,Math.min(1e6,Number(s.failures)||0)),reference:s.reference===true};
 }
 syncQuizRevisions(clean);return clean;
}
async function importProgress(event){const file=event.target.files?.[0];if(!file)return;try{if(file.size>20e6)throw new Error('文件太大');state=cleanProgress(JSON.parse(await file.text()));assessmentCenter?.onProgressImported?.();outputs={};hintCount={};save();currentTab='learn';navExpanded.add(lesson().chapter);render();toast('进度已导入，继续上次的旅程');}catch{toast('这不是有效的开练进度文件，请选择之前导出的 JSON。');}}
document.addEventListener('keydown',e=>{if(e.key==='Escape'){$('.modal-overlay')?.remove();$('#sidebar')?.classList.remove('open');}});

let course={chapters:[],sources:[]};
const navExpanded=new Set();
const difficulty={1:'基础',2:'进阶',3:'挑战'};
const quizKey=(l,i)=>i?l.id+':'+i:l.id;
const quizComplete=l=>(l.quizzes||[l.quiz]).every((_,i)=>state.quiz[quizKey(l,i)]);
const wantsReview=l=>Boolean(state.stats?.[l.id]?.reference || (!state.passed[l.id]&&state.stats?.[l.id]?.failures));
function renderNav(){
 const groups=[...new Set(lessons.map(x=>x.group))];
 return `<button class="nav-map" id="nav-map">${icon('book',13)} 课程地图 · 20–30h ${icon('arrow',12)}</button>`+groups.map((name,index)=>{
  const items=lessons.filter(x=>x.group===name),chapter=items[0].chapter;
  return `<div class="nav-chapter"><button class="group-toggle" data-chapter="${chapter}" aria-expanded="${navExpanded.has(chapter)}"><span>${String(index+1).padStart(2,'0')}</span><b>${esc(name)}</b><small>${items.filter(x=>state.passed[x.id]).length}/${items.length}</small><i>${navExpanded.has(chapter)?'−':'+'}</i></button>${navExpanded.has(chapter)?items.map(item=>`<button class="lesson-nav ${item.id===state.current?'active':''} ${state.passed[item.id]?'done':''}" data-lesson="${item.id}" aria-current="${item.id===state.current?'step':'false'}"><span class="nav-number">${state.passed[item.id]?'✓':String(lessons.indexOf(item)+1).padStart(2,'0')}</span><span>${esc(item.title)}</span><i class="level-dot level-${item.level}" title="${difficulty[item.level]}"></i></button>`).join(''):''}</div>`;
 }).join('');
}
function render(){
 state.stats??={};state.inputs??={};renderBase();
 const l=lesson();
 if(progressSync){$('.top-actions').insertAdjacentHTML('afterbegin',progressSync.renderButton());$('#cloud-progress').onclick=progressSync.open;}
 $('.top-actions').insertAdjacentHTML('afterbegin',`<button class="icon-button" id="course-map">${icon('book')}<span>课程地图</span></button>`);
 $('.lesson-meta').insertAdjacentHTML('afterbegin',`<span class="level-badge level-${l.level}">${difficulty[l.level]}</span><span class="kind-badge">${esc(l.kind)}</span>`);
 $('.hero-copy>p').textContent='12 章练习约 20–30h · 新增分层考核与复习约 4–6h';
 document.querySelectorAll('[data-chapter]').forEach(b=>b.onclick=()=>{const id=b.dataset.chapter;navExpanded.has(id)?navExpanded.delete(id):navExpanded.add(id);render();});
 $('#course-map').onclick=openMap;$('#nav-map').onclick=openMap;$('.top-actions').insertAdjacentHTML('afterbegin',`<button class="icon-button" id="assessment-open">${icon('check')}<span>考核与复习</span></button>`);$('#nav-map').insertAdjacentHTML('afterend',`<button class="nav-map" id="assessment-nav">${icon('check',13)}考核与间隔复习 ${icon('arrow',12)}</button>`);$('#assessment-open').onclick=openAssessments;$('#assessment-nav').onclick=openAssessments;
 if(l.tests.some(t=>Object.hasOwn(t,'stdin'))){
  $('.editor-footer').insertAdjacentHTML('beforebegin',`<details class="stdin-panel" open><summary>标准输入 <small>「运行」使用这里的输入；「提交」使用全部测试</small></summary><textarea id="stdin-editor" aria-label="测试用标准输入" spellcheck="false"></textarea></details>`);
  $('#stdin-editor').value=state.inputs[l.id]??l.tests[0].stdin??'';
  $('#stdin-editor').oninput=e=>{state.inputs[l.id]=e.target.value;save();};
 }
}
function lessonResources(l){return `<div class="reading-links"><b>对应的专业资料</b>${l.resources.map(r=>`<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)} ↗</a>`).join('')}<small>本节讲解与题目为原创；链接用于知识核对和延伸学习。</small></div>`;}
function conceptWidget(l){return renderLessonLab(l.id);}
function renderContent(){
 const l=lesson(),examples=l.examples||[];let body='';
 if(currentTab==='learn'){
  body=`<div class="learning-goals"><b>这一节要练到</b><span>${esc(l.signature)}</span><small>先理解过程，再处理变式与边界。学习路径：${esc(l.prerequisites?.join('、')||'无，可以直接开始')}</small></div>${(l.teaching||[]).map((t,i)=>`<section class="teaching-section"><h3><span>0${i+1}</span>${esc(t.title)}</h3><p>${esc(t.body)}</p>${i===0?snippet(l.example):''}</section>`).join('')}<div class="cpp-note"><b>C++ → PY</b><span>${esc(l.cpp)}</span></div>${conceptWidget(l)}<h3 class="section-title">例题拆解 <span>预测 → 验证 → 解释</span></h3>${examples.map((e,i)=>`<details class="worked-example" ${i===0?'open':''}><summary><span>例 ${i+1} · ${esc(e.title)}</span><small>展开推演</small></summary><div class="worked-body">${snippet(e.code)}<div class="example-expected"><b>预期输出</b><pre>${esc(e.output)}</pre></div><p>${esc(e.explanation)}</p><button class="button outline" data-run-example="${i}">${icon('play',12)}运行这个示例</button></div></details>`).join('')}<div class="pitfalls"><b>容易踩的坑</b>${l.pitfalls.map(p=>`<p>• ${esc(p)}</p>`).join('')}</div>${lessonResources(l)}<div class="lesson-bottom"><span class="subtle">理解后做两道预测题</span><button class="button primary" data-go-tab="quiz">检验理解 ${icon('arrow',13)}</button></div>`;
 }
 if(currentTab==='quiz')body=`<div class="quiz-progress">本节 ${l.quizzes.filter((_,i)=>state.quiz[quizKey(l,i)]).length} / ${l.quizzes.length} 道已理解 · 答错可重试</div>${l.quizzes.map((q,index)=>{const key=quizKey(l,index),selection=state.answers[key],answered=selection!==undefined,good=selection===q.answer;return `<section class="quiz-card"><span class="mission-number">QUESTION ${String(index+1).padStart(2,'0')}</span>${q.contract?`<details class="contract"><summary>回看这道题的输入输出约定</summary><p>${esc(q.contract)}</p></details>`:''}<p class="quiz-question">${esc(q.question)}</p>${q.code?snippet(q.code):''}${q.options.map((o,i)=>`<button class="quiz-option ${answered&&selection===i?(good?'correct':'wrong'):''}" data-question="${index}" data-choice="${i}"><span class="option-letter">${String.fromCharCode(65+i)}</span><span>${esc(o)}</span></button>`).join('')}${answered?`<div class="quiz-feedback ${good?'correct':''}">${good?'✓ ':'再推一步 · '}${esc(q.why[selection])}</div>`:''}</section>`;}).join('')}<div class="lesson-bottom"><button class="button" data-go-tab="learn">回看讲解</button><button class="button primary" data-go-tab="mission">挑战完整代码题 ${icon('arrow',13)}</button></div>`;
 if(currentTab==='mission')body=`<span class="mission-number">${esc(l.kind)} · ${difficulty[l.level]}</span><div class="mission-body">${esc(l.task)}</div><code class="signature">${esc(l.signature)}</code>${l.bug?`<details class="bug-sample" open><summary>待修复的实现 · 请在右侧独立重写</summary>${snippet(l.bug)}</details>`:''}${l.fixtures?`<details class="fixtures"><summary>练习文件 · 运行时自动创建 ${Object.keys(l.fixtures).length} 个附件</summary>${Object.entries(l.fixtures).map(([name,text])=>`<h4>${esc(name)}</h4><pre>${esc(text)}</pre>`).join('')}</details>`:''}<div class="mini-label">${icon('check',12)} ${l.tests.length} 项验收 · 以下是前两项样例</div>${l.tests.slice(0,2).map(c=>`<div class="example-case"><b>${esc(c.label)}</b><br><span>${esc(c.stdin??c.expr??'标准输出')}</span><br><small>期望：${esc(c.raises?'抛出 '+c.raises:format(c.expected))}</small></div>`).join('')}<p class="mission-tip">提交后会检查本节全部边界、异常或行为约定。先写一个正确版本，再考虑向量化与结构改进。</p>${l.forbiddenCalls?`<div class="pitfalls"><b>本题实现约定</b><p>需要手写核心逻辑，不能直接调用：${esc(l.forbiddenCalls.join('、'))}。</p></div>`:''}${l.runtime==='torch'&&!native?`<div class="bridge-note">真实 PyTorch 代码在本机版运行。<a href="http://127.0.0.1:8766" target="_blank" rel="noopener">打开本机训练台 ↗</a></div>`:''}${lessonResources(l)}<div class="lesson-bottom"><button class="button" data-go-tab="quiz">回看理解测验</button><button class="button primary" id="focus-editor">开始写 ${icon('arrow',13)}</button></div>`;
 $('#lesson-content').innerHTML=body;bindContent();
}
function bindContent(){
 bindContentBase();
 bindLessonLab(lesson().id,$('#lesson-content'));
 document.querySelectorAll('[data-question]').forEach(button=>button.onclick=()=>{const l=lesson(),index=Number(button.dataset.question),answer=Number(button.dataset.choice),key=quizKey(l,index),q=l.quizzes[index];state.answers[key]=answer;state.quizRevisions??={};state.quizRevisions[key]=q.revision??1;if(answer===q.answer&&!state.quiz[key]){state.quiz[key]=true;toast('理解更近一步','+15 XP');}save();render();});
 document.querySelectorAll('[data-run-example]').forEach(button=>button.onclick=()=>runExample(Number(button.dataset.runExample)));
}
async function runExample(index){
 if(busy)return;const l=lesson();activeConsole='result';if(l.runtime==='torch'&&!native){outputs[l.id]={bridge:true};renderConsole();return;}
 busy=true;outputs[l.id]={loading:true,message:'正在运行例题，不会替换你的代码草稿或获得通关记录…'};renderConsole();
 try{const request={lesson:l.id,code:l.examples[index].code,action:'run',stdin:''};const result=native?await fetch('/api/run',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(request),signal:AbortSignal.timeout(30000)}).then(r=>r.json()):await browserRun(request);outputs[l.id]=result;}catch(e){outputs[l.id]={error:{type:'示例运行提示',message:e.message}};}finally{busy=false;render();}
}
function renderConsole(){
 renderConsoleBase();const button=$('#show-solution');if(button){const show=button.onclick;button.onclick=()=>{state.stats??={};state.stats[state.current]??={attempts:0,failures:0};state.stats[state.current].reference=true;save();show();};}
}
let mapFilter={query:'',level:'',kind:'',status:''};
function openMap(){
 $('.modal-overlay')?.remove();document.body.insertAdjacentHTML('beforeend',`<div class="modal-overlay" id="map-overlay"><section class="modal course-modal" role="dialog" aria-modal="true" aria-labelledby="map-title"><div class="map-heading"><div><span class="eyebrow">CURRICULUM / 20–30 HOURS</span><h3 id="map-title">把基础连成一条路</h3><p>72 道编程练习 · 144 道理解测验 · 由实现到排错、挑战和综合实验</p></div><button class="icon-button" id="close-map" aria-label="关闭课程地图">${icon('close',20)}</button></div><div class="map-controls"><input id="map-query" type="search" aria-label="搜索知识点或题目" placeholder="搜索：切片、文件、mask、梯度…"><select id="map-level" aria-label="按难度筛选"><option value="">全部难度</option value="1">基础</option><option value="2">进阶</option><option value="3">挑战</option></select><select id="map-kind" aria-label="按题型筛选"><option value="">全部题型</option>${['实现','排错','挑战','综合'].map(x=>`<option>${x}</option>`).join('')}</select><select id="map-status" aria-label="按进度筛选"><option value="">全部进度</option><option value="unfinished">未完成</option><option value="review">待复习</option><option value="done">已完成</option></select></div><div class="map-summary" id="map-summary"></div><div class="map-results" id="map-results"></div><details class="source-library"><summary>课程依据与延伸阅读 · ${course.sources.length} 份专业资料</summary><p>${esc(course.notes||'讲解与练习为原创，参考资料用于核对知识和延伸学习。')}</p>${course.sources.map(r=>`<a href="${esc(r.url)}" target="_blank" rel="noopener">${esc(r.title)} ↗</a>`).join('')}</details></section></div>`);
 $('#map-query').value=mapFilter.query;for(const key of ['level','kind','status'])$('#map-'+key).value=mapFilter[key];
 $('#map-query').oninput=e=>{mapFilter.query=e.target.value;renderMapResults();};for(const key of ['level','kind','status'])$('#map-'+key).onchange=e=>{mapFilter[key]=e.target.value;renderMapResults();};$('#close-map').onclick=()=>$('#map-overlay').remove();$('#map-overlay').onclick=e=>{if(e.target.id==='map-overlay')e.target.remove();};renderMapResults();$('#map-query').focus();
}
function renderMapResults(){
 const found=lessons.filter(l=>{const hay=[l.title,l.group,l.task,l.signature,l.tag].join(' ').toLowerCase();return(!mapFilter.query||hay.includes(mapFilter.query.toLowerCase()))&&(!mapFilter.level||l.level===Number(mapFilter.level))&&(!mapFilter.kind||l.kind===mapFilter.kind)&&(!mapFilter.status||(mapFilter.status==='done'?state.passed[l.id]:mapFilter.status==='review'?wantsReview(l):!state.passed[l.id]));});
 $('#map-summary').textContent=`找到 ${found.length} 道练习 · 已完成 ${passedCount()} / ${lessons.length} · 可按已掌握程度跳关`;
 $('#map-results').innerHTML=course.chapters.map(ch=>{const items=found.filter(x=>x.chapter===ch.id);if(!items.length)return '';return `<section class="map-chapter"><div class="map-chapter-heading"><h4>${ch.id.slice(1)} · ${esc(ch.title)}</h4><span>约 ${Math.round(ch.minutes/60*10)/10}h · ${items.length} 题</span></div><p>${esc(ch.description)}</p><div class="map-cards">${items.map(l=>`<button class="map-card ${state.passed[l.id]?'complete':''}" data-map-lesson="${l.id}"><div><span class="level-badge level-${l.level}">${difficulty[l.level]}</span><span>${esc(l.kind)} · ${l.minutes}min</span></div><b>${esc(l.title)}</b><small>${state.passed[l.id]?'✓ 已通过':wantsReview(l)?'↻ 建议复习':'○ 尚未通过'} · ${l.tests.length} 项测试</small></button>`).join('')}</div></section>`;}).join('')||'<p class="map-empty">没有找到匹配题目，试着减少筛选条件。</p>';
 document.querySelectorAll('[data-map-lesson]').forEach(b=>b.onclick=()=>{$('#map-overlay').remove();navigate(b.dataset.mapLesson);});
}

function updateSyncStatus(status){
 const button=$('#cloud-progress');
 if(button){button.classList.toggle('has-conflict',status.phase==='conflict');button.setAttribute('aria-label',(status.user?'账号 '+(status.user.name||'学习者')+'，':'')+status.label);const label=button.querySelector('[data-ps-label]');if(label)label.textContent=status.label;}
 const note=$('.bottom-note>span');if(note)note.textContent=status.user?'账号进度保留本机副本 · '+status.label:'访客进度保存在当前浏览器 · 登录后可同步';
}
try{
 const response=await fetch('lessons.json',{cache:'no-store'});if(!response.ok)throw new Error('课程加载失败');lessons=await response.json();
 const revised=syncQuizRevisions(state);save();
 try{course=await fetch('course.json',{cache:'no-store'}).then(r=>r.json());}catch{}
 navExpanded.add(lessons.find(x=>x.id===state.current)?.chapter??lessons[0].chapter);if(!lessons.some(l=>l.id===state.current))state.current='p1';
 progressSync=createProgressSync({getProgress:()=>({...state,version:2}),
  applyProgress:data=>{state=cleanProgress(data);assessmentCenter?.onProgressImported?.();outputs={};hintCount={};currentTab='learn';navExpanded.add(lesson().chapter);render();},
  toast,onStatus:updateSyncStatus});
 render();progressSync.start().catch(error=>toast('云同步暂不可用；本机草稿保留。'+error.message));
 if(revised)toast('预测题已校订，修订题需重答；代码草稿和编程通关记录保留。');connectRuntime();
}catch(error){$('#app').innerHTML=`<div style="padding:50px;font-family:sans-serif"><h1>学习台暂时没有加载成功</h1><p>${esc(error.message)}</p><p>请通过网页地址打开，而不是直接双击 HTML 文件。</p><button onclick="location.reload()">重新加载</button></div>`;}
