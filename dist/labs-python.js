/* Six lesson-specific Python models. No DOM or browser state at import time. */
const esc=value=>String(value).replace(/[&<>"']/g,character=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));
const bool=value=>value?'True':'False';
const pyList=values=>'['+values.map(value=>typeof value==='boolean'?bool(value):String(value)).join(', ')+']';
const pyFloat=value=>Number.isInteger(value)?`${Object.is(value,-0)?0:value}.0`:String(value);
const finiteList=values=>Array.isArray(values)&&values.every(value=>typeof value==='number'&&Number.isFinite(value));

export function assignmentTrace(base,stage=3){
 if(!Number.isInteger(base)||base<0||base>100)throw new RangeError('base must be an integer in 0..100');
 if(!Number.isInteger(stage)||stage<0||stage>3)throw new RangeError('stage must be in 0..3');
 return {base,stage,value:stage===0?null:base+(stage>=2?5:0),stdout:stage===3?String(base+5):''};
}
export function indexTrace(values,index){
 if(!finiteList(values)||!Number.isInteger(index))throw new TypeError('numeric list and integer index required');
 const resolved=index<0?values.length+index:index,ok=resolved>=0&&resolved<values.length;
 return {length:values.length,index,resolved,ok,value:ok?values[resolved]:null,negativeIndex:ok?resolved-values.length:null,error:ok?null:'IndexError'};
}
export function loopTrace(values,steps=0){
 if(!finiteList(values)||!Number.isInteger(steps)||steps<0||steps>values.length)throw new RangeError('invalid loop state');
 return {steps,total:values.length,currentIndex:steps?steps-1:null,completed:steps===values.length,
  outputs:values.slice(0,steps).map(value=>value+5),stdout:values.slice(0,steps).map(value=>value+5).join('\n')};
}
export function meanTrace(values,mode='return'){
 if(!finiteList(values)||!values.length)throw new RangeError('mean requires a nonempty numeric list');
 if(!['return','print'].includes(mode))throw new RangeError('unknown mode');
 const value=values.reduce((total,item)=>total+item,0)/values.length;
 return {value,returned:mode==='return'?value:null,stdout:mode==='return'?`调用结果: ${pyFloat(value)}`:`${pyFloat(value)}\n调用结果: None`};
}
export function parseMeanInput(text){
 const trimmed=String(text).trim();
 if(!trimmed)return {ok:false,error:'本课的 mean 只接受非空列表，请至少填一个整数。'};
 const tokens=trimmed.split(/[,，\s]+/);
 if(tokens.length>8||tokens.some(token=>!/^[-+]?\d+$/.test(token)))return {ok:false,error:'请用逗号或空白分隔 1–8 个整数。'};
 const values=tokens.map(Number);
 if(values.some(value=>!Number.isSafeInteger(value)||value< -100||value>100))return {ok:false,error:'实验输入范围为 -100 到 100 的整数。'};
 return {ok:true,values};
}
export function countGoodTrace(records,threshold){
 if(!Array.isArray(records)||!Number.isFinite(threshold)||records.some(row=>!row||!Number.isFinite(row.loss)))throw new TypeError('finite losses and threshold required');
 const rows=records.map(row=>({model:String(row.model),loss:row.loss,passes:row.loss<threshold,boundary:row.loss===threshold}));
 return {rows,count:rows.filter(row=>row.passes).length,threshold};
}
export function accuracyTrace(preds,labels){
 if(!Array.isArray(preds)||!Array.isArray(labels)||preds.length!==labels.length)throw new RangeError('本课约定 preds 与 labels 等长');
 if([...preds,...labels].some(value=>value!==0&&value!==1))throw new TypeError('binary numbers required');
 const rows=preds.map((pred,index)=>({pred,label:labels[index],correct:pred===labels[index]}));
 const correct=rows.filter(row=>row.correct).length,total=rows.length;
 return {rows,correct,total,accuracy:total?correct/total:0,comparisons:rows.map(row=>bool(row.correct)).join('\n')};
}

export const PYTHON_LAB_META=Object.freeze({
 p1:Object.freeze({widgetId:'lab-p1',topic:'赋值与输出',objective:'逐行执行 score 赋值与加 5，区分旧值、右边计算和标准输出。'}),
 p2:Object.freeze({widgetId:'lab-p2',topic:'列表正负索引',objective:'选择同一列表位置的正负索引，观察长度、最后一项和越界。'}),
 p3:Object.freeze({widgetId:'lab-p3',topic:'for 循环逐项加 5',objective:'逐项执行原题循环，跟踪当前 score 与逐行输出。'}),
 p4:Object.freeze({widgetId:'lab-p4',topic:'mean 函数与返回值',objective:'调整非空数值列表，对照 return 与 print 对函数调用结果的影响。'}),
 p5:Object.freeze({widgetId:'lab-p5',topic:'字典 loss 严格阈值计数',objective:'读取每条字典的 loss，用严格小于筛选，并验证相等边界不计入。'}),
 p6:Object.freeze({widgetId:'lab-p6',topic:'zip 配对与 accuracy',objective:'修改等长预测和标签逐项配对，统计正确数与准确率；双空返回 0.0。'}),
});

const code=source=>`<pre class="plab-code"><code>${esc(source)}</code></pre>`;
const fact=(label,value)=>`<div class="plab-fact"><span>${esc(label)}</span><b>${esc(value)}</b></div>`;
const action=(name,label,extra='')=>`<button type="button" data-plab-action="${esc(name)}" ${extra}>${esc(label)}</button>`;
const output=(text,empty='尚未执行到 print，标准输出仍为空。')=>`<div class="plab-output" aria-live="polite"><span>标准输出</span>${text!==''?`<pre>${esc(text)}</pre>`:`<p>${esc(empty)}</p>`}</div>`;
function frame(id,body){const meta=PYTHON_LAB_META[id];return `<section id="${esc(meta.widgetId)}" class="lesson-lab" data-lab="${esc(id)}" data-python-lab="${esc(id)}" aria-label="${esc(meta.topic)}"><header class="plab-heading"><span>亲手试 · ${esc(id.toUpperCase())}</span><h4>${esc(meta.topic)}</h4></header>${body}</section>`;}
function createLab(id,state,body,handle){
 const bound=new WeakSet();
 const render=()=>frame(id,body(state));
 return Object.freeze({id:PYTHON_LAB_META[id].widgetId,lessonId:id,render,
  bind(root){
   const host=root?.id===PYTHON_LAB_META[id].widgetId?root:root?.querySelector?.('#'+PYTHON_LAB_META[id].widgetId);
   if(!host)return false;
   if(bound.has(host))return true;
   bound.add(host);
   const onEvent=event=>{
    const target=event.target?.closest?.('[data-plab-action], [data-plab-input]');
    if(!target||!host.contains(target))return;
    if(event.type==='click'&&!target.dataset.plabAction)return;
    if(event.type!=='click'&&!target.dataset.plabInput)return;
    if(handle(state,target,event.type,host)){
     const inputName=target.dataset.plabInput;
     const selection=Number.isInteger(target.selectionStart)?target.selectionStart:null;
     host.innerHTML=body(state);
     if(event.type==='input'&&inputName){
      const replacement=host.querySelector?.(`[data-plab-input="${inputName}"]`);
      replacement?.focus?.({preventScroll:true});
      if(selection!==null)try{replacement?.setSelectionRange?.(selection,selection);}catch{}
     }
    }
   };
   host.addEventListener('click',onEvent);host.addEventListener('input',onEvent);host.addEventListener('change',onEvent);
   return true;
  },
 });
}

const p1=createLab('p1',{base:70,stage:0},state=>{
 const trace=assignmentTrace(state.base,state.stage),lines=[`score = ${state.base}`,'score = score + 5','print(score)'];
 return `<p class="plab-note">逐行执行这个实验。初值可调；讲解例题从 70 开始，编程任务从 75 开始，两者使用各自的输入。</p>
 <label class="plab-field" for="lab-p1-base">初始分数 <b>${esc(state.base)}</b><input id="lab-p1-base" data-plab-input="base" type="range" min="0" max="100" step="1" value="${esc(state.base)}"></label>
 <ol class="plab-steps">${lines.map((line,index)=>`<li class="${state.stage===index+1?'is-current':state.stage>index?'is-done':''}"><code>${esc(line)}</code><span>${esc(state.stage>index?'已执行':'待执行')}</span></li>`).join('')}</ol>
 <div class="plab-facts">${fact('score 当前保存的值',trace.value===null?'尚未赋值':trace.value)}${fact('已执行行数',`${state.stage} / 3`)}</div>
 <div class="plab-controls">${action('step',state.stage===3?'三行已完成':'执行下一行',state.stage===3?'disabled':'')}${action('reset','从头执行')}${action('example','例题初值 70')}${action('task','任务初值 75')}</div>
 ${output(trace.stdout)}`;
},(state,target,type)=>{
 if(target.dataset.plabInput==='base'&&type==='input'){state.base=Math.max(0,Math.min(100,Math.round(Number(target.value)||0)));state.stage=0;return true;}
 if(type!=='click')return false;
 if(target.dataset.plabAction==='step')state.stage=Math.min(3,state.stage+1);
 else if(target.dataset.plabAction==='reset')state.stage=0;
 else if(target.dataset.plabAction==='example'){state.base=70;state.stage=0;}
 else if(target.dataset.plabAction==='task'){state.base=75;state.stage=0;}
 else return false;
 return true;
});

const p2=createLab('p2',{index:-1},state=>{
 const values=[60,75,90],trace=indexTrace(values,state.index);
 return `<p class="plab-note">每一列都是同一个元素的两种索引写法。点选正索引或负索引，观察最后一项与越界。</p>
 <div class="plab-index-grid">${values.map((value,index)=>`<div class="plab-index-slot ${trace.ok&&trace.resolved===index?'is-current':''}"><button type="button" data-plab-action="index" data-index="${esc(index)}" aria-label="选择 scores[${esc(index)}]">${esc(index)}</button><b>${esc(value)}</b><button type="button" data-plab-action="index" data-index="${esc(index-values.length)}" aria-label="选择 scores[${esc(index-values.length)}]">${esc(index-values.length)}</button></div>`).join('')}</div>
 <label class="plab-field" for="lab-p2-index">输入索引（整数）<input id="lab-p2-index" type="number" min="-5" max="5" step="1" value="${esc(state.index)}" data-plab-input="index"></label>
 ${code(`scores = [60, 75, 90]\nprint(len(scores))\nprint(scores[${state.index}])`)}
 <div class="plab-facts">${fact('列表长度',trace.length)}${fact('本次索引',state.index)}${fact('访问结果',trace.ok?trace.value:'IndexError')}</div>
 <p class="plab-note ${trace.ok?'':'is-warning'}" aria-live="polite">${esc(trace.ok?`scores[${trace.resolved}] 和 scores[${trace.negativeIndex}] 指向同一项 ${trace.value}。`:'索引越界：合法正索引为 0、1、2，负索引为 -3、-2、-1。长度已先输出，随后索引访问报错。')}</p>
 ${output(trace.ok?`3\n${trace.value}`:'3')}`;
},(state,target,type)=>{
 if(type==='click'&&target.dataset.plabAction==='index'){state.index=Number(target.dataset.index);return true;}
 if(type==='input'&&target.dataset.plabInput==='index'&&/^-?\d+$/.test(target.value)){state.index=Math.max(-5,Math.min(5,Number(target.value)));return true;}
 return false;
});

const p3=createLab('p3',{values:[60,75,90],steps:0},state=>{
 const trace=loopTrace(state.values,state.steps);
 return `<p class="plab-note">这一题遍历每个 score，并逐个输出 score + 5。点一次只执行一个元素，列表本身不会因此被修改。</p>
 ${code(`scores = ${pyList(state.values)}\nfor score in scores:\n    print(score + 5)`)}
 <div class="plab-loop-items">${state.values.map((value,index)=>`<div class="plab-loop-item ${trace.currentIndex===index?'is-current':index<state.steps?'is-done':''}"><span>第 ${esc(index+1)} 项</span><b>${esc(value)}</b><small>${esc(index<state.steps?`+ 5 → ${value+5}`:'等待执行')}</small></div>`).join('')}</div>
 <p class="plab-note" aria-live="polite">${esc(state.steps===0?'循环还未处理任何元素。':trace.completed?'循环已结束，三次 print 的结果各占一行。':`刚处理第 ${state.steps} 项：score=${state.values[state.steps-1]}，本次输出 ${state.values[state.steps-1]+5}。`)}</p>
 <div class="plab-controls">${action('next','执行下一项',trace.completed?'disabled':'')}${action('all','执行完整循环')}${action('reset','重新步进')}${action('original','原题数据')}${action('variant','含零与负数')}</div>
 ${output(trace.stdout,'还没有执行循环体，暂时没有输出。')}`;
},(state,target,type)=>{
 if(type!=='click')return false;
 const name=target.dataset.plabAction;
 if(name==='next')state.steps=Math.min(state.values.length,state.steps+1);
 else if(name==='all')state.steps=state.values.length;
 else if(name==='reset')state.steps=0;
 else if(name==='original'){state.values=[60,75,90];state.steps=0;}
 else if(name==='variant'){state.values=[0,-5,10];state.steps=0;}
 else return false;
 return true;
});

const p4=createLab('p4',{values:[2,4],mode:'return',error:''},state=>{
 const trace=meanTrace(state.values,state.mode),statement=state.mode==='return'?'return':'print';
 const functionLine=statement==='return'?'    return sum(values) / len(values)':'    print(sum(values) / len(values))';
 return `<p class="plab-note">本课的 mean 接受非空数值列表。这里可用 1–8 个整数测试；切换函数体中的 return 与 print，比较调用者拿到的 result。</p>
 <label class="plab-field" for="lab-p4-values">实验列表（整数 -100 到 100，填好后点应用）<input id="lab-p4-values" data-plab-input="values" maxlength="80" value="${esc(state.values.join(', '))}"></label>
 ${state.error?`<p class="plab-note is-warning" role="status">${esc(state.error)}</p>`:''}
 <div class="plab-controls">${action('apply','应用列表')}${action('return','使用 return',`aria-pressed="${esc(state.mode==='return')}"`)}${action('print','误用 print',`aria-pressed="${esc(state.mode==='print')}"`)}${action('sample','用单元素 [7]')}${action('original','恢复 [2, 4]')}</div>
 ${code(`def mean(values):\n${functionLine}\n\nresult = mean(${pyList(state.values)})\nprint("调用结果:", result)`)}
 <div class="plab-facts">${fact('算出的均值',pyFloat(trace.value))}${fact('调用返回给 result',trace.returned===null?'None':pyFloat(trace.returned))}</div>
 <p class="plab-note">${esc(state.mode==='return'?'return 把值交给调用者；这一数值还能参与后续运算。':'print 只把均值显示一次；函数没有 return，所以调用结果是 None。')}</p>
 ${output(trace.stdout)}`;
},(state,target,type,host)=>{
 if(type!=='click')return false;
 if(target.dataset.plabAction==='apply'){
  const parsed=parseMeanInput(host.querySelector('[data-plab-input="values"]')?.value??'');state.error=parsed.ok?'':parsed.error;if(parsed.ok)state.values=parsed.values;return true;
 }
 if(['return','print'].includes(target.dataset.plabAction))state.mode=target.dataset.plabAction;
 else if(target.dataset.plabAction==='sample')state.values=[7];
 else if(target.dataset.plabAction==='original'){state.values=[2,4];state.mode='return';}
 else return false;
 state.error='';return true;
});

const recordsDefault=()=>[{model:'MLP',loss:.25},{model:'CNN',loss:.5},{model:'RNN',loss:.75}];
const p5=createLab('p5',{threshold:50,records:recordsDefault()},state=>{
 const trace=countGoodTrace(state.records,state.threshold/100);
 const recordCode='['+state.records.map(row=>`{"model": "${row.model}", "loss": ${row.loss}}`).join(', ')+']';
 return `<p class="plab-note">每一行是一条实验字典，读取 record["loss"] 再判断。这里使用严格小于 &lt;：loss 恰好等于 threshold 时不计入。</p>
 <label class="plab-field" for="lab-p5-threshold">threshold = <b>${esc(trace.threshold.toFixed(2))}</b><input id="lab-p5-threshold" data-plab-input="threshold" type="range" min="0" max="100" step="5" value="${esc(state.threshold)}"></label>
 <div class="plab-table-wrap"><table class="plab-table"><thead><tr><th>字典的 model</th><th>record["loss"]</th><th>loss &lt; threshold</th></tr></thead><tbody>${trace.rows.map(row=>`<tr class="${row.passes?'is-good':row.boundary?'is-boundary':''}"><td>${esc(row.model)}</td><td>${esc(row.loss.toFixed(2))}</td><td><b>${esc(bool(row.passes))}</b>${row.boundary?'<small>恰好相等，不计入</small>':''}</td></tr>`).join('')||'<tr><td colspan="3">records 是空列表，没有记录可计数。</td></tr>'}</tbody></table></div>
 ${code(`records = ${recordCode}\nthreshold = ${trace.threshold}\ncount = 0\nfor record in records:\n    if record["loss"] < threshold:\n        count += 1\nprint(count)`)}
 <div class="plab-facts">${fact('记录总数',state.records.length)}${fact('严格达标数量',trace.count)}</div>
 <div class="plab-controls">${action('half','阈值 0.50（相等边界）')}${action('empty','空记录列表')}${action('original','恢复三条记录')}</div>
 ${output(String(trace.count))}`;
},(state,target,type)=>{
 if(type==='input'&&target.dataset.plabInput==='threshold'){state.threshold=Math.max(0,Math.min(100,Math.round(Number(target.value)||0)));return true;}
 if(type!=='click')return false;
 if(target.dataset.plabAction==='half')state.threshold=50;
 else if(target.dataset.plabAction==='empty')state.records=[];
 else if(target.dataset.plabAction==='original'){state.records=recordsDefault();state.threshold=50;}
 else return false;
 return true;
});

const p6=createLab('p6',{preds:[1,0,1],labels:[1,1,1]},state=>{
 const trace=accuracyTrace(state.preds,state.labels);
 return `<p class="plab-note">zip 按位置取出一对 pred、label；点任一 0/1 按钮修改这一对中的值。只有 pred == label 的一行才把 correct 加 1。本课约定两个列表等长。</p>
 <div class="plab-pair-lists"><div><b>preds</b><code>${esc(pyList(state.preds))}</code></div><div><b>labels</b><code>${esc(pyList(state.labels))}</code></div></div>
 <div class="plab-table-wrap"><table class="plab-table plab-pairs"><thead><tr><th>第几对</th><th>pred · 可修改</th><th>label · 可修改</th><th>pred == label</th></tr></thead><tbody>${trace.rows.map((row,index)=>`<tr class="${row.correct?'is-good':'is-miss'}"><td>${esc(index+1)}</td><td><button type="button" data-plab-action="toggle" data-field="preds" data-index="${esc(index)}" aria-label="修改第 ${esc(index+1)} 对预测，当前 ${esc(row.pred)}">${esc(row.pred)}</button></td><td><button type="button" data-plab-action="toggle" data-field="labels" data-index="${esc(index)}" aria-label="修改第 ${esc(index+1)} 对标签，当前 ${esc(row.label)}">${esc(row.label)}</button></td><td><b>${esc(bool(row.correct))}</b></td></tr>`).join('')||'<tr><td colspan="4">zip([], []) 没有任何一对，循环体执行 0 次。</td></tr>'}</tbody></table></div>
 <div class="plab-facts">${fact('correct · 正确数',trace.correct)}${fact('total · 样本数',trace.total)}${fact('accuracy',pyFloat(trace.accuracy))}</div>
 <p class="plab-note" aria-live="polite">${esc(trace.total?`accuracy = ${trace.correct} / ${trace.total} = ${pyFloat(trace.accuracy)}；不是只取最后一对的结果。`:'两个列表都为空，按本课契约直接返回 0.0，不进行 0/0 除法。')}</p>
 ${code(`def accuracy(preds, labels):\n    if not labels:\n        return 0.0\n    correct = 0\n    for pred, label in zip(preds, labels):\n        if pred == label:\n            correct += 1\n    return correct / len(labels)\n\npreds = ${pyList(state.preds)}\nlabels = ${pyList(state.labels)}\nprint(accuracy(preds, labels))`)}
 <div class="plab-controls">${action('perfect','改成全部正确')}${action('wrong','改成全部错误')}${action('empty','两个列表都为空')}${action('add','增加一对',trace.total>=6?'disabled':'')}${action('reset','恢复课内示例')}</div>
 ${output(pyFloat(trace.accuracy))}`;
},(state,target,type)=>{
 if(type!=='click')return false;
 const name=target.dataset.plabAction;
 if(name==='toggle'){
  const field=target.dataset.field,index=Number(target.dataset.index);
  if(!['preds','labels'].includes(field)||!Number.isInteger(index)||index<0||index>=state[field].length)return false;
  state[field][index]=1-state[field][index];
 }else if(name==='perfect')state.preds=state.labels.slice();
 else if(name==='wrong')state.preds=state.labels.map(value=>1-value);
 else if(name==='empty'){state.preds=[];state.labels=[];}
 else if(name==='add'&&state.preds.length<6){state.preds.push(0);state.labels.push(1);}
 else if(name==='reset'){state.preds=[1,0,1];state.labels=[1,1,1];}
 else return false;
 return true;
});

export const pythonLabs=Object.freeze({p1,p2,p3,p4,p5,p6});
export const renderPythonLab=id=>Object.hasOwn(pythonLabs,id)?pythonLabs[id].render():'';
export const bindPythonLab=(id,root)=>Object.hasOwn(pythonLabs,id)?pythonLabs[id].bind(root):false;
