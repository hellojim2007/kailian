/* Separate assessment records: practice progress is never overwritten here. */
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const LIMIT=24000;
const CODE_LIMIT=16000;
const reserved=new Set(['__proto__','constructor','prototype']);
const text=(value,max=LIMIT)=>typeof value==='string'?value.slice(0,max):'';
const number=(value,min=0,max=1e9)=>typeof value==='number'&&Number.isFinite(value)?Math.min(max,Math.max(min,value)):min;
const validId=value=>typeof value==='string'&&!reserved.has(value)&&/^[a-zA-Z0-9_.:-]{1,100}$/.test(value);
const date=value=>{
 if(typeof value!=='string'||value.length>40||!/^\d{4}-\d\d-\d\dT/.test(value)||!Number.isFinite(Date.parse(value)))return null;
 const year=Number(value.slice(0,4)),month=Number(value.slice(5,7)),day=Number(value.slice(8,10));
 if(month<1||month>12||day<1||day>new Date(Date.UTC(year,month,0)).getUTCDate())return null;
 return new Date(value).toISOString();
};
const enumValue=(value,list,fallback)=>list.includes(value)?value:fallback;
const idList=value=>Array.isArray(value)?[...new Set(value.filter(validId))].slice(0,160):[];
const DAY=86400000;
const modeLabel={independent:'首次作答',retest:'同卷重测',correction:'订正',review:'间隔复习'};
const aidLabel={independent:'独立完成',docs:'查官方文档',ai:'AI 辅助'};
const kindLabel={chapter:'章末小测',cumulative:'累计测验',stage:'阶段考核'};
const answerKindLabel={choice:'概念辨析',output:'输出预测',code:'完整代码'};
const confidenceLabel={sure:'有把握',unsure:'不确定',guess:'猜的'};
const formatValue=value=>typeof value==='string'?value:JSON.stringify(value,null,2)??'';
const stamp=()=>new Date().toISOString();
const uid=()=>`attempt-${Date.now().toString(36)}-${Math.random().toString(36).slice(2,9)}`;

function cleanAnswers(raw){
 const out={};if(!raw||typeof raw!=='object')return out;
 for(const [id,a] of Object.entries(raw).slice(0,160)){
  if(!validId(id)||!a||typeof a!=='object')continue;
  const value={confidence:enumValue(a.confidence,['sure','unsure','guess'],'unsure')};
  if(Number.isInteger(a.choice)&&a.choice>=0&&a.choice<40)value.choice=a.choice;
  for(const key of ['output','code','stdin'])if(typeof a[key]==='string')value[key]=text(a[key],key==='stdin'?4000:key==='code'?CODE_LIMIT:LIMIT);
  out[id]=value;
 }return out;
}
function cleanError(raw){if(!raw)return undefined;return typeof raw==='string'?{message:text(raw,1600)}:{type:text(raw.type,100),message:text(raw.message,1600),line:Number.isInteger(raw.line)?number(raw.line,1,100000):undefined};}
function cleanChecks(raw){
 if(!Array.isArray(raw))return [];
 return raw.slice(0,80).map(c=>({passed:c?.passed===true,label:text(c?.label,180),input:text(formatValue(c?.input),5000),actual:text(formatValue(c?.actual),5000),expected:text(formatValue(c?.expected),5000),error:cleanError(c?.error),feedback:text(c?.feedback,1800)}));
}
function cleanResults(raw){
 const out={};if(!raw||typeof raw!=='object')return out;
 for(const [id,r]of Object.entries(raw).slice(0,160)){
  if(!validId(id)||!r||typeof r!=='object')continue;
  const maxPoints=number(r.maxPoints,0,10000);
  const points=number(r.points,0,maxPoints);
  out[id]={points,maxPoints,passed:maxPoints>0&&points===maxPoints,checks:cleanChecks(r.checks),error:cleanError(r.error),actual:text(r.actual),expected:text(r.expected),stdout:text(r.stdout)};
 }return out;
}

/** Safe for a progress import; does not access DOM, storage, or course data. */
export function cleanAssessmentProgress(raw){
 const clean={version:1,drafts:{},attempts:[]};if(!raw||typeof raw!=='object')return clean;
 const cleanBase=(r,id)=>{
  if(!r||typeof r!=='object'||!validId(id)||!validId(r.examId)||!date(r.startedAt))return null;
  const row={id,examId:r.examId,mode:enumValue(r.mode,['independent','retest','correction','review'],'independent'),startedAt:date(r.startedAt),updatedAt:date(r.updatedAt)||date(r.startedAt),elapsedMs:number(r.elapsedMs,0,60*DAY),assistance:enumValue(r.assistance,['independent','docs','ai'],'independent'),answers:cleanAnswers(r.answers),itemIds:idList(r.itemIds)};
  if(validId(r.parentId))row.parentId=r.parentId;
  if([1,3,7].includes(r.reviewStep))row.reviewStep=r.reviewStep;
  return row;
 };
 if(raw.drafts&&typeof raw.drafts==='object')for(const [id,r]of Object.entries(raw.drafts).slice(0,80)){const row=cleanBase(r,id);if(row)clean.drafts[id]=row;}
 const seenAttemptIds=new Set();
 if(Array.isArray(raw.attempts))for(const r of raw.attempts.slice(0,500)){
  const row=cleanBase(r,r?.id);if(!row||!date(r.submittedAt)||Date.parse(r.submittedAt)<Date.parse(row.startedAt))continue;
  if(seenAttemptIds.has(row.id))continue;seenAttemptIds.add(row.id);
  row.submittedAt=date(r.submittedAt);row.durationMs=number(r.durationMs,0,60*DAY);row.results=cleanResults(r.results);
  row.maxScore=Object.values(row.results).reduce((n,x)=>n+x.maxPoints,0);row.score=Object.values(row.results).reduce((n,x)=>n+x.points,0);row.percent=row.maxScore?row.score/row.maxScore*100:0;
  row.skills={};if(r.skills&&typeof r.skills==='object')for(const [skill,result]of Object.entries(r.skills).slice(0,100)){if(reserved.has(skill)||skill.length>160)continue;const maxPoints=number(result?.maxPoints,0,1e6);row.skills[skill]={points:number(result?.points,0,maxPoints),maxPoints};}
  row.seenBefore=idList(r.seenBefore);row.retentionEvidence=r.retentionEvidence===true&&row.assistance==='independent'&&row.mode==='review';
  row.delayEvidence=r.delayEvidence===true&&row.assistance==='independent'&&row.mode==='review';
  if(row.seenBefore.length)row.delayEvidence=false;
  clean.attempts.push(row);
 }
 clean.attempts.sort((a,b)=>Date.parse(a.submittedAt)-Date.parse(b.submittedAt));
 const seenExams=new Set(),previous=[];
 for(const row of clean.attempts){
  Object.assign(row,getAssessmentEvidence(row,previous,Date.parse(row.submittedAt)));
  if(row.mode!=='review')seenExams.add(row.examId);
  previous.push(row);delete clean.drafts[row.id];
 }
 for(const row of Object.values(clean.drafts)){if(row.mode==='independent'&&seenExams.has(row.examId))row.mode='retest';}
 return clean;
}

