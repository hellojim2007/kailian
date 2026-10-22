import assert from 'node:assert/strict';
import {test} from 'node:test';
import {DatabaseSync} from 'node:sqlite';
import {randomBytes} from 'node:crypto';
import {readdir, readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import worker, {REQUEST_LIMIT, STORED_LIMIT} from './worker.js';
import {s256} from './pages-auth.mjs';

const sqlDirectory = new URL('../drizzle/', import.meta.url);
const migrations = await Promise.all((await readdir(sqlDirectory)).filter(x=>x.endsWith('.sql')).sort().map(x=>readFile(new URL(x,sqlDirectory),'utf8')));
export function sqliteD1() {
  const sqlite = new DatabaseSync(':memory:');
  for (const sql of migrations) sqlite.exec(sql);
  return {
    sqlite,
    prepare(sql) {
      let bindings = [];
      const api = {
        bind(...values) { bindings=values; return api; },
        async first(column) { const row=sqlite.prepare(sql).get(...bindings); return column ? row?.[column] ?? null : row ?? null; },
        async run() { const result=sqlite.prepare(sql).run(...bindings); return {success:true,meta:{changes:Number(result.changes),last_row_id:Number(result.lastInsertRowid)}}; },
        async all() { return {success:true,results:sqlite.prepare(sql).all(...bindings)}; },
      };return api;
    },
  };
}
const origin='https://kaillian.example';
const pages='https://hellojim2007.github.io';
const progress=(code='print(80)')=>({version:2,current:'p1',drafts:{p1:code},passed:{p1:true},assessments:{version:1,drafts:{},attempts:[]}});
const headers=id=>id?{'oai-authenticated-user-id':id,'oai-authenticated-user-email':`${id}@example.test`}:{};
async function call(DB,path='/api/progress',{id='alice',method='GET',body,extra={}}={}) {
  return worker.fetch(new Request(origin+path,{method,headers:{...headers(id),...(body===undefined?{}:{'Content-Type':'application/json'}),...extra},...(body===undefined?{}:{body:typeof body==='string'?body:JSON.stringify(body)})}),{DB});
}

test('anonymous account is usable but progress requires identity',async()=>{
  const DB=sqliteD1();const account=await call(DB,'/api/account',{id:null});
  assert.equal(account.status,200);assert.equal((await account.json()).user,null);
  assert.equal((await call(DB,'/api/progress',{id:null})).status,401);
});
test('new account and first compressed save round-trip every progress field',async()=>{
  const DB=sqliteD1();assert.deepEqual(await(await call(DB)).json(),{revision:0,progress:null,updatedAt:null});
  const p=progress('中文🧪\n'.repeat(1000));p.assessments.attempts.push({id:'attempt-first',results:{x:{stdout:'yes'}}});
  const saved=await call(DB,'/api/progress',{method:'PUT',body:{revision:0,progress:p}});assert.equal(saved.status,200);
  const value=await saved.json();assert.equal(value.revision,1);assert.deepEqual(value.progress,p);assert.ok(Date.parse(value.updatedAt));
  assert.deepEqual(await(await call(DB)).json(),value);
  const stored=DB.sqlite.prepare('SELECT payload FROM learner_progress').get().payload;
  assert.ok(stored instanceof Uint8Array);assert.ok(stored.byteLength<STORED_LIMIT);
});
test('users are isolated and client user id cannot select another account',async()=>{
  const DB=sqliteD1();await call(DB,'/api/progress',{method:'PUT',body:{revision:0,userId:'bob',progress:progress('alice')}});
  assert.equal((await(await call(DB,'/api/progress',{id:'bob'})).json()).progress,null);
  const own=await(await call(DB)).json();assert.equal(own.progress.drafts.p1,'alice');
});
test('revision CAS rejects stale writes and does not destroy remote state',async()=>{
  const DB=sqliteD1();await call(DB,'/api/progress',{method:'PUT',body:{revision:0,progress:progress('first')}});
  const changed=await call(DB,'/api/progress',{method:'PUT',body:{revision:1,progress:progress('second')}});assert.equal(changed.status,200);
  const stale=await call(DB,'/api/progress',{method:'PUT',body:{revision:1,progress:progress('lost')}});assert.equal(stale.status,409);
  const conflict=await stale.json();assert.equal(conflict.revision,2);assert.equal(conflict.progress.drafts.p1,'second');assert.equal(conflict.error.code,'revision_conflict');
});
test('simultaneous first saves and updates each have exactly one winner',async()=>{
  const DB=sqliteD1();const writes=revision=>Promise.all(['left','right'].map(code=>call(DB,'/api/progress',{method:'PUT',body:{revision,progress:progress(code)}})));
  assert.deepEqual((await writes(0)).map(x=>x.status).sort(),[200,409]);
  assert.deepEqual((await writes(1)).map(x=>x.status).sort(),[200,409]);
  assert.equal((await(await call(DB)).json()).revision,2);
});
test('course default and explicit identifier agree; unknown course rejected',async()=>{
  const DB=sqliteD1();await call(DB,'/api/progress?course=python-pytorch',{method:'PUT',body:{revision:0,progress:progress()}});
  assert.equal((await(await call(DB)).json()).revision,1);
  assert.equal((await call(DB,'/api/progress?course=computer-network')).status,400);
});
test('bad revision, schema, media type, malformed JSON and cross-origin writes rejected',async()=>{
  const DB=sqliteD1();
  for(const body of [{revision:-1,progress:progress()},{revision:0.2,progress:progress()},{revision:0,progress:{}},{revision:0,progress:{version:2,drafts:[],passed:{}}}])assert.equal((await call(DB,'/api/progress',{method:'PUT',body})).status,400);
  assert.equal((await call(DB,'/api/progress',{method:'PUT',body:'{'})).status,400);
  assert.equal((await call(DB,'/api/progress',{method:'PUT',body:{},extra:{'Content-Type':'text/plain'}})).status,415);
  assert.equal((await call(DB,'/api/progress',{method:'PUT',body:{revision:0,progress:progress()},extra:{Origin:'https://evil.example'}})).status,403);
});
test('both declared and streamed oversize requests are rejected before storing',async()=>{
  const DB=sqliteD1();assert.equal((await call(DB,'/api/progress',{method:'PUT',body:'{}',extra:{'Content-Length':String(REQUEST_LIMIT+1)}})).status,413);
  const chunk=new Uint8Array(1024*1024).fill(32);
  const stream=new ReadableStream({start(c){for(let i=0;i<9;i++)c.enqueue(chunk);c.close();}});
  const request=new Request(origin+'/api/progress',{method:'PUT',headers:{...headers('alice'),'Content-Type':'application/json'},body:stream,duplex:'half'});
  assert.equal((await worker.fetch(request,{DB})).status,413);assert.equal((await(await call(DB)).json()).revision,0);
});
test('incompressible oversized snapshot rejected without overwriting saved data',async()=>{
  const DB=sqliteD1();await call(DB,'/api/progress',{method:'PUT',body:{revision:0,progress:progress('retained')}});
  const response=await call(DB,'/api/progress',{method:'PUT',body:{revision:1,progress:progress(randomBytes(1800000).toString('base64'))}});
  assert.equal(response.status,413);assert.equal((await response.json()).error.code,'snapshot_too_large');assert.equal((await(await call(DB)).json()).progress.drafts.p1,'retained');
});
test('cloud runtime is explicit, no arbitrary execution endpoint or auth cache',async()=>{
  const DB=sqliteD1();const health=await(await call(DB,'/api/health')).json();assert.equal(health.runtime,'browser');assert.equal(health.execution,false);
  assert.equal((await call(DB,'/api/run',{method:'POST',body:{code:'evil'}})).status,501);
  const response=await call(DB,'/api/account');assert.match(response.headers.get('Cache-Control'),/no-store/);assert.ok(response.headers.get('Vary').includes('oai-authenticated-user-id'));
});
test('account decodes UTF-8 display name and safely handles malformed encoding',async()=>{
  const DB=sqliteD1();const extra={'oai-authenticated-user-full-name':encodeURIComponent('同学'),'oai-authenticated-user-full-name-encoding':'percent-encoded-utf-8'};
  assert.equal((await(await call(DB,'/api/account',{extra})).json()).user.name,'同学');
  extra['oai-authenticated-user-full-name']='%malformed';assert.ok((await(await call(DB,'/api/account',{extra})).json()).user.name);
});
test('Pages gets exact CORS headers including errors, no credentials permission',async()=>{
  const DB=sqliteD1();const response=await call(DB,'/api/progress',{id:null,extra:{Origin:pages}});
  assert.equal(response.status,401);assert.equal(response.headers.get('Access-Control-Allow-Origin'),pages);assert.equal(response.headers.get('Access-Control-Allow-Credentials'),null);
  assert.equal((await call(DB,'/api/account',{extra:{Origin:'https://evil.example'}})).headers.get('Access-Control-Allow-Origin'),null);
});
test('database failures return a non-sensitive recoverable error',async()=>{
  const response=await call(undefined);assert.equal(response.status,503);assert.equal((await response.json()).error.code,'storage_unavailable');
});
test('full Pages bridge exchanges identity, saves cross-origin, and revokes access',async()=>{
  const DB=sqliteD1(), verifier=randomBytes(32).toString('base64url'), challenge=await s256(verifier);
  const connect=await call(DB,'/auth/connect?'+new URLSearchParams({returnTo:pages+'/kailian/',challenge,state:randomBytes(20).toString('base64url')}));
  assert.equal(connect.status,302);const redirect=new URL(connect.headers.get('Location'));assert.equal(redirect.pathname,'/kailian/');
  const code=new URLSearchParams(redirect.hash.slice(1)).get('sync_code');assert.ok(code);
  const exchange=await call(DB,'/api/session/exchange',{id:null,method:'POST',body:{code,verifier},extra:{Origin:pages}});assert.equal(exchange.status,200);
  const session=await exchange.json(), bearer={Origin:pages,Authorization:'Bearer '+session.token,'Sec-Fetch-Site':'cross-site'};
  const account=await(await call(DB,'/api/account',{id:null,extra:bearer})).json();assert.equal(account.user.id,'alice');
  const write=await call(DB,'/api/progress',{id:null,method:'PUT',body:{revision:0,progress:progress('from Pages')},extra:bearer});assert.equal(write.status,200);assert.equal(write.headers.get('Access-Control-Allow-Origin'),pages);
  const read=await(await call(DB,'/api/progress',{id:null,extra:bearer})).json();assert.equal(read.progress.drafts.p1,'from Pages');
  assert.equal((await call(DB,'/api/session/revoke',{id:null,method:'POST',extra:bearer})).status,200);
  assert.equal((await call(DB,'/api/progress',{id:null,extra:bearer})).status,401);
});
