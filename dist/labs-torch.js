// Lesson-specific numerical illustrations. Actual Python/Torch execution stays
// in the code runner; these deliberately use transparent JavaScript formulas.
const finite = (value, label = 'value') => {
  if (typeof value !== 'number' || !Number.isFinite(value)) throw new TypeError(`${label} must be finite`);
  return value;
};
const integer = (value, min, max, label) => {
  finite(value, label);
  if (!Number.isInteger(value) || value < min || value > max) throw new RangeError(`${label} is out of range`);
  return value;
};
const escape = value => String(value).replace(/[&<>"']/g, character => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[character]));

export function formatNumber(value) {
  finite(value);
  if (Math.abs(value) < 1e-12) return value === 0 ? '0' : value.toExponential(3);
  if (Math.abs(value) < 1e-5 || Math.abs(value) >= 1e7) return value.toExponential(3);
  return String(Number(value.toFixed(6)));
}

function matrixShape(matrix) {
  if (!Array.isArray(matrix) || !matrix.length || !Array.isArray(matrix[0]) || !matrix[0].length) throw new RangeError('matrix must have nonempty rows and columns');
  const width = matrix[0].length;
  for (const row of matrix) {
    if (!Array.isArray(row) || row.length !== width) throw new RangeError('matrix must be rectangular');
    for (const value of row) finite(value);
  }
  return [matrix.length, width];
}

export function matrixMeans(matrix, dim = 1, keepdim = false) {
  const [rows, columns] = matrixShape(matrix);
  if (dim !== 0 && dim !== 1) throw new RangeError('dim must be 0 or 1');
  const values = dim === 1
    ? matrix.map(row => row.reduce((sum, value) => sum + value, 0) / columns)
    : Array.from({length: columns}, (_, column) => matrix.reduce((sum, row) => sum + row[column], 0) / rows);
  const data = keepdim ? (dim === 1 ? values.map(value => [value]) : [values]) : values;
  return {values, data, shape: keepdim ? (dim === 1 ? [rows, 1] : [1, columns]) : [values.length]};
}

export function centerRows(matrix, keepdim = true) {
  const [rows, columns] = matrixShape(matrix);
  const means = matrixMeans(matrix, 1, keepdim);
  // Without keepdim, a [B] result aligns with the last D axis. B=1 may
  // broadcast, B=D silently changes the meaning, and other B/D pairs fail.
  if (!keepdim && rows !== columns && rows !== 1 && columns !== 1) {
    return {ok:false, inputShape:[rows,columns], meanShape:means.shape, outputShape:null, means:means.values, output:null};
  }
  if (!keepdim && columns === 1 && rows > 1) {
    return {ok:true, inputShape:[rows,columns], meanShape:means.shape, outputShape:[rows,rows], means:means.values,
      output:matrix.map(row => means.values.map(mean => row[0]-mean))};
  }
  const output = matrix.map((row, rowIndex) => row.map((value, columnIndex) => value - (keepdim ? means.values[rowIndex] : means.values[rows === 1 ? 0 : columnIndex])));
  return {ok:true, inputShape:[rows,columns], meanShape:means.shape, outputShape:[rows,columns], means:means.values, output};
}

export function functionAndGradient(x, kind = 'quadratic-linear') {
  finite(x, 'x');
  if (kind === 'square') return {x, kind, value:x*x, gradient:2*x, formula:'y = x²', derivative:'dy/dx = 2x'};
  if (kind === 'quadratic-linear') return {x, kind, value:x*x+3*x, gradient:2*x+3, formula:'y = x² + 3x', derivative:'dy/dx = 2x + 3'};
  throw new RangeError('unknown function');
}

export const LINEAR_WEIGHT = Object.freeze([Object.freeze([1,0,-1]),Object.freeze([0,0.5,1])]);
export const LINEAR_BIAS = Object.freeze([0.5,-1]);

export function linearDemo(batch) {
  integer(batch, 1, 100, 'batch');
  const input = Array.from({length:batch}, (_, row) => [row+1,row+2,row+3]);
  const output = input.map(row => LINEAR_WEIGHT.map((weights, index) => row.reduce((sum,value,column) => sum+value*weights[column], LINEAR_BIAS[index])));
  return {batch, input, output, inputShape:[batch,3], outputShape:[batch,2], weightShape:[2,3], biasShape:[2], weightParameters:6, biasParameters:2, parameters:8};
}

export function sgdStep(w, learningRate, storedGradient = 0, clearGrad = true) {
  finite(w, 'w'); finite(learningRate, 'learningRate'); finite(storedGradient, 'storedGradient');
  if (learningRate < 0) throw new RangeError('learningRate must be nonnegative');
  const previousGradient = clearGrad ? 0 : storedGradient;
  const newGradient = 2*(w-3);
  const gradientUsed = previousGradient+newGradient;
  const wAfter = w-learningRate*gradientUsed;
  return {wBefore:w,lossBefore:(w-3)**2,previousGradient,newGradient,gradientUsed,wAfter,lossAfter:(wAfter-3)**2};
}

export function simulateSgd(start, learningRate, steps, clearGrad = true) {
  finite(start, 'start'); integer(steps,0,1000,'steps');
  let w=start,gradient=0;
  const history=[];
  for(let index=0;index<steps;index++) {
    const step=sgdStep(w,learningRate,gradient,clearGrad);
    history.push(step);w=step.wAfter;gradient=step.gradientUsed;
  }
  return {w,gradient,steps,loss:(w-3)**2,history};
}

export const LINE_X = Object.freeze([-2,-1,0,1,2]);
export const LINE_Y = Object.freeze(LINE_X.map(x=>2*x+1));

export function affineMse(w,b) {
  finite(w,'w');finite(b,'b');
  return LINE_X.reduce((sum,x,index)=>sum+(w*x+b-LINE_Y[index])**2,0)/LINE_X.length;
}

export function fitLineStep(w,b,learningRate=0.1) {
  finite(w,'w');finite(b,'b');finite(learningRate,'learningRate');
  if(learningRate<0)throw new RangeError('learningRate must be nonnegative');
  const residuals=LINE_X.map((x,index)=>w*x+b-LINE_Y[index]);
  const gradW=2*residuals.reduce((sum,residual,index)=>sum+residual*LINE_X[index],0)/LINE_X.length;
  const gradB=2*residuals.reduce((sum,residual)=>sum+residual,0)/LINE_X.length;
  const nextW=w-learningRate*gradW,nextB=b-learningRate*gradB;
  return {wBefore:w,bBefore:b,lossBefore:affineMse(w,b),gradW,gradB,w:nextW,b:nextB,loss:affineMse(nextW,nextB)};
}

export function fitLine(steps=0) {
  integer(steps,0,100,'steps');
  let w=0,b=0;
  const history=[];
  for(let index=0;index<steps;index++) {
    const step=fitLineStep(w,b,0.1);history.push(step);w=step.w;b=step.b;
  }
  return {steps,w,b,loss:affineMse(w,b),predictions:LINE_X.map(x=>w*x+b),history};
}

const presets = Object.freeze([
  {label:'[2, 2]',matrix:[[1,3],[2,6]]},
  {label:'[2, 3]',matrix:[[1,2,3],[4,5,6]]},
  {label:'[3, 1]',matrix:[[2],[4],[6]]},
]);
const fmt = formatNumber;
const shape = value => `[${value.join(', ')}]`;
const vector = values => `[${values.map(fmt).join(', ')}]`;
const note = '<p class="tlab-note">公式演示：数值由 JavaScript 按所示公式计算，采用双精度；代码区仍用真实 PyTorch 执行和判题。</p>';
const button = (text, attributes='', selected=false) => `<button type="button" class="tlab-button${selected?' is-active':''}" ${attributes}>${text}</button>`;
function matrixHtml(matrix, label) {
  return `<div class="tlab-matrix-block"><span class="tlab-caption">${escape(label)}</span><div class="tlab-scroll"><table class="tlab-matrix"><tbody>${matrix.map(row=>`<tr>${row.map(value=>`<td>${fmt(value)}</td>`).join('')}</tr>`).join('')}</tbody></table></div></div>`;
}
const numberCard = (label,value,detail='') => `<div class="tlab-number"><span>${escape(label)}</span><strong>${escape(value)}</strong>${detail?`<small>${escape(detail)}</small>`:''}</div>`;
const header = (id,title,description,body) => `<section id="lab-${id}" class="lesson-lab" data-torch-lab="${id}" data-lab="${id}" aria-label="${escape(title)}"><div class="tlab-heading"><span class="tlab-kicker">本课交互 · ${id.toUpperCase()}</span><h4>${escape(title)}</h4><p>${escape(description)}</p></div>${body}${note}</section>`;
const find = (root,id) => root?.matches?.(`[data-torch-lab="${id}"]`) ? root : root?.querySelector?.(`[data-torch-lab="${id}"]`);
function beginBind(root,id) {
  const lab=find(root,id);
  if(!lab || lab.dataset.torchBound==='1')return null;
  lab.dataset.torchBound='1';return lab;
}
function activeButtons(lab,selector,attribute,value) {
  for(const element of lab.querySelectorAll(selector)) {
    const selected=element.getAttribute(attribute)===String(value);
    element.classList.toggle('is-active',selected);element.setAttribute('aria-pressed',String(selected));
  }
}

function rowMeanResult(matrix,dim) {
  const result=matrixMeans(matrix,dim);
  const sums=dim===1?matrix.map(row=>row.reduce((sum,value)=>sum+value,0)):matrix[0].map((_,column)=>matrix.reduce((sum,row)=>sum+row[column],0));
  const divisor=dim===1?matrix[0].length:matrix.length;
  return `${matrixHtml(matrix,`x.shape = ${shape(matrixShape(matrix))} · 行是样本，列是特征`)}<div class="tlab-code">x.mean(dim=${dim}) → ${vector(result.values)}</div><div class="tlab-numbers">${numberCard('输出 shape',shape(result.shape),dim===1?'每行留下一个值':'每列留下一个值')}${numberCard('沿哪一轴归约',`dim = ${dim}`,dim===1?'本题目标：逐行均值':'对照计算：逐列均值')}</div><p class="tlab-explanation">${dim===1?'逐行':'逐列'}计算：${sums.map(sum=>`${fmt(sum)} ÷ ${divisor}`).join('；')}。</p>`;
}
function renderT1() {
  return header('t1','行均值：dim决定归约方向','先认清 [batch, features]，再观察归约后哪一维消失。',`<div class="tlab-controls"><span>输入形状</span>${presets.map((preset,index)=>button(preset.label,`data-preset="${index}" aria-pressed="${index===0}"`,index===0)).join('')}</div><div class="tlab-controls"><span>归约方向</span>${button('dim=1 · 每行', 'data-dim="1" aria-pressed="true"',true)}${button('dim=0 · 每列对照','data-dim="0" aria-pressed="false"')}</div><div data-result aria-live="polite">${rowMeanResult(presets[0].matrix,1)}</div>`);
}
function bindT1(root) {
  const lab=beginBind(root,'t1');if(!lab)return false;
  let preset=0,dim=1;
  const update=()=>{lab.querySelector('[data-result]').innerHTML=rowMeanResult(presets[preset].matrix,dim);activeButtons(lab,'[data-preset]','data-preset',preset);activeButtons(lab,'[data-dim]','data-dim',dim);};
  for(const element of lab.querySelectorAll('[data-preset]'))element.addEventListener('click',()=>{const index=Number(element.dataset.preset);if(presets[index]){preset=index;update();}});
  for(const element of lab.querySelectorAll('[data-dim]'))element.addEventListener('click',()=>{dim=Number(element.dataset.dim)===0?0:1;update();});
  return true;
}

function centeredResult(matrix) {
  const correct=centerRows(matrix,true),incorrect=centerRows(matrix,false);
  return `${matrixHtml(matrix,`输入 x.shape = ${shape(correct.inputShape)}`)}<div class="tlab-compare"><div class="tlab-panel tlab-good"><h5>keepdim=True · 本题目标</h5><div class="tlab-code">mean: ${shape(correct.meanShape)} = ${correct.means.map(v=>`[${fmt(v)}]`).join(', ')}</div>${matrixHtml(correct.output,`x - mean → ${shape(correct.outputShape)}`)}<p>每行减去自己的均值。</p></div><div class="tlab-panel tlab-caution"><h5>keepdim=False · 广播对照</h5><div class="tlab-code">mean: ${shape(incorrect.meanShape)} = ${vector(incorrect.means)}</div>${incorrect.ok?`${matrixHtml(incorrect.output,`x - mean → ${shape(incorrect.outputShape)}`)}<p>${correct.inputShape[1]===1?'特征宽度1被扩展，输出甚至变成方阵。':'没有报错，但按列减去了不同样本的均值。'}</p>`:`<div class="tlab-error">形状不兼容：${shape(incorrect.inputShape)} 与 ${shape(incorrect.meanShape)} 无法广播。</div><p>最后一维无法对齐，PyTorch会报RuntimeError。</p>`}</div></div>`;
}
function renderT2() {
  return header('t2','逐行中心化：保留均值的维度','把同一个输入的两种广播结果并排比较，既看数值，也看shape。',`<div class="tlab-controls"><span>输入形状</span>${presets.map((preset,index)=>button(preset.label,`data-preset="${index}" aria-pressed="${index===0}"`,index===0)).join('')}</div><div data-result aria-live="polite">${centeredResult(presets[0].matrix)}</div>`);
}
function bindT2(root) {
  const lab=beginBind(root,'t2');if(!lab)return false;
  for(const element of lab.querySelectorAll('[data-preset]'))element.addEventListener('click',()=>{const index=Number(element.dataset.preset);if(presets[index]){lab.querySelector('[data-result]').innerHTML=centeredResult(presets[index].matrix);activeButtons(lab,'[data-preset]','data-preset',index);}});
  return true;
}

function derivativeSvg(x,kind) {
  const left=36,right=334,top=16,bottom=168;
  const px=value=>left+(value+4)/8*(right-left),py=value=>bottom-(value+4)/34*(bottom-top);
  const point=functionAndGradient(x,kind);
  const path=Array.from({length:81},(_,index)=>{const coordinate=-4+index/10;return `${index?'L':'M'}${px(coordinate).toFixed(2)},${py(functionAndGradient(coordinate,kind).value).toFixed(2)}`;}).join(' ');
  const x1=x-1.1,x2=x+1.1;
  return `<svg class="tlab-chart" viewBox="0 0 360 195" role="img" aria-label="${escape(point.formula)}的曲线，圆点表示函数值，直线表示此处切线"><defs><clipPath id="tlab-t3-clip"><rect x="${left}" y="${top}" width="${right-left}" height="${bottom-top}"/></clipPath></defs><path d="M${left},${py(0)}H${right} M${px(0)},${top}V${bottom}" class="tlab-axis"/><g clip-path="url(#tlab-t3-clip)"><path d="${path}" class="tlab-function"/><line x1="${px(x1)}" y1="${py(point.value+point.gradient*(x1-x))}" x2="${px(x2)}" y2="${py(point.value+point.gradient*(x2-x))}" class="tlab-tangent"/><circle cx="${px(x)}" cy="${py(point.value)}" r="4.5" class="tlab-point"/></g><text x="${right-7}" y="${py(0)+15}">x</text><text x="${px(0)+7}" y="${top+7}">y</text><text x="${left-6}" y="${bottom+17}">−4</text><text x="${right-3}" y="${bottom+17}">4</text></svg>`;
}
function derivativeResult(x,kind) {
  const result=functionAndGradient(x,kind);
  return `<div class="tlab-formula">${escape(result.formula)} <span>· ${escape(result.derivative)}</span></div>${derivativeSvg(x,kind)}<div class="tlab-numbers">${numberCard('输入 x',fmt(x))}${numberCard('函数值 y',fmt(result.value),'曲线上圆点的纵坐标')}${numberCard('梯度 dy/dx',fmt(result.gradient),'切线斜率；不是函数值')}</div><p class="tlab-explanation">当前是${kind==='square'?'概念题的 y=x²':'完整代码题的 y=x²+3x'}。当 x=${fmt(x)}，函数值为${fmt(result.value)}，对x求导得到${fmt(result.gradient)}。</p>`;
}
function renderT3() {
  return header('t3','函数值与梯度：先选对正在求导的函数','两条函数各有自己的公式与导数，不把x²的斜率当成x²+3x的答案。',`<div class="tlab-controls">${button('y = x² · 概念题','data-function="square" aria-pressed="false"')}${button('y = x² + 3x · 代码题','data-function="quadratic-linear" aria-pressed="true"',true)}</div><label class="tlab-slider">改变输入 x<input type="range" min="-4" max="4" step="0.25" value="2" data-x aria-label="调整求导位置x"></label><div data-result aria-live="polite">${derivativeResult(2,'quadratic-linear')}</div>`);
}
function bindT3(root) {
  const lab=beginBind(root,'t3');if(!lab)return false;
  let kind='quadratic-linear';
  const update=()=>{const x=Number(lab.querySelector('[data-x]').value);lab.querySelector('[data-result]').innerHTML=derivativeResult(x,kind);activeButtons(lab,'[data-function]','data-function',kind);};
  lab.querySelector('[data-x]').addEventListener('input',update);
  for(const element of lab.querySelectorAll('[data-function]'))element.addEventListener('click',()=>{if(['square','quadratic-linear'].includes(element.dataset.function)){kind=element.dataset.function;update();}});
  return true;
}

function linearResult(batch) {
  const result=linearDemo(batch);
  return `<div class="tlab-numbers">${numberCard('输入 x.shape',shape(result.inputShape))}${numberCard('输出 y.shape',shape(result.outputShape))}${numberCard('可训练参数总数','8','6个weight + 2个bias')}</div><div class="tlab-compare"><div class="tlab-panel">${matrixHtml(result.input,`输入 · ${batch}条样本，每条3个特征`)}</div><div class="tlab-panel tlab-good">${matrixHtml(result.output,`输出 · ${batch}条样本，每条2个得分`)}</div></div><div class="tlab-compare">${matrixHtml(LINEAR_WEIGHT,'weight.shape = [2, 3] · 参数数6')}${matrixHtml([LINEAR_BIAS],'bias.shape = [2] · 参数数2')}</div><div class="tlab-code">y = x @ weight.T + bias</div><p class="tlab-explanation">这里固定一组权重展示实际乘加；nn.Linear默认会随机初始化。改变batch只增加要处理的样本，不增加weight或bias的数量。</p>`;
}
function renderT4() {
  return header('t4','nn.Linear(3,2)：样本数与参数数是两件事','输入3个特征，输出2个得分；同一层的8个参数在所有样本间共享。',`<label class="tlab-slider">改变 batch 大小<input type="range" min="1" max="6" step="1" value="2" data-batch aria-label="调整Linear输入的batch大小"></label><div data-result aria-live="polite">${linearResult(2)}</div>`);
}
function bindT4(root) {
  const lab=beginBind(root,'t4');if(!lab)return false;
  lab.querySelector('[data-batch]').addEventListener('input',()=>{lab.querySelector('[data-result]').innerHTML=linearResult(Number(lab.querySelector('[data-batch]').value));});
  return true;
}

function sgdPanel(result,title,correct) {
  const latest=result.history.at(-1);
  return `<div class="tlab-panel ${correct?'tlab-good':'tlab-caution'}"><h5>${title}</h5><div class="tlab-numbers">${numberCard('当前参数 w',fmt(result.w))}${numberCard('当前 loss',fmt(result.loss))}</div>${latest?`<dl class="tlab-steps"><div><dt>本步更新前w</dt><dd>${fmt(latest.wBefore)}</dd></div><div><dt>旧梯度${correct?'已清空':'未清空'}</dt><dd>${fmt(latest.previousGradient)}</dd></div><div><dt>本次backward新梯度 2(w−3)</dt><dd>${fmt(latest.newGradient)}</dd></div><div><dt>step使用的累计.grad</dt><dd>${fmt(latest.gradientUsed)}</dd></div></dl>`:'<p>尚未执行backward；.grad尚无值，参数还没有更新。</p>'}</div>`;
}
function sgdResult(start,rate,steps) {
  const good=simulateSgd(start,rate,steps,true),bad=simulateSgd(start,rate,steps,false);
  return `<div class="tlab-formula">loss = (w − 3)² <span>· grad = 2(w − 3)</span></div><p class="tlab-explanation">已执行 <b>${steps}</b> 步；每步使用 w ← w − ${fmt(rate)} × .grad。${steps===0?'先执行一步，两边相同；再执行一步，观察错误累积的差别。':''}</p><div class="tlab-compare">${sgdPanel(good,'每步zero_grad → backward → step',true)}${sgdPanel(bad,'漏掉zero_grad · 错误累积对照',false)}</div>`;
}
function renderT5() {
  return header('t5','一次SGD更新：梯度先算，参数后改','对照每步正确清梯度与意外累积；loss.backward本身不会更新w。',`<div class="tlab-slider-pair"><label class="tlab-slider">初始 w = <output data-start-value>0</output><input type="range" min="-1" max="6" step="0.5" value="0" data-start aria-label="调整SGD初始参数w"></label><label class="tlab-slider">学习率 = <output data-rate-value>0.1</output><input type="range" min="0.01" max="0.3" step="0.01" value="0.1" data-rate aria-label="调整SGD学习率"></label></div><div class="tlab-controls">${button('执行一步','data-step="1"')}${button('再执行5步','data-step="5"')}${button('重置','data-reset')}</div><div data-result aria-live="polite">${sgdResult(0,0.1,0)}</div><p class="tlab-note">修改初始值或学习率会从第0步重新开始；完整代码题只要求执行一次正确更新。</p>`);
}
function bindT5(root) {
  const lab=beginBind(root,'t5');if(!lab)return false;
  let steps=0;
  const update=()=>{const start=Number(lab.querySelector('[data-start]').value),rate=Number(lab.querySelector('[data-rate]').value);lab.querySelector('[data-start-value]').textContent=fmt(start);lab.querySelector('[data-rate-value]').textContent=fmt(rate);lab.querySelector('[data-result]').innerHTML=sgdResult(start,rate,steps);for(const element of lab.querySelectorAll('[data-step]'))element.disabled=steps>=30;};
  for(const element of lab.querySelectorAll('[data-step]'))element.addEventListener('click',()=>{steps=Math.min(30,steps+Number(element.dataset.step));update();});
  for(const selector of ['[data-start]','[data-rate]'])lab.querySelector(selector).addEventListener('input',()=>{steps=0;update();});
  lab.querySelector('[data-reset]').addEventListener('click',()=>{steps=0;update();});
  return true;
}

function fitSvg(result) {
  const left=36,right=334,top=14,bottom=182;
  const px=x=>left+(x+2.5)/5*(right-left),py=y=>bottom-(y+5)/12*(bottom-top);
  const target=LINE_X.map((x,index)=>`<circle cx="${px(x)}" cy="${py(LINE_Y[index])}" r="4.5" class="tlab-target"/>`).join('');
  const predictions=LINE_X.map((x,index)=>`<circle cx="${px(x)}" cy="${py(result.predictions[index])}" r="3" class="tlab-prediction"/>`).join('');
  return `<svg class="tlab-chart tlab-fit-chart" viewBox="0 0 360 209" role="img" aria-label="五个真实数据点y等于2x加1，以及当前拟合直线y等于${fmt(result.w)}x加${fmt(result.b)}"><path d="M${left},${py(0)}H${right} M${px(0)},${top}V${bottom}" class="tlab-axis"/><path d="M${px(-2.5)},${py(result.w*-2.5+result.b)}L${px(2.5)},${py(result.w*2.5+result.b)}" class="tlab-function"/>${target}${predictions}<text x="${left}" y="${bottom+17}">−2.5</text><text x="${right-14}" y="${bottom+17}">2.5</text><text x="${px(0)+7}" y="${top+7}">y</text><text x="${right-9}" y="${py(0)+15}">x</text></svg>`;
}
function fitResult(steps) {
  const result=fitLine(steps),latest=result.history.at(-1);
  return `<div class="tlab-formula">训练目标 y = 2x + 1 <span>· 模型 pred = wx + b</span></div>${fitSvg(result)}<div class="tlab-legend"><span class="tlab-target-key">● 固定数据点</span><span class="tlab-model-key">— 当前模型与预测点</span></div><div class="tlab-numbers">${numberCard('当前w',fmt(result.w),'目标为2')}${numberCard('当前b',fmt(result.b),'目标为1')}${numberCard('当前MSE',fmt(result.loss),`第${steps}次更新后的参数`)}</div><div class="tlab-code">MSE = mean((w*x + b − y)²)<br>grad_w = mean(2*(pred−y)*x)<br>grad_b = mean(2*(pred−y))</div>${latest?`<p class="tlab-explanation">最近一步：w ${fmt(latest.wBefore)} − 0.1 × (${fmt(latest.gradW)}) → ${fmt(result.w)}；b ${fmt(latest.bBefore)} − 0.1 × (${fmt(latest.gradB)}) → ${fmt(result.b)}。</p>`:'<p class="tlab-explanation">w、b均从0开始，此时直线水平，MSE为9。数据固定为x=[−2,−1,0,1,2]，y=[−3,−1,1,3,5]。</p>'}<p class="tlab-note">这里显示更新后参数的loss；代码中在step前计算的loss对应上一组参数。JavaScript双精度与真实Torch float32在收敛后的末尾数位会略有差异。</p>`;
}
function renderT6() {
  return header('t6','训练第一条直线：一次更新放进循环','固定零初始化、SGD学习率0.1与100步上限，观察参数、损失和直线同时变化。',`<label class="tlab-slider">训练进度 <output data-iteration-value>0 / 100步</output><input type="range" min="0" max="100" step="1" value="0" data-iteration aria-label="选择线性拟合训练步数"></label><div class="tlab-controls">${button('+1步','data-advance="1"')}${button('+10步','data-advance="10"')}${button('训练到100步','data-complete')}${button('从0重置','data-reset')}</div><div data-result aria-live="polite">${fitResult(0)}</div>`);
}
function bindT6(root) {
  const lab=beginBind(root,'t6');if(!lab)return false;
  const slider=lab.querySelector('[data-iteration]');
  const update=()=>{const steps=Number(slider.value);lab.querySelector('[data-iteration-value]').textContent=`${steps} / 100步`;lab.querySelector('[data-result]').innerHTML=fitResult(steps);for(const element of lab.querySelectorAll('[data-advance],[data-complete]'))element.disabled=steps>=100;};
  slider.addEventListener('input',update);
  for(const element of lab.querySelectorAll('[data-advance]'))element.addEventListener('click',()=>{slider.value=String(Math.min(100,Number(slider.value)+Number(element.dataset.advance)));update();});
  lab.querySelector('[data-complete]').addEventListener('click',()=>{slider.value='100';update();});
  lab.querySelector('[data-reset]').addEventListener('click',()=>{slider.value='0';update();});
  return true;
}

export const torchLabMetadata = Object.freeze([
  {id:'t1',widgetId:'torch-row-means',target:'row_means(x)：二维张量逐行均值、dim与输出shape'},
  {id:'t2',widgetId:'torch-center-rows',target:'center_rows(x)：keepdim控制逐行中心化与广播'},
  {id:'t3',widgetId:'torch-autograd-functions',target:'gradient_at(value)：区分x²与x²+3x的函数值和导数'},
  {id:'t4',widgetId:'torch-linear-shapes',target:'TinyModel：nn.Linear(3,2)输入输出shape与8个参数'},
  {id:'t5',widgetId:'torch-sgd-step',target:'update_weight(start)：loss=(w−3)²的一步SGD与清梯度'},
  {id:'t6',widgetId:'torch-affine-training',target:'fit_line()：零初始化、学习率0.1、100步拟合y=2x+1'},
].map(Object.freeze));

const rendering=[renderT1,renderT2,renderT3,renderT4,renderT5,renderT6];
const binding=[bindT1,bindT2,bindT3,bindT4,bindT5,bindT6];
export const torchLabs=Object.freeze(Object.fromEntries(torchLabMetadata.map((metadata,index)=>[metadata.id,Object.freeze({...metadata,render:rendering[index],bind:binding[index]})])));
export function renderTorchLabById(id) {return Object.hasOwn(torchLabs,id)?torchLabs[id].render():'';}
export function bindTorchLabById(id,root) {return Object.hasOwn(torchLabs,id)?torchLabs[id].bind(root):false;}
