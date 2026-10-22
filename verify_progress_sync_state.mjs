import assert from 'node:assert/strict';
import {DatabaseSync} from 'node:sqlite';
import {readFile,readdir} from 'node:fs/promises';
import {setImmediate as tick} from 'node:timers/promises';
import cloudWorker from './cloud/worker.js';
import {s256} from './cloud/pages-auth.mjs';
import {
  COURSE_ID,PAGES_URL,MAX_PROGRESS_BYTES,MAX_COMPRESSED_BYTES,
  accountStorageKey,emptyCourseProgress,validProgress,progressByteSize,
  normalizeCloudSnapshot,normalizeCache,planCloudReconcile,
  resolveConflictSnapshot,validateLoginReturn,createProgressSync,
  normalizeGuestProgress,canLoginHere,
} from './dist/sync.js';

const tests=[],test=(title,fn)=>tests.push({title,fn});
const freeze=value=>{if(value&&typeof value==='object'){Object.freeze(value);Object.values(value).forEach(freeze);}return value;};
const progress=(code='')=>({...emptyCourseProgress(),drafts:{p1:code}});
const local=(overrides={})=>({userId:'alice',courseId:COURSE_ID,revision:3,dirty:false,progress:progress('alice code'),updatedAt:'2026-01-01T00:00:00.000Z',serverUpdatedAt:null,...overrides});
const remote=(overrides={})=>({revision:3,progress:progress('cloud code'),updatedAt:'2026-01-01T00:00:00.000Z',...overrides});

test('module is importable with no DOM, storage, fetch mocks, or authenticated cloud',()=>{
  assert.equal(typeof createProgressSync,'function');assert.equal(COURSE_ID,'python-pytorch');assert.equal(PAGES_URL,'https://hellojim2007.github.io/kailian/');
});
test('account and course cache keys are distinct; guest remains a separate namespace',()=>{
  const keys=[accountStorageKey('alice'),accountStorageKey('bob'),accountStorageKey('alice','networking'),accountStorageKey('alice:networking')];
  assert.equal(new Set(keys).size,4);assert(keys.every(key=>key!=='kaillian-v1'));assert(accountStorageKey('a/b').includes('a%2Fb'));
});
test('new account starts empty instead of copying guest progress',()=>{
  const guest=progress('guest solution');guest.passed.p1=true;
  const fresh=emptyCourseProgress();assert.deepEqual(fresh.drafts,{});assert.deepEqual(fresh.passed,{});assert.notDeepEqual(fresh,guest);
  assert.equal(planCloudReconcile(null,remote({revision:0,progress:null}),'alice').action,'pull');
});
test('cache normalization rejects another account or course and clones owned data',()=>{
  assert.equal(normalizeCache(local(),'bob'),null);assert.equal(normalizeCache(local(),'alice','networking'),null);
  const source=freeze(local()),clean=normalizeCache(source,'alice');clean.progress.drafts.p1='edited';assert.equal(source.progress.drafts.p1,'alice code');
  assert.deepEqual(normalizeCache(normalizeCache(local(),'alice'),'alice'),normalizeCache(local(),'alice'));
});
test('cloud malformed revisions or progress are rejected without applying anything',()=>{
  for(const source of [{},{revision:-1,progress:null},{revision:1.5,progress:null},{revision:Number.MAX_SAFE_INTEGER+1,progress:null},{revision:3,progress:{version:1}},{revision:3,progress:[]}])assert.throws(()=>normalizeCloudSnapshot(source));
  assert.deepEqual(normalizeCloudSnapshot({revision:0,progress:null,updatedAt:null}),{revision:0,progress:null,updatedAt:null});
  assert(!validProgress({version:2,drafts:[],passed:{}}));
});
test('reconcile distinguishes clean pull, dirty push, 409 conflict, account rejection',()=>{
  assert.equal(planCloudReconcile(local(),remote(),'alice').action,'noop');
  assert.equal(planCloudReconcile(local(),remote({revision:4}),'alice').action,'pull');
  assert.equal(planCloudReconcile(local({dirty:true}),remote(),'alice').action,'push');
  assert.equal(planCloudReconcile(local({dirty:true}),remote({revision:4}),'alice').action,'conflict');
  assert.equal(planCloudReconcile(local({userId:'bob'}),remote(),'alice').action,'reject');
  assert.equal(planCloudReconcile(local({courseId:'networking'}),remote(),'alice').action,'reject');
});
test('interrupted local two-key writes require conflict handling even at same revision',()=>{
  const interrupted=normalizeCache(local({writePending:true,dirty:true}),'alice');
  assert.equal(planCloudReconcile(interrupted,remote(),'alice').action,'conflict');
});
test('explicit conflict choices clone and retain both sources without silent merge',()=>{
  const l=freeze(local({dirty:true})),r=freeze(remote({revision:4}));
  const cloud=resolveConflictSnapshot('cloud',l,r,'alice');assert.equal(cloud.revision,4);assert.equal(cloud.dirty,false);assert.equal(cloud.progress.drafts.p1,'cloud code');
  const mine=resolveConflictSnapshot('local',l,r,'alice');assert.equal(mine.revision,4);assert.equal(mine.dirty,true);assert.equal(mine.progress.drafts.p1,'alice code');
  assert.equal(l.revision,3);assert.equal(l.dirty,true);cloud.progress.drafts.p1='x';assert.equal(r.progress.drafts.p1,'cloud code');
  assert.throws(()=>resolveConflictSnapshot('merge',l,r,'alice'));assert.throws(()=>resolveConflictSnapshot('cloud',l,r,'bob'));
});
test('choosing local does not bypass a cloud write that happens after conflict choice',()=>{
  const resolved=resolveConflictSnapshot('local',local({dirty:true}),remote({revision:4}),'alice');
  assert.equal(planCloudReconcile(resolved,remote({revision:5}),'alice').action,'conflict');
});
test('PKCE callback requires matching state, verifier, code and a fresh flow',()=>{
  const now=1000000,pending={verifier:'x'.repeat(64),state:'random-state',createdAt:now-1000};
  assert(validateLoginReturn({pending,code:'single-use-code',state:'random-state',now}));
  assert(!validateLoginReturn({pending,code:'single-use-code',state:'wrong-state',now}));
  assert(!validateLoginReturn({pending:{...pending,createdAt:now-600001},code:'code',state:pending.state,now}));
  assert(!validateLoginReturn({pending:{...pending,createdAt:now+1},code:'code',state:pending.state,now}));
  assert(!validateLoginReturn({pending:{...pending,verifier:'short'},code:'code',state:pending.state,now}));
  assert(!validateLoginReturn({pending,code:'',state:pending.state,now}));
});
test('payload sizes use actual UTF-8 bytes, with documented backend limits',()=>{
  assert.equal(progressByteSize('汉'),5);assert.equal(MAX_PROGRESS_BYTES,8388608);assert.equal(MAX_COMPRESSED_BYTES,1500000);
  const large=progress('x'.repeat(MAX_PROGRESS_BYTES));assert(progressByteSize(large)>MAX_PROGRESS_BYTES);
});

