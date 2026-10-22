import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {homedir} from 'node:os';
import {join} from 'node:path';
import {matrixMeans,centerRows,functionAndGradient,linearDemo,sgdStep,simulateSgd,
  affineMse,fitLineStep,fitLine,torchLabs,torchLabMetadata,renderTorchLabById,
  bindTorchLabById} from './dist/labs-torch.js';

let numericChecks=0;
function close(actual,expected,tolerance=1e-9) {
  if(Array.isArray(expected)) {
    assert.ok(Array.isArray(actual));assert.equal(actual.length,expected.length);
    for(let index=0;index<expected.length;index++)close(actual[index],expected[index],tolerance);
    return;
  }
  assert.ok(Number.isFinite(actual));
  assert.ok(Math.abs(actual-expected)<=tolerance*Math.max(1,Math.abs(expected)),`${actual} != ${expected}`);
  numericChecks++;
}

close(matrixMeans([[1,3],[2,6]],1).values,[2,4]);
close(matrixMeans([[1,3],[2,6]],0).values,[1.5,4.5]);
assert.deepEqual(matrixMeans([[1,3],[2,6]],1,true).shape,[2,1]);
assert.deepEqual(matrixMeans([[1,3],[2,6]],0,true).shape,[1,2]);
assert.deepEqual(matrixMeans([[1,3],[2,6]],1,true).data,[[2],[4]]);
close(centerRows([[1,3],[2,6]],true).output,[[-1,1],[-2,2]]);
close(centerRows([[1,3],[2,6]],false).output,[[-1,-1],[0,2]]);
assert.equal(centerRows([[1,2,3],[4,5,6]],false).ok,false);
close(centerRows([[2],[4],[6]],false).output,[[0,-2,-4],[2,0,-2],[4,2,0]]);
assert.deepEqual(centerRows([[2],[4],[6]],false).outputShape,[3,3]);
close(centerRows([[1,3,8]],false).output,centerRows([[1,3,8]],true).output);
assert.throws(()=>matrixMeans([[1],[2,3]],1));

for(const kind of ['square','quadratic-linear'])for(const x of [-4,-3,-1.5,0,2,4]) {
  const result=functionAndGradient(x,kind),e=1e-5;
  const numerical=(functionAndGradient(x+e,kind).value-functionAndGradient(x-e,kind).value)/(2*e);
  close(result.gradient,numerical,1e-8);
}
assert.equal(functionAndGradient(2,'square').value,4);
assert.equal(functionAndGradient(2,'square').gradient,4);
assert.equal(functionAndGradient(2,'quadratic-linear').value,10);
assert.equal(functionAndGradient(2,'quadratic-linear').gradient,7);

for(const batch of [1,2,6]) {
  const result=linearDemo(batch);
  assert.deepEqual(result.inputShape,[batch,3]);assert.deepEqual(result.outputShape,[batch,2]);
  assert.deepEqual(result.weightShape,[2,3]);assert.deepEqual(result.biasShape,[2]);
  assert.equal(result.parameters,8);
  close(result.output,Array.from({length:batch},(_,index)=>[-1.5,3+1.5*index]));
}
close(sgdStep(0,.1).wAfter,.6);close(sgdStep(5,.1).wAfter,4.6);close(sgdStep(3,.1).wAfter,3);
close(simulateSgd(0,.1,2,true).w,1.08);
close(simulateSgd(0,.1,2,false).w,1.68);
close(simulateSgd(0,.1,2,false).gradient,-10.8);
for(const start of [-1,0,3,5])for(const rate of [.01,.1,.3])for(const steps of [0,1,2,5,30]) {
  close(simulateSgd(start,rate,steps,true).w,3+(start-3)*(1-2*rate)**steps);
}
assert.equal(affineMse(0,0),9);
close([fitLineStep(0,0).w,fitLineStep(0,0).b,fitLineStep(0,0).loss],[.8,.2,3.52]);
for(const steps of [0,1,2,5,10,50,100]) {
  const result=fitLine(steps);
  close(result.w,2*(1-.6**steps));close(result.b,1-.8**steps);
  close(result.loss,8*.36**steps+.64**steps);
  for(let index=1;index<result.history.length;index++)assert.ok(result.history[index].loss<=result.history[index-1].loss);
}
close([fitLine(100).w,fitLine(100).b],[2,1],1e-8);

assert.deepEqual(Object.keys(torchLabs),['t1','t2','t3','t4','t5','t6']);
assert.equal(new Set(torchLabMetadata.map(item=>item.widgetId)).size,6);
for(const item of torchLabMetadata) {
  const html=renderTorchLabById(item.id);
  assert.ok(html.includes(`data-lab="${item.id}"`));
  assert.ok(html.includes(`data-torch-lab="${item.id}"`));
  assert.ok(html.includes('class="lesson-lab"'));assert.ok(html.includes('真实 PyTorch'));
  assert.ok(!html.includes('data-lesson='),'lab must not reuse the navigation data-lesson attribute');
  assert.equal(typeof torchLabs[item.id].bind,'function');
  assert.ok(!html.includes('NaN'));assert.ok(!html.includes('undefined'));
}
for(const id of ['pt20','unknown','constructor','toString','__proto__',null]) {
  assert.equal(renderTorchLabById(id),'');assert.equal(bindTorchLabById(id,null),false);
}
assert.ok(renderTorchLabById('t3').includes('函数值 y'));
assert.ok(renderTorchLabById('t3').includes('梯度 dy/dx'));
assert.ok(renderTorchLabById('t4').includes('weight.shape = [2, 3]'));
assert.ok(!renderTorchLabById('t4').includes('gradient-svg'));
assert.ok(renderTorchLabById('t5').includes('漏掉zero_grad'));
assert.ok(renderTorchLabById('t6').includes('MSE为9'));

