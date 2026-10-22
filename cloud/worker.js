/* Sites supplies authenticated headers at its trusted dispatch boundary.
 * This Worker must not be exposed directly behind a proxy that preserves
 * caller-supplied oai-authenticated-user-* headers. No student code runs here.
 */
import {handleAuthRequest, resolveSessionUser, corsHeaders, allowedOrigin} from './pages-auth.mjs';
const STATIC_ASSETS = /*__ASSETS__*/ {};
export const REQUEST_LIMIT = 8 * 1024 * 1024;
export const STORED_LIMIT = 1500000;
const encoder = new TextEncoder();

class ApiError extends Error {
  constructor(status, code, message) { super(message); this.status = status; this.code = code; }
}

function json(value, status = 200, extra = {}) {
  return new Response(JSON.stringify(value), {status, headers: {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'private, no-store',
    'Vary': 'Cookie, Authorization, oai-authenticated-user-id',
    'X-Content-Type-Options': 'nosniff', ...extra,
  }});
}

async function requireUser(request, env) {
  const user = await resolveSessionUser(request, env);
  if (!user) throw new ApiError(401, 'auth_required', '登录后可同步学习进度。');
  return user;
}

function database(env) {
  if (!env.DB?.prepare) throw new ApiError(503, 'storage_unavailable', '云端存储暂不可用，本机草稿仍可保留和导出。');
  return env.DB;
}

function sameOrigin(request) {
  const origin = request.headers.get('Origin');
  const pagesBearer = allowedOrigin(request) && /^Bearer\s+\S+$/i.test(request.headers.get('Authorization') || '');
  if (!pagesBearer && ((origin && origin !== new URL(request.url).origin) || request.headers.get('Sec-Fetch-Site') === 'cross-site')) {
    throw new ApiError(403, 'cross_origin', '请在学习台页面内保存进度。');
  }
}