test('legacy guest records are upgraded without mutating or silently importing them',()=>{
  for(const version of [undefined,1,2]){const source=progress('legacy');if(version===undefined)delete source.version;else source.version=version;freeze(source);const upgraded=normalizeGuestProgress(source);assert.equal(upgraded.version,2);assert.equal(upgraded.drafts.p1,'legacy');assert.notEqual(upgraded,source);}
  assert.equal(normalizeGuestProgress({version:9,drafts:{},passed:{}}),null);assert.equal(normalizeGuestProgress({drafts:[],passed:{}}),null);
});
test('PKCE begins only from the canonical Pages origin and repository path',()=>{
  assert(canLoginHere({origin:'https://hellojim2007.github.io',pathname:'/kailian/'}));
  for(const value of [{origin:'http://localhost:8766',pathname:'/'},{origin:'https://python-gym-lab-1021.milky-elk-9591.chatgpt.site',pathname:'/'},{origin:'https://hellojim2007.github.io',pathname:'/another-repo/'},{origin:'https://hellojim2007.github.io',pathname:'/kailian-evil/'}])assert(!canLoginHere(value));
});

// These state-machine tests use the actual Worker and actual SQLite statements.
// Only transport timing/failure is controlled; they do not verify a live login.
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b;});return {promise,resolve,reject};};
function memoryStorage(){const values=new Map();return {get length(){return values.size;},key:i=>[...values.keys()][i]??null,getItem:key=>values.get(key)??null,setItem:(key,value)=>values.set(key,String(value)),removeItem:key=>values.delete(key),clear:()=>values.clear()};}
async function harness({dirty=false,writePending=false,localCode='base',locationOrigin='https://hellojim2007.github.io'}={}){
  const sqlite=new DatabaseSync(':memory:');for(const name of (await readdir('drizzle')).filter(x=>x.endsWith('.sql')).sort())sqlite.exec(await readFile('drizzle/'+name,'utf8'));
  const DB={prepare(sql){let bindings=[];const q={bind(...args){bindings=args;return q;},async first(){return sqlite.prepare(sql).get(...bindings)||null;},async run(){const r=sqlite.prepare(sql).run(...bindings);return {success:true,meta:{changes:Number(r.changes)}};}};return q;}};
  const user={id:'alice',name:'Alice',email:'alice@example.test'},sessionToken='a'.repeat(43);
  sqlite.prepare('INSERT INTO pages_sessions (token_hash,user_id,user_name,user_email,created_at,expires_at) VALUES (?,?,?,?,?,?)').run(await s256(sessionToken),user.id,user.name,user.email,Date.now(),Date.now()+600000);
  const server=async(path,options={})=>cloudWorker.fetch(new Request('https://python-gym-lab-1021.milky-elk-9591.chatgpt.site'+path,{...options,headers:{'oai-authenticated-user-id':user.id,'oai-authenticated-user-email':user.email,...options.headers}}),{DB});
  await server('/api/progress',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({revision:0,progress:progress('base')})});
  const storage=memoryStorage(),sessions=memoryStorage(),key=accountStorageKey(user.id);
  storage.setItem('kaillian-v1',JSON.stringify(progress('guest original')));storage.setItem('kaillian-sync-active',JSON.stringify(user));storage.setItem(key,JSON.stringify(progress(localCode)));storage.setItem(key+':meta',JSON.stringify({userId:user.id,courseId:COURSE_ID,revision:1,dirty,writePending,updatedAt:isoForTest()}));
  sessions.setItem('kaillian-sync-token',JSON.stringify({token:sessionToken,user,expiresAt:new Date(Date.now()+600000).toISOString()}));
  const names=['localStorage','sessionStorage','fetch','location','history','window','navigator','setTimeout','clearTimeout','CompressionStream'],descriptors=new Map(names.map(name=>[name,Object.getOwnPropertyDescriptor(globalThis,name)]));
  let model=progress('guest original'),applies=0,intercept=async(_request,execute)=>execute(),nextTimer=1;const timers=new Map(),statuses=[],requests=[];
  const define=(name,value)=>Object.defineProperty(globalThis,name,{value,writable:true,configurable:true});
  define('localStorage',storage);define('sessionStorage',sessions);define('location',{origin:locationOrigin,pathname:locationOrigin.includes('github.io')?'/kailian/':'/',hash:'',search:''});define('history',{replaceState(){}});define('window',{addEventListener(){}});define('navigator',{onLine:true});
  define('setTimeout',(fn)=>{const id=nextTimer++;timers.set(id,fn);return id;});define('clearTimeout',id=>timers.delete(id));
  define('fetch',async(url,options={})=>{const request=new Request(url,options);requests.push({path:new URL(request.url).pathname,method:request.method});return intercept(request,()=>cloudWorker.fetch(request,{DB}));});
  const api=createProgressSync({getProgress:()=>model,applyProgress:value=>{model=structuredClone(value);applies++;},onStatus:value=>statuses.push(value)});
  return {api,storage,sessions,requests,statuses,key,server,define,get model(){return model;},get applies(){return applies;},get lastStatus(){return statuses.at(-1);},setInterceptor:fn=>{intercept=fn;},edit:code=>{model=progress(code);api.changed();},cache:()=>({...JSON.parse(storage.getItem(key+':meta')),progress:JSON.parse(storage.getItem(key))}),
    async remote(){return(await server('/api/progress')).json();},
    dispose(){for(const [name,descriptor]of descriptors)if(descriptor)Object.defineProperty(globalThis,name,descriptor);else delete globalThis[name];sqlite.close();},
  };
}
const isoForTest=()=>new Date().toISOString();

