CREATE TABLE `pages_auth_codes` (
	`code_hash` text PRIMARY KEY NOT NULL,
	`challenge` text NOT NULL,
	`user_id` text NOT NULL,
	`user_name` text NOT NULL,
	`user_email` text NOT NULL,
	`created_at` integer NOT NULL,
	`expires_at` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `codes_expiry` ON `pages_auth_codes` (`expires_at`);--> statement-breakpoint
CREATE TABLE `pages_sessions` (
	`token_hash` text PRIMARY KEY NOT NULL,
	`user_id` text NOT NULL,
	`user_name` text NOT NULL,
	`user_email` text NOT NULL,
	`created_at` integer NOT NULL,
	`expires_at` integer NOT NULL
);
--> statement-breakpoint
CREATE INDEX `sessions_expiry` ON `pages_sessions` (`expires_at`);--> statement-breakpoint
CREATE INDEX `sessions_user` ON `pages_sessions` (`user_id`);