-- D1 schema contract for the GitHub Pages/native Sites identity bridge.
-- All timestamps are Unix epoch milliseconds; raw codes/tokens are never stored.
CREATE TABLE IF NOT EXISTS pages_auth_codes (
  code_hash TEXT PRIMARY KEY NOT NULL,
  challenge TEXT NOT NULL,
  user_id TEXT NOT NULL,
  user_name TEXT NOT NULL,
  user_email TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS codes_expiry ON pages_auth_codes(expires_at);
CREATE TABLE IF NOT EXISTS pages_sessions (
  token_hash TEXT PRIMARY KEY NOT NULL,
  user_id TEXT NOT NULL,
  user_name TEXT NOT NULL,
  user_email TEXT NOT NULL,
  created_at INTEGER NOT NULL,
  expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS sessions_expiry ON pages_sessions(expires_at);
CREATE INDEX IF NOT EXISTS sessions_user ON pages_sessions(user_id);
-- Optional maintenance after session/code expiry, never deleting live sessions:
-- DELETE FROM pages_auth_codes WHERE expires_at <= <trusted server epoch ms>;
-- DELETE FROM pages_sessions WHERE expires_at <= <trusted server epoch ms>;