test('editing while cloud GET is in flight cannot be overwritten by its later snapshot',async()=>{
  const h=await harness(),entered=deferred(),release=deferred();
  try{
    await h.server('/api/progress',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify({revision:1,progress:progress('new remote')})});
    h.setInterceptor(async(request,execute)=>{const response=await execute();if(new URL(request.url).pathname==='/api/progress'&&request.method==='GET'){entered.resolve();await release.promise;}return response;});
    const starting=h.api.start();await entered.promise;h.edit('typed during GET');release.resolve();await starting;
    assert.equal(h.model.drafts.p1,'typed during GET');assert.equal(h.cache().progress.drafts.p1,'typed during GET');assert.equal(h.lastStatus.phase,'conflict');assert.equal(h.applies,1);
    assert.equal((await h.remote()).progress.drafts.p1,'new remote');assert.equal(h.requests.filter(x=>x.method==='PUT').length,0);
  }finally{release.resolve();h.dispose();}
});
test('interrupted cache markers survive activation and require an explicit conflict choice',async()=>{
  const h=await harness({dirty:true,writePending:true,localCode:'uncertain local'});
  try{await h.api.start();assert.equal(h.lastStatus.phase,'conflict');assert.equal(h.cache().writePending,true);assert.equal(h.requests.filter(x=>x.method==='PUT').length,0);await h.api.resolveConflict('cloud');assert.equal(h.cache().writePending,false);assert.equal(h.model.drafts.p1,'base');}finally{h.dispose();}
});
test('PUT committed before response loss is not blindly retried or cleared by later edits',async()=>{
  const h=await harness({dirty:true,localCode:'sent before disconnect'});let puts=0;
  try{
    h.setInterceptor(async(request,execute)=>{const response=await execute();if(request.method==='PUT'){puts++;throw new TypeError('simulated response loss after real SQL commit');}return response;});
    await h.api.start();assert.equal(h.lastStatus.phase,'error');assert.equal(h.cache().writePending,true);assert.equal((await h.remote()).revision,2);
    h.edit('later local editing');assert.equal(h.cache().writePending,true);await h.api.sync();assert.equal(h.lastStatus.phase,'conflict');assert.equal(puts,1);assert.equal(h.model.drafts.p1,'later local editing');assert.equal((await h.remote()).progress.drafts.p1,'sent before disconnect');
  }finally{h.dispose();}
});
test('logout invalidates in-flight GET ownership and restores the unchanged guest namespace',async()=>{
  const h=await harness(),entered=deferred(),release=deferred();
  try{
    h.setInterceptor(async(request,execute)=>{const response=await execute();if(new URL(request.url).pathname==='/api/progress'&&request.method==='GET'){entered.resolve();await release.promise;}return response;});
    const starting=h.api.start();await entered.promise;await h.api.logout();release.resolve();await starting;
    assert.equal(h.lastStatus.phase,'guest');assert.equal(h.model.drafts.p1,'guest original');assert.equal(JSON.parse(h.storage.getItem('kaillian-v1')).drafts.p1,'guest original');assert.equal(h.api.storageKey(),'kaillian-v1');
  }finally{release.resolve();h.dispose();}
});
test('logout while payload compression is pending prevents the old PUT from being sent',async()=>{
  const h=await harness({dirty:true,localCode:'must not be sent'}),entered=deferred(),release=deferred(),OriginalCompression=globalThis.CompressionStream;
  try{
    h.define('CompressionStream',class{constructor(format){const original=new OriginalCompression(format),held=new TransformStream({async transform(chunk,controller){entered.resolve();await release.promise;controller.enqueue(chunk);}});return {readable:original.readable.pipeThrough(held),writable:original.writable};}});
    const starting=h.api.start();await entered.promise;await h.api.logout();release.resolve();await starting;
    assert.equal(h.requests.filter(x=>x.method==='PUT').length,0);assert.equal(h.lastStatus.phase,'guest');assert.equal(h.model.drafts.p1,'guest original');
  }finally{release.resolve();h.dispose();}
});
test('editing during a successful PUT keeps the newer draft and status callbacks never apply/repaint it',async()=>{
  const h=await harness(),entered=deferred(),release=deferred();let held=false;
  try{
    await h.api.start();assert.equal(h.applies,1);h.edit('first edit');
    h.setInterceptor(async(request,execute)=>{const response=await execute();if(request.method==='PUT'&&!held){held=true;entered.resolve();await release.promise;}return response;});
    const syncing=h.api.sync();await entered.promise;h.edit('newer typing');release.resolve();await syncing;
    assert.equal(h.cache().dirty,true);assert.equal(h.cache().writePending,false);assert.equal(h.model.drafts.p1,'newer typing');assert.equal(h.applies,1);
    await h.api.sync();assert.equal(h.cache().dirty,false);assert.equal((await h.remote()).progress.drafts.p1,'newer typing');assert.equal(h.applies,1);
  }finally{release.resolve();h.dispose();}
});
test('non-Pages startup neither restores a foreign flow nor contacts the login backend',async()=>{
  const h=await harness({locationOrigin:'http://localhost:8766'});
  try{await h.api.start();assert.equal(h.lastStatus.phase,'guest');assert.equal(h.requests.length,0);assert.equal(h.sessions.getItem('kaillian-sync-login'),null);assert.equal(h.model.drafts.p1,'guest original');}finally{h.dispose();}
});

let failed=0;for(const {title,fn}of tests){try{await fn();console.log('PASS',title);}catch(error){failed++;console.error('FAIL',title,error.stack);}}
console.log(`${tests.length-failed}/${tests.length} sync-state regressions passed (pure rules and in-process Worker/SQLite transport races; no live-login claim).`);
if(failed)process.exitCode=1;
