import assert from 'node:assert/strict';
import {test} from 'node:test';
import {DatabaseSync} from 'node:sqlite';
import {readFile} from 'node:fs/promises';
import {handleAuthRequest, resolveSessionUser, validReturnTo, s256, PAGES_ORIGIN,
  PAGES_RETURN_PREFIX, AUTH_BODY_LIMIT, SESSION_LIFETIME_MS} from './pages-auth.mjs';

const schema = await readFile(new URL('./pages-auth.sql', import.meta.url), 'utf8');
const site = 'https://native-auth.example';
const verifier = 'v'.repeat(64);
const state = 'state_random_0123456789';
const nativeHeaders = {
  'oai-authenticated-user-id': 'alice',
  'oai-authenticated-user-email': 'alice@example.test',
  'oai-authenticated-user-full-name': encodeURIComponent('学习者甲'),
  'oai-authenticated-user-full-name-encoding': 'percent-encoded-utf-8',
};

function database() {
  const sqlite = new DatabaseSync(':memory:');
  sqlite.exec(schema);
  return {
    sqlite,
    prepare(sql) {
      let bindings = [];
      const statement = {
        bind(...values) { bindings = values; return statement; },
        async first() { return sqlite.prepare(sql).get(...bindings) || null; },
        async run() {
          const result = sqlite.prepare(sql).run(...bindings);
          return {success: true, meta: {changes: Number(result.changes)}};
        },
      };
      return statement;
    },
  };
}

function request(path, {method='GET', headers={}, body, stream=false}={}) {
  const options = {method, headers: {...headers}};
  if (body !== undefined) {
    options.headers['Content-Type'] ||= 'application/json';
    options.body = typeof body === 'string' || stream ? body : JSON.stringify(body);
    if (stream) options.duplex = 'half';
  }
  return new Request(site + path, options);
}

async function connect(DB, {signedIn=true, destination=PAGES_RETURN_PREFIX, proof=verifier}={}) {
  const params = new URLSearchParams({returnTo: destination, challenge: await s256(proof), state});
  return handleAuthRequest(request('/auth/connect?' + params, {headers: signedIn ? nativeHeaders : {}}), {DB});
}

async function mintCode(DB, options) {
  const response = await connect(DB, options);
  assert.equal(response.status, 302);
  const target = new URL(response.headers.get('Location'));
  const hash = new URLSearchParams(target.hash.slice(1));
  assert.equal(hash.get('sync_state'), state);
  return hash.get('sync_code');
}

async function exchange(DB, code, proof=verifier, headers={Origin:PAGES_ORIGIN}) {
  return handleAuthRequest(request('/api/session/exchange', {method:'POST', headers, body:{code,verifier:proof}}), {DB});
}

test('return allowlist is the exact published project, rejects alternate hosts and traversal', () => {
  assert.equal(validReturnTo(PAGES_RETURN_PREFIX), true);
  assert.equal(validReturnTo(PAGES_RETURN_PREFIX + 'index.html?lesson=pt01#old'), true);
  for (const value of [
    'https://hellojim2007.github.io/kailian',
    'https://hellojim2007.github.io/kailian-lab/',
    'https://hellojim2007.github.io/kaillian/',
    'https://hellojim2007.github.io.evil.test/kailian/',
    'https://evil.test/kailian/',
    'http://hellojim2007.github.io/kailian/',
    'https://hellojim2007.github.io:444/kailian/',
    PAGES_RETURN_PREFIX + '../elsewhere/',
    PAGES_RETURN_PREFIX + '%2e%2e/elsewhere/',
    PAGES_RETURN_PREFIX + '%2f..%2felsewhere/',
    'https://hellojim2007.github.io@evil.test/kailian/',
    '//hellojim2007.github.io/kailian/',
  ]) assert.equal(validReturnTo(value), false, value);
});

test('anonymous connect delegates to native top-level sign-in and preserves validated relative return path', async () => {
  const response = await connect(undefined, {signedIn:false});
  assert.equal(response.status,302);
  const redirect = new URL(response.headers.get('Location'),site);
  assert.equal(redirect.pathname,'/signin-with-chatgpt');
  const returnPath=redirect.searchParams.get('return_to');
  assert.ok(returnPath.startsWith('/auth/connect?'));
  const params=new URL(returnPath,site).searchParams;
  assert.equal(params.get('returnTo'),PAGES_RETURN_PREFIX);
  assert.equal(params.get('challenge'),await s256(verifier));
  assert.equal(params.get('state'),state);
  assert.equal(response.headers.get('Referrer-Policy'),'no-referrer');
});

test('authenticated connect returns only one-time code/state in fragment and stores only its hash', async () => {
  const DB=database();
  const code=await mintCode(DB);
  assert.match(code,/^[A-Za-z0-9_-]{43}$/);
  const row=DB.sqlite.prepare('SELECT * FROM pages_auth_codes').get();
  assert.equal(row.code_hash,await s256(code));
  assert.equal(row.challenge,await s256(verifier));
  assert.equal(row.user_id,'alice');
  assert.equal(row.user_name,'学习者甲');
  assert.ok(row.expires_at-Date.now()>4*60*1000 && row.expires_at-Date.now()<=5*60*1000);
  assert.ok(!JSON.stringify(row).includes(code));
  assert.notEqual(await mintCode(DB),code);
});

