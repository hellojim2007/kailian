/* GitHub Pages bridge to Sites' native ChatGPT identity.
 * Deploy only behind Sites dispatch, which owns/overwrites the identity headers.
 * No OAuth provider, sign-in callback, or third-party cookie is implemented here.
 */
export const PAGES_ORIGIN = 'https://hellojim2007.github.io';
export const PAGES_RETURN_PREFIX = `${PAGES_ORIGIN}/kailian/`;
export const AUTH_BODY_LIMIT = 8 * 1024;
export const CODE_LIFETIME_MS = 5 * 60 * 1000;
export const SESSION_LIFETIME_MS = 30 * 24 * 60 * 60 * 1000;
const encoder = new TextEncoder();
const RANDOM_VALUE = /^[A-Za-z0-9_-]{43}$/;
const VERIFIER = /^[A-Za-z0-9._~-]{43,128}$/;
const STATE = /^[A-Za-z0-9_-]{16,128}$/;
const API_METHODS = new Map([
  ['/api/account', ['GET']],
  ['/api/progress', ['GET', 'PUT']],
  ['/api/session/exchange', ['POST']],
  ['/api/session/revoke', ['POST']],
]);

class AuthError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

export function allowedOrigin(request) {
  const origin = request.headers.get('Origin');
  if (origin) return origin === PAGES_ORIGIN || origin === new URL(request.url).origin;
  return request.headers.get('Sec-Fetch-Site') !== 'cross-site';
}

export function corsHeaders(request) {
  return request.headers.get('Origin') === PAGES_ORIGIN
    ? {'Access-Control-Allow-Origin': PAGES_ORIGIN, 'Vary': 'Origin'}
    : {'Vary': 'Origin'};
}

function json(request, data, status = 200, extra = {}) {
  return new Response(JSON.stringify(data), {status, headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'private, no-store',
    'Referrer-Policy': 'no-referrer',
    'X-Content-Type-Options': 'nosniff',
    ...corsHeaders(request), ...extra,
  }});
}

function requireAllowedOrigin(request) {
  if (!allowedOrigin(request)) {
    throw new AuthError(403, 'origin_not_allowed', '此网页来源不能访问学习台账号。');
  }
}

function db(env) {
  if (!env.DB?.prepare) throw new AuthError(503, 'auth_unavailable', '登录同步暂不可用，请稍后重试。');
  return env.DB;
}

export function platformUser(request) {
  const id = request.headers.get('oai-authenticated-user-id');
  if (!id || id.length > 1024) return null;
  const email = (request.headers.get('oai-authenticated-user-email') || '').slice(0, 1024);
  let name = '';
  if (request.headers.get('oai-authenticated-user-full-name-encoding') === 'percent-encoded-utf-8') {
    try { name = decodeURIComponent(request.headers.get('oai-authenticated-user-full-name') || ''); } catch {}
  }
  return {id, name: (name || email || '学习者').slice(0, 1024), email};
}

export function base64url(bytes) {
  let text = '';
  for (const byte of bytes) text += String.fromCharCode(byte);
  return btoa(text).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
}

export async function s256(value) {
  return base64url(new Uint8Array(await crypto.subtle.digest('SHA-256', encoder.encode(value))));
}

function random256() {
  return base64url(crypto.getRandomValues(new Uint8Array(32)));
}

export function validReturnTo(value) {
  if (typeof value !== 'string' || value.length > 4096 || !value.startsWith(PAGES_RETURN_PREFIX)) return false;
  try {
    const target = new URL(value);
    if (target.origin !== PAGES_ORIGIN || target.username || target.password || !target.pathname.startsWith('/kailian/')) return false;
    // Encoded path separators/dot traversal are unnecessary for the published
    // entrypoint and can be interpreted differently by upstream static hosts.
    if (/%(?:2f|5c|2e)/i.test(target.pathname)) return false;
    return true;
  } catch { return false; }
}

