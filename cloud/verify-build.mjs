import assert from 'node:assert/strict';
import {readFile,readdir} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const artifact = resolve(process.argv[2] || '.runtime/cloud-build');
const source = await readFile(resolve(artifact,'server/index.js'),'utf8');
assert.ok(!/^\s*import\s/m.test(source),'Worker must be self-contained');
const {default:worker} = await import(pathToFileURL(resolve(artifact,'server/index.js')));
assert.equal(typeof worker.fetch,'function');
let count=0;
for (const entry of await readdir('dist',{withFileTypes:true})) {
  if (!entry.isFile() || entry.name.startsWith('.') || entry.name.endsWith('.pyc')) continue;
  const response=await worker.fetch(new Request('https://build.example/'+entry.name));
  assert.equal(response.status,200,entry.name);
  const binaryType=entry.name.endsWith('.png')?'image/png':entry.name.endsWith('.ico')?'image/x-icon':null;
  if(binaryType){assert.deepEqual(Buffer.from(await response.arrayBuffer()),await readFile(resolve('dist',entry.name)),entry.name+' exact binary bytes');assert.equal(response.headers.get('Content-Type'),binaryType);}
  else assert.equal(await response.text(),await readFile(resolve('dist',entry.name),'utf8'),entry.name+' byte-equivalent UTF-8 body');
  assert.equal(response.headers.get('X-Content-Type-Options'),'nosniff');
  const cached=await worker.fetch(new Request('https://build.example/'+entry.name,{headers:{'If-None-Match':response.headers.get('ETag')}}));assert.equal(cached.status,304);
  const head=await worker.fetch(new Request('https://build.example/'+entry.name,{method:'HEAD'}));assert.equal(head.status,200);assert.equal(await head.text(),'');count++;
}
assert.equal((await worker.fetch(new Request('https://build.example/'))).status,200);
assert.equal((await worker.fetch(new Request('https://build.example/missing'))).status,404);
assert.equal((await worker.fetch(new Request('https://build.example/api/progress'))).status,401);
assert.equal((await worker.fetch(new Request('https://build.example/api/run',{method:'POST'}))).status,501);
const manifest=JSON.parse(await readFile(resolve(artifact,'.openai/hosting.json'),'utf8'));assert.equal(manifest.d1,'DB');assert.equal(manifest.static,undefined);
assert.ok((await readdir(resolve(artifact,'.openai/drizzle'))).some(x=>x.endsWith('.sql')));
console.log(`PASS self-contained Worker artifact, ${count} static assets, cache/HEAD, API boundaries and migration metadata`);