const pythonCode=String.raw`
import json,torch
torch.set_num_threads(1)
matrices=[[[1.,3.],[2.,6.]],[[1.,2.,3.],[4.,5.,6.]],[[2.],[4.],[6.]]]
output={'reductions':[],'centering':[],'derivatives':[],'linear':[],'sgd':[],'fit':[]}
for matrix in matrices:
    x=torch.tensor(matrix,dtype=torch.float64)
    for dim in [0,1]:
        for keep in [False,True]:
            result=x.mean(dim=dim,keepdim=keep)
            output['reductions'].append({'matrix':matrix,'dim':dim,'keep':keep,'values':result.tolist(),'shape':list(result.shape)})
    for keep in [False,True]:
        try:
            result=x-x.mean(dim=1,keepdim=keep)
            output['centering'].append({'matrix':matrix,'keep':keep,'ok':True,'output':result.tolist(),'shape':list(result.shape)})
        except RuntimeError:
            output['centering'].append({'matrix':matrix,'keep':keep,'ok':False})
for kind in ['square','quadratic-linear']:
    for value in [-4.,-3.,-1.5,0.,2.,4.]:
        x=torch.tensor(value,dtype=torch.float64,requires_grad=True)
        y=x*x if kind=='square' else x*x+3*x
        y.backward()
        output['derivatives'].append({'kind':kind,'x':value,'value':y.item(),'gradient':x.grad.item()})
for batch in [1,2,6]:
    m=torch.nn.Linear(3,2,dtype=torch.float64)
    with torch.no_grad():
        m.weight.copy_(torch.tensor([[1.,0.,-1.],[0.,.5,1.]],dtype=torch.float64))
        m.bias.copy_(torch.tensor([.5,-1.],dtype=torch.float64))
    x=torch.tensor([[r+1.,r+2.,r+3.] for r in range(batch)],dtype=torch.float64)
    output['linear'].append({'batch':batch,'output':m(x).tolist(),'parameters':sum(p.numel() for p in m.parameters())})
for start in [-1.,0.,3.,5.]:
    for rate in [.01,.1,.3]:
        for steps in [0,1,2,5,30]:
            for clear in [False,True]:
                w=torch.tensor(start,dtype=torch.float64,requires_grad=True)
                optimizer=torch.optim.SGD([w],lr=rate)
                for _ in range(steps):
                    if clear:optimizer.zero_grad()
                    loss=(w-3)**2
                    loss.backward();optimizer.step()
                output['sgd'].append({'start':start,'rate':rate,'steps':steps,'clear':clear,'w':w.item(),'gradient':w.grad.item() if w.grad is not None else 0.})
for steps in [0,1,2,10,100]:
    x=torch.tensor([-2.,-1.,0.,1.,2.]);y=2*x+1
    w=torch.tensor(0.,requires_grad=True);b=torch.tensor(0.,requires_grad=True)
    optimizer=torch.optim.SGD([w,b],lr=.1)
    for _ in range(steps):
        optimizer.zero_grad();loss=((w*x+b-y)**2).mean();loss.backward();optimizer.step()
    output['fit'].append({'steps':steps,'w':w.item(),'b':b.item(),'loss':((w*x+b-y)**2).mean().item(),'predictions':(w*x+b).tolist()})
print(json.dumps(output))
`;
const python=process.env.KAILIAN_PYTHON || (process.platform==='win32'?join(homedir(),'AppData','Local','Programs','Python','Python310','python.exe'):'python3');
const result=spawnSync(python,['-X','utf8','-c',pythonCode],{encoding:'utf8',timeout:60000,maxBuffer:2*1024*1024});
assert.equal(result.status,0,`真实Torch对照执行失败：${result.stderr||result.error||'unknown'}`);
const native=JSON.parse(result.stdout);
let torchCases=0;
for(const item of native.reductions) {const actual=matrixMeans(item.matrix,item.dim,item.keep);close(actual.data,item.values);assert.deepEqual(actual.shape,item.shape);torchCases++;}
for(const item of native.centering) {const actual=centerRows(item.matrix,item.keep);assert.equal(actual.ok,item.ok);if(item.ok){close(actual.output,item.output);assert.deepEqual(actual.outputShape,item.shape);}torchCases++;}
for(const item of native.derivatives) {const actual=functionAndGradient(item.x,item.kind);close(actual.value,item.value);close(actual.gradient,item.gradient);torchCases++;}
for(const item of native.linear) {const actual=linearDemo(item.batch);close(actual.output,item.output);assert.equal(actual.parameters,item.parameters);torchCases++;}
for(const item of native.sgd) {const actual=simulateSgd(item.start,item.rate,item.steps,item.clear);close(actual.w,item.w);close(actual.gradient,item.gradient);torchCases++;}
for(const item of native.fit) {const actual=fitLine(item.steps);close(actual.w,item.w,1e-6);close(actual.b,item.b,1e-6);close(actual.loss,item.loss,1e-6);close(actual.predictions,item.predictions,1e-6);torchCases++;}
console.log(`PASS: six unique lesson labs; ${numericChecks} numeric comparisons; ${torchCases} real PyTorch cases.`);
console.log(`100-step fit (JS illustration): w=${fitLine(100).w}, b=${fitLine(100).b}, loss=${fitLine(100).loss}`);
console.log(`100-step fit (real Torch float32): ${JSON.stringify(native.fit.at(-1))}`);