test('PKCE exchange produces 30-day cookie-free bearer session, with only hashed token in SQLite', async () => {
  const DB=database();const code=await mintCode(DB);
  const response=await exchange(DB,code);assert.equal(response.status,200);
  const data=await response.json();
  assert.match(data.token,/^[A-Za-z0-9_-]{43}$/);
  assert.deepEqual(data.user,{id:'alice',name:'学习者甲',email:'alice@example.test'});
  assert.ok(Date.parse(data.expiresAt)-Date.now()>SESSION_LIFETIME_MS-2000);
  const row=DB.sqlite.prepare('SELECT * FROM pages_sessions').get();
  assert.equal(row.token_hash,await s256(data.token));assert.ok(!JSON.stringify(row).includes(data.token));
  assert.equal(row.expires_at,Date.parse(data.expiresAt));
  assert.equal(response.headers.get('Set-Cookie'),null);
  assert.equal(response.headers.get('Access-Control-Allow-Origin'),PAGES_ORIGIN);
  assert.equal(response.headers.get('Access-Control-Allow-Credentials'),null);
  assert.match(response.headers.get('Cache-Control'),/no-store/);
  assert.deepEqual(await resolveSessionUser(request('/api/account',{headers:{Authorization:`Bearer ${data.token}`}}),{DB}),data.user);
  assert.equal(DB.sqlite.prepare('SELECT count(*) AS n FROM pages_auth_codes').get().n,0);
});

test('wrong verifier does not consume valid code; successful exchange cannot be replayed', async () => {
  const DB=database();const code=await mintCode(DB);
  const wrong=await exchange(DB,code,'w'.repeat(64));assert.equal(wrong.status,400);
  assert.equal((await wrong.json()).error.code,'invalid_grant');
  assert.equal(DB.sqlite.prepare('SELECT count(*) AS n FROM pages_auth_codes').get().n,1);
  assert.equal((await exchange(DB,code)).status,200);
  const replay=await exchange(DB,code);assert.equal(replay.status,400);
  assert.equal((await replay.json()).error.code,'invalid_grant');
});

test('concurrent code redemption has exactly one winner and creates one session', async () => {
  const DB=database();const code=await mintCode(DB);
  const results=await Promise.all([exchange(DB,code),exchange(DB,code),exchange(DB,code)]);
  assert.deepEqual(results.map(r=>r.status).sort(),[200,400,400]);
  assert.equal(DB.sqlite.prepare('SELECT count(*) AS n FROM pages_sessions').get().n,1);
});

test('expired code and expired bearer do not authenticate', async () => {
  const DB=database();const code=await mintCode(DB);
  DB.sqlite.prepare('UPDATE pages_auth_codes SET expires_at=?').run(Date.now()-1);
  assert.equal((await exchange(DB,code)).status,400);
  const fresh=await mintCode(DB);const data=await(await exchange(DB,fresh)).json();
  DB.sqlite.prepare('UPDATE pages_sessions SET expires_at=?').run(Date.now()-1);
  assert.equal(await resolveSessionUser(request('/api/progress',{headers:{Authorization:`Bearer ${data.token}`}}),{DB}),null);
});

test('platform identity takes precedence over bearer and does not need storage', async () => {
  const headers={...nativeHeaders,'oai-authenticated-user-id':'bob',Authorization:`Bearer ${'A'.repeat(43)}`};
  const user=await resolveSessionUser(request('/api/account',{headers}),{});
  assert.equal(user.id,'bob');
  assert.equal(await resolveSessionUser(request('/api/account',{headers:{Authorization:'Bearer not-valid'}}),{}),null);
});

test('revoke is idempotent and invalidates the bearer', async () => {
  const DB=database();const data=await(await exchange(DB,await mintCode(DB))).json();
  const headers={Origin:PAGES_ORIGIN,Authorization:`Bearer ${data.token}`};
  for(let i=0;i<2;i++) {
    const response=await handleAuthRequest(request('/api/session/revoke',{method:'POST',headers}),{DB});
    assert.equal(response.status,200);assert.deepEqual(await response.json(),{revoked:true});
  }
  assert.equal(await resolveSessionUser(request('/api/account',{headers}),{DB}),null);
  assert.equal((await handleAuthRequest(request('/api/session/revoke',{method:'POST',headers:{Origin:PAGES_ORIGIN}}),{DB})).status,401);
});

test('foreign/null origins and origin-less browser cross-site exchanges are rejected before consuming code', async () => {
  const DB=database();const code=await mintCode(DB);
  for(const Origin of ['https://evil.test','https://hellojim2007.github.io.evil.test','null']) {
    const response=await exchange(DB,code,verifier,{Origin});
    assert.equal(response.status,403);assert.equal(response.headers.get('Access-Control-Allow-Origin'),null);
  }
  assert.equal((await exchange(DB,code,verifier,{'Sec-Fetch-Site':'cross-site'})).status,403);
  assert.equal((await exchange(DB,code)).status,200);
});