/** Recomputed from immutable history, rather than trusting imported flags. */
export function getAssessmentEvidence(row,previousAttempts=[],now=Date.now()){
 const prior=previousAttempts.filter(a=>a.id!==row.id&&Number.isFinite(Date.parse(a.submittedAt))&&Date.parse(a.submittedAt)<=now);
 const mode=row.mode==='independent'&&prior.some(a=>a.examId===row.examId&&a.mode!=='review')?'retest':row.mode;
 const priorItems=new Set(prior.flatMap(a=>a.itemIds||[]));
 const seenBefore=idList(row.itemIds).filter(id=>priorItems.has(id));
 const last=prior.length?Math.max(...prior.map(a=>Date.parse(a.submittedAt))):null;
 const retentionEvidence=mode==='review'&&row.assistance==='independent'&&last!==null&&now-last>=DAY;
 return {mode,seenBefore,retentionEvidence,delayEvidence:retentionEvidence&&idList(row.itemIds).length>0&&seenBefore.length===0};
}

/** Whole-paper scoring; code gets the proportion of checks it passes. */
export function scoreAssessment(items,answers={},codeResults={}){
 const results={},skills={};let score=0,maxScore=0;
 for(const item of items){
  if(!validId(item.id))continue;
  const a=answers[item.id]||{},maxPoints=number(item.points,0,10000);let fraction=0;
  const result={points:0,maxPoints,passed:false};
  if(item.kind==='choice'){fraction=a.choice===item.answer?1:0;result.actual=Number.isInteger(a.choice)?item.options?.[a.choice]??'未作答':'未作答';result.expected=item.options?.[item.answer]??'';}
  else if(item.kind==='output'){result.actual=text(a.output);result.expected=text(item.expectedStdout);fraction=result.actual.replaceAll('\r\n','\n').trim()===result.expected.replaceAll('\r\n','\n').trim()?1:0;}
  else if(item.kind==='code'){
   const execution=codeResults[item.id]||{tests:[],error:{type:'未作答',message:'没有提交代码。'}};
   result.checks=cleanChecks(execution.tests);result.error=cleanError(execution.error);result.stdout=text(execution.stdout);
   fraction=result.checks.length?result.checks.filter(c=>c.passed).length/result.checks.length:0;
  }
  result.points=maxPoints*fraction;result.passed=fraction===1;results[item.id]=result;score+=result.points;maxScore+=maxPoints;
  for(const skill of Array.isArray(item.skills)?item.skills:[]){if(typeof skill!=='string'||reserved.has(skill))continue;skills[skill]??={points:0,maxPoints:0};skills[skill].points+=result.points;skills[skill].maxPoints+=maxPoints;}
 }return {results,score,maxScore,percent:maxScore?score/maxScore*100:0,skills};
}

export function getReviewSchedule(progress,reviewDays=[1,3,7],now=Date.now()){
 const attempts=progress?.attempts||[];
 const first=attempts.filter(a=>a.mode==='independent').sort((a,b)=>Date.parse(a.submittedAt)-Date.parse(b.submittedAt))[0];
 if(!first)return [];
  return reviewDays.map(day=>{const dueAt=new Date(Date.parse(first.submittedAt)+day*DAY).toISOString();const done=attempts.some(a=>a.mode==='review'&&a.reviewStep===day&&Date.parse(a.submittedAt)>=Date.parse(dueAt)&&(a.retentionEvidence||a.delayEvidence));return {day,dueAt,done,due:now>=Date.parse(dueAt)};});
}

/** Review uses a separate pool. Weak, confident mistakes are selected first. */
export function selectReviewItems(data,progress,{now=Date.now(),limit=4,learnedChapters=[]}={}){
 const pool=new Set(data.reviewItems||[]),items=(data.items||[]).filter(i=>pool.has(i.id));
 const learned=new Set(learnedChapters),exams=new Map((data.exams||[]).map(e=>[e.id,e]));
 for(const a of progress?.attempts||[])for(const ch of exams.get(a.examId)?.chapters||[])learned.add(ch);
 const skillWeakness=new Map(),chapterWeakness=new Map();
 for(const a of progress?.attempts||[])for(const [id,result]of Object.entries(a.results||{})){
  const item=data.items.find(i=>i.id===id);if(!item)continue;
  const wrong=result.maxPoints?1-result.points/result.maxPoints:0,boost=a.answers?.[id]?.confidence==='sure'?2:1;
  chapterWeakness.set(item.chapter,Math.max(chapterWeakness.get(item.chapter)||0,wrong*boost));
  for(const skill of item.skills||[])skillWeakness.set(skill,Math.max(skillWeakness.get(skill)||0,wrong*boost));
 }
 const relevant=learned.size?items.filter(i=>learned.has(i.chapter)):items;
 return relevant.map((item,index)=>{
  const seen=(progress?.attempts||[]).flatMap(a=>a.itemIds?.includes(item.id)?[Date.parse(a.submittedAt)]:[]),last=seen.length?Math.max(...seen):0;
  const weak=Math.max(chapterWeakness.get(item.chapter)||0,...(item.skills||[]).map(s=>skillWeakness.get(s)||0));
  return {item,index,rank:weak*10+(last?Math.min(8,(now-last)/DAY):9)};
 }).sort((a,b)=>b.rank-a.rank||a.index-b.index).slice(0,limit).map(x=>x.item.id);
}