function bearer(request) {
  const match = /^Bearer ([A-Za-z0-9_-]{43})$/i.exec(request.headers.get('Authorization') || '');
  return match?.[1] || null;
}

export async function resolveSessionUser(request, env) {
  const native = platformUser(request);
  if (native) return native;
  const token = bearer(request);
  if (!token) return null;
  const row = await db(env).prepare(
    'SELECT user_id, user_name, user_email FROM pages_sessions WHERE token_hash = ? AND expires_at > ?'
  ).bind(await s256(token), Date.now()).first();
  return row ? {id: row.user_id, name: row.user_name, email: row.user_email} : null;
}

async function readAuthBytes(request) {
  const declared = request.headers.get('Content-Length');
  if (declared !== null && Number(declared) > AUTH_BODY_LIMIT) {
    throw new AuthError(413, 'auth_body_too_large', '登录请求过大。');
  }
  const reader = request.body?.getReader();
  const chunks = [];
  let size = 0;
  if (reader) {
    try {
      for (;;) {
        const {done, value} = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > AUTH_BODY_LIMIT) {
          await reader.cancel().catch(() => {});
          throw new AuthError(413, 'auth_body_too_large', '登录请求过大。');
        }
        chunks.push(value);
      }
    } finally { reader.releaseLock(); }
  }
  const bytes = new Uint8Array(size);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return bytes;
}

async function readJson(request) {
  if (!/^application\/json(?:\s*;|$)/i.test(request.headers.get('Content-Type') || '')) {
    throw new AuthError(415, 'json_required', '请使用JSON提交登录信息。');
  }
  const bytes = await readAuthBytes(request);
  let body;
  try { body = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes)); }
  catch { throw new AuthError(400, 'invalid_json', '登录信息不是有效JSON。'); }
  if (!body || typeof body !== 'object' || Array.isArray(body)) throw new AuthError(400, 'invalid_request', '登录信息格式不正确。');
  return body;
}

function redirect(location) {
  return new Response(null, {status: 302, headers: {
    Location: location,
    'Cache-Control': 'private, no-store',
    'Referrer-Policy': 'no-referrer',
    'X-Content-Type-Options': 'nosniff',
  }});
}

async function connect(request, env) {
  const url = new URL(request.url);
  if (url.search.length > AUTH_BODY_LIMIT) throw new AuthError(400, 'invalid_request', '登录校验参数过长。');
  // Top-level navigation normally omits Origin. If one is present, still
  // refuse a third website trying to use this endpoint as its login bridge.
  const origin = request.headers.get('Origin');
  if (origin && origin !== PAGES_ORIGIN && origin !== url.origin) {
    throw new AuthError(403, 'origin_not_allowed', '此网页来源不能访问学习台账号。');
  }
  const returnTo = url.searchParams.get('returnTo');
  const challenge = url.searchParams.get('challenge');
  const state = url.searchParams.get('state');
  if (!validReturnTo(returnTo) || !RANDOM_VALUE.test(challenge || '') || !STATE.test(state || '')) {
    throw new AuthError(400, 'invalid_request', '登录返回地址或校验参数无效。');
  }
  const user = platformUser(request);
  if (!user) {
    // Dispatch owns this native route. Its return path is same-origin and
    // contains the original validated connect parameters for the second visit.
    return redirect('/signin-with-chatgpt?return_to=' + encodeURIComponent(url.pathname + url.search));
  }
  const code = random256();
  const now = Date.now();
  await db(env).prepare(
    'INSERT INTO pages_auth_codes (code_hash, challenge, user_id, user_name, user_email, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?)'
  ).bind(await s256(code), challenge, user.id, user.name, user.email, now, now + CODE_LIFETIME_MS).run();
  const target = new URL(returnTo);
  target.hash = new URLSearchParams({sync_code: code, sync_state: state}).toString();
  return redirect(target.toString());
}