test('precise preflights allow only endpoint methods and Authorization/Content-Type', async () => {
  for(const [path,method] of [['/api/progress','PUT'],['/api/progress','GET'],['/api/account','GET'],['/api/session/exchange','POST'],['/api/session/revoke','POST']]) {
    const response=await handleAuthRequest(request(path,{method:'OPTIONS',headers:{Origin:PAGES_ORIGIN,'Access-Control-Request-Method':method,'Access-Control-Request-Headers':'Content-Type, Authorization'}}),{});
    assert.equal(response.status,204);assert.equal(response.headers.get('Access-Control-Allow-Origin'),PAGES_ORIGIN);
    assert.equal(response.headers.get('Access-Control-Allow-Credentials'),null);
  }
  for(const headers of [
    {Origin:PAGES_ORIGIN,'Access-Control-Request-Method':'DELETE'},
    {Origin:PAGES_ORIGIN,'Access-Control-Request-Method':'PUT','Access-Control-Request-Headers':'X-Other'},
    {Origin:'https://evil.test','Access-Control-Request-Method':'PUT'},
    {'Access-Control-Request-Method':'PUT'},
  ]) assert.equal((await handleAuthRequest(request('/api/progress',{method:'OPTIONS',headers}),{})).status,403);
});

test('invalid S256 arguments and destination fail before native sign-in or database', async () => {
  for(const replacement of [
    {returnTo:'https://evil.test/'},{state:'short'}, {challenge:'plain-verifier'},
    {returnTo:PAGES_RETURN_PREFIX+'../elsewhere/'},
  ]) {
    const params=new URLSearchParams({returnTo:PAGES_RETURN_PREFIX,challenge:await s256(verifier),state,...replacement});
    const response=await handleAuthRequest(request('/auth/connect?'+params),{});
    assert.equal(response.status,400);assert.equal(response.headers.get('Location'),null);
  }
  const params=new URLSearchParams({returnTo:PAGES_RETURN_PREFIX,challenge:await s256(verifier),state});
  assert.equal((await handleAuthRequest(request('/auth/connect?'+params,{headers:{Origin:'https://evil.test',...nativeHeaders}}),{DB:database()})).status,403);
});

test('bad code/verifier and non-JSON bodies have stable non-sensitive errors', async () => {
  const DB=database();
  for(const body of [{code:'short',verifier},{code:'A'.repeat(43),verifier:'x'.repeat(42)},{code:'A'.repeat(43),verifier:'x'.repeat(129)},{code:'A'.repeat(43),verifier:'坏'.repeat(64)}]) {
    assert.equal((await handleAuthRequest(request('/api/session/exchange',{method:'POST',headers:{Origin:PAGES_ORIGIN},body}),{DB})).status,400);
  }
  assert.equal((await handleAuthRequest(request('/api/session/exchange',{method:'POST',body:'{'}),{DB})).status,400);
  assert.equal((await handleAuthRequest(request('/api/session/exchange',{method:'POST',headers:{'Content-Type':'text/plain'},body:'{}'}),{DB})).status,415);
});

test('auth body has both declared and actual 8 KiB limits, including streaming bodies', async () => {
  const path='/api/session/exchange';
  assert.equal((await handleAuthRequest(request(path,{method:'POST',headers:{'Content-Length':String(AUTH_BODY_LIMIT+1)},body:'{}'}),{})).status,413);
  assert.equal((await handleAuthRequest(request(path,{method:'POST',body:' '.repeat(AUTH_BODY_LIMIT+1)}),{})).status,413);
  const stream=new ReadableStream({start(controller){controller.enqueue(new Uint8Array(4096));controller.enqueue(new Uint8Array(4097));controller.close();}});
  assert.equal((await handleAuthRequest(request(path,{method:'POST',body:stream,stream:true}),{})).status,413);
  const DB=database();const data=await(await exchange(DB,await mintCode(DB))).json();
  const headers={Origin:PAGES_ORIGIN,Authorization:`Bearer ${data.token}`};
  assert.equal((await handleAuthRequest(request('/api/session/revoke',{method:'POST',headers,body:' '.repeat(AUTH_BODY_LIMIT+1)}),{DB})).status,413);
  assert.equal((await resolveSessionUser(request('/api/account',{headers}),{DB})).id,'alice');
});

test('storage exceptions do not leak SQL, keys, or secret values', async () => {
  const secret='SECRET_SQL_DETAILS_do_not_echo';
  const DB={prepare(){throw new Error('SELECT token_hash '+secret);}};
  const response=await connect(DB);assert.equal(response.status,503);
  const text=await response.text();assert.ok(!text.includes(secret));assert.ok(!text.includes('SELECT'));
  assert.equal((await handleAuthRequest(request('/auth/connect',{method:'POST'}),{})).status,405);
  assert.equal((await handleAuthRequest(request('/api/session/exchange'),{})).status,405);
  assert.equal(await handleAuthRequest(request('/some-other-page'),{}),null);
});
