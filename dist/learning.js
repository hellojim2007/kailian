// Learning UI is independent of the full-task editor and completion history.
const esc = v => String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const code = value => `<pre class="guide-code"><code>${esc(value)}</code></pre>`;
export const normalOutput = value => String(value??'').replace(/\r\n?/g,'\n').trim();
export function checkWarmupResult(result, expected){
 return Boolean(result?.ok&&!result.error&&normalOutput(result.stdout)===normalOutput(expected));
}
export function warmupMismatchHint(lesson,result){
 const actual=normalOutput(result?.stdout),expected=normalOutput(lesson.guide.warmup.expected);
 if(!actual)return '没有标准输出。若你定义了函数，还需要在函数外调用它并print返回值。';
 if(lesson.id==='py06'&&actual.toLowerCase()===expected)return '分词和标点处理已正确，差别在大小写。split不会转小写：先lowered=text.lower()，再对lowered调用split()，最后返回列表。';
 return '对照上方用法卡片，逐步检查中间变量、返回值与输出格式。热身需要完整程序；可先运行最小例子，再改成题目给的数据。';
}
export function cleanWarmups(raw, ids){
 const out={};if(!raw||typeof raw!=='object')return out;
 for(const id of ids){const row=Object.hasOwn(raw,id)?raw[id]:null;if(!row||typeof row!=='object')continue;
  out[id]={draft:typeof row.draft==='string'?row.draft.slice(0,12000):'',passed:row.passed===true,viewed:row.viewed===true};
 }return out;
}
export function routeNext(current, route, allLessons){
 const ids=route?.lessonIds||allLessons.map(l=>l.id),position=ids.indexOf(current);
 return allLessons.find(l=>l.id===ids[position+1]);
}
export function renderTaskContract(lesson){
 return `<div class="guide-contract"><b>正式任务 · 完整接口与边界</b>${(lesson.guide?.contract||[lesson.task]).map(text=>`<p>${esc(text)}</p>`).join('')}</div>`;
}
export function routeOverview(course,lessons,passed={}){
 const route=course.studyRoute;if(!route)return '';
 const byId=new Map(lessons.map(l=>[l.id,l])),next=route.lessonIds.find(id=>!passed[id]);
 return `<section class="guide-route-overview"><div><span class="guide-eyebrow">先学会，再组合</span><h3>推荐路线 · 53 节入门主线 → 19 节进阶回访</h3><p>${esc(route.note)}</p><p>${esc(route.budget)}</p></div>${next?`<button class="button primary" data-guide-lesson="${esc(next)}">接着推荐路线 · ${esc(byId.get(next)?.title)}</button>`:''}<div class="guide-phases">${route.phases.map(phase=>`<details><summary>${esc(phase.title)} · ${phase.lessonIds.filter(id=>passed[id]).length}/${phase.lessonIds.length}</summary><p>${esc(phase.description)}</p><ol>${phase.lessonIds.map(id=>`<li><button data-guide-lesson="${id}" class="guide-link">${passed[id]?'✓ ':''}${esc(byId.get(id)?.title)}</button></li>`).join('')}</ol></details>`).join('')}</div></section>`;
}
export function renderLearningGuide(l,{lessons,warmup={}}){
 const g=l.guide;if(!g)return '';
 const names=new Map(lessons.map(x=>[x.id,x.title]));
 return `<aside class="guide-position"><span class="guide-tag ${g.track==='extension'?'extension':''}">${g.track==='core'?'入门主线':'进阶回访'} · 路线第 ${g.position} 步</span><p>最终要独立实现：<code>${esc(l.signature)}</code></p><p>${esc(g.reason)}</p>${g.requires.length?`<div class="guide-prerequisites">需要先会：${g.requires.map(id=>`<button class="guide-link" data-guide-lesson="${id}">${esc(names.get(id))}</button>`).join(' · ')}</div>`:'<p>从这里开始，不需要先会 Python 语法。</p>'}<small>左侧编号按主题归档；“继续推荐路线”会按先修顺序前进。</small></aside>
 <section class="guide-section"><div class="guide-section-title"><span>01</span><h3>把语法和用法讲清楚</h3></div><p>先读写法、输入与返回值，再运行小例子。标为“复习”的卡片可以展开查用。</p>${g.cards.map((card,index)=>`<details class="syntax-card" ${card.newHere?'open':''}><summary><strong>${esc(card.title)}</strong><span>${card.newHere?'本节新用法':'复习用法'}</span></summary><div class="syntax-body">${code(card.syntax)}<p>${esc(card.body)}</p><div class="guide-example-label">最小完整例子</div>${code(card.code)}<div class="guide-output"><b>这段代码的输出</b><pre>${esc(card.output)}</pre></div><button class="button outline" data-guide-run="${index}">运行这个语法例子</button><pre class="guide-run-result" data-guide-result="${index}" aria-live="polite" hidden></pre><a href="${esc(card.source)}" target="_blank" rel="noopener">核对这个用法 ↗</a></div></details>`).join('')}</section>
 ${g.trace?`<section class="guide-section"><h3>逐步跟踪：值和类型怎样变化</h3>${g.trace.map(t=>`<div class="guide-trace">${code(t.statement)}<p><b>${esc(t.kind)}</b> → <code>${esc(t.value)}</code></p><p>${esc(t.explanation)}</p></div>`).join('')}</section>`:''}
 <section class="guide-section guide-warmup" id="guide-warmup"><div class="guide-section-title"><span>02</span><h3>先自己写一小段</h3></div><p>${esc(g.warmup.prompt)}</p><details><summary>目标标准输出</summary><pre>${esc(g.warmup.expected)}</pre></details><label for="warmup-editor">热身代码 · 与右侧正式作业分开保存</label><textarea id="warmup-editor" class="warmup-editor" maxlength="12000" spellcheck="false" autocapitalize="off" autocomplete="off" aria-label="热身代码">${esc(warmup.draft||'')}</textarea><div class="warmup-actions"><button class="button primary" data-warmup-run>运行并检查输出</button><button class="button outline" data-warmup-solution>看热身参考</button></div><div class="warmup-feedback" aria-live="polite" id="warmup-feedback">${warmup.passed?'上次热身样例已通过；完整掌握还要看右侧任务和后续考核。':'先尝试独立写；有错可以根据输出和报错修改。'}</div><div id="warmup-solution" hidden>${code(g.warmup.code)}<p>看过参考后的通过用于练习反馈，不计为首次独立完成。热身只检查这组输出，不会替代正式判题。</p></div></section>
 <section class="guide-section"><div class="guide-section-title"><span>03</span><h3>把这些用法组合起来</h3></div><ol class="guide-steps">${g.steps.map(step=>`<li>${esc(step)}</li>`).join('')}</ol>${renderTaskContract(l)}<p class="guide-handover">接下来读完整例题，先预测再运行；最后在右侧实现正式任务。每题需要的辅助函数请一并写在代码里。热身通过不自动计入正式通关。</p></section>`;
}
export function bindLearningGuide(root,{lesson,getWarmup,saveWarmup,runCode,navigate,onError}){
 if(!root)return;
 root.querySelectorAll('[data-guide-lesson]').forEach(b=>b.onclick=()=>navigate(b.dataset.guideLesson));
 const textarea=root.querySelector('#warmup-editor');
 if(textarea)textarea.oninput=()=>saveWarmup({...getWarmup(),draft:textarea.value,passed:false});
 const button=root.querySelector('[data-warmup-run]');
 if(textarea)textarea.onkeydown=event=>{
  if(event.key==='Tab'){event.preventDefault();textarea.setRangeText('    ',textarea.selectionStart,textarea.selectionEnd,'end');textarea.dispatchEvent(new Event('input'));}
  if(event.key==='Enter'&&!event.ctrlKey&&!event.metaKey){event.preventDefault();const line=textarea.value.slice(0,textarea.selectionStart).split('\n').at(-1),indent=(line.match(/^\s*/)?.[0]||'')+(line.trimEnd().endsWith(':')?'    ':'');textarea.setRangeText('\n'+indent,textarea.selectionStart,textarea.selectionEnd,'end');textarea.dispatchEvent(new Event('input'));}
  if(event.key==='Enter'&&(event.ctrlKey||event.metaKey)){event.preventDefault();if(!button.disabled)button.click();}
 };
 if(button)button.onclick=async()=>{
  const output=root.querySelector('#warmup-feedback'),draft=textarea.value;
  if(!draft.trim()){output.textContent='先写一段完整代码，再检查输出。';return;}
  const row=getWarmup();saveWarmup({...row,draft});button.disabled=true;output.textContent='正在实际运行代码…';
  try{const result=await runCode(draft),passed=checkWarmupResult(result,lesson.guide.warmup.expected);
   // The owner callback ignores results after account changes; this view need not repaint.
   const latest=getWarmup();
   if(latest.draft!==draft){output.textContent='这次运行的是修改前的代码；新草稿已保留，请再次运行检查。';return;}
   saveWarmup({...latest,draft,passed});
   output.textContent=result.error?`${result.error.type||'执行错误'}${result.error.line?' · 第 '+result.error.line+' 行':''}：${result.error.message}\n${result.error.guide||''}`:passed?'这组热身输出正确。现在尝试正式任务和其他输入。':`输出还不一致。\n期望：\n${lesson.guide.warmup.expected}\n实际：\n${result.stdout||'（没有输出）'}\n${warmupMismatchHint(lesson,result)}`;
   output.classList.toggle('passed',passed);
  }catch(error){output.textContent=error.message;onError?.(error);}finally{button.disabled=false;}
 };
 const solution=root.querySelector('[data-warmup-solution]');if(solution)solution.onclick=()=>{
  root.querySelector('#warmup-solution').hidden=false;saveWarmup({...getWarmup(),viewed:true});
 };
 root.querySelectorAll('[data-guide-run]').forEach(b=>b.onclick=async()=>{
  const index=Number(b.dataset.guideRun),output=root.querySelector(`[data-guide-result="${index}"]`);b.disabled=true;output.hidden=false;output.textContent='正在实际运行…';
  try{const result=await runCode(lesson.guide.cards[index].code);output.textContent=result.error?`${result.error.type}：${result.error.message}`:result.stdout||'（没有输出）';}catch(error){output.textContent=error.message;}finally{b.disabled=false;}
 });
}
