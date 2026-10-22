import {readFile, writeFile, mkdir, readdir, stat, cp} from 'node:fs/promises';
import {resolve, dirname, relative, sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
if (args.length && (args.length !== 2 || args[0] !== '--out')) throw new Error('Usage: node cloud/build.mjs [--out PROJECT_RELATIVE_DIRECTORY]');
const out = resolve(root, args[1] || 'dist');
const rel = relative(root, out);
if (rel === '..' || rel.startsWith('..' + sep) || resolve(out) === root) throw new Error('Build output must be a subdirectory of this project');
const mime = {'.html':'text/html; charset=utf-8','.js':'application/javascript; charset=utf-8','.mjs':'application/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json; charset=utf-8','.py':'text/x-python; charset=utf-8','.svg':'image/svg+xml; charset=utf-8','.txt':'text/plain; charset=utf-8'};
const assets = {};
async function walk(dir, prefix = '') {
  for (const entry of (await readdir(dir, {withFileTypes:true})).sort((a,b)=>a.name.localeCompare(b.name, 'en'))) {
    if (entry.name.startsWith('.') || entry.name === '__pycache__' || entry.name.endsWith('.pyc') || (prefix === '' && entry.name === 'server')) continue;
    const path = resolve(dir, entry.name), key = prefix + '/' + entry.name;
    if (entry.isSymbolicLink()) throw new Error('Static assets must not be symlinks');
    if (entry.isDirectory()) { await walk(path, key); continue; }
    if (!entry.isFile()) throw new Error('Static asset is not a regular file: ' + key);
    const ext = entry.name.slice(entry.name.lastIndexOf('.')).toLowerCase(), type = mime[ext];
    if (!type) throw new Error('Only text assets can be embedded by this build: ' + key);
    const bytes = await readFile(path), body = new TextDecoder('utf-8', {fatal:true}).decode(bytes);
    assets[key] = {type, body, etag:'"' + createHash('sha256').update(bytes).digest('hex').slice(0,24) + '"'};
  }
}
await walk(resolve(root, 'dist'));
if (!assets['/index.html']) throw new Error('Missing dist/index.html');
const manifest = JSON.parse(await readFile(resolve(root, '.openai/hosting.json'), 'utf8'));
if (manifest.static != null || manifest.d1 !== 'DB') throw new Error('Worker migration needs static removed and d1: "DB" in source hosting.json');
const source = await readFile(resolve(root, 'cloud/worker.js'), 'utf8');
const auth = await readFile(resolve(root, 'cloud/pages-auth.mjs'), 'utf8');
const authImport = "import {handleAuthRequest, resolveSessionUser, corsHeaders, allowedOrigin} from './pages-auth.mjs';";
if (!source.includes(authImport) || /^\s*import\s/m.test(auth)) throw new Error('Auth bundle must be a self-contained ESM module');
const marker = 'const STATIC_ASSETS = /*__ASSETS__*/ {};';
if (!source.includes(marker)) throw new Error('Worker asset marker missing');
const authNames = 'handleAuthRequest, resolveSessionUser, corsHeaders, allowedOrigin';
const authBundle = `const {${authNames}} = (() => {\n${auth.replace(/^export\s+/gm, '')}\nreturn {${authNames}};\n})();\n`;
const output = authBundle + source.replace(authImport, '').replace(marker, 'const STATIC_ASSETS = ' + JSON.stringify(assets) + ';');
await mkdir(resolve(out, 'server'), {recursive:true});
await mkdir(resolve(out, '.openai'), {recursive:true});
await writeFile(resolve(out, 'server/index.js'), output);
await writeFile(resolve(out, '.openai/hosting.json'), JSON.stringify(manifest, null, 2) + '\n');
await cp(resolve(root, 'drizzle'), resolve(out, '.openai/drizzle'), {recursive:true});
console.log(JSON.stringify({kind:'worker',assets:Object.keys(assets).length,entry:'server/index.js',bytes:(await stat(resolve(out,'server/index.js'))).size,output:out}));