async function exchange(request, env) {
  requireAllowedOrigin(request);
  const body = await readJson(request);
  if (typeof body.code !== 'string' || !RANDOM_VALUE.test(body.code) ||
      typeof body.verifier !== 'string' || !VERIFIER.test(body.verifier)) {
    throw new AuthError(400, 'invalid_grant', '登录校验已失效，请重新登录。');
  }
  const database = db(env);
  const now = Date.now();
  // This one conditional DELETE is the consumption CAS. A wrong verifier
  // leaves the code intact; concurrent/replayed exchanges cannot both win.
  const row = await database.prepare(
    'DELETE FROM pages_auth_codes WHERE code_hash = ? AND challenge = ? AND expires_at > ? RETURNING user_id, user_name, user_email'
  ).bind(await s256(body.code), await s256(body.verifier), now).first();
  if (!row) throw new AuthError(400, 'invalid_grant', '登录校验已失效，请重新登录。');
  const token = random256();
  const expiresAt = now + SESSION_LIFETIME_MS;
  await database.prepare(
    'INSERT INTO pages_sessions (token_hash, user_id, user_name, user_email, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?)'
  ).bind(await s256(token), row.user_id, row.user_name, row.user_email, now, expiresAt).run();
  return json(request, {token, expiresAt: new Date(expiresAt).toISOString(), user: {id: row.user_id, name: row.user_name, email: row.user_email}});
}

async function revoke(request, env) {
  requireAllowedOrigin(request);
  const token = bearer(request);
  if (!token) throw new AuthError(401, 'auth_required', '请先登录。');
  await readAuthBytes(request);
  await db(env).prepare('DELETE FROM pages_sessions WHERE token_hash = ?').bind(await s256(token)).run();
  // Intentionally idempotent: reveal neither token existence nor profile.
  return json(request, {revoked: true});
}

function preflight(request, methods) {
  const origin = request.headers.get('Origin');
  if (!origin || !allowedOrigin(request)) throw new AuthError(403, 'origin_not_allowed', '此网页来源不能访问学习台账号。');
  const method = request.headers.get('Access-Control-Request-Method') || '';
  const headers = (request.headers.get('Access-Control-Request-Headers') || '').split(',').map(h => h.trim().toLowerCase()).filter(Boolean);
  if (!methods.includes(method) || headers.some(h => !['authorization','content-type'].includes(h))) {
    throw new AuthError(403, 'preflight_not_allowed', '此跨站请求方法或请求头未获允许。');
  }
  return new Response(null, {status: 204, headers: {
    ...corsHeaders(request),
    'Access-Control-Allow-Methods': methods.join(', '),
    'Access-Control-Allow-Headers': 'Authorization, Content-Type',
    'Access-Control-Max-Age': '600',
    'Cache-Control': 'private, no-store',
    'Vary': 'Origin, Access-Control-Request-Method, Access-Control-Request-Headers',
  }});
}

export async function handleAuthRequest(request, env = {}) {
  const path = new URL(request.url).pathname;
  const managed = path === '/auth/connect' || path === '/api/session/exchange' || path === '/api/session/revoke';
  if (!managed && !(request.method === 'OPTIONS' && API_METHODS.has(path))) return null;
  try {
    if (request.method === 'OPTIONS' && API_METHODS.has(path)) return preflight(request, API_METHODS.get(path));
    const method = path === '/auth/connect' ? 'GET' : 'POST';
    if (request.method !== method) return json(request, {error: {code: 'method_not_allowed', message: '请求方法不受支持。'}}, 405, {Allow: method});
    if (path === '/auth/connect') return await connect(request, env);
    if (path === '/api/session/exchange') return await exchange(request, env);
    return await revoke(request, env);
  } catch (error) {
    if (error instanceof AuthError) return json(request, {error: {code: error.code, message: error.message}}, error.status);
    // Never expose SQL, session secrets, profile information or stack traces.
    return json(request, {error: {code: 'auth_unavailable', message: '登录同步暂不可用，请稍后重试。'}}, 503);
  }
}
