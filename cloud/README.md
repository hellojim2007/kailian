# Account and progress API

This is a Sites Worker ESM backend. It preserves the existing `dist/` teaching
application and does not execute student Python/PyTorch code. `/api/run` returns
501; the browser Python worker and the local native PyTorch server stay separate.

## Hosting migration

The public GitHub mirror omits the existing Site's `.openai/hosting.json`.
For your own deployment, register/configure your own Sites project and use its
returned project ID in that file; `cloud/hosting.example.json` shows the storage
bindings. Do not reuse another deployment's identity. Static Pages builds do
not need a Sites project manifest.

The original static Site cannot use D1. Its existing project ID is retained in
`.openai/hosting.json`, `static` is removed, `d1` is `"DB"`, and unused `r2` is
`null`. Sites provisions the logical binding. Publication must use the existing
Site and the normal Sites source/packaging workflow. This directory does not
create a Site or change its audience.

The installed Worker ESM starter supports a single self-contained ES module.
`node cloud/build.mjs` embeds all existing UTF-8 static assets into that module,
then writes only `dist/server/index.js` and `dist/.openai/` metadata. It does not
delete, move, or rewrite the original `dist` assets. Generated output must be
rebuilt after any frontend change. For isolated validation:

```text
node cloud/build.mjs --out .runtime/cloud-build
node --test cloud/verify.mjs
```

SQL and Drizzle metadata are under root `drizzle/`, where the Sites packager
expects them. They were generated from `cloud/db/schema.ts` with:

```text
npm --prefix cloud ci
npm --prefix cloud run db:generate
```

Migrations are schema-only; never mutate/create tables in request handlers.
Append migrations after deployment rather than changing applied SQL or journals.
Hosted migration execution is performed by Sites before Worker publication.

## Progress contract

- `GET /api/account`: `{user:{id,name,email}|null,signInUrl,signOutUrl,storage:"d1",syncAvailable,limits}`.
- `GET /api/progress?course=python-pytorch`: `{revision,progress,updatedAt}`.
- Missing progress: `{revision:0,progress:null,updatedAt:null}`.
- `PUT /api/progress?course=python-pytorch` accepts JSON
  `{revision:<nonnegative safe integer>,progress:{version:2,...state}}`.
  Export version 1 is also accepted. `drafts` and `passed` must be objects.
- Successful PUT returns the same snapshot shape with the incremented revision.
- A stale revision returns HTTP 409 with the current remote snapshot plus
  `error:{code:"revision_conflict",message}`. It does not overwrite remote data.
- Omitted `course` defaults to `python-pytorch`; other courses return HTTP 400.
  The database primary key contains both authenticated user and course.
- HTTP 401 means sign-in is required; 400/415 mean malformed input; 413 means
  the snapshot is too large; 503 means temporary or unconfigured storage.

No account ID supplied in request JSON/query chooses the stored user. Identity
comes from the Sites dispatch headers or the verified Pages bearer session.
Progress is untrusted user data, not a credential or proof of course competence.
The client must still sanitize imported and downloaded state before rendering.

## Limits, concurrency, and privacy

Requests are bounded to 8 MiB even when Content-Length is absent. Snapshots are
gzip-compressed into at most 1,500,000 bytes to stay below D1's 2,000,000-byte row
limit with metadata headroom. Oversized writes leave the previous cloud snapshot
untouched; keep/export local progress and report the error instead of discarding
history. Account/progress responses are `private, no-store` and vary by identity.

Create and update are atomic conditional SQL statements. A GET followed by PUT
without revision checking would not provide the same protection. The client
should keep both local and remote backups after 409 and let the learner choose
which snapshot to continue from. A network error does not prove a PUT failed:
fetch the remote revision before deciding to retry an uncertain write.

Sessions and one-time login codes support the separate GitHub Pages origin.
API responses allow only `https://hellojim2007.github.io` and do not grant
cross-origin cookie credentials. Authorization is an opaque bearer token; never
include it in source control, console output, shared URLs, or progress exports.

## Portable deployment boundary

The teaching frontend is ordinary static HTML/CSS/JS and can be hosted on GitHub
Pages. Account storage here relies on Sites D1 and Sites-authenticated identity.
The optional Docker path should preserve that split: a static web container and
an independently authenticated API adapter (SQLite/PostgreSQL) with persistent
volumes, HTTPS, and backups. A reverse proxy must authenticate the user and strip
incoming identity headers before injecting trusted identity. Never deploy this
Worker directly behind a generic public proxy that trusts arbitrary caller
`oai-authenticated-user-*` headers.

Native PyTorch execution requires a separate restricted execution service. The
current local `server.py` is intended for a user's loopback computer; exposing it
publicly or merely putting it in a Docker container does not supply a multi-user
code sandbox. GitHub Pages and this Worker do not pretend to offer that runtime.

References: installed Sites `identity-and-secrets.md`, `storage.md`, Worker ESM
starter README, and [Cloudflare D1 limits](https://developers.cloudflare.com/d1/platform/limits/).
