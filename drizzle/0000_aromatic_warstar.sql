CREATE TABLE `learner_progress` (
	`user_id` text NOT NULL,
	`course_id` text DEFAULT 'python-pytorch' NOT NULL,
	`revision` integer NOT NULL,
	`payload` blob NOT NULL,
	`updated_at` text NOT NULL,
	PRIMARY KEY(`user_id`, `course_id`)
);
