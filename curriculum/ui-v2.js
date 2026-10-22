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
function conceptWidget(l){
 if(!/^[pt]\d$/.test(l.id))return '';
 return `<div class="mini-label">${icon('spark',12)} 可操作的直觉实验</div>${widget(l.visual)}`;
}
function renderContent(){
 const l=lesson(),examples=l.examples||[];let body='';
 if(currentTab==='learn'){
  body=`<div class="learning-goals"><b>这一节要练到</b><span>${esc(l.signature)}</span><small>先理解过程，再处理变式与边界。前置：${esc(l.prerequisites?.join('、')||'无，可以直接开始')}</small></div>${(l.teaching||[]).map((t,i)=>`<section class="teaching-section"><h3><span>0${i+1}</span>${esc(t.title)}</h3><p>${esc(t.body)}</p>${i===0?snippet(l.example):''}</section>`).join('')}<div class="cpp-note"><b>C++ → PY</b><span>${esc(l.cpp)}</span></div>${conceptWidget(l)}<h3 class="section-title">例题拆解 <span>预测 → 验证 → 解释</span></h3>${examples.map((e,i)=>`<details class="worked-example" ${i===0?'open':''}><summary><span>例 ${i+1} · ${esc(e.title)}</span><small>展开推演</small></summary><div class="worked-body">${snippet(e.code)}<div class="example-expected"><b>预期输出</b><pre>${esc(e.output)}</pre></div><p>${esc(e.explanation)}</p><button class="button outline" data-run-example="${i}">${icon('play',12)}运行这个示例</button></div></details>`).join('')}<div class="pitfalls"><b>容易踩的坑</b>${l.pitfalls.map(p=>`<p>• ${esc(p)}</p>`).join('')}</div>${lessonResources(l)}<div class="lesson-bottom"><span class="subtle">理解后做两道预测题</span><button class="button primary" data-go-tab="quiz">检验理解 ${icon('arrow',13)}</button></div>`;
 }
 if(currentTab==='quiz')body=`<div class="quiz-progress">本节 ${l.quizzes.filter((_,i)=>state.quiz[quizKey(l,i)]).length} / ${l.quizzes.length} 道已理解 · 答错可重试</div>${l.quizzes.map((q,index)=>{const key=quizKey(l,index),selection=state.answers[key],answered=selection!==undefined,good=selection===q.answer;return `<section class="quiz-card"><span class="mission-number">QUESTION ${String(index+1).padStart(2,'0')}</span>${q.contract?`<details class="contract"><summary>回看这道题的输入输出约定</summary><p>${esc(q.contract)}</p></details>`:''}<p class="quiz-question">${esc(q.question)}</p>${q.code?snippet(q.code):''}${q.options.map((o,i)=>`<button class="quiz-option ${answered&&selection===i?(good?'correct':'wrong'):''}" data-question="${index}" data-choice="${i}"><span class="option-letter">${String.fromCharCode(65+i)}</span><span>${esc(o)}</span></button>`).join('')}${answered?`<div class="quiz-feedback ${good?'correct':''}">${good?'✓ ':'再推一步 · '}${esc(q.why[selection])}</div>`:''}</section>`;}).join('')}<div class="lesson-bottom"><button class="button" data-go-tab="learn">回看讲解</button><button class="button primary" data-go-tab="mission">挑战完整代码题 ${icon('arrow',13)}</button></div>`;
 if(currentTab==='mission')body=`<span class="mission-number">${esc(l.kind)} · ${difficulty[l.level]}</span><div class="mission-body">${esc(l.task)}</div><code class="signature">${esc(l.signature)}</code>${l.bug?`<details class="bug-sample" open><summary>待修复的实现 · 请在右侧独立重写</summary>${snippet(l.bug)}</details>`:''}${l.fixtures?`<details class="fixtures"><summary>练习文件 · 运行时自动创建 ${Object.keys(l.fixtures).length} 个附件</summary>${Object.entries(l.fixtures).map(([name,text])=>`<h4>${esc(name)}</h4><pre>${esc(text)}</pre>`).join('')}</details>`:''}<div class="mini-label">${icon('check',12)} ${l.tests.length} 项验收 · 以下是前两项样例</div>${l.tests.slice(0,2).map(c=>`<div class="example-case"><b>${esc(c.label)}</b><br><span>${esc(c.stdin??c.expr??'标准输出')}</span><br><small>期望：${esc(c.raises?'抛出 '+c.raises:format(c.expected))}</small></div>`).join('')}<p class="mission-tip">提交后会检查本节全部边界、异常或行为约定。先写一个正确版本，再考虑向量化与结构改进。</p>${l.forbiddenCalls?`<div class="pitfalls"><b>本题实现约定</b><p>需要手写核心逻辑，不能直接调用：${esc(l.forbiddenCalls.join('、'))}。</p></div>`:''}${l.runtime==='torch'&&!native?`<div class="bridge-note">真实 PyTorch 代码在本机版运行。<a href="http://127.0.0.1:8766" target="_blank" rel="noopener">打开本机训练台 ↗</a></div>`:''}${lessonResources(l)}<div class="lesson-bottom"><button class="button" data-go-tab="quiz">回看理解测验</button><button class="button primary" id="focus-editor">开始写 ${icon('arrow',13)}</button></div>`;
 $('#lesson-content').innerHTML=body;bindContent();
}
function bindContent(){
 bindContentBase();
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
