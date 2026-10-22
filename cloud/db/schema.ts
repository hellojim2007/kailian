import {sqliteTable, text, integer, blob, primaryKey, index} from 'drizzle-orm/sqlite-core';
export const learnerProgress = sqliteTable('learner_progress', {
  userId: text('user_id').notNull(),
  courseId: text('course_id').notNull().default('python-pytorch'),
  revision: integer('revision').notNull(),
  payload: blob('payload', {mode:'buffer'}).notNull(),
  updatedAt: text('updated_at').notNull(),
}, (table) => [primaryKey({columns:[table.userId,table.courseId]})]);

export const pagesAuthCodes = sqliteTable('pages_auth_codes', {
  codeHash: text('code_hash').primaryKey().notNull(),
  challenge: text('challenge').notNull(),
  userId: text('user_id').notNull(),
  userName: text('user_name').notNull(),
  userEmail: text('user_email').notNull(),
  createdAt: integer('created_at').notNull(),
  expiresAt: integer('expires_at').notNull(),
}, (table) => [index('codes_expiry').on(table.expiresAt)]);

export const pagesSessions = sqliteTable('pages_sessions', {
  tokenHash: text('token_hash').primaryKey().notNull(),
  userId: text('user_id').notNull(),
  userName: text('user_name').notNull(),
  userEmail: text('user_email').notNull(),
  createdAt: integer('created_at').notNull(),
  expiresAt: integer('expires_at').notNull(),
}, (table) => [index('sessions_expiry').on(table.expiresAt),index('sessions_user').on(table.userId)]);