async function readLimited(stream, max, code = 'request_too_large') {
  if (!stream) return new Uint8Array();
  const reader = stream.getReader();
  const chunks = []; let size = 0;
  try {
    for (;;) {
      const {done, value} = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > max) {
        await reader.cancel().catch(() => {});
        throw new ApiError(413, code, '进度超过云端容量限制，请先导出备份并减少历史记录；云端原进度未被覆盖。');
      }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const result = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { result.set(chunk, offset); offset += chunk.byteLength; }
  return result;
}

async function readBody(request) {
  if (!/^application\/json(?:\s*;|$)/i.test(request.headers.get('Content-Type') || '')) {
    throw new ApiError(415, 'json_required', '请使用 JSON 保存进度。');
  }
  const length = Number(request.headers.get('Content-Length'));
  if (Number.isFinite(length) && length > REQUEST_LIMIT) throw new ApiError(413, 'request_too_large', '进度请求超过 8 MiB，请先导出备份。');
  const bytes = await readLimited(request.body, REQUEST_LIMIT);
  let body;
  try { body = JSON.parse(new TextDecoder('utf-8', {fatal: true}).decode(bytes)); }
  catch { throw new ApiError(400, 'invalid_json', '进度不是有效的 UTF-8 JSON。'); }
  if (!body || typeof body !== 'object' || Array.isArray(body) ||
      !Number.isSafeInteger(body.revision) || body.revision < 0 || body.revision >= Number.MAX_SAFE_INTEGER ||
      !body.progress || typeof body.progress !== 'object' || Array.isArray(body.progress) ||
      ![1, 2].includes(body.progress.version) ||
      !isRecord(body.progress.drafts) || !isRecord(body.progress.passed)) {
    throw new ApiError(400, 'invalid_progress', '需要有效的 revision 和开练 version 1/2 进度对象。');
  }
  return body;
}

function isRecord(value) { return value !== null && typeof value === 'object' && !Array.isArray(value); }

async function compress(progress) {
  const bytes = encoder.encode(JSON.stringify(progress));
  const stream = new Response(bytes).body.pipeThrough(new CompressionStream('gzip'));
  return readLimited(stream, STORED_LIMIT, 'snapshot_too_large');
}

function blobBytes(value) {
  if (value instanceof Uint8Array) return value;
  if (value instanceof ArrayBuffer) return new Uint8Array(value);
  if (Array.isArray(value)) return new Uint8Array(value);
  throw new Error('Invalid stored payload');
}

async function snapshot(db, id, course) {
  const row = await db.prepare('SELECT revision, payload, updated_at FROM learner_progress WHERE user_id = ? AND course_id = ?').bind(id, course).first();
  if (!row) return {revision: 0, progress: null, updatedAt: null};
  const stream = new Response(blobBytes(row.payload)).body.pipeThrough(new DecompressionStream('gzip'));
  const bytes = await readLimited(stream, REQUEST_LIMIT, 'stored_snapshot_too_large');
  return {revision: row.revision, progress: JSON.parse(new TextDecoder().decode(bytes)), updatedAt: row.updated_at};
}

async function progressApi(request, env) {
  const user = await requireUser(request, env), db = database(env);
  const course = new URL(request.url).searchParams.get('course') || 'python-pytorch';
  if (course !== 'python-pytorch') throw new ApiError(400, 'unknown_course', '该课程尚未开放云端进度。');
  if (request.method === 'GET') return json(await snapshot(db, user.id, course));
  if (request.method !== 'PUT') return json({error: {code: 'method_not_allowed', message: '仅支持 GET 和 PUT。'}}, 405, {Allow: 'GET, PUT'});
  sameOrigin(request);
  const body = await readBody(request);
  const payload = await compress(body.progress), updatedAt = new Date().toISOString();
  // Each write is a single conditional SQL statement. Two devices cannot both
  // successfully update the same revision, including an account's first save.
  const row = body.revision === 0
    ? await db.prepare('INSERT INTO learner_progress (user_id, course_id, revision, payload, updated_at) VALUES (?, ?, 1, ?, ?) ON CONFLICT(user_id, course_id) DO NOTHING RETURNING revision, updated_at').bind(user.id, course, payload, updatedAt).first()
    : await db.prepare('UPDATE learner_progress SET revision = revision + 1, payload = ?, updated_at = ? WHERE user_id = ? AND course_id = ? AND revision = ? RETURNING revision, updated_at').bind(payload, updatedAt, user.id, course, body.revision).first();
  if (!row) return json({...await snapshot(db, user.id, course), error: {code: 'revision_conflict', message: '其他设备已保存新进度，请比较设备与云端版本后再选择。'}}, 409);
  return json({revision: row.revision, progress: body.progress, updatedAt: row.updated_at});
}

async function handle(request, env) {
  const url = new URL(request.url), path = url.pathname;
  const authResponse = await handleAuthRequest(request, env);
  if (authResponse) return authResponse;
  if (path === '/api/account') {
    if (request.method !== 'GET') return json({error: {code: 'method_not_allowed', message: '仅支持 GET。'}}, 405, {Allow: 'GET'});
    return json({user: await resolveSessionUser(request, env), signInUrl: '/signin-with-chatgpt?return_to=%2F', signOutUrl: '/signout-with-chatgpt?return_to=%2F', storage: 'd1', syncAvailable: Boolean(env.DB?.prepare), limits: {requestBytes: REQUEST_LIMIT, compressedBytes: STORED_LIMIT}});
  }
  if (path === '/api/progress') return progressApi(request, env);
  if (path === '/api/health') return json({status: 'ok', runtime: 'browser', mode: 'cloud', execution: false, progress: Boolean(env.DB?.prepare)});
  if (path === '/api/run') return json({error: {code: 'cloud_execution_unsupported', message: '云端不执行学习者代码。Python 使用浏览器运行环境；真实 PyTorch 请打开本机学习台。'}}, 501);
  if (path.startsWith('/api/')) return json({error: {code: 'not_found', message: '接口不存在。'}}, 404);
  const asset = STATIC_ASSETS[path === '/' ? '/index.html' : path];
  if (!asset) return new Response('Not found', {status: 404});
  if (!['GET', 'HEAD'].includes(request.method)) return new Response('Method not allowed', {status: 405, headers: {Allow: 'GET, HEAD'}});
  const headers = {'Content-Type': asset.type, 'Cache-Control': 'no-cache', 'ETag': asset.etag, 'X-Content-Type-Options': 'nosniff', 'Referrer-Policy': 'same-origin'};
  if (request.headers.get('If-None-Match') === asset.etag) return new Response(null, {status: 304, headers});
  return new Response(request.method === 'HEAD' ? null : asset.body, {headers});
}

export default {
  async fetch(request, env = {}) {
    let response;
    try { response = await handle(request, env); }
    catch (error) {
      if (error instanceof ApiError) response = json({error: {code: error.code, message: error.message}}, error.status);
      else {
      // Never log snapshots, student code, email, or SQL bind parameters.
      console.error('Cloud progress request failed');
        response = json({error: {code: 'storage_error', message: '云端暂时未能完成保存，请保留本机进度后重试。'}}, 503);
      }
    }
    if (new URL(request.url).pathname.startsWith('/api/')) {
      const headers = new Headers(response.headers);
      const vary = headers.get('Vary') || '';
      for (const [name, value] of Object.entries(corsHeaders(request))) if (name.toLowerCase() !== 'vary') headers.set(name, value);
      headers.set('Vary', [...new Set(vary.split(',').map(x=>x.trim()).filter(Boolean).concat('Origin'))].join(', '));
      return new Response(response.body, {status:response.status, statusText:response.statusText, headers});
    }
    return response;
  },
};