export async function createAssessmentCenter({getProgress,saveProgress,runCode,getRuntime,toast=()=>{}}){
 const response=await fetch('exams.json');if(!response.ok)throw new Error('暂时无法读取考核题库，请刷新后重试。');
 const data=await response.json(),itemMap=new Map(data.items.map(i=>[i.id,i])),examMap=new Map(data.exams.map(e=>[e.id,e])),exerciseMap=new Map(data.exercises.map(e=>[e.id,e]));
 getProgress().assessments=cleanAssessmentProgress(getProgress().assessments);
 let lessons=[];try{const r=await fetch('lessons.json');if(r.ok)lessons=await r.json();}catch{}
 let overlay=null,view={kind:'overview'},returnFocus=null,timer=null,lastTick=0,busyId=null,notice='',submitConfirm=false;
 const runOutputs=new Map(),runBusy=new Set();
 function progress(){const state=getProgress();if(!state.assessments||state.assessments.version!==1)state.assessments=cleanAssessmentProgress(state.assessments);return state.assessments;}
 function persist(){saveProgress();}
 function chapterName(ch){return `${Number(ch?.slice(1))||'?'} 章`;}
 function shortDate(value){return new Date(value).toLocaleString('zh-CN',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit',hour12:false});}
 function learnedChapters(){const p=getProgress();return [...new Set([...lessons.filter(l=>p.passed?.[l.id]||p.quiz?.[l.id]).map(l=>l.chapter),...Object.entries(data.chapterLessons||{}).filter(([,ids])=>ids.some(id=>p.passed?.[id]||p.quiz?.[id])).map(([ch])=>ch)])];}
 function skillTitle(skill){return data.skillTitles?.[skill]||skill;}
 function tick(){if(!overlay||view.kind!=='attempt')return;const draft=progress().drafts[view.id];if(!draft)return;const now=Date.now();draft.elapsedMs+=Math.max(0,now-lastTick);lastTick=now;const el=overlay.querySelector('[data-clock]');if(el)el.textContent=clock(draft.elapsedMs);draft.updatedAt=stamp();persist();}
 function clock(ms){return `${Math.floor(ms/60000)}:${String(Math.floor(ms/1000)%60).padStart(2,'0')}`;}
 function close(){tick();if(timer)clearInterval(timer);timer=null;overlay?.remove();overlay=null;document.body.classList.remove('assessment-open');returnFocus?.focus?.();}
 function open(){if(overlay){overlay.focus();return;}returnFocus=document.activeElement;overlay=document.createElement('section');overlay.className='ac-overlay';overlay.setAttribute('role','dialog');overlay.setAttribute('aria-modal','true');overlay.setAttribute('aria-label','考核与间隔复习');overlay.tabIndex=-1;document.body.append(overlay);document.body.classList.add('assessment-open');lastTick=Date.now();timer=setInterval(tick,5000);render();overlay.focus();}
 function go(next){tick();view=next;notice='';submitConfirm=false;lastTick=Date.now();render();overlay?.querySelector('h1,h2')?.focus();}
 function shell(content){return `<header class="ac-top"><a class="ac-brand" href="#" data-action="overview"><span>&gt;_</span>开练<span class="ac-subbrand">考核中心</span></a><button class="ac-btn ac-quiet" data-action="close" aria-label="关闭考核中心，回到课程">返回课程 <span aria-hidden="true">×</span></button></header><main class="ac-main">${content}</main>`;}
 function render(){if(!overlay)return;const focusKey=document.activeElement?.dataset?.focus;overlay.innerHTML=shell(view.kind==='attempt'?renderAttempt():view.kind==='result'?renderResult():renderOverview());bind();if(focusKey)overlay.querySelector(`[data-focus="${CSS.escape(focusKey)}"]`)?.focus();}
 function renderOverview(){
  const p=progress(),attempts=p.attempts,formal=attempts.filter(a=>['independent','retest'].includes(a.mode)),firstByExam=new Map();for(const a of formal.filter(a=>a.mode==='independent'&&a.assistance==='independent'))if(!firstByExam.has(a.examId))firstByExam.set(a.examId,a);
  const avg=firstByExam.size?[...firstByExam.values()].reduce((sum,a)=>sum+a.percent,0)/firstByExam.size:null,schedule=getReviewSchedule(p,data.policy.reviewDays),next=schedule.find(s=>!s.done),learned=learnedChapters();
  return `<section class="ac-hero"><div><span class="ac-eyebrow">KNOW IT · WRITE IT · RETAIN IT</span><h1 tabindex="-1">用一次独立作答，检验学到哪里。</h1><p>在原有 20–30 小时训练之外，另用约 4–6 小时检验、订正与复习。章末、累计、阶段考核各自保留首考成绩与辅助记录；同卷重测、订正另记。</p></div><div class="ac-hero-mark" aria-hidden="true">∑<small>LEARNING EVIDENCE</small></div></section><div class="ac-metrics"><div><b>${firstByExam.size}<small> / ${data.exams.length}</small></b><span>已完成独立试卷</span></div><div><b>${avg===null?'—':Math.round(avg)+'%'}</b><span>首次独立均分</span></div><div><b>${Object.keys(p.drafts).length}</b><span>自动保存的草稿</span></div><div><b>${attempts.filter(a=>a.delayEvidence).length}</b><span>间隔 ≥24h 的独立新题复测</span></div></div>
  <section class="ac-review-banner"><div><span class="ac-eyebrow">SPACED REVIEW</span><h2>换一道题，过一段时间再试。</h2><p>每次最多 4 题，从独立复习池中优先选择薄弱点与高信心答错的知识点。${next?`下个设计复习日：<b>${esc(shortDate(next.dueAt))}</b>（第 ${next.day} 天${next.due?'，现在可复习':''}）。`:formal.length?'1 / 3 / 7 天复习已完成，仍可自由复习。':'首次正式测验后，安排第 1 / 3 / 7 天复习；现在也可自由试做。'}</p></div><button class="ac-btn ac-primary" data-action="review">${next?.due?'开始到期复习':'开始自由复习'} →</button><small>日期是本课程的练习安排，不是通用遗忘曲线常数。可提前做；间隔不足 24 小时不会记作延迟复测证据。</small></section>
  ${Object.values(p.drafts).length?`<section class="ac-section"><div class="ac-section-heading"><h2>接着上次写</h2><span>草稿不会因关闭页面丢失</span></div><div class="ac-draft-list">${Object.values(p.drafts).sort((a,b)=>Date.parse(b.updatedAt)-Date.parse(a.updatedAt)).map(d=>`<div class="ac-draft"><div><b>${esc(examMap.get(d.examId)?.title||'短时复习')}</b><span>${esc(modeLabel[d.mode])} · ${clock(d.elapsedMs)} · ${esc(shortDate(d.updatedAt))}</span></div><button class="ac-btn ac-soft" data-action="resume" data-id="${esc(d.id)}">恢复草稿</button></div>`).join('')}</div></section>`:''}
  ${['chapter','cumulative','stage'].map(kind=>`<section class="ac-section"><div class="ac-section-heading"><h2>${kind==='chapter'?'01':kind==='cumulative'?'02':'03'} · ${kindLabel[kind]}</h2><span>${kind==='chapter'?'刚学完，核对基础':kind==='cumulative'?'跨章节选择方法':'从概念走到完整实现'}</span></div><div class="ac-exam-grid">${data.exams.filter(e=>e.kind===kind).map(e=>{
   const rows=formal.filter(a=>a.examId===e.id),first=rows[0],draft=Object.values(p.drafts).find(d=>d.examId===e.id&&['independent','retest'].includes(d.mode)),items=e.itemIds.map(id=>itemMap.get(id)).filter(Boolean),covered=e.chapters.filter(ch=>learned.includes(ch)),required=[...new Set(e.chapters.flatMap(ch=>data.chapterLessons?.[ch]||lessons.filter(l=>l.chapter===ch).map(l=>l.id)))],prepared=required.filter(id=>getProgress().passed?.[id]).length;
   return `<article class="ac-exam"><div class="ac-card-meta"><span>${esc(kindLabel[e.kind])}</span><span>${e.minutes} MIN · ${items.length} 题</span></div><h3>${esc(e.title)}</h3><p>${esc(e.description)}</p><div class="ac-coverage">${e.chapters.map(ch=>`<span class="${learned.includes(ch)?'learned':''}">${esc(chapterName(ch))}</span>`).join('')}</div><small>建议先学：${esc(e.chapters.map(chapterName).join('、'))} · 已完成先修练习 ${prepared}/${required.length} 项（可直接开考）</small><div class="ac-card-score">${first?`<strong>${Math.round(first.percent)}<small>%</small></strong><span>首考 · ${esc(aidLabel[first.assistance])}<br>${rows.filter(r=>r.mode==='retest').length} 次同卷重测</span>`:'<span>尚无首次成绩<br>不锁关，按自己的掌握程度选择</span>'}</div><div class="ac-card-actions"><button class="ac-btn ${draft?'ac-soft':'ac-primary'}" data-action="${draft?'resume':'start'}" data-id="${esc(draft?.id||e.id)}">${draft?'恢复草稿':first?'同卷重测':'开始小测'}</button>${first?`<button class="ac-btn ac-quiet" data-action="result" data-id="${esc(rows.at(-1).id)}">看记录</button>`:''}</div></article>`;
  }).join('')}</div></section>`).join('')}
  <section class="ac-section"><div class="ac-section-heading"><h2>每次作答都有自己的位置</h2><span>首考 · 同卷重测 · 订正 · 复习分别记录</span></div>${attempts.length?`<div class="ac-history">${[...attempts].reverse().map(a=>`<button class="ac-history-row" data-action="result" data-id="${esc(a.id)}"><span><b>${esc(examMap.get(a.examId)?.title||'短时复习')}</b><small>${esc(shortDate(a.submittedAt))} · ${esc(modeLabel[a.mode])} · ${esc(aidLabel[a.assistance])}${a.delayEvidence?' · 延迟复测':''}</small></span><strong>${Math.round(a.percent)}%</strong><span aria-hidden="true">↗</span></button>`).join('')}</div>`:'<div class="ac-empty">现在还没有成绩。先完成一份小测，再决定下一步练什么。</div>'}</section><p class="ac-footnote">${esc(data.policy.note)} · 建议达标线 ${data.policy.suggestedPassPercent}% 仅用于发现待练内容，不等同于研究或实习能力认证。进度随课程一起导出 / 导入。</p>`;
 }
 function newAttempt(examId,mode='independent',parentId){
  const p=progress(),exam=examMap.get(examId),parent=p.attempts.find(a=>a.id===parentId);let itemIds=parent?.itemIds||exam?.itemIds||[];
  if(mode==='independent'&&p.attempts.some(a=>a.examId===examId&&a.mode!=='review'))mode='retest';
  if(mode==='review')itemIds=selectReviewItems(data,p,{learnedChapters:learnedChapters()});
  if(!itemIds.length){toast('还没有可用的复习题，请先完成一章练习。');return;}
  const now=stamp(),id=uid(),draft={id,examId:mode==='review'?'review-pool':examId,mode,startedAt:now,updatedAt:now,elapsedMs:0,assistance:mode==='correction'?(parent?.assistance||'independent'):'independent',answers:parent?JSON.parse(JSON.stringify(parent.answers)):{},itemIds:[...itemIds]};
  if(parentId)draft.parentId=parentId;
  if(mode==='review'){const next=getReviewSchedule(p,data.policy.reviewDays).find(s=>!s.done);if(next?.due)draft.reviewStep=next.day;}
  p.drafts[id]=draft;persist();go({kind:'attempt',id});
 }
 function currentItems(row){return row.itemIds.map(id=>itemMap.get(id)).filter(Boolean);}
 function renderAttempt(){
  const draft=progress().drafts[view.id];if(!draft){view={kind:'overview'};return renderOverview();}
  const exam=examMap.get(draft.examId),items=currentItems(draft),answered=items.filter(i=>i.kind==='choice'?Number.isInteger(draft.answers[i.id]?.choice):Boolean((draft.answers[i.id]?.[i.kind==='code'?'code':'output']||'').trim())).length;
  return `<div class="ac-attempt-head"><div><button class="ac-link" data-action="overview">← 考核总览 · 草稿自动保存</button><div class="ac-badges"><span>${esc(modeLabel[draft.mode])}</span>${draft.mode==='correction'?'<span class="ac-warning">不会覆盖原考试成绩</span>':''}</div><h1 tabindex="-1">${esc(exam?.title||'短时复习 · 换题检查')}</h1><p>${draft.mode==='correction'?'根据上一份结果重新写一遍；本次记录标为订正。':draft.mode==='retest'?'本卷题目已经作答并展示过解析。本次从空白开始，记录为同卷重测，不作为未见题的首次独立证据。':'提交整卷之前不显示正确答案、解析或完整判题结果。可查阅资料，请如实记录辅助方式。'}</p></div><div class="ac-clock"><b data-clock>${clock(draft.elapsedMs)}</b><span>建议 ${exam?.minutes||12} 分钟 · 不强制交卷</span></div></div>
  <div class="ac-attempt-layout"><aside class="ac-attempt-nav"><div class="ac-nav-head"><b>${answered} / ${items.length} 题已写</b><small>答案自动保存</small></div><div class="ac-question-dots">${items.map((i,n)=>`<button class="${draft.answers[i.id]?'touched':''}" data-action="jump" data-id="${esc(i.id)}" aria-label="跳到第 ${n+1} 题">${n+1}</button>`).join('')}</div><fieldset class="ac-aid"><legend>本卷使用的辅助方式</legend>${Object.entries(aidLabel).map(([value,label])=>`<label><input type="radio" name="assistance" value="${value}" ${draft.assistance===value?'checked':''}>${label}</label>`).join('')}<small>用于解释成绩，不扣分。用过 AI 或文档请选择对应项。</small></fieldset><p class="ac-nav-note">${draft.mode==='review'?'复习题来自独立题池。见过的题会在结果中注明，重复做不代表新题迁移。':'所有选择、输出和代码一并交卷；运行代码只查看标准输出与报错。'}</p><button class="ac-btn ac-primary" data-action="submit" ${busyId?'disabled':''}>${busyId===draft.id?'正在集中判分…':'交整卷，查看分析'}</button></aside><div class="ac-questions">${notice?`<div class="ac-notice" role="status">${esc(notice)}</div>`:''}${items.map((item,index)=>renderQuestion(item,index,draft)).join('')}<section class="ac-submit-card"><h2>准备好了，再看答案。</h2><p>已写 ${answered}/${items.length} 题。空题按未作答计分；环境连接失败会保留草稿，让你重试。</p>${submitConfirm?`<div class="ac-confirm" role="alert"><p>确认交卷？交卷后显示答案，本次记录将被保存。</p><div><button class="ac-btn ac-primary" data-action="confirm-submit" ${busyId?'disabled':''}>确认交卷</button><button class="ac-btn ac-quiet" data-action="cancel-submit">继续检查</button></div></div>`:`<button class="ac-btn ac-primary" data-action="submit" ${busyId?'disabled':''}>${busyId===draft.id?'正在集中判分…':'交整卷，查看分析'}</button>`}</section></div></div>`;
 }
 function renderQuestion(item,index,draft){
  const a=draft.answers[item.id]||{},exercise=exerciseMap.get(item.exerciseId),torchBlocked=item.runtime==='torch'&&!getRuntime().native,output=runOutputs.get(`${draft.id}:${item.id}`);
  return `<article class="ac-question" id="ac-q-${esc(item.id)}"><div class="ac-question-meta"><span>QUESTION ${String(index+1).padStart(2,'0')} · ${esc(answerKindLabel[item.kind])}</span><span>${item.points} 分 · ${esc(chapterName(item.chapter))}</span></div><h2>${esc(item.prompt)}</h2><div class="ac-skill-tags">${(item.skills||[]).map(s=>`<span>${esc(skillTitle(s))}</span>`).join('')}</div>${item.code?`<pre class="ac-code-block">${esc(item.code)}</pre>`:''}
  ${item.kind==='choice'?`<div class="ac-options">${item.options.map((option,n)=>`<label class="ac-option ${a.choice===n?'selected':''}"><input type="radio" name="answer-${esc(item.id)}" data-item="${esc(item.id)}" data-field="choice" data-focus="choice-${esc(item.id)}-${n}" value="${n}" ${a.choice===n?'checked':''}><span>${String.fromCharCode(65+n)}</span><pre>${esc(option)}</pre></label>`).join('')}</div>`:item.kind==='output'?`<label class="ac-field-label" for="ac-output-${esc(item.id)}">预测标准输出（保留换行；末尾空白不影响判分）</label><textarea id="ac-output-${esc(item.id)}" class="ac-output-editor" data-item="${esc(item.id)}" data-field="output" data-focus="output-${esc(item.id)}" rows="3" spellcheck="false" placeholder="先推演，再写出每一行输出…">${esc(a.output||'')}</textarea>`:`<div class="ac-code-task">${exercise?.task&&exercise.task!==item.prompt?`<p>${esc(exercise.task)}</p>`:''}<code>${esc(item.signature||exercise?.signature)}</code></div>${sampleMarkup(exercise)}<label class="ac-field-label" for="ac-code-${esc(item.id)}">${esc(item.runtime==='torch'?'Python · PyTorch':'Python')} · 完整实现</label><textarea id="ac-code-${esc(item.id)}" class="ac-editor" maxlength="16000" data-item="${esc(item.id)}" data-field="code" data-focus="code-${esc(item.id)}" rows="10" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" placeholder="# 在这里独立写完整实现…">${esc(a.code||'')}</textarea>${exercise?.tests?.some(t=>Object.hasOwn(t,'stdin'))?`<label class="ac-field-label" for="ac-stdin-${esc(item.id)}">运行用标准输入</label><textarea class="ac-output-editor" id="ac-stdin-${esc(item.id)}" data-item="${esc(item.id)}" data-field="stdin" data-focus="stdin-${esc(item.id)}" rows="2" spellcheck="false">${esc(a.stdin??exercise.tests[0]?.stdin??'')}</textarea>`:''}${torchBlocked?'<p class="ac-bridge">本题需要真实 PyTorch。草稿已保留；请在 <a href="http://127.0.0.1:8766/" target="_blank" rel="noopener">本机学习台 ↗</a> 继续，并用导出 / 导入携带考核进度。</p>':''}<div class="ac-run-row"><button class="ac-btn ac-soft" data-action="run" data-id="${esc(item.id)}" ${runBusy.has(item.id)||busyId?'disabled':''}>${runBusy.has(item.id)?'正在运行…':'▷ 运行代码'}</button><small>只运行代码，不提前判整题 · Tab 缩进</small></div><div class="ac-run-output" id="ac-run-${esc(item.id)}" aria-live="polite">${renderRunOutput(output)}</div>`}
  <fieldset class="ac-confidence"><legend>提交这个答案时，我的信心是</legend>${Object.entries(confidenceLabel).map(([value,label])=>`<label><input type="radio" name="confidence-${esc(item.id)}" data-item="${esc(item.id)}" data-field="confidence" value="${value}" ${(a.confidence||'unsure')===value?'checked':''}>${label}</label>`).join('')}</fieldset></article>`;
 }
 function sampleMarkup(exercise){if(!exercise)return '';const sample=exercise.tests?.[0];return `${sample?`<details class="ac-sample"><summary>查看一个公开样例</summary>${sample.setup?`<b>样例准备</b><pre>${esc(sample.setup)}</pre>`:''}<b>${sample.stdin!==undefined?'输入':'调用 / 检查'}</b><pre>${esc(sample.stdin??sample.expr??'运行程序')}</pre><b>期望</b><pre>${esc(sample.raises?'抛出 '+sample.raises:formatValue(sample.expected))}</pre></details>`:''}${exercise.fixtures?`<details class="ac-sample"><summary>本题附件（运行时自动创建）</summary>${Object.entries(exercise.fixtures).map(([name,content])=>`<b>${esc(name)}</b><pre>${esc(content)}</pre>`).join('')}</details>`:''}`;}
 function renderRunOutput(result){if(!result)return '';if(result.environment)return `<p class="ac-error">${esc(result.environment)}</p>`;return `${result.stdout?`<b>标准输出</b><pre>${esc(result.stdout)}</pre>`:!result.error?'<p>运行完成，没有标准输出。函数题可自行补调用与 print 检查。</p>':''}${result.error?`<p class="ac-error">${esc(result.error.type)}${result.error.line?` · 第 ${Number(result.error.line)} 行`:''}</p><pre>${esc(result.error.message)}</pre>`:''}`;}
 function renderResult(){
  const p=progress(),record=p.attempts.find(a=>a.id===view.id);if(!record){view={kind:'overview'};return renderOverview();}const exam=examMap.get(record.examId),items=currentItems(record),first=p.attempts.find(a=>a.examId===record.examId&&['independent','retest'].includes(a.mode)),weak=Object.entries(record.skills||{}).sort((a,b)=>(a[1].points/a[1].maxPoints)-(b[1].points/b[1].maxPoints)),seen=items.filter(i=>p.attempts.some(a=>a.id!==record.id&&Date.parse(a.submittedAt)<Date.parse(record.submittedAt)&&a.itemIds.includes(i.id)));
  return `<button class="ac-link" data-action="overview">← 回到考核总览</button><section class="ac-result-hero"><div><span class="ac-eyebrow">${esc(modeLabel[record.mode])} · ${esc(aidLabel[record.assistance])}</span><h1 tabindex="-1">${esc(exam?.title||'短时复习')} · 本次结果</h1><p>${esc(shortDate(record.submittedAt))} · 用时 ${clock(record.durationMs)}${record.mode==='correction'?' · 订正成绩，原考试记录保留':''}</p><div class="ac-result-evidence">${record.mode==='review'?(record.delayEvidence?`独立作答，距此前相关作答至少 24 小时。${seen.length?'其中 '+seen.length+' 题已见过：这是同题保持的证据，不是新题迁移。':'本轮使用此前未见的复习题。'}`:record.retentionEvidence?'本轮独立且间隔至少 24 小时，但包含已见题；记为间隔独立复现，不记作未见题的迁移证据。':'本轮属于提前、辅助或间隔不足的复习，不记作新的延迟掌握证据。'):record.mode==='retest'?'本卷题目和解析已经见过。本次是从空白同卷重测，不是未见题，也不会增加首次独立或新题迁移证据。':'本次只说明这份题目中的表现；之后用独立复习题检查保持与迁移。'}</div></div><div class="ac-score"><b>${Math.round(record.percent)}<small>%</small></b><span>${Number(record.score.toFixed(2))} / ${record.maxScore} 分</span><strong>${record.percent>=data.policy.suggestedPassPercent?'达到本次建议线':'先练弱项，再独立复测'}</strong></div></section>
  ${first&&first.id!==record.id?`<div class="ac-first-note">首考记录仍为 <b>${Math.round(first.percent)}%</b>（${esc(shortDate(first.submittedAt))} · ${esc(aidLabel[first.assistance])}）。本次成绩单独保存。</div>`:''}<section class="ac-section"><div class="ac-section-heading"><h2>按技能看，下一步练什么</h2><span>同一题可覆盖多个技能</span></div><div class="ac-skill-grid">${weak.map(([skill,s])=>{const ratio=s.maxPoints?s.points/s.maxPoints:0;return `<div class="ac-skill ${ratio<.8?'weak':''}"><b>${esc(skillTitle(skill))}</b><span>${Math.round(ratio*100)}%</span><div><i style="width:${number(ratio*100,0,100)}%"></i></div><small>${ratio<.8?'建议先重写对应题，再用复习题检验':'本卷通过，之后检查延迟保持'}</small></div>`;}).join('')}</div></section><div class="ac-result-actions"><button class="ac-btn ac-primary" data-action="correct" data-id="${esc(record.id)}">订正本卷 →</button><button class="ac-btn ac-soft" data-action="review">换题复习</button>${exam?`<button class="ac-btn ac-quiet" data-action="start" data-id="${esc(exam.id)}">从空白同卷重测</button>`:''}</div><section class="ac-section"><div class="ac-section-heading"><h2>逐题复盘</h2><span>先解释失败原因，再展开参考解</span></div>${items.map((item,index)=>renderResultItem(item,index,record)).join('')}</section>`;
 }
 function renderResultItem(item,index,record){
  const r=record.results[item.id]||{points:0,maxPoints:item.points,passed:false},a=record.answers[item.id]||{},exercise=exerciseMap.get(item.exerciseId),highWrong=a.confidence==='sure'&&!r.passed;
  return `<article class="ac-question ac-result-question ${r.passed?'passed':'needs-work'}"><div class="ac-question-meta"><span>${r.passed?'✓':'↻'} QUESTION ${String(index+1).padStart(2,'0')} · ${esc(answerKindLabel[item.kind])}</span><span>${Number(r.points.toFixed(2))} / ${r.maxPoints} 分</span></div><h2>${esc(item.prompt)}</h2><p class="ac-confidence-result">作答信心：${esc(confidenceLabel[a.confidence]||'不确定')}${highWrong?' · 高信心答错，优先进入复习选择':''}</p>${item.code?`<pre class="ac-code-block">${esc(item.code)}</pre>`:''}${item.kind==='code'?`<details class="ac-sample"><summary>查看当时提交的代码</summary><pre>${esc(a.code||'未作答')}</pre></details>`:`<div class="ac-answer-compare"><div><b>你的答案</b><pre>${esc(r.actual||'（空输出）')}</pre></div><div><b>正确答案</b><pre>${esc(r.expected)}</pre></div></div>`}<div class="ac-explanation"><b>为什么</b><p>${esc(item.explanation)}</p></div>${r.error?`<div class="ac-notice"><b>${esc(r.error.type)}</b><p>${esc(r.error.message)}</p></div>`:''}${r.checks?.length?`<div class="ac-checks">${r.checks.map(check=>`<details class="ac-check ${check.passed?'passed':'failed'}" ${!check.passed?'open':''}><summary>${check.passed?'✓':'×'} ${esc(check.label||'测试检查')}</summary><div><b>输入 / 调用</b><pre>${esc(check.input)}</pre><b>期望</b><pre>${esc(check.expected)}</pre><b>实际</b><pre>${esc(check.error?`${check.error.type||''}: ${check.error.message}`:check.actual)}</pre>${check.feedback?`<p>${esc(check.feedback)}</p>`:''}</div></details>`).join('')}</div>`:''}${item.kind==='code'&&exercise?.solution?`<details class="ac-reference"><summary>我已分析过自己的代码，展开参考实现</summary><p>参考实现只是可行写法之一。关上它，再从空白重写。</p><pre>${esc(exercise.solution)}</pre></details>`:''}</article>`;
 }
 function bind(){
  overlay.onclick=async event=>{
   const button=event.target.closest('[data-action]');if(!button||!overlay.contains(button))return;event.preventDefault();const action=button.dataset.action,id=button.dataset.id;
   if(action==='close')close();else if(action==='overview')go({kind:'overview'});else if(action==='start')newAttempt(id);else if(action==='resume')go({kind:'attempt',id});else if(action==='result')go({kind:'result',id});else if(action==='correct'){const r=progress().attempts.find(a=>a.id===id);if(r)newAttempt(r.examId,'correction',r.id);}else if(action==='review')newAttempt('review-pool','review');else if(action==='jump')overlay.querySelector(`#ac-q-${CSS.escape(id)}`)?.scrollIntoView({behavior:'smooth',block:'start'});else if(action==='run')await runItem(id);else if(action==='submit'){tick();submitConfirm=true;render();overlay.querySelector('.ac-confirm')?.scrollIntoView({behavior:'smooth',block:'center'});overlay.querySelector('[data-action="confirm-submit"]')?.focus();}else if(action==='cancel-submit'){submitConfirm=false;render();}else if(action==='confirm-submit')await submit();
  };
  overlay.oninput=event=>{
   const el=event.target,draft=progress().drafts[view.id];if(view.kind!=='attempt'||!draft||busyId===draft.id)return;
   if(el.name==='assistance'){draft.assistance=enumValue(el.value,['independent','docs','ai'],'independent');draft.updatedAt=stamp();persist();return;}
   const id=el.dataset.item,field=el.dataset.field;if(!id||!field)return;draft.answers[id]??={confidence:'unsure'};
   draft.answers[id][field]=field==='choice'?Number(el.value):text(el.value,field==='stdin'?4000:field==='code'?CODE_LIMIT:LIMIT);draft.updatedAt=stamp();persist();
   if(field==='choice'){el.closest('.ac-options')?.querySelectorAll('.ac-option').forEach(label=>label.classList.toggle('selected',label.contains(el)));}
   const items=currentItems(draft),count=items.filter(i=>i.kind==='choice'?Number.isInteger(draft.answers[i.id]?.choice):Boolean((draft.answers[i.id]?.[i.kind==='code'?'code':'output']||'').trim())).length;
   const counter=overlay.querySelector('.ac-nav-head b');if(counter)counter.textContent=`${count} / ${items.length} 题已写`;
   const submitCount=overlay.querySelector('.ac-submit-card>p');if(submitCount)submitCount.textContent=`已写 ${count}/${items.length} 题。空题按未作答计分；环境连接失败会保留草稿，让你重试。`;
   overlay.querySelectorAll('.ac-question-dots [data-action="jump"]').forEach(dot=>dot.classList.toggle('touched',Boolean(draft.answers[dot.dataset.id])));
  };
  overlay.onkeydown=event=>{
   if(event.key==='Escape'){event.preventDefault();close();return;}
   const el=event.target;
   if(el.matches?.('.ac-editor')&&event.key==='Tab'){
    event.preventDefault();const start=el.selectionStart,end=el.selectionEnd,value=el.value,lineStart=value.lastIndexOf('\n',start-1)+1;
    if(start===end&&!event.shiftKey){el.setRangeText('    ',start,end,'end');}
    else{const endLine=value.indexOf('\n',end),stop=endLine<0?value.length:endLine,part=value.slice(lineStart,stop),changed=part.split('\n').map(line=>event.shiftKey?line.replace(/^ {1,4}/,''):'    '+line).join('\n');el.setRangeText(changed,lineStart,stop,'select');}
    el.dispatchEvent(new Event('input',{bubbles:true}));return;
   }
   if(el.matches?.('.ac-editor')&&event.key==='Enter'&&!event.ctrlKey&&!event.metaKey){event.preventDefault();const start=el.selectionStart,line=el.value.slice(el.value.lastIndexOf('\n',start-1)+1,start),spaces=line.match(/^ */)?.[0]||'',extra=line.trimEnd().endsWith(':')?'    ':'';el.setRangeText('\n'+spaces+extra,start,el.selectionEnd,'end');el.dispatchEvent(new Event('input',{bubbles:true}));return;}
   if(event.key==='Tab'){
    const focusables=[...overlay.querySelectorAll('button:not(:disabled),a[href],input:not(:disabled),textarea:not(:disabled),summary,[tabindex="0"]')].filter(n=>n.getClientRects().length),first=focusables[0],last=focusables.at(-1);
    if(event.shiftKey&&document.activeElement===first){event.preventDefault();last?.focus();}else if(!event.shiftKey&&document.activeElement===last){event.preventDefault();first?.focus();}
   }
  };
 }
 async function runItem(id){
  const draft=progress().drafts[view.id],item=itemMap.get(id);if(!draft||!item||runBusy.has(id)||busyId)return;
  const key=`${draft.id}:${id}`,runtime=getRuntime();if(item.runtime==='torch'&&!runtime.native){runOutputs.set(key,{environment:'需要本机真实 PyTorch。草稿已保留，请在本机版继续。'});render();return;}
  if(!runtime.ready){runOutputs.set(key,{environment:'运行环境尚未就绪。草稿已保留，稍后重试。'});render();return;}
  const a=draft.answers[id]||{},exercise=exerciseMap.get(item.exerciseId);runBusy.add(id);render();
  try{const result=await runCode({lesson:item.exerciseId,code:a.code||'',action:'run',stdin:a.stdin??exercise?.tests?.[0]?.stdin??''});runOutputs.set(key,result);}catch(error){runOutputs.set(key,{environment:`连接未完成：${error.message}。草稿保留，可重试。`});}
  finally{runBusy.delete(id);if(overlay)render();}
 }
 function infraFailure(result){return !result||(!Array.isArray(result.tests)&&!result.error)||(/环境|连接|服务|fetch|network/i.test(result.error?.type||''))||(result.error?.type==='ModuleNotFoundError'&&/torch/.test(result.error.message||''));}
 async function submit(){
  const p=progress(),draft=p.drafts[view.id];if(!draft||busyId)return;
  if(runBusy.size){notice='一段代码仍在运行，等它结束后即可交卷。草稿继续保存。';submitConfirm=false;render();return;}
  tick();const items=currentItems(draft),codeItems=items.filter(i=>i.kind==='code'&&(draft.answers[i.id]?.code||'').trim());
  if(codeItems.some(i=>i.runtime==='torch')&&!getRuntime().native){notice='本卷有 PyTorch 代码需要在本机版判分。所有答案与草稿已保留；请用导出 / 导入携带进度。';submitConfirm=false;render();return;}
  if(codeItems.length&&!getRuntime().ready){notice='运行环境尚未就绪，尚未交卷或记错题。草稿已保留，请连接后重试。';submitConfirm=false;render();return;}
  const snapshot=JSON.parse(JSON.stringify(draft)),codeResults={};busyId=draft.id;notice='正在逐题运行代码并集中判分，请稍候。';submitConfirm=false;render();overlay?.querySelectorAll('textarea,input').forEach(el=>el.disabled=true);
  try{
   for(const item of codeItems){
    const result=await runCode({lesson:item.exerciseId,code:snapshot.answers[item.id]?.code||'',action:'submit',stdin:snapshot.answers[item.id]?.stdin||''});
    if(infraFailure(result))throw new Error(result?.error?.message||'运行服务未返回完整判题结果');codeResults[item.id]=result;
   }
   if(getProgress().assessments!==p){toast('学习进度已经导入或重置，旧考核的提交结果未写入新进度。');return;}
   const graded=scoreAssessment(items,snapshot.answers,codeResults),now=stamp();
   const record={...snapshot,...graded,...getAssessmentEvidence(snapshot,p.attempts,Date.parse(now)),submittedAt:now,updatedAt:now,durationMs:snapshot.elapsedMs};
   p.attempts.push(record);delete p.drafts[draft.id];persist();notice='';if(overlay)go({kind:'result',id:record.id});toast('本卷已交，首考、重测与订正会分别保留。');
  }catch(error){if(getProgress().assessments!==p){toast('学习进度已经导入或重置，旧考核的提交结果未写入新进度。');return;}notice=`这次未交卷、未记错题：${error.message}。全部草稿保留，请检查运行环境后重试。`;if(overlay&&view.id===draft.id)render();toast('运行未完成，草稿已保留。');}
  finally{busyId=null;if(overlay)render();}
 }
 function onProgressImported(){if(overlay){view={kind:'overview'};notice='';render();}if(busyId)toast('新进度已保留，旧考核的判分结果将被取消。');}
 return {open,onProgressImported};
}
